# REL001-CODEX v0.2.0 发布

- status: in_progress
- assignment: accepted
- collaboration_mode: serial
- mode_source: 用户“好的帮我完成release”；许可证重新选择后授权使用整合者推荐
- owner: codex-bootstrap-integrator-20261011
- created: 2026-10-11
- updated: 2026-10-11
- base_commit: f290f2a5809cc7e365013132eaad0bc361a0bbfb
- version_tag: 待验证 v0.2.0

## Objective

发布可固定安装、可从旧版升级的 v0.2.0；采用 Apache-2.0，按实际发布提交验证 CI，不移动已有标签。

## Scope

LICENSE、.agents/licenses/、.agents/template_manifest.json、README.md、docs/template-usage.md、tools/template_manager.py、tests/test_template_manager.py，以及本任务、维护 CURRENT／历史和版本说明。默认新增两个许可文件，业务根 LICENSE 保持其自有内容；发布到已授权 origin。

## Completed

许可证推荐经用户授权为 Apache-2.0。安装可固定标签；补 update --ref，成功应用才保存目标引用，预览、失败或冲突不提前切换。

## Verification

安装器30项回归通过（269.265秒）；新用例覆盖CLI固定标签、预览只读、无效引用不写、冲突apply后保存ref和同提交引用切换。35项模板维护检查与diff检查通过。完整回归正在执行；版本快照安装／旧版升级、发布提交CI与GitHub release读回待完成。

## Remaining

完成源码许可、文档、测试、提交、推送、CI、固定标签演练与正式 release。
