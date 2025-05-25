#!/bin/bash
# 前端開發服務啟動腳本

# 設置顏色輸出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 顯示標頭
echo -e "${BLUE}=====================================================${NC}"
echo -e "${BLUE}  DataScout 前端開發環境啟動腳本                     ${NC}"
echo -e "${BLUE}=====================================================${NC}"

# 確保在腳本所在目錄的上一級目錄（web_frontend）執行
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.." || { echo -e "${RED}無法進入前端根目錄${NC}"; exit 1; }

echo -e "${YELLOW}正在啟動 DataScout 前端開發服務...${NC}"

# 檢查是否已安裝 Node.js 和 npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}錯誤: 找不到 npm，請確保 Node.js 已安裝。${NC}"
    exit 1
fi

# 顯示 Node.js 和 npm 版本
echo -e "${YELLOW}Node 版本: $(node -v)${NC}"
echo -e "${YELLOW}npm 版本: $(npm -v)${NC}"

# 安裝依賴（如果 node_modules 不存在或 package.json 更新）
if [ ! -d "node_modules" ] || [ package.json -nt node_modules ]; then
    echo -e "${YELLOW}正在安裝依賴...${NC}"
    npm install
fi

# 確認 vite 已安裝
if ! npm list vite 2>/dev/null | grep -q 'vite'; then
    echo -e "${YELLOW}安裝 vite...${NC}"
    npm install vite
fi

# 啟動開發服務
echo -e "${GREEN}啟動 Vite 開發服務器...${NC}"
echo -e "${GREEN}訪問地址: http://localhost:5173 ${NC}"
echo -e "${BLUE}=====================================================${NC}"

# 直接使用 npx 啟動 vite，確保能找到命令
npx vite
