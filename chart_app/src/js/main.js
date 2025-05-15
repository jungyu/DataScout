import { showError, showSuccess, showLoading, fetchAllDataFiles, fetchFileData } from './utils.js';
import { CHART_TYPE_TO_EXAMPLE_FILE, loadExampleDataForChartType } from './chart-helpers.js';
import { createChart, captureChart } from './chart-renderer.js';
import { uploadChart, exportDataToCSV, exportDataToJSON, exportDataToExcel } from './data-exporter.js';
import { initThemeHandler, syncChartThemeWithPageTheme } from './theme-handler.js';
import { guessChartTypeFromFilename, getExampleFilesForChartType, refreshAvailableFiles } from './file-handler.js';
import { fetchAvailableExamples, fetchChartTypes, fetchExampleData } from './example-loader.js';

/**
 * 應用程式狀態
 */
const appState = {
    myChart: null,
    currentDataFile: null,
    currentDataType: 'json',
    currentChartType: 'radar',  // 預設為雷達圖
    currentChartTheme: 'default',
    availableDataFiles: {},
    dataColumnInfo: null
};

/**
 * 從 URL 查詢參數取得指定值
 * @param {string} name - 參數名稱
 * @returns {string|null} - 參數值，如果不存在則返回 null
 */
function getQueryParam(name) {
    const urlSearchParams = new URLSearchParams(window.location.search);
    return urlSearchParams.get(name);
}

/**
 * 初始化頁面
 */
async function initPage() {
    console.log('初始化圖表應用程式...');
    
    // 初始化主題處理
    initThemeHandler();
    
    // 獲取所有可用的資料檔案
    const files = await fetchAllDataFiles();
    appState.availableDataFiles = files;
    
    // 獲取 UI 元素
    const chartTypeSelect = document.getElementById('chartType');
    const chartThemeSelect = document.getElementById('chartTheme');
    const dataTypeSelect = document.getElementById('dataTypeSelect');
    const dataSourceExample = document.getElementById('dataSourceExample');
    const dataSourceUpload = document.getElementById('dataSourceUpload');
    const exampleFilesContainer = document.getElementById('exampleFilesContainer');
    const uploadSection = document.getElementById('uploadSection');
    
    // 初始化圖表類型選擇器
    if (chartTypeSelect) {
        chartTypeSelect.addEventListener('change', async () => {
            const selectedChartType = chartTypeSelect.value;
            appState.currentChartType = selectedChartType;
            console.log(`圖表類型已變更為: ${selectedChartType}`);
            
            // 如果是使用範例資料，則根據圖表類型自動載入對應範例
            if (dataSourceExample && dataSourceExample.classList.contains('tab-active')) {
                await loadExampleDataForChartType(selectedChartType, appState);
                // 更新範例檔案列表
                updateExampleFileList();
            }
        });
    }
    
    // 初始化資料來源選擇器
    if (dataSourceExample && dataSourceUpload) {
        // 範例資料標籤點擊處理
        dataSourceExample.addEventListener('click', function() {
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
        });
        
        // 自有資料標籤點擊處理
        dataSourceUpload.addEventListener('click', function() {
            // 更新標籤狀態
            dataSourceUpload.classList.add('tab-active');
            dataSourceExample.classList.remove('tab-active');
            
            // 更新顯示區域
            exampleFilesContainer.classList.add('hidden');
            uploadSection.classList.remove('hidden');
            
            // 更新當前數據類型
            appState.currentDataType = dataTypeSelect ? dataTypeSelect.value : 'csv';
        });
    }
    
    // 監聽圖表主題變更
    if (chartThemeSelect) {
        chartThemeSelect.addEventListener('change', () => {
            const selectedTheme = chartThemeSelect.value;
            appState.currentChartTheme = selectedTheme;
            console.log(`主題已變更為: ${selectedTheme}`);
            
            // 如果有現有圖表，則使用新主題重新渲染
            if (appState.myChart && appState.currentDataFile) {
                const fileType = appState.currentDataType || 'json';
                refreshChart(appState.currentDataFile, fileType);
            }
        });
    }
    
    // 監聽資料類型變更
    if (dataTypeSelect) {
        dataTypeSelect.addEventListener('change', () => {
            appState.currentDataType = dataTypeSelect.value;
            console.log(`資料類型已變更為: ${appState.currentDataType}`);
        });
    }
    
    // 初始化匯出按鈕
    initExportButtons();
    
    // 初始化資料摘要
    initDataSummary();
    
    // 初始化上傳功能
    initUploadFeature();
    
    // 載入範例檔案系統
    try {
        // 檢查是否應該重新載入資料檔案（如果之前沒有資料或資料不完整）
        if (!appState.availableDataFiles || !appState.availableDataFiles.json || appState.availableDataFiles.json.length === 0) {
            await refreshAvailableFiles(appState);
        }
        
        // 更新範例檔案列表
        await updateExampleFileList();
        
        // 檢查 URL 是否包含範例參數
        const exampleFilename = getQueryParam('example');
        if (exampleFilename) {
            // 如果有指定範例檔案，則載入該檔案
            console.log(`從 URL 參數載入範例檔案: ${exampleFilename}`);
            try {
                await loadExampleFile(exampleFilename);
                // 確保「範例資料」選項卡被激活
                if (dataSourceExample) {
                    dataSourceExample.click();
                }
            } catch (exampleError) {
                console.error(`載入指定範例檔案 ${exampleFilename} 失敗:`, exampleError);
                showError(`無法載入指定的範例檔案 ${exampleFilename}`);
                // 載入預設圖表（雷達圖範例）
                await loadExampleDataForChartType('radar', appState);
            }
        } else {
            // 載入預設圖表（雷達圖範例）
            await loadExampleDataForChartType('radar', appState);
        }
    } catch (error) {
        console.error('初始化範例檔案系統時發生錯誤：', error);
        
        // 如果加載失敗，顯示錯誤訊息並嘗試使用舊的API方式加載
        showError('載入範例檔案時發生錯誤，嘗試使用備用方式...');
        
        try {
            await loadExampleDataForChartType('radar', appState);
        } catch (backupError) {
            console.error('備用載入方式也失敗:', backupError);
            showError('所有載入方式均失敗，請刷新頁面或聯繫管理員');
        }
    }
    
    console.log('圖表應用程式初始化完成');
}

