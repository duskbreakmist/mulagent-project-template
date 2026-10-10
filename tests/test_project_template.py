"""验证多文件模板独立复制、只读检查及错误检测，不依赖原工程运行时。"""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

PROJECT = Path(__file__).resolve().parents[1]
SOURCE = PROJECT if (PROJECT / ".agents/template_manifest.json").exists() else PROJECT / "gpt/project_templateA"


class ProjectTemplateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "new-project"
        shutil.copytree(SOURCE, self.root,
                        ignore=shutil.ignore_patterns(".git", ".test-tmp", "__pycache__", "*.pyc"))

    def tearDown(self):
        self.temp.cleanup()

    def run_check(self):
        # 从新目录运行已复制的脚本，检查它没有引用原工程。
        return subprocess.run(
            [sys.executable, "tools/check_template.py", "--root", "."],
            cwd=self.root, capture_output=True)

    def digest(self):
        return {str(path.relative_to(self.root)): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in self.root.rglob("*") if path.is_file()}

    def rewrite_manifest(self, transform):
        path = self.root / ".agents/template_manifest.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        transform(data)
        path.write_text(json.dumps(data), encoding="utf-8")

    def test_copied_package_runs_independently_and_check_is_read_only(self):
        before = self.digest()
        for _ in range(2):
            result = self.run_check()
            self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(before, self.digest())
        self.assertFalse((self.root / ".git").exists())
        self.assertFalse((self.root / ".agents/.bootstrap-v1").exists())

    def test_missing_required_protocol_or_mode_files_reported_without_repair(self):
        for name in (".agents/PROTOCOL.md", ".agents/guides/modes.md",
                     ".agents/coordination.md", ".agents/guides/coordination.md",
                     ".agents/guides/tools.md", ".agents/feedback/README.md",
                     ".agents/feedback/TEMPLATE.md", ".agents/tasks/TEMPLATE-lite.md",
                     ".agents/guides/records.md", "docs/history/README.md",
                     "results/README.md", "README.md", "docs/template-usage.md",
                     "tools/template_manager.py"):
            with self.subTest(name=name):
                path = self.root / name
                path.unlink()
                before = self.digest()
                self.assertEqual(1, self.run_check().returncode)
                self.assertEqual(before, self.digest())
                self.assertFalse(path.exists())
                # 下一种漏复制情形独立验证；只恢复本测试临时副本。
                shutil.copyfile(SOURCE / name, path)

    def test_custom_project_state_is_preserved(self):
        path = self.root / "agents_list.md"
        path.write_text("# 用户自己的登记表\n\ncustom state\n", encoding="utf-8")
        # 用户反馈不属于固定清单；检查器仍须保持它原样，不清空或自动采纳。
        feedback = self.root / ".agents/feedback/example-agent/feedback.md"
        feedback.parent.mkdir()
        feedback.write_text("# 用户反馈\n\n觉得步骤繁琐，尚未采纳。\n", encoding="utf-8")
        before = self.digest()
        self.assertEqual(0, self.run_check().returncode)
        self.assertEqual(before, self.digest())

    def test_invalid_encoding_is_reported_without_rewriting(self):
        path = self.root / "agents_list.md"
        path.write_bytes(b"\xff\xfe")
        before = self.digest()
        self.assertEqual(1, self.run_check().returncode)
        self.assertEqual(before, self.digest())

    def test_empty_template_file_is_rejected(self):
        (self.root / ".agents/tasks/TEMPLATE.md").write_bytes(b"")
        self.assertEqual(1, self.run_check().returncode)

    def test_path_escape_in_manifest_is_rejected(self):
        self.rewrite_manifest(lambda data: data["required"].append("../outside.md"))
        self.assertEqual(1, self.run_check().returncode)

    def test_absolute_path_in_manifest_is_rejected(self):
        self.rewrite_manifest(lambda data: data["required"].append(str(self.root / "AGENTS.md")))
        self.assertEqual(1, self.run_check().returncode)

    def test_duplicate_manifest_entry_is_rejected(self):
        self.rewrite_manifest(lambda data: data["required"].append("AGENTS.md"))
        self.assertEqual(1, self.run_check().returncode)

    def test_unknown_version_is_rejected(self):
        self.rewrite_manifest(lambda data: data.update(version=99))
        self.assertEqual(1, self.run_check().returncode)

    def test_entry_is_short_and_has_no_embedded_program_or_runtime_registration(self):
        text = (self.root / "AGENTS.md").read_text(encoding="utf-8")
        self.assertLessEqual(len(text.splitlines()), 15)
        self.assertNotIn("```python", text)
        self.assertNotIn("COLLAB001", (self.root / "agents_list.md").read_text(encoding="utf-8"))
        self.assertEqual(["README.md", "TEMPLATE-lite.md", "TEMPLATE.md"],
                         sorted(path.name for path in (self.root / ".agents/tasks").iterdir()))

    def test_broken_inline_link_is_rejected_without_repair(self):
        path = self.root / "AGENTS.md"
        path.write_text(path.read_text(encoding="utf-8") + "\n[缺失](missing.md)\n", encoding="utf-8")
        before = self.digest()
        self.assertEqual(1, self.run_check().returncode)
        self.assertEqual(before, self.digest())

    def test_reference_links_are_checked(self):
        path = self.root / "AGENTS.md"
        original = path.read_text(encoding="utf-8")
        path.write_text(original + "\n[说明][guide]\n[guide]: .agents/PROTOCOL.md\n", encoding="utf-8")
        self.assertEqual(0, self.run_check().returncode)
        path.write_text(original + "\n[说明][guide]\n[guide]: missing.md\n", encoding="utf-8")
        self.assertEqual(1, self.run_check().returncode)

    def test_code_examples_external_urls_and_anchors_are_ignored(self):
        path = self.root / "AGENTS.md"
        examples = "\n".join([
            "\n````markdown", "[示例](missing.md)", "````",
            "~~~markdown", "[示例](missing.md)", "~~~",
            "`[内联代码](missing.md)`", "[网址](https://example.invalid/missing)",
            "[锚点](#missing)", "[邮件](mailto:example@example.invalid)",
        ])
        path.write_text(path.read_text(encoding="utf-8") + examples, encoding="utf-8")
        self.assertEqual(0, self.run_check().returncode)

    def test_link_with_spaces_parentheses_encoding_and_title(self):
        target = self.root / ".agents/feedback/a file (中文).md"
        target.write_text("# 用户的文档\n", encoding="utf-8")
        path = self.root / "AGENTS.md"
        extra = ('\n[本地](<.agents/feedback/a file (中文).md> "标题")\n'
                 '[编码](.agents/feedback/a%20file%20(中文).md#section)\n')
        path.write_text(path.read_text(encoding="utf-8") + extra, encoding="utf-8")
        self.assertEqual(0, self.run_check().returncode)

    def test_local_link_cannot_escape_root_even_when_target_exists(self):
        (Path(self.temp.name) / "outside.md").write_text("# 外部文档\n", encoding="utf-8")
        path = self.root / "AGENTS.md"
        path.write_text(path.read_text(encoding="utf-8") + "\n[外部](../outside.md)\n", encoding="utf-8")
        self.assertEqual(1, self.run_check().returncode)

    def test_invalid_task_status_and_duplicate_status_are_rejected(self):
        path = self.root / ".agents/tasks/DEV001.md"
        for metadata in ("- status: finished", "- status: done\n- status: todo"):
            with self.subTest(metadata=metadata):
                path.write_text("# DEV001\n\n" + metadata + "\n", encoding="utf-8")
                before = self.digest()
                self.assertEqual(1, self.run_check().returncode)
                self.assertEqual(before, self.digest())

    def test_valid_task_states_do_not_treat_body_examples_as_metadata(self):
        path = self.root / ".agents/tasks/DEV001.md"
        for status in ("todo", "in_progress", "blocked", "review", "done"):
            with self.subTest(status=status):
                path.write_text("# DEV001\n\n- status: " + status +
                                "\n\n## Verification\n```yaml\nstatus: example\n```\n",
                                encoding="utf-8")
                self.assertEqual(0, self.run_check().returncode)

    def test_version_one_remains_a_basic_integrity_check(self):
        self.rewrite_manifest(lambda data: data.update(version=1))
        path = self.root / "AGENTS.md"
        path.write_text(path.read_text(encoding="utf-8") + "\n[缺失](missing.md)\n", encoding="utf-8")
        (self.root / ".agents/tasks/DEV001.md").write_text("# DEV001\n- status: custom\n", encoding="utf-8")
        before = self.digest()
        self.assertEqual(0, self.run_check().returncode)
        self.assertEqual(before, self.digest())


if __name__ == "__main__":
    unittest.main()
