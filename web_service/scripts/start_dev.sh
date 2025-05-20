#!/bin/bash

# 設置顏色輸出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 顯示標頭
echo -e "${BLUE}=====================================================${NC}"
echo -e "${BLUE}  DataScout Web Service - 啟動開發環境               ${NC}"
echo -e "${BLUE}=====================================================${NC}"

# 檢查工作目錄
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.." || { echo -e "${RED}無法進入專案根目錄${NC}"; exit 1; }

# 檢查虛擬環境
if [ ! -d "venv" ]; then
  echo -e "${YELLOW}正在創建 Python 虛擬環境...${NC}"
  python3 -m venv venv || { echo -e "${RED}創建虛擬環境失敗${NC}"; exit 1; }
fi

# 激活虛擬環境
source venv/bin/activate

# 安裝依賴
echo -e "${YELLOW}正在安裝依賴...${NC}"
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 檢查前端構建
echo -e "${YELLOW}檢查是否需要構建前端資源...${NC}"
if [ -d "../web_frontend" ]; then
  read -p "是否構建前端資源? (y/n): " build_frontend
  if [ "$build_frontend" = "y" ] || [ "$build_frontend" = "Y" ]; then
    echo -e "${YELLOW}正在構建前端資源...${NC}"
    ../web_frontend/scripts/build_frontend.sh --output ./static
  fi
fi

# 創建必要的目錄
mkdir -p static/uploads
mkdir -p static/js/dist
mkdir -p static/css

# 啟動 FastAPI 應用
echo -e "${GREEN}啟動 FastAPI 應用...${NC}"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 停用虛擬環境
deactivate
