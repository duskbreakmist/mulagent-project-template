"""五项用户需求的场景验收；用独立进程和模拟适配器，不冒充实际客户端接入。"""
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
import importlib.util
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

PROJECT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT / "tools/agent_workbench.py"
SPEC = importlib.util.spec_from_file_location("agent_workbench", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class WorkbenchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / ".agents").mkdir()
        (self.root / ".agents/PROTOCOL.md").write_text("测试协议", encoding="utf-8")
        self.w = MODULE.Workbench(self.root)
        self.w.join("dev", "开发实例", ["developer", "tester"])
        self.w.join("backup", "备用开发实例", ["developer"])
        self.w.join("tester", "独立测试实例", ["tester"])
        self.w.join("human", "人", ["human", "integrator"])
        self.w.join("r1", "研究一", ["researcher"])
        self.w.join("r2", "研究二", ["researcher"])

    def tearDown(self):
        self.temp.cleanup()

    def task(self, task="D1", scopes=None, **options):
        return self.w.create_task(task, "功能开发", "development", scopes or ["src/auth"],
                                  "公共接口契约", **options)

    def implement(self, revision="commit-a"):
        self.task()
        claim = self.w.claim("D1", "dev")
        self.w.finish("D1", "dev", claim["epoch"], {"revision": revision, "files": ["src/auth"]})
        self.w.create_task("T1", "独立验收", "test", ["tests/auth"],
                           "hidden-test-marker；独立设计边界", subject="D1")

    def research(self):
        self.w.create_run("R1", "公共问题", "同一基线与来源标准", ["r1", "r2"], "human")

    def report(self, marker):
        return {"claims": [{"kind": "fact", "statement": marker,
                            "sources": ["https://example.org/primary-source"]}]}

    def adapter(self, name, source):
        path = self.root / (name + ".py")
        path.write_text(source, encoding="utf-8")
        return [sys.executable, str(path)]

    def test_five_processes_claim_same_task_only_one_wins(self):
        self.task()
        agents = ["dev", "backup"]
        for i in range(3):
            agent = "dev-" + str(i)
            agents.append(agent)
            self.w.join(agent, "并发实例", ["developer"])
        def claim(agent):
            return subprocess.run([sys.executable, str(SCRIPT), "--root", str(self.root),
                                   "call", "claim", "--data", json.dumps({"task": "D1", "agent": agent})],
                                  capture_output=True, encoding="utf-8")
        with ThreadPoolExecutor(max_workers=5) as pool:
            results = list(pool.map(claim, agents))
        self.assertEqual(1, sum(x.returncode == 0 for x in results))
        self.assertEqual(4, sum(x.returncode == 2 for x in results))
        self.assertTrue(all(x.stderr for x in results if x.returncode == 2))
        self.assertIn(self.w.status()["tasks"][0]["owner"], agents)

    def test_distinct_modules_parallel_and_parent_scope_conflicts(self):
        self.task()
        self.task("D2", ["src/progress"])
        self.task("D3", ["src/auth/parser.py"])
        self.w.claim("D1", "dev")
        self.w.claim("D2", "backup")
        with self.assertRaisesRegex(ValueError, "重叠"):
            self.w.claim("D3", "human")
        self.assertEqual(2, sum(x["status"] == "active" for x in self.w.status()["tasks"]))

    def test_path_escape_and_serial_execution_are_rejected(self):
        for path in ("../outside", "/absolute", ".git/index", "src/../outside", "C:/outside"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                self.task(scopes=[path])
        self.task(mode="serial")
        self.task("D2", ["src/other"])
        self.w.claim("D1", "dev")
        with self.assertRaisesRegex(ValueError, "串行"):
            self.w.claim("D2", "backup")

    def test_checkpoint_survives_quota_handoff_and_old_writer_is_fenced(self):
        self.task(backups=["backup", "human"])
        claim = self.w.claim("D1", "dev")
        self.w.checkpoint("D1", "dev", claim["epoch"], {"remaining": "补充错误处理"})
        self.w.stop("D1", "quota_exhausted", stopped=True)
        next_claim = self.w.claim("D1", "backup")
        self.assertEqual("补充错误处理", self.w.context("D1", "backup")["checkpoint"]["remaining"])
        with self.assertRaisesRegex(ValueError, "失效"):
            self.w.finish("D1", "dev", claim["epoch"], {"revision": "stale"})
        with self.assertRaisesRegex(ValueError, "旧适配器"):
            self.w.stop("D1", "adapter_error", True, "dev", claim["epoch"])
        self.assertEqual("backup", self.w.status()["tasks"][0]["owner"])
        self.assertGreater(next_claim["epoch"], claim["epoch"])
        self.assertTrue(self.w.inbox("backup"))

    def test_missing_heartbeat_does_not_release_unstopped_writer(self):
        self.task()
        claim = self.w.claim("D1", "dev")
        with self.w.connection(True) as conn:
            conn.execute("UPDATE agents SET seen=0 WHERE id='dev'")
        self.w.stop("D1", "quota_exhausted", stopped=False)
        self.task("D2", ["src/auth/file.py"])
        with self.assertRaises(ValueError):
            self.w.claim("D2", "backup")
        with self.assertRaises(ValueError):
            self.w.checkpoint("D1", "dev", claim["epoch"], {"remaining": "旧写者"})
        self.assertEqual("stopping", self.w.status()["tasks"][0]["status"])

    def test_independent_tester_routes_feedback_without_private_plan(self):
        self.implement()
        with self.assertRaisesRegex(ValueError, "不能测试"):
            self.w.claim("T1", "dev")
        claim = self.w.claim("T1", "tester")
        self.assertEqual("commit-a", self.w.context("T1", "tester")["implementation"]["result"]["revision"])
        with self.assertRaises(ValueError):
            self.w.context("T1", "dev")
        self.w.finish("T1", "tester", claim["epoch"],
                      {"revision": "commit-a", "passed": False, "feedback": "空用户名应返回错误",
                       "private": "hidden-test-marker；内部测试构造"})
        feedback = self.w.inbox("dev")[0]
        self.assertIn("空用户名", feedback["body"])
        self.assertNotIn("hidden-test-marker", feedback["body"])
        self.assertNotIn("hidden-test-marker", json.dumps(self.w.status()))
        self.assertEqual("todo", self.w.status()["tasks"][0]["status"])
        with self.assertRaises(ValueError):
            self.w.ack("backup", feedback["id"])
        self.w.ack("dev", feedback["id"])
        self.assertEqual([], self.w.inbox("dev"))

    def test_test_revision_must_match_and_new_revision_needs_new_test(self):
        self.implement()
        claim = self.w.claim("T1", "tester")
        with self.assertRaisesRegex(ValueError, "revision"):
            self.w.finish("T1", "tester", claim["epoch"],
                          {"revision": "wrong", "passed": True, "feedback": "通过"})
        self.w.finish("T1", "tester", claim["epoch"],
                      {"revision": "commit-a", "passed": False, "feedback": "需要修复"})
        dev_claim = self.w.claim("D1", "backup")
        self.w.finish("D1", "backup", dev_claim["epoch"], {"revision": "commit-b"})
        test_claim = self.w.claim("T1", "tester")
        self.w.finish("T1", "tester", test_claim["epoch"],
                      {"revision": "commit-b", "passed": True, "feedback": "验收通过"})
        self.assertEqual(["done", "done"], [x["status"] for x in self.w.status()["tasks"]])

    def test_research_stays_sealed_until_close_then_designated_synthesis(self):
        self.research()
        self.w.submit_report("R1", "r1", self.report("unique-first-draft"))
        self.assertEqual({}, self.w.view_run("R1", "r2")["reports"])
        self.assertEqual({}, self.w.view_run("R1", "human")["reports"])
        self.assertNotIn("unique-first-draft", json.dumps(self.w.status()))
        self.assertNotIn("unique-first-draft", self.w.snapshot())
        with self.assertRaises(ValueError):
            self.w.close_run("R1", "human")
        self.w.submit_report("R1", "r2", self.report("second-source"))
        self.assertEqual({}, self.w.view_run("R1", "human")["reports"])
        self.w.close_run("R1", "human")
        self.assertEqual(2, len(self.w.view_run("R1", "human")["reports"]))
        with self.assertRaises(ValueError):
            self.w.synthesize("R1", "r1", "非指定汇总者")
        self.w.synthesize("R1", "human", "保留来源和分歧，不能多数票替代证据")
        self.assertIn("分歧", self.w.view_run("R1", "human")["summary"])

    def test_independent_drafts_cannot_be_overwritten_or_forwarded(self):
        self.research()
        self.task()
        self.w.submit_report("R1", "r1", self.report("首稿"))
        with self.assertRaises(sqlite3.IntegrityError):
            self.w.submit_report("R1", "r1", self.report("偷改首稿"))
        with self.assertRaisesRegex(ValueError, "封存"):
            self.w.send("r1", "r2", "D1", "请先看我的结论")
        with self.assertRaises(ValueError):
            self.w.submit_report("R1", "r2", {"claims": [{"kind": "fact", "statement": "无来源", "sources": []}]})
        self.w.close_run("R1", "human", allow_missing=True)
        self.assertEqual(["r2"], self.w.view_run("R1", "human")["missing"])

    def test_human_can_take_over_with_checkpoint_and_use_same_task_interface(self):
        self.task()
        claim = self.w.claim("D1", "dev")
        self.w.checkpoint("D1", "dev", claim["epoch"], {"remaining": "人来补齐"})
        with self.assertRaises(ValueError):
            self.w.takeover("D1", "human", stopped=False)
        human = self.w.takeover("D1", "human", stopped=True)
        self.assertEqual("人来补齐", self.w.context("D1", "human")["checkpoint"]["remaining"])
        self.w.finish("D1", "human", human["epoch"], {"revision": "human-commit"})
        self.assertIn("待领取", self.w.snapshot())

    def test_external_supervisor_automatically_resumes_after_explicit_quota_exit(self):
        exhausted = self.adapter("exhausted", """
import json,sys
print(json.dumps({"type":"checkpoint","data":{"remaining":"resume-me"}}),flush=True)
sys.exit(75)
""")
        replacement = self.adapter("replacement", """
import json,os
from pathlib import Path
brief=json.loads(Path(os.environ["AGENT_WORKBENCH_BRIEF"]).read_text(encoding="utf-8"))
assert brief["checkpoint"]["remaining"]=="resume-me"
print("ordinary adapter log",flush=True)
print(json.dumps({"type":"result","data":{"revision":"resumed-commit"}}),flush=True)
""")
        self.w.join("quota", "额度用尽适配器", ["developer"], exhausted, [75], foreground=True)
        self.w.join("replacement", "接手适配器", ["developer"], replacement, [75], foreground=True)
        self.task(backups=["quota", "replacement"])
        outcome = self.w.dispatch("D1")
        self.assertEqual("awaiting_review", outcome["status"])
        actor = next(x for x in self.w.status()["agents"] if x["id"] == "quota")
        self.assertEqual("quota_exhausted", actor["state"])
        with self.w.connection() as conn:
            result = json.loads(self.w.row(conn, "tasks", "D1")["result"])
        self.assertEqual("resumed-commit", result["revision"])

    def test_unknown_adapter_lifetime_never_automatically_releases_scope(self):
        command = self.adapter("unknown", "import sys\nsys.exit(75)\n")
        self.w.join("unknown", "可能脱离前台的客户端", ["developer"], command, [75])
        self.task(backups=["unknown", "backup"])
        self.assertEqual("stopping", self.w.dispatch("D1")["status"])
        self.assertEqual("unknown", self.w.status()["tasks"][0]["owner"])
        self.assertEqual([], self.w.inbox("backup"))

    def test_unclassified_failure_is_not_quota_and_manual_transport_is_explicit(self):
        command = self.adapter("failure", "import sys\nsys.exit(9)\n")
        self.w.join("failure", "未知错误适配器", ["developer"], command, [75], foreground=True)
        self.task(backups=["failure", "backup"])
        self.assertEqual("adapter_error", self.w.dispatch("D1")["status"])
        actor = next(x for x in self.w.status()["agents"] if x["id"] == "failure")
        self.assertEqual("available", actor["state"])
        self.w.availability("failure", "paused")
        self.assertEqual("manual", self.w.dispatch("D1")["status"])
        self.assertEqual("backup", self.w.status()["tasks"][0]["owner"])

    def test_http_requires_capability_and_never_embeds_user_html(self):
        self.task()
        server, address = MODULE.make_server(self.w)
        base, token = address.split("#")
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with urlopen(base) as response:
                self.assertIn("textContent", response.read().decode("utf-8"))
            body = json.dumps({"operation": "status", "params": {}}).encode()
            with self.assertRaises(HTTPError) as error:
                urlopen(Request(base + "api", data=body))
            self.assertEqual(403, error.exception.code)
            headers = {"X-Workbench-Token": token, "Content-Type": "application/json"}
            with urlopen(Request(base + "api", data=body, headers=headers)) as response:
                self.assertEqual("D1", json.load(response)["tasks"][0]["id"])
            bad = json.dumps({"operation": "connection", "params": {}}).encode()
            with self.assertRaises(HTTPError) as error:
                urlopen(Request(base + "api", data=bad, headers=headers))
            self.assertEqual(400, error.exception.code)
        finally:
            server.shutdown()
            server.server_close()
            thread.join()

    def test_new_human_interface_has_operator_without_overwriting_existing_registry(self):
        fresh = self.root / "fresh"
        (fresh / ".agents").mkdir(parents=True)
        (fresh / ".agents/PROTOCOL.md").write_text("测试协议", encoding="utf-8")
        other = MODULE.Workbench(fresh)
        server, _ = MODULE.make_server(other)
        server.server_close()
        self.assertEqual(["human", "integrator"], other.status()["agents"][0]["roles"])
        server, _ = MODULE.make_server(self.w)
        server.server_close()
        self.assertEqual("人", next(x for x in self.w.status()["agents"] if x["id"] == "human")["client"])

    def test_research_candidate_handoff_preserves_actual_author_and_sealing(self):
        self.research()
        self.w.join("r3", "备用研究者", ["researcher"])
        self.w.create_task("RESEARCH1", "候选一调研", "research", ["results/R1/r1"],
                           "不采用调用者改写的题目", backups=["r1", "r3"], run="R1", slot="r1")
        old = self.w.claim("RESEARCH1", "r1")
        self.w.checkpoint("RESEARCH1", "r1", old["epoch"], {"remaining": "核实第二个来源"})
        self.w.stop("RESEARCH1", "quota_exhausted", True)
        new = self.w.claim("RESEARCH1", "r3")
        self.assertIn("公共问题", self.w.context("RESEARCH1", "r3")["contract"])
        with self.assertRaises(ValueError):
            self.w.submit_report("R1", "r1", self.report("旧作者抢写"))
        with self.assertRaises(ValueError):
            self.w.send("r3", "r2", "RESEARCH1", "偷看结论")
        self.w.finish("RESEARCH1", "r3", new["epoch"], {"report": self.report("接力完成候选一")})
        self.assertEqual({}, self.w.view_run("R1", "r1")["reports"])
        self.assertEqual("r3", self.w.view_run("R1", "r3")["reports"]["r1"]["author"])
        self.w.create_task("RESEARCH2", "候选二", "research", ["results/R1/r2"],
                           "固定问题", backups=["r2", "r3"], run="R1", slot="r2")
        with self.assertRaisesRegex(ValueError, "另一独立候选"):
            self.w.claim("RESEARCH2", "r3")
        second = self.w.claim("RESEARCH2", "r2")
        self.w.finish("RESEARCH2", "r2", second["epoch"], {"report": self.report("候选二")})
        self.w.close_run("R1", "human")
        self.assertEqual("r3", self.w.view_run("R1", "human")["reports"]["r1"]["author"])

    def test_research_does_not_reuse_another_independent_candidate_as_backup(self):
        self.research()
        with self.assertRaisesRegex(ValueError, "备用作者"):
            self.w.create_task("RESEARCH1", "候选一", "research", [], "公共问题",
                               backups=["r1", "r2"], run="R1", slot="r1")

    def test_earlier_runtime_database_keeps_reports_during_additive_migration(self):
        fresh = self.root / "old-runtime"
        (fresh / ".agents").mkdir(parents=True)
        (fresh / ".agents/PROTOCOL.md").write_text("测试协议", encoding="utf-8")
        other = MODULE.Workbench(fresh)
        other.directory.mkdir(parents=True)
        old_schema = MODULE.SCHEMA.replace(", run_id TEXT, slot TEXT", "").replace("author TEXT NOT NULL, ", "")
        with closing(sqlite3.connect(other.db)) as conn:
            conn.executescript(old_schema)
            conn.execute("INSERT INTO reports VALUES(?,?,?)", ("old-run", "r1", json.dumps(self.report("旧首稿"))))
            conn.commit()
        other.join("human", "人", ["human"])
        with other.connection() as conn:
            old = dict(conn.execute("SELECT * FROM reports").fetchone())
            self.assertEqual("r1", old["author"])
            self.assertIn("旧首稿", json.loads(old["report"])["claims"][0]["statement"])
        other.join("r1", "研究者", ["researcher"])
        other.create_run("R1", "问题", "标准", ["r1"], "human")
        other.submit_report("R1", "r1", self.report("新首稿"))


if __name__ == "__main__":
    unittest.main()
