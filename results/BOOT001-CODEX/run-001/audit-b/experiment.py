"""隔离验证分发副本二次安装和维护侧检查边界，不修改生产仓库。"""
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile

PROJECT = Path(__file__).resolve().parents[4]


def run(*args, cwd=None):
    environment = dict(os.environ, PYTHONIOENCODING="utf-8")
    value = subprocess.run(args, cwd=cwd, text=True, encoding="utf-8", errors="replace",
                           capture_output=True, env=environment)
    if value.returncode:
        raise RuntimeError(value.stdout + value.stderr)
    return value.stdout.strip()


def main():
    baseline = run("git", "rev-parse", "HEAD", cwd=PROJECT)
    manifest = json.loads((PROJECT / ".agents/template_manifest.json").read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory(prefix="boot001-audit-b-") as temp:
        first, second = Path(temp) / "first", Path(temp) / "second"
        print(run(sys.executable, str(PROJECT / "tools/template_manager.py"), "init", "--root", str(first),
                  "--source", str(PROJECT), "--ref", baseline, "--no-git"))
        # 普通分发副本的发布前置条件是自己的已提交 Git 快照；只设置临时仓库身份。
        run("git", "init", "-b", "main", cwd=first)
        run("git", "config", "user.name", "Bootstrap Audit Fixture", cwd=first)
        run("git", "config", "user.email", "fixture@example.invalid", cwd=first)
        run("git", "add", "--", *manifest["required"], ".agents/template-state.json", cwd=first)
        run("git", "commit", "-m", "isolated distributed source", cwd=first)
        print(run(sys.executable, str(first / "tools/template_manager.py"), "init", "--root", str(second),
                  "--source", str(first), "--ref", "main", "--no-git"))
        print(run(sys.executable, str(second / "tools/check_template.py"), "--root", str(second)))
        equal = all(hashlib.sha256((first / name).read_bytes()).digest() ==
                    hashlib.sha256((second / name).read_bytes()).digest() for name in manifest["required"])
        # 刻意插入维护 task 错误，核对检查器是否覆盖母模板专用路径。
        invalid = second / "docs/maintenance/tasks/INVALID-AUDIT.md"
        invalid.parent.mkdir(parents=True)
        invalid.write_text("# isolated audit\n\n- status: definitely_invalid\n", encoding="utf-8")
        ignored_status = run(sys.executable, str(second / "tools/check_template.py"), "--root", str(second))
        result = {
            "base_commit": baseline,
            "python": platform.python_version(),
            "git": run("git", "--version"),
            "required_count": len(manifest["required"]),
            "all_required_files_equal_across_generations": equal,
            "second_has_tests": (second / "tests").exists(),
            "second_has_workbench": (second / "tools/agent_workbench.py").exists(),
            "first_has_maintenance_guide": (first / "docs/maintenance/README.md").exists(),
            "invalid_maintenance_status_check_output": ignored_status,
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        assert equal
        assert ignored_status == "TEMPLATE_OK files=33"


if __name__ == "__main__":
    main()
