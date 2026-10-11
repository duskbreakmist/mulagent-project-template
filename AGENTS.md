# Agent 工作入口

- 默认中文；文档按[写作规范](.agents/guides/documentation.md)；修改前读相关实现，关键设计／边界写简洁中文注释，完成后检查并如实记未验证项。
- 用户当前授权优先；保留已有产出，不记录内部思考链。
- 新会话先读 [.agents/PROTOCOL.md](.agents/PROTOCOL.md)。同一会话规则未变时不必反复全文读取。
- 确认主协作目录。明确维护母模板，或 origin 指向 duskbreakmist/mulagent-project-template 时，先读 docs/maintenance/README.md 与 docs/maintenance/CURRENT.md，实际维护任务写 docs/maintenance/tasks/；其他工程读取主目录的 [登记表](agents_list.md) 与 [.agents/tasks](.agents/tasks/README.md)。
- 模式按当前指令、明确父任务或已授权工程默认确定；仍未定才由 integrator 询问，已有来源不重复问，细节见 [模式指南](.agents/guides/modes.md)。
- 独立对照时各写 results/<TASK-ID>/<RUN-ID>/<agent-id>/，首稿提交前不读其他候选；任务状态与协作模式分开。
- 只修改已确认 scope；不全量覆盖未读过的共享文件；[共享整合者](.agents/coordination.md) 串行汇总，worker 写自己的消息／交接。
- 默认纳入 Git 管理：检查已有仓库／忽略项，无仓库由 integrator 初始化；交付前验证、显式暂存、审查并提交，见 [Git 指南](.agents/guides/git.md)。
- 并行代码开发使用独立 worktree；共享 checkout 的 Git 操作串行。中断有剩余／移交写交接，正常单人完成用 task 收尾。
- 单人串行用精简 task，更新索引与 [CURRENT](docs/CURRENT.md) 短摘要；登记不写任务流水，记录／归档按需看 [指南](.agents/guides/records.md)。
- 觉得模板繁琐或有改进点时，可自主写 [本人反馈](.agents/feedback/README.md)；无问题不必写，反馈不自动改规则。
- 首次配置／维护看 [template_readme.md](template_readme.md)，普通任务不要求读手册、脚本或全部模板。
- 母模板维护时，根登记／任务索引／CURRENT 是分发种子，保持空白；维护身份、scope、进度在 docs/maintenance/tasks/ 和 docs/maintenance/CURRENT.md 记录，普通登记／任务规则使用这些维护路径。业务工程按正常协议管理自身状态。
