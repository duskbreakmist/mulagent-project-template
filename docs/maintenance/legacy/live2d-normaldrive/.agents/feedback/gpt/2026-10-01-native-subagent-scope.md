# 原生临时子 Agent 不宜重复执行全部工程登记流程

- author: gpt
- date: 2026-10-01
- tool_model: 本 Codex 会话
- template_baseline: 8a5622c
- status: proposed（仅反馈，本轮未修改模板规则）

## 问题与核查

用户询问同一个 Codex 的多个 Agent 是否仍需工程协调。现行协议要求同类并发实例不同 ID，却未明确区分独立会话与主 Agent 派生的临时子 Agent；可能让短期审查／调查重复登记、建任务、写交接。这里是规则歧义评估，未测量具体时间或 token 成本。

[OpenAI Docs 子 Agent 说明](https://learn.chatgpt.com/docs/agent-configuration/subagents)确认 Codex 负责创建、后续指令路由、等待与汇总，并提醒并行写入存在冲突；[worktree 说明](https://learn.chatgpt.com/docs/environments/git-worktrees)支持独立会话在不同工作树运行。原生调度不等于共享文件互斥。

## 建议

- 同一主会话派生的临时子 Agent 使用运行时 ID／父子标识，由主 Agent 在当前 task 汇总范围、产出与验证；不要求每个子 Agent 都在工程登记表注册、再建立一套独立 task／CURRENT。
- 内部派发、消息与等待优先用原生能力；子 Agent 仍读适用规则与相关实现，遵守具体可写范围。共享任务表、登记与 Git 操作由主 Agent 串行汇总，不能复用主 Agent 文件名并发写入。
- 人工打开的多个 Codex 会话仍是独立参与者，即使同工程、同模型也一样：以 gpt-1／gpt-2 等稳定会话 ID 区分，消息／反馈文件各自命名，明确 scope；并行修改代码使用实际隔离工作树。独立对照仍保存各候选和基线，不能省略必要的结果记录。
- 有跨会话接手、长期任务或需要复现的产出时才增加持久交接；不要假定子 Agent 已自动有独立 worktree，先核对实际环境。

## 跟进

本轮仅记录反馈与官方核查，不创建／派发子 Agent，不修改客户端配置。实际规则修改另按用户任务范围落实；没有回应不算采纳。
