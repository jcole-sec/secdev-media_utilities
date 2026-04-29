@echo off
REM MP4 to MP3 Converter
REM Converts all MP4 files to MP3 using ffmpeg

cd /d "%~dp0"

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found. Please install Python 3.7 or later.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if ffmpeg is installed
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo Error: ffmpeg not found. Install with: choco install ffmpeg
    echo Or download from: https://ffmpeg.org/download.html
    pause
    exit /b 1
)

REM Run the converter
echo Converting MP4 files to MP3...
python convert_mp4_to_mp3.py %*

if errorlevel 1 (
    echo.
    echo An error occurred. Check the messages above.
    pause
)
