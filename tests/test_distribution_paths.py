"""两个独立入口必须使用相同的跨平台边界，不依赖待检查工具互相导入。"""
import importlib.util
from pathlib import Path
import unittest

PROJECT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, PROJECT / "tools" / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


MODULES = (load("template_manager"), load("check_template"))


class DistributionPathTests(unittest.TestCase):
    def test_aliases_and_reserved_paths_are_rejected_by_both_entry_points(self):
        names = (".git/config", ".GIT/config", "src/.Git/config", ".git./config",
                 ".AGENTS/template-state.json", ".agents/.TEMPLATE-UPDATE.LOCK",
                 ".agents/TEMPLATE-UPDATES/plan.json", "./AGENTS.md", "a//b.md",
                 "a/./b.md", "a/../b.md", "C:/outside", "/absolute", "a\\b.md",
                 "aux.txt", "COM1", "NUL.md", "docs./a.md", "docs /a.md", "a.md ",
                 "a\x00.md", "", ".")
        for module in MODULES:
            for name in names:
                with self.subTest(module=module.__name__, name=name), self.assertRaises(ValueError):
                    module.path_key(name)

    def test_case_collisions_and_protected_records_have_the_same_meaning(self):
        for module in MODULES:
            self.assertEqual(module.path_key("AGENTS.md"), module.path_key("agents.md"))
            for name in ("readme.md", "Agents_List.md", ".AGENTS/coordination.md",
                         ".AGENTS/tasks/REAL001.md", "RESULTS/run/report.md"):
                with self.subTest(module=module.__name__, name=name):
                    self.assertTrue(module.protected(name))
            for name in ("AGENTS.md", ".agents/tasks/TEMPLATE-lite.md", "docs/template-usage.md"):
                with self.subTest(module=module.__name__, name=name):
                    self.assertFalse(module.protected(name))


if __name__ == "__main__":
    unittest.main()
