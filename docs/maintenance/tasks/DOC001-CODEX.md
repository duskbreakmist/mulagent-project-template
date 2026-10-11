# DOC001-CODEX 新工程使用说明与带职责的文件树

- status: done
- assignment: accepted
- collaboration_mode: serial
- mode_source: 用户向当前实例询问推送、新工程使用和 README 文件树，按本轮范围补齐文档
- owner: codex-docs-20261011
- created: 2026-10-11
- updated: 2026-10-11
- base_commit: a329301
- version_tag: 无

## Objective

实时核实远端状态；让 README 可直接回答如何在新工程安装协议、启动可选工作台和接入多个客户端，并提供 tree 风格的活动文件职责说明。

## Scope

README.md、docs/template-usage.md、docs/optional/agent-workbench.md 及本维护记录／CURRENT／必要摘要归档。保留 32 项分发清单、代码和根状态种子，不提交他人的 TPL005。不把“push 了吗”当作新的推送授权，沿用先前由用户推送的安排。

## Completed

- git ls-remote 实时确认远端 main 为 0df70959dcdbe30d7b3185092d5e38708dad3e7d；本地 a329301，领先 5 项。首次连接被沙箱阻断，获准只读查询后成功。
- 核实 init 只分发 manifest，工作台未在清单；可直接从母仓库运行工作台并把 --root 指向新工程。--source 可选择本地已提交 Git 快照，支持未推送时使用本地版本。
- README 补 tree 风格的活动文件职责表，区分默认、可选与开发；大量原始归档和真实任务按目录折叠，不把维护身份分发到业务工程。
- README 与安装说明补新工程工作台启动及未推送时的本地 --source 安装；工作台说明补四客户端可复制提示词，强调独立会话 ID、共同任务 ID、先登记／认领、按角色读 context 和检查点。

## Verification

- 主目录模板检查通过，TEMPLATE_OK files=32；git diff --check 通过。
- 用母仓库本地 main 已提交快照，在系统临时目录执行 init --source ... --ref main --commit：成功，形成独立 BOOTSTRAP 提交、32 项清单与更新基线，Git 工作树干净、无 origin；可选工作台未被复制。
- 用母仓库工作台 --root 指向上述新工程执行 status：成功，返回空登记／任务／轮次，不创建虚构 Agent。
- 把本轮新 README／安装说明放入最小安装副本再检查：通过，32 项；临时验证目录已核对绝对路径与来源后清理。
- 首次安装冒烟被沙箱临时目录权限阻断，获准沙箱外重跑后成功；不把权限错误当产品缺陷。本轮只改文档，不重复代码全量回归；未推送、未运行远端 CI。

## Remaining

本轮文档交付无剩余；推送仍由用户执行，真实客户端适配仍按 ORCH001-CODEX 的边界另行验收。
