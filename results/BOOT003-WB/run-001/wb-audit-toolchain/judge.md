# 工具链与机械化闭环评审 — wb-audit-toolchain

- 评审对象：`H:\Project\agent-project-template`（母工程）
- 评审视角：抛开人与文字约定，模板自带可执行资产（`tools/`、`tests/`、`.github/`、manifest、init/update/adopt/apply）能否形成"机器自己验证并复制自己"的闭环
- 评审日期：2026-10-11
- 取证方式：读代码 + 在**仓库外**临时目录实测（`C:\Users\Asus\AppData\Local\Temp\wb-audit-init`）；未对母仓库执行任何写入或 git 操作
- 标注约定：全文使用【事实-已读代码】【事实-已实测】【推断】【未验证】【环境伪影】五类标记

---

## 一、结论

### 判定：**部分能**

模板的**"复制自己"这一半闭环是成立的，且已实测跑通到第二代**；**"验证自己"这一半在副本处断裂**——生成出来的副本只能跑一个"文件齐全 + 链接不断"的完整性检查，跑不了母工程那套真正验证协议与安装语义的测试，因为测试与 CI 被明确排除在分发清单之外（这是文档写明的**有意设计**，不是 bug）。

因此准确表述为：

> 模板能机器化地**自我复制**（骨架 + Git 基线，可多代同构复制），
> 但不能机器化地**自我验证**——验证能力只存在于母工程，不随产物分发。
> 自我复制的**契约本身**（manifest）无人校验，可被静默缩减而检查器仍报 OK。

### 三档判定分解

| 子问题 | 结论 | 状态 |
| --- | --- | --- |
| 空白目录能否靠自带命令生成带 Git 基线的可分发模板 | **能**（但产物是 33 项骨架，**不等于**母工程全集） | 已实测 |
| 产物能否与母工程"等价" | **不能** | 已实测 |
| 产物能否自我复制（第二代） | **能**，且与第一代字节一致 | 已实测 |
| 产物能否用它自带的 check + tests 自我验证 | **不能**（只有 check，没有 tests） | 已实测 |
| check 验证的是"文件齐全"还是"协议被遵守" | **文件齐全为主**，协议语义基本不校验 | 已读代码 + 已实测 |
| 工具链是否污染/依赖母工程状态 | **是**（多处） | 已实测 |
| 母工程能否用自家工具维护自己 | **不能**（无安装基线） | 已实测 |

---

## 二、四个判断要点的逐条回答

### 要点 1：空白目录能否仅靠模板自带命令生成"与母工程等价的可分发模板"（含 Git 基线）？

**答案：能生成"可分发模板"，但不能生成"与母工程等价"的副本。含 Git 基线。**

【事实-已实测】在仓库外空目录执行：

```
python H:/Project/agent-project-template/tools/template_manager.py init \
  --root /tmp/wb-audit-init/proj --source "H:/Project/agent-project-template" --ref main --commit
→ INITIALIZED C:\Users\Asus\AppData\Local\Temp\wb-audit-init\proj 8d2645f80f43…
```

产物实测结果：

- 文件数 **34**（33 个清单文件 + `.agents/template-state.json`）
- Git 基线存在：单条提交 `9f39c57 [BOOTSTRAP][template] initialize project template`，`git status` 干净
- **无 remote**（`git remote -v` 为空）——副本与母仓库无 Git 血缘，后续更新只能走 `template_manager update`，不能 `git pull`
- 与母工程对应文件做字节比对：**真实内容差异 0**；4 个文件（manifest、.gitignore、README.md、template_readme.md）仅 CRLF→LF 换行差异（源自在 Windows 检出而 Git 对象为 LF，属正常规范化）

**"不等价"的具体缺口**（已实测，产物中不存在）：

