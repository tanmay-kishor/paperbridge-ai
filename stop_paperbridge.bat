@echo off
title PaperBridge AI Stopper
echo ===================================================
echo           PaperBridge AI - Stopping Services
echo ===================================================

echo Stopping background servers on ports 5000 and 5173...

for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5000" ^| findstr "LISTENING"') do (
    taskkill /f /pid %%a >nul 2>&1
)

for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5173" ^| findstr "LISTENING"') do (
    taskkill /f /pid %%a >nul 2>&1
)

echo PaperBridge AI servers have been stopped.
echo ===================================================
pause
