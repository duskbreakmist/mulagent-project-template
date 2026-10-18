# 多 Agent 工程协作模板

为单人开发、跨工具接力、worktree 分工和独立对照提供仓库规则：短 AGENTS 入口、按需指南、任务与交接记录，以及保护业务定制的安装更新工具。

业务工程拥有独立 Git 历史。AI 按实际需求与实现维护业务 README 的项目概述、功能和运行方式；模板使用说明保存在 `template_readme.md`。

## 快速开始：跟随 main（非固定版本）

需要 Python 3.9+、Git 和自己的真实 Git 提交身份；若系统使用 `python3`，替换下面的 `python`。在**新的空业务工程目录**执行，工具仓库放在同级目录：

```powershell
git clone --branch main https://github.com/duskbreakmist/mulagent-project-template.git ../agent-template-tools
python ../agent-template-tools/tools/template_manager.py init --root . --ref main --commit
python tools/check_template.py --root .
```

`--ref main` 表示跟随来源仓库的 main 分支，每次更新取得该分支的新提交，可能包含尚未发布为标签的改动。init 创建独立业务 Git 基线，并生成供 AI 维护的业务 README。

同级工具目录已存在时，先确认工具仓库位于 main 分支并执行 `git -C ../agent-template-tools pull --ff-only`，再从 init 命令继续。已有业务文件时使用[旧工程接入流程](docs/template-usage.md#4-已经复制旧模板或用-github-模板按钮创建的工程)。

## 日常更新业务工程

先保存现有业务改动，确认工作区与暂存区干净，再在业务工程根目录执行：

```powershell
python tools/template_manager.py update --check
python tools/template_manager.py update
python tools/check_template.py --root .
```

当前 main 版本的 `update` 默认自动提交本次变更的模板文件与 `.agents/template-state.json`。无更新时不创建空提交；冲突时保留报告，停止应用。更新后审阅提交并运行业务工程自己的测试。

需要先审阅再提交时，使用 `python tools/template_manager.py update --no-commit`。AI 读取规则后，也可在聊天中输入 `update` 请求执行更新。工具不自动推送；业务 README、实际登记、任务与进度由业务工程保留。

## 版本选择与切换

| 选择 | 参数 | 后续不带参数的 update |
| --- | --- | --- |
| 非固定版本 | `--ref main` | 跟随来源仓库的 main 新提交 |
| 固定发布版本 | `--ref v0.2.0` | 继续使用该标签 |

**从固定版本切换为非固定版本**，在业务工程根目录执行：

```powershell
python tools/template_manager.py update --ref main --check
python tools/template_manager.py update --ref main
```

成功应用后保存 main 引用，以后直接运行 `update` 即可。省略 `--ref` 会沿用已保存的引用，不能让原本固定的标签自动变成 main。

旧工程内的工具不支持 `--ref` 或自动提交时，先取得最新 main 工具，再使用同级工具升级：

```powershell
python ../agent-template-tools/tools/template_manager.py update --root . --ref main --check
python ../agent-template-tools/tools/template_manager.py update --root . --ref main
```

需要固定版本时，在另一个空业务工程目录使用已获取的工具：

```powershell
python ../agent-template-tools/tools/template_manager.py init --root . --ref v0.2.0 --commit
```

固定版本内的工具行为以对应版本为准。来源切换、离线安装、冲突处理和手动提交见[完整安装与更新说明](docs/template-usage.md)。

## 可选协作工作台

在业务工程根目录运行同级工具中的工作台：

```powershell
python ../agent-template-tools/tools/agent_workbench.py --root . serve
```

打开终端打印的完整本地 URL，登记实例并创建／认领任务。工作台提供进度、消息、检查点和人工接手；服务需要保持运行，各客户端的启动与额度检测仍需显式适配。详见[工作台用法与接入提示词](docs/optional/agent-workbench.md)。

## 文档与目录

| 入口 | 内容 |
| --- | --- |
| [AGENTS.md](AGENTS.md) | AI 工作入口与必需规则 |
| [template_readme.md](template_readme.md) | 模板使用须知、工程约定与协作原理 |
| [docs/template-usage.md](docs/template-usage.md) | 安装、旧工程接入、版本切换与冲突恢复 |
| [.agents/](.agents/PROTOCOL.md) | 核心协议、按需指南和任务／交接格式 |
| [.agents/template_manifest.json](.agents/template_manifest.json) | 默认分发清单；仅包含通用骨架 |
| [docs/maintenance/](docs/maintenance/README.md) | 母模板开发、测试与维护记录 |

默认分发 34 项，init 另生成业务 README。母仓库介绍、测试、CI、维护历史和可选工作台不由安装器复制到业务工程。`TEMPLATE_OK` 表示模板检查通过，业务功能仍需自身构建与测试验收。

## 母模板维护与许可

更新母模板工具仓库时，在该仓库的 main 分支执行 `git pull --ff-only`；更新业务工程使用前面的 `template_manager.py update`。源码与测试位于 `tools/`、`tests/`，维护流程见[维护入口](docs/maintenance/README.md)，文档按[写作规范](.agents/guides/documentation.md)维护。

模板采用 [Apache-2.0](.agents/licenses/Apache-2.0.txt)，范围见[许可说明](.agents/licenses/README.md)。许可文件安装到 `.agents/licenses/`，保留业务工程自己的根 LICENSE。
