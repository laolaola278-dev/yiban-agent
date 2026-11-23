@echo off
chcp 65001 >nul
title 易班百事通 · kotaemon 前端 (7860)
echo 启动 kotaemon（HF 离线模式）...
powershell -NoProfile -Command "try { Invoke-WebRequest -Uri 'http://127.0.0.1:7860/' -UseBasicParsing -TimeoutSec 3 | Out-Null; exit 0 } catch { exit 1 }"
if not errorlevel 1 (
    echo kotaemon 已在运行
) else (
    if exist "E:\hds(js)\workspace\kotaemon\run_server_real.bat" (
        start "kotaemon-server" /min "E:\hds(js)\workspace\kotaemon\run_server_real.bat"
        echo 等待就绪（20-40 秒）...
        timeout /t 20 /nobreak >nul
    ) else (
        echo [错误] 未找到 kotaemon 部署（E:\hds(js)\workspace\kotaemon）
        pause & exit /b 1
    )
)
start http://localhost:7860
echo 登录: admin / admin
pause
