@echo off
rem ============================================================
rem  AI Work OS - Full Work OS launcher (double-click to run)
rem  Opens the interactive goal-driven Work OS session.
rem ============================================================
cd /d "%~dp0"

echo Starting AI Work OS (full mode)...
echo Type "exit" to quit.
echo.
"%~dp0.venv\Scripts\python.exe" main.py

echo.
pause
