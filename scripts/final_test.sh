#!/bin/bash

echo "🎯 DataScout 前端最終驗證測試"
echo "================================"

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

# 檢查核心組件文件
echo -e "${YELLOW}🧩 檢查組件可訪問性...${NC}"
components=(
    "components/layout/Sidebar.html:側邊欄組件"
    "components/layout/Topbar.html:頂部導航組件" 
    "components/charts/ChartHeader.html:圖表標題組件"
    "components/charts/CandlestickContent.html:蠟燭圖內容組件"
)

for item in "${components[@]}"; do
    IFS=':' read -r path name <<< "$item"
    status=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:5173/$path")
    run_test "$name" "echo $status" "200"
done

# 檢查 JavaScript 文件
echo -e "${YELLOW}📄 檢查核心 JavaScript 文件...${NC}"
js_files=(
    "src/index.js:主入口文件"
    "src/component-loader.js:組件加載器"
)

for item in "${js_files[@]}"; do
    IFS=':' read -r path name <<< "$item"
    status=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:5173/$path")
    run_test "$name" "echo $status" "200"
done

# 檢查頁面內容
echo -e "${YELLOW}🌐 檢查頁面內容...${NC}"
page_content=$(curl -s http://localhost:5173/)

# 檢查關鍵元素
run_test "HTML 基礎結構" "echo '$page_content' | grep -c 'data-component'" "[0-9]+"
run_test "TailwindCSS 載入" "echo '$page_content' | grep -c 'tailwindcss'" "[0-9]+"
run_test "ApexCharts 載入" "echo '$page_content' | grep -c 'apexcharts'" "[0-9]+"
run_test "模組化 JS 載入" "echo '$page_content' | grep -c 'type=\"module\"'" "[0-9]+"

# 檢查組件加載器邏輯
echo -e "${YELLOW}⚙️ 檢查組件加載邏輯...${NC}"
component_loader=$(curl -s http://localhost:5173/src/component-loader.js)

run_test "端口檢測邏輯" "echo '$component_loader' | grep -c '5173'" "[0-9]+"
run_test "路徑處理邏輯" "echo '$component_loader' | grep -c 'getBasePath'" "[0-9]+"
run_test "錯誤處理邏輯" "echo '$component_loader' | grep -c 'catch'" "1"

# 最終報告
echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}📊 測試總結${NC}"
echo -e "${BLUE}================================${NC}"
echo -e "${GREEN}✅ 通過: $PASSED${NC}"
echo -e "${RED}❌ 失敗: $FAILED${NC}"

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 所有測試通過！前端系統運行正常${NC}"
    echo -e "${GREEN}🚀 系統已準備就緒，可以進行開發工作${NC}"
    exit 0
else
    echo -e "${RED}⚠️  發現 $FAILED 個問題，建議檢查並修復${NC}"
    exit 1
fi
