import { showError, showLoading, fetchFileData } from './utils.js';
import { createChart } from './chart-renderer.js';
import { syncChartThemeWithPageTheme } from './theme-handler.js';

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
export function findExampleDataFileForChartType(chartType, availableFiles) {
    // 防禦性檢查
    if (!chartType) {
        chartType = 'line'; // 如果沒有指定圖表類型，預設使用折線圖
    }
    
    // 確保 availableFiles 是陣列且包含字串
    if (!Array.isArray(availableFiles)) {
        console.warn('availableFiles 不是陣列，使用預設值');
        availableFiles = [];
    }
    
    // 過濾非字串項目
    const validFiles = Array.isArray(availableFiles) ? availableFiles.filter(file => typeof file === 'string') : [];
    
    // 先使用預設對應表查找
    const defaultFile = CHART_TYPE_TO_EXAMPLE_FILE[chartType];
    
    // 如果配置表中有對應的範例檔案，且該檔案確實存在，則使用它
    if (defaultFile && Array.isArray(validFiles) && validFiles.length > 0 && validFiles.some(file => file && typeof file === 'string' && file.includes(defaultFile))) {
        return defaultFile;
    }
    
    // 否則在可用檔案中搜尋符合此圖表類型的檔案
    const typePattern = `example_${chartType}_`;
    const matchingFiles = Array.isArray(validFiles) ? validFiles.filter(file => file && typeof file === 'string' && file.includes(typePattern)) : [];
    
    if (matchingFiles.length > 0) {
        // 找到匹配的檔案，返回第一個
        return matchingFiles[0];
    }
    
    // 如果沒有找到匹配的檔案，則回退到預設值或其他圖表類型
    const fallbackTypes = {
        'butterfly': 'bar',       // 蝴蝶圖回退到柱狀圖
        'polarArea': 'radar',     // 極座標圖回退到雷達圖
        'ohlc': 'candlestick',    // OHLC 回退到蠟燭圖
        'scatter': 'bubble',      // 散點圖回退到氣泡圖
        'sankey': 'bar'           // 桑基圖回退到柱狀圖
    };
    
    // 檢查是否有回退類型
    const fallbackType = fallbackTypes[chartType];
    if (fallbackType) {
        // 嘗試查找回退類型的檔案
        const fallbackPattern = `example_${fallbackType}_`;
        const fallbackFiles = Array.isArray(validFiles) ? validFiles.filter(file => file && typeof file === 'string' && file.includes(fallbackPattern)) : [];
        
        if (fallbackFiles.length > 0) {
            return fallbackFiles[0];
        }
    }
    
    // 最後回退到任何可用的範例檔案
    if (Array.isArray(validFiles) && validFiles.length > 0) {
        // 優先選擇 line 或 bar 類型的範例
        const lineExamples = validFiles.filter(file => file && typeof file === 'string' && file.includes('example_line_'));
        if (lineExamples.length > 0) return lineExamples[0];
        
        const barExamples = validFiles.filter(file => file && typeof file === 'string' && file.includes('example_bar_'));
        if (barExamples.length > 0) return barExamples[0];
        
        // 如果沒有，返回第一個可用的範例
        return Array.isArray(availableFiles) && availableFiles.length > 0 ? availableFiles[0] : 'example_line_chart.json';
    }
    
    // 如果所有嘗試都失敗，返回預設值
    return 'example_line_chart.json';
}

/**
 * 根據圖表類型獲取相應的範例資料檔案名稱
 * @param {string} chartType - 圖表類型
 * @returns {string} - 範例資料檔案名稱
 */
export function getExampleDataFileForChartType(chartType) {
    // 兼容舊版本的簡單實現
    return CHART_TYPE_TO_EXAMPLE_FILE[chartType] || 'example_line_chart.json';
}

/**
 * 從專用API獲取特定圖表類型的範例檔案列表
 * @param {string} chartType - 圖表類型
 * @returns {Promise<Array>} - 範例檔案列表
 */
export async function getExampleFilesFromApi(chartType) {
    try {
        // 嘗試使用新的範例API
        const url = `/api/examples/list/${chartType ? '?chart_type=' + chartType : ''}`;
        const response = await fetch(url);
        
        if (response.ok) {
            const data = await response.json();
            
            // 返回該圖表類型的所有範例檔案
            if (data.categorized && chartType && data.categorized[chartType]) {
                return data.categorized[chartType];
            }
            
            // 如果沒有指定圖表類型，或者該類型沒有範例，返回所有範例
            return data.examples || [];
        }
        
        return [];
    } catch (error) {
        console.warn('從API獲取範例檔案列表失敗:', error);
        return [];
    }
}

/**
 * 載入與圖表類型對應的範例資料
 * @param {string} chartType - 圖表類型
 * @param {object} appState - 應用狀態
 * @returns {Promise<Object>} - 解析後的範例資料
 */
