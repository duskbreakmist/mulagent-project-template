# 可选旁路安装

旁路模式把规则、任务、消息、交接和验证证据放进独立协作 Git 仓库，实际代码仍在已有业务 Git 工作树中修改和提交。默认 `init` 仍在工程内安装；仅显式指定 `--mode sidecar` 才启用旁路。

## 安装与首次打开

需要 Python 3.9+、Git、已有至少一个提交的业务仓库，以及两个互不嵌套、可访问的目录。协作目录须为空，且不能位于其他 Git 仓库内；允许预建无历史的空 Git。安装器不迁移业务目录已有的模板或任务板。

在业务目录的父目录执行，工具来源使用已支持旁路的版本：

```powershell
python agent-template-tools/tools/template_manager.py init --mode sidecar --root my-app-collab --project-root my-app --ref main --commit
python my-app-collab/tools/check_template.py --root my-app-collab
```

`--root` 是新协作目录，`--project-root` 是已有业务工作树根；可为不同磁盘上的绝对路径。安装器为协作目录创建独立 Git，沿用真实提交身份，不设置 origin；`--commit` 只提交协作文件。业务仓库允许有未提交改动，已有文件、暂存区、HEAD、分支、身份和远程均保留。旁路安装不能使用 `--no-git`。

**新 Agent 默认打开协作文件夹。** 在该文件夹运行：

```powershell
python tools/template_manager.py entry --root .
```

命令先核对绑定，再显示“当前文件夹是协作文件夹”、协作路径、指向的业务路径与启动提示。将完整提示交给 Agent；根 AGENTS 要求它在每个新会话首次回复时向用户显示这项说明，并读取业务现有规则与 README。提示每个新会话显示一次，避免把“首次”做成跨用户共享的已读标记。

客户端必须实际加载协作目录 AGENTS；若不自动加载，在初始提示中明确要求先读它。模板提供终端提示与 Agent 首次回复规则，未接入各客户端的原生弹窗 API，也不能保证客户端未加载规则时仍会自动提示。启动前确认客户端有两个目录的访问权限；旁路不授予文件系统权限。

业务目录可以保留自己的 AGENTS 等规范；旁路安装不增加入口文件，也不覆盖既有规范。执行规则冲突时按用户授权和业务范围核对，不能用协作协议替代业务规范。

## 文件与命令的归属

| 内容／操作 | 目录 |
| --- | --- |
| 登记、任务、计划、消息、交接、进度、研究候选和执行证据 | 协作目录 |
| 协作仓库 README | 说明协作入口与绑定查询，保留在协作仓库 |
| 源码、业务测试、依赖与构建配置、业务 README／接口文档 | 实际业务工作树 |
| 安装更新、模板完整性检查 | 协作目录 |
| 依赖安装、构建、业务测试、格式检查 | 实际业务工作树 |

命令必须显式确认执行目录；可使用 `git -C PATH ...` 避免在错误仓库提交。并行代码开发仍使用业务仓库独立 worktree，task 记录本实例实际工作树；Git 本地协调根由同一业务仓库各 worktree 共享，不能各自改为另一个任务板。

不把业务树通过符号链接接进协作仓库。分发清单、更新和链接检查仍限制在协作根内；跨仓库证据使用 task 中的仓库说明、路径文本和提交 SHA，不依赖逃逸本地 Markdown 链接。

## 两仓库的版本记录

1. 在协作 task 中记业务 `base_commit`、实际工作树、scope、验收命令和已有未提交修改。
2. 在业务工作树运行实际验证，审查并仅提交本任务业务文件；记录真实交付 SHA。
3. 在协作 task 中记录该业务 SHA、命令的执行目录、结果和未验证项，再审查提交协作记录。

两个 Git 仓库无法通过本工具形成原子提交。业务已提交、协作提交失败时保留业务提交，明确记录尚未保存的协作改动，修复后重试；不能因记录失败就撤销业务或声称全部完成。仅本地提交不代表已推送或备份，两个仓库的远程均需按明确授权分别配置和推送。

