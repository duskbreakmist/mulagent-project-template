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
SIDECAR = ".agents/sidecar.json"
SIDECAR_README = """# 业务工程协作记录

本仓库保存模板规则、任务、交接和验证证据；源码、业务 README 和业务测试保存在绑定的业务仓库。

启动前执行 `python tools/template_manager.py entry --root .`，将输出的提示词交给 AI，并确认它能读写两个目录。
本机业务路径由 `git config --local --get agent.projectRoot` 查询，不提交机器绝对路径。

[Agent规则](AGENTS.md) · [当前工作](docs/CURRENT.md) · [旁路安装与恢复](docs/sidecar.md)
"""
# README仅为旧清单保留保护规则；新工程的业务README独立生成，不进入模板基线。
SEEDS = {"README.md", "agents_list.md", ".agents/coordination.md",
         ".agents/tasks/README.md", "docs/CURRENT.md"}
RUNTIME_DIRS = {".agents/tasks", ".agents/messages", ".agents/handoffs",
                ".agents/feedback", ".agents/plans", ".agents/runs",
                ".agents/scratch", "results", "docs/history"}
DEVELOPMENT_PREFIXES = ("docs/maintenance/", "tests/", ".github/", "tools/legacy/")
# 与本地checker的v2最小锚点同步；读取Git对象时不导入或执行上游检查器。
CORE_FILES = {"AGENTS.md", ".agents/PROTOCOL.md", ".agents/coordination.md",
              ".agents/guides/git.md", ".agents/guides/modes.md",
              ".agents/tasks/TEMPLATE-lite.md", ".agents/template_manifest.json",
              "tools/check_template.py", "tools/template_manager.py"}
PROJECT_README = """# 项目名称

## 项目概述

待根据实际需求与实现补充项目用途、目标用户和当前功能。

## 运行与验证

待调查后填写实际安装、启动、构建与测试命令。

## 工程约定

已有规范可直接引用；未知项先通过调查任务补齐，业务代码修改前读取相关约定。

| 约定 | 本项目需要明确的内容 |
| --- | --- |
| 技术栈、依赖与环境 | 工具版本、安装命令与锁文件；无依赖时明确说明 |
| 目录与模块边界 | 源码、测试、资源和生成产物位置及模块职责 |
| 代码、命名与错误处理 | 现有风格、格式化配置、公共接口与错误约定 |
| 构建、测试与静态检查 | 实际命令、环境与成功标准；不适用项说明原因 |
| 敏感文件与忽略项 | 凭据、本地配置、资产策略、忽略项与示例配置 |
| 审查、验收与发布 | owner、必需检查、功能验收、CI与发布／回退步骤 |

## 协作入口

[Agent规则](AGENTS.md) · [当前工作](docs/CURRENT.md) · [模板使用须知](template_readme.md)
"""


def remote_source(source):
    # Git允许URL与scp写法；Windows盘符是本地路径，不能误当URL scheme。
    drive = bool(re.match(r"^[A-Za-z]:", source))
    return not drive and (bool(urlsplit(source).scheme) or bool(re.match(r"^[^/\\]+:.+", source)))


def normalize_source(source):
    if not isinstance(source, str) or not source.strip():
        raise ValueError("来源必须是非空URL或本地Git路径")
    return source if remote_source(source) else str(Path(source).expanduser().resolve())


def normalized(data):
    return data.decode("utf-8").replace("\r\n", "\n")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def path_key(name):
    """模板路径采用跨平台的规范形式；比较键不随宿主大小写规则变化。"""
    if not isinstance(name, str) or re.search(r'[\x00-\x1f<>:"\\|?*]', name):
        raise ValueError("非法模板路径")
    relative = PurePosixPath(name)
    if (relative.is_absolute() or ".." in relative.parts or not relative.parts or
            name != relative.as_posix()):
        raise ValueError("非法模板路径: " + name)
    for part in relative.parts:
        if (part.endswith((".", " ")) or
                re.fullmatch(r"(?:con|prn|aux|nul|com[1-9]|lpt[1-9]|conin\$|conout\$)(?:\..*)?",
                             part, re.IGNORECASE)):
            raise ValueError("不可移植的模板路径: " + name)
    key = name.casefold()
    if (any(part.casefold() == ".git" for part in relative.parts) or
            key in (STATE, LOCK, REPORTS, SIDECAR) or
            key.startswith((REPORTS + "/", SIDECAR + "/"))):
        raise ValueError("保留路径: " + name)
    return key


