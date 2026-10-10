# COLLAB002 拆分可复制的多文件工程模板

- status: done
- assignment: accepted
- owner: gpt
- integrator: gpt
- reviewers: 单 Agent 模板改造自检
- parent: 无
- dependencies: COLLAB001
- created: 2026-09-30
- updated: 2026-09-30
- base_commit: 30b1883

## Objective

按用户要求把单文件 AGENTS 拆成按需阅读的多文件模板，放到 gpt/project_templateA，并提供 template_readme.md 说明使用、目的、原理和注意事项。

## Scope

gpt/project_templateA/、gpt/templates/AGENTS.md、AGENTS.md、README.md、docs/collaboration/README.md、docs/decisions/001-task-centered-collaboration.md、gpt/research/multi-agent-protocol-review.md 的更新提示、tests/、本任务及交接、docs/CURRENT.md、gpt/CURRENT.md。既有研究正文和当前协作初始化器保留。

## Deliverables

18 文件的独立可复制模板；短 AGENTS、核心协议、Git 指南、空登记与任务骨架、消息／交接模板、CURRENT、忽略与换行规则、静态清单、独立可选只读检查工具；template_readme.md。

## Completed

旧单文件改为导航，工程入口改指向新模板。模板直接带好结构，无需运行初始化程序；Python 仅作可选检查。核心规则、手册、脚本和格式分开，普通 Agent 不必每轮全文读取。

## Remaining

本次交付无剩余。不同工具的实际规则自动加载与跨应用通信不在本次复制／拆分验证范围。

## Problems

复制隐藏目录时可能漏 .agents；已有工程需合并规则，不能覆盖真实登记／进度。单主目录仍依赖实际 integrator 串行维护，未部署权限或调度服务。

## Verification

python -m unittest discover -s tests -v：21 项通过，其中新模板 10 项，覆盖独立复制、只读、不覆盖实际状态、漏隐藏文件、路径逃逸、异常编码、重复清单与版本错误。

python gpt/project_templateA/tools/check_template.py --root gpt/project_templateA：TEMPLATE_OK files=18。40 份 Markdown、63 处本地链接与 git diff --check 通过；两份原研究报告 SHA256 未变。具体提交见 git log。

## Handoff

.agents/handoffs/COLLAB002/gpt.md；没有外部接收回执。
