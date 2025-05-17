/**
 * UI 控制模組
 * 處理所有用戶界面交互
 */

import { getAppState, setStateValue } from './state-manager.js';
import { loadExampleDataForChartType } from '../adapters/chart-helpers.js';
import { loadDataFile } from '../data-handling/data-loader.js';
import { captureChart } from '../adapters/chart-renderer.js';
import { uploadChart, exportDataToCSV, exportDataToJSON, exportDataToExcel } from '../data-handling/data-exporter.js';
import { getExampleFilesForChartType, refreshAvailableFiles } from '../utils/file-handler.js';
import { syncChartThemeWithPageTheme } from '../utils/theme-handler.js';
import { showError, showSuccess, showLoading } from '../utils/utils.js';

/**
 * 設定 UI 事件監聽器
 * 為各種 UI 元素註冊事件處理函數
 */
export function setupUIEventListeners() {
    console.log('設定 UI 事件監聽器');
    
    // 獲取 UI 元素
    const chartTypeSelect = document.getElementById('chartType');
    const chartThemeSelect = document.getElementById('chartTheme');
    const dataTypeSelect = document.getElementById('dataTypeSelect');
    const dataSourceExample = document.getElementById('dataSourceExample');
    const dataSourceUpload = document.getElementById('dataSourceUpload');
    const exampleFilesContainer = document.getElementById('exampleFilesContainer');
    const uploadSection = document.getElementById('uploadSection');
    const captureButton = document.getElementById('captureButton');
    const uploadButton = document.getElementById('uploadButton');
    const fileUploadInput = document.getElementById('fileUpload');
    const exportCSVButton = document.getElementById('exportCSV');
    const exportJSONButton = document.getElementById('exportJSON');
    const exportExcelButton = document.getElementById('exportExcel');
    
    // 圖表類型選擇器事件處理
    if (chartTypeSelect) {
        chartTypeSelect.addEventListener('change', handleChartTypeChange);
    }
    
    // 圖表主題選擇器事件處理
    if (chartThemeSelect) {
        chartThemeSelect.addEventListener('change', handleChartThemeChange);
    }

    // 資料類型選擇器事件處理
    if (dataTypeSelect) {
        dataTypeSelect.addEventListener('change', handleDataTypeChange);
    }
    
    // 資料來源切換處理
    if (dataSourceExample && dataSourceUpload) {
        dataSourceExample.addEventListener('click', handleExampleTabClick);
        dataSourceUpload.addEventListener('click', handleUploadTabClick);
    }
    
    // 擷取圖表按鈕事件處理
    if (captureButton) {
        captureButton.addEventListener('click', handleCaptureChart);
    }
    
    // 上傳圖表按鈕事件處理
    if (uploadButton) {
        uploadButton.addEventListener('click', handleUploadChart);
    }
    
    // 檔案上傳事件處理
    if (fileUploadInput) {
        fileUploadInput.addEventListener('change', handleFileUpload);
    }
    
    // 匯出按鈕事件處理
    if (exportCSVButton) {
        exportCSVButton.addEventListener('click', handleExportToCSV);
    }
    
    if (exportJSONButton) {
        exportJSONButton.addEventListener('click', handleExportToJSON);
    }
    
    if (exportExcelButton) {
        exportExcelButton.addEventListener('click', handleExportToExcel);
    }
    
    console.log('UI 事件監聽器設定完成');
}

/**
 * 更新範例檔案列表
 */
