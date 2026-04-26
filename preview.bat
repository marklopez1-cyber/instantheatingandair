@echo off
REM preview.bat — Windows double-click preview script.
REM Double-click this file to start a local server and open the browser.

cd /d "%~dp0"

set PORT=8000
set URL=http://localhost:%PORT%

echo.
echo   Preview running at %URL%
echo   Close this window or press Ctrl+C to stop.
echo.

REM Open browser after a brief delay
start "" cmd /c "timeout /t 1 /nobreak > NUL & start %URL%"

REM Try python3 first, then fall back to python
where python3 >nul 2>nul
if %errorlevel%==0 (
  python3 -m http.server %PORT%
) else (
  where python >nul 2>nul
  if %errorlevel%==0 (
    python -m http.server %PORT%
  ) else (
    echo Python is not installed. Install Python 3 from https://www.python.org/downloads/
    pause
  )
)
