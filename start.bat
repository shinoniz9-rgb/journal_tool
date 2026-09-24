@echo off
chcp 65001 >nul
title Trading Journal - Web Server
cd /d "%~dp0"
echo ======================================================================
echo   [!] TRADING JOURNAL - PHIEN BAN WEB CHUYEN NGHIEP
echo ======================================================================
echo.
echo [*] Dang khoi dong Web App...
echo [*] Mo trinh duyet tai: http://localhost:5000
echo.
timeout /t 2 /nobreak >nul
start "" "http://localhost:5000"
python web_app.py
pause
