# 安装与后续更新

## 1. 获取工具和创建新工程

安装 Python 3.9+ 与 Git，并配置你自己的真实 Git 提交身份。在新建的空工程文件夹内打开终端，执行：

```powershell
git clone https://github.com/duskbreakmist/mulagent-project-template.git ../agent-template-tools
python ../agent-template-tools/tools/template_manager.py init --root . --commit
python tools/check_template.py --root .
```

`../agent-template-tools` 是本次下载的同级工具目录，`--root .` 是当前业务工程；无需原电脑上的路径。相对路径适用于 Windows、Linux 和 macOS；若系统使用 python3，替换示例中的 python 命令。

同级已有该工具仓库时跳过 clone，先执行 `git -C ../agent-template-tools pull --ff-only`。init 每次从 Git 读取最新 main，也可用 --ref v0.2.0 固定已发布版本。目标须为空（新建的无历史空 Git 仓库也可），已有工程不用 init。工具目录放在业务工程外，避免下载工具后使 init 目标不再为空。

默认初始化独立 Git 并设置本地协作根。--commit 保存初始模板提交；身份缺失会明确报错，不捏造姓名／邮箱，已生成文件保留。--no-git 仅在你明确不需要版本管理时使用，不能与 --commit 同时指定。安装器不设置业务工程 origin，不推送。

### 业务代码开工前

将README写成项目说明，集中填写“工程约定”六项或链接已有规范；登记实际参与者，在 .agents/coordination.md 记录已授权整合者与实际协作模式。先确认客户端读到了规则，再按task引用相关工程约定。技术栈／命令尚不明确时先做调查任务，不猜配置。
已有工程的README属于受保护种子，update不会自动加入本节；在保留业务说明的前提下手工添加约定或已有规范链接即可，不覆盖整份README。
新工程的最小验收流程为：init→自身check→建立lite task→实现一个明确小功能→运行业务测试与相关构建→审查diff→更新task／索引／CURRENT→显式提交。失败用例修复后重跑，记录实际命令、结果和未测项。已有工程保留并引用现有约定。
`TEMPLATE_OK` 不代替业务构建／测试，也不证明task与索引／CURRENT同步或工程可上线。业务工程无需复制母仓库回归；运行自己的验收命令即可。

### 使用未推送的本地版本

--source 也接受本地 Git 仓库路径；--ref main 读取已提交快照，不包括工作区未提交内容：

~~~powershell
$templateSource = (Resolve-Path "../agent-template-tools").Path
python ../agent-template-tools/tools/template_manager.py init --root . --source "$templateSource" --ref main --commit
~~~

上面的 PowerShell 先解析同级工具目录。安装器也会把相对本地 --source 按调用时目录解析为绝对路径再保存，因此后续 update 不依赖调用目录。基线沿用该本地 source，不自动切换为 GitHub；源仓库移动后按第6节显式恢复。长期跟随 GitHub 的新工程优先使用默认来源。init 目标须位于母仓库外。

### 同时使用协作工作台

默认清单不包含可选工作台；在业务工程根目录运行同级工具仓库中的脚本：

~~~powershell
python ../agent-template-tools/tools/agent_workbench.py --root . serve
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

--check 对工程只读，不建锁、状态或报告；仍会访问 Git，并在临时目录读取快照。状态基线在 .agents/template-state.json，包含 source、ref、提交与各文件基线哈希，需要随业务工程 Git 保存。不把清单的格式 version 当发布版本。省略 --ref 时沿用原分支／固定标签；要升级到已存在的发布标签，用最新同级工具执行：

```powershell
python ../agent-template-tools/tools/template_manager.py update --root . --ref v0.2.0 --check
python ../agent-template-tools/tools/template_manager.py update --root . --ref v0.2.0
python tools/check_template.py --root .
```

旧版工程自身工具可能不支持 update --ref，因此先更新同级工具仓库，再用上面命令。预览不改变基线；实际成功应用才保存新 ref。冲突时先审查并 apply，不能靠改基线哈希绕过检查。选择 --ref main 可恢复跟随 main。

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

没有安装基线时，不猜旧版本。先保存工程当前 Git 版本，在已有业务工程根目录打开终端。若尚未获取工具，先执行第 1 节的 clone（跳过 init），然后：