def safe_path(root, name):
    # 清单、状态和计划都经同一入口；符号链接解析后仍须在目标工程内。
    path_key(name)
    path = root.joinpath(*PurePosixPath(name).parts)
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError("路径逃逸: " + name)
    return path


def protected(name):
    name = path_key(name)
    if name in {seed.casefold() for seed in SEEDS}:
        return True
    parent = PurePosixPath(name).parent.as_posix()
    for directory in RUNTIME_DIRS:
        if name.startswith(directory + "/"):
            leaf = PurePosixPath(name).name
            # 只管理这些目录中的根级说明／格式；实际 task、交接、反馈和结果始终属于工程。
            return parent != directory or not (leaf == "readme.md" or leaf.startswith("template"))
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
    seen = set()
    for name in data["files"]:
        safe_path(root, name)
        key = path_key(name)
        if key in seen:
            raise ValueError("重复状态路径: " + name)
        seen.add(key)
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
        source = normalize_source(source)
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
        seen = set()
        for name in required:
            safe_path(self.repo, name)
            key = path_key(name)
            if key in seen:
                raise ValueError("重复清单路径: " + name)
            seen.add(key)
            if key.startswith(DEVELOPMENT_PREFIXES):
                raise ValueError("上游包含开发资产: " + name)
            if protected(name) and key not in {seed.casefold() for seed in SEEDS}:
                raise ValueError("上游包含工程运行记录: " + name)
            self.files[name] = self.blob(self.revision, name)
        anchors = {".agents/template_manifest.json", "tools/template_manager.py", "tools/check_template.py"}
        if manifest.get("version") == 2:
            anchors = CORE_FILES
        if not anchors.issubset(self.files):
            raise ValueError("上游缺少核心协议／工具: " + ", ".join(sorted(anchors - self.files.keys())))

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


def local_config(root, key):
    result = run_git("config", "--local", "--get-all", key, cwd=root, check=False)
    if result.returncode not in (0, 1):
        raise ValueError("无法读取本地 Git 绑定: " + key)
    values = result.stdout.decode("utf-8").splitlines()
    if len(values) > 1:
        raise ValueError("Git 绑定存在重复值: " + key)
    return values[0] if values else None


def sidecar_descriptor(root):
    path = root / SIDECAR
    if not path.resolve().is_relative_to(root):
        raise ValueError("旁路描述路径逃逸")
    value = json.loads(path.read_text(encoding="utf-8"))
    if (not isinstance(value, dict) or value.get("version") != 1 or
            not re.fullmatch(r"[0-9a-f]{32}", str(value.get("id", ""))) or
            not re.fullmatch(r"[0-9a-f]{40,64}", str(value.get("project_base_commit", "")))):
        raise ValueError("不支持的旁路描述")
    return value


def sidecar_project(root, project):
    project = Path(project).resolve()
    if root.is_relative_to(project) or project.is_relative_to(root):
        raise ValueError("协作目录与业务目录必须分离，不能相同或互相嵌套")
    if not project.is_dir() or git_root(project) != project:
        raise ValueError("--project-root 必须是已有业务 Git 的实际工作树根目录")
    run_git("rev-parse", "--verify", "HEAD^{commit}", cwd=project)
    if (project / ".agents/PROTOCOL.md").exists() or (project / STATE).exists():
        raise ValueError("业务目录已有模板；先明确迁移现有记录，不创建第二份任务板")
    return project


def validate_binding_target(root, project, descriptor):
    project = sidecar_project(root, project)
    if root.is_dir() and git_root(root) == root:
        def common(repo):
            value = run_git("rev-parse", "--git-common-dir", cwd=repo).stdout.decode().strip()
            return (repo / value).resolve()
        if common(root) == common(project):
            raise ValueError("协作与业务目录不能是同一 Git 仓库的两个 worktree")
    run_git("cat-file", "-e", descriptor["project_base_commit"] + "^{commit}", cwd=project)
    identity = local_config(project, "agent.sidecarId")
    if identity and identity != descriptor["id"]:
        raise ValueError("业务仓库已经绑定另一协作仓库")
    pointer = local_config(project, "agent.coordinationRoot")
    if pointer and Path(pointer).resolve() != root and Path(pointer).exists():
        raise ValueError("业务仓库已有可达主协作目录；拒绝接管或建立第二份任务板")
    return project


