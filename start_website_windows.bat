@echo off
echo 🎉 Starting Bias News Checker Website...
echo ================================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python first.
    pause
    exit /b 1
)

REM Check if Node.js is available
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js not found. Please install Node.js first.
    pause
    exit /b 1
)

REM Check if npm is available
npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ npm not found. Please install Node.js first.
    pause
    exit /b 1
)

echo ✅ Dependencies check passed!

REM Install Python dependencies
echo 📦 Installing Python dependencies...
python -m pip install uvicorn fastapi httpx feedparser python-dateutil

REM Install frontend dependencies
echo 📦 Installing frontend dependencies...
cd frontend
if not exist node_modules (
    npm install
) else (
    echo ✅ Frontend dependencies already installed
)
cd ..

echo.
echo ✅ All dependencies ready!
echo.
echo 🚀 Starting servers...
echo 📝 Backend: http://localhost:8000
echo 📝 Frontend: http://localhost:3000
echo 🛑 Press Ctrl+C to stop all servers
echo ================================================

REM Start backend in background
start "Backend Server" cmd /k "cd backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend
cd frontend
npm start

pause
