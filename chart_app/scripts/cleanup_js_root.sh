#!/bin/zsh
# filepath: /Users/aaron/Projects/DataScout/chart_app/scripts/cleanup_js_root.sh
# 清理 JavaScript 根目錄的腳本

JS_ROOT="/Users/aaron/Projects/DataScout/chart_app/src/js"

# 要保留的檔案列表
KEEP_FILES=(
  "README.md"
  "index.js"
  "main.js"
  "plugins"
  "adapters"
  "core"
  "data-handling"
  "utils"
)

echo "開始清理 JavaScript 根目錄..."
echo "以下檔案將被保留:"
for file in "${KEEP_FILES[@]}"; do
  echo "- ${file}"
done

echo "以下檔案將被移除:"
for file in "${JS_ROOT}"/*; do
  filename=$(basename "$file")
  keep=0
  
  # 檢查是否在保留列表中
  for keep_file in "${KEEP_FILES[@]}"; do
    if [[ "$filename" == "$keep_file" ]]; then
      keep=1
      break
    fi
  done
  
  if [[ $keep -eq 0 ]]; then
    echo "- ${filename}"
  fi
done

# 要求確認
echo -n "確認刪除上述檔案？(y/n): "
read confirm

if [[ "$confirm" != "y" ]]; then
  echo "取消操作，未刪除任何檔案。"
  exit 0
fi

# 執行刪除
for file in "${JS_ROOT}"/*; do
  filename=$(basename "$file")
  keep=0
  
  # 檢查是否在保留列表中
  for keep_file in "${KEEP_FILES[@]}"; do
    if [[ "$filename" == "$keep_file" ]]; then
      keep=1
      break
    fi
  done
  
  if [[ $keep -eq 0 ]]; then
    rm -f "$file"
    echo "已刪除: ${filename}"
  fi
done

echo "清理完成！"
