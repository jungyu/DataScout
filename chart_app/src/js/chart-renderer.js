/**
 * 圖表渲染器模組 - 專門負責 Chart.js 圖表的創建和更新
 */

import { showError } from './utils.js';

/**
 * 創建或更新圖表
 * @param {Object} data - 圖表資料
 * @param {string} chartType - 圖表類型
 * @param {string} theme - 圖表主題
 * @param {Object} appState - 應用狀態
 */
export function createChart(data, chartType, theme, appState) {
    try {
        // 確保 appState 存在
        if (!appState) {
            console.error('appState 未定義');
            throw new Error('appState is not defined');
        }
        
        const canvas = document.getElementById('chartCanvas');
        if (!canvas) {
            console.error('找不到圖表畫布元素');
            return null;
        }
        
        console.log('開始創建圖表:', chartType, '主題:', theme);
        console.log('資料結構:', data);
        
        // 重要修改：銷毀先前的圖表實例，避免 Canvas 重用錯誤
        if (appState.myChart) {
            console.log('銷毀先前的圖表實例');
            try {
                appState.myChart.destroy();
            } catch (destroyError) {
                console.warn('銷毀先前圖表時出錯:', destroyError);
            }
            appState.myChart = null;
        }
        
        // 確保 canvas 清理完畢
        const ctx = canvas.getContext('2d');
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // 準備圖表配置
        const chartConfig = prepareChartConfig(data, chartType, theme, appState);
        
        // 創建新圖表
        const chart = new Chart(ctx, chartConfig);
        
        // 保存到應用狀態
        appState.myChart = chart;
        
        return chart;
    } catch (error) {
        console.error('創建圖表失敗:', error);
        
        // 錯誤處理: 確保在創建失敗時正確清理
        const canvas = document.getElementById('chartCanvas');
        if (canvas) {
            // 嘗試重設 canvas
            const ctx = canvas.getContext('2d');
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // 創建一個錯誤圖表顯示錯誤訊息
            createErrorChart(canvas, `創建圖表失敗: ${error.message}`);
        }
        
        // 確保舊實例被清理
        if (appState.myChart) {
            try {
                appState.myChart.destroy();
            } catch (e) {
                console.warn('清理舊圖表時出錯:', e);
            }
            appState.myChart = null;
        }
        
        return null;
    }
}

/**
 * 在圖表加載失敗時顯示錯誤信息
 * @param {HTMLCanvasElement} canvas - 畫布元素
 * @param {string} errorMessage - 錯誤訊息
 */
function createErrorChart(canvas, errorMessage) {
    try {
        // 檢查 canvas 是否存在並且可以獲取 context
        if (!canvas || typeof canvas.getContext !== 'function') {
            console.error('無效的 canvas 元素');
            return;
        }
        
        const ctx = canvas.getContext('2d');
        ctx.font = '16px Arial';
        ctx.fillStyle = 'red';
        ctx.textAlign = 'center';
        ctx.fillText('圖表加載失敗', canvas.width / 2, 30);
        
        ctx.font = '14px Arial';
        ctx.fillStyle = 'black';
        
        // 將錯誤訊息拆分為多行
        const maxWidth = canvas.width - 40;
        const words = errorMessage.split(' ');
        let line = '';
        let y = 60;
        
        for (let word of words) {
            const testLine = line + word + ' ';
            const metrics = ctx.measureText(testLine);
            
            if (metrics.width > maxWidth && line !== '') {
                ctx.fillText(line, canvas.width / 2, y);
                line = word + ' ';
                y += 20;
            } else {
                line = testLine;
            }
        }
        
        ctx.fillText(line, canvas.width / 2, y);
        
        // 添加重試按鈕指引
        ctx.fillStyle = 'blue';
        ctx.fillText('請嘗試選擇其他圖表類型或資料來源', canvas.width / 2, y + 40);
    } catch (e) {
        console.error('顯示錯誤信息失敗:', e);
    }
}

