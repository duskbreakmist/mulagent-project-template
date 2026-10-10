"""真实本地 Git 快照验证安装、更新与冲突保护；不访问 GitHub 或改全局 Git 配置。"""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

PROJECT = Path(__file__).resolve().parents[1]
SOURCE = PROJECT
SPEC = importlib.util.spec_from_file_location("template_manager", SOURCE / "tools/template_manager.py")
M = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


class TemplateManagerTests(unittest.TestCase):
    def setUp(self):
        self.temp_parent = PROJECT / ".test-tmp"
        self.temp_parent.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=self.temp_parent)
        self.folder = Path(self.temp.name)
        self.source = self.folder / "source"
        self.source.mkdir()
        self.required = json.loads((SOURCE / ".agents/template_manifest.json").read_text(encoding="utf-8"))["required"]
        for name in self.required:
            target = self.source / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(SOURCE / name, target)
        self.git(self.source, "init", "-b", "main")
        self.identity(self.source)
        self.commit(self.source)
        self.project = self.folder / "project"
        self.project.mkdir()
        self.git(self.project, "init", "-b", "main")
        self.identity(self.project)
        # 所有 Git 状态都在本测试的独立仓库，不借用父工作树或真实 origin。
        M.initialize(self.project, str(self.source), "main", no_git=True)
        self.commit(self.project)

    def tearDown(self):
        # 只递归清理本测试在指定父目录创建的临时副本。
        self.assertTrue(self.folder.resolve().is_relative_to(self.temp_parent.resolve()))
        self.temp.cleanup()

    def git(self, root, *args):
        return subprocess.run(["git", *args], cwd=root, capture_output=True, check=True).stdout.decode().strip()

    def identity(self, root):
        self.git(root, "config", "user.name", "Template Test Fixture")
        self.git(root, "config", "user.email", "fixture@example.invalid")

    def commit(self, root):
        self.git(root, "add", ".")
        self.git(root, "commit", "--allow-empty", "-m", "fixture snapshot")

    def digest_project(self):
        return {str(p.relative_to(self.project)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in self.project.rglob("*") if p.is_file() and ".git" not in p.relative_to(self.project).parts}

    def modify_source(self, name, text):
        (self.source / name).write_text(text, encoding="utf-8", newline="\n")
        self.commit(self.source)

    def plan_file(self):
        plans = list((self.project / M.REPORTS).glob("*/plan.json"))
        self.assertEqual(1, len(plans))
        return plans[0]

    def test_init_installs_metadata_and_no_template_remote(self):
        state = M.read_state(self.project)
        self.assertEqual(self.git(self.source, "rev-parse", "HEAD"), state["revision"])
        self.assertTrue((self.project / "tools/template_manager.py").exists())
        self.assertEqual("", self.git(self.project, "remote"))
        self.assertEqual(0, M.update(self.project, check=True))

    def test_new_git_init_and_commit_save_real_baseline(self):
        target = self.folder / "committed-project"
        target.mkdir()
        self.git(target, "init", "-b", "main")
        self.identity(target)
        M.initialize(target, str(self.source), "main", commit=True)
        self.assertEqual("", self.git(target, "status", "--porcelain"))
        self.assertEqual(str(target.resolve()), self.git(target, "config", "--get", "agent.coordinationRoot"))
        self.assertTrue(self.git(target, "rev-parse", "HEAD"))

    def test_init_refuses_existing_contents(self):
        target = self.folder / "nonempty"
        target.mkdir()
        (target / "my-code.py").write_text("keep", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "空目录"):
            M.initialize(target, str(self.source), "main")
        self.assertEqual("keep", (target / "my-code.py").read_text())
        self.assertFalse((target / "AGENTS.md").exists())

    def test_download_failure_does_not_create_destination(self):
        target = self.folder / "never-created"
        with self.assertRaises(ValueError):
            M.initialize(target, str(self.folder / "not-a-repository"), "main")
        self.assertFalse(target.exists())

    def test_preview_is_read_only(self):
        path = self.source / ".agents/PROTOCOL.md"
        self.modify_source(".agents/PROTOCOL.md", path.read_text(encoding="utf-8") + "\n上游规则补充。\n")
        before = self.digest_project()
        self.assertEqual(0, M.update(self.project, check=True))
        self.assertEqual(before, self.digest_project())
        self.assertFalse((self.project / M.REPORTS).exists())

    def test_update_changes_rules_but_preserves_project_state(self):
        local = {"agents_list.md": "# 实际登记\n", ".agents/coordination.md": "# 实际负责人\n",
                 ".agents/tasks/README.md": "# 实际索引\n", "docs/CURRENT.md": "# 实际进度\n",
                 "README.md": "# 我的业务工程\n", ".agents/tasks/DEV001.md": "# 实际任务\n- status: done\n"}
        for name, text in local.items():
            path = self.project / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        self.commit(self.project)
        self.modify_source(".agents/PROTOCOL.md", "# 新上游规则\n")
        self.assertEqual(0, M.update(self.project))
        self.assertEqual("# 新上游规则\n", (self.project / ".agents/PROTOCOL.md").read_text(encoding="utf-8"))
        for name, text in local.items():
            self.assertEqual(text, (self.project / name).read_text(encoding="utf-8"))

    def test_non_overlapping_custom_rules_are_merged(self):
        lines = "\n".join("line " + str(i) for i in range(20)) + "\n"
        self.modify_source("AGENTS.md", lines)
        # 采用新的已知基线，再制造不同位置的双边修改。
        self.assertEqual(0, M.update(self.project))
        self.commit(self.project)
        (self.project / "AGENTS.md").write_text(lines.replace("line 1\n", "LOCAL\n"), encoding="utf-8")
        self.commit(self.project)
        self.modify_source("AGENTS.md", lines.replace("line 18\n", "UPSTREAM\n"))
        self.assertEqual(0, M.update(self.project))
        merged = (self.project / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("LOCAL", merged)
        self.assertIn("UPSTREAM", merged)

    def create_conflict(self):
        (self.project / "AGENTS.md").write_text("# 本地完全替换\n", encoding="utf-8")
        self.commit(self.project)
        self.modify_source("AGENTS.md", "# 上游完全替换\n")
        before = (self.project / "AGENTS.md").read_bytes(), (self.project / M.STATE).read_bytes()
        self.assertEqual(2, M.update(self.project))
        self.assertEqual(before, ((self.project / "AGENTS.md").read_bytes(), (self.project / M.STATE).read_bytes()))
        return self.plan_file()

    def test_conflict_leaves_originals_and_can_be_manually_applied(self):
        plan = self.create_conflict()
        candidate = plan.parent / "proposed/AGENTS.md"
        self.assertIn("<<<<<<<", candidate.read_text(encoding="utf-8"))
        candidate.write_text("# 保留本地与上游的人工决定\n", encoding="utf-8")
        M.apply_plan(self.project, plan)
        self.assertEqual("# 保留本地与上游的人工决定\n",
                         (self.project / "AGENTS.md").read_text(encoding="utf-8"))
        self.assertEqual(self.git(self.source, "rev-parse", "HEAD"), M.read_state(self.project)["revision"])

    def test_conflict_markers_cannot_be_applied(self):
        plan = self.create_conflict()
        before = self.digest_project()
        with self.assertRaisesRegex(ValueError, "冲突标记"):
            M.apply_plan(self.project, plan)
        self.assertEqual(before, self.digest_project())

    def test_stale_plan_does_not_overwrite_new_edits(self):
        plan = self.create_conflict()
        (plan.parent / "proposed/AGENTS.md").write_text("# resolved\n", encoding="utf-8")
        (self.project / "AGENTS.md").write_text("# newer local edit\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "已变"):
            M.apply_plan(self.project, plan)
        self.assertEqual("# newer local edit\n", (self.project / "AGENTS.md").read_text(encoding="utf-8"))

    def test_deleted_local_managed_file_is_not_restored(self):
        (self.project / "AGENTS.md").unlink()
        self.commit(self.project)
        self.modify_source("AGENTS.md", "# 上游更新\n")
        self.assertEqual(0, M.update(self.project))
        self.assertFalse((self.project / "AGENTS.md").exists())

    def test_upstream_removal_does_not_delete_local_file(self):
        manifest = self.source / ".agents/template_manifest.json"
        data = json.loads(manifest.read_text(encoding="utf-8"))
        data["required"].remove("template_readme.md")
        manifest.write_text(json.dumps(data), encoding="utf-8")
        self.commit(self.source)
        self.assertEqual(0, M.update(self.project))
        self.assertTrue((self.project / "template_readme.md").exists())

    def test_new_file_is_added_from_manifest(self):
        name = ".agents/guides/new.md"
        (self.source / name).write_text("# 新指南\n", encoding="utf-8")
        manifest = self.source / ".agents/template_manifest.json"
        data = json.loads(manifest.read_text(encoding="utf-8"))
        data["required"].append(name)
        manifest.write_text(json.dumps(data), encoding="utf-8")
        self.commit(self.source)
        self.assertEqual(0, M.update(self.project))
        self.assertTrue((self.project / name).exists())

    def test_adopt_does_not_guess_unknown_baseline_or_overwrite_files(self):
        (self.project / M.STATE).unlink()
        (self.project / "AGENTS.md").write_text("# 定制旧模板\n", encoding="utf-8")
        before = (self.project / "AGENTS.md").read_bytes()
        state = M.adopt(self.project, str(self.source), "main")
        self.assertIsNone(state["files"]["AGENTS.md"]["revision"])
        self.assertEqual(before, (self.project / "AGENTS.md").read_bytes())
        self.commit(self.project)
        self.assertEqual(2, M.update(self.project))

    def test_dirty_project_refuses_writes_but_can_preview(self):
        (self.project / "README.md").write_text("# 未提交内容\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "未提交"):
            M.update(self.project)
        self.assertEqual(0, M.update(self.project, check=True))

    def test_existing_lock_is_not_deleted(self):
        with M.write_lock(self.project):
            before = (self.project / M.LOCK).read_bytes()
            with self.assertRaisesRegex(ValueError, "锁已存在"):
                with M.write_lock(self.project):
                    pass
            self.assertEqual(before, (self.project / M.LOCK).read_bytes())

    def test_manifest_rejects_runtime_records_and_path_escape(self):
        manifest = self.source / ".agents/template_manifest.json"
        original = manifest.read_text(encoding="utf-8")
        for bad in ("../outside.md", ".agents/tasks/REAL001.md", ".git/config"):
            data = json.loads(original)
            data["required"].append(bad)
            manifest.write_text(json.dumps(data), encoding="utf-8")
            self.commit(self.source)
            with self.assertRaises(ValueError):
                M.update(self.project, check=True)

    def test_repeated_update_is_idempotent_after_commit(self):
        path = self.source / "template_readme.md"
        self.modify_source("template_readme.md", path.read_text(encoding="utf-8") + "\nnew text\n")
        self.assertEqual(0, M.update(self.project))
        self.commit(self.project)
        before = self.digest_project()
        self.assertEqual(0, M.update(self.project))
        self.assertEqual(before, self.digest_project())

    def test_write_failure_rolls_back_earlier_files(self):
        self.modify_source("AGENTS.md", "# new rule\n")
        self.modify_source("template_readme.md", "# new guide\n")
        before = {name: (self.project / name).read_bytes() for name in ("AGENTS.md", "template_readme.md", M.STATE)}
        original_write = M.atomic_write
        def fail(path, data):
            if path == self.project / "template_readme.md":
                raise OSError("simulated disk failure")
            return original_write(path, data)
        with patch.object(M, "atomic_write", side_effect=fail):
            with self.assertRaises(OSError):
                M.update(self.project)
        for name, data in before.items():
            self.assertEqual(data, (self.project / name).read_bytes())


if __name__ == "__main__":
    unittest.main()
