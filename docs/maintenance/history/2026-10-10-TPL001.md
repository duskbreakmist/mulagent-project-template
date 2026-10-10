# 母模板维护记录

## 当前任务

2026-10-10 TPL001 / gpt：首版 GitHub 发布，以及本地新工程安装／既有工程更新工具。

## 方案与范围

基于原 29 文件协作模板增加 README、安装更新说明和标准库管理器，安装清单共 32 文件。清单仅含分发骨架；测试、CI 和此维护记录不由安装器分发。分发的登记、任务索引、CURRENT 保持空白。

初始化拉取 Git 快照并建立工程独立基线；更新保护状态种子、按文件旧基线三方合并，冲突整轮不应用。元数据需提交，备份与锁留本机；不配置业务 origin、执行上游脚本或自动推送业务工程。

## 验证

19 项本地 Git 行为测试、18 项模板独立复制测试已通过；最终独立发布目录 37 项复测全部通过，TEMPLATE_OK files=32；首版 GitHub CI Ubuntu／Windows 成功，公开远端 init／update／登记保留验收通过。第一次沙箱测试因 Windows 临时目录权限失败，提升权限后完成。早先自动审批额度故障已恢复，未绕过权限。

## 发布结果

main／v0.1.0 首版代码提交 921cd9ee8fb3a044efbbae1239bd438cfda82bf0；is_template=true。CI：https://github.com/duskbreakmist/mulagent-project-template/actions/runs/38038954158。实际临时工程初始提交成功、无模板 origin，定制登记后预览／重复更新均保持原样。

交付范围无待办；复杂业务定制仍按实际工程验证。

## v0.1.1 兼容修正

三方合并临时文件使用 UTF-8 字节写入，避免 Python 3.10 才增加的 Path.write_text newline 参数；固定版本示例改为 v0.1.1。实际非重叠三方合并回归 1 项通过。本机使用较新 Python；未直接运行 Python 3.9，兼容修正按标准库 API 边界核对。

公开跨版本验收通过：v0.1.0 安装的独立工程升级到 main／v0.1.1，仅更新两项模板文件；定制登记保留，预览只读，没有模板 origin，更新后检查 32 项通过，提交后重复更新 ALREADY_CURRENT。临时工程已清理。修正版 c6e3e0cb7aab86247d66d869e7faa39055614dfc 的 Windows／Ubuntu CI 全部成功：https://github.com/duskbreakmist/mulagent-project-template/actions/runs/38040232118。HTTP/2 推送遭遇临时 HTTP 500，改为单次 HTTP/1.1 传输后完成，未改全局配置。