export function updateExampleFileList() {
    const appState = getAppState();
    const chartType = appState.currentChartType;
    const exampleFilesContainer = document.getElementById('exampleFilesContainer');
    const exampleFiles = getExampleFilesForChartType(chartType, appState.availableDataFiles);
    
    if (!exampleFilesContainer || !exampleFiles || exampleFiles.length === 0) {
        console.log('沒有可用的範例檔案或容器');
        return;
    }
    
    // 清除目前內容
    exampleFilesContainer.innerHTML = '';
    
    // 建立標題
    const title = document.createElement('h3');
    title.className = 'text-lg font-medium mb-2';
    title.textContent = `${chartType.charAt(0).toUpperCase() + chartType.slice(1)} 圖表範例`;
    exampleFilesContainer.appendChild(title);
    
    // 建立檔案列表
    const list = document.createElement('ul');
    list.className = 'space-y-2';
    
    // 添加所有範例檔案
    exampleFiles.forEach(file => {
        const item = document.createElement('li');
        const link = document.createElement('a');
        link.className = 'text-blue-600 hover:text-blue-800 hover:underline cursor-pointer';
        link.textContent = file.replace(/\.(json|csv|excel)$/, '');
        link.dataset.filename = file;
        
        // 獲取檔案類型
        let fileType = 'json';  // 預設為 JSON
        if (file.endsWith('.csv')) {
            fileType = 'csv';
        } else if (file.endsWith('.xlsx') || file.endsWith('.xls')) {
            fileType = 'excel';
        }
        
        link.dataset.type = fileType;
        
        // 添加點擊事件
        link.addEventListener('click', function() {
            loadDataFile(this.dataset.filename, this.dataset.type);
        });
        
        item.appendChild(link);
        list.appendChild(item);
    });
    
    exampleFilesContainer.appendChild(list);
    console.log(`已更新範例檔案列表，共 ${exampleFiles.length} 個檔案`);
}

/**
 * 處理圖表類型變更
 */
async function handleChartTypeChange() {
    const chartTypeSelect = document.getElementById('chartType');
    const selectedChartType = chartTypeSelect.value;
    const appState = getAppState();
    
    setStateValue('currentChartType', selectedChartType);
    console.log(`圖表類型已變更為: ${selectedChartType}`);
    
    // 如果是使用範例資料，則根據圖表類型自動載入對應範例
    const dataSourceExample = document.getElementById('dataSourceExample');
    if (dataSourceExample && dataSourceExample.classList.contains('tab-active')) {
        await loadExampleDataForChartType(selectedChartType, appState);
        // 更新範例檔案列表
        updateExampleFileList();
    }
}

/**
 * 處理圖表主題變更
 */
function handleChartThemeChange() {
    const chartThemeSelect = document.getElementById('chartTheme');
    const selectedTheme = chartThemeSelect.value;
    const appState = getAppState();
    
    setStateValue('currentChartTheme', selectedTheme);
    console.log(`圖表主題已變更為: ${selectedTheme}`);
    
    // 若已加載數據，立即更新圖表主題
    if (appState.currentDataFile) {
        const effectiveTheme = syncChartThemeWithPageTheme(appState);
        
        import('./chart-manager.js').then(module => {
            module.updateChartTheme(effectiveTheme);
        });
    }
}

/**
 * 處理資料類型變更
 */
function handleDataTypeChange() {
    const dataTypeSelect = document.getElementById('dataTypeSelect');
    const selectedDataType = dataTypeSelect.value;
    
    setStateValue('currentDataType', selectedDataType);
    console.log(`資料類型已變更為: ${selectedDataType}`);
}

/**
 * 處理範例資料標籤點擊
 */
function handleExampleTabClick() {
    const dataSourceExample = document.getElementById('dataSourceExample');
    const dataSourceUpload = document.getElementById('dataSourceUpload');
    const exampleFilesContainer = document.getElementById('exampleFilesContainer');
    const uploadSection = document.getElementById('uploadSection');
    const appState = getAppState();
    
    // 更新標籤狀態
    dataSourceExample.classList.add('tab-active');
    dataSourceUpload.classList.remove('tab-active');
    
    // 更新顯示區域
    exampleFilesContainer.classList.remove('hidden');
    uploadSection.classList.add('hidden');
    
    // 載入範例資料
    loadExampleDataForChartType(appState.currentChartType, appState);
    // 更新範例檔案列表
    updateExampleFileList();
}

/**
 * 處理上傳資料標籤點擊
 */
