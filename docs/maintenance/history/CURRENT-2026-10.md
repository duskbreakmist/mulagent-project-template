# 2026-10 母模板维护完成摘要

## TPL003（从维护 CURRENT 保存）

2026-10-11 [TPL003](../tasks/TPL003.md) / codex-structure-20261011：确认母模板开发定位并评审结构，单人串行；范围仅评审与维护记录。
建议优先补维护 task／链接校验和分发边界回归，再完善维护入口、协作场景验收与文案。建议尚未实施，根分发种子保持原样。
本轮模板检查通过（32 项）；测试首次被沙箱临时目录权限阻断，获准沙箱外重跑后 56 项全通过；git diff --check 通过。未验证真实客户端互通或远端 CI。

归档时仅调整 task 相对链接，保留原结论的时间语境；之后的实现见 ORCH001-CODEX，不改写旧验收事实。

## TPL004（从维护 CURRENT 保存）

2026-10-11 [TPL004](../tasks/TPL004.md) / wb-structure-20261011：对 TPL003 的交叉复核。认可母模板定位与四层结构；分发骨架 32 项、根种子保持空白。增量建议：维护身份识别去掉对 git remote 的依赖、legacy 同名快照加归档标识防误改、共享 CURRENT 并发写入保护。本轮 check 通过（32 项），base_commit 01f66e7，本地 ahead 1 未推送。

归档仅调整 task 相对链接，原作者结论和当时 Git 状态保持原样。

## TPL006（从维护 CURRENT 保存）

2026-10-11 [TPL006](../tasks/TPL006.md) / wb-hy4-20261011：同源指令第四实例，对话评审后按用户要求补记。认可母模板定位与三层结构；评审时实测发现 TPL003 未提交、他人沙箱外测试重跑进行中，选择只读避让（事后证实）。独有建议：维护任务小模板、跨 harness 真实任务试点验收协议。评审 base 0df7095，补记中 HEAD 前进至 8eebc25（RUN 审计记录），提交后本地 ahead 4 未推送；TPL002 摘要已移入 history/CURRENT-2026-10.md。

归档仅调整 task 相对链接，保留原作者结论和当时状态，不据后续产出改写历史。

## ORCH001-CODEX（从维护 CURRENT 保存）

2026-10-11 [ORCH001-CODEX](../tasks/ORCH001-CODEX.md) / codex-workbench-20261011：按五项要求交付[可选工作台](../../optional/agent-workbench.md)，含登记／原子认领、额度检查点接力、开发测试反馈、封存调研与人工界面。
隔离 worktree 完整 70 项回归通过；最终工作台 18 项通过（补充人工入口、候选接力与数据保留迁移）；模板 32 项检查、Python 编译与 diff 检查通过；浏览器人工创建／暂停／接手／检查点读取实测成功。
真实四客户端启动与额度适配、独立测试 Agent 审查、文件权限硬隔离未完成；本轮不调用模型、不推送。旧 TPL003 本人摘要见[维护历史](CURRENT-2026-10.md)，根种子与他人暂存保持原样。

2026-10-11 归档仅调整相对链接，保留原交付时的验证及未推送语境；之后的发布与双平台 CI 见 PUB001-CODEX。

## DOC001-CODEX（从维护 CURRENT 保存）

2026-10-11 [DOC001-CODEX](../tasks/DOC001-CODEX.md) / codex-docs-20261011：README 补活动文件职责树、工作台用法、本地已提交版本安装；接入说明补各客户端可复制提示词。
模板检查 32 项、diff 检查、独立新工程 init --commit／无 origin／外置工作台 status 冒烟通过；新 README 在最小安装副本检查通过。本轮开始时实时远端 main=0df7095，本地=a329301；未 push、未跑远端 CI。

2026-10-11 归档仅调整 task 相对链接，保留当时验证与未推送语境；后续发布见 PUB001-CODEX，跨电脑示例修正见 DOC003-CODEX。

## DOC002-CODEX（从维护 CURRENT 保存）

2026-10-11 [DOC002-CODEX](../tasks/DOC002-CODEX.md) / codex-docstyle-20261011：将 Microsoft／Google 写作参考、Diátaxis 内容结构、GFM 排版和 RFC 约束词写入[通用指南](../../../.agents/guides/documentation.md)，并接入 AGENTS／协议／README／模板手册与 manifest；默认中文，用户及工程具体约定优先。
模板 33 项、AGENTS 15 行、diff 检查通过；独立候选包新装与 32→33 项升级通过，升级保留业务 README。未推送、未跑远端 CI；TPL006 完成摘要移入[维护历史](CURRENT-2026-10.md)，保留原结论语境。

