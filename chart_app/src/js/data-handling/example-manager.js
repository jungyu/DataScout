/**
 * 範例資料管理模組 
 * 整合了所有與範例資料載入、處理和展示相關的功能
 */

import { showError, showSuccess, showLoading, fetchFileData } from '../utils/utils.js';
import { getAppState, setStateValue } from '../core/state-manager.js';
import { guessChartTypeFromFilename } from '../utils/file-handler.js';
import { createChart } from '../adapters/chart-renderer.js';
import { syncChartThemeWithPageTheme } from '../utils/theme-handler.js';
import { updateExampleFileList } from '../core/ui-controller.js';

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
            console.error('獲取範例檔案列表失敗');
            return { examples: [], categorized: {}, total: 0 };
        }
    } catch (error) {
        console.error('獲取範例檔案列表錯誤：', error);
        return { examples: [], categorized: {}, total: 0 };
    }
}

/**
 * 獲取所有可用的圖表類型
 * @returns {Promise<Array<string>>} - 圖表類型列表
 */
export async function fetchChartTypes() {
    try {
        const response = await fetch('/api/chart-types/');
        if (response.ok) {
            return await response.json();
        } else {
            console.error('獲取圖表類型列表失敗');
            return [];
        }
    } catch (error) {
        console.error('獲取圖表類型錯誤：', error);
        return [];
    }
}

/**
 * 獲取範例資料
 * @param {string} filename - 檔案名稱
 * @returns {Promise<Object>} - 範例資料
 */
export async function fetchExampleData(filename) {
    try {
        // 如果沒有提供檔案名稱，返回空物件
        if (!filename) {
            return null;
        }
        
        const response = await fetch(`/api/examples/data/?filename=${encodeURIComponent(filename)}`);
        if (response.ok) {
            return await response.json();
        } else {
            showError(`無法獲取範例資料：${filename}`);
            return null;
        }
    } catch (error) {
        console.error('獲取範例資料錯誤：', error);
        showError(`獲取範例資料時發生錯誤: ${error.message}`);
        return null;
    }
}

/**
 * 載入範例檔案
 * @param {string} filename - 檔案名稱
 */
export async function loadExampleFile(filename) {
    try {
        showLoading(true);
        
        const appState = getAppState();
        
        // 獲取檔案資料
        const data = await fetchExampleData(filename);
        if (data) {
            // 獲取目前主題和圖表類型
            const chartTypeElement = document.getElementById('chartType');
            
            // 檢測檔案類型以自動選擇適合的圖表類型
            let chartType = chartTypeElement ? chartTypeElement.value : appState.currentChartType;
            
            // 使用輔助函數根據檔案名稱判斷最適合的圖表類型
            const detectedType = guessChartTypeFromFilename(filename);
            if (detectedType) {
                chartType = detectedType;
            }
            
            // 更新圖表類型選擇器（如果圖表類型有變）
            if (chartTypeElement && chartType !== chartTypeElement.value) {
                chartTypeElement.value = chartType;
                setStateValue('currentChartType', chartType);
                console.log(`圖表類型已根據檔案名稱自動更新為: ${chartType}`);
            }
            
            // 根據頁面主題同步圖表主題
            const effectiveTheme = syncChartThemeWithPageTheme(appState);
            
            // 渲染圖表
            createChart(data, chartType, effectiveTheme, appState);
            
            // 儲存目前檔案資訊
            setStateValue('currentDataFile', filename);
            setStateValue('currentDataType', 'json');
            
            showSuccess('成功載入範例檔案');
        } else {
            showError('無法載入範例檔案');
        }
    } catch (error) {
        console.error('載入範例檔案錯誤：', error);
        showError(`載入範例檔案時發生錯誤: ${error.message}`);
    } finally {
        showLoading(false);
    }
}

// 圖表範例資料檔案對應
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
 * 根據圖表類型載入對應的範例資料
 * @param {string} chartType - 圖表類型
 * @param {Object} appState - 應用狀態
 * @returns {Promise<boolean>} - 是否成功載入
 */
export async function loadExampleDataForChartType(chartType, appState = null) {
    try {
        if (!appState) {
            appState = getAppState();
        }
        
        // 根據圖表類型獲取對應的範例檔案
        const exampleFile = CHART_TYPE_TO_EXAMPLE_FILE[chartType] || 'example_line_chart.json';
        
        console.log(`為圖表類型 ${chartType} 載入範例資料: ${exampleFile}`);
        
        // 載入範例檔案
        await loadExampleFile(exampleFile);
        
        // 更新範例檔案列表
        updateExampleFileList();
        
        return true;
    } catch (error) {
        console.error('載入圖表範例資料錯誤：', error);
        showError(`載入範例資料時發生錯誤: ${error.message}`);
        return false;
    }
}

/**
 * 根據圖表類型查找可用的範例資料檔案名稱
 * @param {string} chartType - 圖表類型
 * @param {Array<string>} availableFiles - 可用的檔案列表
 * @returns {string} - 範例資料檔案名稱
 */
export function findExampleDataFileForChartType(chartType, availableFiles) {
    // 防禦性檢查
    if (!chartType) {
        chartType = 'line'; // 如果沒有指定圖表類型，預設使用折線圖
    }
    
    const defaultExample = CHART_TYPE_TO_EXAMPLE_FILE[chartType] || 'example_line_chart.json';
    
    // 如果沒有可用的檔案列表，直接返回預設範例
    if (!availableFiles || !Array.isArray(availableFiles.examples) || availableFiles.examples.length === 0) {
        return defaultExample;
    }
    
    // 從檔案列表中查找符合的範例
    const matchingFiles = availableFiles.examples.filter(file => {
        // 檢查檔案名稱是否包含圖表類型
        const lcFileName = file.toLowerCase();
        const lcChartType = chartType.toLowerCase();
        
        // 檢查檔案名稱是否符合特定模式
        return lcFileName.includes(`_${lcChartType}_`) || 
               lcFileName.includes(`example_${lcChartType}`) || 
               lcFileName.includes(`${lcChartType}_chart`);
    });
    
    // 如果找到符合的檔案，返回第一個
    if (matchingFiles.length > 0) {
        return matchingFiles[0];
    }
    
    // 否則返回預設範例
    return defaultExample;
}