| 母工程有、分发产物没有 | 性质 |
| --- | --- |
| `tests/`（5 个测试模块） | 验证能力 |
| `.github/workflows/checks.yml` | CI |
| `tools/agent_relay.py`、`tools/agent_workbench.py`、`tools/start_agent_relay.cmd` | 可选组件 |
| `tools/legacy/agent_bootstrap.py` | 归档旧初始化器 |
| `docs/maintenance/`、`docs/optional/`、`docs/history/`（非 README 部分） | 维护记录 |
| `results/BOOT001/` 等实际产出 | 运行记录 |

【事实-已读代码】依据是清单本身：`.agents/template_manifest.json:4-38` 的 `required` 共 33 项，不含上述任何一项。
【事实-已读代码】这是**有意设计**，文档三处写明：`docs/template-usage.md:94`（"母模板维护者的 tests／CI／维护日志不在安装清单里"）、`README.md:134`（"tests/ # 开发：独立验证，不默认分发"）、`README.md:159`。

**第二代自举（关键正向证据）**【事实-已实测】：在生成产物 `proj` 内执行 `python tools/template_manager.py init --root ../proj2 --source . --ref main --commit` → 成功，产出 34 个文件，与 `proj` 逐字节比对 **唯一差异是 `.agents/template-state.json`**（该文件记录了 source 路径，必然不同），其余全部一致。

即：**骨架的机械自我复制闭环成立且可多代迭代**；每一代都能复制出下一代，且不需要人工介入。

【事实-已读代码】但复制只认**已提交的 Git 快照**：`template_manager.py:120-124` 先 `git clone --no-checkout` 再 `rev-parse --verify <ref>^{commit}`，工作区未提交内容不可见。故"母工程未提交改动"无法进入自举。

【推断】默认源是 GitHub（`template_manager.py:17`），本机实测未走网络；网络可达性【未验证】。

### 要点 2：生成出来的副本能否用它自带的 check + tests 自我验证？验证的是"文件齐全"还是"协议被遵守"？

**答案：只能用 check 自我验证；tests 不存在。且 check 验证的是"文件齐全 + 链接不断 + status 词表"，基本不验证协议语义。**

【事实-已实测】在产物目录内：

```
python tools/check_template.py --root .      → TEMPLATE_OK files=33     (EXIT=0)
python -m unittest discover -s tests -v      → ImportError: Start directory is not importable: 'tests'
ls .github                                   → No such file or directory
python tools/template_manager.py update --check → UPDATE_PLAN changes=0 conflicts=0 protected=5   (可运行)
```

副本可运行的验证只有两条：`check_template.py`（随清单分发）与 `template_manager.py update --check`（需能访问记录的上游源）。

【事实-已读代码】`check_template.py:105-134` 的 `validate()` 实际做的检查：

1. `.agents/template_manifest.json` 存在且 `format == "project_templateA"`、`version ∈ {1,2}`（:110）
2. `required` 为非空列表、每项为相对路径字符串、无绝对路径、无 `..`、无重复（:118-123）
3. 每个 required 文件**存在**、**非空**、**UTF-8 无 BOM 无替换符**（:125-127，`readable_text`）
4. version==2 追加：Markdown 内联/引用式**本地链接目标存在**且不得越出工程根（:130-132，:69-87）
5. version==2 追加：`.agents/tasks/**.md` 的头部 `status` 字段取值 ∈ {todo,in_progress,blocked,review,done}、不得重复（:133，:90-102）

**结论：这是"文件齐全 + 目录卫生 + 链接可达 + 状态词表"级别的完整性/lint 检查，不是协议合规检查。** 它不校验：

- PROTOCOL 条款是否被遵守（例如 `coordination.md` 是否真填了唯一协调人、任务是否有 owner/scope/验收）
- 清单本身是否**完整**（见阻断点 B2）
- `.py` 文件的**语法**——`check_template.py` 对 `.py` 只做"存在 + 非空 + 编码"；只有 `template_manager.py:342-343` 的 `validate_proposal()`（更新落地时）才做 `ast.parse`。即分发的两个 Python 工具即使语法损坏，`check` 仍报 OK
- 安装基线 `.agents/template-state.json` 是否存在/合法（实测 B2）
- 产物是否真由 init 生成

