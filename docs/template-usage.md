# 安装与后续更新

## 1. 获取工具和创建新工程

```powershell
git clone https://github.com/duskbreakmist/mulagent-project-template.git H:\Project\agent-project-template
python H:\Project\agent-project-template\tools\template_manager.py init --root H:\Project\my-new-project --commit
```

已有 H:\Project\agent-project-template 时跳过 clone。init 每次从 Git 读取最新 main，也可用 --ref v0.1.1 固定已发布版本。目标须为空（新建的无历史空 Git 仓库也可），已有工程不用 init。

默认初始化独立 Git 并设置本地协作根。--commit 保存初始模板提交；身份缺失会明确报错，不捏造姓名／邮箱，已生成文件保留。--no-git 仅在你明确不需要版本管理时使用，不能与 --commit 同时指定。安装器不设置业务工程 origin，不推送。

### 使用未推送的本地版本

--source 也接受本地 Git 仓库路径；--ref main 读取已提交快照，不包括工作区未提交内容：

~~~powershell
python H:\Project\agent-project-template\tools\template_manager.py init --root H:\Project\my-new-project --source H:\Project\agent-project-template --ref main --commit
~~~

基线会记录这个本地 source，后续 update 沿用它；不会自动切换成 GitHub 来源。需要长期跟随 GitHub 的新工程优先使用默认安装方式。init 目标须位于母仓库外，避免创建嵌套仓库。

### 同时使用协作工作台

默认清单不包含可选工作台；可从母仓库运行它，将 --root 指向业务工程：

~~~powershell
python H:\Project\agent-project-template\tools\agent_workbench.py --root H:\Project\my-new-project serve
~~~

所有客户端使用同一个业务 --root，但使用不同会话 ID 和自己的角色／worktree。先登记并领取任务，再读专属 context；开启网页不等于客户端已经连接。可复制提示词见[工作台接入说明](https://github.com/duskbreakmist/mulagent-project-template/blob/main/docs/optional/agent-workbench.md)。

## 2. 日常更新业务工程

先 git status 并提交现有工作，然后：

```powershell
python tools/template_manager.py update --check
python tools/template_manager.py update
python tools/check_template.py --root .
git diff
```

--check 对工程只读，不建锁、状态或报告；仍会访问 Git，并在临时目录读取快照。状态基线在 .agents/template-state.json，包含 source、ref、提交与各文件基线哈希，需要随业务工程 Git 保存。改 ref 前明确选择已存在分支／标签，不把清单的格式 version 当发布版本。

保护规则：

| 类型 | 更新行为 |
| --- | --- |
| 登记表、coordination、任务索引、CURRENT、业务 README | 已存在就保留；空工程安装时才写初始骨架 |
| 真实 task／消息／交接／反馈／结果／历史 | 不从模板覆盖或删除；上游清单混入这些记录会被拒绝 |
| 规则／指南／格式模板／工具 | 未定制则更新，定制时用旧基线、本地与上游做三方合并 |
| 本地删除的已管理文件 | 保留删除，不自动恢复 |
| 上游删除的文件 | 不自动删本地，报告提示，由你确认 |
| 原来不存在的新组成文件 | 可新增；已有同名非基线文件形成冲突，不直接覆盖 |

三方文本合并采用 [git merge-file](https://git-scm.com/docs/git-merge-file)。它不能保证语义正确；更新后仍审阅 Git diff 和运行工程验证。工具不运行远端脚本，也不代你提交更新。

## 3. 发生冲突

退出码 2 表示有冲突：本轮所有模板文件与基线均不应用，报告位于 .agents/template-updates/<时间-提交-编号>/。其中 current／base／upstream 保存输入，proposed 是候选合并稿；未知基线时 proposed 只是上游候选，必须自行保留本地需求。

编辑 proposed 中的冲突文件，保留需要的双方改动、移除冲突标记，再执行：

```powershell
python tools/template_manager.py apply --plan ".agents/template-updates/<报告目录>/plan.json"
```

没有额外确认弹窗，此命令表示你已经审查候选。工具验证文件与状态自生成计划后未改变，拒绝仍带冲突标记、非法 JSON／Python 语法的候选。随后检查模板与工程，提交模板更新和基线。

生成报告后若原文件改变，重新运行 update 生成新计划，不修改计划中的哈希绕过核对。报告包含备份且被 .gitignore 排除，仍可手工恢复；写入异常会尝试恢复仍属于本工具的改动，不覆盖其他执行者的新内容。

## 4. 已经复制旧模板或用 GitHub 模板按钮创建的工程

没有安装基线时，不猜旧版本。先保存工程当前 Git 版本，然后使用母模板目录里的工具：

```powershell
python H:\Project\agent-project-template\tools\template_manager.py adopt --root H:\Project\existing-project
git -C H:\Project\existing-project add -- .agents/template-state.json
git -C H:\Project\existing-project commit -m "Record template update baseline"
python H:\Project\agent-project-template\tools\template_manager.py update --root H:\Project\existing-project --check
python H:\Project\agent-project-template\tools\template_manager.py update --root H:\Project\existing-project
```

adopt 只创建元数据，不覆盖已有内容。完全相同的文件可自动识别；不同文件标为未知基线，更新时留候选供人工合并。缺少 updater／新指南可新增，完成后可从业务工程自身 tools/ 运行。

母模板维护者的 tests／CI／维护日志不在安装清单里，不自动放入旧业务工程。上游仓库需要保持历史可追溯；旧基线不可取时降级为人工合并，不假装能自动恢复历史。

## 5. 母模板维护者

```powershell
git -C H:\Project\agent-project-template pull --ff-only
```

维护者在母模板仓库审查、测试、提交与推送；发布标签后用户可用 --ref 固定。GitHub Template repository 提供 Use this template，但不建立后续模板自动合并关系，已有业务工程使用本工具管理基线。

更新锁只协调本工具的并发运行，不是所有编辑器的事务锁。残留 .agents/.template-update.lock 时，核对 host／pid 和实际持有者停写后再人工清理，不按超时自动删除。
