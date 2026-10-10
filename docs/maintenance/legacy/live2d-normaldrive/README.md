# live2d_normalDrive

研究 AI 驱动 Live2D／三维角色表达，以及可复用的行为中间层和形态适应。已有研究报告、协作工具及可运行的独立连续驱动软件 NormalDrive 1.0。

## 研究正文

- [GPT 完整学术调研](gpt/research/2026-09-30-avatar-expression-and-morphology.md)：连续表达状态、接口、实时控制、身体适应与实验。
- [WorkBuddy 独立报告](wb/research/embodied-expression-vfs.workbuddy.md)：具身表达虚拟总线研究纲领。
- [多 Agent 对话评估](gpt/research/multi-agent-protocol-review.md)：哪些观点成立、哪里需修正、实际落地和限制。

作者报告不是自动成立的共同结论；WorkBuddy 明列的待核实项已索引到 R002。

## 当前任务与协作入口

| 任务 | 状态／含义 |
| --- | --- |
| [COLLAB003](.agents/tasks/COLLAB003.md) | 同任务独立对照和模式选择 |
| [COLLAB002](.agents/tasks/COLLAB002.md) | 多文件模板拆分 |
| [COLLAB001](.agents/tasks/COLLAB001.md) | 先前协作规则改造 |
| [R001](.agents/tasks/R001.md) | GPT 研究交付完成；原型未实现 |
| [R002](.agents/tasks/R002.md) | WorkBuddy 报告已发现，证据待审；未收到本人确认 |
| [R000](.agents/tasks/R000.md) | 后续综合与原型方案，尚未启动 |

- [AGENTS 入口](AGENTS.md)、[Agent 登记](agents_list.md)、[协作协议](.agents/PROTOCOL.md)。
- [共享 CURRENT](docs/CURRENT.md)、[GPT CURRENT](gpt/CURRENT.md)、[操作手册](docs/collaboration/README.md)。
- [任务模板](.agents/tasks/TEMPLATE.md)、[消息模板](docs/collaboration/TEMPLATE.md)、[gpt 交接](.agents/handoffs/COLLAB001/gpt.md)。
- [可复制的多文件模板 project_templateA](gpt/project_templateA/template_readme.md)：复制目录内全部内容到新工程根目录，包含隐藏文件；入口、规则、格式模板与可选校验工具分开。
- [协作模式与独立对照指南](.agents/guides/modes.md)：模式未指定时询问，独立结果按任务／轮次／Agent 隔离。
- [长期设计决定](docs/decisions/001-task-centered-collaboration.md)。

## 本地操作

```powershell
python tools/agent_bootstrap.py --root . --check
python -m unittest discover -s tests -v
git config --get agent.coordinationRoot
git status --short
git log --oneline --decorate
```

需要 Python 3.9+ 与支持硬链接的文件系统；本机测试使用 Python 3.13.8。本地 Git 已建立 main，未配置远程。并行开发按任务创建真正的 worktree，并从指定主目录读实时任务；文件协议不会自动唤醒外部应用。

## NormalDrive 独立软件（ND002）

默认DSFlash生成我方对白，GPT-SoVITS配音，AudioWorklet样本时钟驱动口型、微笑、眨眼、头眼；暂不STT。

- [使用说明](docs/software/README.md)、[接口](docs/software/API.md)、[实现记录](docs/software/CURRENT.md)、[验证结果](docs/software/verification.json)。
- Windows便携包：[启动NormalDrive](release/NormalDrive-1.0.0-b4fcc96b/启动NormalDrive.cmd)，附Node运行时，无需npm安装；模型与语音运行包仍用本机安装。
- 源码运行：`node src/server.mjs --open`；测试：`node --test tests/normaldrive-*.test.mjs`。
- [ND002任务](.agents/tasks/ND002.md)、[本人移交](.agents/handoffs/ND002/codex-normal-1.md)。前期ND001未实现描述保留为历史状态。
