#!/bin/bash
set -e

# 啟動 Xvfb
Xvfb :99 -screen 0 1920x1080x24 > /dev/null 2>&1 &

# 等待 Xvfb 啟動
sleep 2

# 檢查必要的目錄是否存在
for dir in /app/data /app/logs /app/backups; do
    if [ ! -d "$dir" ]; then
        echo "創建目錄: $dir"
        mkdir -p "$dir"
    fi
done

# 檢查配置文件
if [ ! -f "/app/config/storage.json" ]; then
    echo "錯誤: 找不到配置文件 /app/config/storage.json"
    exit 1
fi

# 設置 Python 路徑
export PYTHONPATH=/app

# 啟動爬蟲服務
echo "啟動爬蟲服務..."
if [ "$1" = "crawler" ]; then
    # 運行爬蟲主程序
    python src/main.py
elif [ "$1" = "test" ]; then
    # 運行測試
    pytest tests/
elif [ "$1" = "setup" ]; then
    # 運行安裝腳本
    python scripts/setup.py
else
    # 默認運行爬蟲主程序
    python src/main.py
fi 