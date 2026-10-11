# 五项需求驱动的 Agent 协作工作台

这是一个可运行的本地原型，源码为 [agent_workbench.py](../../tools/agent_workbench.py)，只用 Python 3.9+ 标准库。它管理登记、任务认领、接力、角色反馈、调研封存和人工介入。它与原 relay 分开，当前不在默认安装清单；使用者明确指定唯一业务主目录。

## 从需求到行为

| 用户需求 | 工作台行为 | 客户端还要负责的部分 |
| --- | --- | --- |
| 一个 Agent 没额度，换其他 Agent | 前台监督器接收适配器约定的额度退出码，保存最近检查点，确认停写后按有序 backups 接力；旧代次失效 | 翻译真实额度错误、提供启动入口，保证前台退出后没有后台写者 |
| 不同功能同时开发 | 原子认领；scope 不相交的 collaborative 任务可并行；串行任务独占阶段 | 各自在实际 worktree 开发，不绕过认领工具改共享文件 |
| 开发与测试职责分开、互相反馈 | 保留开发参与者历史，禁止其验收同一功能；按 revision 验收，反馈自动进入开发者收件箱 | 独立测试客户端只加载契约、交付代码和测试计划，不带入开发者完整会话 |
| 相同问题同时调研、指定汇总 | 固定公共输入与标准；每人一个不可覆写首稿；状态看板不暴露正文；关闭轮次后由指定汇总者提交汇总 | 各自查阅原始来源，记录事实／推断／建议；不绕过封存规则读取数据库 |
| 人方便阅读并参与开发 | 本地网页看任务／登记／消息／轮次；暂停与接手；人也可领取任务、写检查点和提交版本；可导出 Markdown | 人确认实际停写、负责发布与重要裁决，继续使用自己的编辑器和 Git |

这些方式可组合在一个工程中，不要求全工程只能选一种：模块开发采用 collaborative；测试是依赖交付版本的另一任务；额度接力替换该任务执行者；调研另建 independent_compare 轮次。

~~~mermaid
flowchart LR
  H[人：任务与裁决] --> W[工作台：登记／任务／消息／检查点]
  W --> D1[开发 A：模块一]
  W --> D2[开发 B：模块二]
  D1 --> V[冻结交付 revision]
  V --> T[独立测试 Agent]
  T --> F[显式测试反馈]
  F --> D1
  D1 -.额度耗尽且确认停止.-> B[备用开发者：读取检查点]
  W --> R[多 Agent 同题调研：分别封存]
  R --> C[收齐或人工截止]
  C --> I[指定汇总者：来源与分歧]
~~~

## 打开人工界面

在母模板目录运行，ROOT 换成已安装协议的业务主目录：

~~~powershell
python tools/agent_workbench.py --root "ROOT" serve
~~~

终端打印完整的本地 URL，包含本次服务令牌。复制该 URL 到浏览器；服务仅监听 127.0.0.1，不自动安装、启动其他客户端或打开窗口。首次打开人工界面会登记 human 本机操作者；已有同名登记保持原样。Ctrl+C 停止服务。网页每 5 秒刷新元数据，收件箱／任务上下文需主动读取；隐藏首稿不随刷新进入公共看板。人可用普通表单创建工作和发送反馈，高级 JSON 操作折叠在下方。

命令行同样可以查看：

~~~powershell
python tools/agent_workbench.py --root "ROOT" status
python tools/agent_workbench.py --root "ROOT" snapshot
~~~

snapshot 输出方便保存为 Markdown 的进度快照；它不是第二份可写任务板。业务源码与正式报告继续通过各工程 Git 管理。运行状态保存在 ROOT/.agent-relay/workbench/state.sqlite3，沿用已有 .agent-relay 忽略规则，不把当前身份分发给其他项目。

## 快速演示

先创建一个新的演示目录，并放置 .agents/PROTOCOL.md（可复制当前协议）。不要对真实运行目录执行 demo：

~~~powershell
python tools/agent_workbench.py --root "演示目录" demo
python tools/agent_workbench.py --root "演示目录" serve
~~~

