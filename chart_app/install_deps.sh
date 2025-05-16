#!/bin/bash

# 設置顏色輸出
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
NC="\033[0m" # No Color

echo -e "${YELLOW}開始安裝 Chart App 依賴項...${NC}"

# 檢查 pip 是否存在
if ! command -v pip &> /dev/null; then
    echo -e "${RED}找不到 pip。請確保已安裝 Python 及 pip。${NC}"
    exit 1
fi

# 安裝基本依賴
echo -e "${GREEN}安裝基本依賴項...${NC}"
pip install fastapi uvicorn jinja2 python-multipart

# 安裝 werkzeug 專門用於檔案名稱處理
echo -e "${GREEN}安裝 werkzeug 用於檔案安全處理...${NC}"
pip install werkzeug

# 安裝資料處理相關依賴
echo -e "${GREEN}安裝資料處理相關依賴...${NC}"
pip install pandas numpy openpyxl xlrd

# 安裝圖像處理相關依賴
echo -e "${GREEN}安裝圖像處理相關依賴...${NC}"
pip install pillow

# 確認安裝
echo -e "${GREEN}檢查相關模組是否正確安裝...${NC}"
python -c "import fastapi; import uvicorn; import jinja2; import werkzeug; import pandas; print('所有必要模組已成功安裝！')" || echo -e "${RED}有些模組可能未正確安裝，請查看錯誤訊息。${NC}"

echo -e "${GREEN}完成！${NC}"
echo -e "${YELLOW}現在可以執行 'uvicorn app.main:app --reload' 來啟動應用程式。${NC}"

# 更新 requirements.txt
echo -e "${GREEN}更新 requirements.txt...${NC}"
pip freeze > requirements.txt
echo -e "${GREEN}成功更新 requirements.txt${NC}"
