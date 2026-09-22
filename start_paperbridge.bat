@echo off
title PaperBridge AI Launcher
echo ===================================================
echo           PaperBridge AI - Starting Services
echo ===================================================

echo [1/3] Launching Flask Backend API (Port 5000)...
start "PaperBridge-Backend" /min cmd /k "cd /d C:\Users\tznma\.gemini\antigravity\scratch\paperbridge-ai\backend && python app.py"

echo Waiting 2 seconds for backend to initialize...
timeout /t 2 /nobreak >nul

echo [2/3] Launching Vite React Frontend (Port 5173)...
start "PaperBridge-Frontend" /min cmd /k "cd /d C:\Users\tznma\.gemini\antigravity\scratch\paperbridge-ai\frontend && npm run dev"

echo Waiting 2 seconds for frontend to initialize...
timeout /t 2 /nobreak >nul

echo [3/3] Opening your browser to http://localhost:5173 ...
start http://localhost:5173

echo ===================================================
echo PaperBridge AI is live!
echo Close this window whenever you want.
echo To shut down the servers later, double-click stop_paperbridge.bat
echo ===================================================
pause
