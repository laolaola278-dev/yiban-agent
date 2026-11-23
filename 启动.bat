﻿﻿@echo off
chcp 65001 >nul
title 易班百事通 · 一键启动
cd /d "%~dp0"

echo ============================================
echo    易班百事通 · 一键启动（后端+前端）
echo ============================================
echo.

REM ---------- [1/6] Python 自检 ----------
where python >nul 2>nul
if errorlevel 1 (
    echo [错误] 未找到 python，请安装 Python 3.10+ 并勾选 Add to PATH
    pause & exit /b 1
)

REM ---------- [2/6] 主项目环境 ----------
if not exist ".venv\Scripts\python.exe" (
    echo [2/6] 首次运行：创建虚拟环境...
    python -m venv .venv
)
call ".venv\Scripts\activate.bat"
python -c "import openai, faiss, pdfplumber, docx, dotenv, fastapi, uvicorn" >nul 2>nul
if errorlevel 1 (
    echo [2/6] 安装依赖（仅首次）...
    python -m pip install -q -r requirements.txt
) else (
    echo [2/6] 依赖已就绪
)

REM ---------- [3/6] .env 配置 ----------
if not exist ".env" (
    echo [3/6] 未找到 .env，生成模板...
    copy /y ".env.example" ".env" >nul
    echo   请填入两个 Key 后保存，再重新双击本脚本：
    echo     CHAT_API_KEY  = DeepSeek   https://platform.deepseek.com
    echo     EMBED_API_KEY = SiliconFlow https://cloud.siliconflow.cn（bge-m3 免费）
    echo   （单智谱 Key 备选方案见 README）
    start notepad .env
    pause & exit /b 1
)
echo [3/6] .env 已就绪

REM ---------- [4/6] 知识库 ----------
if not exist "data\corpus\corpus.jsonl" (
    echo [4/6] 首次构建知识库（64 篇校规切片+向量化，约 2-5 分钟）...
    python scripts\ingest.py
    if errorlevel 1 (
        echo [错误] 建库失败，请查看报错
        pause & exit /b 1
    )
) else (
    echo [4/6] 知识库已就绪（更新 data\raw 后请双击 重建知识库.bat）
)

REM ---------- [5/6] 后端网关 8010 ----------
powershell -NoProfile -Command "try { Invoke-WebRequest -Uri 'http://127.0.0.1:8010/health' -UseBasicParsing -TimeoutSec 3 | Out-Null; exit 0 } catch { exit 1 }"
if errorlevel 1 (
    echo [5/6] 启动后端网关（8010）...
    start "yiban-backend" /min cmd /c "cd /d "%~dp0" && .venv\Scripts\python.exe backend_api.py > backend_run.log 2>&1"
    timeout /t 6 /nobreak >nul
) else (
    echo [5/6] 后端网关已在运行
)

REM ---------- [6/6] kotaemon 前端 7860 ----------
powershell -NoProfile -Command "try { Invoke-WebRequest -Uri 'http://127.0.0.1:7860/' -UseBasicParsing -TimeoutSec 3 | Out-Null; exit 0 } catch { exit 1 }"
if errorlevel 1 (
    if exist "E:\hds(js)\workspace\kotaemon\run_server_real.bat" (
        echo [6/6] 启动 kotaemon 前端（7860）...
        start "kotaemon-server" /min "E:\hds(js)\workspace\kotaemon\run_server_real.bat"
        timeout /t 20 /nobreak >nul
    ) else (
        echo [错误] 未找到 kotaemon 部署，请先完成 kotaemon 部署（见 README）
        pause & exit /b 1
    )
) else (
    echo [6/6] kotaemon 前端已在运行
)

:done
echo.
echo ============================================
echo   启动完成！
echo   主界面 : http://localhost:7860   （admin/admin 登录）
echo   后端API: http://127.0.0.1:8010/v1
echo.
echo   首次接入（kotaemon 页面内）:
echo     Settings -^> OpenAI-compatible -^>
echo     API Base: http://127.0.0.1:8010/v1
echo     API Key: 任意（如 sk-local）  Model: yiban-agent
echo ============================================
echo   关闭全部: 双击 停止.bat
echo.
timeout /t 8 >nul
start http://localhost:7860
