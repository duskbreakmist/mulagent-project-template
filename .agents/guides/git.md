# Git 与并行整合（按需阅读）

## 默认纳入 Git 管理

除非用户明确要求不使用 Git，新工程由 integrator 在第一次实质修改前检查并建立版本管理。模板文件不会自动执行命令。

```powershell
git rev-parse --show-toplevel
git status --short
```

已有仓库保留分支、身份和配置；若项目位于父仓库中，先明确真实仓库根，避免误建嵌套仓库。确认尚无仓库后才在实际主目录执行：

```powershell
git init -b main
git config --local agent.coordinationRoot (Get-Location).Path
git status --short
```

先合并／核对 .gitignore，排除凭据、缓存和本地运行状态；模型、贴图等大型资产根据实际需求选择资产管理或 LFS。不要盲目 git add .。实际首个任务与模板骨架可作为明确范围的初始基线提交。

Git 不可用或提交身份缺失时保留产出，明确“尚未提交”并说明原因；不捏造姓名／邮箱、已保存提交或历史，不把无提交当作完成 Git 保存。当前身份沿用仓库／用户真实配置，不因 Agent 名称反复更改共享身份。

主目录绝对路径只存本地配置，不进入共享模板。普通 worktree 共享 Git 配置，独立 clone 需另行约定主目录／状态同步。

## 每次交付保存

1. 运行相关验证，读取 git status --short 并确认他人未提交内容。
2. 显式 git add 本任务文件，读取 git diff --cached，确认范围和敏感／运行文件未进入索引。
3. 提交有意义阶段与交付，格式 [TASK-ID][agent-id] summary；正文可附 Agent / Task / Role trailer。git log -1 核实真实提交；不能只改 Markdown 却声称版本已保存。
4. 工程要求版本标签时记录真实 version_tag／release_commit；不默认打标签、配置远程、推送或发布。Git 提交来源标签不等于身份认证。

## 工作树与整合

接受任务且基线已提交后，integrator 可使用：

```powershell
git worktree add -b agent/worker/DEV001 .worktrees/worker-DEV001 main
git worktree list
```

替换实例、任务和基线；实际打开隔离路径。只建分支不隔离当前目录，worker 读取指定主目录的实时 task。实现候选各用独立工作树，共享 checkout 的 Git 操作由一人串行。

worker 提供基线、提交和证据；integrator 审查后 merge / cherry-pick 并验证整体，自动合并成功不保证语义一致。不默认删除他人工作树／分支，不使用 force 丢弃未知修改。
