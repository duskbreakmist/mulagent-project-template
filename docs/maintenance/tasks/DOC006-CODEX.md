# DOC006-CODEX README 非固定版本说明与精简

- status: done
- assignment: accepted
- collaboration_mode: serial
- mode_source: 沿用本会话用户明确选择的单人串行；用户2026-10-18要求添加非固定版本命令说明并精简README
- owner: codex-audit-20261013
- created: 2026-10-18
- updated: 2026-10-18
- base_commit: fbb6e4f1ae9c1c88601515ac2524580d402d4b7a
- version_tag: 无

## Objective

让README清楚区分跟随main与固定标签，提供安装、日常更新和从固定版本切回main的命令；压缩重复说明和完整文件树。

## Scope

根README、本task及维护CURRENT／必要摘要归档和协调入口。不改工具、协议、分发清单、业务种子或发布标签。

## Completed

- 根据管理器实际默认source／ref、引用保存和自动提交逻辑核对命令；新建示例显式使用 `--branch main` 与 `--ref main`。
- 将README组织为快速开始、日常更新、版本选择、可选工作台、文档导航和母模板维护／许可；以导航表替代完整文件树，详细操作继续引用已有文档。
- 明确省略 `--ref` 沿用原引用，切回main须显式选择；保留旧工具升级入口、README归属、业务验收和许可范围。

## Verification

- README由203行缩减至93行，移除完整文件树和重复边界／历史说明，保留已有详细文档入口。
- `python -X utf8 tools/check_template.py --root . --maintenance`：通过，`TEMPLATE_OK files=34`；变更Markdown的本地链接与 `git diff --check` 通过。
- `template_manager.py init --help`／`update --help`和实际实现确认 `--root`、`--ref main`、`--check`、自动提交／手动选项；本地 `v0.2.0` 标签已核实存在。未执行会修改业务工程或访问远端的示例安装／更新命令。
- 纯文档修改，不新增测试或重复运行未变更的功能套件；未将历史CI结果算作本轮验证。默认分发清单和四份状态种子不变。

## Remaining

本轮文档与本地验证已完成；沿用本会话用户对同一仓库main的上传要求，保存提交后正常推送，不移动发布标签。实际推送及CI结果按远端对应提交核对，不递归追加每次文档提交的验证记录。
