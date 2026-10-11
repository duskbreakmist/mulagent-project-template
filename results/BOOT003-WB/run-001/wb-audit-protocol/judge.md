# BOOT001 自举评审 · wb-audit-protocol（协议与治理的自洽性）

- 评审实例：wb-audit-protocol（独立评审，首稿未读其他候选）
- 对象：H:/Project/agent-project-template（协作模板母工程），HEAD = 8d2645f
- 视角：协议与治理的自洽性（不含代码质量、分发边界、文档文案）
- 本文件性质：只读评审。全程未修改仓库任何文件、未提交、未运行测试脚本。
- 标注约定：【事实】文件可验证的内容／【推断】基于事实的推理／【未验证】本轮无法确认

## 结论

**部分能。**

协议可以施加于母工程自身：母工程确实在用它自己的任务模板、CURRENT、Git 规范来治理自己的演化（`docs/maintenance/tasks/*.md` 11 份、`docs/maintenance/CURRENT.md`、`git log` 提交格式 `[TASK-ID][agent-id]`），这已经是可运行的自举实例。【事实】

但自举存在两处**结构性断点**：(1) 母工程为保护分发种子而主动留空的根状态文件，恰好是协议里承载"唯一 integrator / 继任 / 空窗"的载体，母工程没有为它建立维护侧等价物；(2) 协议自身的修改缺少元规则约束。这两点使"规则治理规则的演化"在最关键的一环（谁有权汇总、谁有权分配任务号、谁有权改规则）退化为**用户临场口头授权**，而不是协议内闭环。【推断】

判定不构成"不能"的理由：没有任何一条规则在母工程上产生**不可绕过的循环阻塞**——读规则不需要先登记，写任务不需要先有 integrator（规则允许首位执行者登记 active）。所有死锁都是**条件性**的：只有"多实例并行 + integrator 空缺 + 无人裁决"同时成立时才卡住。【推断】

---

## 缺口清单

### G1【死锁级】共享 integrator 在母工程没有可写载体

证据：

- `.agents/coordination.md:3-5`：`shared_integrator: 未指定 / state: vacant / updated: 待首次任务登记`
- `tools/template_manager.py:21-22`：`SEEDS = {"README.md", "agents_list.md", ".agents/coordination.md", ".agents/tasks/README.md", "docs/CURRENT.md"}` —— coordination.md 是**受保护的分发种子**，安装后永不更新
- `AGENTS.md:15`：母模板维护时"根登记／任务索引／CURRENT 是分发种子，保持空白"
- `docs/maintenance/README.md:5`：空骨架清单只点名 `agents_list.md`、`.agents/tasks/README.md`、`docs/CURRENT.md`，**未提 coordination.md**
- `template_readme.md:10`："默认模板中没有任何已登记 Agent…"
- `docs/maintenance/runs/2026-10-11-structure-audit.md:37`：四实例"共享 integrator 从未指定（coordination.md 仍 vacant）"
- 同文件 `:86`：收尾者"未自任共享 integrator；.agents/coordination.md 状态未改动"

分析：协议把"项目级 integrator"记在 coordination.md（`PROTOCOL.md:13`、`guides/coordination.md:6-7`），而该文件在母工程是分发种子。母工程若写入自己的 integrator，会随模板分发给所有新工程，违反 `template_readme.md:10`；若不写，则该文件在母工程永久 vacant，协议"integrator 串行汇总"失去授权链。母工程的维护目录里也**没有 coordination 的等价文件**（【事实】：`docs/maintenance/` 下无 COORDINATION.md，全文检索 `integrator` 在 `docs/maintenance/` 仅出现于 CURRENT/README 的叙述文字，无字段载体）。

结论：这是**例外的副作用，不是设计**——空骨架规则覆盖了 3 个种子，恰好漏掉了唯一承载治理权限的那个。属于死锁级：在没有用户介入时，母工程内不存在"合法的共享 integrator"这一角色，任何 Agent 声称自己担任都缺乏文件依据。

### G2【死锁级·条件性】中断实例的代收尾没有协议内路径，只能靠用户临场授权

证据：