2026-10-11 归档仅调整 task 相对链接，保留原文案与当时验证语境；后续推送见 PUB001-CODEX。

## PUB001-CODEX（从维护 CURRENT 保存）

2026-10-11 [PUB001-CODEX](../tasks/PUB001-CODEX.md) / codex-publish-20261011：按用户授权发布文档规范与前序提交，实测 GitHub 默认新工程安装（33 项、独立 Git、干净状态）；首次 Windows CI 短路径问题已最小修复。
修复 f9c7669 经官方 API 原样发布，提交 SHA 一致；相关 20 项、隔离完整 75 项和[双平台 CI](https://github.com/duskbreakmist/mulagent-project-template/actions/runs/38120883231)通过。常规 Git 通道故障未改持久配置；他人 TPL005 暂存保留。ORCH001 完成摘要移入维护历史，保留原验收边界。

2026-10-11 BOOT001-CODEX 归档调整 task 相对链接，并修复 DOC002 既有通用指南相对链接；保留发布当时事实，不把当时 CI 算成本轮验证。

## DOC003-CODEX（从维护 CURRENT 保存）

2026-10-11 [DOC003-CODEX](../tasks/DOC003-CODEX.md) / codex-portable-20261011：README／安装说明去掉固定 H 盘路径；在空工程目录 clone 同级工具仓库，再 init --root .，工作台／本地来源／adopt／母仓库更新示例同步。
本地候选 Git 副本的相对路径安装、33 项检查、外置工作台 status、干净独立 Git 和 diff 检查通过；未实机验证其他操作系统。只改文档，不重复完整代码回归；DOC001 完成摘要移入维护历史，保留原语境。

2026-10-11 BOOT004-INTEGRATE 归档仅调整 task 相对链接，保留原结论与当时验证边界。

## DOC004-WB（从维护 CURRENT 保存）

2026-10-11 [DOC004-WB](../tasks/DOC004-WB.md) / wb-hy4-20261011：审计 33 项分发文件中的"白熊效应"（负向引用受众不知道的迁移史，用户举例 README"不再依赖 Live2D 工程"）。真白熊 5 处：README Live2D 句、template_readme"旧单文件／解包／.bootstrap-v1"、tools.md 与 template_readme 的未定义"源工程"；判定准则"可操作的否定保留，考古的否定删除"，正常的时间性指称（旧执行者／旧基线等）已排除。
check 33 项与 diff 检查通过；建议均未实施，待用户确认后另立任务。DOC002 摘要移入维护历史。遗留：TPL005 仍 staged、审计轮次待指定汇总者。

2026-10-11 BOOT005-CODEX归档仅调整task相对链接，保留原审计当时语境；后续文案清理与代收见既有结构审计RUN，不改写历史说明。

## BOOT001-CODEX（从维护 CURRENT 保存）

2026-10-11 [BOOT001-CODEX](../tasks/BOOT001-CODEX.md) / codex-bootstrap-20261011：当前实例与两个内部子 Agent 同题独立判断，全部首稿交付后汇总，见[证据与对照](../../../results/BOOT001-CODEX/run-001/comparison/review.md)。人参与的自身维护和协议骨架跨代复制成立；默认副本无完整开发体系，真实 AI 自主迭代闭环尚未形成。
本轮 33 项检查、沙箱外 75 项测试及三份隔离两代实验通过；另实测业务登记 seed 继承与维护 task 状态不在通用检查覆盖范围。未改实现／未接真实客户端／未推送；PUB001 摘要移入维护历史，保留原验收语境。

2026-10-11 ENG001-CODEX归档仅调整相对链接，保留原评估时间语境；后续检查覆盖和发布改进见BOOT005，不改写当时边界。

## 自举审计统一整合（本轮已完成）

2026-10-11 用户指定 codex-bootstrap-integrator-20261011 整合，[BOOT004-INTEGRATE](../tasks/BOOT004-INTEGRATE.md)／[统一 RUN](../runs/2026-10-11-bootstrap-audit.md)。已收 Codex、WB 两组共六份首稿；[BOOT002-ZCODE](../tasks/BOOT002-ZCODE.md) 用户确认停止且报告缺失，按 missing 收尾，源任务 blocked。原稿保留，治理授权与共享写入范围记在维护 RUN，根种子保持空白。
清单缩减、语法／状态检查覆盖与路径问题隔离复现；对“自检为零／母仓库不能维护自己／必然死锁”等强结论作限定。形成五项去重候选，未改生产实现；前轮 75 项通过按当时事实引用，不冒充本阶段重跑。DOC003 摘要保存至维护历史。

## BOOT005-CODEX（从维护 CURRENT 保存）

2026-10-11 [BOOT005-CODEX](../tasks/BOOT005-CODEX.md) / codex-bootstrap-integrator-20261011：完成核心清单／Python语法／维护task检查、维护COORDINATION、本地来源规范化与update --source恢复、移动／种子整理指南。默认分发33项不变，真实AI接入／完整开发包不在本轮范围。
33项维护检查与85项本地完整回归通过；实现b69d630原样发布，官方API核对SHA一致，Windows／Ubuntu CI均成功。常规Git连接重置后经官方API非强制发布，未改持久配置／移动标签；DOC004旧摘要归档。
2026-10-11 后续应用评估：已足够作为有人监督的业务开发协作基础；业务目标、构建／测试、验收和自身CI／发布流程由目标工程定义。下一步以真实小任务验证完整交付闭环，详见task模板备注。

2026-10-11 PILOT001-WB归档时仅调整相对链接并去掉CI行内链接，保留原文与当时验证语境；该闭环已由 PILOT001-WB 试点实证串行形态，后续发布见 REL001-CODEX v0.2.0。

## 业务工程约定与小任务验收（本轮已完成）

2026-10-11 [ENG001-CODEX](../tasks/ENG001-CODEX.md) / codex-bootstrap-integrator-20261011：工程约定集中到README／引用文档，AGENTS与两种task格式接入，补检查边界及旧工程手工保留README的迁移说明，保持33项分发。
独立CLI示例完成BOOTSTRAP→业务红／绿测试3项→核对提交／记录，86项完整回归通过；57ef7f1原样发布，[Windows／Ubuntu CI](https://github.com/duskbreakmist/mulagent-project-template/actions/runs/38139625505)均成功。不宣称真实产品上线或独立AI审查；BOOT001旧摘要保存到维护历史。

## AUDIT001 归档的旧完成摘要

以下原文来自维护 CURRENT；2026-10-14 归档，仅调整相对链接，保留当时的版本、验证和发布语境。

## v0.2.0 发布（已完成）

2026-10-11 [REL001-CODEX](../tasks/REL001-CODEX.md) / codex-bootstrap-integrator-20261011：[v0.2.0](https://github.com/duskbreakmist/mulagent-project-template/releases/tag/v0.2.0)正式发布，标签固定64a135e，Apache-2.0原文与范围说明随35项分发；补update --ref与固定版本安装／升级说明，业务根LICENSE不覆盖。
90项本地完整回归、35项维护检查、真实标签安装／v0.1.1升级及GitHub源码归档逐文件比对通过；[Windows／Ubuntu CI](https://github.com/duskbreakmist/mulagent-project-template/actions/runs/38143819730)均成功。标准Git HTTPS在本机仍受连接限制，未宣称远端clone成功；BOOT004旧摘要归入维护历史，旧标签不移动。

## 多实例同源审计轮次（已收尾）

2026-10-11 四实例用同一提示词审计本仓库，见 [轮次索引](../runs/2026-10-11-structure-audit.md)。四实例确认：codex-structure（TPL003）、wb-structure（TPL004）、zcode-structure（TPL005，中断后由汇总者代收 4f71580）、wb-hy4（TPL006，即第四实例）。盲态不一致，结论作互相印证的审计而非公平横向评测。
2026-10-11 16:02 用户授权 wb-hy4-20261011 收尾：合并建议清单见 RUN 记录（已实施 7 项、未实施候选 8 项，维护边界回归测试居首）。收尾提交：TPL005 代收 4f71580、白熊清理 a0872fc、本收尾；GitHub 推送由用户执行。

## TPL002 迁移方案与修改

根目录仍保存 32 项分发骨架；测试去掉原工程路径回退。COLLAB001–007、评审、反馈与设计归入 legacy，清单记录原始字节哈希。旧初始化器进入 tools/legacy；消息工具进入 tools/ 和 docs/optional，启动器要求显式业务目录；都不默认分发。

## TPL002 迁移验证

独立 56 项 unittest 全通过，TEMPLATE_OK files=32；启动器缺少业务目录退出 2；75 份历史原始字节与 Git 对象哈希一致；原工程 41 项开发文件移除，48 项保护文件哈希和迁移链接检查通过。目标的根登记／任务索引／CURRENT 仍为空骨架。四客户端真实收发、提示音／剪贴板、EXE 未验证；不实现自动唤醒或额度轮换。

## 先前发布

v0.1.1 已发布，实际安装／跨版本更新及双平台 CI 成功；完整记录在 2026-10-10-TPL001.md。本次不移动已发布标签。

## 当前边界

源工程 README 的另一作者软件追加段、ADR-002 未提交编辑及其他业务工作保持原样；模板维护历史和未提交消息工具记录按原作者存档，迁移不扩大既有验收。首次归档发现 Git 换行转换，以归档局部属性修正并逐项核验；没有改写原历史字节。

## 接手与发布

实际开发 task 保存 docs/maintenance/tasks，根分发状态保持空骨架。2026-10-11 用户随后明确授权推送，GitHub main 已接收 f9c7669 及其前序提交；最新发布与 CI 状态见 PUB001-CODEX。历史任务的未推送／未验证说明保留当时语境，不能把旧版绿色 CI 算成本轮通过。

## UPDATE001 归档的旧完成摘要

2026-10-14从维护CURRENT移入以下原文，仅调整相对任务链接，保留原验证语境。

## 业务工程多 AI 试点验收（本轮已完成）

2026-10-11 [PILOT001-WB](../tasks/PILOT001-WB.md) / wb-hy4-20261011：只读评审用户在 H:/Project/test_template_a 的真实试点（基于 f290f2a 可移植流程安装）：dsh-1／wb-1／zcode-1 三 harness 串行接力交付俄罗斯方块 4 功能（FEAT-001–004），跨 AI 代码续写成立，任务内含失败→修复→复测。
独立复验：33 项模板检查、网页逻辑测试、桌面版 `--selftest` 48 项与 `--storage-selftest` 全过；登记／任务板／CURRENT 按协议执行，模板备注反馈通道生效。BOOT004 候选 5 在串行接力层面实证；并行 worktree／真实适配器／跨机器／并发写仍未覆盖，用户预告交由 codex 后续改进。BOOT005 旧摘要归入维护历史。

## DOC006 归档的旧完成摘要

2026-10-18从维护CURRENT移入以下原文，仅调整相对任务链接，保留原验证语境。

## 母模板与业务 README 分离（已完成）

2026-10-13 [DOC005-CODEX](../tasks/DOC005-CODEX.md) / codex-bootstrap-integrator-20261011：母README退出新清单（34项）；init --commit另生成并提交精简业务README，不进入模板基线。template_readme保留文件名并承担模板使用须知；相关活动引用区分业务／模板／母仓库说明。
实现b629ecf已推main，[Windows／Ubuntu完整CI](https://github.com/duskbreakmist/mulagent-project-template/actions/runs/38364780433)均成功（最终94项）。实际v0.2.0旧CLI→新CLI和新工程BOOTSTRAP演练通过；旧README／定制／删除保留，旧基线仅清理元数据，预览只读。v0.2.0标签不移动；ENG001旧摘要归入维护历史。

## SIDECAR001 归档的旧完成摘要

2026-10-21从维护CURRENT移入以下原文，仅调整相对链接，保留原验证语境。

## 全面审查与修复（已完成）

2026-10-14 [AUDIT001-CODEX](../tasks/AUDIT001-CODEX.md) / codex-audit-20261013：用户选择单人串行，完成需求、分发边界、工作台状态机和可维护性审查，见 [详细评估](../reviews/AUDIT001-CODEX.md)。
修复路径别名／大小写保护、分发种子防污染、多测试验收、未知生命周期停写、接力作者封存与异常回滚；补路径交叉回归、最低 Python CI 配置和双记录使用说明。默认分发仍为34项，根种子内容不变。
基线94项通过；本地104项完整回归通过（477.953秒）。用户追加授权后37ab41a已推main；c4d9f5a修复相对源测试的模拟目录问题，[Windows／Ubuntu × Python 3.9／3.13 CI](https://github.com/duskbreakmist/mulagent-project-template/actions/runs/38433606962)四组均通过，每组104项回归与34项模板检查。真实客户端与跨机器仍未验证，标签未改。
