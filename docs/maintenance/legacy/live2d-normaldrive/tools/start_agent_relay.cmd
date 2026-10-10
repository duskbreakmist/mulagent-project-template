@echo off
setlocal
rem 使用启动器所在工程作为主目录；其他 worktree 应显式指定主协作目录。
python "%~dp0agent_relay.py" --root "%~dp0.." serve
if errorlevel 1 pause
