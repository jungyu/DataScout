/**
 * 資料載入模組
 * 處理所有與資料載入相關的功能
 */

import { fetchFileData, showError, showSuccess, showLoading } from '../utils/utils.js';
import { getAppState } from '../core/state-manager.js';
import { guessChartTypeFromFilename } from '../utils/file-handler.js';
import { syncChartThemeWithPageTheme } from '../utils/theme-handler.js';
import { createChart } from '../adapters/chart-renderer.js';

/**
 * 確保資料格式符合圖表要求
 * @param {Object} data - 原始資料
 * @param {string} chartType - 圖表類型
 * @returns {Object} 處理後的資料
 */
export function ensureValidChartData(data, chartType) {
    // 如果已經是有效格式，直接返回
    if (data && data.datasets && Array.isArray(data.datasets)) {
        console.log('資料已經是有效圖表格式');
        return data;
    }
    
    console.log('正在轉換資料為有效圖表格式');
    
    // 如果是物件陣列，轉換為有效的圖表資料格式
    if (Array.isArray(data)) {
        try {
            const labels = Object.keys(data[0] || {}).filter(key => key !== 'label' && key !== 'color');
            
            // 創建資料集
            const datasets = [];
            data.forEach(item => {
                const dataset = {
                    label: item.label || '未命名',
                    data: []
                };
                
                // 設定顏色（如果有提供）
                if (item.color) {
                    dataset.backgroundColor = item.color;
                    dataset.borderColor = item.color;
                }
                
                // 添加資料點
                labels.forEach(label => {
                    dataset.data.push(item[label]);
                });
                
                datasets.push(dataset);
            });
            
            return {
                labels,
                datasets
            };
        } catch (error) {
            console.error('轉換資料格式時發生錯誤:', error);
            throw new Error(`無法處理資料格式: ${error.message}`);
        }
    }
    
    // 針對無法自動處理的資料，拋出錯誤
    throw new Error('不支援的資料格式');
}

/**
 * 載入資料檔案
 * @param {string} filename - 檔案名稱
 * @param {string} type - 檔案類型
 * @returns {Promise<boolean>} - 是否成功載入
 */
export async function loadDataFile(filename, type) {
    try {
        if (!filename) {
            throw new Error('未提供檔案名稱');
        }
        
        showLoading(true);
        console.log(`開始載入檔案: ${filename}, 類型: ${type}`);
        
        // 處理檔案路徑
        let filepath = filename;
        if (!filename.includes('/')) {
            // 根據檔案類型確定路徑
            if (type === 'csv') {
                filepath = `examples/csv/${filename}`;
            } else if (type === 'json') {
                filepath = `examples/json/${filename}`;
            } else if (type === 'excel') {
                filepath = `examples/excel/${filename}`;
            }
        } else if (filename.includes('uploads_')) {
            // 處理上傳的檔案
            if (type === 'csv') {
                filepath = `uploads/csv/${filename}`;
            } else if (type === 'json') {
                filepath = `uploads/json/${filename}`;
            } else if (type === 'excel') {
                filepath = `uploads/excel/${filename}`;
            }
        }
        
        console.log(`準備載入檔案，路徑: ${filepath}, 類型: ${type}`);
        
        // 獲取檔案資料
        const data = await fetchFileData(filepath, type);
        
        if (!data) {
            throw new Error(`無法獲取檔案內容: ${filepath}`);
        }
        
        console.log('成功獲取檔案資料，準備渲染圖表');
        
        const appState = getAppState();
        
        // 獲取目前主題和圖表類型
        const chartTypeElement = document.getElementById('chartType');
        
        // 檢測檔案類型以自動選擇適合的圖表類型
        let chartType = chartTypeElement ? chartTypeElement.value : appState.currentChartType;
        
        // 使用輔助函數根據檔案名稱判斷最適合的圖表類型
        const detectedType = guessChartTypeFromFilename(filename);
        if (detectedType) {
            chartType = detectedType;
            console.log(`根據檔案名稱檢測到圖表類型: ${detectedType}`);
        }
        
        // 更新圖表類型選擇器（如果圖表類型有變）
        if (chartTypeElement && chartType !== chartTypeElement.value) {
            chartTypeElement.value = chartType;
            appState.currentChartType = chartType;
            console.log(`圖表類型已自動更新為: ${chartType}`);
        }
        
        // 根據頁面主題同步圖表主題
        const effectiveTheme = syncChartThemeWithPageTheme(appState);
        
        // 處理資料格式
        const chartData = ensureValidChartData(data, chartType);
        
        // 渲染圖表
        console.log(`開始渲染圖表, 類型: ${chartType}, 主題: ${effectiveTheme}`);
        const chart = createChart(chartData, chartType, effectiveTheme, appState);
        
        if (chart) {
            console.log('圖表渲染成功');
        } else {
            console.warn('圖表可能未成功渲染');
        }
        
        // 儲存目前檔案和類型
        appState.currentDataFile = filename;
        appState.currentDataType = type;
        
        showSuccess(`已成功載入檔案: ${filename}`);
        return true;
    } catch (error) {
        console.error('載入資料檔案錯誤：', error);
        showError(`載入資料檔案時發生錯誤: ${error.message}`);
        return false;
    } finally {
        showLoading(false);
    }
}

/**
 * 重新整理圖表
 * @param {string} filename - 檔案名稱
 * @param {string} type - 檔案類型
 */
export async function refreshChart(filename, type) {
    try {
        showLoading(true);
        
        const appState = getAppState();
        
        // 獲取檔案資料
        const data = await fetchFileData(filename, type);
        if (data) {
            // 獲取目前圖表類型和主題
            const chartType = appState.currentChartType;
            
            // 根據頁面主題同步圖表主題
            const effectiveTheme = syncChartThemeWithPageTheme(appState);
            
            // 渲染圖表
            createChart(data, chartType, effectiveTheme, appState);
            showSuccess('圖表已重新整理');
        } else {
            showError('無法重新整理圖表');
        }
    } catch (error) {
        console.error('重新整理圖表錯誤：', error);
        showError('重新整理圖表時發生錯誤');
    } finally {
        showLoading(false);
    }
}
