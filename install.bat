@echo off
echo ECoG GUI Installation Script
echo ============================

REM Check if Python 3 is installed
python3 --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python 3 is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

echo ✓ Python 3 detected

REM Create virtual environment
echo Creating virtual environment...
python3 -m venv .venv

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Installation completed successfully!
echo.
echo To run the application:
echo 1. Activate the virtual environment: .venv\Scripts\activate.bat
echo 2. Run the GUI: python GUI.py
echo.
echo To analyze MATLAB files:
echo python ANALYZE_MAT.py [filename.mat]
echo.
pause
