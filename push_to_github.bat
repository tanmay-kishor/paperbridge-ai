@echo off
title Push PaperBridge AI to GitHub
echo ===================================================
echo   Pushing PaperBridge AI to GitHub (tanmay-kishor)
echo ===================================================
cd /d C:\Users\tznma\.gemini\antigravity\scratch\paperbridge-ai

git remote remove origin >nul 2>&1
git remote add origin https://github.com/tanmay-kishor/PaperBridge-AI.git
git branch -M main

echo Running: git push origin main
git push origin main

echo.
if %ERRORLEVEL% EQU 0 (
    echo ===================================================
    echo SUCCESS: Project has been uploaded to GitHub!
    echo Refresh your repository page:
    echo https://github.com/tanmay-kishor/PaperBridge-AI
    echo ===================================================
) else (
    echo.
    echo Push encountered an error or needs your GitHub authorization.
)
pause
