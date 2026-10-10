# 跨客户端消息与人工交接工具

2026-10-01，原作者 gpt-relay / RELAY001；2026-10-11 迁入独立仓库。可选组件不在默认安装清单中。用户已选择“共享消息和交接，提醒后手动启动接手方”。

## 现在可以做什么

[agent_relay.py](../../tools/agent_relay.py) 用 Python 标准库提供 send、inbox、ack 和浏览器收件箱。客户端只需能运行本地命令，并能访问同一个主协作目录；不要求同一个模型供应商，不调用模型、不消耗推理 token。

通知队列保存到主目录 .agent-relay/inbox.sqlite3，SQLite 事务负责多个客户端并发投递。正式消息、任务、交接继续在原有 .agents 目录中维护；运行队列不进 Git、不代写共享任务板。工具的 ack 只代表收件箱已读，不表示 Agent 接受任务，更不自动修改 owner。

每次 send 创建新消息；重试会产生新 ID，请在正文引用同一个正式消息编号供接手方去重。ack 可重复执行。运行队列没有自动清理功能，先以小规模本机使用为目标。

## 打开收件箱

本机须有 Python 3.9+（当前测试环境可用）。使用 [start_agent_relay.cmd](../../tools/start_agent_relay.cmd) 时，必须传入业务主目录，例如 start_agent_relay.cmd "H:/Project/my-project"；保持启动终端开着。或在 PowerShell 运行：

```powershell
python H:\Project\agent-project-template\tools\agent_relay.py --root "H:\Project\my-project" serve
```

默认仅监听 127.0.0.1，使用系统分配的空闲端口。启动后自动打开浏览器，完整 URL 含本次会话令牌。若浏览器没有打开，将终端显示的完整地址复制到浏览器。关闭终端／Ctrl+C 停止服务，重启后须使用新地址。

在网页填写收件 Agent ID，如 wb。网页每 5 秒查询该收件箱，标题显示未读数量，点击“开启提示音”后对本次打开页面后新到达的未读消息播放短音。初次加载只显示既有消息，不补播历史提示音。浏览器后台节流、静音、休眠或关闭页面可能延迟／阻止提示音；本版没有 Windows 托盘或系统通知服务。

每条消息可“复制接手提示词”与“标记已读”。复制内容包含主目录、任务、交接路径和接手核对要求。把它粘贴到目标客户端并发送；已读按钮本身不启动客户端。

启动器缺少业务目录会报用法并退出，不把模板仓库当作目标工程；使用业务工程 git config 返回的主目录，工具不自动推断或修改 Git 配置。

## 客户端用法

给每个客户端复制 [通用提示词](agent-relay-prompt.md)，替换自己的 ID 和实际任务。示例中的 gpt／wb／ds／zcode 是命名建议，不代表在线、已登记或已接受任务。先在各客户端验证它确实可以执行 python 和读取主目录。

以下仅是演示命令，不意味着向 WorkBuddy 分配了 RELAY001；实际使用须替换为已授权的任务 ID。工具要求 task 文件已存在，交接／额度通知还要求发送者自己的交接文件已存在。

```powershell
python H:\Project\agent-project-template\tools\agent_relay.py --root "H:\Project\my-project" send --from gpt-relay --to wb --task RELAY001 --kind handoff --body "已停止编辑。请先读取交接文件和当前 task，核对范围后回复是否接手。"
python H:\Project\agent-project-template\tools\agent_relay.py --root "H:\Project\my-project" inbox --agent wb
python H:\Project\agent-project-template\tools\agent_relay.py --root "H:\Project\my-project" ack --agent wb --id 1
```

消息类型 message 表示一般提醒，handoff 表示移交提议，quota 表示额度相关提醒；三者都不改变正式任务。接收者核对 Git 状态、原执行者已停止，再写自己的正式确认，由 integrator 更新 owner。

工具只读正式 task／handoff，Agent 自己保存正式交接文件的权限由客户端配置决定。只安装本工具不能改变其文件沙箱权限。

## 提示词、MCP 与自动调度的差别

提示词规定何时保存检查点、何时收发消息。本地队列完成实际持久传递，网页负责人工提醒。后续可以把同一队列封装为 MCP 工具，但 MCP 支持收发工具调用，不足以证明客户端会被外部消息自动唤醒。

官方文档可确认的接口（查阅日期 2026-10-01）：

| 客户端 | 已确认的公开能力 | 本次没有验证的部分 |
| --- | --- | --- |
| Codex | [MCP 支持本地 STDIO 与 HTTP](https://learn.chatgpt.com/docs/extend/mcp?surface=cli)；[App Server](https://learn.chatgpt.com/docs/app-server) 提供 account/rateLimits/read、额度更新通知与 turn/start | 用户本机版本／登录可用性、特定模型的实际额度、驱动现有桌面会话 |
| WorkBuddy | [官方 MCP 接入文档](https://www.codebuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/MCP-Guide) | 赠送积分查询 API、空闲会话外部唤醒接口、本地 CLI 执行效果 |
| ZCode | [官方 MCP 配置文档](https://zcode.z.ai/cn/docs/mcp-services) | 100M 配额余额查询、会话自动启动接口、本机实际产品版本 |
| DeepSeek Harness | [官方源码入口](https://github.com/deepseek-ai/deepseek-harness) | 用户实际安装形态、额度查询与调度插件接口、6 元余额与 Flash 配置 |

用户自述的 Plus、3000 积分、6 元、100M token 采用不同计量，不能直接相加、转换为统一余额或据此认定哪个模型适合所有任务。本工具不读取账户，不验证赠送额度，不使用 API Key。

全自动轮换需要常驻程序和各客户端适配器：额度状态来源（接口或事件）→任务检查点→停止／确认原执行者→选择有额度的接手方→实际启动接口→失败回退。可自己编写辅助软件，不必购买第三方软件。只在有接口时查额度；其他客户端未验证前标为 unknown，不能当作零额度或无限额度。没有额度事件的客户端可低频查询；不需要靠模型不停询问。

额度用尽后的模型可能无法执行任何交接动作，故应提前／定期保存检查点；外部程序负责处理明确错误信号。HTTP 429 可能是临时请求限速，认证错误、网络超时也不是余额耗尽证据。本次交付不包含自动余额检测、后台客户端启动或模型调度，不读取客户端凭据。

## EXE 与验证边界

当前提供源码与双击 .cmd 入口。测试环境没有 PyInstaller，未安装打包依赖、未生成 EXE。若以后需要免 Python 的分发包，可在具备 PyInstaller 的 Windows 环境运行下列构建，再在干净机器验收：

```powershell
python -m PyInstaller --onefile --name agent-relay tools/agent_relay.py
.\dist\agent-relay.exe --root "H:\Project\my-project" serve
```

EXE 打包不会增加唤醒 Agent 或查询余额的能力。启动器／命令行均只是调用同一套本地队列逻辑。数据库与 Agent ID 是本机协作标签，不是密码学认证；有主目录访问权限的程序可自报 ID。网页接口的随机令牌防止普通跨网页访问，不提供远程共享或账户权限管理。

已验证项见 [维护记录](../maintenance/CURRENT.md) 与 [原 RELAY001 task](../maintenance/legacy/live2d-normaldrive/.agents/tasks/RELAY001.md)。浏览器空收件箱已实际打开并确认无读取错误；四客户端真实互相收发、浏览器声音与系统剪贴板、EXE 分发尚需实际使用确认。
