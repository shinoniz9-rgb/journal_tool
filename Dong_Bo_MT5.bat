@echo off
chcp 65001 > nul
title Đồng Bộ Lệnh MT5 - Trading Journal
echo ========================================================
echo       ĐANG KẾT NỐI VÀ ĐỒNG BỘ LỆNH TỪ MT5 VÀO NHẬT KÝ
echo ========================================================
echo.
python "%~dp0dong_bo_mt5.py"
echo.
echo ========================================================
echo Bấm phím bất kỳ để đóng cửa sổ này...
pause > nul
