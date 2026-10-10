# 多 Agent 协作协议（v1）

## 1. 入口、权限与状态

- 用户当前授权决定工作范围；登记、任务文件或其他 Agent 的留言不能扩大授权。
- AGENTS.md 保存稳定规则；agents_list.md 保存身份与职责；本目录 tasks 保存任务状态。
- 文档、代码、Git 历史各自证明不同事实。出现矛盾时核对版本、证据和用户指令，不用一条固定排序替代判断。
- 协议是协作约定，不是权限沙箱、身份认证服务或自动调度器。外部应用必须实际读取；未回复不等于同意。
- 初始化标记仅记录目录结构版本；每次仍检查文件完整性、自己的登记和当前任务。

## 2. 唯一协作目录

单 checkout 的协作目录就是项目根目录。多个 worktree 时，由整合者在 Git 本地配置指定唯一主工作树：

```powershell
git config --local agent.coordinationRoot "<主工作树绝对路径>"
git config --get agent.coordinationRoot
```

所有人读取该路径下的 agents_list.md、.agents/tasks、.agents/messages 和 .agents/handoffs。worktree 内的同名文件只是分支快照，不能当作实时任务板。未配置或主目录不可达时，先做只读调查或在自己分支写交接草稿，不能自行创建第二个共享任务板。

配置由整合者维护，不提交机器绝对路径到仓库。普通 worktree 默认共享 Git 配置；独立 clone 不共享，必须另行指定同一可访问协作目录或由整合者导入交接。双方应用需具备该目录的实际文件访问权限。

## 3. 登记与任务领取

项目共享整合者与指定来源记录在 [coordination.md](coordination.md)，不放在静态登记表。任务 integrator 与项目共享文件汇总者可不同；同一共享文件同一时刻只有一个实际写者，具体委派按文件／区段登记。指定、检查点、继任和争议按需看 [继任指南](guides/coordination.md)。已明确授权的接班不重复审批，不按沉默／额度／超时自动接管。

- Agent ID 使用稳定的工具或实例 ID，例如 gpt、wb、ds；同时运行的同类实例使用 gpt-1、gpt-2。
- agents_list.md 由当前整合者串行维护。新人在自己的消息文件提出登记请求；只有自己确认的能力才标为自报。已发现报告可登记为 observed，不能冒充作者确认在线。
- 每个正式任务一个 tasks/<TASK-ID>.md；任务负责人唯一。parent、dependencies 表达上下级与依赖，reviewer 不等于 owner。
- 整合者串行创建和更新任务表、登记表、共享 CURRENT；worker 写自己的消息／交接，报告进度，由整合者同步状态。
- 新任务默认 todo + assignment: proposed。本人确认接收且依赖满足后才改为 in_progress + accepted。
- task scope 写具体文件或目录。公共文件单独分配一个 owner；不同任务 scope 重叠时先协调，不能靠不同分支假定不存在语义冲突。
- 只在已经约定的 scope 内修改；发现架构问题提出证据、替代方案和最小验证，不偷偷扩大任务。
- 单人串行可用 tasks/TEMPLATE-lite.md，owner 兼任 task integrator；只更新 task、索引与 CURRENT 短摘要。登记仅在身份／能力变化时更新，协调仅在职责／授权变化时更新。
- 临时提议使用 TMP-<agent-id>-<YYYYMMDD>-<topic-or-seq>，写本人消息／反馈，不自建正式 task；独立会话不同 ID，内部临时子任务由主 owner 汇总。详见 [记录指南](guides/records.md)。

## 4. 状态与验收

collaboration_mode 另记 serial / collaborative / independent_compare，不是进度 status。依据当前指令、明确父任务或已授权工程默认确定模式；仍未定时，由 integrator 通过可用交互提问工具请求用户选择；无工具则文字询问，已有明确指令或记录不重复问。独立对照允许同任务多个 participants，按各 Agent 子目录提交，首稿不互读；具体见 [模式指南](guides/modes.md)。

主流程：todo → in_progress → review → done；依赖缺失可进入 blocked，解除后回到实际阶段。
assignment 可用 proposed / accepted / observed；observed 表示从文件导入的历史产出。

done 必须注明交付物、实际验证和未验证项；不要求存在第二个 AI 才能结束独立文档任务。需要独立审查的实现先进入 review，由指定 reviewer 验收。文档完成不等于论文结论都已验证，更不等于驱动原型已实现。

