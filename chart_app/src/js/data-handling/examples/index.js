/**
 * 範例模組索引 - 整合所有範例相關功能並優化結構
 * 文件路徑: /Users/aaron/Projects/DataScout/chart_app/src/js/data-handling/examples/index.js
 */

// 從原有檔案導入所有需要的函數
import { showError, showSuccess, showLoading, fetchFileData } from '../../utils/utils.js';
import { getAppState, setStateValue } from '../../core/state-manager.js';
import { guessChartTypeFromFilename } from '../../utils/file-handler.js';
import { createChart } from '../../adapters/chart-renderer.js';
import { syncChartThemeWithPageTheme } from '../../utils/theme-handler.js';
import { updateExampleFileList } from '../../core/ui-controller.js';

/**
 * 圖表範例資料檔案對應
 * 定義各圖表類型對應的範例檔案名稱
 */
export const CHART_TYPE_TO_EXAMPLE_FILE = {
    'line': 'example_line_chart.json',
    'bar': 'example_bar_chart.json',
    'pie': 'example_pie_chart.json', 
    'radar': 'example_radar_chart.json',
    'doughnut': 'example_doughnut_chart.json',
    'scatter': 'example_scatter_stock_risk_return.json',
    'bubble': 'example_bubble_market_analysis.json',
    'candlestick': 'example_candlestick_gold_twd.json',
    'mixed': 'example_mixed_sp500_price_volume.json',
    'sankey': 'example_sankey_energy_flow.json',
    'butterfly': 'example_butterfly_population_pyramid.json'
};

/**
 * 獲取所有可用的範例檔案
 * @param {string} chartType - 可選，圖表類型，用於過濾範例
 * @returns {Promise<Object>} - 範例檔案列表
 */
export async function fetchAvailableExamples(chartType = null) {
    try {
        let url = '/api/examples/list/';
        if (chartType) {
            url += `?chart_type=${chartType}`;
        }
        
        const response = await fetch(url);
        if (response.ok) {
            return await response.json();
        } else {
            console.error('獲取範例檔案列表失敗，狀態碼:', response.status);
            // 如果 API 失敗，使用預設的範例檔案列表
            return useDefaultExampleFiles();
        }
    } catch (error) {
        console.error('獲取範例檔案列表時發生錯誤:', error);
        // 如果發生錯誤，使用預設的範例檔案列表
        return useDefaultExampleFiles();
    }
}

/**
 * 獲取默認的範例檔案列表
 * 當 API 請求失敗時使用
 * @returns {Object} - 範例檔案列表
 */
function useDefaultExampleFiles() {
    // 返回一些默認的預設範例檔案名稱
    const examples = [
        "example_line_chart.json",
        "example_bar_chart.json",
        "example_pie_chart.json",
        "example_doughnut_chart.json",
        "example_radar_investment_risk.json",
        "example_scatter_chart.json",
        "example_bubble_chart.json",
        "example_mixed_chart.json",
        "example_candlestick_chart.json"
    ];
    
    // 創建一個分類後的默認範例資料結構
    const categorized = {
        "line": ["example_line_chart.json"],
        "bar": ["example_bar_chart.json"],
        "pie": ["example_pie_chart.json"],
        "doughnut": ["example_doughnut_chart.json"],
        "radar": ["example_radar_investment_risk.json"],
        "scatter": ["example_scatter_chart.json"],
        "bubble": ["example_bubble_chart.json"],
        "mixed": ["example_mixed_chart.json"],
        "candlestick": ["example_candlestick_chart.json"]
    };
    
    console.log('使用預設範例檔案列表:', examples.length, '個文件');
    return { examples, categorized, total: examples.length };
}

/**
 * 根據圖表類型查找可用的範例資料檔案名稱
 * @param {string} chartType - 圖表類型
 * @param {Array<string>} availableFiles - 可用的檔案列表
 * @returns {string} - 範例資料檔案名稱
 */
