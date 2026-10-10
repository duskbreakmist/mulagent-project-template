# COLLAB006 根据 WB 实用性评审改进母模板

- status: done
- assignment: accepted
- collaboration_mode: serial
- mode_source: 用户授权本会话判断合理性后修改模板，并明确加强 Git 管理
- owner: gpt
- created: 2026-10-10
- updated: 2026-10-10
- base_commit: 40aec539f353b17c65920b892d35c4253db36d1a
- version_tag: 无

## Objective

落实有证据的记录降本、生命周期、默认模式与检查器改进；保留授权、防覆盖和验证边界，Git 管理成为默认交付要求。

## Scope

gpt/project_templateA、相关模板测试与本工程对应规则／反馈／任务／CURRENT／历史记录。外部 live2d_drive 评审仅只读，不搬移其 44 个任务或历史；其他会话的 README、ADR-002、ND／relay 未提交内容保持独立。

## Completed

落实精简 task、记录生命周期、活跃／最近完成索引、有效工程默认来源、稳定 ID／临时提议 alias、version_tag 与低摩擦备注。默认 Git 管理写进入口、协议和手册。v2 增加只读本地链接与任务状态检查，兼容 v1；母模板 29 文件、入口 14 行。

[逐项裁决](../feedback/gpt/2026-10-10-wb-template-review.md)说明采纳与调整，外部工程数据未当作本轮实测。

## Verification

18 项模板测试和 11 项旧初始化器测试通过，TEMPLATE_OK files=29；编码／本地链接／staged diff 检查通过。原研究正文未改，外部评审保持原样。外部评审 SHA256：67e37e6ead6add35c2d54305618b363ad8f9a3f00789471a7567ba2751794fce；来源为 H:/Project/live2d_drive/docs/wb/research/2026-10-10-agent-template-review.md。

## Remaining

交付范围内无剩余。未模拟真实多 Agent 冲突、各客户端加载或测量 token 节约；外部工程历史迁移为独立后续工作。正常单人完成由本 task 收尾，不另造交接。