def bind_sidecar(root, project):
    """只绑定本机路径；Git 配置失败时恢复本次写入，不撤销他人配置。"""
    root = Path(root).resolve()
    if git_root(root) != root:
        raise ValueError("旁路协作目录必须是独立 Git 工作树根目录")
    if read_state(root).get("installation_mode") != "sidecar":
        raise ValueError("bind 只用于旁路安装")
    descriptor = sidecar_descriptor(root)
    project = sidecar_project(root, project)
    common = Path(run_git("rev-parse", "--git-common-dir", cwd=project).stdout.decode().strip())
    common = (project / common).resolve()
    previous_project = local_config(root, "agent.projectRoot")
    if previous_project and Path(previous_project).exists():
        previous_root = Path(previous_project).resolve()
        if not previous_root.is_dir() or git_root(previous_root) != previous_root:
            raise ValueError("旧业务路径已被其他内容占用；先核对并清除旧 agent.projectRoot")
        old_common = run_git("rev-parse", "--git-common-dir", cwd=previous_root).stdout.decode().strip()
        if (previous_root / old_common).resolve() != common:
            raise ValueError("协作仓库已绑定另一可达业务仓库；先明确迁移，不保留双向歧义")
    # 同一业务仓库的多个 worktree 共用绑定锁；它不替代代码开发的隔离或互斥。
    lock = common / "agent-sidecar.lock"
    try:
        stream = lock.open("x", encoding="utf-8")
    except FileExistsError as error:
        raise ValueError("业务绑定锁已存在；确认持有者停写后再处理，不自动删锁") from error
    try:
        with stream:
            json.dump({"pid": os.getpid(), "host": socket.gethostname()}, stream)
        validate_binding_target(root, project, descriptor)
        updates = [(project, "agent.sidecarId", descriptor["id"]),
                   (project, "agent.coordinationRoot", str(root)),
                   (root, "agent.coordinationRoot", str(root)),
                   (root, "agent.projectRoot", str(project))]
        previous = [(repo, key, value, local_config(repo, key)) for repo, key, value in updates]
        written = []
        try:
            for repo, key, value, old in previous:
                if local_config(repo, key) != old:
                    raise ValueError("绑定配置发生并发变化: " + key)
                run_git("config", "--local", key, value, cwd=repo)
                written.append((repo, key, value, old))
        except Exception as error:
            failures = []
            for repo, key, value, old in reversed(written):
                try:
                    if local_config(repo, key) != value:
                        failures.append(key + " 已被其他执行者修改")
                    elif old is None:
                        run_git("config", "--local", "--unset-all", key, cwd=repo)
                    else:
                        run_git("config", "--local", key, old, cwd=repo)
                except (ValueError, OSError) as recovery_error:
                    failures.append(str(recovery_error))
            if failures:
                raise ValueError("绑定失败，部分配置未恢复: " + "; ".join(failures)) from error
            raise
    finally:
        lock.unlink(missing_ok=True)
    print("BOUND", root, "PROJECT", project)


def check_sidecar(root, state=None):
    state = read_state(root) if state is None else state
    marker = root / SIDECAR
    if state.get("installation_mode", "in-tree") not in ("in-tree", "sidecar"):
        raise ValueError("未知安装模式")
    if state.get("installation_mode") != "sidecar":
        if marker.exists():
            raise ValueError("旁路描述与安装模式不一致")
        return None
    if git_root(root) != root:
        raise ValueError("旁路协作 Git 根无效")
    descriptor = sidecar_descriptor(root)
    project_path = local_config(root, "agent.projectRoot")
    if not project_path or not Path(project_path).is_absolute():
        raise ValueError("旁路业务路径未绑定；使用 bind --root COLLAB --project-root PROJECT")
    project = validate_binding_target(root, project_path, descriptor)
    for repo in (root, project):
        pointer = local_config(repo, "agent.coordinationRoot")
        if not pointer or not Path(pointer).is_absolute() or Path(pointer).resolve() != root:
            raise ValueError("旁路主目录绑定失效；使用 bind 显式恢复")
    if local_config(project, "agent.sidecarId") != descriptor["id"]:
        raise ValueError("旁路身份绑定失效；使用 bind 显式恢复")
    return project


