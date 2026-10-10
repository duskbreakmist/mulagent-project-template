# COLLAB007 发布独立 GitHub 模板并提供安装／更新工具

- status: done
- assignment: accepted
- collaboration_mode: serial
- mode_source: 用户指定仓库和本地目录，授权本会话完成发布及安装／更新命令
- owner: gpt
- created: 2026-10-10
- updated: 2026-10-10
- base_commit: 77e5f14
- version_tag: v0.1.1（独立模板仓库）

## Objective

完成 duskbreakmist/mulagent-project-template 发布、Template repository 设置；新工程用命令获取骨架，已有工程后续更新保护真实记录与定制规则。

## Scope

H:/Project/agent-project-template 的模板、脚本、测试、说明与 GitHub 发布；本工程母模板镜像、相关测试、任务／CURRENT。其他会话产出不动。维护记录不作为新工程的模板状态分发。

## Completed

独立仓库 36 文件已发布，32 项分发清单包含 Git 管理器、README 和安装／更新说明；v0.1.0 保留首版代码提交 921cd9ee8fb3a044efbbae1239bd438cfda82bf0；v0.1.1 指向兼容修正 c6e3e0cb7aab86247d66d869e7faa39055614dfc，main 继续保留维护验收记录。GitHub is_template=true；Ubuntu／Windows CI 已成功。

新工程 init 从 Git 获取快照并建立独立基线／Git；update 保护状态种子、三方合并、冲突整轮不应用；adopt 不猜未知旧基线，apply 检查未变更与冲突标记／JSON／Python 语法。保留本地删除与上游删除的文件，不自动推送业务工程。

## Verification

独立发布目录 37 项测试通过（18 复制 + 19 实际本地 Git），TEMPLATE_OK files=32。GitHub CI 成功：https://github.com/duskbreakmist/mulagent-project-template/actions/runs/38038954158。

公开 Git 验收：init --commit 建立临时独立工程、无模板 origin；定制登记后 update --check 对工程只读，update 返回 ALREADY_CURRENT 且登记／状态／全部文件不变，检查器通过。临时验收工程已清理。

修正 Python 3.9 不支持的 Path.write_text newline 参数为 UTF-8 字节写入；相关实际三方合并回归 1 项通过。公开跨版本验收 v0.1.0 → main/v0.1.1 通过，只更新两项模板文件，定制登记保留、预览只读、无模板 origin、32 项检查通过、提交后重复更新不变；临时工程已清理。修正版双平台 CI 成功：https://github.com/duskbreakmist/mulagent-project-template/actions/runs/38040232118。本机未直接运行 Python 3.9。

最初自动审批额度失败未执行外部写入，后恢复；最初沙箱测试被 Windows ACL 拒绝，提升后完成，不把初次失败计为通过。

## Remaining

交付范围内无剩余；未来其他工程的大规模定制／复杂冲突需在自身环境审阅与验证。用户原项目、旧研究和其他会话的未提交内容保留。维护日志不由安装器分发；正常单人完成用本 task 收尾。
