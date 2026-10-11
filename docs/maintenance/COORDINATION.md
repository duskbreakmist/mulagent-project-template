# 母模板维护协调

- shared_integrator: codex-bootstrap-integrator-20261011
- selection_source: 用户2026-10-11指定“你现在负责整合”，随后授权合理改动并推送测试
- state: active
- default_collaboration_mode: unset
- default_mode_source: unset（本次串行实现不构成全工程默认）
- backup_authorization: 无
- previous_integrator: 未指定
- last_handoff: 无
- updated: 2026-10-11

## 共享写入范围

维护 CURRENT、轮次汇总、任务接收与跨任务整合；具体实现与发布权限按当前用户任务和 task 确定。本轮实现入口为 [BOOT005-CODEX](tasks/BOOT005-CODEX.md)，审计接收事实见 [BOOT004 RUN](runs/2026-10-11-bootstrap-audit.md)。
同一共享文件由实际整合者串行写入，worker 只写已接受 scope。active 表示当前职责，不表示进程在线、后台监控或自动调度；文件本身不是锁，也不自动通知其他客户端。

## 维护与分发

母仓库用本文件承载真实协调状态；根 .agents/coordination.md 留作业务工程空种子。本文件不进入 manifest。业务工程仍使用自己的根协调记录。
职责变化或接班时记录真实用户指定／预授权、停写和接收事实，遵循[继任指南](../../.agents/guides/coordination.md)；单人普通任务无需重复更新本记录。
