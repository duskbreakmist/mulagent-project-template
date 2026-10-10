# 当前共享工作记录

## 活跃与待办

- [R000](../.agents/tasks/R000.md)：todo，模式待明确，未启动。
- [R002](../.agents/tasks/R002.md)：review，保留报告待验收。
- 其他实例的 ND001／RELAY001 工作区内容仍独立未提交，不代验收。

## 最近完成

### 2026-10-10 COLLAB007 发布与安装更新

- [任务](../.agents/tasks/COLLAB007.md)：独立 [GitHub 模板仓库](https://github.com/duskbreakmist/mulagent-project-template) 已发布并启用 Template repository，版本 v0.1.1。
- [安装更新说明](../gpt/project_templateA/docs/template-usage.md)：32 项骨架，init／adopt／update／apply；独立工程 Git、状态保护、三方合并及冲突备份。
- 独立发布目录 37 项测试与 [GitHub CI](https://github.com/duskbreakmist/mulagent-project-template/actions/runs/38040232118) 成功；公开远端实际安装及 v0.1.0 → v0.1.1 升级、无模板 origin、定制登记保留与重复更新通过；三方合并兼容修正回归通过。
- 母仓库路径 H:/Project/agent-project-template；此工程 gpt/project_templateA 是同步镜像。其他作者 README／ADR／ND／relay 未提交内容保持原样。
- 曾有审批额度与 Windows ACL 故障，恢复后完成，未绕过审批。正常单人收尾不另造交接。

### 2026-10-10 COLLAB006 记录减负

- [任务](../.agents/tasks/COLLAB006.md)：lite、生命周期、索引、有效默认模式、默认 Git；29 项相关测试通过。

### 2026-10-01 COLLAB005 反馈

- [任务](../.agents/tasks/COLLAB005.md)：可选反馈与低摩擦建议通道。

## 历史

旧摘要保留在 [历史](history/CURRENT-2026-10.md)，详细事实与验证按 task 查询，不复制全文。

## RELAY001：共享消息与人工接手（2026-10-01）

[任务记录](../.agents/tasks/RELAY001.md)，实例 gpt-relay；本段追加保留另一个会话的 COLLAB003 记录。用户已选择先共享消息／交接，提醒后人工启动接手方。

分析与方案：原文件协议缺少实际通知。新增 SQLite 本地队列和标准库浏览器收件箱，正式 task／handoff 继续按原协议维护；ack 只标记已读。额度耗尽时可能无法再生成交接，提示词要求定期检查点；自动检测额度与唤醒需真实客户端接口，MCP 本身不能保证唤醒。

变更：[使用说明](collaboration/agent-relay.md)、[通用提示词](collaboration/agent-relay-prompt.md)、tools/agent_relay.py、tools/start_agent_relay.cmd、tests/test_agent_relay.py、.gitignore 运行队列忽略条目、RELAY001 task／gpt-relay 消息与交接。其他会话的规则／模板改动没有覆盖或暂存。

验证：29 项 unittest 通过（新工具 8 项、现有 21 项），含 40 条并发投递与跨进程读取、交接前置检查、已读幂等和 HTTP 会话令牌。浏览器空收件箱实际打开正常；空 inbox 不创建数据库。首次沙箱测试因临时 .agents 权限失败，提升后通过。Git diff --check 通过。

待办／未验证：四客户端实际命令收发、提示音／剪贴板、EXE 分发未验收。本机无 PyInstaller，交付双击 CMD 与 Python 源码；未安装依赖。没有实现自动余额查询或自动轮换，没有实际外部派发，没有进行 Git 提交。独立实例登记申请保存在 .agents/messages/RELAY001/gpt-relay.md，待登记表 integrator 确认。
