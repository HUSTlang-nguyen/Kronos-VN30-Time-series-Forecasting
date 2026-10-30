@echo off
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0demo\start.ps1" %*
if errorlevel 1 pause
