#!/bin/bash

# 修正靜態資源路徑腳本
# 將所有前端和後端 JavaScript 檔案中的 assets/examples/ 路徑統一為 /static/assets/examples/

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=====================================================${NC}"
echo -e "${BLUE}  DataScout 靜態資源路徑統一修正腳本                   ${NC}"
echo -e "${BLUE}=====================================================${NC}"

# 切換到專案根目錄
cd "$(dirname "$0")/.." || exit 1

echo -e "${YELLOW}正在修正後端 JavaScript 檔案中的路徑...${NC}"

# 修正後端檔案中的路徑
find web_service/static -name "*.js" -type f | while read -r file; do
    if grep -q "assets/examples/" "$file"; then
        echo -e "${YELLOW}修正: $file${NC}"
        
        # 替換各種形式的 assets/examples/ 路徑
        sed -i '' 's|fetch(`assets/examples/|fetch(`/static/assets/examples/|g' "$file"
        sed -i '' 's|fetch('\''assets/examples/|fetch('\''/static/assets/examples/|g' "$file"
        sed -i '' 's|fetch("assets/examples/|fetch("/static/assets/examples/|g' "$file"
        sed -i '' 's|`assets/examples/|`/static/assets/examples/|g' "$file"
        sed -i '' 's|'\''assets/examples/|'\''/static/assets/examples/|g' "$file"
        sed -i '' 's|"assets/examples/|"/static/assets/examples/|g' "$file"
        sed -i '' 's|'\''\.\/assets/examples/|'\''/static/assets/examples/|g' "$file"
        sed -i '' 's|"\.\/assets/examples/|"/static/assets/examples/|g' "$file"
        sed -i '' 's|`\.\/assets/examples/|`/static/assets/examples/|g' "$file"
        sed -i '' 's|fetch(`\.\/assets/examples/|fetch(`/static/assets/examples/|g' "$file"
        sed -i '' 's|fetch('\''\.\/assets/examples/|fetch('\''/static/assets/examples/|g' "$file"
        sed -i '' 's|fetch("\.\/assets/examples/|fetch("/static/assets/examples/|g' "$file"
        
        # 處理已經有 /assets/examples/ 的情況
        sed -i '' 's|/assets/examples/|/static/assets/examples/|g' "$file"
    fi
done

echo -e "${YELLOW}正在修正前端 JavaScript 檔案中的路徑...${NC}"

# 修正前端檔案中的路徑
find web_frontend/public -name "*.js" -type f | while read -r file; do
    if grep -q "assets/examples/" "$file"; then
        echo -e "${YELLOW}修正: $file${NC}"
        
        # 替換各種形式的 assets/examples/ 路徑
        sed -i '' 's|fetch(`assets/examples/|fetch(`/static/assets/examples/|g' "$file"
        sed -i '' 's|fetch('\''assets/examples/|fetch('\''/static/assets/examples/|g' "$file"
        sed -i '' 's|fetch("assets/examples/|fetch("/static/assets/examples/|g' "$file"
        sed -i '' 's|`assets/examples/|`/static/assets/examples/|g' "$file"
        sed -i '' 's|'\''assets/examples/|'\''/static/assets/examples/|g' "$file"
        sed -i '' 's|"assets/examples/|"/static/assets/examples/|g' "$file"
        sed -i '' 's|'\''\.\/assets/examples/|'\''/static/assets/examples/|g' "$file"
        sed -i '' 's|"\.\/assets/examples/|"/static/assets/examples/|g' "$file"
        sed -i '' 's|`\.\/assets/examples/|`/static/assets/examples/|g' "$file"
        sed -i '' 's|fetch(`\.\/assets/examples/|fetch(`/static/assets/examples/|g' "$file"
        sed -i '' 's|fetch('\''\.\/assets/examples/|fetch('\''/static/assets/examples/|g' "$file"
        sed -i '' 's|fetch("\.\/assets/examples/|fetch("/static/assets/examples/|g' "$file"
        
        # 處理已經有 /assets/examples/ 的情況（但不是 /static/assets/examples/）
        sed -i '' 's|fetch("/assets/examples/|fetch("/static/assets/examples/|g' "$file"
        sed -i '' 's|fetch('\''\/assets/examples/|fetch('\''/static/assets/examples/|g' "$file"
        sed -i '' 's|fetch(`\/assets/examples/|fetch(`/static/assets/examples/|g' "$file"
    fi
done

echo -e "${GREEN}路徑修正完成！${NC}"

# 顯示修正結果
echo -e "${BLUE}正在驗證修正結果...${NC}"
echo -e "${YELLOW}剩餘需要手動檢查的檔案（如果有）：${NC}"
grep -r "assets/examples/" web_service/static/*.js web_frontend/public/*.js 2>/dev/null | grep -v "/static/assets/examples/" || echo -e "${GREEN}所有路徑已正確修正！${NC}"

echo -e "${BLUE}=====================================================${NC}"
echo -e "${GREEN}路徑統一修正完成！${NC}"
echo -e "${BLUE}=====================================================${NC}"
