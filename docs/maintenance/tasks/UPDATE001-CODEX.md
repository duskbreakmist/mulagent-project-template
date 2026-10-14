# UPDATE001-CODEX 自动提交模板更新与业务 README 维护

- status: done
- assignment: accepted
- collaboration_mode: serial
- mode_source: 沿用本会话用户明确选择的单人串行；用户2026-10-14要求Python更新命令自动提交，并由AI维护业务README概述
- owner: codex-audit-20261013
- created: 2026-10-14
- updated: 2026-10-14
- base_commit: 6031d210f172a946fc147e2e9473283581382a5d
- version_tag: 无

## Objective

`python tools/template_manager.py update` 成功应用后自动保存模板文件与基线的Git提交；AI按实际项目持续维护README概述。

## Scope

管理器与对应回归、AGENTS、模板使用须知、根README和更新说明；本目录task／协调／CURRENT及必要摘要归档。默认分发清单不扩容。终端直接使用现有Python命令，用户最新澄清后不安装全局shell命令。

## Completed

读取更新计划、应用回滚、Git保护和README生成／迁移逻辑；采用CLI默认自动提交、`--no-commit`保留手动流程，Python内部API默认行为保留以兼容既有调用。

- 管理器应用前检查Git根、暂存区、进行中的Git操作与真实提交身份；成功后只暂存计划中的模板路径及状态基线，用字面路径与限定路径提交，输出真实SHA。
- 预览、无更新及冲突不提交；仅基线变化也保存Git版本。`apply --commit`支持已审阅候选，省略该选项保持手动流程。提交阶段失败保留已应用文件、基线、暂存与报告供恢复。
- AGENTS约定业务工程聊天输入 `update` 时调用默认Python命令，并要求AI首次明确需求及功能／目录／命令变化后主动维护真实业务README；更新器继续保护已有README，初始化栏目改为项目概述、运行与验证及工程约定。
- 新增九项实际临时Git／CLI回归；包括方括号文件名、外部业务暂存隔离、非Git工程手动模式及提交失败仿真。未将真实AI客户端自动遵循文档规则冒充实机验收。

## Verification

- 初版管理器43项回归通过（355.516秒）。补强字面路径与非Git用例后，在Windows／Python 3.13.8执行完整113项回归（366.283秒）；112项通过，唯一失败为AGENTS从15行增至17行的短入口断言，生产更新逻辑及其44项管理器用例全部通过。
- 将两项新增规则合并回既有入口、详细要求保留在按需说明后，`python -X utf8 -m unittest discover -s tests -p test_project_template.py -v`：25项全部通过（14.347秒）。此后仅收尾文档变化；未再次重复运行未受影响的完整套件。日志 `.test-tmp/UPDATE001-full-tests.log` 与 `.test-tmp/UPDATE001-protocol-retest.log` 忽略保存。
- 维护检查 `TEMPLATE_OK files=34`、修改文档本地链接及两份Python的3.9语法解析通过；语法解析不代替3.9运行时测试。本地阶段未取得远端CI与Linux／Python 3.9运行时结果，追加推送后的实际结果见下节。
- 已审查实际实现与文档diff；根四份状态种子内容不变，默认分发仍为34项。旧CURRENT完成摘要保留到维护history；按项目规则显式暂存并保存本地提交。

## Remaining

本轮实现、上传与远端四组合CI验收已完成。真实AI客户端是否自动读取并执行新规则需在业务工程中验收。现有业务工程及已发布标签未改，新行为须使用新版工具与规则。

## 推送与 CI（2026-10-14）

- 用户明确要求上传刚完成的新功能；实现提交 `923f2324fa03cc38ef03d5bbf471bb404b400484` 已正常推送到 `https://github.com/duskbreakmist/mulagent-project-template` 的main。
- 标准HTTPS推送先后超时／连接重置；读取Windows现有系统代理后，仅对本次命令使用 `git -c http.proxy=http://127.0.0.1:7197 -c http.version=HTTP/1.1 push origin main` 成功，没有修改持久Git配置。
- [实现CI](https://github.com/duskbreakmist/mulagent-project-template/actions/runs/38510819401)对应923f232；四组全部成功，逐组日志确认113项测试与 `TEMPLATE_OK files=34`，入口长度修正也在完整套件中重新通过。

| 环境 | 实际Python | 完整unittest |
| --- | --- | --- |
| Ubuntu | 3.9.25 | 113项，22.841秒，OK |
| Ubuntu | 3.13.16 | 113项，30.956秒，OK |
| Windows | 3.9.13 | 113项，237.171秒，OK |
| Windows | 3.13.15 | 113项，252.118秒，OK |

仅补充维护授权与验收记录后再正常推送，交付前按最终SHA核对CI；不递归追加每次文档提交的CI记录。
