"""隔离验证：已安装的分发副本能否再次成为安装来源，以及登记种子的边界。"""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile

PROJECT = Path(__file__).resolve().parents[4]
BASE = "8d2645f80f43df4932515f5b6650a05e53410f5b"
SPEC = importlib.util.spec_from_file_location("audit_template_manager", PROJECT / "tools/template_manager.py")
MANAGER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MANAGER)


def git(path, *args):
    return subprocess.run(["git", *args], cwd=path, capture_output=True, text=True, check=True).stdout.strip()


def fixture_commit(path):
    # 仅为临时仓库创建明确标注的测试身份，不改母仓库和全局 Git 配置。
    git(path, "add", ".")
    git(path, "-c", "user.name=Bootstrap Test Fixture", "-c", "user.email=fixture@example.invalid",
        "commit", "-m", "temporary audit fixture")


def main():
    temporary_parent = PROJECT / ".test-tmp" / "audit-a"
    temporary_parent.mkdir(parents=True, exist_ok=True)
    # 安装器内部也使用 tempfile；统一放进本人实验目录，避免修改系统临时配置。
    tempfile.tempdir = str(temporary_parent)
    with tempfile.TemporaryDirectory(prefix="replication-", dir=temporary_parent) as folder:
        folder = Path(folder)
        assert folder.resolve().is_relative_to(temporary_parent.resolve())
        first, second = folder / "first", folder / "second"
        # 临时目录位于母仓库内；先创建空独立仓库，满足安装器对父仓库隔离的要求。
        first.mkdir()
        git(first, "init", "-b", "main")
        MANAGER.initialize(first, str(PROJECT), BASE, no_git=True)
        fixture_commit(first)
        manifest = json.loads((first / ".agents/template_manifest.json").read_text(encoding="utf-8"))
        print("FIRST_REQUIRED_FILES", len(manifest["required"]))
        print("FIRST_HAS_TESTS", (first / "tests").exists())
        print("FIRST_HAS_WORKBENCH", (first / "tools/agent_workbench.py").exists())
        print("FIRST_HAS_MAINTENANCE", (first / "docs/maintenance").exists())
        print("FIRST_HAS_TOOL", (first / "tools/template_manager.py").exists())
        marker = "# bootstrap reproduction test marker\n"
        (first / "agents_list.md").write_text(marker, encoding="utf-8")
        fixture_commit(first)
        second.mkdir()
        git(second, "init", "-b", "main")
        # 第二代直接运行第一代安装出来的管理器，验证分发副本本身具备再安装能力。
        install = subprocess.run([sys.executable, str(first / "tools/template_manager.py"), "init",
                                  "--root", str(second), "--source", str(first), "--ref", "main", "--no-git"],
                                 capture_output=True, text=True, check=True)
        print(install.stdout.strip())
        print("SECOND_FROM_DISTRIBUTED_COPY", (second / "tools/template_manager.py").exists())
        print("SECOND_INHERITS_FIRST_REGISTRY", (second / "agents_list.md").read_text(encoding="utf-8") == marker)
        print("SECOND_STATE_SOURCE_IS_FIRST", MANAGER.read_state(second)["source"] == str(first))
        check = subprocess.run([sys.executable, str(second / "tools/check_template.py"), "--root", str(second)],
                               capture_output=True, text=True)
        print("SECOND_CHECK_RETURN", check.returncode)
        print("SECOND_CHECK_OUTPUT", check.stdout.strip(), check.stderr.strip())
        assert check.returncode == 0
    print("PYTHON_VERSION", sys.version.split()[0])
    print("GIT_VERSION", subprocess.run(["git", "--version"], capture_output=True, text=True).stdout.strip())


if __name__ == "__main__":
    main()
