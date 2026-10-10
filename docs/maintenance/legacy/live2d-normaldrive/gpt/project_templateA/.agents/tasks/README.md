# 共享任务板

一个正式任务一个 <TASK-ID>.md。单人串行用 [TEMPLATE-lite.md](TEMPLATE-lite.md)，多人／依赖较复杂／独立对照用 [TEMPLATE.md](TEMPLATE.md)，字段只在需要时补充。task 是状态事实源，索引不复述正文。

## 活跃任务

| ID／文件 | 标题 | status | owner | updated |
| --- | --- | --- | --- | --- |

初始无任务。integrator 维护 todo / in_progress / blocked / review 项，新会话只读索引和相关 task，不遍历全目录。

## 最近完成

| ID／文件 | 标题 | status | owner | updated |
| --- | --- | --- | --- | --- |

只留最近 10 项；完成正文仍留 tasks/<ID>.md，其他历史通过任务文件与 Git 查询，不按版本周期自动移动／删除。

## 创建与收尾

未实际接受的分配保持 assignment: proposed；正常单人完成更新 task、这一行索引和 CURRENT 短摘要，不额外写登记流水或独立 handoff。中断有剩余／移交时才写交接。

version_tag 仅记录实际标签，无标签填“无”；本字段不要求每任务打标签。模式读取明确用户／父任务／已授权工程默认，仍 unset 才提问，见 [模式指南](../guides/modes.md)。

临时提议编号、生命周期和特殊归档见 [记录指南](../guides/records.md)。README、TEMPLATE 与 TEMPLATE-lite 不是实际任务。
