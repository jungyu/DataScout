#!/bin/bash

echo "🧪 快速前端功能測試"
echo "====================="

# 檢查開發服務器
echo "📡 檢查開發服務器..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:5173/ | grep -q "200"; then
    echo "✅ 開發服務器正常運行"
else
    echo "❌ 開發服務器無法訪問"
    exit 1
fi

# 檢查核心組件
echo "🧩 檢查組件文件..."
components=(
    "components/layout/Sidebar.html"
    "components/layout/Topbar.html" 
    "components/charts/ChartHeader.html"
    "components/charts/CandlestickContent.html"
)

for component in "${components[@]}"; do
    status=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:5173/$component")
    if [ "$status" = "200" ]; then
        echo "✅ $component 可訪問"
    else
        echo "❌ $component 無法訪問 (狀態碼: $status)"
    fi
done

# 檢查主要 JS 文件
echo "📄 檢查 JavaScript 文件..."
js_files=(
    "src/index.js"
    "src/component-loader.js"
)

for js_file in "${js_files[@]}"; do
    status=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:5173/$js_file")
    if [ "$status" = "200" ]; then
        echo "✅ $js_file 可訪問"
    else
        echo "❌ $js_file 無法訪問 (狀態碼: $status)"
    fi
done

echo "🎯 測試完成"
