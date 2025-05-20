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
// 選擇性導出 UI 控制器，避免命名衝突
import { 
    setupUIEventListeners, 
    updateExampleFileList 
} from './core/ui-controller.js';
export { 
    setupUIEventListeners, 
    updateExampleFileList 
};

// 選擇性導出 chart-manager.js 中的函數，避免命名衝突
import { 
    createOrUpdateChart, 
    updateChartTheme, 
    updateChartData 
} from './core/chart-manager.js'; 
export { 
    createOrUpdateChart, 
    updateChartTheme, 
    updateChartData 
};

// 重新導出資料處理相關模組
export * from './data-handling/data-loader.js';
export * from './data-handling/data-processor.js';
export * from './data-handling/data-exporter.js';

// 選擇性導出範例模組 - 使用明確命名避免混淆
import { 
    fetchAvailableExamples, 
    loadExampleDataForChartType as loadExampleFromExampleModule 
} from './data-handling/examples/index.js';
export { 
    fetchAvailableExamples, 
    loadExampleFromExampleModule   // 重命名為更明確的名稱
};

// 重新導出轉接器模組
export * from './adapters/chart-type-adapters.js';
export * from './adapters/chart-renderer.js';
export * from './adapters/chart-date-adapter.js';
export * from './adapters/chart-fix.js';
export * from './adapters/candlestick-helper.js';

// 導入 chart-helpers.js 中的所有函數 - 使用明確命名避免混淆
import { 
    CHART_TYPE_TO_EXAMPLE_FILE, 
    findExampleDataFileForChartType,
    getExampleDataFileForChartType, 
    getExampleFilesFromApi, 
    initChartTypeSelector, 
    initDataSourceToggle, 
    loadExampleDataForChartType as loadExampleFromHelperModule
} from './adapters/chart-helpers.js';
export { 
    CHART_TYPE_TO_EXAMPLE_FILE as CHART_HELPER_EXAMPLE_FILE_MAP, 
    findExampleDataFileForChartType,
    getExampleDataFileForChartType, 
    getExampleFilesFromApi, 
    initChartTypeSelector, 
    initDataSourceToggle, 
    loadExampleFromHelperModule    // 同樣重命名為更明確的名稱
};

// 導出主入口
export * from './main.js';