- `guides/coordination.md:14`：无指定／无预授权时"请用户确定，**不能凭额度、超时或沉默自我接管**"
- `guides/coordination.md:16-17`：异常退出时用检查点恢复，"**仍需用户指定／已有授权**"；不按时间自动判定失联
- `guides/coordination.md:25`："这些规则不提供 CAS、事务或权限隔离…本模板不实现此服务"
- 实证：`runs/2026-10-11-structure-audit.md:41` TPL005 留下 untracked 文件；`:18` 最终"会话中断后由汇总者代收"；`:3`、`:86` 收尾权限来自"2026-10-11 16:02 用户授权"（对话内）
- `docs/maintenance/CURRENT.md:22-23`：`zcode-structure（TPL005，中断后由汇总者代收 4f71580）`

分析：规则自己承认不提供停止机制与互斥（`guides/coordination.md:25`），因此中断实例的收尾**必然**依赖外部（用户）裁决。这次实际发生了，且是靠用户在对话里口头授权解决的——**用户成了协议的运行时组件**。只要用户在场，这不是死锁；一旦跨机器／跨时段并行（协议自己设想的 `agent-mail`、workbench 场景，`tools.md:31-33` 登记为待验证），收尾就无路径。【推断】

附带摩擦：代提交 `4f71580` 的提交信息署名为 `[TPL005][zcode-structure-20261011]`，实际执行者是另一实例（`git log`；`CURRENT.md:22`）【事实】。这与 `guides/git.md:22`"当前身份沿用仓库／用户真实配置，不因 Agent 名称反复更改"冲突——协议没有"代提交如何署名"的规则（摩擦级）。

### G3【摩擦级】空骨架使 PROTOCOL 第 2 条在母工程指向空文件；重定向是补丁且不完整

证据：

- `PROTOCOL.md:2`："读登记、任务索引、当前 task 和它引用的消息／交接"
- 三处目标全空：`agents_list.md:7`（表体为空）、`.agents/tasks/README.md:10`（"初始无任务"）、`docs/CURRENT.md:7`（"待首次实际任务确定"）
- 重定向条款：`AGENTS.md:6` 与 `AGENTS.md:15`
- `docs/maintenance/tasks/` 下**无索引文件**（【事实】：目录内仅 11 个任务文件）
- `docs/maintenance/README.md:32`："若并行维护，按**共同约定**写 scope、单一整合者和独立 worktree"

分析：这是**例外补丁**，不是自洽设计。理由：(a) 补丁写在 AGENTS.md 的正文行里（第 6、15 行），靠硬编码 text 生效，母工程一旦改动维护目录名或 origin 就要改规则本身；(b) 重定向**不完整**——母工程的对照产出同时落在 `results/`（本轮 BOOT001 审计，符合 `PROTOCOL.md:32`）与 `docs/maintenance/runs/`（`runs/2026-10-11-structure-audit.md`），规则未定义母工程该用哪一个【事实】；(c) `docs/maintenance/README.md:32` 对多实例并行的要求是"按共同约定"，即**把协议未定义的决策外包给当次协商**。

判定为摩擦级而非死锁级：读空文件只是浪费一轮读取，不会阻塞；真正阻塞的是 G1。

### G4【死锁级·条件性】维护模式识别依赖 git remote，且该缺陷已被自身审计判定未修复

证据：

- `AGENTS.md:6`："明确维护母模板，**或 origin 指向 duskbreakmist/mulagent-project-template** 时，先读 docs/maintenance/README.md…"
- `runs/2026-10-11-structure-audit.md:75`：未实施候选 3"维护身份自证不依赖 git remote（TPL004-1）"
- 备选标记无效：【事实】本仓库 `git config --local --get agent.coordinationRoot` = `H:/Project/agent-project-template`（自身），与业务工程"指向自身"的形态相同，不能区分维护模式
- `docs/maintenance/README.md:5` 把 `coordinationRoot` 指向本仓库当作维护侧标记，但 `PROTOCOL.md:5` 对它定义的是"多 worktree 定位主目录"用途

