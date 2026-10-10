"""从 Git 安装／更新协作模板；保护工程状态，冲突留报告，不推送工程或执行上游脚本。"""
import argparse
import ast
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import socket
import subprocess
import tempfile
from urllib.parse import urlsplit
import uuid

DEFAULT_SOURCE = "https://github.com/duskbreakmist/mulagent-project-template.git"
STATE = ".agents/template-state.json"
LOCK = ".agents/.template-update.lock"
REPORTS = ".agents/template-updates"
SEEDS = {"README.md", "agents_list.md", ".agents/coordination.md",
         ".agents/tasks/README.md", "docs/CURRENT.md"}
RUNTIME_DIRS = {".agents/tasks", ".agents/messages", ".agents/handoffs",
                ".agents/feedback", ".agents/plans", ".agents/runs",
                ".agents/scratch", "results", "docs/history"}


def normalized(data):
    return data.decode("utf-8").replace("\r\n", "\n")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def safe_path(root, name):
    # 即使来自清单／状态／计划，也重新验证；不能碰 Git 元数据、绝对路径或符号链接外部目标。
    if not isinstance(name, str) or "\\" in name or ":" in name:
        raise ValueError("非法模板路径")
    relative = PurePosixPath(name)
    if relative.is_absolute() or ".." in relative.parts or not relative.parts:
        raise ValueError("非法模板路径: " + name)
    if relative.parts[0] == ".git" or name in (STATE, LOCK) or name.startswith(REPORTS + "/"):
        raise ValueError("保留路径: " + name)
    path = root.joinpath(*relative.parts)
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError("路径逃逸: " + name)
    return path


def protected(name):
    if name in SEEDS:
        return True
    parent = PurePosixPath(name).parent.as_posix()
    for directory in RUNTIME_DIRS:
        if name.startswith(directory + "/"):
            leaf = PurePosixPath(name).name
            # 只管理这些目录中的根级说明／格式；实际 task、交接、反馈和结果始终属于工程。
            return parent != directory or not (leaf == "README.md" or leaf.startswith("TEMPLATE"))
    return False


def run_git(*args, cwd=None, check=True):
    result = subprocess.run(["git", *map(str, args)], cwd=cwd, capture_output=True)
    if check and result.returncode:
        raise ValueError("Git 操作失败: " + result.stderr.decode("utf-8", "replace").strip())
    return result


def atomic_write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name("." + path.name + "." + uuid.uuid4().hex + ".tmp")
    try:
        temporary.write_bytes(data)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def read_state(root):
    path = root / STATE
    if not path.resolve().is_relative_to(root):
        raise ValueError("状态文件路径逃逸")
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("version") != 1 or not isinstance(data.get("files"), dict):
        raise ValueError("不支持的安装状态")
    for name in data["files"]:
        safe_path(root, name)
    return data


@contextmanager
def write_lock(root):
    path = root / LOCK
    if not path.resolve().is_relative_to(root):
        raise ValueError("锁路径逃逸")
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        stream = path.open("x", encoding="utf-8")
    except FileExistsError as error:
        raise ValueError("更新锁已存在；先确认持有者停写，不按超时自动删锁") from error
    try:
        with stream:
            json.dump({"pid": os.getpid(), "host": socket.gethostname()}, stream)
        yield
    finally:
        path.unlink(missing_ok=True)


class Upstream:
    def __init__(self, directory, source, ref):
        parts = urlsplit(source)
        if parts.username or parts.password:
            raise ValueError("源地址不能内嵌凭据")
        if not ref or ref.startswith("-") or "\n" in ref:
            raise ValueError("非法版本引用")
        self.repo = Path(directory) / "upstream"
        self._trees, self._blobs = {}, {}
        # 不 checkout 或执行远端脚本；读取 Git 对象中的 UTF-8 文件。
        run_git("clone", "--quiet", "--no-checkout", "--", source, self.repo)
        resolved = run_git("rev-parse", "--verify", ref + "^{commit}", cwd=self.repo, check=False)
        if resolved.returncode:
            resolved = run_git("rev-parse", "--verify", "origin/" + ref + "^{commit}", cwd=self.repo)
        self.revision = resolved.stdout.decode().strip()
        self.source, self.ref = source, ref
        manifest = json.loads(self.blob(self.revision, ".agents/template_manifest.json"))
        if manifest.get("format") != "project_templateA" or manifest.get("version") not in (1, 2):
            raise ValueError("不支持的上游清单")
        required = manifest.get("required")
        if (not isinstance(required, list) or not required or
                not all(isinstance(name, str) for name in required) or len(set(required)) != len(required)):
            raise ValueError("清单为空或重复")
        self.files = {}
        for name in required:
            safe_path(self.repo, name)
            if protected(name) and name not in SEEDS:
                raise ValueError("上游包含工程运行记录: " + name)
            self.files[name] = self.blob(self.revision, name)
        if ".agents/template_manifest.json" not in self.files or "tools/template_manager.py" not in self.files:
            raise ValueError("上游不包含安装器或清单")

    def blob(self, revision, name):
        safe_path(self.repo, name)
        if not re.fullmatch(r"[0-9a-f]{40,64}", revision):
            raise ValueError("非法提交 ID")
        key = (revision, name)
        if key in self._blobs:
            return self._blobs[key]
        if revision not in self._trees:
            # 一次读取提交树，避免每个小模板文件都重复启动 ls-tree。
            tree = {}
            for entry in run_git("ls-tree", "-r", "-z", revision, cwd=self.repo).stdout.split(b"\0"):
                if entry:
                    metadata, path = entry.split(b"\t", 1)
                    tree[path.decode("utf-8")] = metadata.split()[0]
            self._trees[revision] = tree
        if self._trees[revision].get(name) not in (b"100644", b"100755"):
            raise ValueError("模板只接受普通文件: " + name)
        data = run_git("show", revision + ":" + name, cwd=self.repo).stdout
        text = normalized(data)
        if not text.strip() or text.startswith("\ufeff") or "\ufffd" in text:
            raise ValueError("模板空文件／编码异常: " + name)
        self._blobs[key] = text
        return text