/**
 * 準備圖表配置
 * @param {Object} data - 圖表資料
 * @param {string} chartType - 圖表類型
 * @param {string} theme - 圖表主題
 * @param {Object} appState - 應用狀態
 * @returns {Object} 圖表配置
 */
function prepareChartConfig(data, chartType, theme, appState) {
    try {
        console.log('準備圖表配置:', { chartType, theme });
        
        // 處理和驗證圖表資料
        const chartData = processChartData(data, chartType);
        if (!chartData) {
            throw new Error('無法處理圖表資料');
        }
        
        // 根據蠟燭圖、金融圖表等特殊類型進行處理
        let config = {};
        
        switch (chartType) {
            case 'candlestick':
                config = prepareCandlestickConfig(data, theme);
                break;
                
            case 'mixed':
            case 'barLine':
                config = prepareMixedChartConfig(data, theme);
                break;
                
            case 'ohlc':
            case 'ohlcVolume':
            case 'ohlcMaKd':
                config = prepareFinancialChartConfig(data, chartType, theme);
                break;
                
            default:
                // 標準圖表類型
                config = {
                    type: chartType,
                    data: chartData,
                    options: generateChartOptions(chartType, chartData, theme)
                };
                break;
        }
        
        // 如果存在標題，應用標題
        if (data.chartTitle) {
            if (!config.options) config.options = {};
            if (!config.options.plugins) config.options.plugins = {};
            if (!config.options.plugins.title) config.options.plugins.title = {};
            
            config.options.plugins.title.display = true;
            config.options.plugins.title.text = data.chartTitle;
        }
        
        // 如果傳入的資料中有選項，合併這些選項
        if (data.options) {
            config.options = Object.assign({}, config.options || {}, data.options);
        }
        
        // 從資料提取欄位信息
        extractDataColumnInfo(chartData, appState);
        
        // 更新計數
        updateDataPointsCount(chartData, appState);
        
        return config;
    } catch (error) {
        console.error('準備圖表配置時出錯:', error);
        throw new Error(`準備圖表配置失敗: ${error.message}`);
    }
}

/**
 * 處理蠟燭圖配置
 * @param {Object} data - 圖表資料
 * @param {string} theme - 圖表主題
 * @returns {Object} 蠟燭圖配置
 */
function prepareCandlestickConfig(data, theme) {
    try {
        console.log('開始準備蠟燭圖配置', data);
        
        // 驗證資料格式
        if (!data.datasets || !Array.isArray(data.datasets) || data.datasets.length === 0) {
            if (data.data && data.data.datasets) {
                data = data.data; // 使用嵌套的資料結構
                console.log('使用嵌套資料結構', data);
            } else {
                throw new Error('無效的蠟燭圖資料格式');
            }
        }
        
        // 取得第一個數據集
        const dataset = data.datasets[0];
        if (!dataset || !dataset.data || !Array.isArray(dataset.data)) {
            throw new Error('蠟燭圖數據集格式錯誤');
        }
        
        console.log('蠟燭圖數據集：', dataset);
        
        // 確保數據中包含所有必要欄位
        const validData = dataset.data.filter(item => {
            return item && item.t && typeof item.o === 'number' && 
                   typeof item.h === 'number' && typeof item.l === 'number' && 
                   typeof item.c === 'number';
        });
        
        if (validData.length === 0) {
            throw new Error('蠟燭圖沒有有效的資料點');
        }
        
        console.log(`蠟燭圖有效資料點數: ${validData.length}/${dataset.data.length}`);
        
        // 建立蠟燭圖配置
        const config = {
            type: 'candlestick',
            data: {
                datasets: [{
                    label: dataset.label || '蠟燭圖',
                    data: validData.map(item => ({
                        t: new Date(item.t),
                        o: item.o,
                        h: item.h,
                        l: item.l,
                        c: item.c
                    })),
                    color: {
                        up: dataset.color?.up || 'rgba(75, 192, 192, 1)',
                        down: dataset.color?.down || 'rgba(255, 99, 132, 1)',
                        unchanged: dataset.color?.unchanged || 'rgba(201, 203, 207, 1)'
                    }
                }]
            },
            options: data.options || {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: 'day'
                        }
                    },
                    y: {
                        beginAtZero: false
                    }
                },
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                const point = context.raw;
                                return [
                                    `開盤: ${point.o}`,
                                    `最高: ${point.h}`,
                                    `最低: ${point.l}`,
                                    `收盤: ${point.c}`
                                ];
                            }
                        }
                    }
                }
            }
        };
        
        // 應用主題設置
        applyTheme(config.options, theme);
        
        return config;
    } catch (error) {
        console.error('準備蠟燭圖配置時出錯:', error);
        throw new Error(`準備蠟燭圖配置失敗: ${error.message}`);
    }
}

