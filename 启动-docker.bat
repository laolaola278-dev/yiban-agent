@echo off
chcp 65001 >nul
title 易班百事通 - Docker 一键启动
cd /d "%~dp0"
echo ============================================
echo   易班百事通 Docker 部署（后端8010 + 前端7860）
echo ============================================
echo.
docker info >nul 2>nul
if errorlevel 1 (
    echo [错误] Docker 未运行，请先启动 Docker Desktop
    pause & exit /b 1
)
if not exist .env (
    echo [错误] 缺少 .env，请先运行 启动.bat 生成并填写 API Key
    pause & exit /b 1
)
echo 构建并启动容器（首次拉取镜像约 2-4GB）...
docker compose up -d --build
if errorlevel 1 (
    echo [错误] 启动失败，请查看上方日志
    pause & exit /b 1
)
echo.
echo 等待服务就绪...
timeout /t 15 /nobreak >nul
start http://localhost:7860
echo.
echo 完成！前端 http://localhost:7860  后端 http://127.0.0.1:8010/v1
echo 停止：docker compose down
pause