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

    def test_actual_install_runs_its_own_checker_without_development_assets(self):
        before = self.digest_project()
        checked = subprocess.run([sys.executable, "tools/check_template.py", "--root", "."],
                                 cwd=self.project, capture_output=True)
        self.assertEqual(0, checked.returncode, checked.stderr)
        self.assertEqual(before, self.digest_project())
        self.assertFalse((self.project / "tests").exists())
        self.assertFalse((self.project / "docs/maintenance").exists())

    def test_business_task_delivery_requires_real_project_tests(self):
        # 用已安装副本的CLI初始化另一空工程，真实形成BOOTSTRAP基线。
        project = self.folder / "business-delivery"
        project.mkdir()
        self.git(project, "init", "-b", "main")
        self.identity(project)
        installed = subprocess.run([sys.executable, str(self.project / "tools/template_manager.py"),
                                   "init", "--root", str(project), "--source", str(self.source),
                                   "--ref", "main", "--commit"], capture_output=True)
        self.assertEqual(0, installed.returncode, installed.stderr)
        self.assertIn("[BOOTSTRAP][template]", self.git(project, "log", "-1", "--format=%s"))
        self.assertEqual("", self.git(project, "status", "--porcelain"))
        self.assertEqual(str(project.resolve()), self.git(project, "config", "--get", "agent.coordinationRoot"))
        self.assertFalse((project / "tests").exists())

        def write(name, text):
            path = project / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8", newline="\n")

        def execute(*args):
            return subprocess.run([sys.executable, *args], cwd=project, capture_output=True)

        write("README.md", """# 标签示例工程

## 工程约定

- 技术栈／依赖：Python 3.9+标准库，无第三方依赖或锁文件。
- 目录：app.py提供标签规范化，tests/存业务验收。
- 风格／错误：snake_case；空标签ValueError，非字符串TypeError。
- 命令：python -m unittest discover -s tests -v；python -m py_compile app.py。
- 忽略：沿用.gitignore的__pycache__/和*.pyc，不使用凭据或本地配置。
- 验收／发布：合并Unicode空白、拒绝无效标签；单个fixture核对并提交，无部署／业务CI。
""")
        write("agents_list.md", "# 参与者\n\nworkflow-fixture：隔离测试执行者，不代表在线AI。\n")
        write(".agents/coordination.md", "# 示例协调\n\n- shared_integrator: workflow-fixture\n"
              "- selection_source: 本回归固定的单人示例契约\n- state: active\n"
              "- default_collaboration_mode: serial\n")
        task = (project / ".agents/tasks/TEMPLATE-lite.md").read_text(encoding="utf-8")
        task = (task.replace("<TASK-ID>", "DEV001").replace("<标题>", "规范化标签")
                .replace("<agent-id>", "workflow-fixture").replace("YYYY-MM-DD", "2026-10-11")
                .replace("- status: todo", "- status: in_progress", 1)
                .replace("- assignment: proposed", "- assignment: accepted", 1)
                .replace("mode_source: 填写真实的用户指令／父任务／已授权工程默认来源",
                         "mode_source: 本回归固定的单人示例契约")
                .replace("base_commit: 待记录", "base_commit: " + self.git(project, "rev-parse", "HEAD")))
        task = task.replace("## Objective\n", "## Objective\n\n"
                            "按[工程约定](../../README.md#工程约定)合并标签空白并拒绝无效输入；"
                            "验收命令 python -m unittest discover -s tests -v。\n", 1)
        write(".agents/tasks/DEV001.md", task)
        write(".agents/tasks/README.md", "# 任务索引\n\n[DEV001](DEV001.md)：in_progress，workflow-fixture。\n")
        write("docs/CURRENT.md", "# 当前记录\n\n[DEV001](../.agents/tasks/DEV001.md)：正在实现。\n")
        checker = ("tools/check_template.py", "--root", ".")
        self.assertEqual(0, execute(*checker).returncode)
        bad_app = """def normalize_label(text):
    if not isinstance(text, str):
        raise TypeError("label must be a string")
    # 标签必须非空，所有Unicode空白按契约合并。
    text = text.strip()
    if not text:
        raise ValueError("label must not be empty")
    return text
"""
        write("app.py", bad_app)
        write("tests/test_labels.py", """import unittest
from app import normalize_label


class LabelTests(unittest.TestCase):
    def test_merge_unicode_whitespace(self):
        self.assertEqual("项目 标签", normalize_label("  项目\\u3000 \\t标签\\n"))

    def test_plain_label(self):
        self.assertEqual("demo", normalize_label("demo"))

    def test_invalid_input(self):
        with self.assertRaises(ValueError):
            normalize_label(" \\t\\n")
        with self.assertRaises(TypeError):
            normalize_label(None)
""")
        test_command = ("-m", "unittest", "discover", "-s", "tests", "-v")
        failed = execute(*test_command)
        self.assertNotEqual(0, failed.returncode)
        self.assertIn(b"FAIL: test_merge_unicode_whitespace", failed.stderr)
        # 文件完整性不认证业务行为：错误实现仍可通过模板检查。
        self.assertEqual(0, execute(*checker).returncode)
        write("app.py", bad_app.replace("text = text.strip()", 'text = " ".join(text.split())'))
        passed = execute(*test_command)
        self.assertEqual(0, passed.returncode, passed.stderr)
        self.assertIn(b"Ran 3 tests", passed.stderr)
        self.assertEqual(0, execute("-m", "py_compile", "app.py").returncode)
        task = task.replace("- status: in_progress", "- status: done", 1)
        task += "\n## 示例验收结果\n\n业务测试3项通过，语法检查通过；记录过失败与修复。"
        task += "单fixture核对代码／测试／契约，不声称独立AI审查或产品上线。\n"
        write(".agents/tasks/DEV001.md", task)
        write(".agents/tasks/README.md", "# 最近完成\n\n[DEV001](DEV001.md)：done，workflow-fixture。\n")
        write("docs/CURRENT.md", "# 最近完成\n\n[DEV001](../.agents/tasks/DEV001.md)：标签规范化，业务3项通过。\n")
        files = ("README.md", "agents_list.md", ".agents/coordination.md", ".agents/tasks/DEV001.md",
                 ".agents/tasks/README.md", "docs/CURRENT.md", "app.py", "tests/test_labels.py")
        self.git(project, "add", "--", *files)
        self.git(project, "diff", "--cached", "--check")
        reviewed = self.git(project, "diff", "--cached", "--", "app.py", "tests/test_labels.py")
        self.assertIn('" ".join(text.split())', reviewed)
        self.assertIn("test_merge_unicode_whitespace", reviewed)
        self.git(project, "commit", "-m", "[DEV001][workflow-fixture] normalize labels")
        self.assertEqual("", self.git(project, "status", "--porcelain"))
        self.assertEqual("2", self.git(project, "rev-list", "--count", "HEAD"))
        self.assertEqual("", self.git(project, "remote"))
        self.assertEqual(0, execute(*checker).returncode)
        print("BUSINESS_WORKFLOW_OK task=DEV001 tests=3 red=observed commits=2 clean=yes",
              self.git(project, "rev-parse", "HEAD"))

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

    def test_upstream_core_removal_is_rejected_before_installation(self):
        path = self.source / ".agents/template_manifest.json"
        original = path.read_text(encoding="utf-8")
        for name in ("tools/check_template.py", ".agents/guides/git.md"):
            with self.subTest(name=name):
                data = json.loads(original)
                data["required"].remove(name)
                path.write_text(json.dumps(data), encoding="utf-8")
                self.commit(self.source)
                target = self.folder / "invalid-source-target"
                with self.assertRaisesRegex(ValueError, "核心协议"):
                    M.initialize(target, str(self.source), "main")
                self.assertFalse(target.exists())

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


    def test_relative_source_is_persisted_independently_of_cwd(self):
        target = self.folder / "relative-project"
        target.mkdir()
        self.git(target, "init", "-b", "main")
        self.identity(target)
        with patch("os.getcwd", return_value=str(self.folder)):
            M.initialize(target, "source", "main", no_git=True)
        self.commit(target)
        self.assertEqual(str(self.source.resolve()), M.read_state(target)["source"])
        with patch("os.getcwd", return_value=str(target)):
            self.assertEqual(0, M.update(target, check=True))

    def test_explicit_source_recovers_legacy_metadata_without_preview_writes(self):
        state = M.read_state(self.project)
        state["source"] = "."
        (self.project / M.STATE).write_text(json.dumps(state), encoding="utf-8")
        self.commit(self.project)
        before = self.digest_project()
        with self.assertRaisesRegex(ValueError, "update --source"):
            M.update(self.project, check=True)
        self.assertEqual(0, M.update(self.project, check=True, source=str(self.source)))
        self.assertEqual(before, self.digest_project())
        self.assertEqual(0, M.update(self.project, source=str(self.source)))
        self.assertEqual(str(self.source.resolve()), M.read_state(self.project)["source"])

    def test_upstream_rejects_development_assets_before_initialization(self):
        name = "docs/maintenance/COORDINATION.md"
        path = self.source / name
        path.parent.mkdir(parents=True)
        path.write_text("# 实际维护身份\n", encoding="utf-8")
        manifest = self.source / ".agents/template_manifest.json"
        data = json.loads(manifest.read_text(encoding="utf-8"))
        data["required"].append(name)
        manifest.write_text(json.dumps(data), encoding="utf-8")
        self.commit(self.source)
        target = self.folder / "must-not-exist"
        with self.assertRaisesRegex(ValueError, "开发资产"):
            M.initialize(target, str(self.source), "main")
        self.assertFalse(target.exists())

    def test_cli_selects_release_tag_without_changing_preview_baseline(self):
        original = self.digest_project()
        self.modify_source("template_readme.md", "# Release candidate\n")
        self.git(self.source, "tag", "v-next")
        command = [sys.executable, str(SOURCE / "tools/template_manager.py"), "update",
                   "--root", str(self.project), "--ref", "v-next"]
        preview = subprocess.run([*command, "--check"], capture_output=True)
        self.assertEqual(0, preview.returncode, preview.stdout + preview.stderr)
        self.assertEqual(original, self.digest_project())
        applied = subprocess.run(command, capture_output=True)
        self.assertEqual(0, applied.returncode, applied.stdout + applied.stderr)
        self.assertEqual("v-next", M.read_state(self.project)["ref"])
        self.assertEqual("# Release candidate\n", (self.project / "template_readme.md").read_text())
        self.commit(self.project)
        self.modify_source("template_readme.md", "# Later main\n")
        # 不带--ref的后续更新仍固定标签，不能悄悄追随main。
        self.assertEqual(0, M.update(self.project))
        self.assertEqual("# Release candidate\n", (self.project / "template_readme.md").read_text())

    def test_missing_release_ref_leaves_project_unchanged(self):
        before = self.digest_project()
        with self.assertRaisesRegex(ValueError, "Git 操作失败"):
            M.update(self.project, ref="missing-release")
        self.assertEqual(before, self.digest_project())

    def test_conflicted_release_switch_saves_ref_only_when_applied(self):
        (self.project / "AGENTS.md").write_text("# 本地完全替换\n", encoding="utf-8")
        self.commit(self.project)
        self.modify_source("AGENTS.md", "# 上游完全替换\n")
        self.git(self.source, "tag", "v-conflict")
        original = M.read_state(self.project)
        self.assertEqual(2, M.update(self.project, ref="v-conflict"))
        self.assertEqual(original, M.read_state(self.project))
        plan = self.plan_file()
        data = json.loads(plan.read_text(encoding="utf-8"))
        self.assertEqual("v-conflict", data["next_state"]["ref"])
        proposed = plan.parent / "proposed/AGENTS.md"
        proposed.write_text("# Reviewed release merge\n", encoding="utf-8")
        M.apply_plan(self.project, plan)
        self.assertEqual("v-conflict", M.read_state(self.project)["ref"])

    def test_same_commit_ref_switch_persists_metadata(self):
        self.git(self.source, "tag", "v-same")
        original = M.read_state(self.project)["revision"]
        self.assertEqual(0, M.update(self.project, ref="v-same"))
        state = M.read_state(self.project)
        self.assertEqual("v-same", state["ref"])
        self.assertEqual(original, state["revision"])

    def test_remote_urls_and_scp_sources_keep_their_meaning(self):
        for source in (M.DEFAULT_SOURCE, "ssh://git@example.invalid/repo.git", "git@example.invalid:repo.git"):
            with self.subTest(source=source):
                self.assertEqual(source, M.normalize_source(source))


if __name__ == "__main__":
    unittest.main()