/**
 * 處理混合圖表配置
 * @param {Object} data - 圖表資料
 * @param {string} theme - 圖表主題
 * @returns {Object} 混合圖表配置
 */
function prepareMixedChartConfig(data, theme) {
    try {
        // 驗證資料格式
        if (!data.datasets && data.data && data.data.datasets) {
            data = data.data; // 使用嵌套的資料結構
        }
        
        if (!data.datasets || !Array.isArray(data.datasets)) {
            throw new Error('無效的混合圖表資料格式');
        }
        
        // 為每個數據集指定類型 (如果未指定)
        const datasets = data.datasets.map((dataset, index) => {
            const newDataset = { ...dataset };
            if (!newDataset.type) {
                // 預設第一個數據集為柱狀圖，其餘為線圖
                newDataset.type = index === 0 ? 'bar' : 'line';
            }
            return newDataset;
        });
        
        // 建立混合圖表配置
        const config = {
            type: 'bar', // 基本類型為柱狀圖，但個別數據集可以覆蓋
            data: {
                labels: data.labels || [],
                datasets: datasets
            },
            options: data.options || {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: false
                    }
                },
                plugins: {
                    legend: {
                        position: 'top',
                    }
                }
            }
        };
        
        // 應用主題設置
        applyTheme(config.options, theme);
        
        return config;
    } catch (error) {
        console.error('準備混合圖表配置時出錯:', error);
        throw new Error(`準備混合圖表配置失敗: ${error.message}`);
    }
}

/**
 * 處理金融圖表配置
 * @param {Object} data - 圖表資料
 * @param {string} chartType - 圖表類型
 * @param {string} theme - 圖表主題
 * @returns {Object} 金融圖表配置
 */
function prepareFinancialChartConfig(data, chartType, theme) {
    try {
        // 驗證資料格式
        if (!data.datasets && data.data && data.data.datasets) {
            data = data.data; // 使用嵌套的資料結構
        }
        
        if (!data.datasets || !Array.isArray(data.datasets)) {
            throw new Error('無效的金融圖表資料格式');
        }
        
        // 取得主數據集 (OHLC)
        const mainDataset = data.datasets[0];
        if (!mainDataset || !mainDataset.data || !Array.isArray(mainDataset.data)) {
            throw new Error('金融圖表主數據集格式錯誤');
        }
        
        // 建立基本 OHLC 配置
        const config = {
            type: 'ohlc',
            data: {
                datasets: [{
                    label: mainDataset.label || 'OHLC',
                    data: mainDataset.data.map(item => ({
                        t: new Date(item.t),
                        o: item.o,
                        h: item.h,
                        l: item.l,
                        c: item.c
                    })),
                    color: {
                        up: mainDataset.color?.up || 'rgba(75, 192, 192, 1)',
                        down: mainDataset.color?.down || 'rgba(255, 99, 132, 1)',
                        unchanged: mainDataset.color?.unchanged || 'rgba(201, 203, 207, 1)'
                    }
                }]
            },
            options: data.options || {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: 'day'
                        }
                    },
                    y: {
                        beginAtZero: false
                    }
                },
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                const point = context.raw;
                                return [
                                    `開盤: ${point.o}`,
                                    `最高: ${point.h}`,
                                    `最低: ${point.l}`,
                                    `收盤: ${point.c}`
                                ];
                            }
                        }
                    }
                }
            }
        };
        
        // 根據圖表類型添加額外數據集
        if (chartType === 'ohlcVolume' && data.datasets.length > 1) {
            // 添加成交量數據集
            const volumeDataset = data.datasets[1];
            config.data.datasets.push({
                type: 'bar',
                label: volumeDataset.label || '成交量',
                data: volumeDataset.data,
                backgroundColor: volumeDataset.backgroundColor || 'rgba(54, 162, 235, 0.5)',
                borderColor: volumeDataset.borderColor || 'rgba(54, 162, 235, 1)',
                borderWidth: 1,
                yAxisID: 'volume'
            });
            
            // 添加成交量 Y 軸
            config.options.scales.volume = {
                position: 'right',
                beginAtZero: true,
                grid: {
                    drawOnChartArea: false
                }
            };
        }
        
        // 應用主題設置
        applyTheme(config.options, theme);
        
        return config;
    } catch (error) {
        console.error('準備金融圖表配置時出錯:', error);
        throw new Error(`準備金融圖表配置失敗: ${error.message}`);
    }
}

