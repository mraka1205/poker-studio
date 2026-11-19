@echo off
chcp 65001 >nul
title Poker Studio Launcher
echo ======================================================
echo   در حال راه‌اندازی استودیو کمدی و آموزش پوکر...
echo ======================================================

echo [1/2] در حال اجرای سرور بک‌اند (FastAPI - Port 8000)...
start "Poker Studio - Backend" cmd /k "python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload"

echo [2/2] در حال اجرای فرانت‌اند (Vite - Port 5173)...
start "Poker Studio - Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo در حال باز کردن مرورگر...
timeout /t 3 >nul
start http://127.0.0.1:5173

echo.
echo ======================================================
echo   استودیو با موفقیت اجرا شد!
echo   برای خاموش کردن کافیست پنجره‌های ترمینال باز شده را ببندید.
echo ======================================================
pause
