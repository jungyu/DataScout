#!/bin/bash
# 這個腳本用來更新圖表相關的依賴，並重新編譯JS文件

echo "開始更新圖表依賴..."

# 安裝npm依賴
echo "安裝npm依賴..."
npm install

# 清理舊的編譯文件
echo "清理舊的編譯文件..."
npm run clean

# 重新編譯JS
echo "重新編譯JavaScript..."
npm run build:js:prod

echo "更新圖表依賴完成！"
