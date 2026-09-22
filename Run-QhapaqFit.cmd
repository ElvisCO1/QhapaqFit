@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Run the setup steps in README.md first.
    echo Ejecuta primero los pasos de instalacion de README.md.
    pause
    exit /b 1
)
".venv\Scripts\python.exe" main.py
if errorlevel 1 pause