/**
 * 載入範例檔案
 * @param {string} filename - 檔案名稱
 */
async function loadExampleFile(filename) {
    try {
        showLoading(true);
        
        // 獲取檔案資料（先嘗試新API，失敗則嘗試舊API）
        let data;
        
        try {
            data = await fetchExampleData(filename);
        } catch (error) {
            console.warn('使用新API獲取範例失敗，嘗試舊API:', error);
            data = await fetchFileData(filename, 'json');
        }
        
        if (data) {
            // 獲取目前主題和圖表類型
            const chartTypeElement = document.getElementById('chartType');
            const chartThemeElement = document.getElementById('chartTheme');
            
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
                appState.currentChartType = chartType;
                console.log(`圖表類型已根據檔案名稱自動更新為: ${chartType}`);
            }
            
            const chartTheme = chartThemeElement ? chartThemeElement.value : appState.currentChartTheme;
            
            // 根據頁面主題同步圖表主題
            const effectiveTheme = syncChartThemeWithPageTheme(appState);
            
            // 渲染圖表
            createChart(data, chartType, effectiveTheme, appState);
            
            // 儲存目前檔案和類型
            appState.currentDataFile = filename;
            appState.currentDataType = 'json';
            
            // 更新範例檔案列表中的選中狀態
            updateExampleFileList();
            
            showSuccess(`已載入範例: ${filename}`);
        } else {
            showError('無法載入範例檔案');
        }
    } catch (error) {
        console.error('載入範例檔案錯誤：', error);
        showError('載入範例檔案時發生錯誤');
    } finally {
        showLoading(false);
    }
}

/**
 * 初始化匯出按鈕
 */
