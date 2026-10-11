# ORCH001-CODEX 五项协作需求的可运行工作台原型

- status: done
- assignment: accepted
- collaboration_mode: serial
- mode_source: 用户要求当前 Codex 围绕五项协作需求推进；原型开发由本会话执行，产品支持多种并行模式
- owner: codex-workbench-20261011
- created: 2026-10-11
- updated: 2026-10-11
- base_commit: 71ede6680da3e8c4c998a9bb1cddfc5f52f674f2
- version_tag: 无

## Objective

把额度接力、功能并行、职责分离与反馈、独立调研与汇总、人工介入映射为可运行的本地协调核心、CLI 与人工界面。用模拟适配器和进程并发验证，不宣称四个实际客户端已经自动接入。

## Scope

唯一主协作目录仍是 H:/Project/agent-project-template；代码开发隔离于 .worktrees/agent-workbench，分支 codex/agent-workbench。新增 tools/agent_workbench.py、tests/test_agent_workbench.py、docs/optional/agent-workbench.md，及本维护 task；维护 README 加可选工作台入口，CURRENT 串行更新本人摘要，旧 TPL003 本人摘要保留到维护 history。分发清单和既有 relay 保持原样；保存他人的 TPL005 暂存与既有评审。运行状态复用已忽略的 .agent-relay 下独立数据库，不写根分发登记。原型不调用模型、不代发外部消息、不自动推送。

## Completed

- 实现 SQLite 事务下的会话登记、任务／依赖／scope 认领、检查点、消息、状态与 Markdown 快照；父子目录重叠也拒绝并发，失效 epoch 拦截旧执行者写入。
- 功能开发与测试分为不同任务；开发参与历史禁止自验收，测试必须指定同一 revision；反馈自动发送给开发者，隐藏测试计划／private 字段不自动转发。
- 调研轮次固定公共输入、参与者与指定汇总者；每人首稿不可覆写，公共状态只展示提交数量，明确关闭后才开放候选与汇总；人可截止并保留缺失名单。
- 同题调研候选同样可关联接力任务，保留 slot 与实际 author；禁止同一备用实例参与另一独立候选。运行数据库版本 2 追加迁移保留旧候选和作者，不通过重建丢失进度。
- 监督前台适配器，流式保存 checkpoint；明确额度退出且确认全部写者停止后按有序 backups 接力。模拟额度用尽→备用进程读取检查点→提交结果已实测。未知错误不假定断额，未知生命周期保持 stopping；人工客户端返回 manual 入口。
- 本地看板用普通表单创建工作／发送反馈，显示真实运行登记、任务、阻塞、消息和调研进度；人可暂停、确认停写后接手、读取检查点。已运行五个模拟 Agent 加 human 的演示，不假称真实客户端上线。
- 首次测试发现 Windows CLI stderr 代码页造成后台解码错误，统一 stdout/stderr 为 UTF-8 并增加实际错误输出断言后重跑通过。

## Verification

- 隔离 worktree 的完整 unittest 回归：70 项通过（251.129 秒，包含原 56 项和初版 14 项工作台场景）。
- 补充人工入口、候选接力与数据库迁移后，最终工作台 18 项场景测试通过（3.860 秒）；覆盖五进程抢领、功能并行、停止确认、旧代次、角色与隐式反馈隔离、版本验收、调研首稿封存／接力作者溯源、人接手、HTTP 令牌和模拟接力。迁移测试首次因测试连接未关闭造成 Windows 清理占用，显式关闭后重跑通过。
- python tools/check_template.py --root .：TEMPLATE_OK files=32；Python 编译和 git diff --check 通过。新可选说明的相对链接人工核对，不扩大默认分发清单。
- 实际浏览器演示验收：创建 H001、暂停 D001 保留占用、人工接手为 human、读取原检查点均成功；窄面板表格改为横向滚动。截图保存在本会话可视化目录，演示服务仅本机监听。
- 本机 PATH 检测到 codex.exe 和 dsh.cmd；未检测到 WB／ZCode 同名命令，不据此认定其没有其他接口。本轮没有测试真实启动／额度信号，不消耗模型额度。
- 自动测试由本会话编写并运行，不算另一独立测试 Agent 已审查本原型。默认 API 上下文／发布门槛不构成文件系统保密隔离，需客户端工作区／权限配合。

## Remaining

本轮通用原型交付无剩余；真实四客户端额度／启动适配、独立测试 Agent 审查、强文件访问隔离与自动集成发布属于后续验收，尚未完成。采用显式参数数组和前台生命周期契约，不能把模拟成功推定为实机互通。保存交付时保持他人 TPL005 暂存 blob abbb29f99945a79338e614a876733888d729f43b 原样。
