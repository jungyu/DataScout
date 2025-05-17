/**
 * 應用程式初始化模組
 * 負責應用程式啟動和初始設定
 */

import { showChartMessage, fetchAllDataFiles } from '../utils/utils.js';
import { initThemeHandler } from '../utils/theme-handler.js';
import { getAppState, initializeAppState } from './state-manager.js';
import { setupUIEventListeners } from './ui-controller.js';
import { verifyDateAdapter } from '../adapters/chart-date-adapter.js';

/**
 * 從 URL 查詢參數取得指定值
 * @param {string} name - 參數名稱
 * @returns {string|null} - 參數值，如果不存在則返回 null
 */
export function getQueryParam(name) {
    const urlSearchParams = new URLSearchParams(window.location.search);
    return urlSearchParams.get(name);
}

/**
 * 初始化頁面
 */
export async function initPage() {
    console.log('初始化圖表應用程式...');
    
    // 初始化應用程式狀態
    initializeAppState();
    const appState = getAppState();
    
    // 初始化主題處理
    initThemeHandler();
    
    // 顯示圖表提示訊息
    showChartMessage();
    
    // 獲取所有可用的資料檔案
    try {
        const files = await fetchAllDataFiles();
        appState.availableDataFiles = files;
    } catch (error) {
        console.error('獲取可用資料檔案時發生錯誤:', error);
    }

    // 設定 UI 事件監聽器
    setupUIEventListeners();

    // 驗證日期轉接器是否可用
    verifyDateAdapter();
    
    console.log('應用程式初始化完成');
    
    // 自動處理 URL 參數
    handleUrlParameters();
}

/**
 * 處理 URL 參數
 * 例如，處理預設載入的檔案和圖表類型
 */
function handleUrlParameters() {
    const fileParam = getQueryParam('file');
    const typeParam = getQueryParam('type');
    const chartTypeParam = getQueryParam('chart');
    
    if (fileParam) {
        console.log(`從 URL 參數檢測到檔案: ${fileParam}`);
        
        const appState = getAppState();
        appState.currentDataFile = fileParam;
        
        // 如果有指定檔案類型，則設定
        if (typeParam) {
            appState.currentDataType = typeParam;
        }
        
        // 如果有指定圖表類型，則設定
        if (chartTypeParam) {
            appState.currentChartType = chartTypeParam;
            const chartTypeSelect = document.getElementById('chartType');
            if (chartTypeSelect) {
                chartTypeSelect.value = chartTypeParam;
            }
        }
        
        // 載入來自 URL 參數的檔案
        // 延遲執行以確保頁面完全載入
        setTimeout(() => {
            import('../data-handling/data-loader.js').then(module => {
                module.loadDataFile(fileParam, appState.currentDataType);
            });
        }, 500);
    }
}

// 當頁面載入完成時初始化應用程式
document.addEventListener('DOMContentLoaded', initPage);
