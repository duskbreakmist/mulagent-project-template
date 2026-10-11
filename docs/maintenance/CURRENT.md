# 母模板维护记录

写入前先 git status 确认 HEAD 未变；提交只 add 自己改动的文件，不用 git add .。

## 业务工程约定与小任务验收（本轮已完成）

2026-10-11 [ENG001-CODEX](tasks/ENG001-CODEX.md) / codex-bootstrap-integrator-20261011：工程约定集中到README／引用文档，AGENTS与两种task格式接入，补检查边界及旧工程手工保留README的迁移说明，保持33项分发。
独立CLI示例完成BOOTSTRAP→业务红／绿测试3项→核对提交／记录，86项完整回归通过；57ef7f1原样发布，[Windows／Ubuntu CI](https://github.com/duskbreakmist/mulagent-project-template/actions/runs/38139625505)均成功。不宣称真实产品上线或独立AI审查；BOOT001旧摘要保存到维护历史。

## 自举审计改进与发布（本轮已完成）

2026-10-11 [BOOT005-CODEX](tasks/BOOT005-CODEX.md) / codex-bootstrap-integrator-20261011：完成核心清单／Python语法／维护task检查、维护COORDINATION、本地来源规范化与update --source恢复、移动／种子整理指南。默认分发33项不变，真实AI接入／完整开发包不在本轮范围。
33项维护检查与85项本地完整回归通过；实现b69d630原样发布，官方API核对SHA一致，[Windows／Ubuntu CI](https://github.com/duskbreakmist/mulagent-project-template/actions/runs/38132901028)均成功。常规Git连接重置后经官方API非强制发布，未改持久配置／移动标签；DOC004旧摘要归档。
2026-10-11 后续应用评估：已足够作为有人监督的业务开发协作基础；业务目标、构建／测试、验收和自身CI／发布流程由目标工程定义。下一步以真实小任务验证完整交付闭环，详见task模板备注。

## 自举审计统一整合（本轮已完成）

2026-10-11 用户指定 codex-bootstrap-integrator-20261011 整合，[BOOT004-INTEGRATE](tasks/BOOT004-INTEGRATE.md)／[统一 RUN](runs/2026-10-11-bootstrap-audit.md)。已收 Codex、WB 两组共六份首稿；[BOOT002-ZCODE](tasks/BOOT002-ZCODE.md) 用户确认停止且报告缺失，按 missing 收尾，源任务 blocked。原稿保留，治理授权与共享写入范围记在维护 RUN，根种子保持空白。
清单缩减、语法／状态检查覆盖与路径问题隔离复现；对“自检为零／母仓库不能维护自己／必然死锁”等强结论作限定。形成五项去重候选，未改生产实现；前轮 75 项通过按当时事实引用，不冒充本阶段重跑。DOC003 摘要保存至维护历史。

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
