@echo off
chcp 65001 >nul
title 易班百事通 · 跑评测出数据
cd /d "%~dp0"
echo 跑 eval\testset.jsonl 全量评测（逐条 PASS/FAIL + 通过率 + 平均耗时）
echo 注意：需后端知识库已建好（corpus.jsonl 存在）且 .env 已填 Key
if not exist ".venv\Scripts\python.exe" (
    echo [错误] 请先运行 启动.bat
    pause & exit /b 1
)
call ".venv\Scripts\activate.bat"
python scripts\eval.py
echo.
echo 截图放 PPT 第 7 页（实测数据）。
pause