这里的“日志”包括任务过程、关键操作与验收证据，不自动抓取其他客户端完整对话或内部思考链。凭据、缓存、运行锁、数据库和大型临时产物不自动纳入 Git；默认 `*.log` 被忽略。需要保存的命令输出可经筛选后放入 `evidence/<TASK-ID>/` 的 `.txt`／`.md` 文件；不要为“所有日志”取消全部忽略规则。

## 更新

在协作目录执行，提交要求仅针对协作仓库：

```powershell
python tools/template_manager.py update --check
python tools/template_manager.py update
python tools/check_template.py --root .
python tools/template_manager.py entry --root .
```

更新前后都核对本机绑定。更新只改协作仓库，保留旁路身份描述和安装模式，不接触业务 Git 暂存、提交或配置。不能切回不支持旁路的旧来源版本；不能通过 update/apply 切换安装模式。冲突处理沿用[安装更新说明](template-usage.md#3-发生冲突)。

## 搬迁、克隆与恢复

旁路描述 `.agents/sidecar.json` 随协作 Git 保存，含随机协作 ID 与安装时业务基线提交；不含机器绝对路径。机器路径只存本地 Git 配置：

| 仓库 | 本地配置 |
| --- | --- |
| 协作 | `agent.coordinationRoot`、`agent.projectRoot` |
| 业务（普通 worktree 共用） | `agent.coordinationRoot`、`agent.sidecarId` |

搬迁后或在新机器分别克隆两个仓库后，显式重新绑定：

```powershell
python NEW-COLLAB/tools/template_manager.py bind --root NEW-COLLAB --project-root NEW-PROJECT
python NEW-COLLAB/tools/check_template.py --root NEW-COLLAB
```

`bind` 核对两个仓库、已保存业务基线对象和已有身份，只写本机 Git 配置，不修改已提交描述。浅克隆缺少基线对象时先获取所需历史；仓库历史重写导致基线消失时先调查，不能修改描述来绕过检查。随机 ID 与提交对象用于发现误绑定，不构成身份认证或访问控制。

目标业务仓库已绑定其他协作 ID，或已有另一个可达主协作目录时拒绝覆盖。确需迁移到一份复制的协作仓库，先确认所有实例停写且唯一任务板已确定，核对旧配置后，由操作者显式清除业务仓库旧绑定再运行 bind：

```powershell
git -C PROJECT config --local --get-all agent.coordinationRoot
git -C PROJECT config --local --get-all agent.sidecarId
git -C PROJECT config --local --unset-all agent.coordinationRoot
git -C PROJECT config --local --unset-all agent.sidecarId
```

这些命令不是日常启动步骤。业务规则、旧任务、Git 历史或目录不可达时，Agent 应显示原因并停止业务写入，不能自动新建第二份任务板。旁路不会自动同步两台机器上的任务记录。

协作仓库也拒绝改绑到另一份仍可访问的业务仓库；同一业务 Git 的不同 worktree 可以重新选择。确需切换独立业务副本时，先停止旧实例、处理旧业务仓库上的反向绑定，再核对并清除协作仓库的 `agent.projectRoot` 后显式 bind。不能仅改一端配置让两个业务仓库同时使用同一任务板。

## 失败与当前边界

- 无效目录／参数、旧模板版本、已有任务板或绑定冲突：拒绝安装；先核对目标，不覆盖文件。
- 配置写入失败：尝试恢复本次配置；若并发配置已改变则保留并报告。绑定锁位于业务 Git 公共目录 `agent-sidecar.lock`，异常退出后先确认持有者停写再处理，不按超时自动删除。
- 下载失败不安装文件；安装后绑定或初始提交失败会保留已生成的协作文件，明确报错。不要反复 init；核对文件后用 bind 恢复并手动审查提交。
- 已在业务目录安装的模板不自动迁移。需另做清点、记录搬迁和入口切换，避免丢失旧任务。
- 旁路只分离记录与代码；它不提供客户端调度、跨机同步、权限沙箱或代码并发隔离。
