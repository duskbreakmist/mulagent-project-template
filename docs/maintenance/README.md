# 模板开发工程

本仓库是协作模板唯一开发位置。根目录保存分发骨架，tools/ 保存管理器，tests/ 保存独立验证，GitHub Actions 运行检查；原 Live2D 工程只消费当地规则。

实际维护任务在本目录 tasks/ 与 CURRENT.md；根 agents_list.md、.agents/tasks/README.md、docs/CURRENT.md 保持空骨架，不把维护者状态分发给新工程。Git 本地 agent.coordinationRoot 指向本仓库，与业务工程分离。

原开发记录在 legacy/，旧初始化器在 tools/legacy/；可选消息工具在 tools/agent_relay.py 与 docs/optional/，都不在默认安装清单中。消息工具必须显式传入目标工程 --root，不自动派发或接管 Agent。

面向额度接力、功能并行、职责分离、同题调研与人工介入的[协作工作台原型](../optional/agent-workbench.md)位于 tools/agent_workbench.py。它提供实际登记、任务认领、消息与本地看板；真实客户端启动／额度检测通过显式适配器接入。该组件同样不默认分发，不把模拟接力当成四客户端已经实机接入。

维护命令：

~~~powershell
python tools/check_template.py --root .
python -m unittest discover -s tests -v
git diff --check
~~~

交付前显式暂存、审阅并提交。改变分发文件时维护 .agents/template_manifest.json；修改历史、测试或可选工具，不扩大安装清单。

## 让其他 AI 接手开发

在 Codex、WorkBuddy 或其他工具中打开此仓库目录；不能假定它自动读取 AGENTS。新会话可粘贴：

~~~text
这个仓库是协作模板开发工程。
先读 AGENTS.md、docs/maintenance/README.md 和 docs/maintenance/CURRENT.md，再读相关实现与测试。
只做我本轮指定的改进。实际维护任务写 docs/maintenance/tasks/<TASK-ID>.md；单人任务在该文件记录 owner、scope、进度和验证，不把维护身份或真实任务写入根分发种子。
保持安装清单只包含通用骨架。完成后运行相关检查，更新维护 CURRENT，显式暂存、审阅并提交；GitHub 推送由用户执行。
~~~

先查看 tasks/TPL002.md 和最新 Git 历史。新任务用独立 ID；根 .agents/tasks 中的格式模板可参考，但实际 task 保存到维护目录。普通单人修改不用登记多个重复进度表；若并行维护，按共同约定写 scope、单一整合者和独立 worktree。

## 应用到新工程

业务工程推荐从 README 的 init 命令安装，自动创建独立 Git 基线；本目录维护历史、测试和可选工具不会默认进入业务工程。业务工程以后使用 update，不回传自己的 task、CURRENT 或登记表作为模板源码。

## 提交和推送

本轮改动已在本地提交。用户在本目录运行 git push origin main；推送前 git status 确认没有意外文件，推送后查看 GitHub Actions。已发布版本标签不移动。
