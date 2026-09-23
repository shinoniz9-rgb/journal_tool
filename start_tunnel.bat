@echo off
chcp 65001 >nul
title Crypto Trading Journal - Remote Mobile Access (Tunnel)
cd /d "%~dp0"
python run_tunnel.py
pause
