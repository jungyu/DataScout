/**
 * 圖表管理模組
 * 處理圖表的創建、更新和管理
 * 整合了 chart-helpers.js 的功能
 */

import { createChart, captureChart } from '../adapters/chart-renderer.js';
import { getAppState, updateDataStats, setStateValue } from './state-manager.js';
import { showError, showLoading, fetchFileData, showSuccess } from '../utils/utils.js';
import { syncChartThemeWithPageTheme } from '../utils/theme-handler.js';
import { ChartTypeAdapter } from '../adapters/chart-type-adapters.js';
import { guessChartTypeFromFilename } from '../utils/file-handler.js';

/**
 * 創建或更新圖表
 * @param {Object} data - 圖表數據
 * @param {string} chartType - 圖表類型
 * @param {string} theme - 圖表主題
 * @returns {Object} - 建立的圖表物件
 */
export function createOrUpdateChart(data, chartType, theme) {
    try {
        showLoading(true);
        
        const appState = getAppState();
        
        // 如果未提供特定參數，使用全局狀態中的值
        chartType = chartType || appState.currentChartType;
        theme = theme || syncChartThemeWithPageTheme(appState);
        
        // 創建新圖表
        const chart = createChart(data, chartType, theme, appState);
        
        // 更新數據統計
        updateDataStats(data);
        
        console.log(`已創建/更新圖表，類型: ${chartType}, 主題: ${theme}`);
        return chart;
    } catch (error) {
        console.error('創建/更新圖表時發生錯誤:', error);
        showError(`無法創建/更新圖表: ${error.message}`);
        return null;
    } finally {
        showLoading(false);
    }
}

/**
 * 更新圖表主題
 * @param {string} theme - 新的主題
 * @returns {boolean} - 是否成功更新
 */
export function updateChartTheme(theme) {
    try {
        const appState = getAppState();
        if (!appState.myChart) {
            console.warn('無法更新圖表主題: 圖表不存在');
            return false;
        }
        
        // 獲取目前圖表設定
        const chartType = appState.currentChartType;
        const chartData = appState.myChart.data;
        
        // 更新圖表
        createChart(chartData, chartType, theme, appState);
        
        console.log(`圖表主題已更新為 ${theme}`);
        return true;
    } catch (error) {
        console.error('更新圖表主題時發生錯誤:', error);
        showError(`無法更新圖表主題: ${error.message}`);
        return false;
    }
}

/**
 * 更新圖表數據
 * @param {Object} newData - 新的圖表數據
 * @returns {boolean} - 是否成功更新
 */
export function updateChartData(newData) {
    try {
        const appState = getAppState();
        if (!appState.myChart) {
            console.warn('無法更新圖表數據: 圖表不存在');
            return false;
        }
        
        // 取得目前圖表設定
        const chartType = appState.currentChartType;
        const theme = syncChartThemeWithPageTheme(appState);
        
        // 更新圖表
        createChart(newData, chartType, theme, appState);
        
        // 更新數據統計
        updateDataStats(newData);
        
        console.log('圖表數據已更新');
        return true;
    } catch (error) {
        console.error('更新圖表數據時發生錯誤:', error);
        showError(`無法更新圖表數據: ${error.message}`);
        return false;
    }
}

/**
 * 清除當前圖表
 * @returns {boolean} - 是否成功清除
 */
export function clearChart() {
    try {
        const appState = getAppState();
        if (appState.myChart) {
            appState.myChart.destroy();
            appState.myChart = null;
            
            // 清除圖表容器
            const chartContainer = document.getElementById('chartContainer');
            if (chartContainer) {
                const canvas = document.createElement('canvas');
                canvas.id = 'chartCanvas';
                chartContainer.innerHTML = '';
                chartContainer.appendChild(canvas);
            }
            
            console.log('圖表已清除');
            return true;
        }
        return false;
    } catch (error) {
        console.error('清除圖表時發生錯誤:', error);
        return false;
    }
}

/**
 * 獲取圖表數據統計資訊
 * @returns {Object} - 數據統計資訊
 */
export function getChartDataStatistics() {
    try {
        const appState = getAppState();
        if (!appState.myChart) {
            return {
                totalPoints: 0,
                datasetCount: 0,
                hasData: false
            };
        }
        
        const chartData = appState.myChart.data;
        let totalPoints = 0;
        let datasetCount = 0;
        
        if (chartData && chartData.datasets) {
            datasetCount = chartData.datasets.length;
            chartData.datasets.forEach(dataset => {
                if (dataset.data && Array.isArray(dataset.data)) {
                    totalPoints += dataset.data.length;
                }
            });
        }
        
        return {
            totalPoints,
            datasetCount,
            hasData: totalPoints > 0
        };
    } catch (error) {
        console.error('獲取圖表統計資訊時發生錯誤:', error);
        return {
            totalPoints: 0,
            datasetCount: 0,
            hasData: false,
            error: error.message
        };
    }
}

/**
 * 獲取特定圖表類型的配置
 * @param {string} chartType - 圖表類型
 * @returns {Object} - 圖表配置
 */
export function getChartConfig(chartType) {
    // 使用適配器模式獲取適當的配置
    const adapter = ChartTypeAdapter.getAdapter(chartType);
    return adapter.getChartConfig();
}

/**
 * 驗證並轉換圖表數據
 * @param {Object} data - 原始數據
 * @param {string} chartType - 圖表類型
 * @returns {Object} - 處理後的數據
 */
export function processChartData(data, chartType) {
    const adapter = ChartTypeAdapter.getAdapter(chartType);
    
    if (!adapter.validateData(data)) {
        console.warn(`資料格式不符合 ${chartType} 圖表要求，嘗試自動修復`);
    }
    
    return adapter.transformData(data);
}

/**
 * 匯出圖表為圖像
 * @param {string} format - 圖像格式，如 'png', 'jpeg'
 * @returns {Promise<string>} - 圖像資料 URL
 */
export async function exportChartAsImage(format = 'png') {
    const appState = getAppState();
    if (!appState.myChart) {
        throw new Error('沒有可用的圖表');
    }
    
    try {
        const imageURL = await captureChart(appState.myChart, format);
        return imageURL;
    } catch (error) {
        console.error('匯出圖表為圖像時發生錯誤:', error);
        throw new Error(`無法匯出圖表: ${error.message}`);
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
 * 根據圖表類型查找可用的範例資料檔案名稱
 * @param {string} chartType - 圖表類型
 * @param {Array<string>} availableFiles - 可用的檔案列表
 * @returns {string} - 範例資料檔案名稱
 */
export function findExampleFileForChartType(chartType, availableFiles) {
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
