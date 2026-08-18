@echo off
rem ============================================================
rem  AI Work OS - Chat launcher (double-click to run)
rem  Uses the project's virtual environment Python directly,
rem  so it works even when the venv isn't "activated".
rem ============================================================
cd /d "%~dp0"

echo Starting AI Work OS chat...
echo Type "exit" to quit.
echo.
"%~dp0.venv\Scripts\python.exe" main.py --chat

echo.
pause
