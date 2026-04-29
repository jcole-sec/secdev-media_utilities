@echo off
REM Duplicate COPY File Remover
REM Removes files with "COPY" in name if they are identical to source files

cd /d "%~dp0"

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found. Please install Python 3.7 or later.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Run the remover
echo Checking for duplicate COPY files...
python remove_duplicate_copies.py

if errorlevel 1 (
    echo.
    echo An error occurred. Check the messages above.
    pause
)