function initExportButtons() {
    // 下拉選單切換
    const exportDropdownBtn = document.getElementById('exportDropdownBtn');
    const exportDropdown = document.getElementById('exportDropdown');
    
    if (exportDropdownBtn && exportDropdown) {
        exportDropdownBtn.addEventListener('click', () => {
            exportDropdown.classList.toggle('hidden');
            exportDropdown.classList.toggle('active');
        });
        
        // 點擊其他地方關閉下拉選單
        document.addEventListener('click', (event) => {
            if (!exportDropdownBtn.contains(event.target) && !exportDropdown.contains(event.target)) {
                exportDropdown.classList.add('hidden');
                exportDropdown.classList.remove('active');
            }
        });
    }
    
    // 圖片匯出按鈕
    const exportPngBtn = document.getElementById('exportPng');
    if (exportPngBtn) {
        exportPngBtn.addEventListener('click', () => {
            captureChart('image/png', appState);
            exportDropdown.classList.add('hidden');
        });
    }
    
    const exportWebpBtn = document.getElementById('exportWebp');
    if (exportWebpBtn) {
        exportWebpBtn.addEventListener('click', () => {
            captureChart('image/webp', appState);
            exportDropdown.classList.add('hidden');
        });
    }
    
    // 資料匯出按鈕
    const exportCsvBtn = document.getElementById('exportCsv');
    if (exportCsvBtn) {
        exportCsvBtn.addEventListener('click', () => {
            exportDataToCSV(appState);
            exportDropdown.classList.add('hidden');
        });
    }
    
    const exportJsonBtn = document.getElementById('exportJson');
    if (exportJsonBtn) {
        exportJsonBtn.addEventListener('click', () => {
            exportDataToJSON(appState);
            exportDropdown.classList.add('hidden');
        });
    }
    
    const exportExcelBtn = document.getElementById('exportExcel');
    if (exportExcelBtn) {
        exportExcelBtn.addEventListener('click', () => {
            exportDataToExcel(appState);
            exportDropdown.classList.add('hidden');
        });
    }
    
    // 上傳到雲端按鈕
    const uploadChartBtn = document.getElementById('uploadChart');
    if (uploadChartBtn) {
        uploadChartBtn.addEventListener('click', () => {
            uploadChart(appState);
            exportDropdown.classList.add('hidden');
        });
    }
}

/**
 * 初始化資料摘要功能
 */
function initDataSummary() {
    const showDataSummaryBtn = document.getElementById('showDataSummary');
    const dataInfo = document.getElementById('dataInfo');
    const closeDataInfoBtn = document.getElementById('closeDataInfo');
    
    if (showDataSummaryBtn && dataInfo) {
        showDataSummaryBtn.addEventListener('click', () => {
            dataInfo.classList.remove('hidden');
            updateDataSummary();
        });
    }
    
    if (closeDataInfoBtn && dataInfo) {
        closeDataInfoBtn.addEventListener('click', () => {
            dataInfo.classList.add('hidden');
        });
    }
}

/**
 * 更新資料摘要內容
 */
