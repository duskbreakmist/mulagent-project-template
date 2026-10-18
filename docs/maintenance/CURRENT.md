# 母模板维护记录

写入前先 git status 确认 HEAD 与共享文件未变；提交只 add 自己改动的文件，不用 git add .。职责见 [COORDINATION](COORDINATION.md)，旧摘要保留在 [维护历史](history/CURRENT-2026-10.md)。

## README非固定版本说明与精简（已完成）

2026-10-18 [DOC006-CODEX](tasks/DOC006-CODEX.md) / codex-audit-20261013：README从203行精简至93行，推荐命令显式跟随main，区分日常更新、固定标签与切回main；提供旧工具升级和可选工作台入口，用导航表代替完整文件树。默认34项与状态种子不变。
维护检查、变更文档链接、CLI参数核对与diff检查通过；纯文档未重复运行功能套件，未执行真实业务安装／更新示例。DOC005旧摘要保留到维护历史。

## 更新自动提交与业务README维护（已完成）

2026-10-14 [UPDATE001-CODEX](tasks/UPDATE001-CODEX.md) / codex-audit-20261013：现有Python更新命令默认仅提交本次模板变更与基线，保留 `--no-commit`；新增身份／Git操作检查、字面路径及提交失败恢复说明，`apply --commit`支持已审阅候选。AI按实际业务维护README概述、功能与运行方式，模板说明独立；默认34项与四份状态种子不变。
本地完整113项执行的短入口长度失败修正后，相关25项复测全过。用户追加上传要求后923f232已推main，[Windows／Ubuntu × Python 3.9／3.13 CI](https://github.com/duskbreakmist/mulagent-project-template/actions/runs/38510819401)四组全部通过，每组113项测试与34项模板检查；旧PILOT摘要保留到维护历史。

## 全面审查与修复（已完成）

2026-10-14 [AUDIT001-CODEX](tasks/AUDIT001-CODEX.md) / codex-audit-20261013：用户选择单人串行，完成需求、分发边界、工作台状态机和可维护性审查，见 [详细评估](reviews/AUDIT001-CODEX.md)。
修复路径别名／大小写保护、分发种子防污染、多测试验收、未知生命周期停写、接力作者封存与异常回滚；补路径交叉回归、最低 Python CI 配置和双记录使用说明。默认分发仍为34项，根种子内容不变。
基线94项通过；本地104项完整回归通过（477.953秒）。用户追加授权后37ab41a已推main；c4d9f5a修复相对源测试的模拟目录问题，[Windows／Ubuntu × Python 3.9／3.13 CI](https://github.com/duskbreakmist/mulagent-project-template/actions/runs/38433606962)四组均通过，每组104项回归与34项模板检查。真实客户端与跨机器仍未验证，标签未改。

## 后续验收

真实客户端额度与停写契约、worktree 并行整合、跨机器恢复及权限隔离的验收标准见 [评估报告](reviews/AUDIT001-CODEX.md#后续验收边界)。发布时按维护 README 核对目标提交的实际 CI，不沿用历史结果。
