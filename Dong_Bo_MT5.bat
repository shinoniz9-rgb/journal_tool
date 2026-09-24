@echo off
chcp 65001 > nul
title Dong Bo Lenh MT5 - Trading Journal
echo ========================================================
echo       DANG KET NOI VA DONG BO LENH TU MT5 VAO NHAT KY
echo ========================================================
echo.
python  %~dp0dong_bo_mt5.py
echo.
echo ========================================================
echo Bam phim bat ky de dong cua so nay...
pause > nul