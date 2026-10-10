# 正式对照结果

独立对照使用 <TASK-ID>/<RUN-ID>/<agent-id>/ 保存每个参与者自己的候选，公共输入为该轮 input.md，比较结果为 comparison/review.md。范围由 task 固定；这里的例子不是实际任务。

- 每个 Agent 维护自己的 RUN.md 和交付物，其他作者不覆盖。
- 首稿提交前不读取其他候选内容；对照结束后按统一标准比较，保留原始结果。
- 正式输入、结果、状态记录与评审进入 Git，不能塞进被忽略的 scratch。
- 多轮使用不同 RUN-ID。真实模型／工具版本与输入差异明确记录，不能把条件不同的结果当严格公平评测。
- 实现代码通过独立 worktree／分支管理，这里记录引用与复现方法。

具体规则按需读 [.agents/guides/modes.md](../.agents/guides/modes.md)。