母工程那套真正有分量的验证（`tests/test_template_manager.py` 覆盖 init/commit/update/三方合并/冲突/回滚/锁/路径逃逸）**不分发**，所以副本拿不到。

### 要点 3：工具链是否会污染/依赖母工程自身状态？

**答案：会，共 4 处，且均已实测。**

1. **绝对路径写进副本的 Git 配置**【事实-已实测】
   `template_manager.py:220` `run_git("config", "--local", "agent.coordinationRoot", root, cwd=root)`，其中 `root` 已 `resolve()`。实测产物中该值为 `C:\Users\Asus\AppData\Local\Temp\wb-audit-init\proj`。而 `.agents/PROTOCOL.md:5` 规定多 worktree 协作要读 `git config --get agent.coordinationRoot`。**副本一旦移动/改名/换机，该配置即失效且无自检**。

2. **state 记录机器绝对路径**【事实-已实测】
   `template_manager.py:212` 写入 `.agents/template-state.json` 的 `source` 字段。实测第一代 = `H:/Project/agent-project-template`（本机绝对路径）；第二代 = `.`（相对路径，换 cwd 即失效）。该文件需随工程提交，故**路径被固化进 Git 历史**。

3. **测试把母工程状态当"纯净副本"**【事实-已实测】
   `tests/test_project_template.py:19-20` 用 `shutil.copytree(SOURCE, ...)` 复制母工程，ignore 列表只有 `.git` / `.test-tmp` / `__pycache__` / `*.pyc`，**不含 `.worktrees/`（实测 1.2M，一份完整第二检出）**。即"独立复制可运行"这一断言是在一个**混有母工程维护产物**的树上做的，而非在 init 真实产物上做的。

4. **母工程残留与同名快照干扰**【事实-已实测】
   - `.test-tmp/` 实测残留 119 项（含散落的 `documentation-guide.md`）；`tests/test_template_manager.py:22-24` 把临时夹具建在**工程内** `.test-tmp`，测试被中断/超时即留下永久残留
   - 同名重复：`find` 命中 **2 份** `.agents/template_manifest.json` 与 **3 份** `PROTOCOL.md`，重复来源为 `docs/maintenance/legacy/live2d-normaldrive/gpt/project_templateA/`。任何"按基名定位协议文件"的自动化（含 AI 检索）会同时命中归档副本；`check_template.py` **不做基名冲突检测**

【事实-已实测】反向补充：已 grep 确认 `tools/` 与分发文档中**没有**任何 `H:\Project` / `C:\Users` 硬编码。源码层面的路径卫生是干净的，污染只发生在上述运行时写入与母工程目录结构上。

### 要点 4：缺口清单——哪些环节必须人工/外部 AI 介入

| 环节 | 为什么必须人工/外部 |
| --- | --- |
| 提交/推送/打发布标签/发布 Release | 工具只读已提交快照（`template_manager.py:120-124`），无 export/pack/publish 子命令（子命令仅 `init/adopt/update/apply`，:440） |
| 判定"这一版能不能发" | 完整验证（tests + CI）只在母工程；CI 还被 `checks.yml:15` 限定只在母仓库生效，产物永不触发 |
| 更新冲突的人工裁决 | 设计如此：`update` 遇冲突退出码 2、落报告、`apply --plan` 前必须人工编辑 proposed（`docs/template-usage.md:66-76`） |
| 校验分发契约（manifest）是否被误改 | 无工具覆盖，见 B2 |
| 协议语义合规（是否真按 PROTOCOL 协作） | 无任何机器检查，只能靠人或外部 AI 读文件判断 |
| 残留锁 / 残留 `.test-tmp` 清理 | 明确要求人工核对 host/pid 后清理（`docs/template-usage.md:106`） |

---

## 三、阻断点清单（按严重度排序）

### B1 — 分发契约刻意排除验证资产，副本的自验证能力为零【最严重】

