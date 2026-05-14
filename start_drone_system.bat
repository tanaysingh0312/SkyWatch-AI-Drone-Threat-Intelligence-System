@echo off
title Drone Security Analyst Agent - Launcher
echo ======================================================
echo    🚁 Drone Security Analyst Agent - Startup Script
echo ======================================================
echo.

:: 1. Verify Python
echo [1/4] Checking Python...
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python not found in PATH!
    pause
    exit /b
)

:: 2. Check Ollama & Models
echo [2/4] Checking Ollama AI System...
where ollama >nul 2>nul
if %errorlevel% neq 0 (
    echo [WARNING] Ollama not found in PATH! 
    echo Please install Ollama from https://ollama.com
    pause
    exit /b
)

echo [DEBUG] Ensuring AI Models are ready...
echo (This may take a moment if it's your first time)
start "Ollama Serve" /min ollama serve
timeout /t 2 >nul
ollama pull llava
ollama pull qwen3:8b

:: 3. Start Backend in a new window
echo [3/4] Starting Backend (Port 8000)...
start "Drone Backend" cmd /k "python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload"

:: 4. Start Frontend in a new window
echo [4/4] Starting Frontend (Port 3000)...
pushd frontend
start "Drone Frontend" cmd /k "npm run dev"
popd

:: 5. Launch Browser
echo.
echo Waiting 5 seconds for servers to initialize...
timeout /t 5 >nul
start http://localhost:3000

echo.
echo ======================================================
echo    ✅ System Started Successfully!
echo    - Dashboard: http://localhost:3000
echo    - AI Models: LLava (Vision) & Qwen (Agent)
echo ======================================================
echo.
echo Keep this window open or press any key to exit launcher...
pause >nul
