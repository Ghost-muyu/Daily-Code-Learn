#!/bin/bash
set -e

cd "$(dirname "$0")"

if [ ! -f .env ]; then
    echo "[!] .env 文件不存在，请先配置："
    echo "    1. cp .env.example .env"
    echo "    2. 编辑 .env 填入你的 API Key"
    exit 1
fi

echo "=============================="
echo "  SJTUClaw CLI"
echo "=============================="
echo ""
echo "输入 /exit 退出"
echo ""

python -m src.main
