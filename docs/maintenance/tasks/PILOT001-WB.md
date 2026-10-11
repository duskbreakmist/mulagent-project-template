# PILOT001-WB 业务工程多 AI 串行试点验收

- status: done
- owner: wb-hy4-20261011
- created: 2026-10-11
- updated: 2026-10-11
- base_commit: 3cdc987（记录时；v0.2.0 发布记录）
- 授权：用户 2026-10-11 23:43 指令“记录吧，我等下让codex改”

## Objective

只读评审用户在 H:/Project/test_template_a 进行的业务工程试点，作为 BOOT004 候选 5（真实前台 AI + 独立测试最小闭环）的验收证据记入维护层。不修改试点工程与母模板生产实现。

## 事实

- 安装链：GitHub clone `../agent-template-tools`（f290f2a）→ `init --root . --commit`（DOC003 可移植安装流程实测）；试点工程 `template-state.json` 记录 revision f290f2a 与 33 项逐文件 sha256。试点版本早于 v0.2.0（35 项，含 LICENSE）。
- 交付链（5 提交，同一 Git 身份，标签 `[TASK-ID][agent-id]`）：
  - `598b743` BOOTSTRAP 模板初始化
  - `6b36166` FEAT-001 dsh-1（DSH／deepseek-flash）：网页版俄罗斯方块 + 补齐工程约定
  - `fa1fc9c` FEAT-002 wb-1（WorkBuddy／hy4）：ImGui 桌面版单 exe（vendored 1.93.0，build.bat）
  - `52b04d3` FEAT-003 dsh-1：桌面版排行榜 Top 10 + 本地存档
  - `7dd1201` FEAT-004 zcode-1（ZCode／GLM-5.3-Flash）：双端暂存方块（Hold Piece）
- 跨 AI 代码续写：FEAT-003 基于 wb-1 的 C++ 续写；FEAT-004 同时修改 dsh-1 的 `tetris.html` 与 wb-1 的桌面端并保持两端测试全绿。

## 验证（本轮独立复验，2026-10-11 23:40）

- `tools/check_template.py --root .`：TEMPLATE_OK files=33
- `node tests/tetris_logic.test.mjs`：全部断言通过
- `dist/tetris_imgui.exe --selftest`：48 项通过，退出码 0
- `dist/tetris_imgui.exe --storage-selftest`：2 项通过，退出码 0
- Git：工作树干净；`build/`、`dist/`、`.test-tmp/` 按 .gitignore 忽略；`third_party/imgui` vendored 源码入库
- FEAT-002/003 任务记录含真实失败→修复→复测过程（消行函数连续两行只消 1 行的 bug 被自检抓出修正；名次断言语义修正）

## 协议执行观察

- 登记表 3 个 agent（dsh-1／wb-1／zcode-1）齐全，能力注明自报，证据指向真实交付物
- 任务板 4 项 done；task 正文含 status/assignment/mode_source/base_commit 并引用 `docs/project.md` 工程约定——ENG001 新增的约定字段当天即被正确使用
- CURRENT 摘要含产出／验证／未验证／模板备注；两条环境反馈经模板备注通道记录：沙箱拦截 `reg.exe`（build.bat 已内置无注册表回退）、已存在 `.git` 无沙箱写权限需一次完全权限提交
- 根 `coordination.md` 保持 vacant：纯串行未用共享整合者，符合“普通任务不重复写五处”的克制边界

## 对 BOOT004 候选 5 的判定

串行接力层面实证成立：多 harness 接力开发、跨 AI 代码续写、任务内失败→修复→复测。仍未覆盖：并行 worktree 协作、workbench 真实供应商适配器、跨机器、多 AI 并发写共享文件。用户已预告后续交由 codex 改进。

## Remaining

- 试点两条环境反馈可评估进模板指南或已知问题说明（受限沙箱下的构建路径、写权限提升提示）
- 未覆盖项保持候选状态；可选实测 test_template_a 从 f290f2a 升级到 v0.2.0 的 update 路径（含 LICENSE 不覆盖业务根的验证）
- 本任务不改生产实现；提交后推送按惯例由用户或指定者执行
