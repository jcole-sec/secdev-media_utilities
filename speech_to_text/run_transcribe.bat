@echo off
REM ElevenLabs Audio Transcription Script Runner
REM Requires Python 3.7+ and dependencies from requirements.txt

cd /d "%~dp0"

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found. Please install Python 3.7 or later.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Run the transcription script
echo Transcribing audio files with ElevenLabs Speech-to-Text API...
python transcribe.py

if errorlevel 1 (
    echo.
    echo An error occurred. Check the messages above.
    pause
)
@echo off
REM Audio Transcription Script Runner
REM Requires Python 3.7+ and dependencies from requirements.txt

cd /d "%~dp0"

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found. Please install Python 3.7 or later.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Run the transcription script
echo Transcribing audio files...
python transcribe.py

if errorlevel 1 (
    echo.
    echo An error occurred. Check the messages above.
    pause
)
