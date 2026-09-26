@echo off
set "ROOT=%~dp0"

echo ========================================
echo     VideoForensic AI - Startup
echo ========================================

if not exist "%ROOT%backend\venv\Scripts\python.exe" (
  echo [1/3] Creating Python virtual environment...
  py -m venv "%ROOT%backend\venv"
  if errorlevel 1 (
    echo Failed to create virtual environment.
    pause
    exit /b 1
  )
)

echo [2/3] Installing/checking backend dependencies...
call "%ROOT%backend\venv\Scripts\python.exe" -m pip install -r "%ROOT%backend\requirements.txt"
if errorlevel 1 (
  echo Backend dependency installation failed.
  pause
  exit /b 1
)

echo [3/3] Starting backend and frontend in separate windows...
start "VideoForensic AI - Backend" cmd /k "cd /d "%ROOT%backend" && call venv\Scripts\activate.bat && python app.py"
start "VideoForensic AI - Frontend" cmd /k "cd /d "%ROOT%frontend" && npm install && npm run dev"

timeout /t 3 /nobreak >nul
echo.
echo Open http://localhost:5173 after Vite starts.
echo Backend: http://localhost:5000
pause