/**
 * 處理圖表資料，確保符合 Chart.js 格式
 * @param {Object} data - 原始資料
 * @param {string} chartType - 圖表類型
 * @returns {Object} 處理後的資料
 */
function processChartData(data, chartType) {
    // 如果資料已經是標準 Chart.js 格式，直接使用
    if (data.datasets) {
        return data;
    }
    
    // 如果資料在 data 屬性中
    if (data.data && data.data.datasets) {
        return data.data;
    }
    
    // 其他情況: 嘗試從提供的資料中構建 Chart.js 格式
    console.warn('資料格式未符合 Chart.js 標準，嘗試自動適配');
    
    try {
        // 建立基本的資料結構
        const chartData = {
            labels: data.labels || [],
            datasets: []
        };
        
        // 如果有數據陣列，將其轉換為數據集
        if (Array.isArray(data)) {
            chartData.datasets.push({
                label: '數據集1',
                data: data,
                backgroundColor: 'rgba(75, 192, 192, 0.6)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            });
        } 
        // 如果有 datasets 屬性但格式不完全符合
        else if (Array.isArray(data.datasets)) {
            chartData.datasets = data.datasets.map((dataset, index) => {
                return {
                    label: dataset.label || `數據集${index+1}`,
                    data: dataset.data || [],
                    backgroundColor: dataset.backgroundColor || generateColor(index, 'background'),
                    borderColor: dataset.borderColor || generateColor(index, 'border'),
                    borderWidth: dataset.borderWidth || 1
                };
            });
        }
        // 如果有單一數據集
        else if (Array.isArray(data.data)) {
            chartData.datasets.push({
                label: data.label || '數據集',
                data: data.data,
                backgroundColor: data.backgroundColor || 'rgba(75, 192, 192, 0.6)',
                borderColor: data.borderColor || 'rgba(75, 192, 192, 1)',
                borderWidth: data.borderWidth || 1
            });
        }
        
        return chartData;
    } catch (error) {
        console.error('處理圖表資料時發生錯誤:', error);
        return null;
    }
}

/**
 * 生成圖表配置選項
 * @param {string} chartType - 圖表類型
 * @param {Object} data - 圖表資料
 * @param {string} theme - 圖表主題
 * @returns {Object} 圖表配置選項
 */
function generateChartOptions(chartType, data, theme) {
    // 基本配置
    const options = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'top',
                labels: {
                    font: {
                        family: "'Noto Sans TC', sans-serif"
                    }
                }
            },
            title: {
                display: false
            },
            tooltip: {
                callbacks: {}
            }
        }
    };
    
    // 根據圖表類型調整配置
    switch (chartType) {
        case 'line':
            options.scales = {
                y: {
                    beginAtZero: false
                }
            };
            break;
            
        case 'bar':
            options.scales = {
                y: {
                    beginAtZero: true
                }
            };
            break;
            
        case 'pie':
        case 'doughnut':
        case 'polarArea':
            options.plugins.legend.position = 'right';
            break;
            
        case 'radar':
            options.scales = {
                r: {
                    angleLines: {
                        display: true
                    },
                    ticks: {
                        backdropColor: 'transparent'
                    }
                }
            };
            break;
            
        case 'scatter':
        case 'bubble':
            options.scales = {
                x: {
                    type: 'linear',
                    position: 'bottom'
                },
                y: {
                    beginAtZero: false
                }
            };
            break;
    }
    
    // 應用主題設置
    applyTheme(options, theme);
    
    return options;
}

