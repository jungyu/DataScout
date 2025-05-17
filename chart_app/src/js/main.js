import { showError, showSuccess, showLoading, showChartMessage, hideChartMessage, fetchAllDataFiles, fetchFileData } from './utils.js';
import { CHART_TYPE_TO_EXAMPLE_FILE, loadExampleDataForChartType } from './chart-helpers.js';
import { createChart, captureChart } from './chart-renderer.js';
import { uploadChart, exportDataToCSV, exportDataToJSON, exportDataToExcel } from './data-exporter.js';
import { initThemeHandler, syncChartThemeWithPageTheme } from './theme-handler.js';
import { guessChartTypeFromFilename, getExampleFilesForChartType, refreshAvailableFiles } from './file-handler.js';
import { fetchAvailableExamples, fetchChartTypes, fetchExampleData } from './example-loader.js';
import { verifyDateAdapter } from './chart-date-adapter.js';

/**
 * 應用程式狀態
 */
// 初始化時顯示啟動訊息，確認程式碼正確載入
console.log('初始化 chart_app - ' + new Date().toISOString());
window.chartAppLoaded = true;

const appState = {
    myChart: null,
    currentDataFile: null,
    currentDataType: 'json',
    currentChartType: 'radar',  // 預設為雷達圖
    currentChartTheme: 'default',
    availableDataFiles: {},
    dataColumnInfo: null,
    dataStats: {
        totalPoints: 0,
        datasetCount: 0
    }
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
    
    // 顯示圖表提示訊息
    showChartMessage();
    
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
            console.log('成功使用新API獲取範例資料:', filename);
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
            
            console.log('建立新圖表:', {
                chartType,
                effectiveTheme,
                dataLength: data.datasets ? data.datasets.length : data.data?.datasets?.length || '未知'
            });
            
            // 檢查資料結構，修正不符合標準的資料格式
            const chartData = ensureValidChartData(data, chartType);
            
            // 渲染圖表
            try {
                // 隱藏提示訊息，準備顯示圖表
                hideChartMessage();
                
                const chartResult = createChart(chartData, chartType, effectiveTheme, appState);
                if (!chartResult) {
                    console.error('圖表創建失敗，無返回值');
                    showError('圖表渲染失敗');
                    // 如果圖表渲染失敗，顯示提示訊息
                    showChartMessage();
                }
            } catch (chartError) {
                console.error('圖表渲染錯誤：', chartError);
                showError(`圖表渲染錯誤: ${chartError.message}`);
                // 如果圖表渲染錯誤，顯示提示訊息
                showChartMessage();
            }
            
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
 * 確保圖表數據結構有效
 * @param {object} data - 圖表數據
 * @param {string} chartType - 圖表類型
 * @returns {object} - 處理過的圖表數據
 */
function ensureValidChartData(data, chartType) {
    try {
        console.log(`處理${chartType}類型的圖表數據`, data);
        
        // 開始處理圖表數據前記錄這一步，方便後續排查
        console.log('數據處理開始，圖表類型:', chartType);
        
        // 確保基本結構存在
        if (!data) {
            console.warn('圖表數據為空，創建基本結構');
            data = {
                datasets: [],
                labels: []
            };
        }
        
        // 特殊處理蠟燭圖和OHLC數據
        if ((chartType === 'candlestick' || chartType === 'ohlc') && data.datasets) {
            console.log(`處理${chartType}金融圖表特殊結構數據`);
            
            // 金融圖表數據格式化
            data.datasets.forEach(dataset => {
                // 確保數據點格式正確
                if (dataset.data && Array.isArray(dataset.data)) {
                    dataset.data = dataset.data.map(point => {
                        // 安全地解析時間值
                        let timeValue;
                        try {
                            const rawTime = point.t || point.time || point.x || point.date;
                            
                            if (rawTime instanceof Date) {
                                timeValue = rawTime;
                            } else if (typeof rawTime === 'string') {
                                // 嘗試多種日期格式解析
                                if (rawTime.match(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/)) {
                                    // ISO 格式
                                    timeValue = new Date(rawTime);
                                } else if (rawTime.match(/^\d{4}-\d{2}-\d{2}$/)) {
                                    // YYYY-MM-DD 格式 - 使用UTC避免時區問題
                                    const [year, month, day] = rawTime.split('-').map(Number);
                                    timeValue = new Date(Date.UTC(year, month - 1, day));
                                } else if (rawTime.match(/^\d+$/)) {
                                    // 純數字（時間戳）
                                    timeValue = new Date(parseInt(rawTime));
                                } else {
                                    // 其他格式嘗試標準解析
                                    timeValue = new Date(rawTime);
                                }
                                
                                // 驗證是否為有效日期
                                if (isNaN(timeValue.getTime())) {
                                    console.warn('無效的日期字符串，使用當前日期', rawTime);
                                    timeValue = new Date();
                                }
                            } else if (typeof rawTime === 'number') {
                                // 處理日期時間戳 (毫秒)
                                timeValue = new Date(rawTime);
                            } else {
                                // 如果沒有有效的時間欄位，使用當前時間
                                console.warn('無法識別的時間格式，將使用當前時間');
                                timeValue = new Date();
                            }
                        } catch (dateError) {
                            console.error('解析時間值時出錯:', dateError, '對應數據點:', point);
                            // 發生錯誤時使用當前時間
                            timeValue = new Date();
                        }
                        
                        // 統一數據格式 - 確保t, o, h, l, c 屬性存在並是數字類型
                        return {
                            t: timeValue,
                            o: Number(point.o || point.open || point.y || 0),
                            h: Number(point.h || point.high || point.y || 0),
                            l: Number(point.l || point.low || point.y || 0),
                            c: Number(point.c || point.close || point.y || 0)
                        };
                    });
                    
                    // 確保數據按時間排序
                    dataset.data.sort((a, b) => a.t - b.t);
                }
                
                // 設置適當的色彩
                if (!dataset.color) {
                    dataset.color = {
                        up: 'rgba(75, 192, 75, 1)',
                        down: 'rgba(255, 99, 132, 1)',
                        unchanged: 'rgba(160, 160, 160, 1)'
                    };
                }
            });
            
            console.log(`${chartType}數據處理完成:`, data);
        } 
        // 特殊處理極坐標圖數據
        else if (chartType === 'polarArea' && data) {
            console.log('處理極坐標圖特殊結構數據');
            
            // 確保有標籤
            if (!data.labels || !Array.isArray(data.labels) || data.labels.length === 0) {
                console.warn('極坐標圖缺少標籤，生成預設標籤');
                data.labels = ['項目 1', '項目 2', '項目 3', '項目 4', '項目 5'];
            }
            
            // 確保有數據集
            if (!data.datasets || !Array.isArray(data.datasets) || data.datasets.length === 0) {
                console.warn('極坐標圖缺少數據集，生成預設數據集');
                data.datasets = [{
                    label: '數據系列',
                    data: [10, 20, 30, 40, 50],
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.6)',
                        'rgba(54, 162, 235, 0.6)',
                        'rgba(255, 206, 86, 0.6)',
                        'rgba(75, 192, 192, 0.6)',
                        'rgba(153, 102, 255, 0.6)'
                    ]
                }];
            } 
            // 如果數據集存在但缺少背景色
            else if (data.datasets[0] && !data.datasets[0].backgroundColor) {
                console.warn('極坐標圖數據集缺少背景色，添加預設顏色');
                const defaultColors = [
                    'rgba(255, 99, 132, 0.6)',
                    'rgba(54, 162, 235, 0.6)',
                    'rgba(255, 206, 86, 0.6)',
                    'rgba(75, 192, 192, 0.6)',
                    'rgba(153, 102, 255, 0.6)'
                ];
                
                // 如果是單個數據集但需要多個顏色
                if (!Array.isArray(data.datasets[0].backgroundColor)) {
                    // 創建足夠長度的顏色數組
                    const colors = [];
                    for (let i = 0; i < data.datasets[0].data.length; i++) {
                        colors.push(defaultColors[i % defaultColors.length]);
                    }
                    data.datasets[0].backgroundColor = colors;
                }
            }
            
            console.log('極坐標圖數據處理完成:', data);
        }
        
        // 確保數據集和標籤存在
        if (!data.datasets && !data.data) {
            console.warn('數據缺少 datasets 屬性，創建空數據集');
            data.datasets = [];
        }
        
        console.log('數據處理完成，結果:', data);
        return data;
    } catch (error) {
        console.error('處理圖表數據時發生錯誤:', error);
        // 返回一個最小可用的數據結構
        return {
            datasets: [],
            labels: []
        };
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
    const exportPngBtn = document.getElementById('exportPngBtn') || document.getElementById('exportPng');
    if (exportPngBtn) {
        exportPngBtn.addEventListener('click', () => {
            captureChart('image/png', appState);
            if (exportDropdown) exportDropdown.classList.add('hidden');
        });
    }
    
    const exportWebpBtn = document.getElementById('exportWebpBtn') || document.getElementById('exportWebp');
    if (exportWebpBtn) {
        exportWebpBtn.addEventListener('click', () => {
            captureChart('image/webp', appState);
            if (exportDropdown) exportDropdown.classList.add('hidden');
        });
    }
    
    // 資料匯出按鈕
    const exportCsvBtn = document.getElementById('exportCsvBtn') || document.getElementById('exportCsv');
    if (exportCsvBtn) {
        exportCsvBtn.addEventListener('click', () => {
            exportDataToCSV(appState);
            if (exportDropdown) exportDropdown.classList.add('hidden');
        });
    }
    
    const exportJsonBtn = document.getElementById('exportJsonBtn') || document.getElementById('exportJson');
    if (exportJsonBtn) {
        exportJsonBtn.addEventListener('click', () => {
            exportDataToJSON(appState);
            if (exportDropdown) exportDropdown.classList.add('hidden');
        });
    }
    
    const exportExcelBtn = document.getElementById('exportExcelBtn') || document.getElementById('exportExcel');
    if (exportExcelBtn) {
        exportExcelBtn.addEventListener('click', () => {
            exportDataToExcel(appState);
            if (exportDropdown) exportDropdown.classList.add('hidden');
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
        
        // 檢查並預設 categorized 屬性
        if (!exampleData || typeof exampleData !== 'object') {
            throw new Error('範例資料格式無效');
        }
        
        const categorizedFiles = exampleData.categorized || {};
        
        // 如果沒有任何範例檔案
        if (Object.keys(categorizedFiles).length === 0) {
            // 如果API沒有返回分類文件，嘗試使用原始資料
            if (exampleData.examples && exampleData.examples.length > 0) {
                // 如果 API 沒返回分類資料但有原始資料，手動分類
                const manualCategorized = {};
                exampleData.examples.forEach(example => {
                    const type = example.chart_type || 'unknown';
                    if (!manualCategorized[type]) {
                        manualCategorized[type] = [];
                    }
                    manualCategorized[type].push(example);
                });
                
                // 使用手動分類的檔案
                displayCategorizedExamples(manualCategorized, currentChartType, exampleFileList);
                return;
            }
            
            // 如果API返回的數據無效，嘗試舊方式
            if (appState.availableDataFiles && appState.availableDataFiles.json) {
                // 使用舊方式顯示
                displayExampleFilesLegacy();
                return;
            }
            
            // 真的沒有檔案可顯示
            const noFilesMsg = document.createElement('p');
            noFilesMsg.textContent = '沒有可用的範例檔案';
            noFilesMsg.className = 'text-sm text-gray-500 p-2 text-center';
            exampleFileList.appendChild(noFilesMsg);
            return;
        }
        
        // 顯示分類後的檔案
        displayCategorizedExamples(categorizedFiles, currentChartType, exampleFileList);
        
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
 * 顯示分類的範例檔案
 * @param {Object} categorizedFiles - 分類的檔案列表
 * @param {string} currentChartType - 目前的圖表類型
 * @param {HTMLElement} container - 要顯示檔案的容器
 */
function displayCategorizedExamples(categorizedFiles, currentChartType, container) {
    // 僅顯示目前圖表類型的範例檔案
    let currentTypeFiles = categorizedFiles[currentChartType] || [];
    
    if (currentTypeFiles.length > 0) {
        // 添加當前類型標題
        const typeHeading = document.createElement('div');
        typeHeading.className = 'px-3 py-2 text-sm font-bold text-gray-800 bg-gray-100';
        typeHeading.textContent = `${currentChartType.charAt(0).toUpperCase() + currentChartType.slice(1)}型圖表`;
        container.appendChild(typeHeading);
        
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
            
            container.appendChild(fileButton);
        });
    } else {
        // 沒有當前圖表類型的範例檔案
        const noFilesMsg = document.createElement('p');
        noFilesMsg.textContent = `沒有可用的${currentChartType}型範例檔案`;
        noFilesMsg.className = 'text-sm text-gray-500 p-2 text-center';
        container.appendChild(noFilesMsg);
    }
    
    // 可以添加一個"所有範例"的按鈕或鏈接
    const viewAllExamples = document.createElement('div');
    viewAllExamples.className = 'text-center p-2 mt-2';
    const viewAllLink = document.createElement('a');
    viewAllLink.href = '/examples';
    viewAllLink.className = 'text-xs text-primary hover:text-primary-focus underline';
    viewAllLink.textContent = '瀏覽所有範例圖表 →';
    viewAllExamples.appendChild(viewAllLink);
    container.appendChild(viewAllExamples);
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
                    
                    // 修正檔案路徑處理
                    const filename = data.filename || data.file_path;
                    
                    // 修正：確保使用正確的檔案類型和處理邏輯
                    try {
                        console.log(`正在載入上傳的檔案: ${filename}, 類型: ${fileType}`);
                        await loadDataFile(filename, fileType);
                        
                        if (uploadStatus) {
                            uploadStatus.textContent = '數據載入完成！';
                            uploadStatus.classList.add('text-success');
                        }
                    } catch (loadError) {
                        console.error('載入上傳檔案時發生錯誤:', loadError);
                        showError(`載入檔案失敗: ${loadError.message}`);
                        
                        if (uploadStatus) {
                            uploadStatus.textContent = `載入失敗: ${loadError.message}`;
                            uploadStatus.classList.add('text-error');
                        }
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
                }
            } catch (error) {
                console.error('上傳檔案發生異常:', error);
                showError(`上傳檔案時發生錯誤: ${error.message || '網路問題'}`);
                
                if (uploadStatus) {
                    uploadStatus.textContent = `上傳檔案時發生錯誤: ${error.message || '請檢查網路連接'}`;
                    uploadStatus.classList.add('text-error');
                }
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
        
        // 獲取檔案路徑的規範化處理
        let filepath = filename;
        
        // 如果是上傳的檔案，需要加上上傳目錄前綴
        if (!filename.includes('/')) {
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
        
        // 獲取目前主題和圖表類型
        const chartTypeElement = document.getElementById('chartType');
        const chartThemeElement = document.getElementById('chartTheme');
        
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
    // 確保圖表容器可見
    const chartContainer = document.getElementById('chartContainer');
    if (chartContainer) {
        chartContainer.style.display = 'block';
    }
    
    // 初始化應用
    initPage();
    initThemeSelector();
    
    // 初始化測試按鈕
    const testChartsButton = document.getElementById('testCharts');
    if (testChartsButton) {
        testChartsButton.addEventListener('click', () => {
            const canvas = document.getElementById('chartCanvas');
            if (canvas) {
                console.log('圖表測試功能已移除');
                showSuccess('測試功能已移至測試目錄');
            } else {
                console.error('找不到圖表畫布元素');
                showError('無法啟動測試模式：找不到圖表畫布');
            }
        });
    }
    
    // 添加視窗大小變化監聽
    window.addEventListener('resize', () => {
        if (appState.myChart) {
            appState.myChart.resize();
        }
    });
});

// 添加以下檢查代碼來確保蠟燭圖插件正確加載

// 檢查 Chart.js 是否正確載入
if (typeof Chart === 'undefined') {
    console.error('Chart.js 未正確載入，蠟燭圖將無法顯示');
}

// 檢查是否有蠟燭圖擴展
if (Chart && !Chart.controllers.candlestick) {
    console.error('Chart.js 蠟燭圖擴展未正確載入，請確保已引入 chartjs-chart-financial.js');
}

// 檢查是否有OHLC圖擴展
if (Chart && !Chart.controllers.ohlc) {
    console.error('Chart.js OHLC圖擴展未正確載入，請確保已引入 chartjs-chart-financial.js');
}

// 檢查是否有桑基圖擴展
if (Chart && !Chart.controllers.sankey) {
    console.error('Chart.js 桑基圖擴展未正確載入，請確保已引入 chartjs-chart-sankey.js');
}

// 確認可用的圖表類型
if (Chart) {
    console.log('可用圖表類型:', Object.keys(Chart.controllers || {}));
}