## 5. 讨论与交接

每个任务使用 messages/<TASK-ID>/<agent-id>.md；每个文件只有该实例写入。同一实例串行操作，消息编号如 gpt-001，回复明确引用文件和编号。不要多人追加同一个“接龙日志”。

消息包含任务、作者、接收者、时间／时区、类型、状态、基线提交、编辑范围、事实／假设／提议、证据、问题和验收条件。接收确认必须由接收者自己写。

中断有剩余、责任移交、跨 Agent 接力或 task 不足以恢复的复杂检查点时，写自己的 handoffs/<TASK-ID>/<agent-id>.md；正常单人完成可只用 task 收尾，不为交付重复造交接。写清已完成、剩余、关键文件、验证和下一步；不替接收者回执。

这些文件是持久交接，不会自动通知或唤醒另一个应用。需要自动通信时另行接入实际 API／调度器；向外部应用发消息遵循用户授权。

## 6. 分工、分支与整合

- orchestrator 拆任务、定接口与验收；worker 完成限定范围；reviewer 验证；integrator 合并。
- 角色按任务确定，不能凭厂商名字宣称某个 Agent 永远更聪明或必须服从另一个。
- 小型文档任务可以在同一 checkout 按文件分工，所有 Git 暂存、提交和切分支由一个整合者串行执行。
- 真正并行开发使用独立 worktree + 分支 agent/<agent-id>/<task-id>，不在别人正在用的 checkout 切分支。
- worker 提交交付物、测试证据和基线；整合者 review 后 merge / cherry-pick，处理契约冲突和总体验收。
- 不为尚未确认参与的 Agent 自动开工或假定它已接收任务。

## 7. Git 与身份

提交格式：[TASK-ID][agent-id] summary；提交正文可以附：

```text
Agent: gpt
Task: COLLAB001
Role: integrator
```

默认使用 Git，无仓库时由 integrator 初始化，交付前保存真实提交；已有仓库与提交身份保留。显式 git add 本任务文件，检查 staged diff，保留他人未提交改动。禁止无授权 reset --hard、clean -fd、force push 或丢弃未知冲突。

保留仓库现有 user.name / user.email，不在共享 Git 配置里反复切换不同 Agent 身份。如确需显示不同 author，使用单次 git -c 配置或已明确启用的 worktreeConfig，不能伪造他人的身份。

分支、Task 和 trailer 是可修改的来源标签，不能证明身份。密码学签名另有密钥管理与验证，本项目尚未配置。提交是可追溯版本记录，但并非绝对不可篡改。

## 修改与证据底线

- 不对未读过的共享文件做全量写入。局部修改先读相关范围；确需整文件重写时先读取当前全文，合并并保留别人内容。写入前核对文件是否又变化，发现变化先重新读取／协调。
- 不在未确认 scope 内开工，不编造引用、链接、执行结果、接收回执或其他 Agent 的观点。
- 新目录优先沿用既有结构；需要新目录时说明用途、所有者与是否临时，不按 notes／tmp 等名称一刀切禁止正常实验。

## 使用反馈（可选）

在当前用户授权工程中，允许自主新增 feedback/<agent-id>/日期-主题.md；不用为单条意见先建任务或等批准，也不要求每轮读取全量反馈。本人文件单独写，评审回复也写自己的文件；意见不自动修改规则、不暂停无关任务。一句话反馈可写本人 task／handoff 的“模板备注”，值得跟进再立文件；最小格式、评审和回传母模板方法按需看 [反馈说明](feedback/README.md)。

## 8. 文档与实验

正式代码进入统一源码目录；task 保持稳定路径，索引列活跃与近期完成。CURRENT 只留活跃入口和最近 3 项完成摘要，每项最多 10 行，旧内容保留到 docs/history/CURRENT-YYYY-MM.md；登记只保留 2–3 条代表证据，不追加任务流水。生命周期与精简路径见 [记录指南](guides/records.md)。
调研区分事实、推断、提议、未验证，并给重要事实的一手来源。有长期价值的决定写 docs/decisions。
scratch 仅存可复核的实验记录、草稿和中间文件；不保存内部思考链。临时文件和本地锁忽略，正式任务／交接进入 Git。