/**
 * 根據索引生成顏色
 * @param {number} index - 顏色索引
 * @param {string} type - 'background' 或 'border'
 * @returns {string} 顏色字串
 */
function generateColor(index, type) {
    // 預設顏色集
    const colors = [
        { bg: 'rgba(75, 192, 192, 0.6)', border: 'rgba(75, 192, 192, 1)' },
        { bg: 'rgba(255, 99, 132, 0.6)', border: 'rgba(255, 99, 132, 1)' },
        { bg: 'rgba(54, 162, 235, 0.6)', border: 'rgba(54, 162, 235, 1)' },
        { bg: 'rgba(255, 206, 86, 0.6)', border: 'rgba(255, 206, 86, 1)' },
        { bg: 'rgba(153, 102, 255, 0.6)', border: 'rgba(153, 102, 255, 1)' },
        { bg: 'rgba(255, 159, 64, 0.6)', border: 'rgba(255, 159, 64, 1)' },
        { bg: 'rgba(199, 199, 199, 0.6)', border: 'rgba(199, 199, 199, 1)' }
    ];
    
    // 使用模數取顏色
    const colorIndex = index % colors.length;
    return type === 'background' ? colors[colorIndex].bg : colors[colorIndex].border;
}

/**
 * 應用主題設置
 * @param {Object} options - 圖表配置選項
 * @param {string} theme - 主題名稱
 */
function applyTheme(options, theme) {
    const themes = {
        default: {
            fontColor: '#666',
            gridColor: 'rgba(0, 0, 0, 0.1)',
            titleColor: '#333'
        },
        light: {
            fontColor: '#555',
            gridColor: 'rgba(0, 0, 0, 0.05)',
            titleColor: '#333'
        },
        dark: {
            fontColor: '#ddd',
            gridColor: 'rgba(255, 255, 255, 0.1)',
            titleColor: '#fff'
        },
        pastel: {
            fontColor: '#6c757d',
            gridColor: 'rgba(188, 223, 245, 0.5)',
            titleColor: '#5b8c85'
        },
        vibrant: {
            fontColor: '#333',
            gridColor: 'rgba(63, 81, 181, 0.2)',
            titleColor: '#ff5722'
        }
    };
    
    // 獲取主題設置 (如果不存在則使用預設)
    const themeSettings = themes[theme] || themes.default;
    
    // 套用主題設置到選項
    if (options.scales) {
        const axisKeys = Object.keys(options.scales);
        axisKeys.forEach(key => {
            if (options.scales[key].grid) {
                options.scales[key].grid.color = themeSettings.gridColor;
            } else {
                options.scales[key].grid = { color: themeSettings.gridColor };
            }
            
            if (options.scales[key].ticks) {
                options.scales[key].ticks.color = themeSettings.fontColor;
            } else {
                options.scales[key].ticks = { color: themeSettings.fontColor };
            }
        });
    }
    
    // 套用到圖例和標題
    if (options.plugins && options.plugins.legend) {
        if (options.plugins.legend.labels) {
            options.plugins.legend.labels.color = themeSettings.fontColor;
        } else {
            options.plugins.legend.labels = { color: themeSettings.fontColor };
        }
    }
    
    if (options.plugins && options.plugins.title) {
        options.plugins.title.color = themeSettings.titleColor;
    }
}

