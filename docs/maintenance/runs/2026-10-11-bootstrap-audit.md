# 2026-10-11 自举审计统一整合

当前项目支持外部 AI 与人工授权参与的自身维护，也支持协议骨架跨代复制。默认分发副本有有限完整性检查，尚未携带完整开发测试体系；真实多 AI 自动开发、测试、修复闭环尚未验收。

## 整合授权与接收范围

- integrator: codex-bootstrap-integrator-20261011
- selection_source: 用户本轮明确指定“你现在负责整合”
- state: 本轮整合完成；不表示后台持续运行或永久工程默认
- task: [BOOT004-INTEGRATE](../tasks/BOOT004-INTEGRATE.md)
- coordination_root: 本仓库，Git 本地配置已核对
- shared_write_scope: 本轮 RUN、相关接收／任务记录、维护 CURRENT／必要摘要历史与对应 Git 提交
- implementation_scope: 无；本轮不把审计建议自动落实为生产修改

根协调、登记、任务索引和业务 CURRENT 继续保持分发种子；本轮实际授权与接收事实保存在维护侧。记录不是互斥锁，也不意味着其他客户端收到通知。

| 来源 | 作者自报／可见交付 | 接收处理 | 独立性与限制 |
| --- | --- | --- | --- |
| [BOOT001-CODEX](../tasks/BOOT001-CODEX.md) | 3 份首稿、3 份实验脚本／证据与汇总，已提交 b13a84f | 已验收范围内采用 | 当前主实例＋两个内部子 Agent；首稿完成后比较，不是跨厂商盲测 |
| [BOOT003-WB](../tasks/BOOT003-WB.md) | 3 份 judge、公共输入与汇总；作者记 done，并明确等待统一整合者代收 | observed：保留原稿并代收；下表复核／限定重要判断 | 三个同实例派生上下文分不同视角；组汇总已读 Codex 结论，不能把所有结果称为同题全盲评测 |
| [BOOT002-ZCODE](../tasks/BOOT002-ZCODE.md) | 只有 task 与公共输入，4 个预期候选及汇总未交付 | missing：用户答“已经停止，按缺失记录”；仅保存已有残稿，不计入结论 | 不因参与者列表推断 ZCode 子会话／Claude CLI 实际完成或在线；源任务按缺失交付保留 blocked |

两组均声明源码基线 `8d2645f80f43df4932515f5b6650a05e53410f5b`；整合入口为 `b13a84f`。实际内容和验证强度决定采信，模型品牌、篇幅和赞同人数不作为正确性标准。
外部候选／公共输入共 6 份文件的原始字节 SHA-256 保存在[接收快照](../../../results/BOOT004-INTEGRATE/received-files.json)，提交前再次核对；来源 task 的接收注记另行记录。

## 统一判断

| 能力 | 统一判定 | 可复核依据 |
| --- | --- | --- |
| 自身协议治理自身维护 | 可以，依赖实际执行者与授权 | AGENTS／PROTOCOL／维护入口、既有任务与提交；本轮也实际使用 |
| 从母仓库及已安装副本再生成骨架 | 可以，已实测 | BOOT001 三份两代实验；WB 工具链报告独立两代实验；管理器与清单在 33 项分发集内 |
| 副本有限完整性自检 | 可以，但非完整开发验证 | checker 校验受信任清单所列文件、编码、链接、业务 task 状态；不验证任意删改清单后的原始契约、Python 语法或维护 task |
| 默认副本再生产完整母模板开发体系 | 不具备 | manifest 不含 tests／CI／maintenance／workbench；完整 Git clone 是另外的取得开发仓库方式 |
| 通用前台适配器监督与接力 | 有实现和模拟验证 | workbench 的 command／checkpoint／result／quota_codes 接口及 tests；真实供应商适配仍待接入 |
| 真实多个 AI 持续开发→独立测试→失败修复→复测 | 尚未形成已验收闭环 | dispatch 处理指定任务，finish 依据提交结果状态流转；实际 revision／测试执行及后续调度未端到端验证 |

## 争议复核与限定

保留 WB 原稿，不把下面的整合判断回写成作者共识。