demo 创建五个明确标注为演示的 Agent 加一个 human，两个正在并行的开发任务、一个待交付后验收的测试任务，以及一个三方调研轮次。它不会调用模型，不会伪造真实客户端已经上线。重复 demo 会拒绝覆盖已有数据库。

## 客户端接入契约

所有客户端先登记独立的会话 ID；同工具两个实例分别用 wb-1、wb-2。登记记录是本地协作标签，未提供密码学身份认证。人可以登记为 human，角色包含 human；注册不会改模型账户或 Git 身份。

建议把请求参数保存为 UTF-8 JSON 文件，再执行：

~~~powershell
python tools/agent_workbench.py --root "ROOT" call join --file join.json
~~~

join.json：

~~~json
{"agent":"wb-1","client":"WorkBuddy 本次会话","roles":["developer"],"workspace":"实际 worktree 绝对路径"}
~~~

模式已明确时记录到任务，不重复弹窗；尚未明确时由实际任务整合者通过本客户端提问工具或文字询问。原型没有强制四个客户端原生弹窗，也不把客户端预选项当作用户回答。

开发任务的 create_task 参数示例：

~~~json
{
  "task":"AUTH001",
  "title":"实现登录模块",
  "kind":"development",
  "mode":"collaborative",
  "scopes":["src/auth"],
  "contract":"按公共接口实现；提交可复现版本，不注入完整开发会话。",
  "backups":["codex-1","wb-1","human"]
}
~~~

任务编号必须是同一用户任务的共同 ID；数据库拒绝重复 ID。不同提示词是否描述同一语义目标需要人／整合者确认，不用文本相似度自动决定。scope 是共同代码树中的逻辑相对路径，各客户端仍在不同 worktree 写代码；父子路径算重叠。

通过 call 执行以下操作；参数均为 JSON 对象：

| 操作 | 参数与行为 |
| --- | --- |
| join | agent、client、roles；可选 command、quota_codes、workspace、foreground |
| availability | agent、state：available / paused / quota_exhausted |
| claim | task、agent；返回 epoch。认领依赖和 scope 在同一 SQLite 事务检查 |
| context | task、agent；只给当前 owner 返回契约、scope、epoch 和最新 checkpoint |
| checkpoint | task、agent、epoch、data；记录 completed／remaining／revision／files／验证等显式信息 |
| finish | task、agent、epoch、result；开发结果须含 revision，进入 awaiting_review |
| create_task | task、title、kind、scopes、contract；可选 dependencies、subject、mode、backups；调研候选可关联 run、slot |
| stop | task、reason、stopped；未确认停止时保留 owner 和 scope 占用 |
| takeover | task、agent、stopped=true；人确认旧执行者停止后接手，旧 epoch 作废 |
| send | sender、recipient、task、body；显式消息，独立调研封存阶段禁止向其他参与者／汇总者发送自由文本 |
| inbox / ack | agent；ack 另传 message 数字 ID；已读不代表接受任务 |
| create_run | run、question、criteria、participants、integrator；固定同题输入与比较标准 |
| submit_report | run、agent、report；claims 含 kind、statement、sources，fact 必须附来源 |
| view_run | run、agent；关闭前只返回本人首稿和提交元数据 |
| close_run | run、actor；收齐后关闭；人可显式 allow_missing=true 截止并记录缺失者 |
| synthesize | run、agent、summary；关闭后仅指定 integrator 可提交最终汇总 |

开发与测试：

1. 开发者提交 revision，例如可复现 Git commit，状态进入 awaiting_review，释放修改范围。
2. 测试任务 kind=test、subject=AUTH001，contract 存独立测试计划。此 subject 自动成为依赖；只有交付冻结后能领取测试。
3. 开发参与历史中的任何会话，即使具有 tester 角色，也不能测试自己的功能。
4. 测试 result 必须含与交付相同的 revision、布尔 passed、明确 feedback。可选 private 保存隐藏用例信息。
5. 只把 revision／passed／feedback 路由给开发者，private 与测试计划不自动转发。失败将开发任务恢复 todo；新 revision 提交后旧测试任务重置，必须重新验收。