def entry(root):
    root = Path(root).resolve()
    print("【旁路模式：当前文件夹是协作文件夹】")
    print("协作文件夹：", root)
    project = check_sidecar(root)
    if project is None:
        raise ValueError("entry 只用于旁路安装")
    print("指向的业务文件夹：", project)
    print("新 Agent 默认打开协作文件夹；首次回复必须向用户显示以上说明与两个实际路径。")
    print("先读取以下协作入口：", root / "AGENTS.md")
    print("同时读取业务目录现有规则与 README 工程约定；任务、消息、交接和执行证据写协作目录。")
    print("源码、业务文档、构建和测试在业务工作树；两仓库分别审查提交，task 记录业务基线与交付 SHA。")
    print("核对两个目录的实际访问权限；并行代码开发使用业务仓库的独立 worktree。")


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


def require_update_commit(root):
    """写模板前确认提交条件，沿用工程身份与当前分支。"""
    if git_root(root) != root:
        raise ValueError("自动提交需要工程根的 Git 仓库；无 Git 工程使用 --no-commit")
    git_dir = Path(run_git("rev-parse", "--absolute-git-dir", cwd=root).stdout.decode().strip())
    if any((git_dir / name).exists() for name in
           ("MERGE_HEAD", "CHERRY_PICK_HEAD", "REVERT_HEAD", "rebase-merge", "rebase-apply", "sequencer")):
        raise ValueError("Git 正在合并／变基／接续提交；先完成当前操作再更新模板")
    # 锁和报告虽允许留在工作区，也不能把已暂存的这些内容带入自动提交。
    if run_git("diff", "--cached", "--quiet", cwd=root, check=False).returncode:
        raise ValueError("暂存区不是空的；先保存或处理已有暂存内容")
    run_git("var", "GIT_AUTHOR_IDENT", cwd=root)
    run_git("var", "GIT_COMMITTER_IDENT", cwd=root)


def commit_template_update(root, plan):
    # 字面路径避免方括号等被Git当作匹配式；--only不带入后来暂存的业务文件。
    paths = sorted({entry["path"] for entry in plan["entries"]} | {STATE})
    try:
        run_git("--literal-pathspecs", "add", "--", *paths, cwd=root)
        changed = run_git("--literal-pathspecs", "diff", "--cached", "--quiet", "--", *paths,
                          cwd=root, check=False)
        if changed.returncode == 0:
            print("NO_COMMIT_NEEDED")
            return
        if changed.returncode != 1:
            raise ValueError("无法检查模板暂存差异")
        run_git("--literal-pathspecs", "commit", "--only", "-m",
                "[TEMPLATE][update] update to " + plan["revision"][:12],
                "--", *paths, cwd=root)
    except (ValueError, OSError) as error:
        # 写入已经成功；提交失败时保留改动与备份，供用户核对后重试提交。
        raise ValueError("模板已应用，但自动提交失败；改动与更新报告已保留：" + str(error)) from error
    print("COMMITTED", run_git("rev-parse", "HEAD", cwd=root).stdout.decode().strip())


