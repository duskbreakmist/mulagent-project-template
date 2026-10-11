# 多 Agent 工程协作模板

为单人任务、跨工具分工、接力和独立对照提供简洁的仓库规则。短 AGENTS 入口、按需指南、独立任务／反馈记录；不自动派发其他模型或运行后台服务。

文档采用 Microsoft 主写作参考、Google 开发者细节补充、Diátaxis 内容结构、GFM 排版与 RFC 2119／8174 约束词。默认中文，工程具体约定优先；具体规则见[工程文档写作规范](.agents/guides/documentation.md)。

## 在任意电脑新建工程

需要 Python 3.9+、Git 和你已有的真实 Git 提交身份。Windows、Linux 或 macOS 均可使用下面的相对路径；若 Python 命令为 python3，把示例中的 python 换成 python3。

在新建的空工程文件夹内打开终端，先从 GitHub 下载工具到同级目录，再初始化当前工程：

```powershell
git clone https://github.com/duskbreakmist/mulagent-project-template.git ../agent-template-tools
python ../agent-template-tools/tools/template_manager.py init --root . --commit
python tools/check_template.py --root .
```

`--root .` 表示当前工程文件夹；`../agent-template-tools` 是第一条命令刚下载的工具仓库，不依赖原电脑的盘符或目录。工具放在工程外，初始化前的工程目录保持为空。新工程有自己的 Git 历史，不把模板仓库设为它的 origin。

如果同级已有工具仓库，跳过 clone，先更新它：

```powershell
git -C ../agent-template-tools pull --ff-only
```

然后在新的空工程目录执行上面的 init 和检查。目标已有业务文件时，按[旧工程接入说明](docs/template-usage.md)处理。

## 更新已经使用模板的工程

先提交工程当前改动，再在工程根目录执行：

```powershell
python tools/template_manager.py update --check
python tools/template_manager.py update
python tools/check_template.py --root .
git diff
```

检查无误并运行工程测试后，提交这次模板更新。工程状态始终保留；定制规则尝试三方合并，冲突时不写原文件，按报告手工处理。

[安装、旧工程接入与冲突处理](docs/template-usage.md) · [模板结构与原理](template_readme.md)

## 在新工程启用协作工作台

init 安装的是通用协议骨架。继续在刚建立的新工程目录运行同级工具仓库中的可选工作台，登记、任务和消息都保存在当前工程：

~~~powershell
python ../agent-template-tools/tools/agent_workbench.py --root . serve
~~~

复制终端打印的完整本地 URL 到浏览器。首次打开登记 human 人工入口；可以查看进度、创建任务、暂停、接手和发送反馈。服务需保持运行，Ctrl+C 停止。

让各客户端打开新工程，而后给每个独立会话明确 ID、角色、共同任务 ID 和工作台脚本路径，例如 codex-1／wb-1／wb-2／dsh-1／zcode-1。客户端应先登记、查看状态、认领并读取自己的 context，再开始工作；开发与测试使用不同会话，并行修改使用不同 worktree。直接运行 serve 不会自动连接或唤醒这几个客户端。

