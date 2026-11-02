@echo off
cd /d "%~dp0"
py -3 build_narok_hospital.py
if errorlevel 1 (
  echo.
  echo Build failed. Check that Python 3.10 or newer is installed.
  pause
  exit /b 1
)
echo.
echo Your Packet Tracer project is ready in this folder.
pause
