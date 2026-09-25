@echo off
chcp 65001 > nul
title Dong Bo MT5 Tu Dong Lien Tuc - Trading Journal
echo ========================================================
echo   CHE DO TU DONG DONG BO MT5 LIEN TUC (LIVE AUTO-SYNC)
echo ========================================================
echo.
echo * Tu dong cap nhat lenh va so du moi 15 giay.
echo * Tu dong nhan dien khi doi tai khoan trong app MT5.
echo.

if exist "%~dp0Dong_Bo_MT5.exe" (
    "%~dp0Dong_Bo_MT5.exe" --auto
) else (
    python "%~dp0dong_bo_mt5.py" --auto
)

echo.
pause