分析：一旦仓库被 fork、remote 改名或离线克隆，`AGENTS.md:6` 的判定失效，新会话会走"业务工程"分支，把维护任务写进根 `.agents/tasks/` 与 `docs/CURRENT.md`——即污染分发种子，而协议里保护种子的唯一机制就是这条失效的判定。**改协议的人可能因此不受正确的规则约束**。触发才死锁，故标条件性。【推断】

### G5【摩擦级】元规则缺口：改规则的人不受"任务／评审"约束

证据：

- `PROTOCOL.md:28`：修改"技术文档与协作协议"时**只**要求遵循文档写作规范（Microsoft/Google/Diátaxis/GFM/RFC 2119）
- `PROTOCOL.md:17`："需要独立审查的实现先进入 review；**不要求**普通单人任务制造第二位 reviewer"
- `docs/maintenance/README.md:19`：改分发文件时需维护清单——这是**分发完整性**要求，不是流程要求
- `docs/maintenance/README.md` 全文未出现"修改协议须先立 task"【事实】
- 实践中确实走了任务：DOC002-CODEX 修改 `guides/documentation.md` 并接入 AGENTS/PROTOCOL（`docs/maintenance/tasks/DOC002-CODEX.md:23`）

分析：协议变更在母工程是**惯例**而非规则。当前是单人串行维护状态，风险可控；但协议一旦被改坏（例如删掉"不全量覆盖"或"integrator 串行"），没有任何规则要求它先进入 review 或留下可审计的 task。改规则的人受 Git 规范（`PROTOCOL.md:29-31`）与写作规范约束，**不受**任务登记、评审、ID 分配约束。摩擦级（现状可用，缺保障）。

### G6【摩擦级·自举断点】协议的加载依赖用户手工注入，无强制、无安全默认

证据：

- `.agents/guides/tools.md:11`：WorkBuddy 自动读取仅"模板作者所在工程的 WB 自报"，明确"目标工程重新验证…不能保证所有环境如此"
- `.agents/guides/tools.md:25`：要求"让工具报告实际加载来源，核对关键规则，再开始正式修改"——**软性核对**，无违反后果
- `docs/maintenance/README.md:23`："**不能假定它自动读取 AGENTS**"；`:25-30` 给出可粘贴提示词
- `template_readme.md:25`："不同工具是否自动读取 AGENTS 需实际确认，必要时在任务提示里要求读取"

分析：这是真实的**自举断点**——规则的生效依赖用户粘贴一段文本，即协议无法自己保证被加载。但降级方案存在（粘贴提示词），且母工程把这段提示词写进了自己的维护 README，所以是"可用的降级"而非死锁。缺的是**安全默认**：协议没有规定"若无法确认规则已加载，则本轮降级为只读调查／独占草稿"（对比 `PROTOCOL.md:5` 对 coordinationRoot 不可达的同类降级，说明作者已有该模式，只是没用在加载上）。摩擦级。【推断】

### G7【死锁级·条件性，与 G1 同源】任务 ID 分配权形成闭环缺口

证据：

- `runs/2026-10-11-structure-audit.md:37-38`：四实例"兼任 task integrator 并自选下一个编号"，导致 TPL003/004/005/006 编号抢占
- 同文件 `:46` 已提出修复但 `:74` 列为**未实施**候选 2："worker 不得自选任务编号，未指定 integrator 时应先记录 vacant 并只写本人产物"
- `guides/coordination.md:9`：允许"首位独立执行者只在本次用户任务范围内登记 active"

分析：用户问的循环依赖（改协议须先登记任务，登记又须先有协议）**不是硬死锁**：读协议无需登记，首个执行者可自登记 active（`guides/coordination.md:9`）。真正的环在**编号分配权**上——协议说 ID 由 integrator 分配，而 integrator 在母工程无载体（G1），于是每个实例自抢。该环可用一行规则解除（已提出未实施）。【推断】

---

## 对五个判断要点的直接回答

1. **空骨架是否让"先读登记表／任务索引"失效？** 部分失效。母工程主动留空三个种子（`AGENTS.md:15`、`docs/maintenance/README.md:5`）是**有意的自洽设计**（保护分发纯净性，见 `template_readme.md:10`）；但配套的重定向是**例外补丁**（写在 AGENTS.md 正文、覆盖不全、维护侧无任务索引）。结论：**意图自洽，实现靠补丁**。G3。

