# BOOT005-CODEX 自举审计合理改进与发布验证

- status: done
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
实现提交 b69d6301964ce235bca9e53283021023cbf08d90 已与前序审计一起发布到远端main，官方API读回SHA一致；[该提交双平台CI](https://github.com/duskbreakmist/mulagent-project-template/actions/runs/38132901028)的Ubuntu／Windows模板维护检查与完整测试全部成功。
常规git push遭遇连接重置；官方API上传途中一次SSL中断，有限重试后逐项核对83个对象SHA并非强制更新main，完整保留本地提交作者／时间／父链。不改持久网络配置，不保存或输出凭据，不移动发布标签。收尾仅改维护摘要与本task，不改已验收代码。

## Remaining

本轮实现与发布验收完成。真实AI适配器、完整开发包与自动种子导出未实现；本轮采用可复核的整理步骤，不扩展默认业务安装包。用户可按更新说明使用新工具；旧工具恢复来源时先使用同级最新版安装器。

## 模板备注：业务工程应用判断

2026-10-11 用户询问用于其他工程生产开发是否足够。基于当前33项分发、安装／更新／冲突保护回归与双平台CI，判断已足够作为有人监督的业务开发协作基础；无需先实现自动AI调度或携带母仓库完整开发包。
每个业务工程仍需明确目标／范围、技术栈与构建测试命令、功能验收与自身CI／发布流程；指定实际整合者，并确认所用客户端读取了规则。模板测试覆盖协作工具，不代替业务功能验收。
建议下一步在真实工程完成一个小任务的实现→业务测试→审查→提交→记录闭环，再按实际反馈改模板。尚无本轮指定目标业务目录或业务验收证据，不将该判断写成任意工程已可上线。此次只评估与记录，不改生产逻辑。
