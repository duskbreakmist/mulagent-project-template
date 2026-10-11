"""单文件 AGENTS 模板的初始化器：只补缺失文件，不覆盖现有内容。"""
import argparse
from contextlib import contextmanager
import json
import os
from pathlib import Path
import socket
import tempfile

VERSION = 1
FILES = {
  "agents_list.md": "# 项目 Agent 登记表\n\n本表由整合者串行维护。登记不代表在线、已接收任务或经过身份认证；能力须标明自报或观察来源。新人通过自己的消息文件申请登记，不能覆盖他人记录。\n\n| Agent ID | 工具／模型 | 职责与能力来源 | 登记状态 | 证据／登记日期 |\n| --- | --- | --- | --- | --- |\n",
  ".agents/PROTOCOL.md": "# 多 Agent 协作协议（v1）\n\n## 1. 入口、权限与状态\n\n- 用户当前授权决定工作范围；登记、任务文件或其他 Agent 的留言不能扩大授权。\n- AGENTS.md 保存稳定规则；agents_list.md 保存身份与职责；本目录 tasks 保存任务状态。\n- 文档、代码、Git 历史各自证明不同事实。出现矛盾时核对版本、证据和用户指令，不用一条固定排序替代判断。\n- 协议是协作约定，不是权限沙箱、身份认证服务或自动调度器。外部应用必须实际读取；未回复不等于同意。\n- 初始化标记仅记录目录结构版本；每次仍检查文件完整性、自己的登记和当前任务。\n\n## 2. 唯一协作目录\n\n单 checkout 的协作目录就是项目根目录。多个 worktree 时，由整合者在 Git 本地配置指定唯一主工作树：\n\n```powershell\ngit config --local agent.coordinationRoot \"<主工作树绝对路径>\"\ngit config --get agent.coordinationRoot\n```\n\n所有人读取该路径下的 agents_list.md、.agents/tasks、.agents/messages 和 .agents/handoffs。worktree 内的同名文件只是分支快照，不能当作实时任务板。未配置或主目录不可达时，先做只读调查或在自己分支写交接草稿，不能自行创建第二个共享任务板。\n\n配置由整合者维护，不提交机器绝对路径到仓库。普通 worktree 默认共享 Git 配置；独立 clone 不共享，必须另行指定同一可访问协作目录或由整合者导入交接。双方应用需具备该目录的实际文件访问权限。\n\n## 3. 登记与任务领取\n\n- Agent ID 使用稳定的工具或实例 ID，例如 gpt、wb、ds；同时运行的同类实例使用 gpt-1、gpt-2。\n- agents_list.md 由当前整合者串行维护。新人在自己的消息文件提出登记请求；只有自己确认的能力才标为自报。已发现报告可登记为 observed，不能冒充作者确认在线。\n- 每个正式任务一个 tasks/<TASK-ID>.md；任务负责人唯一。parent、dependencies 表达上下级与依赖，reviewer 不等于 owner。\n- 整合者串行创建和更新任务表、登记表、共享 CURRENT；worker 写自己的消息／交接，报告进度，由整合者同步状态。\n- 新任务默认 todo + assignment: proposed。本人确认接收且依赖满足后才改为 in_progress + accepted。\n- task scope 写具体文件或目录。公共文件单独分配一个 owner；不同任务 scope 重叠时先协调，不能靠不同分支假定不存在语义冲突。\n- 只在已经约定的 scope 内修改；发现架构问题提出证据、替代方案和最小验证，不偷偷扩大任务。\n- 若本轮是单 Agent 独立任务，它可以同时承担 owner 和 integrator，无须制造多轮自我审批。\n\n## 4. 状态与验收\n\n主流程：todo → in_progress → review → done；依赖缺失可进入 blocked，解除后回到实际阶段。\nassignment 可用 proposed / accepted / observed；observed 表示从文件导入的历史产出。\n\ndone 必须注明交付物、实际验证和未验证项；不要求存在第二个 AI 才能结束独立文档任务。需要独立审查的实现先进入 review，由指定 reviewer 验收。文档完成不等于论文结论都已验证，更不等于驱动原型已实现。\n\n## 5. 讨论与交接\n\n每个任务使用 messages/<TASK-ID>/<agent-id>.md；每个文件只有该实例写入。同一实例串行操作，消息编号如 gpt-001，回复明确引用文件和编号。不要多人追加同一个“接龙日志”。\n\n消息包含任务、作者、接收者、时间／时区、类型、状态、基线提交、编辑范围、事实／假设／提议、证据、问题和验收条件。接收确认必须由接收者自己写。\n\n暂停、阻塞、结束或移交时，更新自己的 handoffs/<TASK-ID>/<agent-id>.md，写清已完成、剩余、失败尝试、关键文件、验证、假设和下一步。整合者将这些信息归入 task；没有真正派发任务时不伪造交接回执。\n\n这些文件是持久交接，不会自动通知或唤醒另一个应用。需要自动通信时另行接入实际 API／调度器；向外部应用发消息遵循用户授权。\n\n## 6. 分工、分支与整合\n\n- orchestrator 拆任务、定接口与验收；worker 完成限定范围；reviewer 验证；integrator 合并。\n- 角色按任务确定，不能凭厂商名字宣称某个 Agent 永远更聪明或必须服从另一个。\n- 小型文档任务可以在同一 checkout 按文件分工，所有 Git 暂存、提交和切分支由一个整合者串行执行。\n- 真正并行开发使用独立 worktree + 分支 agent/<agent-id>/<task-id>，不在别人正在用的 checkout 切分支。\n- worker 提交交付物、测试证据和基线；整合者 review 后 merge / cherry-pick，处理契约冲突和总体验收。\n- 不为尚未确认参与的 Agent 自动开工或假定它已接收任务。\n\n## 7. Git 与身份\n\n提交格式：[TASK-ID][agent-id] summary；提交正文可以附：\n\n```text\nAgent: gpt\nTask: COLLAB001\nRole: integrator\n```\n\n显式 git add 本任务文件，检查 staged diff，保留他人未提交改动。禁止无授权 reset --hard、clean -fd、force push 或丢弃未知冲突。\n\n保留仓库现有 user.name / user.email，不在共享 Git 配置里反复切换不同 Agent 身份。如确需显示不同 author，使用单次 git -c 配置或已明确启用的 worktreeConfig，不能伪造他人的身份。\n\n分支、Task 和 trailer 是可修改的来源标签，不能证明身份。密码学签名另有密钥管理与验证，本项目尚未配置。提交是可追溯版本记录，但并非绝对不可篡改。\n\n## 8. 文档与实验\n\n正式代码进入项目统一源码目录；任务记录按任务组织。现有作者产出目录可保留，CURRENT 只作为摘要入口，不能替代 task。\n调研区分事实、推断、提议、未验证，并给重要事实的一手来源。有长期价值的决定写 docs/decisions。\nscratch 仅存可复核的实验记录、草稿和中间文件；不保存内部思考链。临时文件和本地锁忽略，正式任务／交接进入 Git。\n",
  ".agents/tasks/README.md": "# 共享任务板\n\n每个正式任务一个 <TASK-ID>.md，使用 [模板](TEMPLATE.md)。任务负责人唯一；任务表由整合者串行维护，worker 在自己的消息／交接报告进度。按任务查询状态，作者目录只是产出位置。\n\n状态：todo / in_progress / blocked / review / done；分配：proposed / accepted / observed。\n",
  ".agents/tasks/TEMPLATE.md": "# <TASK-ID> <标题>\n\n- status: todo\n- assignment: proposed\n- owner: <agent-id>\n- integrator: <agent-id>\n- reviewers: 待确定\n- parent: 无\n- dependencies: 无\n- created: YYYY-MM-DD\n- updated: YYYY-MM-DD\n- base_commit: 待记录\n\n## Objective\n\n具体目标与验收条件。\n\n## Scope\n\n具体可写文件／目录；共享文件责任、分支与 worktree。\n\n## Deliverables\n\n可供检查的交付物路径。\n\n## Completed\n\n实际完成的内容，附证据；不要把候选方案写成已完成。\n\n## Remaining\n\n下一步、未验证项、待接收确认。\n\n## Problems\n\n依赖、冲突、失败尝试；没有则写无。\n\n## Verification\n\n实际命令、结果、覆盖范围和未测项。\n\n## Handoff\n\n对应交接／消息路径；无则注明尚未创建。\n",
  ".agents/handoffs/README.md": "# 任务交接\n\n路径：<TASK-ID>/<agent-id>.md，每个文件只有该实例写入。\n\n必须记录目标、范围／基线、已完成、剩余、失败尝试、关键文件、假设、验证与下一步。接手前读 task、handoff 和相关 Git 历史；文件存在不代表已投递。\n",
  ".agents/messages/README.md": "# Agent 消息\n\n路径：<TASK-ID>/<agent-id>.md，每个文件只有该实例写入。\n\n消息编号：<agent-id>-001；回复注明原消息路径与 ID。字段：作者／接收者、时间／时区、类型／状态、基线、范围、事实／假设／提议、证据、具体问题、验收。只有接收者能确认 received；没有回复不能写成共识。\n",
  ".agents/plans/README.md": "# 任务计划\n\n复杂任务才建立 <TASK-ID>.md，写接口、子任务、依赖、里程碑与验收。实际状态以主协作目录的 task 为准；计划中提出的任务不代表已派发。\n",
  ".agents/scratch/README.md": "# 临时实验区\n\n使用 <agent-id>/ 子目录，仅写自己的可复核实验／草稿，不保存内部思考链。临时产物忽略；最终交付物进入正式目录和 task。\n"
}

