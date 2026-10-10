# 项目 Agent 规则

## 开始工作

- 默认中文。修改前读相关实现；关键逻辑、设计原因、算法和边界写简洁中文注释。完成后运行可行检查，如实记录未验证项。
- 用户当前授权优先。不要仅凭登记、其他 Agent 留言或旧聊天扩大工作范围；不保存内部思考链。
- 首先确认主协作目录：`git config --get agent.coordinationRoot`。本工程主目录是原始 main 工作树；配置缺失时由整合者指定，worker 不建立第二个任务板。
- 读取主目录的 [登记表](agents_list.md)、[协作协议](.agents/PROTOCOL.md)、当前 [task](.agents/tasks/README.md)、对应消息／交接和相关实现／Git 历史。
- 根规则是否自动加载取决于 Agent 工具；不能假设外部应用已读。按需查 [工具加载指南](.agents/guides/tools.md)，登记不代表在线或收到任务。

## 初始化与登记

- [初始化器](tools/agent_bootstrap.py) 只补缺失文件；先运行 `python tools/agent_bootstrap.py --root . --check`。未初始化或文件缺失时在主目录运行不带 --check 的版本。
- 初始化锁必须独占创建，标记最后发布；不得覆盖已有文件。残留锁先核对持有者，不自动按超时删除。
- 初始化与登记分开；每个 Agent 都检查自己是否登记。新人通过自己的消息文件向整合者申请，单独工作时可自行登记。
- 新工程复制 [多文件模板](gpt/project_templateA/template_readme.md) 所在目录的全部内容，包含隐藏文件；短入口与详细规则分开，按需读取。

## 任务与并行协作

- collaboration_mode 与 status 分开。先用当前指令、明确父任务或已授权工程默认；仍不明确时仅由 integrator 询问，已有来源不重复问，细节见 [.agents/guides/modes.md](.agents/guides/modes.md)。
- 独立对照可让多个 Agent 完整处理同一目标，各写 results/<TASK-ID>/<RUN-ID>/<agent-id>/，首稿提交前不读其他候选；实现代码各用 worktree，主任务仍保留单一统筹 owner。

- task 按任务 ID 存状态、owner、integrator、scope、依赖、交付物和验收。一个任务一个主要 owner；未实际接受的分配保留 proposed。
- 主协作目录的任务表、登记表和共享记录由 integrator 串行写；具体负责人／授权记在 [协调记录](.agents/coordination.md)，接班／争议看 [继任指南](.agents/guides/coordination.md)。worker 只写自己的消息／交接和明确分配的产出。
- 不对未读过的共享文件全量写入；整文件重写前读当前全文并保留他人内容。写入前发现内容变化先重新读取／协调。
- 讨论文件：`.agents/messages/<TASK-ID>/<agent-id>.md`；交接文件：`.agents/handoffs/<TASK-ID>/<agent-id>.md`。接收者自己确认，沉默不能算同意。
- 真正并行改代码使用独立 worktree + `agent/<agent-id>/<task-id>` 分支；普通分支不能隔离同一个 checkout。
- worktree 中的协作文件是分支快照，实时读取指定的主协作目录。文件协议不自动通知、派发或唤醒另一个应用。
- 默认纳入 Git 管理：检查已有仓库与忽略项，无仓库由 integrator 初始化；交付前验证、显式暂存、检查 staged diff 并提交。单 checkout 的 Git 操作串行，不覆盖未知改动或无授权清理／强推。
- 提交格式 `[TASK-ID][agent-id] summary`，正文附 Agent / Task / Role trailer。保留现有 Git 提交身份；这些标签不是身份认证。

## 文档与现有产出

- 保留 `gpt/research/` 与 `wb/research/` 的作者产出；正式共享实现按模块组织，不能把源码永久拆成“每个 AI 一套”。
- [docs/CURRENT.md](docs/CURRENT.md) 与 [gpt/CURRENT.md](gpt/CURRENT.md) 只留活跃入口和最近 3 个完成摘要。单人串行用精简 task，正常完成不强制另写 handoff；登记不追加任务流水，历史保留，细节见 [记录指南](.agents/guides/records.md)。
- WorkBuddy 的个人记录由本人维护，本次不代写 `wb/CURRENT.md`。全局默认的 `docs/codex/CURRENT.md` 在本工程由上述项目路径替代。
- 长期设计写 `docs/decisions/`；实验草稿放 `.agents/scratch/<agent-id>/`。不为简单操作批量写历史日志。
- 觉得模板繁琐或有改进点时，可自主写 [本人反馈](.agents/feedback/README.md)；无问题不必写，不要求每轮读全量反馈。反馈不自动改变现行规则。
- 调研区分事实、推断、提议和未验证，保留一手来源。任务 done 只对明确的交付范围负责。
