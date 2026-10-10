# 多 Agent 工程协作模板

为单人任务、跨工具分工、接力和独立对照提供简洁的仓库规则。短 AGENTS 入口、按需指南、独立任务／反馈记录；不自动派发其他模型或运行后台服务。

## 新建本地工程

已下载本仓库时，用一条命令从 Git 拉取最新模板并建立独立工程：

```powershell
python H:\Project\agent-project-template\tools\template_manager.py init --root H:\Project\my-new-project --commit
```

目标必须为空；需要 Python 3.9+ 与 Git，提交沿用你已有的真实 Git 身份。新工程有自己的历史，不把模板仓库设为它的 origin。

尚未下载工具时先执行一次：

```powershell
git clone https://github.com/duskbreakmist/mulagent-project-template.git H:\Project\agent-project-template
```

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

## 维护母模板仓库

H:\Project\agent-project-template 是母模板工作目录，它自身接收 GitHub 更新使用：

```powershell
git -C H:\Project\agent-project-template pull --ff-only
```

这是更新母模板 checkout。使用模板的业务工程通过上面的 template_manager 更新，不对业务工程执行指向模板仓库的 git pull。

母仓库保持安装清单里的登记／任务索引／CURRENT 为空骨架，维护记录放 docs/maintenance/CURRENT.md；业务工程通过自己的实际 task 记录工作。测试与维护记录不在安装清单中。

## 边界

- 安装清单只分发模板组成文件，维护测试／CI 和日志不由安装器写入业务工程。
- 普通任务不用读完整手册或可选对照机制。
- 提交自己的模板基线文件 .agents/template-state.json；锁和冲突备份只存本机。
- 不自动推送、删除工程文件或执行下载的脚本；复制与 GitHub 的 Use this template 本身不等于已建立更新基线。

## 独立开发与可选组件

本仓库独立保存源码、测试、CI 和开发历史，不再依赖 Live2D 工程。[维护入口](https://github.com/duskbreakmist/mulagent-project-template/blob/main/docs/maintenance/README.md)与[可选消息工具](https://github.com/duskbreakmist/mulagent-project-template/blob/main/docs/optional/agent-relay.md)均不由安装器分发；消息工具必须指定业务主目录，不自动启动 Agent。
