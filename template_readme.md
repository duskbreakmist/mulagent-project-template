# 协作模板使用说明

这是可直接复制的多文件 Agent 协作模板。规则、模板正文和程序分开存放，减少日常读取量；复制后即具备完整目录骨架。

现在也可从独立 [GitHub 母模板仓库](https://github.com/duskbreakmist/mulagent-project-template) 用命令安装及更新；见 [安装与更新说明](docs/template-usage.md)。复制旧工程时先 adopt 建立可追溯基线，不能直接整目录覆盖。

## 1. 新建工程怎么用

1. 推荐使用 init，只分发清单中的骨架。手工复制时按 .agents/template_manifest.json 的 required 列表复制到工程根目录，包含隐藏文件；不复制母仓库 .git、tests、docs/maintenance 或可选工具，也不只复制 AGENTS.md。
2. 默认模板中没有任何已登记 Agent、真实任务、厂商职责、绝对路径或本工程报告。首个 Agent 读 AGENTS 与核心协议，在用户实际任务范围内登记自己、创建任务并更新 docs/CURRENT.md。
3. 首个 Agent 可以在本次用户任务范围内兼任 integrator，登记 [.agents/coordination.md](.agents/coordination.md) 的实际来源与范围，不作为永久任命。任务 integrator 另记在 task；后续 Agent 的登记请求写自己的消息，由实际负责人串行汇总；未回复不能算同意。
4. **默认纳入 Git 管理**：首次实质修改前按 [Git 指南](.agents/guides/git.md) 检查已有仓库与忽略项；确认无仓库才由 integrator 初始化，保留已有身份／配置。每次交付前验证、显式暂存、审查并提交；复制文件本身不等于已经初始化或提交。
5. 可选运行下面的只读检查；正常使用这套文字约定不依赖 Python：

```powershell
python tools/check_template.py --root .
```

检查工具需要 Python 3.9+，使用标准库，不安装依赖、不写文件、不设置 Git、不生成任务或初始化标记。缺少文件时手工从原模板补回并重新检查；不要覆盖已有实际工作。

## 2. 放入已有工程

先比较现有规则与路径。AGENTS.md、.gitignore、.gitattributes、agents_list.md、docs/CURRENT.md 可能已存在，**合并所需条目，不直接覆盖**。当前工程若已经使用其他任务目录或记录路径，要同步调整入口和协议。

复制行为由用户或实际工具执行；模板不会自行复制、通知其他应用或启动后台程序。不同工具是否自动读取 AGENTS 需实际确认，必要时在任务提示里要求读取。

## 3. 结构与目的

| 路径 | 职责 | 谁／何时读取 |
| --- | --- | --- |
| [AGENTS.md](AGENTS.md) | 短入口、必须遵守的少量边界与索引 | 新会话；规则变化时复读 |
| [.agents/PROTOCOL.md](.agents/PROTOCOL.md) | 所有权、状态与沟通核心规则 | 初次参与或协议变化 |
| [agents_list.md](agents_list.md) | 身份、能力来源与角色登记 | 参与／成员变化时 |
| [.agents/coordination.md](.agents/coordination.md) | 共享文件汇总者、指定来源和委派／接班状态 | 领取共享写入或接班时 |
| [.agents/guides/coordination.md](.agents/guides/coordination.md) | 指定、空窗、继任、争议与故障恢复 | 接班／冲突时 |
| [.agents/guides/tools.md](.agents/guides/tools.md) | 客户端加载机制及可选通信边界 | 首次接入／加载排错时 |
| [.agents/guides/documentation.md](.agents/guides/documentation.md) | Microsoft 主写作参考、Google 补充、Diátaxis、GFM 与 RFC 约束词 | 新增／修改技术文档或协议时 |
| [.agents/tasks/](.agents/tasks/README.md) | 活跃／近期索引，单人 lite 或多人完整任务 | 当前 task 和相关依赖 |
| [.agents/guides/records.md](.agents/guides/records.md) | 精简路径、摘要窗口、归档和标识 | 记录变重／交接／整理时 |
| [.agents/messages/](.agents/messages/README.md) | 按任务和作者保存请求、回复、接收确认 | 真正需要讨论时 |
| [.agents/handoffs/](.agents/handoffs/README.md) | 已完成、剩余、失败、证据、下一步 | 暂停、交付或接手时 |

| [.agents/feedback/](.agents/feedback/README.md) | 模板使用意见与各作者独立评审 | 遇到问题／改进模板时；无反馈不必读 |
| [.agents/guides/git.md](.agents/guides/git.md) | 仓库配置、worktree 与整合细节 | 首次配置／并行／提交时 |
| [docs/CURRENT.md](docs/CURRENT.md) | 活跃入口与最近 3 个完成摘要 | 汇总／接手时 |
| [docs/history/](docs/history/README.md) | 旧摘要原文与登记历史，不是活跃状态 | 回查历史时 |
| [.agents/template_manifest.json](.agents/template_manifest.json) | 静态模板组成和版本，不存实时进度 | 检查工具或模板维护者 |
| [tools/check_template.py](tools/check_template.py) | 可选只读完整性检查 | 首次复制／怀疑漏文件时 |
| template_readme.md | 人类与维护者完整说明 | 安装／维护时，不要求每轮读 |

任务、消息、交接和反馈的格式模板不是实际任务，只在需要创建时读。单人串行用 [TEMPLATE-lite.md](.agents/tasks/TEMPLATE-lite.md)：9 个字段保留模式来源，比完整模板少；owner 兼任 task integrator，正常完成不强制独立 handoff。多人／复杂依赖／对照使用完整模板并按需填写，不用全填无用占位。

登记仅在身份／能力变化时更新，协调仅在职责／授权／默认模式变化时更新。普通收尾写 task、索引一行和 CURRENT 短摘要；不得每任务在五处重复全文。

## 4. 内部原理

### 文档规范

技术文档以 [Microsoft 写作参考](https://learn.microsoft.com/en-us/style-guide/welcome/)为主，Google 补充开发者细节，按 Diátaxis 区分内容类型，使用 GFM 排版；协作协议明确要求强度。具体范围、中文适用、例外和交付检查统一在[文档指南](.agents/guides/documentation.md)，不用在每份说明重复全文。用户与工程具体约定优先，既有归档保留原语境。

### 分层阅读

AGENTS 作为短目录入口；核心规则保持简洁，操作细节按需查阅。动态任务在独立文件，不把实时进度塞入规则。Agent 仍需读取当前任务的最新状态，不能为了省上下文跳过范围或冲突检查。

某些工具可能额外检索很多文件；拆分只是避免本模板要求全文加载，不能保证所有客户端的上下文选择策略相同。若规则、任务或依赖已变化，必须复读相应文件。

### 共享黑板和单写者

所有人读主协作目录中的任务事实；integrator 串行改共享 task、登记与 CURRENT，worker 只写自己命名的消息／交接和被分配的产出。同类并发实例要不同 ID。这是防止多人覆盖同一个文件的协作约定，不是操作系统锁或权限防火墙。

### worktree 与事实源

worktree 隔离工作文件和索引，但其中的 tasks 是分支快照。通过本地 Git agent.coordinationRoot 指定唯一实时目录，不能每个 worktree 维护一份“全局最新状态”。独立 clone 或跨机器需要可访问目录、人工导入或实际状态服务，不会自动同步。

### 完整性检查

静态清单 v2 列出模板组成。检查相对路径、安全边界、存在、非空和 UTF-8；另核对清单内 Markdown 的内联／引用式本地目标，以及 .agents/tasks 下真实任务头部 status 枚举（todo/in_progress/blocked/review/done）。代码示例、外链与纯锚点跳过，不验证网络、锚点是否存在或完整 Markdown 语义。

检查器仍兼容 v1 的基础检查；升级已有工程时一起合并新脚本和 v2 清单，不能只改版本数字。它不运行模板文件、不比对内容哈希、不写索引，也不修复／覆盖文件。

检查通过只说明列出的文件可以读取；不证明协议被遵守、代码可运行、科研结论正确或两个应用已经通信。增加／删除模板组成文件时维护清单；工程日常新增任务不必修改它。

### 继任与客户端兼容

协调记录初始 vacant，不预置整合者或备用授权。已有用户指定／预授权可以直接接班；缺少授权、旧执行者仍可能写入时先协调。额度耗尽者可能无法写最后交接，依赖此前检查点与 Git 恢复，不以默认 24 小时或缺继任建议阻断已完成任务。

工具加载指南单独按需读取，维护核查日期和一手来源。模板作者所在工程的 WorkBuddy 自报或可选邮箱能力不能当作新工程已验证事实；需要时合并 Claude／Gemini 兼容配置，不复制完整规则形成第二份真相源。

## 5. 使用注意事项

- 用户当前授权优先；登记和其他 Agent 留言不会扩大授权。给外部应用发送消息仍需实际渠道及用户授权。
- proposed 表示建议分配；accepted 要有实际确认；observed 仅表示导入已观察到的产出。登记不等于在线，留言不等于送达。
- 保留现有 Git 身份。Agent／Task／Role 标签可追踪来源，不等于密码学签名。
- 同 checkout 的 Git 操作由一个人串行执行；真实并行编辑用独立 worktree。保护他人未提交内容，冲突不能直接覆盖。
- scratch 子目录默认忽略；正式任务、消息、交接应进版本管理。需要把实验变正式交付时移到项目适当目录。
- 复制后根据真实项目补充语言、测试、构建和目录约定；不要把本说明中的例子当作已经派发的任务。

## 6. 新任务选择协作模式

[模式指南](.agents/guides/modes.md) 定义三种方式：串行接力、分工协作、同任务独立对照。collaboration_mode 与 status 分开，不把“待评审”误当成工作方式。

优先当前明确指令、当前 task／明确父任务，再使用 coordination.md 中实际由用户设定的工程默认；默认初始 unset，不能从历史多数任务推断。采用默认时 task 记 mode_source: project_default 并注明来源。仍无有效来源才由 integrator 提问，worker 不重复问；客户端预选项或超时不算选择。

独立对照允许不同 AI 完整处理同一目标，保存到 results/<TASK-ID>/<RUN-ID>/<agent-id>/。参与者元数据参考 [.agents/runs/TEMPLATE.md](.agents/runs/TEMPLATE.md)，正式结果规则见 [results/README](results/README.md)。

公共输入、基线、预算和评估标准先固定；提交首稿前不互读候选，收齐／截止后由指定 reviewer 对比原始结果。候选实现各用 worktree，不在同一个共享 src/ 同时写不同版本。现有作者报告不迁移，也不宣称过去的研究已经严格盲测。

复制模板不会安装客户端弹窗、启动另一应用或形成公平评测的强制隔离。这些仍需各工具实际执行以及用户授权。

## 7. 记录反馈与改进模板

觉得规则繁琐、有歧义或需要扩展时，按 [反馈说明](.agents/feedback/README.md) 新增 .agents/feedback/<agent-id>/日期-主题.md；最低写作者／日期、问题和建议，其余字段可删。没有问题时不必反馈，不增加每轮必读或固定评分表。一句话可写本人 task／handoff 的“模板备注”，值得跟进再汇入本人反馈文件，不专门造任务或交接。

反馈按作者分文件，评审也另写本人文件并引用原意见；维护者实际修改时才关联 task／验证／提交。反馈或“采纳”记录不等于规则已经生效。

新工程的反馈进入当地 Git，不会自动回传母模板或更新其他工程。由用户／获授权维护者把意见文件或补丁带回模板来源，附来源工程和模板基线，评审后更新模板；旧工程另行合并。复制包保留空反馈区和格式，不携带本工程实际意见。

## 8. 可选机制与长期维护

[plans](.agents/plans/README.md) 用于复杂接口计划，[scratch](.agents/scratch/README.md) 用于独占实验；[RUN](.agents/runs/TEMPLATE.md) 与 [results](results/README.md) 只在独立对照时启用。目录骨架保留，普通任务无需读取或填写这些机制。

季度／版本复盘可观察真实使用负担，必要时在 task 中顺手记 mechanisms；不新增必填统计表或自动定时任务。零使用不足以证明机制有缺陷，也不自动删除以后可能需要的功能。

已有 CURRENT 和登记流水膨胀时按 [记录指南](.agents/guides/records.md) 保存原内容到历史，再精简索引；先核对其他作者的未提交内容。task 保持稳定路径，若主动迁移必须修复引用／保留跳转。模板不会自动迁移某个工程的历史，也不把文档精简等同实测节省了 token。