def initialize(root, source, ref, no_git=False, commit=False, mode="in-tree", project_root=None):
    root = Path(root).resolve()
    if mode not in ("in-tree", "sidecar"):
        raise ValueError("未知安装模式")
    descriptor = None
    if mode == "sidecar":
        if no_git or project_root is None:
            raise ValueError("旁路安装需要 --project-root 且不能 --no-git")
        project_root = sidecar_project(root, project_root)
        descriptor = {"version": 1, "id": uuid.uuid4().hex, "project_base_commit":
                      run_git("rev-parse", "HEAD", cwd=project_root).stdout.decode().strip()}
        validate_binding_target(root, project_root, descriptor)
    elif project_root is not None:
        raise ValueError("--project-root 仅用于 --mode sidecar")
    if commit and no_git:
        raise ValueError("--commit 与 --no-git 不兼容")
    # 先下载并验证；网络失败不留下一个让下次 init 被拒绝的半空工程。
    with tempfile.TemporaryDirectory() as temp:
        upstream = Upstream(temp, source, ref)
        if descriptor and "docs/sidecar.md" not in upstream.files:
            raise ValueError("该来源版本不支持旁路模式；请选择支持旁路的版本")
        root.mkdir(parents=True, exist_ok=True)
        if any(path.name != ".git" for path in root.iterdir()):
            raise ValueError("init 只接受空目录；已有工程使用 adopt")
        existing = git_root(root)
        if existing and existing != root:
            raise ValueError("不能在父仓库内创建嵌套工程")
        if existing and run_git("rev-parse", "--verify", "HEAD", cwd=root, check=False).returncode == 0:
            raise ValueError("该仓库已有历史，不按空新工程初始化")
        with write_lock(root):
            # 新清单不携带母仓库README；旧版本仍按其原清单安装以保持兼容。
            installed = dict(upstream.files)
            if "README.md" not in installed:
                installed["README.md"] = PROJECT_README
            if descriptor:
                installed["README.md"] = SIDECAR_README
            state = {"version": 1, "source": upstream.source, "ref": ref, "revision": upstream.revision,
                     "files": {name: baseline(upstream, text) for name, text in upstream.files.items()}}
            if descriptor:
                state["installation_mode"] = "sidecar"
            for name, text in installed.items():
                atomic_write(safe_path(root, name), text.encode("utf-8"))
            atomic_write(root / STATE, (json.dumps(state, ensure_ascii=False, indent=2) + "\n").encode())
            if descriptor:
                atomic_write(root / SIDECAR, (json.dumps(descriptor, indent=2) + "\n").encode())
            if not no_git:
                if not existing:
                    run_git("init", "-b", "main", cwd=root)
                run_git("config", "--local", "agent.coordinationRoot", root, cwd=root)
                if descriptor:
                    bind_sidecar(root, project_root)
                if commit:
                    run_git("--literal-pathspecs", "add", "--", *installed, STATE,
                            *([SIDECAR] if descriptor else []), cwd=root)
                    run_git("commit", "-m", "[BOOTSTRAP][template] initialize project template", cwd=root)
            print("INITIALIZED", root, upstream.revision)
            if descriptor:
                entry(root)
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
        state = {"version": 1, "source": upstream.source, "ref": ref, "revision": upstream.revision, "files": records}
        atomic_write(root / STATE, (json.dumps(state, ensure_ascii=False, indent=2) + "\n").encode())
        print("ADOPTED", root, "existing files unchanged")
        return state


def three_way(current, base, incoming, directory):
    directory.mkdir(parents=True, exist_ok=True)
    paths = [directory / name for name in ("current", "base", "upstream")]
    for path, text in zip(paths, (current, base, incoming)):
        path.write_bytes(text.encode("utf-8"))
    result = run_git("merge-file", "--stdout", "--diff3", "-L", "LOCAL", "-L", "BASE",
                     "-L", "UPSTREAM", *paths, check=False)
    if result.returncode < 0 or result.returncode > 127:
        raise ValueError("三方合并工具失败")
    return normalized(result.stdout), result.returncode != 0


def make_plan(root, upstream, state, temp):
    if state.get("installation_mode") == "sidecar" and "docs/sidecar.md" not in upstream.files:
        raise ValueError("旁路安装不能更新到不支持旁路的来源版本")
    changed, conflicts, skipped = [], [], []
    new_state = json.loads(json.dumps(state))
    new_state.update(revision=upstream.revision, source=upstream.source, ref=upstream.ref)
    for name, incoming in upstream.files.items():
        path = safe_path(root, name)
        if path.exists() and not path.is_file():
            raise ValueError("目标不是普通文件: " + name)
        # README只在init产生；即使回选旧清单，也不重建业务已删除的README。
        if name.casefold() == "readme.md" or (path.exists() and protected(name)):
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
    if "README.md" not in upstream.files:
        # 旧业务README转为完全由业务持有；只移除基线项，不删除或恢复文件。
        new_state["files"].pop("README.md", None)
        removed = [name for name in removed if name != "README.md"]
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
    current_state = read_state(root)
    check_sidecar(root, current_state)
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
        key = path_key(name)
        if key in seen:
            raise ValueError("重复计划文件: " + name)
        seen.add(key)
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
    if next_state.get("installation_mode") != current_state.get("installation_mode"):
        raise ValueError("更新计划不能切换安装模式")
    state_seen = set()
    for name in next_state["files"]:
        safe_path(root, name)
        key = path_key(name)
        if key in state_seen:
            raise ValueError("重复状态路径: " + name)
        state_seen.add(key)
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
    except Exception as error:
        # 某一文件被外部删除或恢复失败，不能中断其他文件的恢复。
        rollback_errors = []
        recovery = [(STATE, state_bytes, before_state)] + [
            (name, changes[name], originals[name]) for name in reversed(written)]
        for name, ours, original in recovery:
            try:
                path = state_path if name == STATE else safe_path(root, name)
                current = path.read_bytes() if path.exists() else None
                if current == ours:
                    if original is None:
                        path.unlink()
                    else:
                        atomic_write(path, original)
            except (OSError, ValueError) as rollback_error:
                rollback_errors.append(name + ": " + str(rollback_error))
        if rollback_errors:
            raise ValueError("更新失败，部分恢复未完成；核对报告备份：" +
                             "; ".join(rollback_errors)) from error
        raise
    print("APPLIED", len(changes), "files", plan["revision"], "backup", plan_path.parent)
    return plan


