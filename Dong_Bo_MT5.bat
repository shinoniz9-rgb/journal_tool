@echo off
chcp 65001 > nul
title Dong Bo Lenh MT5 - Trading Journal
echo ========================================================
echo       DANG KET NOI VA DONG BO LENH TU MT5 VAO NHAT KY
echo ========================================================
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [!] May tinh nay chua cai dat Python hoac chua tick chon 'Add Python to PATH'!
    echo [*] Vui long tai va cai dat Python tai: https://www.python.org/downloads/
    echo.
    pause
    exit /b
)

python  %~dp0dong_bo_mt5.py
echo.
echo ========================================================
echo Bam phim bat ky de dong cua so nay...
pause > nul