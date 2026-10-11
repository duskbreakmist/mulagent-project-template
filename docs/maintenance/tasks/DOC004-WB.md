# DOC004-WB 分发文案"白熊效应"审计（迁移史残留）

- status: done
- assignment: accepted
- collaboration_mode: serial
- mode_source: 用户明确要求检查模板中"房间里大象"式的白熊效应（以 README"不再依赖 Live2D 工程"为例），并询问工程当前状态
- owner: wb-hy4-20261011（本会话；兼任 task integrator；TPL006 同一持续会话）
- created: 2026-10-11
- updated: 2026-10-11
- base_commit: b310c0e
- version_tag: 无

## Objective

审计 33 项分发文件中是否存在"负向引用受众不知道的历史"的白熊句（如"不再依赖 X""旧 Y 流程"），区分真问题与正常的时间性指称，形成修复建议。本轮只审计与记录，不实施修改。

## Scope

只读扫描 manifest 33 项（Markdown 全文 + 分发工具注释）与维护侧对照文件的以下模式：Live2D、旧／原工程／源工程、母仓库／母模板、不再、.bootstrap-v1、绝对路径；复核 tools/check_template.py 与 template_manager.py 注释。写入本任务、docs/maintenance/CURRENT.md 与维护历史，本地提交。不推送，不实施建议，不动他人暂存（TPL005.md 保持 staged）。

## Completed（发现）

**真白熊 5 处（分发文件 + 引用受众不知道的迁移史）**：

1. README.md:166 "不再依赖 Live2D 工程"——分发链最典型：每个新装业务工程的 README 都带这句对它们无意义的迁移史。
2. template_readme.md:3 "它把旧单文件里的规则……不再需要提取代码、解包或写初始化标记"——"旧单文件／解包／初始化标记"是 v1 时代考古词。
3. template_readme.md:96 "不再维护旧 .bootstrap-v1 或初始化锁；不要混用旧解包流程和新模板"——整句只对经历过旧版的人有意义。
4. .agents/guides/tools.md:11 "源工程 WB 自报……"——"源工程"（=原 Live2D 工程）未定义，新工程读者无法定位该数据点。
5. template_readme.md:87 "源工程的 WorkBuddy 自报或可选邮箱能力……"——同上。

**弱白熊 1 处**：README.md:132–133/139 树注释"旧初始化器，不用于当前安装"等——描述新工程不会收到的开发侧目录（已标"开发"，DOC003 已折叠，残留程度低）。

**非白熊（正常用法，勿误伤）**："旧执行者／旧摘要／旧流水归档"（当前体系的前序状态）；"旧工程接入／旧基线"（template-usage，用户自己工程的既有状态，可操作）；"不复制母仓库 .git、tests"（手工复制边界，可操作）；工具代码注释"旧模板／旧版本／旧基线"（升级逻辑实际场景）；"回传母模板"（真实反馈路径）。

**维护侧 1 处待补**：docs/maintenance/README.md:3 "原 Live2D 工程只消费当地规则"——维护文档保留历史合理，但首次出现无链接，新维护者线索断在 legacy/README.md 之前。

## 根因与判定准则

白熊句 = 为母仓库维护者写的负向历史声明泄漏进分发文件。两类读者（业务工程用户／母仓库维护者）共用同一份文案时，为第二类写的"不再 X"进入第一类视野即成噪音。判定准则：**可操作的否定保留，考古的否定删除**——"不对业务工程执行 git pull"是现行规则，保留；"不再依赖 Live2D"删掉后句子依然自洽，属考古。

## 建议（未实施）

1. P1：删 README:166 "不再依赖 Live2D 工程"（其余自洽）；顺带审视"独立开发与可选组件"段的母仓库视角内容是否留在分发 README。
2. P1：template_readme.md:3 改纯现在时（"规则、模板正文和程序分开存放，减少日常读取量"），去掉旧单文件／解包／初始化标记。
3. P2：template_readme.md:96 整句删除或并入 template-usage 第 4 节（旧工程接入才是谈旧版本的地方）。
4. P2：tools.md:11 与 template_readme.md:87 的"源工程"改为可独立理解的表述（如"模板作者所在工程的自报"），保留证据来源语义。
5. P3：maintenance/README.md:3 "原 Live2D 工程"补链接到 legacy/README.md。
6. 判定准则可并入 .agents/guides/documentation.md 写作规范（"分发文件不引用受众不知道的历史"一条）。

## Verification

- 逐文件 grep（33 项 manifest 文件 + 两个分发工具）+ 人工复核每处命中语境；分发工具注释无白熊。
- python tools/check_template.py --root . 通过（TEMPLATE_OK files=33）；git diff --check 通过。
- 未验证：修复实施效果（建议均未实施）、业务工程实装后的读者体验。

## 实施（同会话，用户 2026-10-11 16:02 授权"完成剩下的并提交"）

- README.md:166 删除"不再依赖 Live2D 工程"（P1）。
- template_readme.md:3 改为现在时表述，去掉旧单文件／解包／初始化标记（P1）。
- template_readme.md 删除".bootstrap-v1／旧解包流程"整条（P2；旧工程场景已由 template-usage 第 4 节 adopt 流程覆盖）。
- tools.md 与 template_readme.md 的"源工程"改为"模板作者所在工程"（P2）。
- maintenance/README.md "原 Live2D 工程"补 legacy/ 链接（P3）；顺带修正"先查看 tasks/TPL002.md"过时指引为本目录 CURRENT.md（TPL003 建议 2 的入口过时问题）。
- documentation.md 写作与示例新增"分发说明不引用读者无法获知的历史；可操作的否定保留，考古性的否定删除"（P3 准则入规范）。
- README 树注释"旧初始化器"按原结论保留：已标"开发"且 DOC003 已折叠，属弱白熊不处理。

## Verification（实施后复验）

- python tools/check_template.py --root . 通过（TEMPLATE_OK files=33）；git diff --check 通过。
- manifest 未变（无文件增删，不需要更新清单）。
- 未验证：业务工程实装后的读者体验、远端 CI（未推送）。

## Remaining

建议已全部实施（含 P1–P3）。审计轮次收尾另行处理：TPL005 代提交 4f71580、RUN 记录与合并建议清单由本会话按用户授权收尾。
