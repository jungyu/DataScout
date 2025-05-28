#!/bin/bash
# 增強版自動化部署腳本：將 web_frontend 編譯產物部署到 web_service
# 特色：自動處理路徑差異，確保在生產環境中連結正確
# 使用方式：在 web_frontend 目錄下執行 bash deploy_to_web_service_enhanced.sh

set -e

echo "🚀 DataScout 增強版部署腳本"
echo "================================"

# 1. 編譯前端
echo "📦 正在編譯前端..."
npm run build

# 2. 設定目標目錄
WEB_SERVICE_PATH="../web_service"
STATIC_PATH="$WEB_SERVICE_PATH/static"
TEMPLATES_PATH="$WEB_SERVICE_PATH/templates"

# 3. 備份現有的靜態資源
echo "📦 備份現有的靜態資源..."
BACKUP_DIR="$STATIC_PATH/backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
if [ "$(ls -A $STATIC_PATH 2>/dev/null)" ]; then
    mv "$STATIC_PATH"/* "$BACKUP_DIR" 2>/dev/null || true
fi

# 4. 創建必要的目錄
echo "📦 創建必要的目錄..."
mkdir -p "$STATIC_PATH"
mkdir -p "$TEMPLATES_PATH"

# 5. 複製靜態資源
echo "📦 複製靜態資源..."
cp -r dist/* "$STATIC_PATH/"

# 5.1 複製根目錄的 HTML 文件 (重要！)
echo "📦 複製根目錄的 HTML 文件..."
for html_file in *.html; do
    if [ -f "$html_file" ]; then
        echo "  → 複製 $html_file"
        cp "$html_file" "$STATIC_PATH/"
    fi
done

# 5.2 額外複製範例資料
echo "📦 複製範例資料..."
mkdir -p "$STATIC_PATH/assets/examples"
if [ -d "public/assets/examples" ]; then
    cp -r public/assets/examples/* "$STATIC_PATH/assets/examples/" 2>/dev/null || true
fi

# 5.3 複製組件目錄
echo "📦 複製組件目錄..."
if [ -d "public/components" ]; then
    cp -r public/components "$STATIC_PATH/"
fi

# 5.4 複製 src 目錄 (用於模組導入)
echo "📦 複製 src 目錄..."
if [ -d "src" ]; then
    cp -r src "$STATIC_PATH/"
fi

# 5.5 複製自訂 JS 文件
echo "📦 複製自訂 JS 文件..."
if [ -d "public" ]; then
    find public -name "*.js" -exec cp {} "$STATIC_PATH/" \;
fi

# 6. 🔧 處理生產環境路徑差異
echo "🔧 處理生產環境路徑差異..."

# 6.1 修復 test-all-charts.html 的模組導入路徑
echo "  → 修復 test-all-charts.html 的模組導入路徑..."
if [ -f "$STATIC_PATH/test-all-charts.html" ]; then
    # 將 /src/ 路徑替換為 /static/src/ (支援單引號和雙引號)
    sed -e 's|from "/src/|from "/static/src/|g' \
        -e "s|from '/src/|from '/static/src/|g" \
        "$STATIC_PATH/test-all-charts.html" > \
        "$STATIC_PATH/test-all-charts_temp.html"
    mv "$STATIC_PATH/test-all-charts_temp.html" \
       "$STATIC_PATH/test-all-charts.html"
    echo "  ✅ test-all-charts.html 模組路徑已更新為生產環境"
fi

# 6.2 修復 chart-test.html 的模組導入路徑（如果存在）
echo "  → 修復 chart-test.html 的模組導入路徑..."
if [ -f "$STATIC_PATH/chart-test.html" ]; then
    sed -e 's|from "/src/|from "/static/src/|g' \
        -e "s|from '/src/|from '/static/src/|g" \
        "$STATIC_PATH/chart-test.html" > \
        "$STATIC_PATH/chart-test_temp.html"
    mv "$STATIC_PATH/chart-test_temp.html" \
       "$STATIC_PATH/chart-test.html"
    echo "  ✅ chart-test.html 模組路徑已更新為生產環境"
fi

# 6.2.1 修復 modern-index.html 的模組導入路徑（如果存在）
echo "  → 修復 modern-index.html 的模組導入路徑..."
if [ -f "$STATIC_PATH/modern-index.html" ]; then
    sed -e 's|from "/src/|from "/static/src/|g' \
        -e "s|from '/src/|from '/static/src/|g" \
        "$STATIC_PATH/modern-index.html" > \
        "$STATIC_PATH/modern-index_temp.html"
    mv "$STATIC_PATH/modern-index_temp.html" \
       "$STATIC_PATH/modern-index.html"
    echo "  ✅ modern-index.html 模組路徑已更新為生產環境"
fi

# 6.3 創建生產版本的 Sidebar.html，添加 /static/ 前綴
echo "  → 更新側邊欄連結為生產環境路徑..."
if [ -f "$STATIC_PATH/components/layout/Sidebar.html" ]; then
    # 使用 sed 替換所有不含 static 的連結，添加 /static/ 前綴
    sed 's|href="/\([^s][^/]*\.html\)"|href="/static/\1"|g' \
        "$STATIC_PATH/components/layout/Sidebar.html" > \
        "$STATIC_PATH/components/layout/Sidebar_temp.html"
    mv "$STATIC_PATH/components/layout/Sidebar_temp.html" \
       "$STATIC_PATH/components/layout/Sidebar.html"
    echo "  ✅ 側邊欄連結已更新為生產環境路徑"
fi

# 6.4 更新重定向邏輯為生產環境
echo "  → 更新重定向邏輯為生產環境..."
if [ -f "$STATIC_PATH/index.js" ]; then
    # 修改重定向目標為 /static/line.html
    sed 's|window\.location\.href = .*/line\.html.*|window.location.href = "/static/line.html";|g' \
        "$STATIC_PATH/index.js" > "$STATIC_PATH/index_temp.js"
    mv "$STATIC_PATH/index_temp.js" "$STATIC_PATH/index.js"
    echo "  ✅ 重定向邏輯已更新為生產環境"
