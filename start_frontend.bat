@echo off
echo Starting Frontend Server (React)...
echo.

cd backend\frontend
echo Running: npm start
npm start

echo.
echo If you see this message, the frontend server stopped.
echo Press any key to exit...
pause > nul
