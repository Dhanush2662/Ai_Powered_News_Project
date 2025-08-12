@echo off
echo Starting Bias News Checker Project...
echo.

echo Step 1: Installing Python dependencies...
cd backend
pip install -r requirements.txt
cd ..

echo.
echo Step 2: Installing Node.js dependencies...
cd frontend
npm install
cd ..

echo.
echo Step 3: Setting up environment variables...
echo Please make sure to:
echo 1. Copy backend/.env.example to backend/.env
echo 2. Add your API keys to backend/.env
echo 3. Set up PostgreSQL database

echo.
echo Step 4: Starting the backend server...
cd backend
start "Backend Server" python main.py

echo.
echo Step 5: Starting the frontend server...
cd ../frontend
start "Frontend Server" npm start

echo.
echo Project is starting up!
echo Backend will be available at: http://localhost:8000
echo Frontend will be available at: http://localhost:3000
echo.
pause
