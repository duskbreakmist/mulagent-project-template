# DOC002-CODEX 将组合文档规范纳入分发模板

- status: done
- assignment: accepted
- collaboration_mode: serial
- mode_source: 用户明确要求当前实例把已认可的组合规范写入模板
- owner: codex-docstyle-20261011
- created: 2026-10-11
- updated: 2026-10-11
- base_commit: 73562bb
- version_tag: 无

## Objective

默认分发 Microsoft 主写作参考、Google 开发者补充、Diátaxis 内容结构、GFM 排版和 RFC 约束词规范。入口明确、中文适用和例外边界清楚；新工程安装与已有基线更新均能获得该指南。

## Scope

.agents/guides/documentation.md、.agents/PROTOCOL.md、.agents/template_manifest.json、AGENTS.md、README.md、template_readme.md，以及本人维护 task／CURRENT／必要历史摘要。只改规则和分发清单，不改工具代码、不批量重写历史，不提交他人的 TPL005，不推送。

## Completed

已新增 `.agents/guides/documentation.md`，明确 Microsoft 主写作参考、Google 开发者补充、Diátaxis 内容结构、GFM 排版和 RFC 2119／8174 约束词的职责、中文适配与优先级。AGENTS、协议、README 和模板手册均接入该指南；原有任务／交接格式与历史记录保留自己的语境。

指南加入默认分发清单，文件由 32 项增至 33 项；清单格式仍为 v2，不把格式版本当发布版本。完成维护摘要归档，根登记／任务索引／CURRENT 分发种子保持原样。

## Verification

- 模板检查通过：`TEMPLATE_OK files=33`；AGENTS 仍为 15 行；`git diff --check` 通过。
- 在独立临时 Git 副本中提交候选包并执行新工程 `init --commit`，安装后的 33 项检查通过，指南已分发。
- 从原 32 项基线初始化另一工程，再更新到候选包：检查显示 5 项变化、0 冲突；升级应用成功，安装后 33 项检查通过，业务 README 的 SHA256 保持原值。临时副本已清理。
- 本轮为文档／清单变更，未新增镜像式测试、未重复无关完整代码回归；上述检查不代表自动认证全部外部写作规范。未推送、未运行远端 CI。

## Remaining

本轮实现与本地验证完成；按用户既有安排由用户推送。源仓库发布该提交后，新工程安装和已有工程的正常更新均可获得指南。
