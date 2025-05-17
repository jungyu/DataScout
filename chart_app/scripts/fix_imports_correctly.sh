#!/bin/zsh
# filepath: /Users/aaron/Projects/DataScout/chart_app/scripts/fix_imports_correctly.sh
# 正確修復模組導入路徑的腳本

JS_ROOT="/Users/aaron/Projects/DataScout/chart_app/src/js"

echo "開始修復模組導入路徑..."

# 修復 core 目錄下的檔案
echo "修復 core 目錄下的檔案..."
find "${JS_ROOT}/core" -name "*.js" | while read file; do
  # 替換導入路徑
  sed -i '' 's|import .* from '\''./utils.js'\'';|import \{ showError, showSuccess, showLoading, fetchFileData \} from "../utils/utils.js";|g' "$file"
  sed -i '' 's|import .* from '\''./theme-handler.js'\'';|import \{ syncChartThemeWithPageTheme, initThemeHandler \} from "../utils/theme-handler.js";|g' "$file"
  sed -i '' 's|import .* from '\''./file-handler.js'\'';|import \{ guessChartTypeFromFilename \} from "../utils/file-handler.js";|g' "$file"
  sed -i '' 's|import .* from '\''./chart-renderer.js'\'';|import \{ createChart, captureChart \} from "../adapters/chart-renderer.js";|g' "$file"
  sed -i '' 's|import .* from '\''./chart-type-adapters.js'\'';|import \{ ChartTypeAdapter \} from "../adapters/chart-type-adapters.js";|g' "$file"
  sed -i '' 's|import .* from '\''./chart-date-adapter.js'\'';|import \{ verifyDateAdapter \} from "../adapters/chart-date-adapter.js";|g' "$file"
  sed -i '' 's|import .* from '\''./data-loader.js'\'';|import \{ loadDataFile, refreshChart \} from "../data-handling/data-loader.js";|g' "$file"
  sed -i '' 's|import .* from '\''./data-exporter.js'\'';|import \{ uploadChart, exportDataToCSV, exportDataToJSON, exportDataToExcel \} from "../data-handling/data-exporter.js";|g' "$file"
  sed -i '' 's|import .* from '\''./chart-helpers.js'\'';|import \{ loadExampleDataForChartType \} from "../adapters/chart-helpers.js";|g' "$file"
  sed -i '' 's|import .* from '\''./dependency-checker.js'\'';|import \{ checkAllDependencies \} from "../utils/dependency-checker.js";|g' "$file"
done

# 修復 adapters 目錄下的檔案
echo "修復 adapters 目錄下的檔案..."
find "${JS_ROOT}/adapters" -name "*.js" | while read file; do
  sed -i '' 's|import .* from '\''./utils.js'\'';|import \{ showError, showSuccess, showLoading, fetchFileData \} from "../utils/utils.js";|g' "$file"
  sed -i '' 's|import .* from '\''./theme-handler.js'\'';|import \{ syncChartThemeWithPageTheme \} from "../utils/theme-handler.js";|g' "$file"
done

# 修復 data-handling 目錄下的檔案
echo "修復 data-handling 目錄下的檔案..."
find "${JS_ROOT}/data-handling" -name "*.js" | while read file; do
  sed -i '' 's|import .* from '\''./utils.js'\'';|import \{ showError, showSuccess, showLoading, fetchFileData \} from "../utils/utils.js";|g' "$file"
  sed -i '' 's|import .* from '\''./state-manager.js'\'';|import \{ getAppState, setStateValue \} from "../core/state-manager.js";|g' "$file"
  sed -i '' 's|import .* from '\''./file-handler.js'\'';|import \{ guessChartTypeFromFilename \} from "../utils/file-handler.js";|g' "$file"
  sed -i '' 's|import .* from '\''./chart-renderer.js'\'';|import \{ createChart \} from "../adapters/chart-renderer.js";|g' "$file"
  sed -i '' 's|import .* from '\''./theme-handler.js'\'';|import \{ syncChartThemeWithPageTheme \} from "../utils/theme-handler.js";|g' "$file"
  sed -i '' 's|import .* from '\''./ui-controller.js'\'';|import \{ updateExampleFileList \} from "../core/ui-controller.js";|g' "$file"
done

# 修復 main.js
echo "修復 main.js..."
sed -i '' 's|import '\''./app-initializer.js'\'';|import "./core/app-initializer.js";|g' "${JS_ROOT}/main.js"
sed -i '' 's|import { checkAllDependencies } from '\''./dependency-checker.js'\'';|import { checkAllDependencies } from "./utils/dependency-checker.js";|g' "${JS_ROOT}/main.js"
sed -i '' 's|export { initPage } from '\''./app-initializer.js'\'';|export { initPage } from "./core/app-initializer.js";|g' "${JS_ROOT}/main.js"
sed -i '' 's|export { loadDataFile, refreshChart } from '\''./data-loader.js'\'';|export { loadDataFile, refreshChart } from "./data-handling/data-loader.js";|g' "${JS_ROOT}/main.js"
sed -i '' 's|export { createOrUpdateChart, updateChartTheme, updateChartData } from '\''./chart-manager.js'\'';|export { createOrUpdateChart, updateChartTheme, updateChartData } from "./core/chart-manager.js";|g' "${JS_ROOT}/main.js"
sed -i '' 's|export { getAppState, setStateValue } from '\''./state-manager.js'\'';|export { getAppState, setStateValue } from "./core/state-manager.js";|g' "${JS_ROOT}/main.js"

echo "修復完成！"
