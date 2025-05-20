#!/bin/sh

# DataScout FastAPI 服務啟動腳本
# 創建日期: 2025-05-19

# 確保腳本可被執行
if [ ! -x "$0" ]; then
    echo "設置腳本為可執行..."
    chmod +x "$0"
fi

# 檢查虛擬環境
if [ -d "./venv" ]; then
    echo "正在啟用虛擬環境..."
    source ./venv/bin/activate
else
    echo "沒有找到虛擬環境，確保您已安裝所有依賴。"
    echo "可以使用 'python -m pip install -r requirements.txt' 安裝依賴。"
fi

# 檢查依賴是否已安裝
echo "檢查並安裝依賴..."
python -m pip install -r requirements.txt

# 參數處理
HOST="127.0.0.1"
PORT="8000"
DEBUG=""
CONFIG=""

# 解析命令行參數
while [ "$#" -gt 0 ]; do
  case "$1" in
    --host=*)
      HOST="${1#*=}"
      ;;
    --port=*)
      PORT="${1#*=}"
      ;;
    --debug)
      DEBUG="--debug"
      ;;
    --config=*)
      CONFIG="--config ${1#*=}"
      ;;
    *)
      echo "未知選項: $1"
      exit 1
      ;;
  esac
  shift
done

echo "正在啟動 DataScout API 服務..."
echo "訪問地址: http://$HOST:$PORT"
echo "文檔地址: http://$HOST:$PORT/docs"

# 啟動服務
python main.py --host="$HOST" --port="$PORT" $DEBUG $CONFIG
