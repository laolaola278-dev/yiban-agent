@echo off
chcp 65001 >nul
title 易班百事通 · 重建知识库
cd /d "%~dp0"
echo 扫描 data\raw 下全部校规文件（当前 64 篇），重新切片并向量化。
echo 更新过校规文件后运行本脚本；注意 kotaemon File Collection 里的旧索引需手动删除重传。
if not exist ".venv\Scripts\python.exe" (
    echo [错误] 请先运行 启动.bat 完成首次安装
    pause & exit /b 1
)
call ".venv\Scripts\activate.bat"
python scripts\ingest.py
echo.
echo 完成。双击 启动.bat 重启后端生效。
pause
