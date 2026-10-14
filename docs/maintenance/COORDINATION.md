# 母模板维护协调

- shared_integrator: codex-audit-20261013
- selection_source: 用户2026-10-13选择单人串行；2026-10-14授权实现更新自动提交与业务README维护规则，随后明确要求上传
- state: active
- default_collaboration_mode: unset
- default_mode_source: unset（本次串行实现不构成全工程默认）
- backup_authorization: 无
- previous_integrator: codex-bootstrap-integrator-20261011
- last_handoff: 无
- updated: 2026-10-14

## 共享写入范围

维护 CURRENT、当前实现的任务记录、管理器、测试和相关使用说明；本轮范围见 [UPDATE001-CODEX](tasks/UPDATE001-CODEX.md)。用户追加上传授权后，将923f232及必要验证记录正常推送到 duskbreakmist/mulagent-project-template 的main并核对CI；不移动发布标签。此前审查推送事实见 [AUDIT001-CODEX](tasks/AUDIT001-CODEX.md)。
同一共享文件由实际整合者串行写入，worker 只写已接受 scope。active 表示当前职责，不表示进程在线、后台监控或自动调度；文件本身不是锁，也不自动通知其他客户端。

## 维护与分发

母仓库用本文件承载真实协调状态；根 .agents/coordination.md 留作业务工程空种子。本文件不进入 manifest。业务工程仍使用自己的根协调记录。
职责变化或接班时记录真实用户指定／预授权、停写和接收事实，遵循[继任指南](../../.agents/guides/coordination.md)；单人普通任务无需重复更新本记录。
