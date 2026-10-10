@echo off
setlocal
rem 工具与业务工程已分离，调用者必须显式提供主协作目录。
if "%~1" == "" (
    echo Usage: start_agent_relay.cmd "H:\Project\my-project"
    exit /b 2
)
python "%~dp0agent_relay.py" --root "%~1" serve
if errorlevel 1 pause
