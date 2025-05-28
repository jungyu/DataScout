#!/bin/bash

# 修正後端重複路徑腳本
# 將後端 JavaScript 檔案中的 /static/static/assets/examples/ 路徑修正為 /static/assets/examples/

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=====================================================${NC}"
echo -e "${BLUE}  修正後端重複路徑腳本                               ${NC}"
echo -e "${BLUE}=====================================================${NC}"

cd "$(dirname "$0")/.." || exit 1

echo -e "${YELLOW}正在修正後端 JavaScript 檔案中的重複路徑...${NC}"

# 修正後端檔案中的重複路徑（排除備份目錄）
find web_service/static -name "*.js" -type f ! -path "*/backup*" | while read -r file; do
    if grep -q "/static/static/assets/examples/" "$file"; then
        echo -e "${YELLOW}修正: $file${NC}"
        
        # 將重複路徑 /static/static/assets/examples/ 修正為 /static/assets/examples/
        sed -i '' 's|/static/static/assets/examples/|/static/assets/examples/|g' "$file"
    fi
done

echo -e "${GREEN}後端重複路徑修正完成！${NC}"

# 驗證修正結果
echo -e "${BLUE}正在驗證修正結果...${NC}"
echo -e "${YELLOW}檢查是否還有重複路徑：${NC}"
find web_service/static -name "*.js" -type f ! -path "*/backup*" -exec grep -l "/static/static/assets/examples/" {} \; 2>/dev/null | wc -l | xargs echo "剩餘有重複路徑的檔案數量："

if [ $(find web_service/static -name "*.js" -type f ! -path "*/backup*" -exec grep -l "/static/static/assets/examples/" {} \; 2>/dev/null | wc -l) -eq 0 ]; then
    echo -e "${GREEN}所有重複路徑已修正！${NC}"
else
    echo -e "${YELLOW}仍有檔案需要手動檢查${NC}"
fi

echo -e "${BLUE}=====================================================${NC}"
echo -e "${GREEN}後端路徑修正完成！${NC}"
echo -e "${BLUE}=====================================================${NC}"
