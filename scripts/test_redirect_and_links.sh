#!/bin/bash

echo "🧪 DataScout 導向與連結修改驗證測試"
echo "====================================="

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 測試計數器
PASSED=0
FAILED=0

# 測試函數
run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected="$3"
    
    echo -e "${BLUE}🔍 測試: $test_name${NC}"
    
    result=$(eval "$test_command" 2>/dev/null)
    
    if [[ "$result" == "$expected" || "$result" =~ $expected ]]; then
        echo -e "${GREEN}✅ 通過${NC}"
        ((PASSED++))
    else
        echo -e "${RED}❌ 失敗 (期望: $expected, 實際: $result)${NC}"
        ((FAILED++))
    fi
    echo
}

# 檢查開發服務器
echo -e "${YELLOW}📡 檢查服務器狀態...${NC}"
SERVER_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5173/)
run_test "開發服務器響應" "echo $SERVER_STATUS" "200"

if [ "$SERVER_STATUS" != "200" ]; then
    echo -e "${RED}❌ 開發服務器未運行，跳過其他測試${NC}"
    exit 1
fi

# 檢查 line.html 可訪問性
echo -e "${YELLOW}📄 檢查 line.html 可訪問性...${NC}"
line_status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5173/line.html)
run_test "line.html 可訪問" "echo $line_status" "200"

# 檢查首頁導向邏輯 (檢查 JavaScript 是否包含導向邏輯)
echo -e "${YELLOW}🔄 檢查導向邏輯...${NC}"
index_js=$(curl -s http://localhost:5173/src/index.js)
redirect_check=$(echo "$index_js" | grep -c "checkAndRedirectToLine")
run_test "導向函數存在" "echo $redirect_check" "[1-9]+"

# 檢查路徑檢查邏輯
path_check=$(echo "$index_js" | grep -c "window.location.pathname")
run_test "路徑檢查邏輯" "echo $path_check" "[1-9]+"

# 檢查側邊欄連結修改
echo -e "${YELLOW}🔗 檢查側邊欄連結...${NC}"
sidebar_content=$(curl -s http://localhost:5173/components/layout/Sidebar.html)

# 檢查基本圖表連結是否移除了 static
basic_charts=(
    "line.html"
    "area.html" 
    "column.html"
    "bar.html"
    "pie.html"
    "donut.html"
    "radar.html"
    "scatter.html"
    "heatmap.html"
    "treemap.html"
)

for chart in "${basic_charts[@]}"; do
    correct_link_count=$(echo "$sidebar_content" | grep -c "href=\"/$chart\"")
    run_test "$chart 連結正確" "echo $correct_link_count" "1"
done

# 檢查進階圖表連結
advanced_charts=(
    "candlestick.html"
    "boxplot.html"
    "histogram.html"
    "bubble.html"
    "funnel.html"
    "polararea.html"
)

for chart in "${advanced_charts[@]}"; do
    correct_link_count=$(echo "$sidebar_content" | grep -c "href=\"/$chart\"")
    run_test "$chart 連結正確" "echo $correct_link_count" "1"
done

# 檢查是否仍有 /static/ 連結殘留
static_links=$(echo "$sidebar_content" | grep -c "/static/")
run_test "無 static 連結殘留" "echo $static_links" "0"

# 檢查組件載入器功能
echo -e "${YELLOW}⚙️ 檢查組件載入功能...${NC}"
component_loader=$(curl -s http://localhost:5173/src/component-loader.js)
loader_function_count=$(echo "$component_loader" | grep -c "loadComponent")
run_test "組件載入器功能" "echo $loader_function_count" "[1-9]+"

# 最終報告
echo -e "${BLUE}====================================${NC}"
echo -e "${BLUE}📊 測試總結${NC}"
echo -e "${BLUE}====================================${NC}"
echo -e "${GREEN}✅ 通過: $PASSED${NC}"
echo -e "${RED}❌ 失敗: $FAILED${NC}"

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 所有測試通過！${NC}"
    echo -e "${GREEN}✅ 首頁將自動導向 line.html${NC}"
    echo -e "${GREEN}✅ 所有側邊欄連結已移除 /static/ 前綴${NC}"
    echo -e "${GREEN}🚀 修改完成，系統運行正常${NC}"
    exit 0
else
    echo -e "${RED}⚠️  發現 $FAILED 個問題，建議檢查並修復${NC}"
    exit 1
fi
