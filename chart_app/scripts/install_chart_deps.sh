#!/bin/bash
# 安裝並配置Chart.js相關依賴

set -e

echo "開始安裝Chart.js相關依賴..."
cd "$(dirname "$0")/.."

# 確認npm和node已安裝
if ! command -v npm &> /dev/null; then
    echo "錯誤: npm未安裝. 請先安裝Node.js及npm."
    exit 1
fi

# 安裝chartjs-adapter-luxon和必要依賴
echo "安裝chartjs-adapter-luxon及相關依賴..."
npm install --save chart.js@3.9.1 luxon@2.5.0 chartjs-adapter-luxon@1.3.0

# 編譯JavaScript
echo "編譯JavaScript檔案..."
npm run build:js:prod

# 確認目錄結構
mkdir -p static/js/dist

echo "Chart.js相關依賴已安裝完成!"
echo "請在瀏覽器中重新整理頁面，並檢查控制台是否有錯誤訊息。"
