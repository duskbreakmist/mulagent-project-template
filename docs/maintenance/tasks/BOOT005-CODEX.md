# BOOT005-CODEX 自举审计合理改进与发布验证

- status: in_progress
- assignment: accepted
- collaboration_mode: serial
- mode_source: 用户授权当前整合者“完成你认为合理的改动，并推送测试”
- owner: codex-bootstrap-integrator-20261011
- created: 2026-10-11
- updated: 2026-10-11
- base_commit: 6d5a96f
- version_tag: 无

## Objective

落实审计中已复核且收益明确的验证、维护协调和本地来源恢复改进；运行回归、提交推送并核对该提交的双平台 CI。

## Scope

tools/check_template.py、tools/template_manager.py、相关 tests、.github/workflows/checks.yml；AGENTS.md、template_readme.md、docs/template-usage.md、维护 README／COORDINATION／CURRENT 与必要历史摘要。保持默认分发33项、不写真实身份到根种子。

## Completed

检查器／安装器增加v2最小核心锚点，拒绝维护／测试／CI／legacy资产进入业务清单；checker只解析受管理Python语法而不执行。显式 --maintenance 检查母仓库入口、记录链接与维护task状态，CI已接入。
本地source在init／adopt保存为调用时绝对路径；update --source支持明确恢复来源，预览保持只读，实际成功后才更新基线；旧相对来源不再按新的cwd猜仓库。URL／scp来源保留原含义。
新增维护COORDINATION并接入入口，根状态种子与33项分发集保持不变。文档补工程移动重新绑定、本地来源恢复、业务副本种子整理／候选验收步骤。checker测试夹具仅复制实际分发集，新增真实init→checker串联与负面回归。

## Verification

本轮完整 unittest 85项全部通过（204.063秒，退出0），日志 .test-tmp/BOOT005-full-tests.log；含新增10项回归。checker首轮22项、manager首轮24项通过；随后完整回归覆盖最终核心锚点拒绝用例。
python tools/check_template.py --root . --maintenance：TEMPLATE_OK files=33；AST／新链接与git diff检查通过。Python3.13.8、Git2.47.1、Windows，隔离临时Git／本地HTTP验证在获准沙箱外执行；未访问真实AI账户。
远端main读取为8d2645f，准备显式保存并推送本轮与前序已完成审计提交，CI尚待本轮实际SHA核对。

## Remaining

本地实施与验证完成；待保存推送、核对双平台CI并收尾记录。真实AI适配器、完整开发包与自动种子导出未实现；本轮采用可复核的整理步骤，不扩展默认业务安装包。