| 原判断／建议 | 整合处理 | 理由或本轮复现 |
| --- | --- | --- |
| “删除检查器自身仍报 OK” | 采纳清单缩减问题，纠正描述 | 从 manifest 移除 checker 与 git guide 两项，checker 文件仍存在并可运行，返回 files=31。没有证明物理删除执行脚本后它还能运行。 |
| “副本自检不成立／验证能力为零” | 限定为完整验证不足 | 副本具有可运行的 lint；缩减契约、缺安装状态、manager 语法损坏仍可通过，不等于对原有检查对象完全无检测能力。 |
| “manifest 无人校验” | 限定为原始契约完整性未校验 | checker 校验 format/version/非空列表/重复项/路径；安装器还要求 manifest 与 manager 在清单中。缺的是独立的核心组成约束，而非零校验。 |
| “没有端到端测试，init 与 checker 从未串联验证” | 接纳自动回归接缝缺口，纠正绝对表述 | 现有 checker 测试复制母目录；manager tests 单独覆盖 init。常规测试中缺少真实 init 产物→checker 的明确串联断言。但 PUB001 及 BOOT001 已实测安装→检查，不能说从未验证。 |
| “母仓库无 template-state，不能用自家工具维护自身” | 不采纳为不能自举的依据 | template-state 属于消费端更新基线；母仓库按 Git／自身协议／checker／tests 维护。缺状态解释 installer update 不适用，不能否定实际自身维护流程。 |
| “绝对路径必须消除，否则产物不可移植” | 接纳迁移恢复问题，保留本地配置设计 | coordinationRoot 本来是本机主目录配置。移动副本后仍指旧路径，checker 不提示，已复现；需要重新绑定。默认 URL source 无本地源路径依赖，不能泛化为所有安装均不可移植。 |
| “相对本地 source 随 cwd 变化而失效” | 采纳，已独立复现 | init 用 --source . 原样记录 .；从母目录运行 update --check 成功，从安装目标目录运行相同 update 命令失败。建议规范化本地源或明确来源解析基准。 |
| “维护侧没有固定共享协调载体，所以必然死锁” | 接纳治理记录缺口，降级死锁结论 | 本轮用户指定＋维护 task／RUN 可以记录合法授权。独立 task owner 可在授权内整合，规则已允许用户指定／预授权接班；缺固定维护侧入口不等于不存在任何合法路径。 |
| “Git author 相同证明人工代提交／所有步骤人工搬运” | 不采纳该推论 | AI 也可按规则调用 Git，统一 author 不认证具体 Agent，也不证明命令由人手工执行。应区分用户目标／授权、AI 执行、工具自动状态处理与无人值守编排。 |
| “空 results／空数据库证明从未真实驱动任何 AI” | 限定证据范围 | 基线或当前空目录只能说明当时该路径未留可见证据，不能证明其他运行历史不存在；本轮实际候选已在 results。已验证事实应写为真实客户端驱动未取得验收证据。 |

直接来源：tools/check_template.py:90–134；tools/template_manager.py:21–25、110–140、196–225、410–434；tools/agent_workbench.py:323–356、565–645；tests/test_project_template.py:16–29；tests/test_template_manager.py:21–88；[PUB001](../tasks/PUB001-CODEX.md)。

## 去重后的后续候选

这些是待实施建议，不是本轮已修复项目。

| 顺序 | 建议任务 | 验收要点 |
| --- | --- | --- |
| 1 | 补分发／维护验证接缝 | 核心组成被移出 manifest、managed Python 语法错误、维护 task 状态错误可检测；真实 init 产物→checker 自动回归；不要求任意普通复制包都有安装状态 |
| 2 | 固定维护侧协调入口 | 明确实际 integrator、授权、当前范围、接收／缺失处理与串行写入；根种子保持空白。普通授权内单人任务继续简化 |
| 3 | 本地源与移动工程恢复 | 相对 source 不依赖调用 cwd；移动后 coordinationRoot 有明确重新绑定步骤／诊断；保留 URL 默认路径和本机配置用途 |
| 4 | 整理业务副本提升为源的步骤 | 保留业务历史，明确处理登记／CURRENT／协调／README 等种子；验证新工程不继承真实身份／进度。可先文档化，不必先造打包平台 |
| 5 | 真实前台 AI＋独立测试最小闭环 | 独立 worktree、核验实际 revision、执行真实测试、失败反馈→修复新版本→复测→成功停止；保留中断／停写确认和人工介入 |

扩大默认清单携带完整 tests／CI 尚未采纳：完整测试当前依赖可选 relay／legacy 等开发资产，简单复制会扩大业务安装包且仍不保证 fork 的母仓库限定 CI 生效。可以另行比较开发 clone、开发包或轻量 smoke，不把这项设计分歧伪装成一致结论。

## 验证与保存

整合阶段新增隔离复现：[verify_claims.py](../../../results/BOOT004-INTEGRATE/verify_claims.py) 与 [UTF-8 原始结果](../../../results/BOOT004-INTEGRATE/verification.json)。固定源码基线运行，沙箱外隔离执行获自动审核允许；复现不改生产代码／配置，两次执行均成功，第二次仅改证据保存以修复 PowerShell 中文编码。

实测：正常检查 33 项；缩减清单 31 项仍通过；无安装状态／manager 语法无效仍通过；移动后协调根失效仍通过；相同相对 source 的 update 因调用 cwd 不同出现退出 0／1。

BOOT001 的 75 项完整 unittest 已在前阶段通过；WB 的超时与删除钩子错误按其环境事实保留，不据此判项目断言失败。本整合阶段不重复完整代码回归；交付前模板检查33项、12份Markdown本地链接、1份复现Python语法与证据关键字段、Git diff 检查通过。本轮无真实外部模型、跨操作系统、新远端 CI 或发布验收。

原始候选：[Codex 汇总](../../../results/BOOT001-CODEX/run-001/comparison/review.md)、[WB 汇总](../../../results/BOOT003-WB/run-001/comparison/review.md)、[WB 工具链](../../../results/BOOT003-WB/run-001/wb-audit-toolchain/judge.md)、[WB 协议](../../../results/BOOT003-WB/run-001/wb-audit-protocol/judge.md)、[WB 实证](../../../results/BOOT003-WB/run-001/wb-audit-evidence/judge.md)、[ZCode 已有公共输入](../../../results/BOOT002-ZCODE/run-001/input.md)。保留原稿中的原始任务号、强结论和时间语境，以上纠正只属于整合者判断。
