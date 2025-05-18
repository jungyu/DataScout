#!/bin/bash
# 清理 src/js 根目錄中的冗餘空文件

# 定義要移除的文件列表
FILES_TO_REMOVE=(
  "/Users/aaron/Projects/DataScout/chart_app/src/js/app-initializer.js"
  "/Users/aaron/Projects/DataScout/chart_app/src/js/chart-fix.js"
  "/Users/aaron/Projects/DataScout/chart_app/src/js/chart-manager.js"
  "/Users/aaron/Projects/DataScout/chart_app/src/js/chart-type-adapters.js"
  "/Users/aaron/Projects/DataScout/chart_app/src/js/data-loader.js"
  "/Users/aaron/Projects/DataScout/chart_app/src/js/data-processor.js"
  "/Users/aaron/Projects/DataScout/chart_app/src/js/dependency-checker.js"
  "/Users/aaron/Projects/DataScout/chart_app/src/js/example-manager.js"
  "/Users/aaron/Projects/DataScout/chart_app/src/js/state-manager.js"
  "/Users/aaron/Projects/DataScout/chart_app/src/js/ui-controller.js"
)

# 檢查並刪除空文件
echo "開始清理 src/js 根目錄中的冗餘文件..."
for file in "${FILES_TO_REMOVE[@]}"; do
  if [ -f "$file" ]; then
    # 檢查文件是否為空
    if [ ! -s "$file" ]; then
      echo "移除空文件: $file"
      rm "$file"
    else
      echo "警告: $file 不是空文件，請手動確認是否可以安全刪除"
    fi
  else
    echo "文件不存在: $file"
  fi
done

echo "清理完成！"