- 证据：`.agents/template_manifest.json:4-38`（33 项无 `tests/`、无 `.github/`）；`docs/template-usage.md:94`；`README.md:134`；`README.md:159`
- 实测：产物 `tests/` 不存在、`unittest discover -s tests` 直接 ImportError、`.github` 不存在
- 影响：闭环在"产物"处断开。能复制 N 代，但每一代都只带一个完整性检查器。母工程 CI 绿灯**推不出**产物质量。

### B2 — manifest 是唯一真相来源，且无人校验它；check 可被"缩减清单"静默绕过【自举契约不可自证】

- 证据：`check_template.py:107-114` 只用 manifest 校验树，manifest 自身只校验 format/version/路径合法性
- 实测（在副本上）：从 `required` 删除 `tools/check_template.py` 与 `.agents/guides/git.md` 后，`check_template.py` 仍返回 `TEMPLATE_OK files=31`（EXIT=0）；再删掉 `.agents/template-state.json` 后仍 `TEMPLATE_OK files=33`（EXIT=0）
- 影响：**一个把"检查器自己"从清单里删掉的副本，依然能对自己报 OK**。这是自举最致命的逻辑洞：工具无法验证自己的分发契约完整性，只能靠人。

### B3 — 生成器与检查器从未被端到端串联验证

- 证据：`grep -rn "check_template" tests/*.py` 只命中 `tests/test_project_template.py:28`，而该行的检查对象是 `shutil.copytree` 出来的**母工程拷贝**（:19-20），不是 `template_manager.initialize` 的产物
- 反之 `tests/test_template_manager.py:41` 覆盖了 init+commit，但从不对其产物跑 `check_template`
- 影响：仓库中**没有任何测试断言"init 出来的工程能通过 check"**。这两个工具之间的接缝完全未测。

### B4 — 无 export/pack 子命令；自举只认已提交快照，发布环节在工具链之外

- 证据：`template_manager.py:440` 子命令仅 `init/adopt/update/apply`；`template_manager.py:120-124` 必须 `git clone` + `rev-parse` 已提交 commit
- 影响：母工程未提交改动无法自举；打标签、推送、发布 Release 只能人工。严格意义上"机器复制自己"的最后一步（对外发布）在闭环外。

### B5 — 绝对路径固化进产物（Git config 本机路径 + state.source 本机路径）

- 证据：`template_manager.py:220`（`agent.coordinationRoot` = resolve 后的绝对 root）；`template_manager.py:212`（state 记录 source）；`.agents/PROTOCOL.md:5`（协议依赖该 config）
- 实测：产物 git config = `C:\Users\Asus\AppData\Local\Temp\wb-audit-init\proj`；第一代 state.source = `H:/Project/agent-project-template`
- 影响：产物不可移植；移动目录后协议第 1 条依赖失效，且无自检提示。默认 GitHub 源模式不受影响，但"本地源"模式（`docs/template-usage.md:19-28`）必然污染。

### B6 — 母工程自身没有安装基线，母工程不能用自家工具维护自己

- 证据：实测 `.agents/template-state.json` 不存在，`git log --all -- .agents/template-state.json` 为空（从未纳入历史）；执行 `python tools/template_manager.py update --check` → `ERROR: [Errno 2] No such file or directory: ...template-state.json`
- 影响：自举是**单向**的（母 → 子）。母工程对自己的更新/基线管理完全靠人 + CI，工具链不成立。

### B7 — 母工程维护状态污染验证链路（`.worktrees`、legacy 同名快照、`.test-tmp` 残留）

- 证据：`tests/test_project_template.py:19-20`（copytree 未排除 `.worktrees`）；实测 `.worktrees` 1.2M；实测 2 份 `template_manifest.json` / 3 份 `PROTOCOL.md`（`docs/maintenance/legacy/live2d-normaldrive/gpt/project_templateA/.agents/template_manifest.json`）；`tests/test_template_manager.py:22-24`（夹具建在工程内 `.test-tmp`，实测残留 119 项）
- 影响：验证用的是"母工程当前状态"而非"纯净分发物"，导致本地验证结果与 CI（CI 检出不含 gitignore 项）不等价；同名归档快照对 AI/脚本按基名定位协议文件构成实质误改风险。

