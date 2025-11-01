@echo off
chcp 65001 >nul
title Codeforces Analytics - Launcher

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║     🚀 Codeforces Analytics Dashboard Launcher            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM ==================================================================
REM Bước 1: Dọn dẹp processes cũ
REM ==================================================================
echo [1/5] 🧹 Cleaning up old processes...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM node.exe 2>nul
timeout /t 2 /nobreak > nul
echo       ✅ Cleanup completed!
echo.

REM ==================================================================
REM Bước 2: Kiểm tra và tạo virtual environment
REM ==================================================================
echo [2/5] 🐍 Setting up Python environment...
if not exist "venv\" (
    echo       Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo       ❌ Failed to create virtual environment!
        pause
        exit /b 1
    )
    echo       ✅ Virtual environment created!
) else (
    echo       ✅ Virtual environment already exists!
)
echo.

REM ==================================================================
REM Bước 3: Kích hoạt venv và cài đặt Python dependencies
REM ==================================================================
echo [3/5] 📦 Installing Python dependencies...
call venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo       ❌ Failed to install Python dependencies!
    pause
    exit /b 1
)
echo       ✅ Python dependencies installed!
echo.

REM ==================================================================
REM Bước 4: Khởi động Flask API Backend
REM ==================================================================
echo [4/5] 🔌 Starting Flask API Backend...

REM Tạo batch file để chạy Flask với đường dẫn tuyệt đối
set FLASK_SCRIPT=%~dp0start_flask.bat
echo @echo off > "%FLASK_SCRIPT%"
echo title Flask API - Port 5000 >> "%FLASK_SCRIPT%"
echo cd /d "%~dp0" >> "%FLASK_SCRIPT%"
echo call "%~dp0venv\Scripts\activate" >> "%FLASK_SCRIPT%"
echo python "%~dp0api\server.py" >> "%FLASK_SCRIPT%"
echo pause >> "%FLASK_SCRIPT%"

REM Khởi động Flask trong cửa sổ mới (sử dụng START với đường dẫn đầy đủ)
start "Flask API Server" /D "%~dp0" cmd /c "%FLASK_SCRIPT%"

echo       ✅ Flask API starting on http://localhost:5000
echo       Waiting for API to initialize...
timeout /t 5 /nobreak > nul
echo.

REM ==================================================================
REM Bước 5: Khởi động React Dashboard Frontend
REM ==================================================================
echo [5/5] 🌐 Starting React Dashboard...

REM Tạo file .env trong dashboard folder
if not exist "codeforces-dashboard\.env" (
    echo       Creating .env file...
    (
        echo PORT=3001
        echo REACT_APP_API_URL=http://localhost:5000
        echo BROWSER=none
    ) > "codeforces-dashboard\.env"
    echo       ✅ .env file created!
)

REM Check npm packages
if not exist "codeforces-dashboard\node_modules\" (
    echo       Installing npm packages...
    cd codeforces-dashboard
    call npm install
    if errorlevel 1 (
        echo       ❌ Failed to install npm packages!
        cd ..
        pause
        exit /b 1
    )
    cd ..
    echo       ✅ npm packages installed!
)

REM Tạo batch file để chạy React với đường dẫn tuyệt đối
set REACT_SCRIPT=%~dp0start_react.bat
echo @echo off > "%REACT_SCRIPT%"
echo title React Dashboard - Port 3001 >> "%REACT_SCRIPT%"
echo cd /d "%~dp0codeforces-dashboard" >> "%REACT_SCRIPT%"
echo set PORT=3001 >> "%REACT_SCRIPT%"
echo set BROWSER=none >> "%REACT_SCRIPT%"
echo npm start >> "%REACT_SCRIPT%"
echo pause >> "%REACT_SCRIPT%"

REM Khởi động React trong cửa sổ mới
start "React Dashboard" /D "%~dp0codeforces-dashboard" cmd /c "%REACT_SCRIPT%"

echo       ✅ React Dashboard starting on http://localhost:3001
echo.

REM ==================================================================
REM Hoàn thành
REM ==================================================================
timeout /t 3 /nobreak > nul

echo ╔════════════════════════════════════════════════════════════╗
echo ║                  ✅ ALL SERVICES STARTED!                  ║
echo ╠════════════════════════════════════════════════════════════╣
echo ║  📊 Dashboard:  http://localhost:3001                      ║
echo ║  🔌 API:        http://localhost:5000                      ║
echo ║  📖 API Health: http://localhost:5000/api/health           ║
echo ╠════════════════════════════════════════════════════════════╣
echo ║  💡 Two new windows opened:                                ║
echo ║     - Flask API Server (showing logs)                      ║
echo ║     - React Dashboard (showing logs)                       ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Đợi services khởi động
timeout /t 8 /nobreak > nul
