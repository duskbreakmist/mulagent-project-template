# ENG001-CODEX 业务工程约定入口与交付闭环

- status: done
- assignment: accepted
- collaboration_mode: serial
- mode_source: 用户“继续”推进上一轮提出的工程约定入口与实际小任务验收；沿用合理改动／推送测试授权
- owner: codex-bootstrap-integrator-20261011
- created: 2026-10-11
- updated: 2026-10-11
- base_commit: eed3c43
- version_tag: 无

## Objective

业务代码修改前有可发现的工程约定，未知项可以先调查；明确TEMPLATE_OK验证范围；独立最小业务工程完成安装、真实功能／业务测试、审查提交和状态记录，再发布核对CI。

## Scope

README.md、AGENTS.md、.agents/tasks/TEMPLATE-lite.md／TEMPLATE.md、docs/template-usage.md、template_readme.md、tests/test_template_manager.py；维护task／CURRENT／必要历史。保持分发33项，工程约定落在业务README或其引用文档，不新增第二套任务板、不固定所有工程技术栈。

## Completed

README增加六项工程约定入口，AGENTS要求业务代码修改前读取实际约定；两种task格式要求引用约定与实际验收命令，未知项可先调查。既有README受保护，接入说明明确手工补链接，不整份覆盖。
README、接入说明与手册明确TEMPLATE_OK范围；不把已填status合法性／模板语法完整性当成业务功能、跨文件同步或上线证明。分发仍33项，无新增通用脚手架或固定技术栈。
新增真实CLI业务闭环回归：已安装工具init --commit另一空工程，BOOTSTRAP／独立Git／协作根／无母tests核对；填写实际工程约定，生成lite task，标签功能先失败再修复，业务3项和语法检查通过，核对staged diff，收尾task／索引／CURRENT并显式提交，最终2提交且干净无remote。

## Verification

本轮 python -m unittest discover -s tests -v：86项通过，197.479秒，退出0；日志 .test-tmp/ENG001-full-tests.log。新闭环内部业务3项最终通过，预期失败已被观察；最后隔离业务提交c83b02302b3a3607fa7e16f287678b6886c1e9df，临时副本随后由夹具清理。
可复现新场景：python -m unittest discover -s tests -p test_template_manager.py -k business_task_delivery -v；最终CLI版本定向用例通过（10.508秒）。模板／维护检查33项、AST与diff检查通过。执行环境Windows/Python3.13.8/Git2.47.1，隔离Git／业务代码用已获准沙箱外方式执行。
apply_patch对已核验的普通README两次误报reparse point；文件属性和Path.resolve确认范围／无符号链接后，用限域替换脚本核对全文、唯一目标段落与并发字节完成文档改动。未将编辑工具限制算成业务缺陷。
示例仅验证单fixture执行的最小工程流程，不宣称真实产品上线、独立AI审查、业务CI或部署；业务工程仍需自身验收。
实现提交57ef7f18155ff59644e701cead69a946c7f919c7已原样发布到main，官方API读回SHA一致；[Windows／Ubuntu CI](https://github.com/duskbreakmist/mulagent-project-template/actions/runs/38139625505)模板维护检查与完整回归均成功。复用官方API通道逐项核对24对象，不强推、不移动标签。发布辅助引号处理失败时，远端SHA校验已安全阻止更新；修正辅助文件后发布成功。

## Remaining

本轮目标完成；收尾仅保存维护记录。生产产品的具体配置／上线、真实AI自动协同不在本轮范围。实际业务工程须填写自身约定并运行自己的验收命令。
