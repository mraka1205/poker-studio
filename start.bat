@echo off
title Poker Studio Launcher

echo Starting Poker Studio Backend (FastAPI on Port 8000)...
start "Poker Studio - Backend" cmd /k "cd /d "%~dp0" && python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload"

echo Starting Poker Studio Frontend (Vite on Port 5173)...
start "Poker Studio - Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo Waiting for services to initialize...
ping 127.0.0.1 -n 4 >nul

echo Opening browser at http://127.0.0.1:5173...
start http://127.0.0.1:5173

echo.
echo ======================================================
echo   Poker Studio is running!
echo   Backend:  http://127.0.0.1:8000
echo   Frontend: http://127.0.0.1:5173
echo   Close the opened terminal windows to stop.
echo ======================================================
pause