def baseline(upstream, content):
    return {"revision": upstream.revision, "sha256": digest(content.encode("utf-8"))}


def git_root(root):
    result = run_git("rev-parse", "--show-toplevel", cwd=root, check=False)
    return Path(result.stdout.decode().strip()).resolve() if result.returncode == 0 else None


def require_clean(root):
    existing = git_root(root)
    if existing and existing != root:
        raise ValueError("目录位于父仓库中；请在实际工程根操作")
    if existing:
        entries = run_git("status", "--porcelain", "-z", "--untracked-files=all", cwd=root).stdout.split(b"\0")
        index = 0
        while index < len(entries):
            entry = entries[index]
            index += 1
            if not entry:
                continue
            status, name = entry[:2], entry[3:].decode("utf-8")
            if b"R" in status or b"C" in status:
                index += 1  # 重命名的第二个路径也属于同一条改动。
            if name == LOCK or name.startswith(REPORTS + "/"):
                continue  # 旧模板未忽略这些辅助路径时，也不能被本工具自己的锁／报告挡住。
            raise ValueError("工程有未提交改动；先保存 Git 版本，或仅用 update --check 预览")


def initialize(root, source, ref, no_git=False, commit=False):
    root = Path(root).resolve()
    if commit and no_git:
        raise ValueError("--commit 与 --no-git 不兼容")
    # 先下载并验证；网络失败不留下一个让下次 init 被拒绝的半空工程。
    with tempfile.TemporaryDirectory() as temp:
        upstream = Upstream(temp, source, ref)
        root.mkdir(parents=True, exist_ok=True)
        if any(path.name != ".git" for path in root.iterdir()):
            raise ValueError("init 只接受空目录；已有工程使用 adopt")
        existing = git_root(root)
        if existing and existing != root:
            raise ValueError("不能在父仓库内创建嵌套工程")
        if existing and run_git("rev-parse", "--verify", "HEAD", cwd=root, check=False).returncode == 0:
            raise ValueError("该仓库已有历史，不按空新工程初始化")
        with write_lock(root):
            state = {"version": 1, "source": source, "ref": ref, "revision": upstream.revision,
                     "files": {name: baseline(upstream, text) for name, text in upstream.files.items()}}
            for name, text in upstream.files.items():
                atomic_write(safe_path(root, name), text.encode("utf-8"))
            atomic_write(root / STATE, (json.dumps(state, ensure_ascii=False, indent=2) + "\n").encode())
            if not no_git:
                if not existing:
                    run_git("init", "-b", "main", cwd=root)
                run_git("config", "--local", "agent.coordinationRoot", root, cwd=root)
                if commit:
                    run_git("add", "--", *upstream.files, STATE, cwd=root)
                    run_git("commit", "-m", "[BOOTSTRAP][template] initialize project template", cwd=root)
            print("INITIALIZED", root, upstream.revision)
            return state


def adopt(root, source, ref):
    root = Path(root).resolve()
    if not root.is_dir() or not (root / "AGENTS.md").is_file():
        raise ValueError("adopt 需要已有模板工程；空工程使用 init")
    if (root / STATE).exists():
        raise ValueError("已有安装状态；不覆盖基线")
    with write_lock(root), tempfile.TemporaryDirectory() as temp:
        upstream = Upstream(temp, source, ref)
        records = {}
        for name, text in upstream.files.items():
            path = safe_path(root, name)
            # 无法确认旧版本时不猜基线：只有完全相同的文件可自动识别。
            same = path.is_file() and normalized(path.read_bytes()) == text
            records[name] = baseline(upstream, text) if same else {"revision": None, "sha256": None}
        state = {"version": 1, "source": source, "ref": ref, "revision": upstream.revision, "files": records}
        atomic_write(root / STATE, (json.dumps(state, ensure_ascii=False, indent=2) + "\n").encode())
        print("ADOPTED", root, "existing files unchanged")
        return state


