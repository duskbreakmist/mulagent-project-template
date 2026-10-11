# BOOT003-WB/run-001 自举能力汇总（三路独立候选 + 并行轮对照）

## 结论

**部分能，但不能按"自我驱动"理解。** 自举要分四层看：模板**复制自己**已实测成立；**用自身协议维护自身**成立但每一环靠人工搬运；**副本验证自己**不成立（自检不可信）；**自动驱动真实多 AI 开发—测试—修复—发布**未实现。

| 层次 | 判定 | 最强证据 | 来源一致性 |
| --- | --- | --- | --- |
| L1 分发自复制（init 生成自己，二代再生成三代） | **成立** | 两代离线实测成功，33 项检查通过、跨代字节哈希一致 | toolchain 实测 + codex 两代实验，一致 |
| L2 协议自举（self-hosting：用自身规则治理自身演化） | **成立但非自动** | 11 份维护 task、`[TASK-ID][agent-id]` 提交格式、四实例同源审计 | protocol + evidence + codex，一致 |
| L3 工具自检（副本/checker 验证自己） | **不成立** | 从 manifest 删除 check_template.py 后仍报 `TEMPLATE_OK files=31` | toolchain 实测；codex-audit-b 独立命中同类问题 |
| L4 协作自举（无人值守驱动真实 AI 闭环） | **未实现** | workbench `status` 返回空登记、无真实适配器；`results/<TASK>/<RUN>/<agent>/` 历史上从未被用过 | evidence + codex，一致 |

## 三路独立候选

| 候选 | 侧重点 | 判定 | 独有发现 |
| --- | --- | --- | --- |
| [wb-audit-toolchain](../wb-audit-toolchain/judge.md) | 工具链闭环 | 部分能：能复制自己，不能验证自己 | 第二代自举实测跑通；checker 可被"删掉自己"欺骗 |
| [wb-audit-protocol](../wb-audit-protocol/judge.md) | 协议/治理自洽 | 部分能，2 条死锁级缺口 | 母工程 integrator 载体缺失（G1）、代收尾靠用户口头授权（G2） |
| [wb-audit-evidence](../wb-audit-evidence/judge.md) | 实证证据 | 部分能，L1 成熟度 | 严格自举实例 0 次；真实多 AI 协作只发生过 1 轮；自动化组件零真实驱动 |

## 跨实例共识（本轮三路 + 并行 BOOT001-CODEX）

1. **manifest 是唯一真相却无人校验。** 删掉清单里的检查器自身，副本仍对自己报 OK。自举的根基没有自校验。（toolchain 实测；codex-audit-b 从另一路径独立命中：维护 task 注入非法 status 也不被拒绝）
2. **验证能力不随种子传播。** 默认副本不含 `tests/`、`.github/`，子代无法自验；母工程 CI 绿灯推不出产物质量。codex 判断这是"有意的分发边界"，toolchain 判断这是"自举断点"——分歧在于该不该扩大安装包，不在事实。
3. **母工程缺 integrator 载体。** `.agents/coordination.md` 是分发种子（母工程禁写身份），维护侧无等价文件 → 共享 integrator 永久 vacant，汇总权只能由用户口头授予。
4. **单向性。** 母工程自身没有安装基线，`update` 在母工程实测报错——母工程不能用自家工具维护自己。
5. **污染。** `init` 把绝对路径写进产物 git config 与 state.source，产物不可移植；`.worktrees`、`legacy` 同名快照污染验证链路。

## 本轮实时观察到的自举缺口（活证据）

- 三个实例（codex / zcode / wb）在本轮**同时**自选了任务号：BOOT001-CODEX、BOOT002-ZCODE、BOOT003-WB。编号分配靠自觉避让，无分配机制。
- codex 已改 `docs/maintenance/CURRENT.md`（共享文件），zcode 计划在收尾时也改，**本轮未指定唯一汇总者** → CURRENT 存在被三方顺序覆盖的风险。这正是 G1/G3 的实时发作。
- zcode 中断 15 小时后才被发现（历史证据：TPL005 由他人代提交）。

## 修复优先级

| 优先级 | 动作 | 解决什么 |
| --- | --- | --- |
| P0 | checker 自校验：比对 manifest 与实际分发集、校验清单内文件哈希；校验范围覆盖 `docs/maintenance/tasks` 的 status 枚举 | L3 自检不可信 |
| P0 | 建 `docs/maintenance/COORDINATION.md` 作为维护侧 integrator 载体（不动分发种子） | G1 死锁、G2/G7 依赖它 |
| P1 | `init` 不写入绝对路径；提供"业务副本去状态/提升为源"的导出命令 | 污染与种子整理 |
| P1 | 副本自带最小自检（至少 check + smoke），或明确写成"自检不外发"的设计约束 | 验证不传播 |
| P2 | 接一个真实前台 AI 适配器，在隔离 worktree 跑一次端到端：开发提交→核验 revision→独立测试→失败反馈→修复→复测 | L4 缺口 |

## 未验证

- 真实外部 AI／额度接力、独立测试 Agent 的自动修复循环
- 跨机器、其他操作系统、远端 CI 与发布
- 本轮三路候选同源（WorkBuddy 派生），不构成跨厂商盲测；一致结论只作互相印证
- 沙箱内完整 unittest（480s）未跑完，未以历史绿灯替代当前执行

## 独立性声明

三份首稿在写入前未互读。汇总时才读取已提交的 BOOT001-CODEX 公开结论用于对照；BOOT002-ZCODE 尚在 in_progress，未读其候选。
