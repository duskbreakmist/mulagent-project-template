# BOOT002-ZCODE run-001 公共输入（fixed，由 integrator 维护）

- base_commit: 8d2645f80f43df4932515f5b6650a05e53410f5b
- 目标仓库：H:/Project/agent-project-template（母模板维护仓库）
- 开始时间：2026-10-11 16:00+08:00 前后；各候选并行启动

## 公共问题

当前项目能否实现自举？请给出：

1. 你对「自举」在本项目的可操作定义（建议区分：安装分发自举／协议自举 self-hosting／工具自检／协作自举等层次，可自行增删）；
2. 每层次的判定与证据（引用具体文件、命令与结果）；
3. 成立条件、能力缺口、未验证边界；
4. 一句话总结论（能／不能／有条件能）。

## 允许的验证手段（各候选自行执行，不得引用他人结果代替实测）

- `python tools/check_template.py --root .`（只读检查）
- `python -m unittest discover -s tests -v`（在母仓库）
- 在**系统临时目录**（如 `%TEMP%`）新建空目录，用本地源验证安装自举：
  `python tools/template_manager.py init --root <临时目录> --source H:/Project/agent-project-template --ref main --commit`，再对安装结果运行 check_template 并检查其独立 Git。
- 只读 Git／文件检查。

## 盲态与边界

- 每个候选只写 `results/BOOT002-ZCODE/run-001/<自己的 agent-id>/` 下的 RUN.md 与 report.md；首稿交付前不读其他候选目录，不读 results/BOOT001-CODEX/（并行轮）。
- 不修改仓库其他任何文件；不做 git add／commit／push；实验产物只留在临时目录。
- 报告写结论、证据与验证，不记录内部思考链；无法确认的版本信息写 unknown。
- 评审标准：判定正确性、证据可复现性、层次划分清晰度、对缺口与未验证项的诚实度；篇幅与相互赞同不作为正确性依据。