/**
 * 從圖表資料中提取欄位資訊
 * @param {Object} chartData - 圖表資料
 * @param {Object} appState - 應用狀態
 */
function extractDataColumnInfo(chartData, appState) {
    // 檢查 appState 是否存在
    if (!appState) {
        console.warn('應用狀態 (appState) 未定義，無法保存欄位資訊');
        return;
    }

    const columnInfo = {
        labels: chartData.labels || [],
        datasets: []
    };
    
    if (chartData.datasets) {
        chartData.datasets.forEach(dataset => {
            columnInfo.datasets.push({
                label: dataset.label || '未命名數據集',
                dataCount: Array.isArray(dataset.data) ? dataset.data.length : 0,
                dataType: getDataType(dataset.data)
            });
        });
    }
    
    appState.dataColumnInfo = columnInfo;
}

/**
 * 更新資料點計數
 * @param {Object} chartData - 圖表資料
 * @param {Object} appState - 應用狀態
 */
function updateDataPointsCount(chartData, appState) {
    // 檢查 appState 是否存在
    if (!appState) {
        console.warn('應用狀態 (appState) 未定義，無法更新資料點計數');
        return;
    }
    
    let totalPoints = 0;
    let datasetCount = 0;
    
    if (chartData.datasets) {
        datasetCount = chartData.datasets.length;
        
        chartData.datasets.forEach(dataset => {
            if (Array.isArray(dataset.data)) {
                totalPoints += dataset.data.length;
            }
        });
    }
    
    // 保存到 appState.dataStats
    if (!appState.dataStats) {
        appState.dataStats = {};
    }
    appState.dataStats.totalPoints = totalPoints;
    appState.dataStats.datasetCount = datasetCount;
    
    // 更新 DOM 元素
    const totalPointsElement = document.getElementById('totalDataPoints');
    const datasetCountElement = document.getElementById('datasetCount');
    
    if (totalPointsElement) {
        totalPointsElement.textContent = totalPoints.toString();
    }
    
    if (datasetCountElement) {
        datasetCountElement.textContent = datasetCount.toString();
    }
}

/**
 * 取得資料類型
 * @param {Array} data - 資料陣列
 * @returns {string} 資料類型
 */
function getDataType(data) {
    if (!Array.isArray(data) || data.length === 0) {
        return 'unknown';
    }
    
    const firstItem = data[0];
    
    if (typeof firstItem === 'number') {
        return 'number';
    } else if (typeof firstItem === 'string') {
        return 'string';
    } else if (typeof firstItem === 'boolean') {
        return 'boolean';
    } else if (firstItem instanceof Date) {
        return 'date';
    } else if (typeof firstItem === 'object') {
        if (firstItem === null) {
            return 'null';
        }
        
        if (firstItem.hasOwnProperty('x') && firstItem.hasOwnProperty('y')) {
            return 'coordinates';
        }
        
        return 'object';
    }
    
    return 'unknown';
}

/**
 * 將圖表截圖為特定格式的圖片
 * @param {string} type - 圖片格式 ('image/png' 或 'image/webp')
 * @param {Object} appState - 應用狀態
 */
export function captureChart(type, appState) {
    try {
        if (!appState.myChart) {
            showError('沒有可用的圖表可供截圖');
            return;
        }
        
        // 獲取圖表的 base64 圖像
        const img = appState.myChart.toBase64Image(type, 1.0);
        
        // 建立臨時連結進行下載
        const link = document.createElement('a');
        const now = new Date();
        const timestamp = now.toISOString().slice(0, 19).replace(/:/g, '-');
        
        // 設定下載名稱和連結
        link.download = `chart-${timestamp}.${type === 'image/webp' ? 'webp' : 'png'}`;
        link.href = img;
        
        // 手動觸發點擊事件
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        console.log('圖表已導出為圖片');
    } catch (error) {
        console.error('截圖時發生錯誤:', error);
        showError(`無法截圖: ${error.message}`);
    }
}
