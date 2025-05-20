#!/bin/bash

# 設置顏色輸出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 顯示標頭
echo -e "${BLUE}=====================================================${NC}"
echo -e "${BLUE}  DataScout Web Frontend - 啟動開發環境              ${NC}"
echo -e "${BLUE}=====================================================${NC}"

# 檢查工作目錄
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.." || { echo -e "${RED}無法進入專案根目錄${NC}"; exit 1; }

# 檢查 Node.js 依賴
if [ ! -d "node_modules" ]; then
  echo -e "${YELLOW}正在安裝 Node.js 依賴...${NC}"
  npm install || { echo -e "${RED}安裝依賴失敗${NC}"; exit 1; }
else
  echo -e "${GREEN}Node.js 依賴已存在${NC}"
fi

# 並行執行 Webpack 和 Tailwind CSS 開發模式
echo -e "${YELLOW}啟動前端開發環境...${NC}"
echo -e "${BLUE}同時運行: ${NC}"
echo -e "${GREEN}1. Webpack 監視模式 (JS 資源)${NC}"
echo -e "${GREEN}2. Tailwind CSS 監視模式 (CSS 資源)${NC}"

# 檢查 concurrently 是否安裝
if ! npm list -g concurrently >/dev/null 2>&1; then
  echo -e "${YELLOW}正在全局安裝 concurrently...${NC}"
  npm install -g concurrently || { echo -e "${RED}安裝 concurrently 失敗${NC}"; exit 1; }
fi

# 啟動開發環境
echo -e "${GREEN}啟動並行任務...${NC}"
npm run start

echo -e "${BLUE}=====================================================${NC}"
echo -e "${GREEN}前端開發伺服器已啟動${NC}"
echo -e "${BLUE}=====================================================${NC}"
echo -e ""
echo -e "您也可以單獨運行以下命令:"
echo -e "${YELLOW}npm run build:css${NC} - 只監視 CSS 變更"
echo -e "${YELLOW}npm run dev${NC} - 只監視 JS 變更"
echo -e ""
