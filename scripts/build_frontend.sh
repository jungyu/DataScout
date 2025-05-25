#!/bin/bash
# DataScout 前端構建腳本
# 這個腳本用於構建前端資源並將它們複製到後端靜態目錄

set -e  # 出錯立即退出

# 預設參數
FRONTEND_DIR="$(dirname "$0")/../web_frontend"
OUTPUT_DIR="$(dirname "$0")/../web_service/static"
VERBOSE=0

# 解析命令行參數
while [[ "$#" -gt 0 ]]; do
  case $1 in
    -o|--output) OUTPUT_DIR="$2"; shift ;;
    -f|--frontend) FRONTEND_DIR="$2"; shift ;;
    -v|--verbose) VERBOSE=1 ;;
    *) echo "未知參數: $1"; exit 1 ;;
  esac
  shift
done

# 輸出配置信息
echo "前端目錄: $FRONTEND_DIR"
echo "輸出目錄: $OUTPUT_DIR"

# 確保目錄存在
if [ ! -d "$FRONTEND_DIR" ]; then
  echo "錯誤: 前端目錄不存在: $FRONTEND_DIR"
  exit 1
fi

# 檢查npm是否安裝
if ! command -v npm &> /dev/null; then
  echo "錯誤: npm未安裝，請先安裝Node.js和npm"
  exit 1
fi

# 進入前端目錄
cd "$FRONTEND_DIR"

# 安裝依賴
echo "安裝前端依賴..."
npm install

# 構建前端資源
echo "構建前端資源..."
npm run build

# 確保輸出目錄存在
mkdir -p "$OUTPUT_DIR"

# 複製構建結果到輸出目錄
echo "複製構建結果到後端靜態目錄..."
# 確保目標資料夾存在
mkdir -p "$OUTPUT_DIR/assets"

# 先複製主要構建結果
if [ $VERBOSE -eq 1 ]; then
  # 啟用詳細輸出
  cp -rv dist/* "$OUTPUT_DIR/"
  
  # 特別注意 JavaScript 和其他靜態資源文件
  echo "確保 JavaScript 和其他資源文件已正確複製..."
  ASSETS_DIR="$FRONTEND_DIR/dist/assets"
  if [ -d "$ASSETS_DIR" ]; then
    # 確保所有 JavaScript 文件被複製
    find "$ASSETS_DIR" -name "*.js" -exec cp -v {} "$OUTPUT_DIR/assets/" \;
    # 確保 JS map 文件被複製
    find "$ASSETS_DIR" -name "*.js.map" -exec cp -v {} "$OUTPUT_DIR/assets/" \;
    # 確保 CSS 文件被複製
    find "$ASSETS_DIR" -name "*.css" -exec cp -v {} "$OUTPUT_DIR/assets/" \;
    # 確保 CSS map 文件被複製
    find "$ASSETS_DIR" -name "*.css.map" -exec cp -v {} "$OUTPUT_DIR/assets/" \;
    # 確保其他資源文件被複製
    find "$ASSETS_DIR" -type f -not -name "*.js" -not -name "*.js.map" -not -name "*.css" -not -name "*.css.map" -exec cp -v {} "$OUTPUT_DIR/assets/" \;
  fi
else
  # 簡單輸出
  cp -r dist/* "$OUTPUT_DIR/"
  
  # 特別注意 JavaScript 文件
  echo "確保 JavaScript 文件已正確複製..."
  ASSETS_DIR="$FRONTEND_DIR/dist/assets"
  if [ -d "$ASSETS_DIR" ]; then
    find "$ASSETS_DIR" -name "*.js" -exec cp {} "$OUTPUT_DIR/assets/" \;
  fi
fi

# 確保 index.html 正確引用 js 文件
# 檢查構建後的 index.html 是否包含腳本標籤
INDEX_HTML="$OUTPUT_DIR/index.html"
if [ -f "$INDEX_HTML" ]; then
  if ! grep -q "<script.*src=\"/static/assets" "$INDEX_HTML"; then
    echo "修正 index.html 腳本路徑..."
    # 尋找資源文件
    JS_FILES=$(find "$OUTPUT_DIR/assets" -name "*.js" | grep -v "polyfill" | head -n 1)
    if [ -n "$JS_FILES" ]; then
      JS_FILE=$(basename "$JS_FILES")
      # 在 </body> 標籤前添加腳本標籤
      sed -i.bak "s|</body>|<script type=\"module\" src=\"/static/assets/$JS_FILE\"></script></body>|g" "$INDEX_HTML"
      rm -f "$INDEX_HTML.bak"
      echo "已添加腳本標籤: $JS_FILE"
    fi
  fi
fi

# 驗證所有必需的文件都已正確複製
echo "驗證構建結果..."
if [ ! -f "$INDEX_HTML" ]; then
  echo "錯誤: 找不到 index.html 文件！"
  exit 1
fi

# 檢查 JS 文件
JS_COUNT=$(find "$OUTPUT_DIR/assets" -name "*.js" | wc -l | tr -d '[:space:]')
if [ "$JS_COUNT" -eq 0 ]; then
  echo "錯誤: 沒有找到 JavaScript 文件！"
  exit 1
else
  echo "找到 $JS_COUNT 個 JavaScript 文件"
fi

# 確保組件目錄結構完整
COMPONENTS_DIR="$OUTPUT_DIR/components"
if [ ! -d "$COMPONENTS_DIR" ]; then
  echo "警告: 組件目錄不存在，正在複製..."
  cp -rv "$FRONTEND_DIR/public/components" "$OUTPUT_DIR/"
fi

# 檢查關鍵組件是否存在
if [ ! -d "$COMPONENTS_DIR/layout" ] || [ ! -d "$COMPONENTS_DIR/charts" ]; then
  echo "警告: 關鍵組件目錄不完整，正在修復..."
  mkdir -p "$COMPONENTS_DIR/layout" "$COMPONENTS_DIR/charts" "$COMPONENTS_DIR/ui"
  
  # 從前端復制關鍵組件
  if [ -d "$FRONTEND_DIR/public/components/layout" ]; then
    cp -rv "$FRONTEND_DIR/public/components/layout"/* "$COMPONENTS_DIR/layout/"
  fi
  
  if [ -d "$FRONTEND_DIR/public/components/charts" ]; then
    cp -rv "$FRONTEND_DIR/public/components/charts"/* "$COMPONENTS_DIR/charts/"
  fi
  
  if [ -d "$FRONTEND_DIR/public/components/ui" ]; then
    cp -rv "$FRONTEND_DIR/public/components/ui"/* "$COMPONENTS_DIR/ui/"
  fi
fi

echo "前端構建和部署完成！"
exit 0