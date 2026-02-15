@echo off
echo ========================================
echo YouTube Video Downloader - Installation
echo ========================================
echo.

echo Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo.
echo Installing required Python packages...
echo This may take a few minutes...
echo.

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ERROR: Failed to install dependencies
    echo Please check your internet connection and try again
    pause
    exit /b 1
)

echo.
echo ========================================
echo Installation completed successfully!
echo ========================================
echo.
echo To run the application, execute:
echo   python youtube_downloader_app.py
echo.
echo Note: Make sure FFmpeg is installed for full functionality
echo Download from: https://ffmpeg.org/download.html
echo.
pause