```powershell
python ../agent-template-tools/tools/template_manager.py adopt --root .
git add -- .agents/template-state.json
git commit -m "Record template update baseline"
python ../agent-template-tools/tools/template_manager.py update --root . --check
python ../agent-template-tools/tools/template_manager.py update --root .
```

adopt 只创建元数据，不覆盖已有内容。完全相同的文件可自动识别；不同文件标为未知基线，更新时留候选供人工合并。缺少 updater／新指南可新增，完成后可从业务工程自身 tools/ 运行。

母模板维护者的 tests／CI／维护日志不在安装清单里，不自动放入旧业务工程。上游仓库需要保持历史可追溯；旧基线不可取时降级为人工合并，不假装能自动恢复历史。

## 5. 母模板维护者

在下载的母模板仓库目录内执行：

```powershell
git pull --ff-only
```

维护者在母模板仓库审查、测试、提交与推送；发布标签后用户可用 --ref 固定。GitHub Template repository 提供 Use this template，但不建立后续模板自动合并关系，已有业务工程使用本工具管理基线。

更新锁只协调本工具的并发运行，不是所有编辑器的事务锁。残留 .agents/.template-update.lock 时，核对 host／pid 和实际持有者停写后再人工清理，不按超时自动删除。

母仓库使用 `python tools/check_template.py --root . --maintenance`，额外检查维护入口、tasks／runs／history 本地链接与维护 task 状态；实际整合者记在 docs/maintenance/COORDINATION.md。默认业务检查验证v2核心协议／工具锚点、清单文件、受管理Python语法、链接和业务任务状态。检查不执行被检查代码，也不认证协议执行事实或文件来源；手工复制包无需安装基线。v1仍采用基本完整性检查。

## 6. 工程或本地来源移动后恢复

在移动后的主工程根目录运行，重新绑定本机协作根；已有 worktree 先确认唯一实时主目录：

```powershell
git config --local agent.coordinationRoot (Get-Location).Path
git config --get agent.coordinationRoot
```

这是本机 Git 配置，不提交绝对主目录到共享规则。若模板 source 仍可达，正常 update 即可。旧基线保存了相对路径，或本地来源已搬家时，先提交当前工程改动，再明确指定原来源的新位置：

```powershell
python tools/template_manager.py update --source "../agent-template-tools" --check
python tools/template_manager.py update --source "../agent-template-tools"
python tools/check_template.py --root .
git diff
```

--source 对URL与Git scp写法保留原含义；本地路径按此次调用目录解析。--check 不改基线；实际 update 成功后保存新来源。ref 沿用既有基线；新来源若没有旧提交，未知旧基线会形成待人工处理候选。审阅规则和新 .agents/template-state.json 后一起提交，不手改文件哈希。远端URL来源也可明确切换，但应先核对仓库和版本。
旧安装器尚不支持 --source 时，先更新第1节的同级工具仓库，再用 `python ../agent-template-tools/tools/template_manager.py update --root . --source "../agent-template-tools" --check` 预览，并以同一路径执行实际 update。

## 7. 将业务副本整理为新的分发来源

需要完整模板开发能力时，优先 clone 母仓库，取得 tests、CI 和维护入口。业务 init 副本主要消费协议；不将实际业务 checkout 直接作为空白工程模板。

确需从业务副本派生来源时：

1. 保存业务 Git 版本，在工程外建立独立 clone／分支作为候选，保留原业务历史和原 checkout。
2. 明确以后由哪个来源提供升级。将 README、agents_list.md、.agents/coordination.md、.agents/tasks/README.md、docs/CURRENT.md 五项种子整理为通用说明／空状态；核对真实身份、任务索引、进度和路径是否残留。保留需要的定制规则，但不能把运行记录加入 manifest。
3. 仅显式暂存审阅过的种子与规则，提交候选；不要把业务源的安装基线误当成新工程基线，init 会为新工程生成自己的状态。
4. 在另一个空工程以候选 Git 仓库为 --source 安装并检查；核对35项当前骨架（包含两个模板许可文件）、独立Git、无模板origin、新登记／CURRENT为空和新source／revision正确。具体新清单允许扩展，核心协议和工具应保留。
5. 完整测试仍在维护仓库执行。本轮默认安装集不包含 tests、CI、维护记录或可选客户端工具。通过候选验收后再按明确授权发布；已有业务工程继续保留原数据。
