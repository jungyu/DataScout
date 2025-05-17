#!/bin/zsh
# filepath: /Users/aaron/Projects/DataScout/chart_app/scripts/restructure_js_files.sh
# 重組 JavaScript 檔案結構的腳本

JS_ROOT="/Users/aaron/Projects/DataScout/chart_app/src/js"
CORE_DIR="${JS_ROOT}/core"
ADAPTERS_DIR="${JS_ROOT}/adapters"
DATA_HANDLING_DIR="${JS_ROOT}/data-handling"
UTILS_DIR="${JS_ROOT}/utils"

# 確保所有子目錄存在
mkdir -p "${CORE_DIR}"
mkdir -p "${ADAPTERS_DIR}"
mkdir -p "${DATA_HANDLING_DIR}"
mkdir -p "${UTILS_DIR}"

# 移動核心檔案
echo "移動核心文件..."
[[ -f "${JS_ROOT}/app-initializer.js" ]] && cp "${JS_ROOT}/app-initializer.js" "${CORE_DIR}/" && echo "已移動 app-initializer.js"
[[ -f "${JS_ROOT}/chart-manager.js" ]] && cp "${JS_ROOT}/chart-manager.js" "${CORE_DIR}/" && echo "已移動 chart-manager.js"
[[ -f "${JS_ROOT}/state-manager.js" ]] && cp "${JS_ROOT}/state-manager.js" "${CORE_DIR}/" && echo "已移動 state-manager.js"
[[ -f "${JS_ROOT}/ui-controller.js" ]] && cp "${JS_ROOT}/ui-controller.js" "${CORE_DIR}/" && echo "已移動 ui-controller.js"

# 移動資料處理檔案
echo "移動資料處理文件..."
[[ -f "${JS_ROOT}/data-loader.js" ]] && cp "${JS_ROOT}/data-loader.js" "${DATA_HANDLING_DIR}/" && echo "已移動 data-loader.js"
[[ -f "${JS_ROOT}/data-processor.js" ]] && cp "${JS_ROOT}/data-processor.js" "${DATA_HANDLING_DIR}/" && echo "已移動 data-processor.js"
[[ -f "${JS_ROOT}/data-exporter.js" ]] && cp "${JS_ROOT}/data-exporter.js" "${DATA_HANDLING_DIR}/" && echo "已移動 data-exporter.js"
[[ -f "${JS_ROOT}/example-loader.js" ]] && cp "${JS_ROOT}/example-loader.js" "${DATA_HANDLING_DIR}/" && echo "已移動 example-loader.js"
[[ -f "${JS_ROOT}/example-functions.js" ]] && cp "${JS_ROOT}/example-functions.js" "${DATA_HANDLING_DIR}/" && echo "已移動 example-functions.js"
[[ -f "${JS_ROOT}/example-loader-functions.js" ]] && cp "${JS_ROOT}/example-loader-functions.js" "${DATA_HANDLING_DIR}/" && echo "已移動 example-loader-functions.js"
[[ -f "${JS_ROOT}/example-manager.js" ]] && cp "${JS_ROOT}/example-manager.js" "${DATA_HANDLING_DIR}/" && echo "已移動 example-manager.js"

# 移動適配器檔案
echo "移動適配器文件..."
[[ -f "${JS_ROOT}/chart-date-adapter.js" ]] && cp "${JS_ROOT}/chart-date-adapter.js" "${ADAPTERS_DIR}/" && echo "已移動 chart-date-adapter.js"
[[ -f "${JS_ROOT}/chart-renderer.js" ]] && cp "${JS_ROOT}/chart-renderer.js" "${ADAPTERS_DIR}/" && echo "已移動 chart-renderer.js"
[[ -f "${JS_ROOT}/chart-type-adapters.js" ]] && cp "${JS_ROOT}/chart-type-adapters.js" "${ADAPTERS_DIR}/" && echo "已移動 chart-type-adapters.js"
[[ -f "${JS_ROOT}/chart-fix.js" ]] && cp "${JS_ROOT}/chart-fix.js" "${ADAPTERS_DIR}/" && echo "已移動 chart-fix.js"
[[ -f "${JS_ROOT}/chart-helpers.js" ]] && cp "${JS_ROOT}/chart-helpers.js" "${ADAPTERS_DIR}/" && echo "已移動 chart-helpers.js"
[[ -f "${JS_ROOT}/candlestick-helper.js" ]] && cp "${JS_ROOT}/candlestick-helper.js" "${ADAPTERS_DIR}/" && echo "已移動 candlestick-helper.js"

# 移動工具檔案
echo "移動工具文件..."
[[ -f "${JS_ROOT}/utils.js" ]] && cp "${JS_ROOT}/utils.js" "${UTILS_DIR}/" && echo "已移動 utils.js"
[[ -f "${JS_ROOT}/theme-handler.js" ]] && cp "${JS_ROOT}/theme-handler.js" "${UTILS_DIR}/" && echo "已移動 theme-handler.js"
[[ -f "${JS_ROOT}/file-handler.js" ]] && cp "${JS_ROOT}/file-handler.js" "${UTILS_DIR}/" && echo "已移動 file-handler.js"
[[ -f "${JS_ROOT}/dependency-checker.js" ]] && cp "${JS_ROOT}/dependency-checker.js" "${UTILS_DIR}/" && echo "已移動 dependency-checker.js"
[[ -f "${JS_ROOT}/chart-themes.js" ]] && cp "${JS_ROOT}/chart-themes.js" "${UTILS_DIR}/" && echo "已移動 chart-themes.js"
[[ -f "${JS_ROOT}/json-validator.js" ]] && cp "${JS_ROOT}/json-validator.js" "${UTILS_DIR}/" && echo "已移動 json-validator.js"

echo "所有文件已複製到適當的目錄。請檢查是否需要更新任何引用路徑。"
