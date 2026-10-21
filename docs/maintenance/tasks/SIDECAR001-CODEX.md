# SIDECAR001-CODEX 可选旁路安装

- status: done
- assignment: accepted
- collaboration_mode: serial
- mode_source: 用户2026-10-21明确交给当前实例实现可选旁路安装；未授权派发其他实例
- owner: codex-sidecar-20261021
- created: 2026-10-21
- updated: 2026-10-21
- base_commit: bdb7087
- version_tag: 无

## Objective

为已有 Git 业务工程提供独立协作仓库的可选安装方式，默认工程内安装保持兼容。按[维护约定](../README.md)验证；双根绑定、目录搬迁、更新和 Git 边界必须可核查。

## Scope

安装器、独立检查器、相关回归、分发说明与协议入口、manifest 和必要维护记录。业务仓库只写本地 Git 绑定，不自动改业务文件、索引、提交、身份或远程；不做已有模板迁移、不自动收集客户端对话、不推送。

## Completed

- 已检查现有安装／更新、主协作目录、路径校验、Git 和记录约定。
- 采用一份协作仓库绑定一个业务仓库；旁路模式显式选择，启动提示显式加载规则。
- `init --mode sidecar --project-root` 安装独立协作 Git，业务文件／索引／HEAD 保留；`entry` 显示协作性质、两个实际路径与新 Agent 首次回复要求。
- `bind` 恢复本机路径，检查基线对象、双向身份、重复绑定、目录嵌套、已有任务板与 Git 公共目录；业务绑定锁与配置失败回滚。
- 独立检查器核对旁路绑定；update/apply 只作用协作仓库，保留模式与身份，拒绝不支持旁路的旧来源和覆盖旁路描述的计划。
- 新增[旁路操作指南](../../sidecar.md)、CLI 回归及入口／Git 约定。清单35项，四份根状态种子不变；最近完成摘要按窗口归档。

## Verification

- Windows／Python 3.13.8：`python -X utf8 -m unittest discover -s tests -v` 完整128项通过，506.774秒；含新增旁路15项。日志保留在本机 `.test-tmp/sidecar-full-suite.txt`，未纳入分发。
- 隔离真实 Git 验证业务已暂存／未跟踪内容保留、仅协作更新提交、安装副本CLI、中文／空格／方括号路径、未创建目录、搬迁、独立克隆、业务worktree、误绑定拒绝、配置失败恢复及计划保护。
- `python tools/check_template.py --root . --maintenance`：35项通过；`git diff --check` 通过。初次沙箱临时目录访问失败后，经自动批准沙箱外执行；首轮12项中的1项是子进程输出编码断言问题，修正为显式UTF-8后纳入完整回归通过。
- 未验证：Linux、Python 3.9、跨机器／跨磁盘实机与真实客户端新会话自动加载。首次提示由AGENTS和entry实现，未接入原生弹窗；未自动采集客户端对话。未推送／未运行本轮远端CI。

## Remaining

无实现剩余；上述实机与客户端边界保持未验证，不沿用历史CI作为本轮结果。