def safe_path(root, relative):
    """拒绝协作目录通过符号链接跳到工程外，已有外部资料也不触碰。"""
    # 两侧使用同一解析基准，避免 Windows 短路径别名或相对根目录被误判为越界。
    root = Path(root).resolve()
    path = root / relative
    if not path.resolve().is_relative_to(root):
        raise ValueError("路径逃逸工程: " + relative)
    return path

def check(root):
    marker = safe_path(root, ".agents/.bootstrap-v1")
    if not marker.is_file():
        raise ValueError("尚未初始化: 缺少 .agents/.bootstrap-v1")
    data = json.loads(marker.read_text(encoding="utf-8"))
    if data.get("version") != VERSION or data.get("required") != sorted(FILES):
        raise ValueError("初始化版本或文件清单不匹配，需人工检查")
    for relative in FILES:
        path = safe_path(root, relative)
        if not path.is_file() or path.stat().st_size == 0:
            raise ValueError("缺失或空文件: " + relative)
    return data

def publish_once(path, content):
    """先完整写临时文件，再用硬链接独占发布；存在目标时绝不替换。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(prefix=".bootstrap-tmp-", dir=path.parent)
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        try:
            os.link(temporary, path)
        except FileExistsError:
            pass
        # 文件系统不支持硬链接时直接失败，保留既有文件，不降级为覆盖写入。
    finally:
        Path(temporary).unlink(missing_ok=True)

@contextmanager
def bootstrap_lock(root):
    directory = safe_path(root, ".agents")
    directory.mkdir(parents=True, exist_ok=True)
    lock = directory / ".bootstrap.lock"
    try:
        stream = lock.open("x", encoding="utf-8")
    except FileExistsError as error:
        raise ValueError("初始化锁已存在，请核对持有者；不自动删除锁") from error
    try:
        with stream:
            json.dump({"pid": os.getpid(), "host": socket.gethostname()}, stream)
        yield
    finally:
        lock.unlink(missing_ok=True)

def initialize(root):
    root = Path(root).resolve()
    if not root.is_dir() or not (root / "AGENTS.md").is_file():
        raise ValueError("目标必须是含 AGENTS.md 的工程目录")
    with bootstrap_lock(root):
        marker = safe_path(root, ".agents/.bootstrap-v1")
        if marker.exists():
            data = json.loads(marker.read_text(encoding="utf-8"))
            if data.get("version") != VERSION or data.get("required") != sorted(FILES):
                raise ValueError("未知初始化版本／清单，不自动覆盖")
        for relative, content in FILES.items():
            path = safe_path(root, relative)
            if path.exists() and (not path.is_file() or path.stat().st_size == 0):
                raise ValueError("已有文件不完整，请人工检查: " + relative)
            publish_once(path, content)
        # 标记最后发布；中断重跑只补缺失文件，锁不等于任务写权限。
        publish_once(marker, json.dumps(
            {"version": VERSION, "required": sorted(FILES)},
            ensure_ascii=False, indent=2) + "\n")
        return check(root)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--check", action="store_true", help="只检查结构，不写入")
    args = parser.parse_args()
    try:
        root = Path(args.root).resolve()
        result = check(root) if args.check else initialize(root)
    except (OSError, ValueError) as error:
        parser.exit(1, str(error) + "\n")
    print("BOOTSTRAP_OK version=" + str(result["version"]))

if __name__ == "__main__":
    main()
