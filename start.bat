@echo off
REM Audio Scraping Service - Windows Startup Script
REM This script starts both the client and server concurrently

echo ========================================
echo   Audio Scraping Service Startup
echo ========================================
echo.

REM Get the directory where the script is located
set SCRIPT_DIR=%~dp0
set CLIENT_DIR=%SCRIPT_DIR%client
set SERVER_DIR=%SCRIPT_DIR%server

echo Checking prerequisites...

REM Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Node.js is not installed
    pause
    exit /b 1
)

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python is not installed
    pause
    exit /b 1
)

echo Prerequisites met
echo.

REM Check if client dependencies are installed
if not exist "%CLIENT_DIR%\node_modules" (
    echo Installing client dependencies...
    cd /d "%CLIENT_DIR%"
    call npm install
    echo Client dependencies installed
    echo.
)

REM Check if server virtual environment exists
if not exist "%SERVER_DIR%\.venv" (
    echo Creating Python virtual environment...
    cd /d "%SERVER_DIR%"
    python -m venv .venv
    echo Virtual environment created
    echo.
)

REM Check if server dependencies are installed
if not exist "%SERVER_DIR%\.venv\Lib\site-packages\fastapi" (
    echo Installing server dependencies...
    cd /d "%SERVER_DIR%"
    call .venv\Scripts\activate.bat
    pip install -r requirements.txt
    call deactivate
    echo Server dependencies installed
    echo.
)

REM Create log directory if it doesn't exist
set LOG_DIR=%SCRIPT_DIR%logs
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

echo ========================================
echo   Starting Services
echo ========================================
echo.

REM Start the server in a new window
echo Starting FastAPI server...
start "FastAPI Server" cmd /k "cd /d %SERVER_DIR% && .venv\Scripts\activate.bat && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo Server started at http://localhost:8000
echo.

REM Wait a bit for the server to start
timeout /t 2 /nobreak >nul

REM Start the client in a new window
echo Starting Vite development server...
start "Vite Client" cmd /k "cd /d %CLIENT_DIR% && npm run dev"
echo Client started at http://localhost:5173
echo.

echo ========================================
echo   Both services are now running!
echo ========================================
echo.
echo Server: http://localhost:8000
echo Client: http://localhost:5173
echo.
echo Close the terminal windows to stop the services.
echo.
pause
