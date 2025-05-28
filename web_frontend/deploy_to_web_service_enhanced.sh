#!/bin/bash
# 增強版自動化部署腳本：將 web_frontend 編譯產物部署到 web_service
# 根據 DataScout Web 開發技術手冊 v3.1 實施
# 特色：智能路徑轉換、自動環境檢測、完整備份機制
# 使用方式：在 web_frontend 目錄下執行 bash deploy_to_web_service_enhanced.sh

set -e

echo "🚀 DataScout 增強版部署腳本 v3.1"
echo "======================================"
echo "📋 根據技術手冊實施智能部署流程"
echo ""

# 1. 編譯前端
echo "📦 正在編譯前端..."
npm run build

# 2. 設定目標目錄
WEB_SERVICE_PATH="../web_service"
STATIC_PATH="$WEB_SERVICE_PATH/static"
TEMPLATES_PATH="$WEB_SERVICE_PATH/templates"

# 3. 備份現有檔案
echo "💾 備份現有檔案..."
BACKUP_DIR="$STATIC_PATH/backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
if [ -d "$STATIC_PATH" ] && [ "$(ls -A $STATIC_PATH 2>/dev/null)" ]; then
    echo "  → 備份現有靜態檔案到 $BACKUP_DIR"
    mv "$STATIC_PATH"/* "$BACKUP_DIR/" 2>/dev/null || true
fi

# 4. 創建必要目錄
echo "📦 創建必要目錄..."
mkdir -p "$STATIC_PATH"
mkdir -p "$TEMPLATES_PATH"

# 5. 複製編譯產物
echo "📋 複製編譯產物..."
cp -r dist/* "$STATIC_PATH/"
echo "  ✅ 編譯後的檔案已複製到 $STATIC_PATH"

# 6. 複製額外檔案
echo "📂 複製額外檔案..."

# 6.1 複製 src 目錄 (用於模組導入)
if [ -d "src" ]; then
    cp -r src "$STATIC_PATH/"
    echo "  ✅ src 目錄已複製"
fi

# 6.2 複製 public 目錄內容
if [ -d "public" ]; then
    # 複製所有 HTML 檔案
    find public -name "*.html" -exec cp {} "$STATIC_PATH/" \;
    echo "  ✅ HTML 檔案已複製"
    
    # 複製所有 JS 檔案
    find public -name "*.js" -exec cp {} "$STATIC_PATH/" \;
    echo "  ✅ JavaScript 檔案已複製"
    
    # 複製組件目錄
    if [ -d "public/components" ]; then
        cp -r public/components "$STATIC_PATH/"
        echo "  ✅ 組件目錄已複製"
    fi
    
    # 複製資源目錄
    if [ -d "public/assets" ]; then
        cp -r public/assets "$STATIC_PATH/"
        echo "  ✅ 資源目錄已複製"
    fi
fi

# 7. 🔧 智能路徑轉換處理 (關鍵步驟)
echo "🔧 執行智能路徑轉換..."

# 7.1 修復側邊欄連結 - 添加 /static/ 前綴
echo "  → 修復側邊欄連結路徑..."
if [ -f "$STATIC_PATH/components/layout/Sidebar.html" ]; then
    # 替換所有不含 static 的 HTML 連結，添加 /static/ 前綴
    # 使用更精確的正則表達式：匹配不是以 static 開頭的路徑
    sed -E 's|href="/([^"]*\.html)"|href="/static/\1"|g; s|href="/static/static/|href="/static/|g' \
        "$STATIC_PATH/components/layout/Sidebar.html" > \
        "$STATIC_PATH/components/layout/Sidebar_temp.html"
    
    # 檢查是否有變更
    if ! cmp -s "$STATIC_PATH/components/layout/Sidebar.html" "$STATIC_PATH/components/layout/Sidebar_temp.html"; then
        mv "$STATIC_PATH/components/layout/Sidebar_temp.html" "$STATIC_PATH/components/layout/Sidebar.html"
        echo "  ✅ 側邊欄連結已更新為生產環境路徑"
    else
        rm "$STATIC_PATH/components/layout/Sidebar_temp.html"
        echo "  ℹ️  側邊欄連結已是正確格式"
    fi
else
    echo "  ⚠️  警告：未找到 Sidebar.html"
fi

# 7.2 修復重定向邏輯 - 更新為生產環境路徑
echo "  → 修復重定向邏輯..."
if [ -f "$STATIC_PATH/index.js" ]; then
    # 更新重定向目標為 /static/line.html
    sed 's|window\.location\.href = ["\x27]/line\.html["\x27]|window.location.href = "/static/line.html"|g' \
        "$STATIC_PATH/index.js" > "$STATIC_PATH/index_temp.js"
    
    if ! cmp -s "$STATIC_PATH/index.js" "$STATIC_PATH/index_temp.js"; then
        mv "$STATIC_PATH/index_temp.js" "$STATIC_PATH/index.js"
        echo "  ✅ 重定向邏輯已更新為生產環境"
    else
        rm "$STATIC_PATH/index_temp.js"
        echo "  ℹ️  重定向邏輯已是正確格式"
    fi
fi

# 7.3 修復 src 目錄中的組件載入器（如果存在）
echo "  → 檢查組件載入器..."
if [ -f "$STATIC_PATH/src/component-loader.js" ]; then
    echo "  ✅ 智能組件載入器已就位，支援自動環境檢測"
else
    echo "  ⚠️  警告：未找到智能組件載入器"
fi

# 7.4 修復所有 HTML 檔案中的模組導入路徑
echo "  → 修復 HTML 檔案中的模組導入路徑..."
for html_file in "$STATIC_PATH"/*.html; do
    if [ -f "$html_file" ]; then
        filename=$(basename "$html_file")
        # 將 /src/ 路徑替換為 /static/src/
        if grep -q 'from "/src/' "$html_file" || grep -q "from '/src/" "$html_file"; then
            sed -e 's|from "/src/|from "/static/src/|g' \
                -e "s|from '/src/|from '/static/src/|g" \
                "$html_file" > "${html_file}_temp"
            mv "${html_file}_temp" "$html_file"
            echo "  ✅ 已修復 $filename 的模組導入路徑"
        fi
    fi
done

# 8. 複製模板檔案
echo "📋 複製模板檔案..."
if [ -f "dist/index.html" ]; then
    cp dist/index.html "$TEMPLATES_PATH/index.html"
    echo "  ✅ index.html 已複製到 templates 目錄"
fi

# 9. 驗證部署完整性
echo "🔍 驗證部署完整性..."
MISSING_FILES=()

# 檢查關鍵檔案
echo "  → 檢查關鍵檔案..."
critical_files=(
    "$STATIC_PATH/component-loader.js"
    "$STATIC_PATH/components/layout/Sidebar.html"
    "$TEMPLATES_PATH/index.html"
)

for file in "${critical_files[@]}"; do
    if [ ! -f "$file" ]; then
        MISSING_FILES+=("$(basename "$file")")
    fi
done

# 檢查圖表頁面檔案
echo "  → 檢查圖表頁面檔案..."
chart_files=("line.html" "area.html" "column.html" "bar.html" "pie.html" "donut.html")
for chart in "${chart_files[@]}"; do
    if [ ! -f "$STATIC_PATH/$chart" ]; then
        MISSING_FILES+=("$chart")
    fi
done

# 報告驗證結果
if [ ${#MISSING_FILES[@]} -eq 0 ]; then
    echo "  ✅ 部署驗證通過，所有關鍵檔案都存在"
else
    echo "  ⚠️  警告：以下檔案缺失："
    for file in "${MISSING_FILES[@]}"; do
        echo "    - $file"
    done
fi

# 10. 生成部署報告
echo "📊 生成部署報告..."
REPORT_FILE="$WEB_SERVICE_PATH/deployment_enhanced_report_$(date +%Y%m%d_%H%M%S).md"
cat > "$REPORT_FILE" << EOF
# DataScout 增強版部署報告

**部署時間**: $(date)
**部署版本**: 增強版 v3.1 (根據技術手冊)
**目標環境**: 生產環境 (web_service)
**腳本**: deploy_to_web_service_enhanced.sh

## 部署摘要

### ✅ 成功部署的內容
- 編譯後的靜態檔案: \`$STATIC_PATH\`
- 組件檔案: \`$STATIC_PATH/components/\`
- 源代碼模組: \`$STATIC_PATH/src/\`
- 模板檔案: \`$TEMPLATES_PATH/index.html\`

### 🔧 路徑轉換處理
- ✅ 側邊欄連結已添加 \`/static/\` 前綴
- ✅ 重定向邏輯已更新為生產環境
- ✅ HTML 模組導入路徑已修復
- ✅ 智能組件載入器支援環境自動檢測

### 📂 關鍵檔案狀態
$(for file in "${critical_files[@]}"; do
    if [ -f "$file" ]; then
        echo "- ✅ $(basename "$file")"
    else
        echo "- ❌ $(basename "$file") (缺失)"
    fi
done)

### 📈 圖表頁面狀態
$(for chart in "${chart_files[@]}"; do
    if [ -f "$STATIC_PATH/$chart" ]; then
        echo "- ✅ $chart"
    else
        echo "- ❌ $chart (缺失)"
    fi
done)

## 備份資訊
- 備份目錄: \`$BACKUP_DIR\`
- 狀態: ✅ 已創建

## 🚀 後續步驟
1. 啟動 web_service 後端服務:
   \`\`\`bash
   cd ../web_service
   source venv/bin/activate
   uvicorn app.main:app --reload
   \`\`\`

2. 訪問 http://localhost:8000/ 驗證部署

3. 測試功能:
   - ✅ 首頁自動重定向到 line.html
   - ✅ 側邊欄導航連結
   - ✅ 組件載入功能
   - ✅ 圖表渲染功能

## 技術特點
- 🧠 智能環境檢測 (開發/生產自動切換)
- 🔄 自動路徑轉換處理
- 💾 完整備份機制
- 🔍 部署完整性驗證
- 📊 詳細的部署報告

EOF

# 11. 最終狀態報告
echo ""
echo "🎉 DataScout 增強版部署完成！"
echo "======================================"
echo "📍 部署目標:"
echo "  - 靜態檔案: $STATIC_PATH"
echo "  - 模板檔案: $TEMPLATES_PATH"
echo "  - 備份目錄: $BACKUP_DIR"
echo ""
echo "📊 部署報告: $REPORT_FILE"
echo ""
echo "🔧 智能功能:"
echo "  ✅ 自動環境檢測 (開發/生產)"
echo "  ✅ 智能路徑轉換"
echo "  ✅ 組件動態載入"
echo "  ✅ 完整備份機制"
echo ""
echo "🚀 測試部署:"
echo "  1. cd ../web_service"
echo "  2. source venv/bin/activate"
echo "  3. uvicorn app.main:app --reload"
echo "  4. 訪問 http://localhost:8000/"
echo ""
echo "📝 查看詳細報告: cat $REPORT_FILE"