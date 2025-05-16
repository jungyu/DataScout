#!/bin/bash

# 顯示顏色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}正在為 DataScout Chart App 建立環境...${NC}"

# 檢查 Python 3 是否安裝
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}未找到 Python 3，請先安裝 Python 3${NC}"
    exit 1
fi

# 檢查虛擬環境目錄
VENV_DIR="venv"
if [ -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}發現既有虛擬環境，正在刪除...${NC}"
    rm -rf "$VENV_DIR"
fi

# 創建新虛擬環境
echo -e "${GREEN}創建新的虛擬環境...${NC}"
python3 -m venv "$VENV_DIR"

# 激活虛擬環境
echo -e "${GREEN}激活虛擬環境...${NC}"
source "$VENV_DIR/bin/activate"

# 安裝依賴前先升級 pip
echo -e "${GREEN}升級 pip...${NC}"
pip install --upgrade pip

# 安裝依賴
echo -e "${GREEN}安裝依賴項...${NC}"
pip install -r requirements.txt

# 檢查安裝結果
if [ $? -eq 0 ]; then
    echo -e "${GREEN}已成功安裝所有依賴！${NC}"
    
    # 建立啟動腳本
    echo "#!/bin/bash" > start.sh
    echo "source $VENV_DIR/bin/activate" >> start.sh
    echo "python -m uvicorn app.main:app --reload --port 8000" >> start.sh
    chmod +x start.sh
    
    echo -e "${GREEN}已建立啟動腳本 start.sh，請執行 ./start.sh 啟動應用${NC}"
else
    echo -e "${RED}安裝過程發生錯誤，請查看上方訊息${NC}"
fi
