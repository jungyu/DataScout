#!/bin/bash

# 設置顏色輸出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 顯示標頭
echo -e "${BLUE}=====================================================${NC}"
echo -e "${BLUE}  DataScout Chart App - 前端構建腳本                 ${NC}"
echo -e "${BLUE}=====================================================${NC}"

# 檢查工作目錄
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.." || { echo -e "${RED}無法進入專案根目錄${NC}"; exit 1; }

# 處理命令行參數
OUTPUT_DIR=""
while [[ $# -gt 0 ]]; do
  case $1 in
    --output)
      OUTPUT_DIR="$2"
      shift 2
      ;;
    *)
      echo -e "${RED}未知參數: $1${NC}"
      exit 1
      ;;
  esac
done

# 配置變數
FRONTEND_DIR="."  # 因為已經在 web_frontend 目錄下運行
STATIC_DIR=${OUTPUT_DIR:-"../web_service/static"}
JS_DIST_DIR="$STATIC_DIR/js/dist"
CSS_DIST_DIR="$STATIC_DIR/css"

# 顯示輸出目錄
echo -e "${BLUE}構建輸出目錄: ${STATIC_DIR}${NC}"

echo -e "${YELLOW}Step 1: 檢查依賴${NC}"
# 安裝 Node.js 依賴
cd "$FRONTEND_DIR" || { echo -e "${RED}無法進入前端目錄${NC}"; exit 1; }
if [ ! -d "node_modules" ]; then
  echo -e "${YELLOW}正在安裝前端依賴...${NC}"
  npm install || { echo -e "${RED}npm install 失敗${NC}"; exit 1; }
else
  echo -e "${GREEN}前端依賴已存在${NC}"
fi

echo -e "${YELLOW}Step 2: 構建 JavaScript${NC}"
# 清理目標目錄
mkdir -p "$JS_DIST_DIR"

# 構建 JavaScript
echo -e "${YELLOW}正在構建 JavaScript...${NC}"
npm run build || { echo -e "${RED}JavaScript 構建失敗${NC}"; exit 1; }
echo -e "${GREEN}JavaScript 構建完成${NC}"

echo -e "${YELLOW}Step 3: 構建 CSS${NC}"
# 建立 CSS 目標目錄
mkdir -p "$CSS_DIST_DIR"

# 構建 CSS
echo -e "${YELLOW}正在構建 CSS...${NC}"
npm run build:css:prod || { echo -e "${RED}CSS 構建失敗${NC}"; exit 1; }
echo -e "${GREEN}CSS 構建完成${NC}"

echo -e "${YELLOW}Step 4: 複製資源檔案${NC}"
# 確保目標目錄存在
mkdir -p "$STATIC_DIR/js/dist"
mkdir -p "$STATIC_DIR/css"

# 複製構建的檔案
echo -e "${GREEN}構建完成${NC}"

cd .. || { echo -e "${RED}無法返回專案根目錄${NC}"; exit 1; }

echo -e "${BLUE}=====================================================${NC}"
echo -e "${GREEN}前端資源構建完成！${NC}"
echo -e "${BLUE}=====================================================${NC}"
echo -e ""
echo -e "您現在可以啟動 FastAPI 應用："
echo -e "${YELLOW}cd ../web_service && ./scripts/start_dev.sh${NC}"
echo -e ""
