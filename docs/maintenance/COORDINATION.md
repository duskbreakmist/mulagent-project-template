# 母模板维护协调

- shared_integrator: codex-audit-20261013
- selection_source: 用户2026-10-13授权当前会话全面分析并解决项目不足，随后明确单人串行；本轮负责修复及维护记录整合
- state: active
- default_collaboration_mode: unset
- default_mode_source: unset（本次串行实现不构成全工程默认）
- backup_authorization: 无
- previous_integrator: codex-bootstrap-integrator-20261011
- last_handoff: 无
- updated: 2026-10-14

## 共享写入范围

维护 CURRENT、当前审查与修复的任务记录、测试和相关使用说明；具体范围见 [AUDIT001-CODEX](tasks/AUDIT001-CODEX.md)。用户于2026-10-14明确确认将37ab41a及必要CI修复／验证记录正常推送到 duskbreakmist/mulagent-project-template 的 main 并测试；不强推、不发布或移动版本标签。此前整合与发布事实保留在历史 task 和 Git 中。
同一共享文件由实际整合者串行写入，worker 只写已接受 scope。active 表示当前职责，不表示进程在线、后台监控或自动调度；文件本身不是锁，也不自动通知其他客户端。

## 维护与分发

母仓库用本文件承载真实协调状态；根 .agents/coordination.md 留作业务工程空种子。本文件不进入 manifest。业务工程仍使用自己的根协调记录。
职责变化或接班时记录真实用户指定／预授权、停写和接收事实，遵循[继任指南](../../.agents/guides/coordination.md)；单人普通任务无需重复更新本记录。
