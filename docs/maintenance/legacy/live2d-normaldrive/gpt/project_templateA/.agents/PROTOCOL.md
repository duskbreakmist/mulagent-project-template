# 协作核心规则

## 每轮工作

1. 确认唯一主协作目录；多 worktree 从 git config --get agent.coordinationRoot 读取。不可达时先做独占草稿／只读调查，不建立第二个任务板。
2. 读登记、任务索引、当前 task 和它引用的消息／交接，再读相关实现与 Git 历史；无需遍历全部任务与可选机制。
3. 单人串行用 [精简模板](tasks/TEMPLATE-lite.md)，owner 兼任 task integrator；多人／对照用完整模板，明确唯一 owner、scope、依赖和验收。
4. 模式依据当前用户指令、明确父任务或**已授权工程默认**确定；仍不明确时只由 integrator 询问。具体见 [模式指南](guides/modes.md)。
5. 未实际接受的委派保持 proposed，本人确认且依赖满足后才进入 accepted / in_progress。正常单人完成用 task 收尾；中断有剩余／责任转移／跨 Agent 接力才需独立 handoff。

## 所有权与状态

- 项目共享负责人、授权与工程默认记在 [coordination.md](coordination.md)；同一共享文件一次一个实际写者，任务 integrator 可以不同，写入范围要明确。
- integrator 串行汇总 task、索引和 CURRENT；worker 写本人消息／交接及已分配产出。身份／能力变化才更新登记，授权／职责变化才更新协调，不每任务重复写五处。
- 消息与交接统一 <TASK-ID>/<agent-id>.md，署名使用登记 ID；独立会话不同 ID，短期内部子任务由主 owner 汇总。临时提议编号见 [记录指南](guides/records.md)。
- status: todo / in_progress / blocked / review / done；assignment: proposed / accepted / observed。observed 仅说明导入产出，done 需按交付范围和实际验证验收。
- 需要独立审查的实现先进入 review；不要求普通单人任务制造第二位 reviewer。角色按任务约定，不凭厂商固定上下级。
- 沉默不是同意，登记不代表在线，文件不自动通知／派发。继任与争议按需读 [继任指南](guides/coordination.md)。

## 记录生命周期与反馈

CURRENT 保留活跃／阻塞入口与最近 3 个完成摘要，每个不超过 10 行；更早完成摘要保留到 docs/history/CURRENT-YYYY-MM.md。登记只留 2–3 条代表性证据，不追加任务流水；任务文件默认保留稳定路径。精简、索引和归档细节见 [记录指南](guides/records.md)。

一句话反馈可写本人 task／handoff 的“模板备注”，值得跟进再立本人 feedback 文件；无问题不写、不每轮全读、不为意见造新任务。意见与采纳不自动改规则，回传母模板按需看 [反馈说明](feedback/README.md)。

## 实施与 Git

- 默认使用 Git：先检查已有仓库与忽略项，无仓库由 integrator 初始化；交付前验证、显式暂存本任务文件、审查 staged diff 并提交。不能把“复制模板”当作已经完成 Git 初始化。具体见 [Git 指南](guides/git.md)。
- 保留现有提交身份、他人未提交内容；禁止无授权破坏性 reset、clean、强推或丢弃冲突。同 checkout 的 Git 操作串行，真实并行改代码使用隔离 worktree。
- 不全量覆盖未读共享文件；整写前读当前全文，写前核对变化并保留他人内容。只改已确认 scope，不编造引用、命令结果、接收回执或他人观点。
- 独立对照候选保存在 results/<TASK-ID>/<RUN-ID>/<agent-id>/，首稿不互读；详细约束只在该模式读取。代码按模块组织，草稿放 scratch；调研区分事实、推断、提议、未验证。
- 用户当前授权优先；分支／提交标签不认证身份，检查器不提供互斥锁或验证研究结论。
