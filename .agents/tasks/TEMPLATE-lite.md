# <TASK-ID> <标题>

- status: todo
- assignment: proposed
- collaboration_mode: serial
- mode_source: 填写真实的用户指令／父任务／已授权工程默认来源
- owner: <agent-id>
- created: YYYY-MM-DD
- updated: YYYY-MM-DD
- base_commit: 待记录
- version_tag: 无

## Objective

具体目标与验收；仅用于已明确的单人串行任务，owner 兼任该任务 integrator。
涉及业务代码时引用业务工程自己的 README 工程约定或其指定文档，并写任务实际验收命令；缺项可以先调查补齐，不要求调查任务先确定整个技术栈。

## Scope

明确可写文件／目录，不省略防覆盖边界。
旁路模式注明协作根与实际业务工作树；base_commit 记录业务基线，Completed 记录真实业务交付 SHA，两个仓库分别审查提交。

## Completed

真实产出及相关文件链接。

## Verification

实际检查结果、覆盖与未验证项；标签实际存在时才填写 version_tag。

## Remaining

剩余工作／阻塞，无则写无。有中断或移交时链接真实交接；模板备注／mechanisms 按需写，不强制增加字段。
