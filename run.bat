@echo off
echo Starting YouTube Video Downloader...
python youtube_downloader_app.py
if errorlevel 1 (
    echo.
    echo ERROR: Failed to start the application
    echo Make sure you have run install.bat first
    echo.
    pause
)
