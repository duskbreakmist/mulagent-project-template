# 母模板维护记录

写入前先 git status 确认 HEAD 与共享文件未变；提交只 add 自己改动的文件，不用 git add .。职责见 [COORDINATION](COORDINATION.md)，旧摘要保留在 [维护历史](history/CURRENT-2026-10.md)。

## 全面审查与修复（本地完成，CI验收中）

2026-10-14 [AUDIT001-CODEX](tasks/AUDIT001-CODEX.md) / codex-audit-20261013：用户选择单人串行，完成需求、分发边界、工作台状态机和可维护性审查，见 [详细评估](reviews/AUDIT001-CODEX.md)。
修复路径别名／大小写保护、分发种子防污染、多测试验收、未知生命周期停写、接力作者封存与异常回滚；补路径交叉回归、最低 Python CI 配置和双记录使用说明。默认分发仍为34项，根种子内容不变。
基线94项通过；本地104项完整回归通过（477.953秒）。用户追加授权后37ab41a已推main，首轮CI三组通过，Windows 3.9仅相对源测试失败；正将模拟目录改为真实CLI子进程目录后复验。真实客户端与跨机器仍未验证，不发布或移动标签。

## 母模板与业务 README 分离（已完成）

2026-10-13 [DOC005-CODEX](tasks/DOC005-CODEX.md) / codex-bootstrap-integrator-20261011：母README退出新清单（34项）；init --commit另生成并提交精简业务README，不进入模板基线。template_readme保留文件名并承担模板使用须知；相关活动引用区分业务／模板／母仓库说明。
实现b629ecf已推main，[Windows／Ubuntu完整CI](https://github.com/duskbreakmist/mulagent-project-template/actions/runs/38364780433)均成功（最终94项）。实际v0.2.0旧CLI→新CLI和新工程BOOTSTRAP演练通过；旧README／定制／删除保留，旧基线仅清理元数据，预览只读。v0.2.0标签不移动；ENG001旧摘要归入维护历史。

## 业务工程多 AI 试点验收（本轮已完成）

2026-10-11 [PILOT001-WB](tasks/PILOT001-WB.md) / wb-hy4-20261011：只读评审用户在 H:/Project/test_template_a 的真实试点（基于 f290f2a 可移植流程安装）：dsh-1／wb-1／zcode-1 三 harness 串行接力交付俄罗斯方块 4 功能（FEAT-001–004），跨 AI 代码续写成立，任务内含失败→修复→复测。
独立复验：33 项模板检查、网页逻辑测试、桌面版 `--selftest` 48 项与 `--storage-selftest` 全过；登记／任务板／CURRENT 按协议执行，模板备注反馈通道生效。BOOT004 候选 5 在串行接力层面实证；并行 worktree／真实适配器／跨机器／并发写仍未覆盖，用户预告交由 codex 后续改进。BOOT005 旧摘要归入维护历史。

## 后续验收

真实客户端额度与停写契约、worktree 并行整合、跨机器恢复及权限隔离的验收标准见 [评估报告](reviews/AUDIT001-CODEX.md#后续验收边界)。发布时按维护 README 核对目标提交的实际 CI，不沿用历史结果。
