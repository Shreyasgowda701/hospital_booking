@echo off
echo 🏥 Hospital Management System - Setup Script
echo ============================================

REM Check Python version
echo 📋 Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)
echo ✅ Python found

REM Install dependencies
echo 📦 Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)
echo ✅ Dependencies installed successfully

REM Run migrations
echo 🗃️ Setting up database...
python manage.py migrate
if %errorlevel% neq 0 (
    echo ❌ Database setup failed
    pause
    exit /b 1
)
echo ✅ Database setup complete

echo.
echo 🎉 Setup Complete!
echo.
echo 🚀 To start the server, run:
echo    python manage.py runserver
echo.
echo 🌐 Then open your browser to:
echo    http://127.0.0.1:8000
echo.
echo 👥 Default login credentials:
echo    Admin:   shreyasadmin / admin@123
echo    Doctor:  shreyasdoctor / admin@123
echo    Patient: shreyaspatient / admin@123
echo.
echo 📚 Check README.md for detailed instructions
pause
