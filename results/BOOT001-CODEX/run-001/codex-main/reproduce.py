"""离线验证母仓库→分发工程→第二代工程；所有写入限于本次临时目录。"""
import json
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[4]
BASE = "8d2645f80f43df4932515f5b6650a05e53410f5b"


def run(args, cwd=ROOT):
    result = subprocess.run(args, cwd=cwd, capture_output=True, text=True, encoding="utf-8")
    if result.returncode:
        raise RuntimeError(result.stderr or result.stdout)
    return result.stdout.strip()


def main():
    parent = ROOT / ".test-tmp"
    parent.mkdir(exist_ok=True)
    # 仅在临时副本沿用真实已有身份，不修改母仓库配置或伪造维护者身份。
    identity = {key: run(["git", "config", "--get", key])
                for key in ("user.name", "user.email")}
    with tempfile.TemporaryDirectory(prefix="BOOT001-", dir=parent) as folder:
        workspace = Path(folder).resolve()
        if not workspace.is_relative_to(parent.resolve()):
            raise RuntimeError("临时目录超出实验边界")
        generations = []
        source, manager, ref = ROOT, ROOT / "tools/template_manager.py", BASE
        for index in (1, 2):
            target = workspace / ("generation-" + str(index))
            target.mkdir()
            run(["git", "init", "-b", "main"], target)
            for key, value in identity.items():
                run(["git", "config", "--local", key, value], target)
            installed = run([sys.executable, str(manager), "init", "--root", str(target),
                             "--source", str(source), "--ref", ref, "--commit"])
            check = run([sys.executable, str(target / "tools/check_template.py"),
                         "--root", str(target)])
            preview = run([sys.executable, str(target / "tools/template_manager.py"),
                           "update", "--root", str(target), "--check"])
            manifest = json.loads((target / ".agents/template_manifest.json").read_text(encoding="utf-8"))
            state = json.loads((target / ".agents/template-state.json").read_text(encoding="utf-8"))
            generations.append({
                "generation": index,
                "installed": installed,
                "managed_files": len(manifest["required"]),
                "check": check,
                "preview": preview,
                "source_revision": state["revision"],
                "clean": run(["git", "status", "--porcelain"], target) == "",
                "no_remote": run(["git", "remote"], target) == "",
                "coordination_root_matches": run(["git", "config", "--get", "agent.coordinationRoot"], target)
                == str(target),
                "development_files_present": {name: (target / name).exists() for name in
                                              ("tests", ".github/workflows/checks.yml", "docs/maintenance",
                                               "tools/agent_workbench.py", "tools/agent_relay.py")},
            })
            # 下一代实际使用第一代已安装的管理器和第一代 Git 快照作为来源。
            source, manager, ref = target, target / "tools/template_manager.py", "main"
        print(json.dumps({"baseline": BASE, "generations": generations}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
