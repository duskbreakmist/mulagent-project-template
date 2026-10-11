# DOC003-CODEX 修正其他电脑的新工程安装说明

- status: done
- assignment: accepted
- collaboration_mode: serial
- mode_source: 用户指出新工程说明不能依赖本机 H 盘路径
- owner: codex-portable-20261011
- created: 2026-10-11
- updated: 2026-10-11
- base_commit: 8ce7f1f
- version_tag: 无

## Objective

让用户在任意电脑的新工程空目录中，从 GitHub 获取工具并初始化当前目录；说明与实际安装器、可选工作台行为一致。

## Scope

README.md、docs/template-usage.md 和本人的维护 task／CURRENT／必要历史摘要。只修正文档示例，不改安装器、分发清单或历史原文；保留 TPL005 暂存。沿用用户此前的模板推送授权发布该修正。

## Completed

将固定 H 盘路径改为“当前空工程目录 + GitHub clone 到同级 ../agent-template-tools + init --root .”。同步更新工作台、本地快照、旧工程 adopt 和母仓库更新示例，明确执行目录和 Python 命令名称。工具仓库放在工程外，保持 init 的空目录前提。

## Verification

- 在系统临时目录模拟另一处工作位置：先在空业务目录 clone 同级工具仓库，再用相对脚本路径、init --root . --commit 初始化；安装后 33 项检查通过，README 含修正后的说明，业务 Git 独立、无模板 origin、状态干净。
- 同级外置工作台 --root . status 通过、登记为空；临时目录已清理。测试用本地候选 Git 快照替代网络源，未把它称为本轮 GitHub 下载验证，也未实机验证其他操作系统。
- 母模板检查通过（33 项）；README 和 docs/template-usage 的固定 H 盘路径检查无匹配，git diff --check 通过；他人 TPL005 暂存 blob 保持原值。
- 本轮仅文档修改，不新增测试、不重复完整代码回归；发布前未运行本次远端 CI，不借用旧 CI 作为本轮验证。

## Remaining

文档与本地验证完成；DOC001 摘要按最近 3 项规则保存到维护历史，保留当时语境。本轮提交沿用既有授权发布，用户在新工程空目录执行 README 的 clone 和 init 两条命令即可安装。