function updateDataSummary() {
    const dataInfoContent = document.getElementById('dataInfoContent');
    if (!dataInfoContent || !appState.myChart) return;
    
    const chart = appState.myChart;
    const datasets = chart.data.datasets;
    const labels = chart.data.labels;
    
    let summaryHTML = `
        <div class="space-y-2">
            <p><strong>圖表類型:</strong> ${appState.currentChartType}</p>
            <p><strong>資料集數量:</strong> ${datasets.length}</p>
            <p><strong>資料點數量:</strong> ${labels ? labels.length : '未知'}</p>
    `;
    
    // 添加每個資料集的摘要
    if (datasets && datasets.length > 0) {
        summaryHTML += `<div class="mt-2"><strong>資料集:</strong></div>`;
        datasets.forEach((dataset, index) => {
            const data = dataset.data;
            let min = Number.MAX_SAFE_INTEGER;
            let max = Number.MIN_SAFE_INTEGER;
            let sum = 0;
            let count = 0;
            
            // 計算統計資料
            if (Array.isArray(data)) {
                data.forEach(value => {
                    if (typeof value === 'number') {
                        min = Math.min(min, value);
                        max = Math.max(max, value);
                        sum += value;
                        count++;
                    } else if (value && typeof value === 'object' && 'y' in value) {
                        // 處理 {x, y} 格式的資料點
                        min = Math.min(min, value.y);
                        max = Math.max(max, value.y);
                        sum += value.y;
                        count++;
                    }
                });
            }
            
            const avg = count > 0 ? sum / count : 0;
            
            summaryHTML += `
                <div class="ml-2 p-2 mb-2 bg-gray-50 rounded">
                    <p><strong>${dataset.label || `資料集 ${index + 1}`}</strong></p>
                    <p>總點數: ${count}</p>
                    ${count > 0 ? `
                        <p>最小值: ${min.toFixed(2)}</p>
                        <p>最大值: ${max.toFixed(2)}</p>
                        <p>平均值: ${avg.toFixed(2)}</p>
                    ` : ''}
                </div>
            `;
        });
    }
    
    summaryHTML += '</div>';
    dataInfoContent.innerHTML = summaryHTML;
}

/**
 * 更新範例檔案列表
 * @returns {Promise<void>}
 */
async function updateExampleFileList() {
    const exampleFileList = document.getElementById('exampleFileList');
    if (!exampleFileList) return;
    
    // 清空現有列表
    exampleFileList.innerHTML = '';
    
    try {
        // 當前選中的圖表類型
        const currentChartType = appState.currentChartType || 'radar';
        
        // 準備一個加載訊息
        const loadingMsg = document.createElement('p');
        loadingMsg.textContent = '載入範例檔案中...';
        loadingMsg.className = 'text-sm text-gray-500 p-2 text-center';
        exampleFileList.appendChild(loadingMsg);
        
        // 使用新的 API 獲取範例檔案
        const exampleData = await fetchAvailableExamples();
        
        // 清空加載訊息
        exampleFileList.innerHTML = '';
        
        const categorizedFiles = exampleData.categorized || {};
        
        // 如果沒有任何範例檔案
        if (Object.keys(categorizedFiles).length === 0) {
            // 如果API沒有返回分類文件，嘗試舊方式
            if (appState.availableDataFiles && appState.availableDataFiles.json) {
                // 使用舊方式显示
                displayExampleFilesLegacy();
                return;
            }
            
            const noFilesMsg = document.createElement('p');
            noFilesMsg.textContent = '沒有可用的範例檔案';
            noFilesMsg.className = 'text-sm text-gray-500 p-2 text-center';
            exampleFileList.appendChild(noFilesMsg);
            return;
        }
        
        // 僅顯示目前圖表類型的範例檔案
        let currentTypeFiles = categorizedFiles[currentChartType] || [];
        
        if (currentTypeFiles.length > 0) {
            // 添加當前類型標題
            const typeHeading = document.createElement('div');
            typeHeading.className = 'px-3 py-2 text-sm font-bold text-gray-800 bg-gray-100';
            typeHeading.textContent = `${currentChartType.charAt(0).toUpperCase() + currentChartType.slice(1)}型圖表`;
            exampleFileList.appendChild(typeHeading);
            
            // 添加當前類型的範例
            currentTypeFiles.forEach(fileInfo => {
                const fileButton = document.createElement('button');
                fileButton.textContent = fileInfo.display_name;
                fileButton.className = 'w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors';
                fileButton.addEventListener('click', () => loadExampleFile(fileInfo.filename));
                
                // 如果是當前檔案，標記為選中狀態
                if (fileInfo.filename === appState.currentDataFile) {
                    fileButton.classList.add('bg-blue-50', 'text-blue-700', 'font-medium');
                }
                
                exampleFileList.appendChild(fileButton);
            });
        } else {
            // 沒有當前圖表類型的範例檔案
            const noFilesMsg = document.createElement('p');
            noFilesMsg.textContent = `沒有可用的${currentChartType}型範例檔案`;
            noFilesMsg.className = 'text-sm text-gray-500 p-2 text-center';
            exampleFileList.appendChild(noFilesMsg);
        }
        
        // 可以添加一個"所有範例"的按鈕或鏈接
        const viewAllExamples = document.createElement('div');
        viewAllExamples.className = 'text-center p-2 mt-2';
        const viewAllLink = document.createElement('a');
        viewAllLink.href = '/examples';
        viewAllLink.className = 'text-xs text-primary hover:text-primary-focus underline';
        viewAllLink.textContent = '瀏覽所有範例圖表 →';
        viewAllExamples.appendChild(viewAllLink);
        exampleFileList.appendChild(viewAllExamples);
    } catch (error) {
        console.error('更新範例檔案列表錯誤:', error);
        // 顯示錯誤訊息並嘗試退回到舊方式
        try {
            displayExampleFilesLegacy();
        } catch (fallbackError) {
            const errorMsg = document.createElement('p');
            errorMsg.textContent = '載入範例檔案列表時發生錯誤';
            errorMsg.className = 'text-sm text-red-500 p-2 text-center';
            exampleFileList.appendChild(errorMsg);
        }
    }
}

