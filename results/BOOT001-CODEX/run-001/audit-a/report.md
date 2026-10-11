# audit-a：当前项目自举能力判断

当前项目已经能在 AI／人的执行下，用自身协议维护自身，也能从已安装副本再安装下一份协议骨架；它尚未构成自主驱动真实 AI、测试、修复、发布的完整自举系统。默认分发副本保留管理器与协议，却没有母仓库的测试、CI、维护记录和可选工作台，因此“能复制自身骨架”与“能独立再生完整开发环境”应分开回答。

本报告基于 `8d2645f80f43df4932515f5b6650a05e53410f5b`。这是独立首稿：未读取 codex-main、audit-b 或 comparison 的本轮候选；共享文件系统没有提供权限盲测隔离。AI 的具体模型版本 unknown，不声称异构模型评测。

## 分层判断

| 自举的含义 | 判断 | 成立条件／边界 |
| --- | --- | --- |
| 用本仓库的 AGENTS、协议、task、检查和 Git 流程改进本仓库 | 已具备 | AI 或人实际读规则并执行；母模板 task 使用维护路径，分发状态保持空白 |
| 安装器把自己的协议、管理器和检查器安装给新工程，随后更新自身规则 | 已实现 | 已有 Python、Git、可读取的 Git 来源；只接受已提交源码；更新须有基线，冲突仍需处理 |
| 已安装副本再次充当安装来源 | 技术上成立，需整理分发种子 | 本轮二代安装实测成功；不会自动把第一代实际登记恢复为空骨架 |
| 从默认分发副本再生完整母模板开发／验证能力 | 未实现 | 测试、CI、maintenance 与工作台不在默认 manifest；需保留或重新获取母仓库 |
| 自主启动真实 AI、自动接力、独立测试、按失败反馈修复并发布新模板 | 未实现完整闭环 | 工作台有任务状态和前台适配器契约，实际客户端适配及生命周期仍需验证；发布和实际 AI 工作不由模板自行提供 |

这里的“已具备”是工程流程可执行的判断，不表示规则文本具有强制执行权限，也不意味着无需人工启动或外部运行环境。

## 源码和协议证据

| 结论 | 文件与行号 | 可复核事实 |
| --- | --- | --- |
| 母模板按自身协议维护，维护状态与分发骨架分离 | `AGENTS.md:5–15`；`docs/maintenance/README.md:3–19` | 母仓库有维护入口、scope／task／CURRENT 约定及检查命令；根任务种子保持空白 |
| 协议本身提供接受任务、所有权、审查和提交约束 | `.agents/PROTOCOL.md:5–18,26–33` | 有唯一主目录、明确接受、串行整合、Git 验证与不互读首稿要求；规则也明确登记不等于在线 |
| 安装器能被自身分发 | `.agents/template_manifest.json:4–38`；`tools/template_manager.py:126–140,196–225` | 清单含 manager 与 checker；初始化从 Git 对象读取清单并写入基线，可建立独立 Git 和首提交 |
| 更新是基于已提交版本的变更传播 | `tools/template_manager.py:119–125,260–312,410–434` | clone 不 checkout；更新读取 state 的 source／ref，尝试三方合并，冲突不应用，完成后提示工程检查与提交 |
| 默认副本不是完整母仓库 | `.agents/template_manifest.json:4–38`；`docs/maintenance/README.md:34–36` | manifest 不包含 tests、CI、maintenance、agent_workbench；本轮安装副本验证相应目录／工具缺失 |
| 自复制不会自动清空业务登记 | `tools/template_manager.py:21–25,134–138,212–215,268–270` | SEEDS 可以进入来源清单；init 原样复制 seed，只有更新时对已有 protected 路径跳过 |
| 工作台有协调与验证反馈状态机 | `tools/agent_workbench.py:236–279,323–356` | 原子认领、scope／角色检查、开发版本 awaiting_review、独立测试 revision 匹配、失败恢复 todo |
| 状态机不直接完成真实 AI 工作 | `tools/agent_workbench.py:565–645,654–657` | dispatch 需要操作者注册 command 和 backups；无 command 返回 manual；只消费适配器 JSON 结果，不自己生成代码或测试 |
| 工作台测试的自动接力是模拟适配器 | `tests/test_agent_workbench.py:207–230` | 临时 Python 程序发 checkpoint、退出 75、输出固定 resumed-commit；未调用真实模型 |
| 检查通过不能证明协作事实正确 | `tools/check_template.py:90–134`；`.agents/PROTOCOL.md:33` | 检查文件、编码、链接和 `.agents/tasks` 状态；不检查真实 AI 是否上线，不验证研究结论；维护任务路径不在该 status 扫描范围 |

## 本轮独立实测

可复现脚本：[validate_replication.py](validate_replication.py)。运行：

```powershell
python results/BOOT001-CODEX/run-001/audit-a/validate_replication.py
```

该脚本创建本人专属临时 Git 仓库，用母仓库指定提交安装第一代，提交一项明确标记的登记种子，再直接运行第一代内的管理器安装第二代。临时测试身份仅用于隔离 fixture，不改母仓库、全局 Git 配置或来源代码。原始输出见 [verification.txt](verification.txt)。

| 验证 | 结果 |
| --- | --- |
| 第一代安装清单 | 33 项 |
| 第一代包含 template_manager | True |
| 第一代包含 tests／agent_workbench／maintenance | 均 False |
| 第一代自己的 manager 安装第二代 | 成功 |
| 第二代 state.source 指向第一代 Git 仓库 | True |
| 第二代继承第一代登记种子标记 | True |
| 第二代 check_template | 退出 0；`TEMPLATE_OK files=33` |
| 执行环境 | Windows；Python 3.13.8；Git 2.47.1.windows.2 |

登记种子继承不是现有“从母模板安装”路径的错误，因为母模板规则要求 seed 本来就为空。它说明：若要把一个已经使用的业务副本提升为新的分发源，必须先整理登记、task 索引、CURRENT、协调和 README 等种子；目前没有专门的安全导出／提升命令。检查器即使通过，也不认证这些种子是否适合分发。

首次两次尝试因沙箱拒绝临时 Git clone／清理失败；随后沙箱外执行获自动审核允许。一次重试触发安装器拒绝父仓库内嵌套工程，脚本按现有测试做法先创建独立空 Git 仓库后成功。没有因此改动生产实现。完整 unittest 由主实例执行，本人不把尚未取得的结果写成通过。

## 当前缺口和建议

1. 如果用户所说自举是“让这套协作模板持续改进自己”，当前已有可用基础。沿母仓库维护入口执行即可，本轮并行审计本身属于一次实际应用。
2. 如果目标是“安装副本能离线发展为完整的新母模板”，需要定义开发分发包或明确 fork／clone 原仓库流程，再为 seed 整理提供可复核步骤。默认业务安装包保持精简有明确原因，无需为了术语直接扩大 manifest。
3. 如果目标是“真实多个 AI 自主改进和验收”，优先完成一个真实前台适配器的端到端闭环：读契约、修改隔离代码、实际检查点、真实 revision、独立测试反馈、失败修复和新 revision 再验收。代码已有协调入口，不等于这些外部执行能力已经接入。

未验证：真实外部 AI／账户接入、跨操作系统本轮运行、真实额度耗尽后的进程停写、后台残留写者、真实独立测试 Agent、完整发布／部署闭环。没有推送、发送外部消息或启动桌面客户端。
