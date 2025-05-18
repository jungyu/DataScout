/**
 * DataScout Chart App 模組索引
 * 提供集中的模組導出，便於導入
 */

// 重新導出工具模組 (需要先導入，避免被其他模組覆寫同名函數)
export * from './utils/chart-themes.js';
export * from './utils/utils.js';
export * from './utils/theme-handler.js';
export * from './utils/dependency-checker.js';
export * from './utils/file-handler.js';
export * from './utils/json-validator.js';

// 重新導出核心模組
export * from './core/app-initializer.js';
export * from './core/state-manager.js';
export * from './core/ui-controller.js';
export * from './core/chart-manager.js'; 

// 重新導出資料處理相關模組
export * from './data-handling/data-loader.js';
export * from './data-handling/data-processor.js';
export * from './data-handling/data-exporter.js';
// 導出重組後的範例模組
export * from './data-handling/examples/index.js';

// 重新導出轉接器模組
export * from './adapters/chart-type-adapters.js';
export * from './adapters/chart-renderer.js';
export * from './adapters/chart-date-adapter.js';
export * from './adapters/chart-fix.js';
export * from './adapters/candlestick-helper.js';
// 選擇性匯入 chart-helpers.js 中的函數，避免命名衝突
import { showChartLegend, createChartTooltip } from './adapters/chart-helpers.js';
export { showChartLegend, createChartTooltip };

// 導出主入口
export * from './main.js';
