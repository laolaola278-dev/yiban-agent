﻿﻿@echo off
chcp 65001 >nul
title 易班百事通 · 全部停止
echo 停止 kotaemon(7860) + 后端(8010)...
powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | Where-Object {$_.CommandLine -like '*app.py*' -or $_.CommandLine -like '*backend_api*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }"
echo 完成。守护脚本 KotaemonWatchdog 会在 5 分钟内重新拉起 kotaemon。
echo 如需彻底停掉守护: schtasks /End /TN "KotaemonWatchdog"
pause
