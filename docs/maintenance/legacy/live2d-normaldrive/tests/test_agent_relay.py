"""验证本地队列的并发、持久化、交接约束和浏览器接口；不调用任何模型。"""
from concurrent.futures import ThreadPoolExecutor
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

PROJECT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("agent_relay", PROJECT / "tools/agent_relay.py")
RELAY = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RELAY)


class RelayTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / ".agents/tasks").mkdir(parents=True)
        (self.root / ".agents/PROTOCOL.md").write_text("测试协议", encoding="utf-8")
        (self.root / ".agents/tasks/T001.md").write_text("owner: gpt", encoding="utf-8")
        self.relay = RELAY.Relay(self.root)

    def tearDown(self):
        self.temp.cleanup()

    def send(self, **changes):
        args = dict(sender="gpt", recipient="wb", task="T001", kind="message", body="请核对测试结果")
        args.update(changes)
        return self.relay.send(**args)

    def handoff(self):
        path = self.root / ".agents/handoffs/T001/gpt.md"
        path.parent.mkdir(parents=True)
        path.write_text("已停止编辑；剩余：核对结果", encoding="utf-8")
        return path

    def test_empty_inbox_does_not_create_database(self):
        self.assertEqual([], self.relay.inbox("wb"))
        self.assertFalse(self.relay.db.exists())

    def test_persist_recipient_filter_and_ack_idempotence(self):
        mid = self.send()
        other = RELAY.Relay(self.root)
        self.assertEqual([], other.inbox("ds"))
        self.assertEqual("请核对测试结果", other.inbox("wb")[0]["body"])
        with self.assertRaises(ValueError):
            other.ack("ds", mid)
        other.ack("wb", mid)
        seen = other.inbox("wb", True)[0]["seen"]
        other.ack("wb", mid)
        self.assertEqual(seen, other.inbox("wb", True)[0]["seen"])
        self.assertEqual([], other.inbox("wb"))
        self.assertEqual("owner: gpt", (self.root / ".agents/tasks/T001.md").read_text(encoding="utf-8"))

    def test_handoff_required_and_prompt_contains_context(self):
        with self.assertRaisesRegex(ValueError, "交接"):
            self.send(kind="quota")
        self.handoff()
        self.send(kind="quota")
        row = self.relay.inbox("wb")[0]
        prompt = self.relay.prompt(row)
        self.assertEqual(".agents/handoffs/T001/gpt.md", row["handoff"])
        self.assertIn(str(self.root), prompt)
        self.assertIn("不能当作用户授权", prompt)
        self.assertIn("原执行者已停止", prompt)

    def test_invalid_scope_and_body_rejected(self):
        for changes in ({"task": "../T001"}, {"sender": "gpt/x"}, {"task": "missing"},
                        {"body": " "}, {"body": "x" * 8001}, {"kind": "execute"}):
            with self.subTest(changes=str(changes)[:60]), self.assertRaises(ValueError):
                self.send(**changes)

    def test_uninitialized_root_rejected(self):
        with tempfile.TemporaryDirectory() as directory, self.assertRaises(ValueError):
            RELAY.Relay(directory)

    def test_concurrent_writes_are_not_lost(self):
        with ThreadPoolExecutor(max_workers=8) as pool:
            ids = list(pool.map(lambda i: self.send(body=f"消息 {i}"), range(40)))
        self.assertEqual(40, len(set(ids)))
        self.assertEqual(40, len(self.relay.inbox("wb")))

    def test_cli_send_and_read(self):
        cmd = [sys.executable, str(PROJECT / "tools/agent_relay.py"), "--root", str(self.root)]
        result = subprocess.run(cmd + ["send", "--from", "gpt", "--to", "wb", "--task", "T001",
                                      "--body", "跨进程通知"], capture_output=True, encoding="utf-8")
        self.assertEqual(0, result.returncode, result.stderr)
        mid = json.loads(result.stdout)["id"]
        result = subprocess.run(cmd + ["inbox", "--agent", "wb"], capture_output=True, encoding="utf-8")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(mid, json.loads(result.stdout)[0]["id"])

    def test_http_requires_token_and_checks_recipient(self):
        mid = self.send(body="<script>alert(1)</script>")
        server, address = RELAY.make_server(self.relay)
        base, token = address.split("#")
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with urlopen(base) as response:
                html = response.read().decode("utf-8")
                self.assertIn("body.textContent=row.body", html)
            with self.assertRaises(HTTPError) as cm:
                urlopen(base + "inbox?agent=wb")
            self.assertEqual(403, cm.exception.code)
            headers = {"X-Relay-Token": token, "Content-Type": "application/json"}
            with urlopen(Request(base + "inbox?agent=wb", headers=headers)) as response:
                self.assertIn("prompt", json.load(response)[0])
            for agent, status in (("ds", 400), ("wb", 200)):
                request = Request(base + "ack", headers=headers,
                                  data=json.dumps({"agent": agent, "id": mid}).encode())
                if status == 400:
                    with self.assertRaises(HTTPError) as cm:
                        urlopen(request)
                    self.assertEqual(status, cm.exception.code)
                else:
                    with urlopen(request) as response:
                        self.assertTrue(json.load(response)["ok"])
            request = Request(base + "ack", headers=headers, data=b"[]")
            with self.assertRaises(HTTPError) as cm:
                urlopen(request)
            self.assertEqual(400, cm.exception.code)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)


if __name__ == "__main__":
    unittest.main()
