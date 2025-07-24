@echo off
echo Setting up Voice Assistant WebSocket Project...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo Python found. Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Setup complete! 
echo.
echo To start the server:
echo 1. Run: venv\Scripts\activate.bat
echo 2. Run: python main.py
echo 3. Open: http://localhost:8000
echo.
echo Don't forget to add your OpenAI API key to the .env file!
echo.
pause
