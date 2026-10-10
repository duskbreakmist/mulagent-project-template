# COLLAB003 增加同任务独立对照与模式选择

- status: done
- assignment: accepted
- collaboration_mode: serial
- mode_source: 本次明确的单 Agent 规则维护范围
- mode_question_status: not_needed
- participants: gpt
- run_id: 无（本次没有启动对照实验）
- output_root: gpt/project_templateA/ 与当前工程协作规则
- owner: gpt
- integrator: gpt
- reviewers: 本次模板维护自检
- parent: 无
- dependencies: COLLAB002
- created: 2026-10-01
- updated: 2026-10-01
- base_commit: dc97030

## Objective

支持多个 Agent 独立处理同一目标并比较，而不是只支持接力或子任务；模式不明确时由 integrator 通过可用交互工具询问用户，明确时不重复问。

## Mode Decision

本次只维护规则与模板，不启动外部 Agent 或研究对照。已经发起后续 R000 模式偏好选择，尚未收到具体模式回答；用户“继续”授权本次收尾，不代表选中某一种模式。

## Scope

AGENTS、.agents/PROTOCOL、模式指南、任务／RUN 模板、results/README、gpt/project_templateA 对应文件和清单、操作说明／ADR、现有 R000 的待答字段、相关测试、CURRENT、本任务与交接；不改原研究报告。

## Deliverables

三种 collaboration_mode；按任务／轮次／Agent 的正式产出约定；首次提问／复用／待答流程；独立提交与后续比较规则。

## Completed

当前工程与复制模板均有模式入口。模式与进度分开；独立对照允许同任务多人完整作答，各自子目录、固定公共输入、首稿不互读、提交后统一比较。实现候选仍各用 worktree。

## Remaining

本次修改无剩余；后续模式选择待用户明确回答，不影响本次完成。

## Problems

文本无法强制客户端弹窗，也不实现跨应用派发或盲测权限隔离。历史报告保留，不能将过去已互相阅读的上下文称作严格独立实验。

## Verification

21 项 unittest 通过，模板完整性检查 TEMPLATE_OK files=21。50 份 Markdown、87 处本地链接与 Git diff 检查通过，两份原报告 SHA256 未变。另有 relay 相关工作保留，不纳入本次提交。

## Handoff

.agents/handoffs/COLLAB003/gpt.md；未向外部应用发送消息。
