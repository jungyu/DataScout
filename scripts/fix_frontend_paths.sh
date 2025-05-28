#!/bin/bash

# 修正前端路徑腳本
# 將前端 JavaScript 檔案中的 /static/assets/examples/ 路徑改為 static/assets/examples/

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=====================================================${NC}"
echo -e "${BLUE}  修正前端靜態資源路徑腳本                           ${NC}"
echo -e "${BLUE}=====================================================${NC}"

cd "$(dirname "$0")/.." || exit 1

echo -e "${YELLOW}正在修正前端 JavaScript 檔案中的路徑...${NC}"

# 修正前端檔案中的路徑
find web_frontend/public -name "*.js" -type f | while read -r file; do
    if grep -q "/static/assets/examples/" "$file"; then
        echo -e "${YELLOW}修正: $file${NC}"
        
        # 將絕對路徑 /static/assets/examples/ 改為相對路徑 static/assets/examples/
        sed -i '' 's|/static/assets/examples/|static/assets/examples/|g' "$file"
    fi
done

echo -e "${GREEN}前端路徑修正完成！${NC}"

# 驗證修正結果
echo -e "${BLUE}正在驗證修正結果...${NC}"
echo -e "${YELLOW}檢查是否還有絕對路徑：${NC}"
grep -r "/static/assets/examples/" web_frontend/public/*.js 2>/dev/null || echo -e "${GREEN}所有前端路徑已正確修正為相對路徑！${NC}"

echo -e "${BLUE}=====================================================${NC}"
echo -e "${GREEN}前端路徑修正完成！${NC}"
echo -e "${BLUE}=====================================================${NC}"
