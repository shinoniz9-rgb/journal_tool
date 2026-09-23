@echo off
chcp 65001 >nul
title Crypto Trading Journal - Web Server
cd /d "%~dp0"
echo ======================================================================
echo   ⚡ CRYPTO TRADING JOURNAL - PHIÊN BẢN WEB CHUYÊN NGHIỆP
echo ======================================================================
echo.
echo [*] Đang khởi động Web App...
echo [*] Mở trình duyệt tại: http://localhost:5000
echo.
timeout /t 2 /nobreak >nul
start "" "http://localhost:5000"
python web_app.py
pause
