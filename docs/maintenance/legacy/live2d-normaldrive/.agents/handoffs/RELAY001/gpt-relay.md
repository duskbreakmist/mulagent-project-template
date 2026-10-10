# RELAY001 gpt-relay 交接

- 作者: gpt-relay / 本 Codex 会话
- 日期: 2026-10-01（Asia/Shanghai）
- 基线: dc970302bdc59d951f608c906bc36649c77bc6c9
- 实际工作树: 主目录 H:/Project/live2d_normalDrive
- 状态: 本范围文件交付；结束本轮后停止编辑；没有派发外部任务

## 已完成

标准库本地消息队列、CLI、浏览器收件箱与双击 CMD，通用提示词和操作说明。消息通知不改变正式 task，ack 只标记已读。数据库是 Git 忽略的本机运行数据；不调用模型。

## 验证

29 项 unittest 通过，包含新工具 8 项。真实浏览器确认空收件箱正常。没有在主工程写测试消息或运行队列。首次测试受沙箱临时 .agents 权限限制，提升后通过。

## 修改文件

tools/agent_relay.py、tools/start_agent_relay.cmd、tests/test_agent_relay.py、docs/collaboration/agent-relay.md、docs/collaboration/agent-relay-prompt.md、.gitignore 三行队列忽略规则、RELAY001 task／本实例消息／交接、CURRENT 追加本任务摘要。

## 剩余与未验证

人工在四客户端配置提示词并验证 python 文件访问；声音、剪贴板与 EXE 分发未验收。自动额度检测／客户端唤醒不在本次选择范围，官方接入事实和未验证边界见操作说明。彻底断额可能无法再生成交接，使用最后检查点和 Git 状态核对。

## 下一步

双击 tools/start_agent_relay.cmd 打开收件箱；按实际任务替换提示词占位符。若未来实现自动轮换，先验证四客户端的额度来源和启动接口，不把 MCP 工具支持等同于唤醒支持。

## 并发边界

另一个会话在同目录维护 COLLAB003，相关改动不属于本任务，不覆盖／暂存／提交它的文件。本实例 gpt-relay 登记请求尚未确认，自己的消息文件已有申请。