2. **多实例并行下 integrator 唯一性／单写者如何保证？** 机制上**不保证**，只剩纪律。`guides/coordination.md:25` 自陈不提供 CAS／事务／隔离；`guides/coordination.md:9` 明说"记录本身不是互斥锁"。实证：共享 CURRENT 被串行追加并出现"瞬时幻影修改"（`runs/:39`），同 checkout 并发提交"靠时间错开侥幸串行"（`runs/:40`）。中断实例的收尾（G2）、空窗（无 24h 规则，`guides/coordination.md:17`）、继任（必须用户指定）均未闭环。

3. **改规则是否走同样流程？** 只走一半：受 Git／写作规范约束，不受任务登记／评审／ID 分配约束（G5）。无元规则条款。

4. **客户端差异算不算自举断点？** 算，但是**可降级的断点**（G6）。协议对非自动读取的客户端是"软性核对 + 提供粘贴文本"，不是硬要求；缺"未确认加载则只读"的安全默认。

5. **有无循环依赖？** 无硬循环（`guides/coordination.md:9` 允许首位执行者自登记）；但存在**编号分配权闭环**（G7），与 G1 同源。

---

## 最小可行自举路径（3 步）

1. **建维护侧协调载体**：新增 `docs/maintenance/COORDINATION.md`（字段沿用 `.agents/coordination.md`），并在 `AGENTS.md:15` 与 `docs/maintenance/README.md:5` 各加一句："母工程的 shared integrator／继任／空窗记在 `docs/maintenance/COORDINATION.md`；根 `.agents/coordination.md` 在母工程恒为 vacant，不作为本工程协调状态。" —— 解除 G1、G7，并为 G2 提供可写状态。

2. **补元规则 + 去掉 remote 依赖**：在 `AGENTS.md` 增一条——"修改 `AGENTS.md`／`.agents/**`／`tools/template_manager.py` 清单，须先在 `docs/maintenance/tasks/` 立 task；未指定 integrator 时 task 状态记 vacant，编号用 `TMP-<agent-id>-<日期>-<主题>` 转正由 integrator 分配；交付前跑 `check_template.py` 与 unittest 并在 task 记录真实结果。" 同时把 `AGENTS.md:6` 的维护模式判定从 origin remote 改为仓库内自证（存在 `docs/maintenance/README.md` 且 `coordinationRoot` 指向自身）。——解除 G4、G5。

3. **会话开场三确认（硬降级）**：新会话必须自报①是否维护模式、②规则实际加载来源（客户端自报，无法确认即为未知）、③本轮 integrator 是否 vacant；任一为"未知/vacant"且存在其他在写实例时，本轮降级为只读调查 + 独占草稿，不写共享文件。——解除 G6，并为 G2 提供无用户时的默认行为。

## 最该优先修的一条规则

**G1：为母工程建立维护侧的 integrator／继任载体。**

理由：G7 是它的直接派生，G2（代收尾、空窗）在无载体时只能靠用户口头授权，G5 的元规则也需要"谁来分配 ID"才能落地。这是唯一一条能把"用户"从协议运行时里替换掉的规则，且改动量最小（一个文件 + 两处一句话）。

---

## 未验证项（本轮未做）

- 【未验证】未运行 `tools/check_template.py`、`python -m unittest discover -s tests`，未验证 manifest required 33 项与仓库实际文件是否一一对应（本轮严格只读）。
- 【未验证】各客户端是否真的自动加载 AGENTS.md，除 `tools.md:5-11` 表格所引厂商文档与自报外未实测；本会话自身的规则加载来源未向客户端求证。
- 【未验证】`template_manager.py` 的 SEEDS 保护在 `update` 路径下的实际行为，仅读到 `protected()`（`template_manager.py:51-60`）实现与 `template-usage.md:53` 的保护规则表标题，未读表内容。
- 【未验证】`docs/maintenance/history/`、`legacy/` 内是否已有协调类记录；仅按文件名与当前目录结构判断，未逐份通读。
- 【未验证】本轮评审为单实例首稿，未读其他候选实例的产出，故不与任何他方结论互相印证。