/**
 * 使用舊方式顯示範例檔案列表（備用方法）
 */
function displayExampleFilesLegacy() {
    const exampleFileList = document.getElementById('exampleFileList');
    if (!exampleFileList) return;
    
    // 清空現有列表
    exampleFileList.innerHTML = '';
    
    // 篩選範例 JSON 檔案
    const exampleFiles = appState.availableDataFiles.json || [];
    const exampleJsonFiles = exampleFiles.filter(file => file.includes('example_'));
    
    // 當前選中的圖表類型
    const currentChartType = appState.currentChartType || 'radar';
    
    // 按圖表類型分類範例檔案
    const categorizedFiles = {
        'bar': exampleJsonFiles.filter(file => file.includes('example_bar_')),
        'line': exampleJsonFiles.filter(file => file.includes('example_line_')),
        'pie': exampleJsonFiles.filter(file => file.includes('example_pie_')),
        'doughnut': exampleJsonFiles.filter(file => file.includes('example_doughnut_')),
        'radar': exampleJsonFiles.filter(file => file.includes('example_radar_')),
        'scatter': exampleJsonFiles.filter(file => file.includes('example_scatter_')),
        'bubble': exampleJsonFiles.filter(file => file.includes('example_bubble_')),
        'candlestick': exampleJsonFiles.filter(file => file.includes('example_candlestick_')),
        'mixed': exampleJsonFiles.filter(file => file.includes('example_mixed_'))
    };
    
    // 只顯示目前圖表類型的範例檔案
    if (categorizedFiles[currentChartType] && categorizedFiles[currentChartType].length > 0) {
        // 添加類型標題
        const typeHeading = document.createElement('div');
        typeHeading.className = 'px-3 py-2 text-sm font-bold text-gray-800 bg-gray-100';
        typeHeading.textContent = `${currentChartType.charAt(0).toUpperCase() + currentChartType.slice(1)}型圖表`;
        exampleFileList.appendChild(typeHeading);
        
        // 添加當前類型的範例
        categorizedFiles[currentChartType].forEach(filename => {
            const fileButton = document.createElement('button');
            // 顯示檔案名稱，移除'example_'和'.json'，並將'_'替換為空格
            const displayName = filename
                .replace(`example_${currentChartType}_`, '')
                .replace('.json', '')
                .replace(/_/g, ' ');
            fileButton.textContent = displayName;
            fileButton.className = 'w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors';
            fileButton.addEventListener('click', () => loadExampleFile(filename));
            
            // 如果是當前檔案，標記為選中狀態
            if (filename === appState.currentDataFile) {
                fileButton.classList.add('bg-blue-50', 'text-blue-700', 'font-medium');
            }
            
            exampleFileList.appendChild(fileButton);
        });
    } else {
        // 沒有當前圖表類型的範例檔案
        const noFilesMsg = document.createElement('p');
        noFilesMsg.textContent = `沒有可用的${currentChartType}型範例檔案`;
        noFilesMsg.className = 'text-sm text-gray-500 p-2 text-center';
        exampleFileList.appendChild(noFilesMsg);
    }
    
    // 添加瀏覽所有範例的鏈接
    const viewAllExamples = document.createElement('div');
    viewAllExamples.className = 'text-center p-2 mt-2';
    const viewAllLink = document.createElement('a');
    viewAllLink.href = '/examples';
    viewAllLink.className = 'text-xs text-primary hover:text-primary-focus underline';
    viewAllLink.textContent = '瀏覽所有範例圖表 →';
    viewAllExamples.appendChild(viewAllLink);
    exampleFileList.appendChild(viewAllExamples);
}

