"""验证初始化器的并发、恢复和单文件可移植性，不依赖外部包。"""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

PROJECT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("agent_bootstrap", PROJECT / "tools/agent_bootstrap.py")
BOOT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BOOT)


class BootstrapTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "AGENTS.md").write_text("# Test project\n", encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def digest(self):
        return {str(path.relative_to(self.root)): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in self.root.rglob("*") if path.is_file()}

    def test_idempotent_preserves_customized_registry(self):
        BOOT.initialize(self.root)
        registry = self.root / "agents_list.md"
        registry.write_text("# 我的登记表\n\n自定义内容\n", encoding="utf-8")
        before = self.digest()
        BOOT.initialize(self.root)
        self.assertEqual(before, self.digest())

    def test_resume_after_marker_missing(self):
        BOOT.initialize(self.root)
        (self.root / ".agents/.bootstrap-v1").unlink()
        (self.root / ".agents/messages/README.md").unlink()
        registry = self.root / "agents_list.md"
        original = registry.read_bytes()
        BOOT.initialize(self.root)
        self.assertEqual(original, registry.read_bytes())
        BOOT.check(self.root)

    def test_marker_does_not_hide_missing_file(self):
        BOOT.initialize(self.root)
        (self.root / ".agents/tasks/TEMPLATE.md").unlink()
        with self.assertRaises(ValueError):
            BOOT.check(self.root)
        BOOT.initialize(self.root)
        BOOT.check(self.root)

    def test_existing_empty_file_is_not_overwritten(self):
        (self.root / "agents_list.md").touch()
        with self.assertRaisesRegex(ValueError, "不完整"):
            BOOT.initialize(self.root)
        self.assertEqual(b"", (self.root / "agents_list.md").read_bytes())
        self.assertFalse((self.root / ".agents/.bootstrap-v1").exists())

    def test_unknown_version_is_not_overwritten(self):
        BOOT.initialize(self.root)
        marker = self.root / ".agents/.bootstrap-v1"
        data = json.loads(marker.read_text(encoding="utf-8"))
        data["version"] = 99
        marker.write_text(json.dumps(data), encoding="utf-8")
        before = self.digest()
        with self.assertRaisesRegex(ValueError, "未知"):
            BOOT.initialize(self.root)
        self.assertEqual(before, self.digest())

    def test_second_process_cannot_initialize_under_lock(self):
        with BOOT.bootstrap_lock(self.root):
            lock = self.root / ".agents/.bootstrap.lock"
            original = lock.read_bytes()
            result = subprocess.run(
                [sys.executable, str(PROJECT / "tools/agent_bootstrap.py"),
                 "--root", str(self.root)], capture_output=True)
            self.assertEqual(1, result.returncode)
            self.assertEqual(original, lock.read_bytes())
            self.assertFalse((self.root / "agents_list.md").exists())
        BOOT.initialize(self.root)
        BOOT.check(self.root)

    def test_stale_lock_is_not_automatically_deleted(self):
        directory = self.root / ".agents"
        directory.mkdir()
        lock = directory / ".bootstrap.lock"
        lock.write_text('{"pid": 0, "host": "unknown"}', encoding="utf-8")
        before = lock.read_bytes()
        with self.assertRaisesRegex(ValueError, "锁已存在"):
            BOOT.initialize(self.root)
        self.assertEqual(before, lock.read_bytes())

    def test_path_escape_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "路径逃逸"):
            BOOT.safe_path(self.root, "../outside")

    def test_publish_does_not_replace_existing_target(self):
        path = self.root / "agents_list.md"
        path.write_bytes(b"original")
        BOOT.publish_once(path, "replacement")
        self.assertEqual(b"original", path.read_bytes())
        self.assertEqual([], list(self.root.glob(".bootstrap-*")))

    def test_old_single_file_entry_points_to_split_template(self):
        text = (PROJECT / "gpt/templates/AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("../project_templateA/template_readme.md", text)
        self.assertNotIn("```python", text)
        self.assertTrue((PROJECT / "gpt/project_templateA/AGENTS.md").is_file())

    def test_worktree_uses_shared_config_but_files_are_snapshots(self):
        BOOT.initialize(self.root)

        def git(*args, cwd=None):
            return subprocess.run(
                ["git", *args], cwd=cwd or self.root,
                capture_output=True, text=True, encoding="utf-8", check=True).stdout.strip()

        git("init", "-b", "main")
        git("add", "AGENTS.md", "agents_list.md", ".agents")
        git("-c", "user.name=Bootstrap Test", "-c", "user.email=test@example.invalid",
            "commit", "-m", "test snapshot")
        git("config", "--local", "agent.coordinationRoot", str(self.root))
        worker = self.root / ".worktrees/worker"
        git("worktree", "add", "-b", "agent/test/COLLAB001", str(worker), "main")
        try:
            board = self.root / ".agents/tasks/README.md"
            board.write_text(board.read_text(encoding="utf-8") + "\n主目录新进展\n", encoding="utf-8")
            self.assertEqual(self.root.resolve(),
                             Path(git("config", "--get", "agent.coordinationRoot",
                                      cwd=worker)).resolve())
            self.assertNotEqual(board.read_bytes(),
                                (worker / ".agents/tasks/README.md").read_bytes())
        finally:
            # 测试工作树无修改；只移除本测试创建的工作树，不使用 force。
            git("worktree", "remove", str(worker))


if __name__ == "__main__":
    unittest.main()
