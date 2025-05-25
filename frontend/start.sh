#!/bin/bash
# DataScout 儀表板啟動腳本

echo "===== DataScout 儀表板啟動腳本 ====="
echo "正在安裝依賴..."
npm install

echo "啟動開發伺服器在端口 8000..."
npm run start

echo "請在瀏覽器中訪問 http://localhost:8000"

# 備註：如果您想要建構生產版本，請使用下面的命令
# npm run build
