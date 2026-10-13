# 母模板维护记录

写入前先 git status 确认 HEAD 未变；提交只 add 自己改动的文件，不用 git add .。

## 母模板与业务 README 分离（已完成）

2026-10-13 [DOC005-CODEX](tasks/DOC005-CODEX.md) / codex-bootstrap-integrator-20261011：母README退出新清单（34项）；init --commit另生成并提交精简业务README，不进入模板基线。template_readme保留文件名并承担模板使用须知；相关活动引用区分业务／模板／母仓库说明。
实现b629ecf已推main，[Windows／Ubuntu完整CI](https://github.com/duskbreakmist/mulagent-project-template/actions/runs/38364780433)均成功（最终94项）。实际v0.2.0旧CLI→新CLI和新工程BOOTSTRAP演练通过；旧README／定制／删除保留，旧基线仅清理元数据，预览只读。v0.2.0标签不移动；ENG001旧摘要归入维护历史。

## 业务工程多 AI 试点验收（本轮已完成）

2026-10-11 [PILOT001-WB](tasks/PILOT001-WB.md) / wb-hy4-20261011：只读评审用户在 H:/Project/test_template_a 的真实试点（基于 f290f2a 可移植流程安装）：dsh-1／wb-1／zcode-1 三 harness 串行接力交付俄罗斯方块 4 功能（FEAT-001–004），跨 AI 代码续写成立，任务内含失败→修复→复测。
独立复验：33 项模板检查、网页逻辑测试、桌面版 `--selftest` 48 项与 `--storage-selftest` 全过；登记／任务板／CURRENT 按协议执行，模板备注反馈通道生效。BOOT004 候选 5 在串行接力层面实证；并行 worktree／真实适配器／跨机器／并发写仍未覆盖，用户预告交由 codex 后续改进。BOOT005 旧摘要归入维护历史。

## v0.2.0 发布（已完成）

2026-10-11 [REL001-CODEX](tasks/REL001-CODEX.md) / codex-bootstrap-integrator-20261011：[v0.2.0](https://github.com/duskbreakmist/mulagent-project-template/releases/tag/v0.2.0)正式发布，标签固定64a135e，Apache-2.0原文与范围说明随35项分发；补update --ref与固定版本安装／升级说明，业务根LICENSE不覆盖。
90项本地完整回归、35项维护检查、真实标签安装／v0.1.1升级及GitHub源码归档逐文件比对通过；[Windows／Ubuntu CI](https://github.com/duskbreakmist/mulagent-project-template/actions/runs/38143819730)均成功。标准Git HTTPS在本机仍受连接限制，未宣称远端clone成功；BOOT004旧摘要归入维护历史，旧标签不移动。

## 多实例同源审计轮次（已收尾）

2026-10-11 四实例用同一提示词审计本仓库，见 [轮次索引](runs/2026-10-11-structure-audit.md)。四实例确认：codex-structure（TPL003）、wb-structure（TPL004）、zcode-structure（TPL005，中断后由汇总者代收 4f71580）、wb-hy4（TPL006，即第四实例）。盲态不一致，结论作互相印证的审计而非公平横向评测。
2026-10-11 16:02 用户授权 wb-hy4-20261011 收尾：合并建议清单见 RUN 记录（已实施 7 项、未实施候选 8 项，维护边界回归测试居首）。收尾提交：TPL005 代收 4f71580、白熊清理 a0872fc、本收尾；GitHub 推送由用户执行。

## TPL002 迁移方案与修改

根目录仍保存 32 项分发骨架；测试去掉原工程路径回退。COLLAB001–007、评审、反馈与设计归入 legacy，清单记录原始字节哈希。旧初始化器进入 tools/legacy；消息工具进入 tools/ 和 docs/optional，启动器要求显式业务目录；都不默认分发。

## TPL002 迁移验证

独立 56 项 unittest 全通过，TEMPLATE_OK files=32；启动器缺少业务目录退出 2；75 份历史原始字节与 Git 对象哈希一致；原工程 41 项开发文件移除，48 项保护文件哈希和迁移链接检查通过。目标的根登记／任务索引／CURRENT 仍为空骨架。四客户端真实收发、提示音／剪贴板、EXE 未验证；不实现自动唤醒或额度轮换。

## 先前发布

v0.1.1 已发布，实际安装／跨版本更新及双平台 CI 成功；完整记录在 history/2026-10-10-TPL001.md。本次不移动已发布标签。

## 当前边界

源工程 README 的另一作者软件追加段、ADR-002 未提交编辑及其他业务工作保持原样；模板维护历史和未提交消息工具记录按原作者存档，迁移不扩大既有验收。首次归档发现 Git 换行转换，以归档局部属性修正并逐项核验；没有改写原历史字节。

## 接手与发布

实际开发 task 保存 docs/maintenance/tasks，根分发状态保持空骨架。2026-10-11 用户随后明确授权推送，GitHub main 已接收 f9c7669 及其前序提交；最新发布与 CI 状态见 PUB001-CODEX。历史任务的未推送／未验证说明保留当时语境，不能把旧版绿色 CI 算成本轮通过。
