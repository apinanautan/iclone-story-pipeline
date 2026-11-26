@echo off
cd /d "%~dp0"
py -3 -B configure.py
if errorlevel 1 exit /b 1
py -3 -B relay.py
