# 跨 Agent 协作操作入口

正式规则见 [根 AGENTS](../../AGENTS.md) 和 [协作协议](../../.agents/PROTOCOL.md)。参与者在 [登记表](../../agents_list.md)，动态进度在 [任务板](../../.agents/tasks/README.md)。

## 先读什么

1. 运行 `git config --get agent.coordinationRoot`，确认唯一主协作目录。
2. 在该目录读登记表、协议、task、相关消息／交接与 Git 历史。
3. 本人确认负责范围和依赖；新分工保留 proposed，确认后由 integrator 更新任务表。
4. 按分配范围写产出，报告真实验证；不要替其他 Agent 回执。

## 怎么留言

使用 [消息模板](TEMPLATE.md)，写到主目录的 .agents/messages/<TASK-ID>/<agent-id>.md。每个实例写自己的文件，回复注明消息 ID。暂停或交付写 .agents/handoffs/<TASK-ID>/<agent-id>.md。

本次已有 [gpt 的 COLLAB001 交接](../../.agents/handoffs/COLLAB001/gpt.md)，供其他 Agent 下一轮读取；没有发送到 WorkBuddy 应用，也没有收到它的确认。

旧 docs/collaboration/topics 消息如已存在可保留供查阅；新消息用任务 ID 组织，不建两个活跃消息系统。

## 开真正并行的工作树

下面命令是待任务实际接收后运行的例子，本次未预先创建这些工作树：

```powershell
# 在主工作树由 integrator 执行，先核对任务、基线和 git status。
git worktree add -b agent/wb/R002 .worktrees/wb-R002 main
git worktree list
```

让 WorkBuddy 实际打开新路径，再确认它读到了规则。该工作树里的任务表是 main 的快照；通过 Git 本地配置取得主目录后读取最新任务。新建独立 clone 时需要额外配置协作目录，不能假设本地配置自动复制。

worker 在自己的分支提交明确交付物，整合者根据 handoff 验证后 merge / cherry-pick。scope 重叠、接口不兼容和未验证结果不能靠 Git 自动解决。

## 初始化和测试

```powershell
python tools/agent_bootstrap.py --root . --check
python -m unittest discover -s tests -v
git status --short
git log --format=full --max-count=3
```

新工程复制 [project_templateA](../../gpt/project_templateA/template_readme.md) 目录内全部内容到根目录，包含隐藏文件；模板已展开，按短入口与对应规则使用。具体评估与限制见 [方案评估](../../gpt/research/multi-agent-protocol-review.md)。

如发现 .agents/.bootstrap.lock，核对内容中的 host / pid，确认初始化持有者已结束后才由 integrator 清理；不要在活跃初始化期间删除锁。

## 同一任务的独立对照

每个新任务确认 collaboration_mode；未明确时由 integrator 用可用交互工具询问，已明确则读取记录，无工具改为文字提问。串行接力、分工协作与同任务独立对照分别处理；细节见 [模式指南](../../.agents/guides/modes.md)。

独立对照不要求把同一个目标拆成不同目标子任务；参与者各自完整作答，各写 results/<TASK-ID>/<RUN-ID>/<agent-id>/，首稿不互读，提交后统一评估。当前已有 gpt/ 与 wb/ 报告保持原位，历史独立性未经严格实验验证。

## 旧初始化锁的人工恢复

仅适用于本工程旧 tools/agent_bootstrap.py；可复制的多文件模板不创建 .bootstrap.lock 或初始化标记。

1. 先取得 git config --get agent.coordinationRoot 指定的实际主目录，在该目录操作，不能在 worker 的分支快照解锁。
2. 读取锁内 host／pid。在相同机器核对进程，并与持有者确认初始化已经结束；PID 可复用，进程名／创建时间也需要核对。远程机器的 PID 不能用本机进程列表推断。信息不足时先找实际持有者，不按时间猜测。
3. **只有持有者已经停写且有处理权限时**，由 integrator 人工执行清理；下面最后一行不是自动检测逻辑。

```powershell
# 在已经确认的主目录读取；此处不删除。
$taskLockPath = Join-Path (Get-Location) '.agents/.bootstrap.lock'
$lockOwner = Get-Content -LiteralPath $taskLockPath -Raw | ConvertFrom-Json
$lockOwner
# 仅当 host 确认是本机时使用；无结果不等于已获得解锁授权。
Get-CimInstance Win32_Process -Filter ("ProcessId = {0}" -f [int]$lockOwner.pid) |
    Select-Object ProcessId, Name, CreationDate
# 完成人工核对后单独执行，不和检测命令当作自动脚本运行。
Remove-Item -LiteralPath $taskLockPath
```

清理后运行 python tools/agent_bootstrap.py --root . --check；确有旧基础文件缺失时再运行初始化器只补缺项，不覆盖当前协议。新模板／新增指南通过 Git 和模板清单维护，不让旧初始化器恢复为旧协议。

## 工具加载与接班

按需阅读 [工具加载指南](../../.agents/guides/tools.md)、[共享协调记录](../../.agents/coordination.md) 和 [继任指南](../../.agents/guides/coordination.md)。本轮 [WB 逐项评审回复](../../.agents/messages/COLLAB003/gpt.md) 与 [ADR-002](../decisions/002-integrator-succession.md) 说明采纳范围。
