# 模板开发工程

本仓库是协作模板唯一开发位置。根目录保存分发骨架，tools/ 保存管理器，tests/ 保存独立验证，GitHub Actions 运行检查；原 Live2D 工程只消费当地规则。

实际维护任务在本目录 tasks/ 与 CURRENT.md；根 agents_list.md、.agents/tasks/README.md、docs/CURRENT.md 保持空骨架，不把维护者状态分发给新工程。Git 本地 agent.coordinationRoot 指向本仓库，与业务工程分离。

原开发记录在 legacy/，旧初始化器在 tools/legacy/；可选消息工具在 tools/agent_relay.py 与 docs/optional/，都不在默认安装清单中。消息工具必须显式传入目标工程 --root，不自动派发或接管 Agent。

维护命令：

~~~powershell
python tools/check_template.py --root .
python -m unittest discover -s tests -v
git diff --check
~~~

交付前显式暂存、审阅并提交。改变分发文件时维护 .agents/template_manifest.json；修改历史、测试或可选工具，不扩大安装清单。
