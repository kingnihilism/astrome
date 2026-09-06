@echo off
cd /d "%~dp0"
py app.py
if errorlevel 1 (
  echo.
  echo Astro Me could not start. Confirm that Python 3 is installed.
  pause
)