/**
 * 初始化檔案上傳功能
 */
function initUploadFeature() {
    const uploadFileBtn = document.getElementById('uploadFileBtn');
    const fileUpload = document.getElementById('fileUpload');
    const dataTypeSelect = document.getElementById('dataTypeSelect');
    
    console.log('初始化上傳功能:', { uploadFileBtn, fileUpload, dataTypeSelect });
    
    if (uploadFileBtn && fileUpload) {
        // 上傳按鈕點擊事件
        uploadFileBtn.addEventListener('click', async (event) => {
            console.log('上傳按鈕被點擊');
            event.preventDefault(); // 防止表單默認提交
            
            if (fileUpload.files.length === 0) {
                showError('請選擇要上傳的檔案');
                return;
            }
            
            const formData = new FormData();
            formData.append('file', fileUpload.files[0]);
            
            // 從資料類型選擇器獲取類型
            const fileType = dataTypeSelect ? dataTypeSelect.value : 'csv';
            formData.append('file_type', fileType);
            
            // 顯示上傳進度
            const uploadProgress = document.getElementById('uploadProgress');
            const uploadStatus = document.getElementById('uploadStatus');
            
            if (uploadProgress) {
                uploadProgress.classList.remove('hidden');
            }
            
            if (uploadStatus) uploadStatus.textContent = '正在上傳...';
            
            try {
                showLoading(true);
                console.log('開始上傳檔案:', fileUpload.files[0].name, '類型:', fileType);
                
                const response = await fetch('/api/upload-file/', {
                    method: 'POST',
                    body: formData
                });
                
                console.log('上傳響應:', response.status, response.statusText);
                
                if (response.ok) {
                    const data = await response.json();
                    console.log('上傳成功，伺服器返回:', data);
                    showSuccess('檔案上傳成功');
                    
                    if (uploadStatus) uploadStatus.textContent = '上傳成功！正在處理數據...';
                    
                    // 獲取所有可用的資料檔案
                    const files = await fetchAllDataFiles();
                    appState.availableDataFiles = files;
                    
                    // 載入上傳的檔案
                    await loadDataFile(data.filename, fileType);
                    
                    // 更新上傳狀態顯示
                    if (uploadStatus) {
                        uploadStatus.textContent = '數據載入完成！';
                        uploadStatus.classList.add('text-success');
                    }
                    
                    // 設定延遲隱藏上傳進度條
                    setTimeout(() => {
                        if (uploadProgress) uploadProgress.classList.add('hidden');
                    }, 3000);
                } else {
                    try {
                        const errorData = await response.json();
                        console.error('上傳失敗:', errorData);
                        const errorMessage = errorData.error || errorData.message || '未知錯誤';
                        showError(`上傳失敗: ${errorMessage}`);
                        
                        if (uploadStatus) {
                            uploadStatus.textContent = `上傳失敗: ${errorMessage}`;
                            uploadStatus.classList.add('text-error');
                        }
                    } catch (jsonError) {
                        console.error('解析錯誤響應失敗:', jsonError);
                        showError(`上傳失敗: HTTP ${response.status}`);
                        
                        if (uploadStatus) {
                            uploadStatus.textContent = `上傳失敗: 伺服器錯誤`;
                            uploadStatus.classList.add('text-error');
                        }
                    }
                    // 保持進度條顯示但不改變其樣式
                }
            } catch (error) {
                console.error('上傳檔案發生異常:', error);
                showError(`上傳檔案時發生錯誤: ${error.message || '網路問題'}`);
                
                if (uploadStatus) {
                    uploadStatus.textContent = `上傳檔案時發生錯誤: ${error.message || '請檢查網路連接'}`;
                    uploadStatus.classList.add('text-error');
                }
                // 不添加 progress-error 類別，因為可能不存在
            } finally {
                showLoading(false);
            }
        });
    }
    
    // JSON 格式範例顯示
    const showJsonFormatBtn = document.getElementById('showJsonFormatBtn');
    const jsonFormatExample = document.getElementById('jsonFormatExample');
    
    if (showJsonFormatBtn && jsonFormatExample) {
        showJsonFormatBtn.addEventListener('click', () => {
            jsonFormatExample.classList.toggle('hidden');
        });
    }
}