def three_way(current, base, incoming, directory):
    directory.mkdir(parents=True, exist_ok=True)
    paths = [directory / name for name in ("current", "base", "upstream")]
    for path, text in zip(paths, (current, base, incoming)):
        path.write_text(text, encoding="utf-8", newline="\n")
    result = run_git("merge-file", "--stdout", "--diff3", "-L", "LOCAL", "-L", "BASE",
                     "-L", "UPSTREAM", *paths, check=False)
    if result.returncode < 0 or result.returncode > 127:
        raise ValueError("三方合并工具失败")
    return normalized(result.stdout), result.returncode != 0


def make_plan(root, upstream, state, temp):
    changed, conflicts, skipped = [], [], []
    new_state = json.loads(json.dumps(state))
    new_state.update(revision=upstream.revision)
    for name, incoming in upstream.files.items():
        path = safe_path(root, name)
        if path.exists() and not path.is_file():
            raise ValueError("目标不是普通文件: " + name)
        if path.exists() and protected(name):
            skipped.append(name)
            continue
        record = state["files"].get(name, {})
        original = path.read_bytes() if path.exists() else None
        current = normalized(original) if original is not None else None
        if current == incoming:
            new_state["files"][name] = baseline(upstream, incoming)
            continue
        base = None
        if record.get("revision"):
            try:
                base = upstream.blob(record["revision"], name)
                if digest(base.encode()) != record.get("sha256"):
                    raise ValueError("基线哈希不一致")
            except ValueError:
                base = None
        if current is None:
            # 曾存在但本地删掉的文件属于定制删除，不自动恢复。
            if record.get("revision"):
                skipped.append(name)
                continue
            proposed, conflict = incoming, False
        elif base is None:
            proposed, conflict = incoming, True
        elif incoming == base:
            new_state["files"][name] = baseline(upstream, incoming)
            continue  # 上游没变，本地定制保留。
        elif current == base:
            proposed, conflict = incoming, False
        else:
            proposed, conflict = three_way(current, base, incoming, Path(temp) / str(len(changed)))
        entry = {"path": name, "original_sha256": digest(original) if original is not None else None,
                 "proposal": proposed, "current": current, "base": base, "upstream": incoming,
                 "conflict": conflict}
        changed.append(entry)
        if conflict:
            conflicts.append(name)
        new_state["files"][name] = baseline(upstream, incoming)
    # 上游删文件时也不自动删本地内容；旧基线保留以便审计。
    removed = sorted(set(state["files"]) - set(upstream.files))
    return {"version": 1, "root": str(root), "revision": upstream.revision,
            "state_sha256": digest((root / STATE).read_bytes()), "entries": changed,
            "conflicts": conflicts, "skipped": skipped, "removed_upstream": removed,
            "next_state": new_state}


def save_plan(root, plan):
    directory = root / REPORTS / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") +
                                  "-" + plan["revision"][:8] + "-" + uuid.uuid4().hex[:6])
    if not directory.resolve().is_relative_to(root):
        raise ValueError("报告路径逃逸")
    directory.mkdir(parents=True)
    stored = json.loads(json.dumps(plan))
    for entry in stored["entries"]:
        for field, folder in (("proposal", "proposed"), ("current", "current"),
                              ("base", "base"), ("upstream", "upstream")):
            text = entry.pop(field)
            if text is not None:
                path = safe_path(directory / folder, entry["path"])
                atomic_write(path, text.encode("utf-8"))
    atomic_write(directory / "plan.json", (json.dumps(stored, ensure_ascii=False, indent=2) + "\n").encode())
    return directory / "plan.json"


def validate_proposal(name, data):
    text = normalized(data)
    if re.search(r"(?m)^(<{7}|>{7}|\|{7})(?:\s|$)", text):
        raise ValueError("仍有冲突标记: " + name)
    if name.endswith(".json"):
        value = json.loads(text)
        if name == ".agents/template_manifest.json":
            if value.get("format") != "project_templateA" or value.get("version") not in (1, 2):
                raise ValueError("清单候选非法")
    if name.endswith(".py"):
        ast.parse(text, filename=name)  # 只解析语法，不执行下载或手工编辑的代码。