function handleUploadTabClick() {
    const dataSourceExample = document.getElementById('dataSourceExample');
    const dataSourceUpload = document.getElementById('dataSourceUpload');
    const exampleFilesContainer = document.getElementById('exampleFilesContainer');
    const uploadSection = document.getElementById('uploadSection');
    
    // 更新標籤狀態
    dataSourceExample.classList.remove('tab-active');
    dataSourceUpload.classList.add('tab-active');
    
    // 更新顯示區域
    exampleFilesContainer.classList.add('hidden');
    uploadSection.classList.remove('hidden');
    
    // 刷新可用檔案列表
    refreshAvailableFiles();
}

/**
 * 處理擷取圖表
 */
function handleCaptureChart() {
    const appState = getAppState();
    
    if (appState.myChart) {
        try {
            captureChart(appState.myChart);
            showSuccess('圖表已擷取並開始下載');
        } catch (error) {
            console.error('擷取圖表時發生錯誤:', error);
            showError(`無法擷取圖表: ${error.message}`);
        }
    } else {
        showError('沒有圖表可擷取');
    }
}

/**
 * 處理上傳圖表
 */
function handleUploadChart() {
    const appState = getAppState();
    
    if (appState.myChart) {
        showLoading(true);
        try {
            uploadChart(appState.myChart)
                .then(result => {
                    showSuccess('圖表已成功上傳');
                })
                .catch(error => {
                    showError(`上傳圖表時發生錯誤: ${error.message}`);
                })
                .finally(() => {
                    showLoading(false);
                });
        } catch (error) {
            console.error('上傳圖表時發生錯誤:', error);
            showError(`無法上傳圖表: ${error.message}`);
            showLoading(false);
        }
    } else {
        showError('沒有圖表可上傳');
    }
}

/**
 * 處理檔案上傳
 */
function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) {
        return;
    }
    
    const appState = getAppState();
    const fileType = document.getElementById('dataTypeSelect').value || appState.currentDataType;
    
    // 建立 FormData 物件
    const formData = new FormData();
    formData.append('file', file);
    formData.append('type', fileType);
    
    showLoading(true);
    
    // 傳送檔案到伺服器
    fetch('/api/upload/', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(data.detail || '上傳失敗');
            });
        }
        return response.json();
    })
    .then(data => {
        showSuccess(`檔案上傳成功: ${file.name}`);
        console.log('檔案上傳成功:', data);
        
        // 載入上傳的檔案
        if (data.filename) {
            loadDataFile(data.filename, fileType);
        }
        
        // 刷新可用檔案列表
        refreshAvailableFiles();
    })
    .catch(error => {
        console.error('上傳檔案時發生錯誤:', error);
        showError(`上傳檔案時發生錯誤: ${error.message}`);
    })
    .finally(() => {
        showLoading(false);
        // 重置檔案選擇器，允許再次上傳相同檔案
        event.target.value = '';
    });
}

/**
 * 處理匯出為 CSV
 */
function handleExportToCSV() {
    try {
        const appState = getAppState();
        exportDataToCSV(appState.myChart, `chart-data-export-${Date.now()}.csv`);
    } catch (error) {
        console.error('匯出 CSV 時發生錯誤:', error);
        showError(`匯出為 CSV 檔案時發生錯誤: ${error.message}`);
    }
}

/**
 * 處理匯出為 JSON
 */
function handleExportToJSON() {
    try {
        const appState = getAppState();
        exportDataToJSON(appState.myChart, `chart-data-export-${Date.now()}.json`);
    } catch (error) {
        console.error('匯出 JSON 時發生錯誤:', error);
        showError(`匯出為 JSON 檔案時發生錯誤: ${error.message}`);
    }
}

/**
 * 處理匯出為 Excel
 */
function handleExportToExcel() {
    try {
        const appState = getAppState();
        exportDataToExcel(appState.myChart, `chart-data-export-${Date.now()}.xlsx`);
    } catch (error) {
        console.error('匯出 Excel 時發生錯誤:', error);
        showError(`匯出為 Excel 檔案時發生錯誤: ${error.message}`);
    }
}
