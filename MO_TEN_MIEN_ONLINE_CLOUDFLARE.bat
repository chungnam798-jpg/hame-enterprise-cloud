@echo off
title Cloudflare Free Public HTTPS Domain (Auto-KeepAlive)
chcp 65001 >nul
cd /d "%~dp0"
python auto_tunnel_supervisor.py
pause
