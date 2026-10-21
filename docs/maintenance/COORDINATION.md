# 母模板维护协调

- shared_integrator: codex-sidecar-20261021
- selection_source: 用户2026-10-21授权当前实例实现可选旁路安装
- state: active
- default_collaboration_mode: unset
- default_mode_source: unset（本次串行实现不构成全工程默认）
- backup_authorization: 无
- previous_integrator: codex-audit-20261013
- last_handoff: 无
- updated: 2026-10-21

## 共享写入范围

本轮范围见 [SIDECAR001-CODEX](tasks/SIDECAR001-CODEX.md)：安装器、检查器、回归和旁路使用说明；验证后本地提交，未获本轮推送授权。此前维护与上传事实保留在 [DOC006-CODEX](tasks/DOC006-CODEX.md)、[UPDATE001-CODEX](tasks/UPDATE001-CODEX.md) 和 [AUDIT001-CODEX](tasks/AUDIT001-CODEX.md)。
同一共享文件由实际整合者串行写入，worker 只写已接受 scope。active 表示当前职责，不表示进程在线、后台监控或自动调度；文件本身不是锁，也不自动通知其他客户端。

## 维护与分发

母仓库用本文件承载真实协调状态；根 .agents/coordination.md 留作业务工程空种子。本文件不进入 manifest。业务工程仍使用自己的根协调记录。
职责变化或接班时记录真实用户指定／预授权、停写和接收事实，遵循[继任指南](../../.agents/guides/coordination.md)；单人普通任务无需重复更新本记录。
