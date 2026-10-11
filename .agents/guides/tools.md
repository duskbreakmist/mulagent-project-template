# 工具加载与可选通信

核查日期：2026-10-01。厂商文档是当前机制说明；本机是否真正加载仍需验证。表格按客户端区分，不将同厂商所有产品混为一个。

| 工具 | 核实的加载方式 | 配置／验证注意 |
| --- | --- | --- |
| Codex | 运行开始构建指令链，同目录先选 AGENTS.override.md，再 AGENTS.md；project_doc_max_bytes 默认合计 32 KiB | 默认值可配置，并非每文件固定硬上限。会话中改规则要显式重读。见 [OpenAI 官方说明](https://learn.chatgpt.com/docs/agent-configuration/agents-md) |
| Claude Code | 新版本在项目没有 CLAUDE.md／CLAUDE.local.md 时可直接读 AGENTS；版本、内置插件和设置影响行为 | 直接支持要求 v2.1.277+，部分会话仍有条件。已有 CLAUDE 或旧版可用 @AGENTS.md 导入，不应一律要求新建兼容文件。见 [官方说明](https://code.claude.com/docs/en/memory) |
| GitHub Copilot CLI | 发现 AGENTS.md、CLAUDE.md、GEMINI.md 等并组合，无一般文件优先级 | 用 /instructions 查看启用来源；避免互相矛盾。不能把 CLI 规则泛化到所有 IDE／云端形态。见 [GitHub 官方说明](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions) |
| Gemini CLI | 默认 GEMINI.md，可通过 context.fileName 改为一个或多个名称 | /memory show 查看、/memory reload 刷新；合并已有 settings，不直接覆盖。见 [官方说明](https://geminicli.com/docs/cli/gemini-md/) |
| WorkBuddy | 模板作者所在工程的 WB 自报本机根 AGENTS 被项目指引自动注入 | 仅是该工程参与者自报，目标工程重新验证；未给出版本，不能保证所有环境如此 |

Claude 兼容方案（只有需要时添加／合并 CLAUDE.md，不复制一份完整规则）：

```text
@AGENTS.md
```

Gemini 配置示例（合并到现有 settings.json，实际文件位置与配置作用域按客户端确认）：

```json
{"context": {"fileName": ["AGENTS.md", "GEMINI.md"]}}
```

普通 Markdown 链接只是导航，不等于客户端加载或 @ 导入。让工具报告实际加载来源，核对关键规则，再开始正式修改。维护时更新核查日期与证据，不把此表当永远不变的事实。

## 可选通信能力

- 仓库 messages／handoffs 是正式记录，读写不等于通知／接受任务。
- 如另接本地队列或浏览器人工提醒，需独立交付并验收客户端收发。模板不包含消息服务／数据库，不能视为自动安装。
- agent-mail：WB 报告其环境有这种智能体邮箱并声称可跨机器／发送真实邮件。模板未确认具体服务、接口、收件地址、身份和可用性；登记为“可选、待验证”，不当作已接入。
- 邮件／远程消息可能承载通知或交付物链接，但不能自动同步任务、停止旧执行者或唤醒另一应用。实际接入要验证来源、回执、失败路径及与公共记录的关系。
- 向真实收件人发送邮件／外部消息仍须用户授权；读取 WB 的建议不构成发送授权。本轮未发外部通知。
