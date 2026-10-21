"""旁路双仓库的真实 Git 验收；不访问远程或修改用户 Git 配置。"""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

PROJECT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, PROJECT / "tools" / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


M, C = load("template_manager"), load("check_template")


class SidecarTests(unittest.TestCase):
    def setUp(self):
        parent = PROJECT / ".test-tmp"
        parent.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=parent)
        self.addCleanup(self.temp.cleanup)
        output = contextlib.redirect_stdout(io.StringIO())
        output.__enter__()
        self.addCleanup(output.__exit__, None, None, None)
        self.folder = Path(self.temp.name).resolve()
        self.source = self.folder / "source"
        self.repo(self.source)
        required = json.loads((PROJECT / ".agents/template_manifest.json").read_text(encoding="utf-8"))["required"]
        for name in required:
            target = self.source / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(PROJECT / name, target)
        self.commit(self.source)
        self.business = self.folder / "业务 工程 [app]"
        self.repo(self.business)
        (self.business / "README.md").write_text("# existing business\n", encoding="utf-8")
        (self.business / "AGENTS.md").write_text("# existing rules\n", encoding="utf-8")
        self.commit(self.business)
        self.collab = self.folder / "协作 [notes]"
        self.repo(self.collab)

    def git(self, root, *args):
        return subprocess.run(["git", *map(str, args)], cwd=root, capture_output=True,
                              check=True).stdout.decode("utf-8").strip()

    def repo(self, root):
        root.mkdir()
        self.git(root, "init", "-b", "main")
        self.git(root, "config", "user.name", "Sidecar Fixture")
        self.git(root, "config", "user.email", "sidecar@example.invalid")

    def commit(self, root):
        self.git(root, "add", ".")
        self.git(root, "commit", "--allow-empty", "-m", "fixture")

    def install(self):
        return M.initialize(self.collab, str(self.source), "main", commit=True,
                            mode="sidecar", project_root=self.business)

    def snapshot(self):
        # tracked／untracked 内容、HEAD、索引、配置中非旁路部分都应保持。
        files = {str(p.relative_to(self.business)): p.read_bytes() for p in self.business.rglob("*")
                 if p.is_file() and ".git" not in p.relative_to(self.business).parts}
        return (files, self.git(self.business, "rev-parse", "HEAD"),
                self.git(self.business, "diff", "--cached", "--binary"),
                self.git(self.business, "status", "--porcelain"),
                self.git(self.business, "config", "--local", "--get", "user.name"))

    def test_install_entry_and_update_preserve_dirty_business(self):
        (self.business / "README.md").write_text("# staged change\n", encoding="utf-8")
        self.git(self.business, "add", "README.md")
        (self.business / "untracked.txt").write_text("keep\n", encoding="utf-8")
        before = self.snapshot()
        self.install()
        self.assertEqual(before, self.snapshot())
        self.assertEqual("", self.git(self.collab, "status", "--porcelain"))
        self.assertEqual("", self.git(self.collab, "remote"))
        descriptor = M.sidecar_descriptor(self.collab)
        self.assertNotIn(str(self.business), (self.collab / M.SIDECAR).read_text())
        self.assertEqual("sidecar", M.read_state(self.collab)["installation_mode"])
        self.assertEqual(len(M.read_state(self.collab)["files"]), C.validate(self.collab))
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            M.entry(self.collab)
        self.assertIn("当前文件夹是协作文件夹", output.getvalue())
        self.assertIn(str(self.business), output.getvalue())
        self.assertIn("首次回复必须", output.getvalue())
        self.assertIn("sidecar.json", (self.collab / "AGENTS.md").read_text(encoding="utf-8"))
        self.assertIn("首次回复必须", (self.collab / "AGENTS.md").read_text(encoding="utf-8"))
        rule = self.source / ".agents/guides/git.md"
        rule.write_text(rule.read_text(encoding="utf-8") + "\n旁路回归变更。\n", encoding="utf-8")
        self.commit(self.source)
        M.update(self.collab, commit=True)
        self.assertEqual(before, self.snapshot())
        self.assertEqual(descriptor, M.sidecar_descriptor(self.collab))
        self.assertIn("[TEMPLATE][update]", self.git(self.collab, "log", "-1", "--format=%s"))
        C.validate(self.collab)

    def test_installed_cli_entry_and_bind_are_independent(self):
        self.install()
        command = [sys.executable, "-X", "utf8", "tools/template_manager.py"]
        for args in (("entry",), ("bind", "--project-root", str(self.business))):
            result = subprocess.run(command + list(args), cwd=self.collab, capture_output=True)
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn(str(self.business).encode("utf-8"), result.stdout)
        result = subprocess.run([sys.executable, "tools/check_template.py"], cwd=self.collab,
                                capture_output=True)
        self.assertEqual(0, result.returncode, result.stderr)

    def test_invalid_modes_missing_git_and_nested_roots_do_not_install(self):
        for mode, project, no_git in (("in-tree", self.business, False),
                                      ("sidecar", None, False), ("sidecar", self.business, True),
                                      ("sidecar", self.folder, False)):
            with self.subTest(mode=mode, project=project, no_git=no_git), self.assertRaises(ValueError):
                M.initialize(self.collab, str(self.source), "main", mode=mode,
                             project_root=project, no_git=no_git)
        for target in (self.business, self.business / "collab"):
            with self.assertRaisesRegex(ValueError, "嵌套"):
                M.initialize(target, str(self.source), "main", mode="sidecar", project_root=self.business)
        self.assertFalse((self.collab / "AGENTS.md").exists())

    def test_existing_task_board_and_binding_are_not_taken_over(self):
        (self.business / ".agents").mkdir()
        protocol = self.business / ".agents/PROTOCOL.md"
        protocol.write_text("existing board", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "已有模板"):
            self.install()
        protocol.unlink()
        self.git(self.business, "config", "agent.coordinationRoot", str(self.source))
        with self.assertRaisesRegex(ValueError, "可达"):
            self.install()
        self.assertFalse((self.collab / M.STATE).exists())

    def test_second_install_is_rejected_without_changing_original_binding(self):
        self.install()
        original = self.collab
        self.collab = self.folder / "second"
        self.repo(self.collab)
        with self.assertRaisesRegex(ValueError, "另一协作"):
            self.install()
        self.assertEqual(str(original), self.git(self.business, "config", "agent.coordinationRoot"))
        self.assertFalse((self.collab / M.STATE).exists())

    def test_moved_directories_fail_until_explicit_bind(self):
        self.install()
        business = self.folder / "moved-business"
        collab = self.folder / "moved-collab"
        self.business.rename(business)
        self.collab.rename(collab)
        self.business, self.collab = business, collab
        for checker in (M.check_sidecar, C.check_sidecar):
            with self.assertRaises((ValueError, OSError)):
                checker(collab)
        M.bind_sidecar(collab, business)
        self.assertEqual(business, M.check_sidecar(collab))
        C.validate(collab)
        self.assertEqual("", self.git(collab, "status", "--porcelain"))

    def test_clones_can_bind_without_machine_paths_in_committed_files(self):
        self.install()
        business, collab = self.folder / "clone-business", self.folder / "clone-collab"
        self.git(self.folder, "clone", "--quiet", self.business, business)
        self.git(self.folder, "clone", "--quiet", self.collab, collab)
        with self.assertRaises(ValueError):
            M.check_sidecar(collab)
        M.bind_sidecar(collab, business)
        C.validate(collab)
        self.assertEqual("", self.git(collab, "status", "--porcelain"))

    def test_unrelated_repo_and_conflicting_id_fail_read_only_checks(self):
        self.install()
        other = self.folder / "unrelated"
        self.repo(other)
        (other / "different.txt").write_text("different history", encoding="utf-8")
        self.commit(other)
        with self.assertRaises(ValueError):
            M.bind_sidecar(self.collab, other)
        self.git(self.business, "config", "agent.sidecarId", "a" * 32)
        for checker in (M.check_sidecar, C.check_sidecar):
            with self.assertRaises(ValueError):
                checker(self.collab)
        before = (self.collab / M.STATE).read_bytes()
        with self.assertRaises(ValueError):
            M.update(self.collab, check=True)
        self.assertEqual(before, (self.collab / M.STATE).read_bytes())

    def test_binding_failure_restores_configuration_and_releases_lock(self):
        self.install()
        self.git(self.business, "config", "--unset-all", "agent.coordinationRoot")
        self.git(self.business, "config", "--unset-all", "agent.sidecarId")
        actual = M.run_git

        def fail(*args, **kwargs):
            if args[:3] == ("config", "--local", "agent.projectRoot"):
                raise ValueError("simulated config write failure")
            return actual(*args, **kwargs)

        with patch.object(M, "run_git", side_effect=fail), self.assertRaisesRegex(ValueError, "simulated"):
            M.bind_sidecar(self.collab, self.business)
        self.assertIsNone(M.local_config(self.business, "agent.sidecarId"))
        self.assertIsNone(M.local_config(self.business, "agent.coordinationRoot"))
        self.assertFalse((self.business / ".git/agent-sidecar.lock").exists())
        M.bind_sidecar(self.collab, self.business)
        C.validate(self.collab)

    def test_old_source_is_rejected_for_install_and_update(self):
        self.install()
        manifest = self.source / ".agents/template_manifest.json"
        value = json.loads(manifest.read_text(encoding="utf-8"))
        value["required"].remove("docs/sidecar.md")
        manifest.write_text(json.dumps(value), encoding="utf-8")
        self.commit(self.source)
        before = (self.collab / M.STATE).read_bytes()
        with self.assertRaisesRegex(ValueError, "不支持旁路"):
            M.update(self.collab, check=True)
        self.assertEqual(before, (self.collab / M.STATE).read_bytes())
        other = self.folder / "new-business"
        self.git(self.folder, "clone", "--quiet", self.business, other)
        target = self.folder / "new-collab"
        self.repo(target)
        with self.assertRaisesRegex(ValueError, "不支持旁路"):
            M.initialize(target, str(self.source), "main", mode="sidecar", project_root=other)
        self.assertFalse((target / M.STATE).exists())

    def test_missing_marker_and_tampered_installation_mode_are_rejected(self):
        self.install()
        marker = self.collab / M.SIDECAR
        saved = marker.read_bytes()
        marker.unlink()
        for checker in (M.check_sidecar, C.check_sidecar):
            with self.assertRaises((ValueError, OSError)):
                checker(self.collab)
        marker.write_bytes(saved)
        state = M.read_state(self.collab)
        state["installation_mode"] = "in-tree"
        (self.collab / M.STATE).write_text(json.dumps(state), encoding="utf-8")
        for checker in (M.check_sidecar, C.check_sidecar):
            with self.assertRaises(ValueError):
                checker(self.collab)

    def test_business_worktrees_share_the_single_binding(self):
        self.install()
        worktree = self.folder / "business-worker"
        self.git(self.business, "worktree", "add", "--detach", worktree)
        self.assertEqual(str(self.collab), self.git(worktree, "config", "agent.coordinationRoot"))
        M.bind_sidecar(self.collab, worktree)
        self.assertEqual(worktree, M.check_sidecar(self.collab))
        C.validate(self.collab)

    def test_install_creates_missing_collaboration_directory(self):
        # 工程外新目录没有父 Git；覆盖常见的 --root 尚不存在路径。
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder).resolve() / "new-collab"
            M.initialize(target, str(self.source), "main", mode="sidecar", project_root=self.business)
            self.assertEqual(self.business, M.check_sidecar(target))
            C.validate(target)

    def test_collaboration_cannot_switch_to_second_accessible_business_clone(self):
        self.install()
        other = self.folder / "other-business"
        self.git(self.folder, "clone", "--quiet", self.business, other)
        with self.assertRaisesRegex(ValueError, "另一可达业务"):
            M.bind_sidecar(self.collab, other)
        self.assertEqual(self.business, M.check_sidecar(self.collab))

    def test_apply_cannot_switch_mode_or_overwrite_sidecar_descriptor(self):
        self.install()
        rule = self.source / ".agents/guides/git.md"
        rule.write_text(rule.read_text(encoding="utf-8") + "\n新规则。\n", encoding="utf-8")
        self.commit(self.source)
        with patch.object(M, "apply_plan", side_effect=ValueError("leave plan")):
            with self.assertRaisesRegex(ValueError, "leave plan"):
                M.update(self.collab)
        plan_path = next((self.collab / M.REPORTS).glob("*/plan.json"))
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        plan["next_state"]["installation_mode"] = "in-tree"
        plan_path.write_text(json.dumps(plan), encoding="utf-8")
        before = (self.collab / M.STATE).read_bytes()
        with self.assertRaisesRegex(ValueError, "切换安装模式"):
            M.apply_plan(self.collab, plan_path)
        self.assertEqual(before, (self.collab / M.STATE).read_bytes())
        plan["next_state"]["installation_mode"] = "sidecar"
        plan["entries"][0]["path"] = M.SIDECAR
        plan_path.write_text(json.dumps(plan), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "保留路径"):
            M.apply_plan(self.collab, plan_path)


if __name__ == "__main__":
    unittest.main()