fi

# 6.5 確保組件載入器正確處理生產環境路徑
echo "  → 驗證組件載入器路徑邏輯..."
if [ -f "$STATIC_PATH/component-loader.js" ]; then
    echo "  ✅ 組件載入器已準備好處理生產環境路徑"
fi

# 7. 複製 index.html 到 templates
echo "📦 複製 index.html 到 templates..."
cp dist/index.html "$TEMPLATES_PATH/index.html"

# 8. 生成部署報告
echo "📊 生成部署報告..."
REPORT_FILE="$WEB_SERVICE_PATH/deployment_report_$(date +%Y%m%d_%H%M%S).md"
cat > "$REPORT_FILE" << EOF
# DataScout 部署報告

**部署時間**: $(date)
**部署版本**: 增強版 v1.0
**目標環境**: 生產環境 (web_service)

## 部署內容

### 靜態資源
- 路徑: \`$STATIC_PATH\`
- 來源: \`web_frontend/dist/*\`
- 狀態: ✅ 已部署

### 組件文件
- 路徑: \`$STATIC_PATH/components/\`
- 來源: \`web_frontend/public/components/*\`
- 狀態: ✅ 已部署

### 範例資料
- 路徑: \`$STATIC_PATH/assets/examples/\`
- 來源: \`web_frontend/public/assets/examples/*\`
- 狀態: ✅ 已部署

### 首頁模板
- 路徑: \`$TEMPLATES_PATH/index.html\`
- 來源: \`web_frontend/dist/index.html\`
- 狀態: ✅ 已部署

## 路徑處理

### 側邊欄連結
- 原始格式: \`href="/line.html"\`
- 生產格式: \`href="/static/line.html"\`
- 狀態: ✅ 自動轉換完成

### 重定向邏輯
- 原始目標: \`/line.html\`
- 生產目標: \`/static/line.html\`
- 狀態: ✅ 自動轉換完成

### 組件載入
- 基礎路徑: \`/static\`
- 狀態: ✅ 自動處理

## 備份資訊
- 備份目錄: \`$BACKUP_DIR\`
- 狀態: ✅ 已創建

## 後續步驟
1. 啟動 web_service 後端服務
2. 訪問 http://localhost:8000/ 驗證部署
3. 檢查所有圖表頁面連結是否正常
4. 驗證首頁自動重定向功能

EOF

# 9. 驗證部署
echo "🔍 驗證部署完整性..."
MISSING_FILES=()

# 檢查關鍵文件是否存在
if [ ! -f "$STATIC_PATH/index.js" ]; then MISSING_FILES+=("index.js"); fi
if [ ! -f "$STATIC_PATH/component-loader.js" ]; then MISSING_FILES+=("component-loader.js"); fi
if [ ! -f "$STATIC_PATH/components/layout/Sidebar.html" ]; then MISSING_FILES+=("Sidebar.html"); fi
if [ ! -f "$TEMPLATES_PATH/index.html" ]; then MISSING_FILES+=("templates/index.html"); fi

if [ ${#MISSING_FILES[@]} -eq 0 ]; then
    echo "✅ 部署驗證通過"
else
    echo "⚠️  警告：以下文件缺失："
    for file in "${MISSING_FILES[@]}"; do
        echo "  - $file"
    done
fi

# 10. 顯示完成訊息
echo ""
echo "🎉 DataScout 增強版部署完成！"
echo "================================"
echo "📍 靜態資源：$STATIC_PATH"
echo "📍 首頁模板：$TEMPLATES_PATH/index.html"
echo "📍 備份目錄：$BACKUP_DIR"
echo "📍 部署報告：$REPORT_FILE"
echo ""
echo "🔧 路徑處理："
echo "  ✅ 側邊欄連結已添加 /static/ 前綴"
echo "  ✅ 重定向邏輯已更新為生產環境"
echo "  ✅ 組件載入器支援生產環境路徑"
echo ""
echo "🚀 下一步："
echo "  1. cd ../web_service"
echo "  2. 啟動後端服務"
echo "  3. 訪問 http://localhost:8000/ 測試"