export function findExampleDataFileForChartType(chartType, availableFiles) {
    if (!chartType) {
        chartType = 'line'; // 如果沒有指定圖表類型，預設使用折線圖
    }
    
    const defaultFile = CHART_TYPE_TO_EXAMPLE_FILE[chartType];
    
    // 如果沒有提供可用文件列表，則直接返回默認文件
    if (!availableFiles || !Array.isArray(availableFiles) || availableFiles.length === 0) {
        return defaultFile;
    }
    
    // 首先嘗試尋找完全匹配的範例文件
    const exactMatch = availableFiles.find(file => file === defaultFile);
    if (exactMatch) {
        return exactMatch;
    }
    
    // 如果沒有完全匹配，則嘗試尋找包含圖表類型名稱的文件
    const partialMatch = availableFiles.find(file => 
        file.includes(`_${chartType}_`) || 
        file.includes(`_${chartType}.`) || 
        file.startsWith(`${chartType}_`)
    );
    
    if (partialMatch) {
        return partialMatch;
    }
    
    // 如果仍然沒有找到匹配的文件，則返回默認文件
    return defaultFile;
}

/**
 * 載入特定圖表類型的範例資料
 * @param {string} chartType - 圖表類型
 * @returns {Promise<boolean>} - 是否成功載入
 */
export async function loadExampleDataForChartType(chartType) {
    showLoading(true);
    
    try {
        const appState = getAppState();
        
        // 獲取所有可用的範例文件
        const exampleFiles = await fetchAvailableExamples(chartType);
        const availableFiles = exampleFiles.examples || [];
        
        // 根據圖表類型找到對應的範例文件
        const exampleFile = CHART_TYPE_TO_EXAMPLE_FILE[chartType] || 'example_line_chart.json';
        
        // 設置應用狀態
        appState.currentChartType = chartType;
        appState.currentDataFile = exampleFile;
        
        // 載入範例資料
        const data = await fetchFileData(`static/examples/${exampleFile}`, 'json');
        if (data) {
            // 獲取當前主題
            const theme = appState.currentChartTheme || 'light';
            
            // 創建圖表
            createChart(data, chartType, theme, appState);
            syncChartThemeWithPageTheme(appState);
            showSuccess(`已載入 ${chartType} 圖表範例資料`);
            return true;
        } else {
            showError('無法載入範例資料');
            return false;
        }
    } catch (error) {
        console.error('載入範例資料時發生錯誤:', error);
        showError(`載入範例資料失敗: ${error.message}`);
        return false;
    } finally {
        showLoading(false);
    }
}

/**
 * 載入指定的範例檔案
 * @param {string} filename - 範例檔案名稱
 * @param {string} chartType - 圖表類型
 * @returns {Promise<boolean>} - 是否成功載入
 */
export async function loadExampleFile(filename, chartType) {
    showLoading(true);
    
    try {
        const appState = getAppState();
        
        // 設置應用狀態
        appState.currentChartType = chartType;
        appState.currentDataFile = filename;
        
        // 載入範例資料
        const data = await fetchFileData(`static/examples/${filename}`, 'json');
        if (data) {
            // 獲取當前主題
            const theme = appState.currentChartTheme || 'light';
            
            // 創建圖表
            createChart(data, chartType, theme, appState);
            syncChartThemeWithPageTheme(appState);
            showSuccess(`已載入範例資料: ${filename}`);
            return true;
        } else {
            showError('無法載入範例資料');
            return false;
        }
    } catch (error) {
        console.error('載入範例資料時發生錯誤:', error);
        showError(`載入範例資料失敗: ${error.message}`);
        return false;
    } finally {
        showLoading(false);
    }
}

/**
 * 更新可用的範例文件列表
 * @param {string} chartType - 圖表類型，用於過濾
 * @returns {Promise<void>}
 */
export async function refreshExamplesList(chartType = null) {
    try {
        const examples = await fetchAvailableExamples(chartType);
        updateExampleFileList(examples.examples || []);
    } catch (error) {
        console.error('更新範例列表時發生錯誤:', error);
        showError('無法更新範例檔案列表');
    }
}

// 導出所有來自原有檔案的函數，保持向後兼容
export * from './example-functions.js';

// 提供一個初始化函數
export function initializeExampleSystem() {
    console.log('初始化範例系統...');
    refreshExamplesList();
    return true;
}
