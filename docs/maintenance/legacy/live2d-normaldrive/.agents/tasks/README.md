# 共享任务板

一个正式任务一个 <TASK-ID>.md。单人串行用 [TEMPLATE-lite.md](TEMPLATE-lite.md)，多人／依赖较复杂／独立对照用 [TEMPLATE.md](TEMPLATE.md)，字段只在需要时补充。task 是状态事实源，索引不复述正文。

## 活跃任务

| ID／文件 | 标题 | status | owner | updated |
| --- | --- | --- | --- | --- |
| [R000](R000.md) | R000 综合研究并决定最小表情控制原型 | todo | gpt（候选，尚未启动） | 2026-10-01 |
| [R002](R002.md) | R002 WorkBuddy：具身表达虚拟总线报告待审 | review | wb | 2026-09-30 |

integrator 维护 todo / in_progress / blocked / review 项，新会话只读索引和相关 task，不遍历全目录。

## 最近完成

| ID／文件 | 标题 | status | owner | updated |
| --- | --- | --- | --- | --- |
| [COLLAB007](COLLAB007.md) | GitHub 发布与模板安装更新 | done | gpt | 2026-10-10 |
| [COLLAB006](COLLAB006.md) | COLLAB006 根据 WB 实用性评审改进母模板 | done | gpt | 2026-10-10 |
| [ND006](ND006.md) | ND006 动作幅度与直接动作入口 | done | codex-normal-1 | 2026-10-06 |
| [ND005](ND005.md) | ND005 奏多GPU流式与情绪／身体驱动 | done | codex-normal-1 | 2026-10-05 |
| [ND004](ND004.md) | ND004 GPU闭环性能与流式验证 | done | codex-normal-1 | 2026-10-04 |
| [ND003](ND003.md) | ND003 开始回应自动启用声音 | done | codex-normal-1 | 2026-10-04 |
| [ND002](ND002.md) | ND002 独立连续语音行为驱动软件 | done | codex-normal-1 | 2026-10-04 |
| [COLLAB005](COLLAB005.md) | COLLAB005 添加轻量模板反馈记录 | done | gpt | 2026-10-01 |
| [COLLAB004](COLLAB004.md) | COLLAB004 审查并落实 WorkBuddy 协作建议 | done | gpt | 2026-10-01 |
| [COLLAB003](COLLAB003.md) | COLLAB003 增加同任务独立对照与模式选择 | done | gpt | 2026-10-01 |

仅索引已保存到 Git 的任务和本轮 COLLAB007；ND001／RELAY001 工作区记录尚未提交。只留最近 10 项；完成正文仍留 tasks/<ID>.md，其他历史通过任务文件与 Git 查询，不按版本周期自动移动／删除。

## 创建与收尾

未实际接受的分配保持 assignment: proposed；正常单人完成更新 task、这一行索引和 CURRENT 短摘要，不额外写登记流水或独立 handoff。中断有剩余／移交时才写交接。

version_tag 仅记录实际标签，无标签填“无”；本字段不要求每任务打标签。模式读取明确用户／父任务／已授权工程默认，仍 unset 才提问，见 [模式指南](../guides/modes.md)。

临时提议编号、生命周期和特殊归档见 [记录指南](../guides/records.md)。README、TEMPLATE 与 TEMPLATE-lite 不是实际任务。
