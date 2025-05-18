#!/bin/bash
# 重構修復腳本

# 顯示腳本開始執行
echo "開始修復範例文件載入問題..."

# 1. 備份原始文件
echo "備份原始文件..."
mkdir -p backup
cp src/js/main.js backup/main.js.bak
cp src/js/core/ui-controller.js backup/ui-controller.js.bak

# 2. 修改 main.js 添加導入
echo "修改 main.js 添加導入..."
sed -i '' 's|import { initThemeHandler } from '\''./utils/theme-handler.js'\'';\(.*\)|import { initThemeHandler } from '\''./utils/theme-handler.js'\'';\1\nimport { fetchAvailableExamples } from '\''./data-handling/examples/index.js'\'';\n|' src/js/main.js

echo "修改完成！"

# 3. 執行測試
echo "運行構建測試..."
npm run build:js:dev

echo "修復完成"