### B8 — 验证门开销过大，本机实测无法跑出全套结论；CI 覆盖面窄

- 证据：`.github/workflows/checks.yml:15`（`if: github.repository == 'duskbreakmist/mulagent-project-template'`，产物永不触发）、:28-31（只有两条命令：`check_template` + `unittest discover`）
- 实测：全套 `python -m unittest discover -s tests` **480s 未跑完（退出 124）**；分模块：`test_agent_workbench` 18 例 OK（97s）、`test_legacy_bootstrap` 12 例 OK（104s）；`test_project_template` **200s 未完成**；`test_agent_relay` 8 例中 2 例 error、`test_template_manager` 多例 error——**这两个模块的失败经查为【环境伪影】**：traceback 命中本会话沙箱的删除钩子（`sitecustomize.py:1109 _safe_remove` 与 `[safe-delete][SAFE_DELETE_BULK_CONFIRM_REQUIRED]`），非模板缺陷
- 【推断】GitHub Actions 双平台曾通过：git log `b310c0e`/`8ce7f1f` 记录了"真实推送与双平台 CI 通过"。【未验证】我无法访问 Actions 实际运行记录。
- 影响：CI 不做 init→check 端到端冒烟，也不验证产物；验证门本身慢到难以作为本地快速反馈。

---

## 四、最小可行自举路径（3 步）

> 前提：只要"骨架级自我复制"，接受"产物不含测试与 CI"。

1. **在母工程提交改动**（工具只读已提交快照，未提交内容不进入自举）：
   `git -C H:/Project/agent-project-template add -A && git -C H:/Project/agent-project-template commit -m "<说明>"`
2. **在空白目录生成带 Git 基线的新工程**（默认走 GitHub 源以避免本机绝对路径污染；本地源模式会把母工程绝对路径写进产物）：
   `python H:/Project/agent-project-template/tools/template_manager.py init --root <空目录> --commit`
3. **在产物内自检**：
   `python tools/check_template.py --root .`

**必须知道的代价**（这 3 步做不到的事）：

- 第 3 步只是**完整性自检**，不是协议合规验证，也不覆盖 B2（`check` 可被缩减清单绕过）
- 完整验证（tests/CI）**不会**随产物下发；若要给产物做协议级验证，必须**人工把母工程 `tests/` 拷进产物**再 `python -m unittest discover -s tests`——这一步当前没有任何自带命令支持，是闭环上唯一必须人工搬运的环节
- 产物与母仓库无 Git 血缘（无 remote），后续更新只能走 `python tools/template_manager.py update`，且遇冲突需人工裁决

**要让闭环真正闭上的最小改动（3 项，供参考）**：

1. 在 `check_template.py` 增加"manifest 不得缩减 + 不得含归档同名基名 + `.py` 须 `ast.parse` 通过 + 安装基线存在"的断言（修 B2）
2. 新增一个测试：对 `initialize()` 的真实产物执行 `check_template.validate()`（修 B3）
3. 给 `init` 增加 `--with-dev` 或独立 `pack` 子命令，可选地把 `tests/` 与 `.github/` 一并分发（修 B1、B4）

---

## 五、取证附录

### A. 实测命令与输出

