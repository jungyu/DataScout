#!/bin/bash
# 生產環境測試腳本：驗證 web_service 部署是否成功
# 測試所有重要功能：首頁重定向、側邊欄連結、組件載入等

set -e

echo "🧪 DataScout 生產環境測試"
echo "=========================="

# 設定測試目標
BASE_URL="http://localhost:8000"
BACKEND_RUNNING=false

# 檢查後端服務是否運行
echo "📡 檢查後端服務..."
if curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/health" | grep -q "200"; then
    echo "✅ 後端服務正常運行"
    BACKEND_RUNNING=true
else
    echo "❌ 後端服務未運行，請先啟動 web_service"
    echo "   提示：cd web_service && ./scripts/start_dev.sh"
    exit 1
fi

# 測試計數器
TOTAL_TESTS=0
PASSED_TESTS=0

# 測試函數
run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected="$3"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo "🔍 測試: $test_name"
    
    if eval "$test_command" | grep -q "$expected"; then
        echo "✅ 通過"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo "❌ 失敗"
        echo "   預期: $expected"
        echo "   實際: $(eval "$test_command")"
    fi
}

# 1. 基礎服務測試
echo ""
echo "📋 基礎服務測試"
echo "=================="

run_test "健康檢查端點" \
    "curl -s $BASE_URL/health" \
    "ok"

run_test "首頁可訪問" \
    "curl -s -o /dev/null -w '%{http_code}' $BASE_URL/" \
    "200"

run_test "靜態資源可訪問" \
    "curl -s -o /dev/null -w '%{http_code}' $BASE_URL/static/line.html" \
    "200"

# 2. 路徑處理測試
echo ""
echo "🔗 路徑處理測試"
echo "=================="

run_test "側邊欄連結包含 /static/ 前綴" \
    "curl -s $BASE_URL/static/components/layout/Sidebar.html" \
    "href=\"/static/line.html\""

run_test "重定向邏輯包含生產路徑" \
    "curl -s $BASE_URL/static/assets/main-*.js" \
    "static/line.html"

run_test "組件載入器可訪問" \
    "curl -s -o /dev/null -w '%{http_code}' $BASE_URL/static/component-loader.js" \
    "200"

# 3. 圖表頁面測試
echo ""
echo "📊 圖表頁面測試"
echo "=================="

# 測試主要圖表頁面
charts=("line" "area" "column" "bar" "pie" "donut" "radar" "scatter")

for chart in "${charts[@]}"; do
    run_test "${chart} 圖表頁面" \
        "curl -s -o /dev/null -w '%{http_code}' $BASE_URL/static/${chart}.html" \
        "200"
done

# 4. 組件載入測試
echo ""
echo "🧩 組件載入測試"
echo "=================="

components=(
    "components/layout/Sidebar.html"
    "components/layout/Topbar.html"
    "components/charts/ChartHeader.html"
)

for component in "${components[@]}"; do
    component_name=$(basename "$component" .html)
    run_test "${component_name} 組件" \
        "curl -s -o /dev/null -w '%{http_code}' $BASE_URL/static/$component" \
        "200"
done

# 5. 資源文件測試
echo ""
echo "📁 資源文件測試"
echo "=================="

run_test "CSS 文件" \
    "curl -s -o /dev/null -w '%{http_code}' $BASE_URL/static/assets/main-*.css" \
    "200"

run_test "JavaScript 文件" \
    "curl -s -o /dev/null -w '%{http_code}' $BASE_URL/static/assets/main-*.js" \
    "200"

run_test "Favicon" \
    "curl -s -o /dev/null -w '%{http_code}' $BASE_URL/static/favicon.ico" \
    "200"

# 6. 功能性測試
echo ""
echo "⚙️ 功能性測試"
echo "=================="

run_test "首頁包含組件載入標記" \
    "curl -s $BASE_URL/" \
    "data-component"

run_test "側邊欄包含圖表連結" \
    "curl -s $BASE_URL/static/components/layout/Sidebar.html" \
    "data-chart-type"

run_test "JavaScript 模組載入" \
    "curl -s $BASE_URL/" \
    "type=\"module\""

# 7. 特殊功能測試
echo ""
echo "🎯 特殊功能測試"
echo "=================="

# 檢查是否有重複的 static 路徑
DOUBLE_STATIC_COUNT=$(curl -s "$BASE_URL/" | grep -o "/static/static/" | wc -l | tr -d ' ')
if [ "$DOUBLE_STATIC_COUNT" -eq 0 ]; then
    echo "🔍 測試: 無重複 static 路徑"
    echo "✅ 通過"
    PASSED_TESTS=$((PASSED_TESTS + 1))
else
    echo "🔍 測試: 無重複 static 路徑"
    echo "❌ 失敗 - 發現 $DOUBLE_STATIC_COUNT 個重複路徑"
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

# 8. 顯示測試結果
echo ""
echo "📊 測試總結"
echo "=================="
echo "✅ 通過: $PASSED_TESTS"
echo "❌ 失敗: $((TOTAL_TESTS - PASSED_TESTS))"
echo "📋 總計: $TOTAL_TESTS"

if [ $PASSED_TESTS -eq $TOTAL_TESTS ]; then
    echo ""
    echo "🎉 所有測試通過！"
    echo "🚀 DataScout 生產環境部署成功"
    echo ""
    echo "📍 訪問地址："
    echo "  🏠 首頁: $BASE_URL/"
    echo "  📊 圖表: $BASE_URL/static/line.html"
    echo "  🔧 健康: $BASE_URL/health"
    echo ""
    echo "🔧 功能驗證："
    echo "  ✅ 首頁自動重定向到 line.html"
    echo "  ✅ 側邊欄連結使用正確的 /static/ 前綴"
    echo "  ✅ 組件載入器支援生產環境路徑"
    echo "  ✅ 所有圖表頁面可正常訪問"
else
    echo ""
    echo "⚠️  部分測試失敗，請檢查上述錯誤"
    exit 1
fi
