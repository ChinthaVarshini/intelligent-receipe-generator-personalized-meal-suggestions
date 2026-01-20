@echo off
echo ============================================
echo   Intelligent Recipe Generator - Launcher
echo ============================================
echo.
echo Starting the backend server...
echo The application will be available at: http://localhost:8000
echo.
echo Press Ctrl+C to stop the server.
echo ============================================
echo.

cd "%~dp0backend\app"
python main.py

pause
