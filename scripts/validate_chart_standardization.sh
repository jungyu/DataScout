#!/bin/bash

# 圖表標準化驗證腳本
# 檢查所有圖表頁面的初始化函數和組件文件

echo "🔍 DataScout 圖表標準化驗證報告"
echo "================================="

# 定義圖表類型
chart_types=("line" "area" "column" "bar" "pie" "donut" "scatter" "mixed" "heatmap" "polararea" "treemap" "radar" "candlestick")

# 檢查每個圖表頁面
for chart in "${chart_types[@]}"; do
    echo ""
    echo "📊 檢查 ${chart} 圖表..."
    
    # 檢查 HTML 文件是否存在
    html_file="/Users/aaron/Projects/DataScout/web_frontend/public/${chart}.html"
    if [[ -f "$html_file" ]]; then
        echo "  ✅ HTML 文件存在: ${chart}.html"
        
        # 檢查初始化函數
        if [[ "$chart" == "polararea" ]]; then
            chart_capitalized="PolarArea"
        else
            chart_capitalized=$(echo "${chart:0:1}" | tr '[:lower:]' '[:upper:]')$(echo "${chart:1}")
        fi
        
        if grep -q "function init${chart_capitalized}Chart" "$html_file"; then
            echo "  ✅ 初始化函數存在: init${chart_capitalized}Chart()"
        else
            echo "  ❌ 初始化函數缺失: init${chart_capitalized}Chart()"
        fi
        
        # 檢查外部數據參數支持
        if grep -q "function init${chart_capitalized}Chart(externalData)" "$html_file"; then
            echo "  ✅ 支援外部數據參數"
        else
            echo "  ⚠️  未檢測到外部數據參數支持"
        fi
        
        # 檢查清理函數調用
        if grep -q "window.cleanupChartInstances" "$html_file"; then
            echo "  ✅ 包含清理函數調用"
        else
            echo "  ❌ 缺少清理函數調用"
        fi
        
        # 檢查圖表註冊
        if grep -q "window.registerChartInstance" "$html_file"; then
            echo "  ✅ 包含圖表實例註冊"
        else
            echo "  ❌ 缺少圖表實例註冊"
        fi
        
        # 檢查 JSON 數據載入
        if grep -q "fetch.*apexcharts_${chart}" "$html_file"; then
            echo "  ✅ 包含 JSON 數據載入"
        else
            echo "  ⚠️  未檢測到 JSON 數據載入"
        fi
        
        # 檢查默認數據回退
        if grep -q "defaultData.*=" "$html_file"; then
            echo "  ✅ 包含默認數據回退"
        else
            echo "  ❌ 缺少默認數據回退"
        fi
        
    else
        echo "  ❌ HTML 文件不存在: ${chart}.html"
    fi
    
    # 檢查組件文件
    if [[ "$chart" == "polararea" ]]; then
        component_file="/Users/aaron/Projects/DataScout/web_frontend/public/components/charts/PolarareaChartContent.html"
    else
        component_file="/Users/aaron/Projects/DataScout/web_frontend/public/components/charts/${chart_capitalized}ChartContent.html"
    fi
    
    if [[ -f "$component_file" ]]; then
        echo "  ✅ 組件文件存在: $(basename "$component_file")"
    else
        echo "  ❌ 組件文件缺失: $(basename "$component_file")"
    fi
done

echo ""
echo "🏁 驗證完成"
echo ""
echo "📝 總結:"
echo "- 已檢查 ${#chart_types[@]} 個圖表類型"
echo "- 請查看上方報告以確認所有項目狀態"
echo ""
echo "💡 修復建議:"
echo "1. 對於缺失的初始化函數，請參考 line.html 模式進行添加"
echo "2. 對於缺失的組件文件，請基於現有組件創建對應文件"
echo "3. 確保所有圖表都支持外部數據參數和實例管理"
