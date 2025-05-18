/**
 * 範例加載器模組 - 專門用於處理範例檔案的載入和處理
 */
import { showError, showSuccess, showLoading } from '../utils/utils.js';

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
 * 獲取可用的圖表類型
 * @returns {Promise<Object>} - 圖表類型列表
 */
export async function fetchChartTypes() {
    try {
        const response = await fetch('/api/examples/chart-types/');
        if (response.ok) {
            return await response.json();
        } else {
            console.error('獲取圖表類型失敗');
            return { chart_types: {} };
        }
    } catch (error) {
        console.error('獲取圖表類型錯誤：', error);
        return { chart_types: {} };
    }
}

/**
 * 獲取範例檔案內容
 * @param {string} filename - 檔案名稱
 * @returns {Promise<Object>} - 檔案內容
 */
export async function fetchExampleData(filename) {
    try {
        showLoading(true);
        
        const url = `/api/examples/get/?filename=${encodeURIComponent(filename)}`;
        const response = await fetch(url);
        
        if (response.ok) {
            const data = await response.json();
            return data;
        } else {
            // 嘗試讀取錯誤訊息
            let errorMessage = `獲取範例資料失敗: ${response.status} ${response.statusText}`;
            try {
                const errorData = await response.json();
                if (errorData && errorData.detail) {
                    errorMessage = errorData.detail;
                }
            } catch (e) {
                console.warn('無法解析錯誤訊息:', e);
            }
            
            showError(errorMessage);
            return null;
        }
    } catch (error) {
        console.error('獲取範例資料錯誤：', error);
        showError('獲取範例資料時發生錯誤');
        return null;
    } finally {
        showLoading(false);
    }
}
