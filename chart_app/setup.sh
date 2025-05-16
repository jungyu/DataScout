#!/bin/bash

# 顯示顏色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}DataScout Chart App 安裝腳本${NC}"
echo -e "============================================"

# 檢查 Python 版本
echo -e "${GREEN}檢查 Python 版本...${NC}"
python3 --version
if [ $? -ne 0 ]; then
    echo -e "${RED}錯誤: 找不到 Python3，請確保已安裝 Python 3.8 或更高版本${NC}"
    exit 1
fi

# 創建虛擬環境
echo -e "${GREEN}創建虛擬環境...${NC}"
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo -e "${RED}錯誤: 無法創建虛擬環境，請安裝 venv 模組${NC}"
    exit 1
fi

# 啟動虛擬環境
echo -e "${GREEN}啟動虛擬環境...${NC}"
source venv/bin/activate

# 升級 pip
echo -e "${GREEN}升級 pip...${NC}"
pip install --upgrade pip

# 分步安裝依賴，避免衝突
echo -e "${GREEN}安裝基礎依賴...${NC}"
pip install fastapi uvicorn jinja2 python-multipart

echo -e "${GREEN}安裝數據處理套件...${NC}"
pip install pandas numpy openpyxl xlrd

echo -e "${GREEN}安裝解析與圖形處理套件...${NC}"
pip install "beautifulsoup4>=4.9.3,<4.12.0"
pip install matplotlib pillow

echo -e "${GREEN}安裝其他工具...${NC}"
pip install requests python-dateutil pytz tqdm

# 創建必要的目錄
echo -e "${GREEN}創建必要的目錄...${NC}"
mkdir -p data/csv data/json data/excel
mkdir -p static/uploads/csv static/uploads/json static/uploads/excel

echo -e "${GREEN}安裝完成！${NC}"
echo -e "您現在可以通過以下命令啟動應用程式:"
echo -e "${YELLOW}source venv/bin/activate${NC}"
echo -e "${YELLOW}uvicorn app.main:app --reload --host 0.0.0.0 --port 8000${NC}"
echo -e "然後在瀏覽器中訪問: ${YELLOW}http://localhost:8000${NC}"
