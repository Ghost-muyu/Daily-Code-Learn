@echo off
chcp 65001 >nul
title SJTUClaw CLI

cd /d "%~dp0"

if not exist .env (
    echo [!] .env 文件不存在，请先配置：
    echo     1. 复制 .env.example 为 .env
    echo     2. 编辑 .env 填入你的 API Key
    pause
    exit /b 1
)

echo ==============================
echo   SJTUClaw CLI
echo ==============================
echo.
echo 输入 /exit 退出，输入 /help 查看命令
echo.

python -m src.main

pause
