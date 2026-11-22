@echo off
rem Ai-iclone: run with no arguments for the manual + status + next command (for AI and people).
rem   Ai-iclone.cmd window   opens the Ai-iclone window (the user's view of the same state)
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
if /i "%~1"=="window" ( start "" pyw -3 "%~dp0scripts\progress_app.py" & exit /b 0 )
py -3 "%~dp0scripts\ai_iclone.py" %*
