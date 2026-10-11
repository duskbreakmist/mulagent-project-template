# PUB001-CODEX 推送模板与验证新工程用法

- status: review
- assignment: accepted
- collaboration_mode: serial
- mode_source: 用户明确要求当前实例推送并说明新工程使用
- owner: codex-publish-20261011
- created: 2026-10-11
- updated: 2026-10-11
- base_commit: 76af135
- version_tag: 无

## Objective

把已提交的模板发布到 origin/main，核对真实 CI 与 GitHub 默认新工程安装路径，提供可执行的新工程初始化和协作接入步骤。

## Scope

推送本地 main；维护任务与 CURRENT／必要历史摘要。发布验证发现 Windows 短路径问题时，最小修复 tools/legacy/agent_bootstrap.py 和相关的两个测试文件。保留 TPL005 他人暂存，不推送其他分支、不移动标签。

## Completed

已正常推送 0df7095→76af135，远端 main SHA 复核一致。在临时目录从默认 GitHub 来源实际执行 init --commit，33 项检查通过，含文档规范，Git 状态干净、无模板 origin；临时目录已清理。

CI run 38119513142：Ubuntu 成功，Windows 模板检查成功、完整测试出现 1 失败与 3 错误。日志定位到 Windows 临时目录短路径：旧初始化器只解析子路径而未解析比较根，relay 测试直接比较未解析根的字符串。新安装器测试通过。

旧初始化器统一解析根目录再做包含关系检查，避免短路径／相对路径的等价名称误报，同时保留真实逃逸拦截。补相对根目录回归，relay 测试改为比较解析后的主目录；未改变分发组成或用户业务文件。

## Verification

- 本机相关测试通过：旧初始化器 12 项、relay 8 项；包含真实父目录逃逸拒绝与跨进程锁检查。
- 模板检查通过（33 项），`git diff --check` 通过；TPL005 暂存 blob 仍为 abbb29f99945a79338e614a876733888d729f43b。
- 临时独立 Git 副本完整 75 项测试通过（159.271 秒）；只拷贝本轮三个修复文件，不带入主目录的 worktree 或他人未提交文件，临时副本已清理。

## Remaining

提交并推送已验证的最小修复，核对新提交的 Windows／Ubuntu CI；向用户给出初始化、看板、Agent 接入及更新命令。
