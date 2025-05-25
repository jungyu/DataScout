#!/bin/bash
# 自動化部署腳本：將 web_frontend 編譯產物部署到 web_service
# 使用方式：在 web_frontend 目錄下執行 bash deploy_to_web_service.sh

set -e

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
mv "$STATIC_PATH"/* "$BACKUP_DIR" 2>/dev/null || true

# 4. 創建必要的目錄
echo "📦 創建必要的目錄..."
mkdir -p "$STATIC_PATH"
mkdir -p "$TEMPLATES_PATH"

# 5. 複製靜態資源
echo "📦 複製靜態資源..."
cp -r dist/* "$STATIC_PATH/"

# 5.1 額外複製範例資料（確保 examples 目錄一定存在）
echo "📦 額外複製範例資料..."
mkdir -p "$STATIC_PATH/assets/examples"
cp -r public/assets/examples/* "$STATIC_PATH/assets/examples/" 2>/dev/null || true

# 5.2 複製組件（特別是 charts 目錄）
echo "📦 複製組件 components/charts..."
mkdir -p "$STATIC_PATH/components/charts"
cp -r public/components/charts/*.html "$STATIC_PATH/components/charts/"

# 5.3 複製自訂 JS（如 data-loader.js、component-loader.js 等）
echo "📦 複製自訂 JS..."
cp -r public/*.js "$STATIC_PATH/"

# 6. 複製 index.html 到 templates
echo "📦 複製 index.html 到 templates..."
cp dist/index.html "$TEMPLATES_PATH/index.html"

# 7. 顯示完成訊息
echo "✅ 前端已成功部署到 web_service！"
echo "- 靜態資源：$STATIC_PATH"
echo "- 首頁模板：$TEMPLATES_PATH/index.html"
echo "- 備份目錄：$BACKUP_DIR" 