| # | 命令 | 结果 |
| --- | --- | --- |
| 1 | `python tools/check_template.py --root .`（母工程） | `TEMPLATE_OK files=33`，EXIT=0 |
| 2 | `init --root /tmp/wb-audit-init/proj --source "H:/Project/agent-project-template" --ref main --commit` | `INITIALIZED … 8d2645f80f43…`，EXIT=0 |
| 3 | 产物 `find`（排除 .git） | 34 个文件，无 `tests/`、无 `.github/` |
| 4 | 产物 `git log` / `git remote -v` / `git status` | 单提交 `9f39c57 [BOOTSTRAP][template] …` / 空 / 干净 |
| 5 | 产物 vs 母工程 33 项字节比对 | 真实内容差异 **0**；4 项仅 CRLF↔LF |
| 6 | 产物内 `check_template.py --root .` | `TEMPLATE_OK files=33`，EXIT=0 |
| 7 | 产物内 `python -m unittest discover -s tests` | `ImportError: Start directory is not importable: 'tests'` |
| 8 | 产物内 `update --check` | `UPDATE_PLAN changes=0 conflicts=0 protected=5 removed_upstream=0` |
| 9 | 第二代 `init --root ../proj2 --source . --ref main --commit` | `INITIALIZED … 9f39c5774f39…`；与一代差异仅 `template-state.json` |
| 10 | 删产物 `.agents/template-state.json` 后 `check` | `TEMPLATE_OK files=33`，EXIT=0 |
| 11 | 从产物 manifest 删 2 项（含 `tools/check_template.py`）后 `check` | `TEMPLATE_OK files=31`，EXIT=0 |
| 12 | 母工程 `update --check` | `ERROR: [Errno 2] No such file or directory: …\.agents\template-state.json` |
| 13 | `find -name template_manifest.json` / `-name PROTOCOL.md` | 2 份 / 3 份（含 legacy 归档快照） |
| 14 | 全套 `unittest discover -s tests` | 480s 未跑完，EXIT=124 |
| 15 | 分模块：workbench / legacy / project_template / relay / template_manager | OK(97s) / OK(104s) / 200s 超时 / 2 error【环境伪影】/ error【环境伪影】 |

### B. 关键证据文件:行号索引

- `.agents/template_manifest.json:4-38` — 33 项分发清单，不含 tests/CI/可选组件
- `tools/template_manager.py:17` — 默认 GitHub 源；`:120-124` 只读已提交快照；`:139-140` 强制上游必须含清单+安装器；`:196-224` initialize；`:212` state 记录 source；`:217-223` git init/config/add/commit；`:220` 写入绝对路径 config；`:440` 子命令仅 init/adopt/update/apply
- `tools/check_template.py:105-134` validate 全流程；`:110-114` manifest 只校验格式/版本/非空；`:125-127` 缺文件/空文件/编码报错；`:130-133` v2 链接与 status 校验
- `.github/workflows/checks.yml:15` 仅母仓库生效；`:28-31` 只有 check + unittest 两步
- `tests/test_project_template.py:19-20` copytree 母工程（未排除 `.worktrees`）；`:28` 唯一调用 check 的地方
- `tests/test_template_manager.py:22-24` 夹具建在工程内 `.test-tmp`；`:41`/`:80-88` 覆盖 init 与 --commit
- `tests/test_agent_relay.py:12`、`tests/test_legacy_bootstrap.py:12` — 依赖不随清单分发的 `tools/agent_relay.py`、`tools/legacy/agent_bootstrap.py`
- `README.md:134`、`README.md:159`、`docs/template-usage.md:94` — 明文声明 tests/CI 不分发
- `.agents/PROTOCOL.md:5` — 多 worktree 依赖 `agent.coordinationRoot`

### C. 声明

- 本评审**未修改母仓库任何受跟踪文件**，**未执行任何 git 提交/推送**。
- 评审过程中 `git status` 出现 `docs/maintenance/CURRENT.md` 等改动与 `results/BOOT001-CODEX/`、`results/BOOT002-ZCODE/` 等未跟踪项——**系并行运行的其他评审实例写入**，非本次评审所为（评审开始时工作树为干净状态）。
- 本次只读命令仅向 gitignore 覆盖的 `.test-tmp/`、`__pycache__/` 及仓库外临时目录写入。
- 【未验证】项：GitHub Actions 实际运行状态、默认 GitHub 源的网络可达性、非 Windows 平台行为。