def apply_plan(root, plan_path):
    root = Path(root).resolve()
    plan_path = Path(plan_path).resolve()
    if not plan_path.is_relative_to(root / REPORTS):
        raise ValueError("计划必须位于本工程的更新报告中")
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    if plan.get("version") != 1 or Path(plan.get("root", "")).resolve() != root:
        raise ValueError("计划不属于本工程")
    state_file = root / STATE
    if not state_file.resolve().is_relative_to(root):
        raise ValueError("状态文件路径逃逸")
    if digest(state_file.read_bytes()) != plan["state_sha256"]:
        raise ValueError("安装状态已改变，请重新生成计划")
    changes, originals = {}, {}
    seen = set()
    for entry in plan["entries"]:
        name = entry["path"]
        if name in seen:
            raise ValueError("重复计划文件: " + name)
        seen.add(name)
        path = safe_path(root, name)
        if protected(name) and path.exists():
            raise ValueError("计划试图覆盖工程状态: " + name)
        original = path.read_bytes() if path.exists() else None
        if (digest(original) if original is not None else None) != entry["original_sha256"]:
            raise ValueError("生成计划后本地文件已变: " + name)
        proposed = safe_path(plan_path.parent / "proposed", name).read_bytes()
        validate_proposal(name, proposed)
        changes[name], originals[name] = proposed, original
    state_path = root / STATE
    before_state = state_path.read_bytes()
    next_state = plan["next_state"]
    for name in next_state["files"]:
        safe_path(root, name)
    state_bytes = (json.dumps(next_state, ensure_ascii=False, indent=2) + "\n").encode()
    written = []
    try:
        for name, content in changes.items():
            path = safe_path(root, name)
            # 文件集合全部验证后再写；写前再检查，拒绝明显的并发修改。
            current = path.read_bytes() if path.exists() else None
            if current != originals[name]:
                raise ValueError("写入前文件发生变化: " + name)
            atomic_write(path, content)
            written.append(name)
        if state_path.read_bytes() != before_state:
            raise ValueError("写入前安装状态变化")
        atomic_write(state_path, state_bytes)
    except Exception:
        if state_path.read_bytes() == state_bytes:
            atomic_write(state_path, before_state)
        for name in reversed(written):
            path = safe_path(root, name)
            # 恢复只覆盖仍等于本工具刚写入的内容，不抢掉其他执行者的新修改。
            if path.read_bytes() == changes[name]:
                if originals[name] is None:
                    path.unlink()
                else:
                    atomic_write(path, originals[name])
        raise
    print("APPLIED", len(changes), "files", plan["revision"], "backup", plan_path.parent)
    return plan


def update(root, check=False):
    root = Path(root).resolve()
    state = read_state(root)
    if not check:
        require_clean(root)
    with tempfile.TemporaryDirectory() as temp:
        upstream = Upstream(temp, state["source"], state["ref"])
        plan = make_plan(root, upstream, state, temp)
        print("UPDATE_PLAN", "changes=" + str(len(plan["entries"])),
              "conflicts=" + str(len(plan["conflicts"])), "protected=" + str(len(plan["skipped"])),
              "removed_upstream=" + str(len(plan["removed_upstream"])))
        for entry in plan["entries"]:
            print("CONFLICT" if entry["conflict"] else "CHANGE", entry["path"])
        if check:
            return 2 if plan["conflicts"] else 0
        if not plan["entries"] and plan["next_state"] == state:
            print("ALREADY_CURRENT")
            return 0
        report = save_plan(root, plan)
        if plan["conflicts"]:
            print("NO_FILES_APPLIED", report, "edit proposed files, then use apply --plan")
            return 2
        apply_plan(root, report)
        print("Review git diff, run project checks, then commit the update.")
        return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("init", "adopt", "update", "apply"):
        command = sub.add_parser(name)
        command.add_argument("--root", default=".")
        if name in ("init", "adopt"):
            command.add_argument("--source", default=DEFAULT_SOURCE)
            command.add_argument("--ref", default="main")
        if name == "init":
            command.add_argument("--no-git", action="store_true")
            command.add_argument("--commit", action="store_true")
        if name == "update":
            command.add_argument("--check", action="store_true")
        if name == "apply":
            command.add_argument("--plan", required=True)
    args = parser.parse_args()
    try:
        if args.command == "init":
            initialize(args.root, args.source, args.ref, args.no_git, args.commit)
        elif args.command == "adopt":
            adopt(args.root, args.source, args.ref)
        elif args.command == "update":
            if args.check:
                return update(args.root, True)
            with write_lock(Path(args.root).resolve()):
                return update(args.root)
        else:
            root = Path(args.root).resolve()
            with write_lock(root):
                require_clean(root)
                apply_plan(root, args.plan)
        return 0
    except (ValueError, OSError, SyntaxError, json.JSONDecodeError) as error:
        print("ERROR:", error)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