export async function loadExampleDataForChartType(chartType, appState) {
    try {
        showLoading(true);
        
        let filename = null;
        let data = null;
        
        // 嘗試從專門的範例API獲取檔案列表
        const exampleFiles = await getExampleFilesFromApi(chartType);
        
        if (exampleFiles && exampleFiles.length > 0) {
            // 找到對應的範例檔案，使用第一個
            // 檢查 exampleFiles 的結構，它可能是文件名字串陣列或物件陣列
            if (typeof exampleFiles[0] === 'object' && exampleFiles[0].filename) {
                filename = exampleFiles[0].filename;
            } else {
                filename = exampleFiles[0];
            }
            
            console.log(`從API獲取 ${chartType} 類型的範例檔案: ${filename}`);
            
            try {
                // 嘗試使用專用API獲取範例資料
                const url = `/api/examples/get/?filename=${encodeURIComponent(filename)}`;
                const response = await fetch(url);
                
                if (response.ok) {
                    data = await response.json();
                }
            } catch (apiError) {
                console.warn('從專用API獲取範例資料失敗，將回退到一般方法:', apiError);
            }
        }
        
        // 如果從專用API獲取失敗，嘗試使用一般方法
        if (!data) {
            // 回退方式：從可用資料檔案中查找
            let availableFiles = [];
            
            // 確保 availableFiles 是一個陣列
            if (appState.availableDataFiles && appState.availableDataFiles.json) {
                if (Array.isArray(appState.availableDataFiles.json)) {
                    availableFiles = appState.availableDataFiles.json;
                } else if (typeof appState.availableDataFiles.json === 'object') {
                    // 如果是物件，嘗試提取可能的陣列或鍵值
                    const jsonData = appState.availableDataFiles.json;
                    if (jsonData.files && Array.isArray(jsonData.files)) {
                        availableFiles = jsonData.files;
                    } else {
                        // 如果是其他形式的物件，使用物件的鍵作為檔案名
                        availableFiles = Object.keys(jsonData);
                    }
                }
            }
            
            console.log('可用檔案列表:', availableFiles);
            
            // 確保每個檔案項目都是字串
            const validFiles = Array.isArray(availableFiles) ? availableFiles.filter(file => typeof file === 'string') : [];
            const exampleFilesFromGeneral = validFiles.filter(file => file && typeof file === 'string' && file.includes('example_'));
            
            console.log('篩選後的範例檔案:', exampleFilesFromGeneral);
            
            // 智能查找對應的範例檔案
            filename = findExampleDataFileForChartType(chartType, exampleFilesFromGeneral);
            console.log(`為圖表類型 ${chartType} 從一般方法選擇範例檔案: ${filename}`);
            
            data = await fetchFileData(filename, 'json');
        }
        
        if (data) {
            // 獲取目前主題
            const chartThemeElement = document.getElementById('chartTheme');
            const chartTheme = chartThemeElement ? chartThemeElement.value : 'default';
            
            // 根據頁面主題同步圖表主題
            const effectiveTheme = syncChartThemeWithPageTheme(appState);
            
            // 渲染圖表
            createChart(data, chartType, effectiveTheme, appState);
            
            // 顯示圖表區域
            const chartContainer = document.getElementById('chartContainer');
            if (chartContainer) chartContainer.classList.remove('hidden');
            
            // 儲存目前檔案和類型
            appState.currentDataFile = filename;
            appState.currentDataType = 'json';
            
            // 更新範例檔案列表
            const updateExampleFileList = window.updateExampleFileList;
            if (typeof updateExampleFileList === 'function') {
                updateExampleFileList();
            }
            
            return data;
        } else {
            showError('無法載入範例資料');
            return null;
        }
    } catch (error) {
        console.error('載入範例資料錯誤：', error);
        showError('載入範例資料時發生錯誤');
        return null;
    } finally {
        showLoading(false);
    }
}

/**
 * 初始化資料來源開關
 * @param {HTMLElement} toggle - 開關元素
 * @param {HTMLElement} label - 顯示標籤元素
 * @param {HTMLElement} dataTypeContainer - 資料類型容器
 * @param {HTMLElement} uploadSection - 上傳區域
 * @param {HTMLElement} dataSourceContainer - 資料來源容器
 * @param {HTMLElement} dataTypeSelect - 資料類型選擇器
 * @param {object} appState - 應用狀態
 */
export function initDataSourceToggle(toggle, label, dataTypeContainer, uploadSection, dataSourceContainer, dataTypeSelect, appState) {
    if (!toggle) return;
    
    toggle.addEventListener('change', function() {
        if (this.checked) {
            // 開關打開：自行上傳資料
            if (label) label.textContent = '自行上傳資料';
            if (dataSourceContainer) dataSourceContainer.classList.add('hidden');
            if (dataTypeContainer) dataTypeContainer.classList.remove('hidden');
            if (uploadSection) uploadSection.classList.remove('hidden');
            appState.currentDataType = dataTypeSelect ? dataTypeSelect.value : 'csv';
            console.log('已切換到「自行上傳資料」模式');
        } else {
            // 開關關閉：使用範例資料
            if (label) label.textContent = '使用範例資料';
            if (dataSourceContainer) dataSourceContainer.classList.add('hidden');
            if (dataTypeContainer) dataTypeContainer.classList.add('hidden');
            if (uploadSection) uploadSection.classList.add('hidden');
            appState.currentDataType = 'json';
            
            // 載入與目前圖表類型對應的範例資料
            loadExampleDataForChartType(appState.currentChartType || 'line', appState);
            console.log('已切換到「使用範例資料」模式');
        }
    });
}

/**
 * 初始化圖表類型選擇器
 * @param {HTMLElement} selector - 圖表類型選擇器元素
 * @param {HTMLElement} dataSourceToggle - 資料來源開關
 * @param {object} appState - 應用狀態
 */
export function initChartTypeSelector(selector, dataSourceToggle, appState) {
    if (!selector) return;
    
    selector.addEventListener('change', async () => {
        const selectedChartType = selector.value;
        appState.currentChartType = selectedChartType;
        console.log(`圖表類型已變更為: ${selectedChartType}`);
        
        // 如果是使用範例資料（開關關閉），則根據圖表類型自動載入對應範例
        if (dataSourceToggle && !dataSourceToggle.checked) {
            await loadExampleDataForChartType(selectedChartType, appState);
        }
    });
}
