#!/bin/bash
# DataScout 前端穩定性測試腳本

echo "🧪 開始 DataScout 前端穩定性測試..."

# 設置顏色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 檢查開發服務器狀態
echo -e "${BLUE}📡 檢查開發服務器狀態...${NC}"
SERVER_PORTS=("5173" "5174" "5175" "5176" "5177")
ACTIVE_PORT=""

for port in "${SERVER_PORTS[@]}"; do
    if curl -s http://localhost:$port/ > /dev/null 2>&1; then
        ACTIVE_PORT=$port
        echo -e "${GREEN}✅ 開發服務器運行在端口 $port${NC}"
        break
    fi
done

if [ -z "$ACTIVE_PORT" ]; then
    echo -e "${RED}❌ 未找到運行中的開發服務器${NC}"
    exit 1
fi

BASE_URL="http://localhost:$ACTIVE_PORT"

# 測試主頁載入
echo -e "${BLUE}🏠 測試主頁載入...${NC}"
if curl -s "$BASE_URL/" > /tmp/homepage_test.html; then
    PAGE_SIZE=$(wc -c < /tmp/homepage_test.html)
    echo -e "${GREEN}✅ 主頁載入成功 (${PAGE_SIZE} bytes)${NC}"
else
    echo -e "${RED}❌ 主頁載入失敗${NC}"
    exit 1
fi

# 檢查組件標記
echo -e "${BLUE}🧩 檢查組件標記...${NC}"
COMPONENT_COUNT=$(grep -c "data-component" /tmp/homepage_test.html)
if [ "$COMPONENT_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✅ 找到 $COMPONENT_COUNT 個組件標記${NC}"
    grep "data-component" /tmp/homepage_test.html | sed 's/^/    /'
else
    echo -e "${RED}❌ 未找到組件標記${NC}"
fi

# 測試各個組件載入
echo -e "${BLUE}📦 測試組件文件載入...${NC}"
COMPONENTS=(
    "components/layout/Sidebar.html"
    "components/layout/Topbar.html"
    "components/charts/ChartHeader.html"
    "components/charts/CandlestickContent.html"
)

FAILED_COMPONENTS=0
for component in "${COMPONENTS[@]}"; do
    echo -n "  測試 $component... "
    if curl -s "$BASE_URL/$component" > /tmp/component_test.html 2>/dev/null; then
        COMP_SIZE=$(wc -c < /tmp/component_test.html)
        if [ "$COMP_SIZE" -gt 50 ]; then
            echo -e "${GREEN}✅ ($COMP_SIZE bytes)${NC}"
        else
            echo -e "${YELLOW}⚠️ 文件過小 ($COMP_SIZE bytes)${NC}"
        fi
    else
        echo -e "${RED}❌ 載入失敗${NC}"
        ((FAILED_COMPONENTS++))
    fi
done

# 測試 JavaScript 文件載入
echo -e "${BLUE}📜 測試 JavaScript 文件載入...${NC}"
JS_FILES=(
    "src/index.js"
    "src/component-loader.js"
    "static/debug-tool.js"
)

for js_file in "${JS_FILES[@]}"; do
    echo -n "  測試 $js_file... "
    if curl -s "$BASE_URL/$js_file" > /dev/null 2>&1; then
        echo -e "${GREEN}✅${NC}"
    else
        echo -e "${RED}❌${NC}"
    fi
done

# 檢查網路請求穩定性
echo -e "${BLUE}🔄 測試載入穩定性...${NC}"
echo "連續請求主頁 5 次："
for i in {1..5}; do
    echo -n "  請求 $i... "
    START_TIME=$(date +%s%N)
    if curl -s "$BASE_URL/" > /dev/null; then
        END_TIME=$(date +%s%N)
        DURATION=$(( (END_TIME - START_TIME) / 1000000 ))
        echo -e "${GREEN}✅ (${DURATION}ms)${NC}"
    else
        echo -e "${RED}❌${NC}"
    fi
done

# 檢查組件載入穩定性
echo -e "${BLUE}⚡ 測試組件載入穩定性...${NC}"
echo "連續請求側邊欄組件 3 次："
for i in {1..3}; do
    echo -n "  組件請求 $i... "
    if curl -s "$BASE_URL/components/layout/Sidebar.html" > /tmp/sidebar_test_$i.html; then
        SIZE=$(wc -c < /tmp/sidebar_test_$i.html)
        echo -e "${GREEN}✅ (${SIZE} bytes)${NC}"
    else
        echo -e "${RED}❌${NC}"
    fi
done

# 生成測試報告
echo -e "${BLUE}📊 測試總結...${NC}"
echo "----------------------------------------"
echo "開發服務器端口: $ACTIVE_PORT"
echo "主頁大小: $(wc -c < /tmp/homepage_test.html) bytes"
echo "組件標記數量: $COMPONENT_COUNT"
echo "失敗的組件: $FAILED_COMPONENTS"

if [ "$FAILED_COMPONENTS" -eq 0 ]; then
    echo -e "${GREEN}🎉 所有測試通過！前端系統穩定運行。${NC}"
    echo ""
    echo -e "${BLUE}💡 建議開啟以下 URL 進行手動測試：${NC}"
    echo "   $BASE_URL/?debug=true"
    echo ""
    echo -e "${YELLOW}📝 如果仍有不穩定問題，請檢查瀏覽器控制台輸出。${NC}"
else
    echo -e "${YELLOW}⚠️ 發現 $FAILED_COMPONENTS 個組件載入問題，需要進一步檢查。${NC}"
fi

echo "----------------------------------------"
echo -e "${BLUE}測試完成！${NC}"