/**
 * 載入資料檔案並創建圖表
 * @param {string} filename - 檔案名稱
 * @param {string} type - 檔案類型
 */
async function loadDataFile(filename, type) {
    try {
        showLoading(true);
        
        // 獲取檔案資料
        const data = await fetchFileData(filename, type);
        if (data) {
            // 獲取目前主題和圖表類型
            const chartTypeElement = document.getElementById('chartType');
            const chartThemeElement = document.getElementById('chartTheme');
            
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
                appState.currentChartType = chartType;
                console.log(`圖表類型已根據檔案名稱自動更新為: ${chartType}`);
            }
            
            const chartTheme = chartThemeElement ? chartThemeElement.value : appState.currentChartTheme;
            
            // 根據頁面主題同步圖表主題
            const effectiveTheme = syncChartThemeWithPageTheme(appState);
            
            // 渲染圖表
            createChart(data, chartType, effectiveTheme, appState);
            
            // 儲存目前檔案和類型
            appState.currentDataFile = filename;
            appState.currentDataType = type;
            
            // 更新範例檔案列表中的選中狀態
            updateExampleFileList();
            
            showSuccess(`已載入檔案: ${filename}`);
        } else {
            showError('無法載入資料檔案');
        }
    } catch (error) {
        console.error('載入資料檔案錯誤：', error);
        showError('載入資料檔案時發生錯誤');
    } finally {
        showLoading(false);
    }
}

/**
 * 重新整理圖表
 * @param {string} filename - 檔案名稱
 * @param {string} type - 檔案類型
 */
async function refreshChart(filename, type) {
    try {
        showLoading(true);
        
        // 獲取檔案資料
        const data = await fetchFileData(filename, type);
        if (data) {
            // 獲取目前圖表類型和主題
            const chartType = appState.currentChartType;
            const chartTheme = appState.currentChartTheme;
            
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

// 將部分函數暴露給全域以供其他模組使用
window.updateExampleFileList = updateExampleFileList;
window.loadDataFile = loadDataFile;

// 初始化主題選擇器
function initThemeSelector() {
    const themeOptions = document.querySelectorAll('.theme-option');
    const chartThemeSelect = document.getElementById('chartTheme');
    
    if (themeOptions.length > 0 && chartThemeSelect) {
        themeOptions.forEach(option => {
            option.addEventListener('click', () => {
                const selectedTheme = option.getAttribute('data-theme');
                
                // 更新隱藏的選擇器值
                chartThemeSelect.value = selectedTheme;
                
                // 觸發變更事件
                const changeEvent = new Event('change');
                chartThemeSelect.dispatchEvent(changeEvent);
                
                // 更新顯示狀態
                themeOptions.forEach(opt => opt.classList.remove('active'));
                option.classList.add('active');
                
                // 輔助顯示通知
                showSuccess(`已套用${option.textContent.trim()}主題`);
            });
        });
    }
}

// 當 DOM 內容載入完畢後初始化頁面
document.addEventListener('DOMContentLoaded', () => {
    initPage();
    initThemeSelector();
});
