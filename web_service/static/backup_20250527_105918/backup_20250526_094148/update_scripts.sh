#!/bin/zsh
# 更新所有HTML頁面，確保它們引用了所有必要的腳本

# 設定工作目錄
cd /Users/aaron/Downloads/Techwind_v3.0.0/HTML/Dashboard/frontend/public

# 需要包含的腳本列表（按照正確順序）
SCRIPTS=(
  "./json-formatter-fix.js"
  "./json-enhancer.js"
  "./chart-error-handler.js"
  "./chart-error-handler-enhanced.js"
  "./chart-recovery-tool.js"
  "./chart-testing-tool.js"
)

# 這些腳本應該延遲加載
DEFERRED_SCRIPTS=(
  "./example-toggle.js"
  "./file-upload-handler.js"
  "./unified-chart-handler.js"
  "./data-loader.js"
  "./chart-fix.js"
  "./chart-compat.js"
  "./chart-verification.js"
)

# 所有HTML文件
HTML_FILES=(
  "index.html"
  "line.html" 
  "area.html" 
  "bar.html" 
  "column.html"
  "pie.html"
  "donut.html"
  "radar.html"
  "polararea.html"
  "heatmap.html"
  "treemap.html"
  "scatter.html"
  "mixed.html"
)

# 修改每個HTML文件，確保它包含必要的腳本
for html_file in "${HTML_FILES[@]}"; do
  if [ -f "$html_file" ]; then
    echo "正在處理 $html_file"
    
    # 檢查每個必要的腳本是否存在
    for script in "${SCRIPTS[@]}"; do
      if ! grep -q "$script" "$html_file"; then
        sed -i '' -e "/<script src=\"https:\/\/cdn.jsdelivr.net\/npm\/apexcharts\"><\/script>/a\\
  <script src=\"$script\"></script>" "$html_file"
        echo "  添加了 $script"
      fi
    done
    
    # 確保延遲加載的腳本存在並有defer屬性
    for script in "${DEFERRED_SCRIPTS[@]}"; do
      if ! grep -q "$script" "$html_file"; then
        sed -i '' -e "/<\/head>/i\\
  <script src=\"$script\" defer></script>" "$html_file"
        echo "  添加了延遲加載腳本 $script"
      elif ! grep -q "$script.*defer" "$html_file"; then
        sed -i '' -e "s/<script src=\"$script\">/<script src=\"$script\" defer>/g" "$html_file"
        echo "  添加了defer屬性到 $script"
      fi
    done
    
    # 確保每個HTML有對應的圖表處理器腳本
    chart_type=$(basename "$html_file" .html)
    handler_script="./${chart_type}-chart-handler.js"
    
    if [ -f "$handler_script" ] && ! grep -q "$handler_script" "$html_file"; then
      sed -i '' -e "/<script src=\".*chart-verification.js.*\".*>/a\\
  <script src=\"$handler_script\" defer></script>" "$html_file"
      echo "  添加了對應的圖表處理器 $handler_script"
    fi
  else
    echo "警告：找不到文件 $html_file"
  fi
done

echo "所有HTML文件已更新完成"
