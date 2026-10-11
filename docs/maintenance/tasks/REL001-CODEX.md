# REL001-CODEX v0.2.0 发布

- status: done
- assignment: accepted
- collaboration_mode: serial
- mode_source: 用户“好的帮我完成release”；许可证重新选择后授权使用整合者推荐
- owner: codex-bootstrap-integrator-20261011
- created: 2026-10-11
- updated: 2026-10-11
- base_commit: f290f2a5809cc7e365013132eaad0bc361a0bbfb
- version_tag: v0.2.0
- release_commit: 64a135e45f9a9587c5577b2a2d9c1680e35a78de

## Objective

发布可固定安装、可从旧版升级的 v0.2.0；采用 Apache-2.0，按实际发布提交验证 CI，不移动已有标签。

## Scope

LICENSE、.agents/licenses/、.agents/template_manifest.json、README.md、docs/template-usage.md、tools/template_manager.py、tests/test_template_manager.py，以及本任务、维护 CURRENT／历史和版本说明。默认新增两个许可文件，业务根 LICENSE 保持其自有内容；发布到已授权 origin。

## Completed

许可证推荐经用户授权为 Apache-2.0。安装可固定标签；补 update --ref，成功应用才保存目标引用，预览、失败或冲突不提前切换。

## Verification

安装器30项回归通过（269.265秒）；新用例覆盖CLI固定标签、预览只读、无效引用不写、冲突apply后保存ref和同提交引用切换。35项模板维护检查与diff检查通过。完整回归90项通过（333.470秒，退出0），日志 .test-tmp/REL001-full-tests.log；35项维护检查及staged diff检查通过。

真实本地Git标签演练：v0.2.0空工程安装、已安装工具的只读更新、v0.1.1→v0.2.0升级均通过（32→35项）。五个自有种子、业务源码和自有根LICENSE字节不变，最终独立Git无remote且干净。新副本许可与源码根LICENSE原文一致；没有母tests／维护记录。
发布提交64a135e45f9a9587c5577b2a2d9c1680e35a78de经官方API逐项核对20个Git对象后非强制推送，远端main／新标签SHA读回一致；[Windows／Ubuntu CI](https://github.com/duskbreakmist/mulagent-project-template/actions/runs/38143819730)均成功。
[GitHub Release](https://github.com/duskbreakmist/mulagent-project-template/releases/tag/v0.2.0)已创建并读回：release_id=409693848，draft=false，prerelease=false，标签固定在发布提交。v0.1.0和v0.1.1未移动。
匿名下载GitHub标签源码ZIP，逐项比对35个manifest文件及根LICENSE与本地Git对象均一致；归档SHA256=939bf3ea2db7ec4fdaa3e1ae77bb933ce3b6705ba89cecf1b84a8eba2a407148，临时日志／下载／辅助脚本均未提交。
本机Git HTTPS只读探测仍遇连接重置；单次Windows原生TLS探测连接443失败，均未改持久配置。标准远端Git clone在本机未通过；官方源码归档与远端标签校验已通过，不能把本地Git快照演练冒充远端clone成功。

## Remaining

本轮发布目标完成。Python3.9／macOS、业务工程上线与真实AI无人值守协同仍未验收，已在版本说明标明；后续维护提交不移动v0.2.0。
