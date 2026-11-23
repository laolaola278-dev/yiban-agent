@echo off
chcp 65001 >nul
title 易班百事通 · 后端网关 (8010)
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo [错误] 请先运行 启动.bat
    pause & exit /b 1
)
call ".venv\Scripts\activate.bat"
echo 后端 API: http://127.0.0.1:8010/v1  (Ctrl+C 停止)
echo kotaemon 接入: Settings -^> OpenAI-compatible -^> Base http://127.0.0.1:8010/v1 -^> Model yiban-agent
python backend_api.py
pause