[工作台完整用法与接入提示词](https://github.com/duskbreakmist/mulagent-project-template/blob/main/docs/optional/agent-workbench.md)说明检查点接力、独立测试反馈和封存调研。真实客户端额度检测／启动适配仍需单独验证。

母模板还未推送或希望离线安装本地版本时，可用本地 Git 快照：

~~~powershell
$templateSource = (Resolve-Path "../agent-template-tools").Path
python ../agent-template-tools/tools/template_manager.py init --root . --source "$templateSource" --ref main --commit
~~~

这段 PowerShell 先解析这台电脑上的工具目录，再读取它的 main 已提交内容，不包括未提交文件；安装基线会记录本地 source，后续 update 也从这个来源读取。希望以后跟随 GitHub 更新的新工程，应使用前面的默认 GitHub 安装方式。

## 文件树与作用

下面是母模板仓库的活动文件和主要目录。标记含义：默认＝由 manifest 分发；可选＝留在母仓库并显式使用；开发＝母仓库维护／验证，不安装到业务工程。实际维护任务和大量原始归档按目录折叠，避免把维护身份写进新工程说明。

~~~text
agent-project-template/
├── README.md                            # 默认：安装、使用、更新与目录导航
├── AGENTS.md                            # 默认：Agent 的短规则入口
├── template_readme.md                    # 默认：协议结构、原理和完整说明
├── agents_list.md                        # 默认：业务工程参与者登记种子
├── .gitignore                           # 默认：凭据、缓存、运行数据库等忽略规则
├── .gitattributes                       # 默认：文本与换行约定
├── .agents/                             # 默认：协作规则及记录格式
│   ├── PROTOCOL.md                      # 所有权、状态、沟通与 Git 核心规则
│   ├── coordination.md                  # 共享整合者、授权来源与工程默认模式种子
│   ├── template_manifest.json           # 精确分发清单；不是实时任务板
│   ├── guides/
│   │   ├── modes.md                     # 串行、分工协作、独立对照及选择规则
│   │   ├── coordination.md              # 整合者指定、继任、争议与恢复
│   │   ├── documentation.md             # 写作风格、内容结构、排版与约束词
│   │   ├── git.md                       # Git 初始化、worktree 与提交整合
│   │   ├── records.md                   # 任务标识、摘要窗口与归档
│   │   └── tools.md                     # 各客户端加载规则和通信边界
│   ├── tasks/
│   │   ├── README.md                    # 活跃／近期任务索引种子
│   │   ├── TEMPLATE-lite.md             # 单人串行任务格式
│   │   └── TEMPLATE.md                  # 多人、依赖或独立对照任务格式
│   ├── messages/
│   │   ├── README.md                    # 按任务／作者记录讨论的规则
│   │   └── TEMPLATE.md                  # 消息与实际接收确认格式
│   ├── handoffs/
│   │   ├── README.md                    # 何时交接、接手前核对什么
│   │   └── TEMPLATE.md                  # 已完成、剩余、验证与停写状态
│   ├── feedback/
│   │   ├── README.md                    # 使用意见、评审和回传方式
│   │   └── TEMPLATE.md                  # 本人反馈格式
│   ├── plans/README.md                  # 复杂接口计划，按需启用
│   ├── runs/TEMPLATE.md                 # 独立对照的公共条件／轮次格式
│   └── scratch/README.md                # 临时实验区规则
├── docs/
│   ├── CURRENT.md                       # 默认：业务工程当前状态空骨架
│   ├── template-usage.md                # 默认：安装、基线、升级与冲突处理
│   ├── history/README.md                # 默认：旧摘要归档规则
│   ├── history/*.md                     # 开发：既有完成摘要，不默认分发
│   ├── optional/                        # 可选：运行工具说明
│   │   ├── agent-workbench.md           # 五项协作需求、看板与客户端接入
│   │   ├── agent-relay.md               # 原消息队列、收件箱与能力边界
│   │   └── agent-relay-prompt.md        # 原 relay 的跨客户端提示词
│   └── maintenance/                     # 开发：母模板真实维护事实
│       ├── README.md                    # 维护入口、命令与接手方法
│       ├── CURRENT.md                   # 活跃入口与最近完成摘要
│       ├── .gitattributes               # 历史原始字节的局部属性
│       ├── tasks/*.md                   # 各维护任务的 owner、scope、验收
│       ├── runs/*.md                    # 维护侧同源审计／轮次记录
│       ├── history/*.md                 # 旧完成摘要与发布记录
│       ├── migrations/*.json            # 迁移清单、文件来源与哈希
│       └── legacy/                      # 原工程历史与快照，非当前源
├── results/README.md                    # 默认：独立候选与比较结果目录规则
├── tools/
│   ├── template_manager.py              # 默认：init／adopt／update／apply
│   ├── check_template.py                # 默认：只读文件、编码、链接与状态检查
│   ├── agent_workbench.py               # 可选：登记、认领、接力、角色反馈与看板
│   ├── agent_relay.py                   # 可选：原 send／inbox／ack 消息队列
│   ├── start_agent_relay.cmd            # 可选：Windows 收件箱启动入口
│   └── legacy/
│       ├── README.md                    # 开发：旧初始化器保留原因与边界
│       └── agent_bootstrap.py           # 开发：旧初始化器，不用于当前安装
├── tests/                               # 开发：独立验证，不默认分发
│   ├── test_project_template.py         # 完整性、独立复制与只读检查
│   ├── test_template_manager.py         # 安装、升级、三方合并与保护规则
│   ├── test_agent_relay.py              # 原消息队列并发和 HTTP 接口
│   ├── test_agent_workbench.py          # 抢领、接力、角色、调研与人工介入
│   └── test_legacy_bootstrap.py         # 旧初始化器兼容／恢复验证
└── .github/workflows/checks.yml         # 开发：Windows／Linux CI
~~~

安装后还会生成 .agents/template-state.json（应提交的更新基线）；启用工作台后生成 .agent-relay/workbench/state.sqlite3（本地运行状态，忽略）；冲突候选保存在 .agents/template-updates/（本地忽略）。这些是运行时产物，不是分发源码。

## 维护母模板仓库

在下载的母模板仓库目录内，更新该仓库使用：

```powershell
git pull --ff-only
```

这是更新母模板 checkout。使用模板的业务工程通过上面的 template_manager 更新，不对业务工程执行指向模板仓库的 git pull。

母仓库保持安装清单里的登记／任务索引／CURRENT 为空骨架，维护记录放 docs/maintenance/CURRENT.md；业务工程通过自己的实际 task 记录工作。测试与维护记录不在安装清单中。

## 边界

- 安装清单只分发模板组成文件，维护测试／CI 和日志不由安装器写入业务工程。
- 普通任务不用读完整手册或可选对照机制。
- 提交自己的模板基线文件 .agents/template-state.json；锁和冲突备份只存本机。
- 不自动推送、删除工程文件或执行下载的脚本；复制与 GitHub 的 Use this template 本身不等于已建立更新基线。

## 独立开发与可选组件

本仓库独立保存源码、测试、CI 和开发历史。[维护入口](https://github.com/duskbreakmist/mulagent-project-template/blob/main/docs/maintenance/README.md)与[可选消息工具](https://github.com/duskbreakmist/mulagent-project-template/blob/main/docs/optional/agent-relay.md)均不由安装器分发；消息工具必须指定业务主目录，不自动启动 Agent。
