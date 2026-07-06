@echo off
chcp 65001 >nul
title SJTUClaw Web

cd /d "%~dp0"

if not exist .env (
    echo [!] .env 文件不存在，请先配置：
    echo     1. 复制 .env.example 为 .env
    echo     2. 编辑 .env 填入你的 API Key
    pause
    exit /b 1
)

echo ==============================
echo   SJTUClaw Web Gateway
echo ==============================
echo.
echo 正在启动...
echo 浏览器打开: http://127.0.0.1:5000
echo 按 Ctrl+C 停止
echo.

python -m src.gateway

pause
