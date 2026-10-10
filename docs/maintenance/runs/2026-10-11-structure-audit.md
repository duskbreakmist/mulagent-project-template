# 2026-10-11 结构定位审计轮次（多实例同源指令）

本文件是轮次（RUN）索引，不是维护任务，不占用 TPL 编号。由 wb-structure-20261011 提议汇总，**未经指定为共享 integrator**（.agents/coordination.md 的 shared_integrator 仍为 vacant），待用户或实际负责人确认后再并入正式结论。

## 公共输入

- 提示词（四实例同源）：`当前工程结构怎么样的？应该是个用来开发模板协议（不同agent协调工作的模板）的工程？你是否认可？你按照协议要求提建议`
- 起点 base_commit：0df7095（第一个实例开始时）
- 目标仓库：H:/Project/agent-project-template（母模板维护仓库）
- 结果：AI 各自输出，互不通气。

## 参与实例

| agent-id | 产出路径 | base_commit | 自报模式 | 盲态 | 落盘状态 |
| --- | --- | --- | --- | --- | --- |
| codex-structure-20261011 | docs/maintenance/tasks/TPL003.md | 0df7095 | serial | 未读任何其他候选（首个） | 已提交 01f66e7 |
| wb-structure-20261011 | docs/maintenance/tasks/TPL004.md | 01f66e7 | serial | 明确读了 TPL003 全文，自述为交叉复核 | 已提交 7387004 |
| zcode-structure-20261011 | docs/maintenance/tasks/TPL005.md | 7387004 | independent_compare | 读了 TPL003；自述未读 TPL004 正文，但见到其提交标题与 CURRENT 摘要 | **未提交**（文件为 untracked，声称将改 CURRENT 但工作树无该改动） |
| 第四实例 | 未落盘 | 未知 | 未知 | 未知 | 截至 2026-10-11 01:15 未见产出文件 |

## 结论收敛点（三实例一致，可采信）

1. 认可"多 Agent 协作协议母模板开发工程"定位；origin 指向 duskbreakmist/mulagent-project-template，docs/maintenance/README.md 声明唯一开发位置。
2. 分发骨架实测 32 项（manifest v2），根登记／任务索引／docs/CURRENT 仍为空骨架。
3. 安装器 SEEDS(5) 与 RUNTIME_DIRS(8) 不含 docs/maintenance、tests、.github，无法拦截维护文件误入清单。
4. 本地领先远端（ahead 2），本轮 CI 未运行；check_template 均通过 files=32。

## 各实例独有贡献（去重后的增量）

- TPL003：维护层检查与分发边界回归（建议 1）、多人维护入口、场景验收、入口文案、relay 与协议分离。
- TPL004：母仓库识别不应依赖 git remote（fork／改 remote 即失效）；legacy 内同名完整旧模板快照会导致检索命中两份 PROTOCOL.md、误改文件；共享 CURRENT 并发写入保护；.test-tmp 残留。
- TPL005：README 与 docs/template-usage 硬编码 `H:\Project\agent-project-template` 绝对路径，公开模板在其他机器／非 Windows 上直接失败；建议把本次三实例并发本身作为场景验收的首个真实样本。

## 为什么这次对照"打架"（合规性问题）

1. **没有 RUN 记录就自称 independent_compare。** 协议要求候选存 `results/<TASK-ID>/<RUN-ID>/<agent-id>/`，并由 RUN 模板固定公共输入与盲态。三个实例都写进了维护任务流水 `docs/maintenance/tasks/TPL00N.md`，把一次对照实验记成了三条维护任务。
2. **任务号由各实例自行抢占。** 四个实例都"兼任 task integrator"并自选下一个编号，而共享 integrator 从未指定（coordination.md 仍 vacant）。任务 ID 本应由 integrator 分配。
3. **盲态不一致。** TPL003 全盲、TPL004 半盲（读了 TPL003）、TPL005 半盲（读了 TPL003＋见到 TPL004 标题／摘要）。因此**这批产出不能当作公平横向评测结论使用**，只能作为互相印证的审计。
4. **共享 CURRENT 被多实例串行追加。** TPL005 记录了一次"瞬时 M 后消失"的幻影修改，说明并发写同一文件已实际发生，只是侥幸未覆盖。机制上无锁、无 worktree、无单一汇总者。
5. **同一 checkout 上并发提交。** 协议要求同 checkout 的 Git 操作串行，此处靠时间错开侥幸串行，不是机制保证。
6. **中断实例留下未提交文件。** TPL005.md 处于 untracked，其自述的 CURRENT 改动未出现，说明该实例可能被打断，需要收尾。

## 模板改进建议（本轮新增，未实施）

- **强制对照前置条件**：自称 independent_compare 前必须存在 RUN 记录（含 RUN-ID、公共输入、base_commit、产出目录、指定 reviewer）；否则降级为 serial 并注明盲态。
- **任务 ID 分配权收归 integrator**：模板明确"worker 不得自选任务编号"，未指定 integrator 时应先记录 vacant 并只写本人产物。
- **并发写共享文件的操作步骤写进 git 指南**：写入前复核 HEAD、只 add 自己文件、中断时写 handoff 而非留 untracked 文件。

## 待办

- 确认第四个实例是否还有产出；有则补入本表并注明其 base_commit 与盲态。
- 指定唯一汇总者（用户授权或按继任指南产生），再合并建议清单。
- 所有实例收尾后再一次性推送，避免把未提交内容推走或产生冲突。