def update(root, check=False, source=None, ref=None, commit=False):
    root = Path(root).resolve()
    state = read_state(root)
    check_sidecar(root, state)
    if source is None and not remote_source(state["source"]) and not Path(state["source"]).is_absolute():
        # 旧相对来源的原始调用目录不可恢复；要求明确选择，不猜一个新的仓库。
        raise ValueError("旧基线使用相对本地来源；请用 update --source 明确原Git来源")
    if not check:
        require_clean(root)
    with tempfile.TemporaryDirectory() as temp:
        # 默认沿用原分支／固定标签；只有显式选择才切换，预览或冲突不写基线。
        upstream = Upstream(temp, source if source is not None else state["source"],
                            ref if ref is not None else state["ref"])
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
        if commit and not plan["conflicts"]:
            require_update_commit(root)
        report = save_plan(root, plan)
        if plan["conflicts"]:
            print("NO_FILES_APPLIED", report, "edit proposed files, then use apply --plan")
            return 2
        applied = apply_plan(root, report)
        if commit:
            commit_template_update(root, applied)
            print("Review git show HEAD and run project checks.")
        else:
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
            command.add_argument("--mode", choices=("in-tree", "sidecar"), default="in-tree",
                                 help="默认工程内安装；sidecar 在独立协作目录安装")
            command.add_argument("--project-root", help="旁路模式绑定的已有业务 Git 工作树根")
        if name == "update":
            command.add_argument("--check", action="store_true")
            commits = command.add_mutually_exclusive_group()
            commits.add_argument("--commit", dest="commit", action="store_true", help="更新成功后提交（默认）")
            commits.add_argument("--no-commit", dest="commit", action="store_false", help="应用更新后保留改动，手动提交")
            command.set_defaults(commit=True)
            command.add_argument("--source", help="明确恢复或更换来源；预览不写基线，实际更新才保存")
            command.add_argument("--ref", help="明确切换到已有分支／标签；成功应用后保存新引用")
        if name == "apply":
            command.add_argument("--plan", required=True)
            command.add_argument("--commit", action="store_true", help="应用已审阅的冲突候选后提交")
    for name in ("bind", "entry"):
        command = sub.add_parser(name)
        command.add_argument("--root", default=".", help="旁路协作目录")
        if name == "bind":
            command.add_argument("--project-root", required=True, help="明确恢复绑定的业务工作树根")
    args = parser.parse_args()
    try:
        if args.command == "init":
            initialize(args.root, args.source, args.ref, args.no_git, args.commit,
                       args.mode, args.project_root)
        elif args.command == "adopt":
            adopt(args.root, args.source, args.ref)
        elif args.command == "update":
            if args.check:
                return update(args.root, True, args.source, args.ref)
            with write_lock(Path(args.root).resolve()):
                return update(args.root, source=args.source, ref=args.ref, commit=args.commit)
        elif args.command == "bind":
            root = Path(args.root).resolve()
            with write_lock(root):
                bind_sidecar(root, args.project_root)
            entry(root)
        elif args.command == "entry":
            entry(args.root)
        else:
            root = Path(args.root).resolve()
            with write_lock(root):
                require_clean(root)
                if args.commit:
                    require_update_commit(root)
                applied = apply_plan(root, args.plan)
                if args.commit:
                    commit_template_update(root, applied)
        return 0
    except (ValueError, OSError, SyntaxError, json.JSONDecodeError) as error:
        print("ERROR:", error)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
