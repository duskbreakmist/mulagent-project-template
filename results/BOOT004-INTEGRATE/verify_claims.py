"""整合阶段只在隔离副本复核清单、安装基线与本地来源路径边界。"""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]
BASE = "8d2645f80f43df4932515f5b6650a05e53410f5b"


def run(args, cwd=ROOT, required=True):
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    value = subprocess.run(args, cwd=cwd, env=env, text=True, encoding="utf-8",
                           errors="replace", capture_output=True)
    if required and value.returncode:
        raise RuntimeError(value.stdout + value.stderr)
    return {"exit": value.returncode, "stdout": value.stdout.strip(), "stderr": value.stderr.strip()}


def install(path, source):
    path.mkdir()
    # 临时目录位于母仓库内，先建空独立 Git 以满足安装器的父仓库隔离约束。
    run(["git", "init", "-b", "main"], path)
    run([sys.executable, str(ROOT / "tools/template_manager.py"), "init", "--root", str(path),
         "--source", source, "--ref", BASE])


def main():
    parent = ROOT / ".test-tmp"
    parent.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="BOOT004-", dir=parent) as folder:
        workspace = Path(folder).resolve()
        assert workspace.is_relative_to(parent.resolve())
        project = workspace / "absolute-source"
        install(project, str(ROOT))
        checker = [sys.executable, str(project / "tools/check_template.py"), "--root", str(project)]
        outcomes = {"baseline": BASE, "normal_check": run(checker)}
        manifest_path = project / ".agents/template_manifest.json"
        original = manifest_path.read_bytes()
        manifest = json.loads(original)
        manifest["required"] = [name for name in manifest["required"] if name not in
                                ("tools/check_template.py", ".agents/guides/git.md")]
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        outcomes["reduced_manifest_check"] = run(checker)
        outcomes["checker_file_still_exists"] = (project / "tools/check_template.py").is_file()
        manifest_path.write_bytes(original)
        state_path = project / ".agents/template-state.json"
        state_bytes = state_path.read_bytes()
        state_path.unlink()
        outcomes["missing_install_state_check"] = run(checker)
        state_path.write_bytes(state_bytes)
        manager = project / "tools/template_manager.py"
        manager_bytes = manager.read_bytes()
        manager.write_text("def deliberately_invalid(:\n", encoding="utf-8")
        outcomes["invalid_python_check"] = run(checker)
        manager.write_bytes(manager_bytes)
        moved = workspace / "moved-project"
        # 两个绝对目标均已确认位于本次临时目录，仅移动本人实验副本。
        assert project.resolve().is_relative_to(workspace) and moved.resolve().is_relative_to(workspace)
        project.rename(moved)
        coordination = run(["git", "config", "--get", "agent.coordinationRoot"], moved)["stdout"]
        outcomes["moved_coordination_root_is_stale"] = Path(coordination).resolve() != moved
        outcomes["moved_project_check"] = run([sys.executable, str(moved / "tools/check_template.py"),
                                               "--root", str(moved)])
        relative = workspace / "relative-source"
        install(relative, ".")
        state = json.loads((relative / ".agents/template-state.json").read_text(encoding="utf-8"))
        outcomes["relative_source_recorded"] = state["source"]
        update = [sys.executable, str(relative / "tools/template_manager.py"), "update", "--root",
                  str(relative), "--check"]
        # 相同目标与状态，只有调用 cwd 不同；确认相对来源是否依赖调用位置。
        outcomes["relative_source_update_from_parent"] = run(update)
        outcomes["relative_source_update_from_project"] = run(update, relative, required=False)
        assert outcomes["reduced_manifest_check"]["stdout"] == "TEMPLATE_OK files=31"
        assert outcomes["checker_file_still_exists"]
        assert outcomes["missing_install_state_check"]["exit"] == 0
        assert outcomes["invalid_python_check"]["exit"] == 0
        assert outcomes["moved_coordination_root_is_stale"]
        assert outcomes["relative_source_recorded"] == "."
        assert outcomes["relative_source_update_from_project"]["exit"] != 0
        # 直接保存 UTF-8，避免 PowerShell 原生命令重定向改变中文错误消息编码。
        evidence = Path(__file__).with_name("verification.json")
        evidence.write_text(json.dumps(outcomes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("CLAIMS_REPRO_OK verification.json")


if __name__ == "__main__":
    main()
