# RELAY001 跨客户端共享消息与人工交接

- status: done
- assignment: accepted
- collaboration_mode: serial
- mode_source: 用户明确选择共享消息与交接，提醒后手动启动接手方
- mode_question_status: answered
- participants: gpt-relay（本会话；独立实例 ID）
- run_id: 无
- output_root: tools/ 与 docs/collaboration/
- owner: gpt-relay
- integrator: gpt-relay（仅本任务；未接管其他任务）
- reviewers: 单 Agent 自检；四客户端实测待实际启动
- parent: 无
- dependencies: COLLAB001
- created: 2026-10-01
- updated: 2026-10-01
- base_commit: dc970302bdc59d951f608c906bc36649c77bc6c9

## Objective

交付通用通信提示词、本地通知队列和人工接手界面，解释额度检测与全自动调度所需的真实接口。

## Mode Decision

用户已选择人工启动接手方；本次不启动其他 Agent，不实现自动额度查询或轮换。

## Scope

仅 tools/agent_relay.py、tools/start_agent_relay.cmd、tests/test_agent_relay.py、docs/collaboration/agent-relay.md、docs/collaboration/agent-relay-prompt.md、.gitignore 的队列忽略条目、本任务／gpt-relay 消息与交接；CURRENT 追加本任务结果，保留其他会话记录。

## Deliverables

标准库 send/inbox/ack/serve；SQLite 持久队列；本地浏览器未读提醒、提示词复制；通用提示词、人工接手操作说明与自动调度边界。

## Completed

实现完成。只读正式 task 与 handoff，不改变 owner，不调用模型 API。通知队列被 Git 忽略。浏览器空收件箱打开正常，显示未读 0 条、刷新时间与暂无消息。未实际发送外部任务消息。

## Remaining

本范围交付完成。四客户端真实命令收发、提示音／剪贴板、EXE 分发、额度查询和唤醒适配器未验证／未实现。

## Problems

本机无 tkinter／PyInstaller，采用本地浏览器和双击 CMD；未安装依赖或构建 EXE。初次沙箱测试因临时 .agents 目录保留权限失败，提升后完整测试通过。

执行期间发现另一个会话占用 COLLAB003 并维护模式规则；本任务改用 RELAY001 和 gpt-relay，保留对方 task／handoff。登记申请见自己的消息文件，不代写他人的登记或伪造回执。没有进行 Git 暂存或提交。

## Verification

python -m unittest discover -s tests -v：29 项通过，含新工具 8 项与现有 21 项。覆盖 40 条并发投递不丢失、跨进程收发、已读幂等与收件人检查、交接前置文件、无效标识／正文拒绝、HTTP 会话令牌。主目录空 inbox 返回 [] 且不创建运行队列。真实浏览器空收件箱确认无读取错误。git diff --check 通过（其他会话模板清单有换行提示）。

## Handoff

.agents/handoffs/RELAY001/gpt-relay.md；未派发／唤醒其他应用。
