# 旧初始化器

agent_bootstrap.py 是旧单文件方案的兼容实现，不是当前模板安装入口，也不在安装清单中。新工程用 tools/template_manager.py init，已有工程用 adopt/update。

旧 11 项并发／恢复测试在 tests/test_legacy_bootstrap.py；原始文件按来源路径归档。不要用它恢复当前模板协议。
