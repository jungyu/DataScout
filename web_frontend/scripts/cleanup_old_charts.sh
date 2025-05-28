#!/bin/bash

# DataScout 舊圖表頁面清理腳本
# 移除不再需要的單圖表頁面，以避免用戶混淆

set -e

echo "🧹 DataScout 舊圖表頁面清理"
echo "========================="

WEB_SERVICE_STATIC="/Users/aaron/Projects/DataScout/web_service/static"

# 需要移除的舊圖表頁面
OLD_CHART_FILES=(
    "line.html"
    "area.html"
    "bar.html" 
    "column.html"
    "pie.html"
    "donut.html"
    "scatter.html"
    "bubble.html"
    "candlestick.html"
    "boxplot.html"
    "heatmap.html"
    "treemap.html"
    "radar.html"
    "polar.html"
    "funnel.html"
    "mixed.html"
    "stacked_bar.html"
    "column_backup.html"
    "candlestick_backup_2.html"
)

echo "📦 正在清理舊圖表頁面..."

for file in "${OLD_CHART_FILES[@]}"; do
    if [ -f "$WEB_SERVICE_STATIC/$file" ]; then
        echo "  🗑️  移除 $file"
        rm "$WEB_SERVICE_STATIC/$file"
    else
        echo "  ✅ $file 不存在"
    fi
done

# 移除相關的舊處理器檔案
OLD_HANDLER_FILES=(
    "line-chart-handler.js"
    "area-chart-handler.js"
    "bar-chart-handler.js"
    "candlestick-chart-handler.js"
    "enhanced-line-chart-handler.js"
    "line-chart-data-override.js"
    "area-fix.js"
    "candlestick-fix.js"
    "apexcharts-fix.js"
)

echo "🔧 正在清理舊處理器檔案..."

for file in "${OLD_HANDLER_FILES[@]}"; do
    if [ -f "$WEB_SERVICE_STATIC/$file" ]; then
        echo "  🗑️  移除 $file"
        rm "$WEB_SERVICE_STATIC/$file"
    else
        echo "  ✅ $file 不存在"
    fi
done

echo ""
echo "🎉 清理完成！"
echo "✅ 現在只保留現代化的 Alpine.js 架構頁面："
echo "   - modern-index.html (主頁面)"
echo "   - test-all-charts.html (所有圖表測試)"
echo "   - chart-test.html (詳細圖表測試)"
echo ""
echo "🔗 訪問方式："
echo "   - http://127.0.0.1:8003/static/modern-index.html"
echo "   - http://127.0.0.1:8003/static/test-all-charts.html"
echo "   - http://127.0.0.1:8003/static/chart-test.html"