“避免隐式泄露”在本原型中指默认上下文和 API 发布门槛：它不继承开发者完整对话，也不把隐藏内容塞进状态摘要。它不是文件系统保密沙箱。数据库文件、任意自报 Agent ID 和本地管理 URL 都属于同一受信任用户的管理边界；真实盲测／隐藏用例要给客户端配置独立上下文、隔离测试资料和必要的文件访问权限。worktree 只隔离修改，不阻止读取其他目录。

调研候选也可以接力：先 create_run 固定 participants，再为某一候选创建 kind=research 的任务，填写 run 和 slot（初始参与者 ID），并指定独立备用研究者。任务上下文自动使用轮次固定的问题和标准。检查点、认领与额度接力沿用普通任务机制，最终通过 finish 的 result.report 提交首稿；系统保留 slot 与实际 author，旧作者不能抢写。另一候选的参与者或已经做过其他候选的备用实例不能兼任此候选，避免伪造多方独立来源。

运行数据库使用版本标记，原型早期数据库的候选／作者字段升级采用追加迁移，保留已有登记、任务、检查点和首稿；遇到更高版本拒绝修改。

## 额度耗尽时的监督与自动接力

自动接力使用进程监督者；额度用完的模型不必还能说出最后一句交接。适配器在每个独立步骤输出一行 checkpoint 事件，监督者立即写入数据库：

~~~json
{"type":"checkpoint","data":{"completed":"请求校验通过","remaining":"补充错误处理","revision":"commit-a"}}
~~~

成功时输出：

~~~json
{"type":"result","data":{"revision":"commit-b","files":["src/auth"],"verification":"相关测试已通过"}}
~~~

stdout 中非 JSON 日志可忽略；stderr 保存在本地日志。实际验证是否真实仍由后续测试者／人验收。

注册可自动执行的适配器时，command 必须是完整参数数组，不能是 shell 拼接文本。quota_codes 是由该适配器明确约定的额度退出码，不默认使用 HTTP 429 或客户端任意报错。foreground=true 仅用于确认退出后所有相关写者都已停止的前台适配器；会启动脱离后台进程的桌面启动器不能设置 true。

~~~json
{
  "agent":"codex-adapter-1",
  "client":"已验证的前台适配器",
  "roles":["developer"],
  "command":["实际可执行文件","实际参数"],
  "quota_codes":[75],
  "foreground":true,
  "workspace":"实际隔离工作目录"
}
~~~

上述 75 是示例适配器协议，不是 Codex、WB、DSH 或 ZCode 的已知退出码。原型没有替这四个客户端提供未经验证的额度查询／启动命令。

~~~powershell
python tools/agent_workbench.py --root "ROOT" dispatch --task AUTH001 --max-hops 5
~~~

监督器按任务 backups 顺序选择可用、角色匹配且无在途任务的会话。它将任务简报路径和 root／task／agent／epoch 放在 AGENT_WORKBENCH_* 环境变量，不把 API Key 放进记录。收到明确额度退出且确认停写，禁用耗尽会话并尝试下一位；保留最新 checkpoint。没有 command 的接手者进入 manual，工作台发本地通知并给出 context，由人启动客户端。

未知错误返回 adapter_error，不能当成余额耗尽自动轮换；未知进程生命周期进入 stopping 并继续占用范围。长时间无心跳仅显示需核查，不自动释放占用。监督器只自动执行已由操作者注册的参数数组和有序备用名单，不会驱动当前桌面会话、发送邮件或读取账户凭据。

## 验证与下一步

本轮场景测试覆盖五进程竞争、不同模块并行、父子 scope 冲突、检查点接力与旧代次拦截、开发／测试分离、revision 验收、私有测试不自动转发、首稿封存和指定汇总、人工接手、本地 HTTP 令牌、模拟前台适配器额度退出接力。

~~~powershell
python -m unittest discover -s tests -p test_agent_workbench.py -v
~~~

下一步实际接入各客户端时，要分别验收：规则是否加载、CLI/MCP 是否能调用、额度错误是否可观察、客户端是否能由外部前台启动、退出后是否仍有写者、检查点与代码版本是否一致。自动测试由本会话编写和运行，不算独立测试 Agent 已完成本原型审查；模拟适配器成功也不等于四客户端实机互通。
