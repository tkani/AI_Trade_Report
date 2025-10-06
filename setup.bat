@echo off
echo ============================================================
echo 🚀 AI Trade Report - Quick Setup (Windows)
echo ============================================================
echo.

echo 📋 Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo    Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)
echo ✅ Python detected

echo.
echo 📦 Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ❌ Failed to create virtual environment
    pause
    exit /b 1
)
echo ✅ Virtual environment created

echo.
echo 📚 Installing dependencies...
call venv\Scripts\activate
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)
echo ✅ Dependencies installed

echo.
echo ⚙️  Setting up configuration...
if not exist .env (
    copy .env_example .env
    echo ✅ .env file created from template
) else (
    echo ⚠️  .env file already exists
)

echo.
echo 📁 Creating directories...
if not exist reports mkdir reports
if not exist static\css mkdir static\css
if not exist static\js mkdir static\js
if not exist static\images mkdir static\images
if not exist templates mkdir templates
echo ✅ Directories created

echo.
echo ============================================================
echo 🎉 Setup Complete!
echo ============================================================
echo.
echo 📋 Next Steps:
echo 1. Edit the .env file with your configuration:
echo    - OpenAI API key
echo    - Email settings (for password recovery)
echo    - Secret key (change the default)
echo.
echo 2. Start the application:
echo    run.bat
echo.
echo 3. Open your browser and go to:
echo    http://127.0.0.1:8000
echo.
echo 📖 For detailed instructions, see INSTALLATION.md
echo.
pause
