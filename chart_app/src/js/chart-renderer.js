/**
 * 圖表渲染器模組 - 專責圖表的創建和更新
 */

import { showError } from './utils.js';
import { 
    validateCandlestickData, 
    normalizeCandlestickData, 
    detectTimeUnit 
} from './candlestick-helper.js';

/**
 * 創建或更新圖表
 * @param {Object} data - 圖表資料
 * @param {string} chartType - 圖表類型
 * @param {string} theme - 圖表主題
 * @param {Object} appState - 應用狀態
 */
export function createChart(data, chartType, theme, appState) {
    try {
        // 添加調試信息
        console.log('嘗試創建圖表 - ' + new Date().toISOString(), {
            chartType,
            theme,
            dataAvailable: !!data
        });
        
        // 輸出詳細的數據結構，有助於調試
        console.log('創建圖表的詳細數據:', JSON.stringify(data, null, 2).substring(0, 500) + '...');
        
        // 確保 Chart.js 存在
        if (typeof Chart === 'undefined') {
            console.error('Chart.js 未載入，無法創建圖表');
            
            // 更新頁面上的調試信息
            const debugInfo = document.getElementById('debug-info');
            if (debugInfo) {
                debugInfo.innerText = 'ERROR: Chart.js 未載入，無法創建圖表';
            }
            
            throw new Error('Chart.js 函式庫未載入');
        }
        
        // 檢查 Chart.js 版本
        console.log('Chart.js 版本:', Chart.version);
        
        // 檢查有哪些可用的控制器
        console.log('可用控制器:', Object.keys(Chart.controllers || {}));
        
        // 特殊圖表類型的處理 - 增強版
        console.log(`處理圖表類型: ${chartType}`);
        
        // 對於特殊圖表類型的轉換處理
        if (chartType === 'butterfly') {
            console.log('檢測到蝴蝶圖，這將被轉換為帶有特殊配置的柱狀圖');
            // 不改變圖表類型，讓 prepareChartConfig 處理轉換
        }

        if (chartType === 'sankey') {
            console.log('檢測到桑基圖，檢查是否已載入 sankey 控制器');
            
            // 檢查是否有 sankey 控制器
            if (!Chart.controllers.sankey) {
                console.warn('未找到桑基圖控制器，可能需要額外的插件');
                
                // 嘗試載入 Chart.js Sankey 插件
                try {
                    if (window.ChartSankey) {
                        console.log('檢測到 ChartSankey 插件，嘗試註冊');
                        Chart.register(window.ChartSankey);
                    } else {
                        // 如果沒有 Sankey 插件，回退到使用其他圖表類型
                        console.warn('未找到 Sankey 圖表插件，回退到使用混合圖表類型');
                        chartType = 'bar'; // 使用柱狀圖作為回退
                        
                        // 提示使用者
                        showError('桑基圖需要額外的插件支援，已回退到使用柱狀圖替代。');
                    }
                } catch (error) {
                    console.error('載入桑基圖插件失敗:', error);
                    chartType = 'bar';
                }
            }
        }
        
        // 初始化圖表控制器狀態檢查
        const existingControllers = Object.keys(Chart.controllers || {});
        console.log('當前註冊的控制器:', existingControllers);

        // 確保支援極座標圖
        if (chartType === 'polarArea') {
            console.log('處理極座標圖 (polarArea)');
            
            // 檢查控制器是否存在
            if (!Chart.controllers.polarArea) {
                console.warn('未找到極座標圖控制器，嘗試手動註冊...');
                
                // 嘗試從Chart.js核心註冊控制器
                try {
                    if (Chart.PolarAreaController) {
                        Chart.register(Chart.PolarAreaController);
                        console.log('成功註冊極座標圖控制器');
                    } else {
                        console.error('未找到極座標圖控制器，將回退到圓餅圖');
                        chartType = 'pie';
                    }
                } catch (error) {
                    console.error('註冊極座標圖控制器失敗:', error);
                    chartType = 'pie';
                }
            }
        }
        
        // 金融圖表類型的特殊處理
        if (['candlestick', 'ohlc'].includes(chartType)) {
            console.log(`準備創建金融圖表: ${chartType}`);
            
            // 檢查金融圖表數據結構
            if (data && data.datasets && data.datasets[0] && Array.isArray(data.datasets[0].data)) {
                const samplePoint = data.datasets[0].data[0];
                if (samplePoint) {
                    console.log('數據點示例:', samplePoint);
                    
                    // 檢查時間字段並進行標準化
                    const timeField = samplePoint.t || samplePoint.time || samplePoint.x || samplePoint.date;
                    console.log('時間字段值:', timeField, '類型:', typeof timeField);
                    
                    // 標準化時間格式
                    if (typeof timeField === 'string') {
                        try {
                            const dateObj = new Date(timeField);
                            const isValid = !isNaN(dateObj.getTime());
                            console.log('轉換後的日期對象:', dateObj, '是有效的:', isValid);
                            
                            // 預處理數據中的時間格式
                            if (isValid && data.datasets) {
                                data.datasets.forEach(dataset => {
                                    if (dataset.data && Array.isArray(dataset.data)) {
                                        dataset.data.forEach(point => {
                                            const pointTime = point.t || point.time || point.x || point.date;
                                            if (typeof pointTime === 'string') {
                                                // 直接轉換為 Date 對象
                                                point.t = new Date(pointTime);
                                            }
                                        });
                                    }
                                });
                            }
                            
                            // YYYY-MM-DD 格式特殊處理
                            if (timeField.match(/^\d{4}-\d{2}-\d{2}$/)) {
                                const [year, month, day] = timeField.split('-').map(Number);
                                const utcDate = new Date(Date.UTC(year, month - 1, day));
                                console.log('使用 UTC 處理的日期:', utcDate);
                            }
                        } catch (dateError) {
                            console.error('日期轉換出錯:', dateError);
                        }
                    }
                }
            }
            
            // 檢查並註冊金融圖表控制器
            if (chartType === 'candlestick') {
                if (!Chart.controllers.candlestick) {
                    console.warn('未找到蠟燭圖控制器，嘗試手動註冊...');
                    let controllerRegistered = false;
                    
                    // 方法1: 嘗試從window對象註冊
                    try {
                        if (window.CandlestickController) {
                            Chart.register(window.CandlestickController);
                            controllerRegistered = true;
                            console.log('已從window.CandlestickController註冊蠟燭圖控制器');
                        }
                    } catch (e) {
                        console.warn('從window.CandlestickController註冊失敗:', e);
                    }
                    
                    // 方法2: 嘗試從financial包註冊
                    if (!controllerRegistered && window.Chart && window.Chart.controllers && window.Chart.controllers.financial) {
                        try {
                            Chart.register(window.Chart.controllers.financial.CandlestickController);
                            controllerRegistered = true;
                            console.log('已從financial包註冊蠟燭圖控制器');
                        } catch (e) {
                            console.warn('從financial包註冊蠟燭圖控制器失敗:', e);
                        }
                    }
                    
                    // 方法3: 從全局命名空間尋找
                    if (!controllerRegistered) {
                        const globalControllers = Object.keys(window).filter(key => key.includes('Candlestick') || key.includes('candlestick'));
                        console.log('可能的全局控制器:', globalControllers);
                        
                        for (const key of globalControllers) {
                            if (window[key] && typeof window[key] === 'function') {
                                try {
                                    Chart.register(window[key]);
                                    controllerRegistered = true;
                                    console.log(`已從${key}註冊蠟燭圖控制器`);
                                    break;
                                } catch (e) {
                                    console.warn(`從${key}註冊失敗:`, e);
                                }
                            }
                        }
                    }
                    
                    // 如果仍未註冊成功，回退到折線圖
                    if (!controllerRegistered) {
                        console.error('無法註冊蠟燭圖控制器，回退到折線圖');
                        chartType = 'line';
                    }
                }
            }
            
            // 檢查並註冊OHLC控制器
            if (chartType === 'ohlc') {
                if (!Chart.controllers.ohlc) {
                    console.warn('未找到OHLC控制器，嘗試手動註冊...');
                    let controllerRegistered = false;
                    
                    // 方法1: 嘗試從window對象註冊
                    try {
                        if (window.OhlcController) {
                            Chart.register(window.OhlcController);
                            controllerRegistered = true;
                            console.log('已從window.OhlcController註冊OHLC控制器');
                        }
                    } catch (e) {
                        console.warn('從window.Ohlc.Controller註冊失敗:', e);
                    }
                    
                    // 方法2: 嘗試從financial包註冊
                    if (!controllerRegistered && window.Chart && window.Chart.controllers && window.Chart.controllers.financial) {
                        try {
                            Chart.register(window.Chart.controllers.financial.OhlcController);
                            controllerRegistered = true;
                            console.log('已從financial包註冊OHLC控制器');
                        } catch (e) {
                            console.warn('從financial包註冊OHLC控制器失敗:', e);
                        }
                    }
                    
                    // 方法3: 從全局命名空間尋找
                    if (!controllerRegistered) {
                        const globalControllers = Object.keys(window).filter(key => key.includes('Ohlc') || key.includes('ohlc') || key.includes('OHLC'));
                        console.log('可能的全局控制器:', globalControllers);
                        
                        for (const key of globalControllers) {
                            if (window[key] && typeof window[key] === 'function') {
                                try {
                                    Chart.register(window[key]);
                                    controllerRegistered = true;
                                    console.log(`已從${key}註冊OHLC控制器`);
                                    break;
                                } catch (e) {
                                    console.warn(`從${key}註冊失敗:`, e);
                                }
                            }
                        }
                    }
                    
                    // 如果仍未註冊成功，嘗試使用candlestick，或回退到折線圖
                    if (!controllerRegistered) {
                        if (Chart.controllers.candlestick) {
                            console.warn('無法註冊OHLC控制器，回退到蠟燭圖');
                            chartType = 'candlestick';
                        } else {
                            console.error('無法註冊OHLC控制器，回退到折線圖');
                            chartType = 'line';
                        }
                    }
                }
            }
        }
        
        // 確保支持桑基圖
        if (chartType === 'sankey' && (!Chart.controllers || !Chart.controllers.sankey)) {
            console.warn('Chart.js 不支援桑基圖，嘗試使用折線圖代替');
            console.error('請確保已引入 chartjs-chart-sankey.js 插件');
            chartType = 'line'; // 回退到折線圖
        }

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
        
        // 增強的圖表銷毀邏輯 - 確保徹底清理圖表實例
        if (appState.myChart) {
            console.log('銷毀先前的圖表實例');
            try {
                // 確保先解除事件監聽器
                if (appState.myChart.canvas) {
                    appState.myChart.canvas.removeEventListener('click', null);
                    appState.myChart.canvas.removeEventListener('mousemove', null);
                }
                
                // 停止任何可能的動畫
                if (appState.myChart.stop) {
                    appState.myChart.stop();
                }
                
                // 正常銷毀圖表
                appState.myChart.destroy();
                
                // 確保銷毀完成
                if (Chart.instances && Chart.instances[appState.myChart.id]) {
                    delete Chart.instances[appState.myChart.id];
                }
            } catch (destroyError) {
                console.warn('銷毀先前圖表時出錯:', destroyError);
            }
            
            // 清除狀態中的圖表引用
            appState.myChart = null;
        }
        
        // 檢查是否有其他圖表實例正在使用同一畫布
        const existingChart = Chart.getChart(canvas);
        if (existingChart) {
            console.log('發現同一畫布上存在其他圖表實例，ID:', existingChart.id);
            try {
                // 在銷毀前先分離事件監聽器
                if (existingChart.canvas) {
                    existingChart.canvas.removeEventListener('click', null);
                    existingChart.canvas.removeEventListener('mousemove', null);
                    existingChart.canvas.removeEventListener('mouseout', null);
                }
                
                // 確保停止任何進行中的動畫
                if (existingChart.stop) {
                    existingChart.stop();
                }
                
                // 銷毀該實例
                existingChart.destroy();
                console.log('成功銷毀畫布上的舊圖表實例');
                
                // 從全局實例登記表中移除引用
                if (Chart.instances && existingChart.id) {
                    delete Chart.instances[existingChart.id];
                }
            } catch (err) {
                console.error('銷毀畫布上的舊圖表實例時出錯:', err);
                
                // 備用清理方式 - 直接清理 Canvas
                try {
                    const ctx = canvas.getContext('2d');
                    ctx.clearRect(0, 0, canvas.width, canvas.height);
                } catch (e) {
                    console.error('Canvas 清理失敗:', e);
                }
            }
        }
        
        // 確保 canvas 徹底清理完畢並重新初始化
        const ctx = canvas.getContext('2d');
        ctx.save();
        ctx.resetTransform();
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.restore();
        
        // 確保 canvas 尺寸正確
        const chartContainer = document.getElementById('chartContainer');
        if (chartContainer) {
            const containerWidth = chartContainer.clientWidth;
            const containerHeight = chartContainer.clientHeight;
            
            // 重新設置 canvas 尺寸，解決舊版本兼容性問題
            canvas.width = containerWidth * 2;  // 高解析度
            canvas.height = containerHeight * 2;
            canvas.style.width = `${containerWidth}px`;
            canvas.style.height = `${containerHeight}px`;
            
            console.log(`Canvas 尺寸重設為 ${containerWidth}x${containerHeight}`);
        }
        
        // 確保 Chart.js 的 registry 正常
        if (Chart.registry) {
            console.log('Chart.js registry 狀態:', {
                controllers: Object.keys(Chart.registry.controllers).length,
                elements: Object.keys(Chart.registry.elements).length,
                plugins: Object.keys(Chart.registry.plugins).length
            });
        }
        
        // 準備圖表配置
        const chartConfig = prepareChartConfig(data, chartType, theme, appState);
        
        // 在創建圖表前輸出詳細的配置和狀態
        console.log(`即將創建${chartType}圖表，詳細配置:`, {
            chartType,
            theme,
            controllers: Object.keys(Chart.controllers || {}),
            config: chartConfig
        });
        
        // 更強健的圖表創建邏輯
        let chart = null;
        const maxRetries = 2; // 最大重試次數
        
        for (let attempt = 0; attempt <= maxRetries; attempt++) {
            try {
                // 特殊處理 polarArea 圖表類型
                if (chartType === 'polarArea' && attempt === 0) {
                    // 確保極座標圖控制器已註冊
                    if (!Chart.controllers.polarArea) {
                        if (Chart.PolarAreaController) {
                            Chart.register(Chart.PolarAreaController);
                            console.log('在創建前註冊極座標圖控制器');
                        }
                    }
                }
                
                // 特殊處理金融圖表
                if (['candlestick', 'ohlc'].includes(chartType) && !Chart.controllers[chartType]) {
                    console.warn(`創建前檢測到Chart.js缺少${chartType}控制器，嘗試最後手動註冊...`);
                    
                    // 嘗試從 window 對象獲取 chartjs-financial 插件的控制器
                    try {
                        if (chartType === 'candlestick' && window.Chart && window.Chart.controllers && 
                            window.Chart.controllers.financial && 
                            typeof window.Chart.controllers.financial.CandlestickController !== 'undefined') {
                            Chart.register(window.Chart.controllers.financial.CandlestickController);
                            console.log('手動註冊 CandlestickController 成功');
                        } else if (chartType === 'ohlc' && window.Chart && window.Chart.controllers && 
                                   window.Chart.controllers.financial && 
                                   typeof window.Chart.controllers.financial.OhlcController !== 'undefined') {
                            Chart.register(window.Chart.controllers.financial.OhlcController);
                            console.log('手動註冊 OhlcController 成功');
                        } else {
                            // 如果仍然無法註冊，回退到基本圖表類型
                            if (attempt === maxRetries) {
                                console.error(`多次嘗試後仍找不到 ${chartType} 控制器，將回退到線圖`);
                                chartConfig.type = 'line';
                            }
                        }
                    } catch (regError) {
                        console.error(`註冊 ${chartType} 控制器失敗:`, regError);
                        if (attempt === maxRetries) {
                            chartConfig.type = 'line';
                        }
                    }
                }
                
                // 增強版日期轉接器處理邏輯
                if (chartConfig.options && chartConfig.options.scales && 
                   (chartConfig.options.scales.x && chartConfig.options.scales.x.type === 'time')) {
                    // 檢查 Luxon 和轉接器是否可用
                    if (typeof luxon === 'undefined' || typeof Chart.adapters._date === 'undefined') {
                        console.warn('Luxon 或日期轉接器未正確載入，嘗試手動註冊');
                        
                        try {
                            // 嘗試註冊內置日期轉接器
                            if (typeof luxon !== 'undefined') {
                                Chart.register({
                                    id: 'luxonAdapter',
                                    _date: {
                                        parse: function(value) {
                                            if (value instanceof Date) {
                                                return value;
                                            }
                                            
                                            if (typeof value === 'string') {
                                                try {
                                                    return luxon.DateTime.fromISO(value).toJSDate();
                                                } catch (e) {
                                                    return new Date(value);
                                                }
                                            }
                                            
                                            return new Date(value);
                                        },
                                        format: function(timestamp, format) {
                                            const dt = luxon.DateTime.fromJSDate(timestamp);
                                            if (format === 'yyyy-MM-dd') {
                                                return dt.toFormat('yyyy-MM-dd');
                                            } else if (format === 'yyyy-MM-dd HH:mm:ss') {
                                                return dt.toFormat('yyyy-MM-dd HH:mm:ss');
                                            } else {
                                                return dt.toLocaleString(luxon.DateTime.DATETIME_SHORT);
                                            }
                                        },
                                        add: function(time, amount, unit) {
                                            const dt = luxon.DateTime.fromJSDate(time);
                                            const result = dt.plus({ [unit]: amount });
                                            return result.toJSDate();
                                        },
                                        diff: function(max, min, unit) {
                                            const dtMax = luxon.DateTime.fromJSDate(max);
                                            const dtMin = luxon.DateTime.fromJSDate(min);
                                            return dtMax.diff(dtMin, unit).values[unit];
                                        },
                                        startOf: function(time, unit) {
                                            const dt = luxon.DateTime.fromJSDate(time);
                                            const result = dt.startOf(unit);
                                            return result.toJSDate();
                                        },
                                        endOf: function(time, unit) {
                                            const dt = luxon.DateTime.fromJSDate(time);
                                            const result = dt.endOf(unit);
                                            return result.toJSDate();
                                        }
                                    }
                                });
                                console.log('已手動註冊 Luxon 日期轉接器');
                            } else {
                                // 如果無法註冊，則切換到類別軸
                                console.log('無法註冊日期轉接器，切換到類別軸以避免問題');
                                chartConfig.options.scales.x.type = 'category';
                                delete chartConfig.options.scales.x.time;
                            }
                        } catch (adapterError) {
                            console.error('註冊日期轉接器時出錯:', adapterError);
                            // 回退到類別軸
                            chartConfig.options.scales.x.type = 'category';
                            delete chartConfig.options.scales.x.time;
                        }
                    } else {
                        console.log('日期轉接器已正確載入');
                    }
                }
                
                // 嘗試創建圖表
                console.log(`嘗試 #${attempt + 1}: 創建${chartConfig.type}圖表`);
                chart = new Chart(ctx, chartConfig);
                
                // 如果成功創建，跳出循環
                console.log(`圖表創建成功，ID: ${chart.id}`);
                break;
            } catch (chartError) {
                console.error(`嘗試 #${attempt + 1} 創建圖表失敗:`, chartError);
                
                // 如果不是最後一次嘗試，則清理 Canvas 並準備下次嘗試
                if (attempt < maxRetries) {
                    console.log('清理 Canvas 並準備重試...');
                    try {
                        // 徹底清理 Canvas
                        ctx.save();
                        ctx.resetTransform();
                        ctx.clearRect(0, 0, canvas.width, canvas.height);
                        ctx.restore();
                        
                        // 如果是特殊圖表類型問題，嘗試回退到更基本的圖表類型
                        if (['polarArea', 'candlestick', 'ohlc'].includes(chartConfig.type)) {
                            if (chartConfig.type === 'polarArea') {
                                console.log('嘗試從極座標圖回退到圓餅圖');
                                chartConfig.type = 'pie';
                            } else if (['candlestick', 'ohlc'].includes(chartConfig.type)) {
                                console.log('嘗試從金融圖表回退到線圖');
                                chartConfig.type = 'line';
                            }
                        }
                    } catch (cleanError) {
                        console.warn('清理 Canvas 時出錯:', cleanError);
                    }
                } else {
                    // 最後一次嘗試也失敗，返回 null
                    console.error('所有嘗試均失敗，無法創建圖表');
                    return null;
                }
            }
        }
        
        // 確認創建的圖表
        if (!chart) {
            console.error('無法創建圖表');
            return null;
        }
        
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
    console.log('正在準備圖表配置，類型:', chartType, '主題:', theme);

    // 驗證輸入
    if (!data || !chartType) {
        throw new Error('無效的圖表參數');
    }

    // 預設配置
    const defaultConfig = {
        responsive: true,
        maintainAspectRatio: false,
        animation: {
            duration: 1000,
            easing: 'easeOutQuad'
        }
    };

    // 根據圖表類型處理
    switch (chartType.toLowerCase()) {
        case 'butterfly':
            // 處理蝴蝶圖數據
            console.log('處理蝴蝶圖，將轉換為特殊配置的橫向柱狀圖');
            
            // 使用蝴蝶圖專用處理函數，如果可用的話
            let butterflyData;
            if (typeof window.processButterFlyData === 'function') {
                console.log('使用專用的蝴蝶圖數據處理函數');
                butterflyData = window.processButterFlyData(data);
            } else {
                console.log('使用標準柱狀圖處理函數處理蝴蝶圖數據');
                butterflyData = processBarData(data);
                
                // 確保第二個數據集的值為負數
                if (butterflyData.datasets && butterflyData.datasets.length >= 2) {
                    butterflyData.datasets[1].data = butterflyData.datasets[1].data.map(val => {
                        return val > 0 ? -Math.abs(val) : val;
                    });
                }
            }
            
            return {
                type: 'bar',
                data: butterflyData,
                options: {
                    ...defaultConfig,
                    indexAxis: 'y', // 橫向柱狀圖
                    plugins: {
                        tooltip: {
                            mode: 'index',
                            callbacks: {
                                label: function(context) {
                                    const value = context.raw;
                                    // 顯示絕對值
                                    return `${context.dataset.label}: ${Math.abs(value)}`;
                                }
                            }
                        },
                        title: {
                            display: true,
                            text: data.title || data.chartTitle || '蝴蝶圖',
                            font: { size: 16 }
                        },
                        legend: {
                            position: 'top'
                        }
                    },
                    scales: {
                        x: {
                            stacked: false,
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: (data.options && data.options.scales && data.options.scales.x && data.options.scales.x.title && data.options.scales.x.title.text) || '數值'
                            },
                            ticks: {
                                callback: function(value) {
                                    // 顯示絕對值
                                    return Math.abs(value);
                                }
                            }
                        },
                        y: {
                            stacked: false,
                            title: {
                                display: true,
                                text: (data.options && data.options.scales && data.options.scales.y && data.options.scales.y.title && data.options.scales.y.title.text) || '類別'
                            }
                        }
                    }
                }
            };
            
        case 'sankey':
            return {
                type: 'sankey',
                data: processSankeyData(data),
                options: {
                    ...defaultConfig,
                    plugins: {
                        tooltip: {
                            callbacks: {
                                title: function(context) {
                                    return context[0].label || '';
                                },
                                label: function(context) {
                                    return `流量: ${context.raw.flow}`;
                                }
                            }
                        },
                        title: {
                            display: true,
                            text: data.title || data.chartTitle || '桑基圖',
                            font: { size: 16 }
                        }
                    }
                }
            };
            
        case 'candlestick':
            // 預處理蠟燭圖數據，確保時間格式正確
            const processedData = processCandlestickData(data);
            
            // 檢查數據並確保時間格式正確
            if (processedData.datasets && processedData.datasets.length > 0) {
                processedData.datasets.forEach(dataset => {
                    if (dataset.data && Array.isArray(dataset.data)) {
                        dataset.data.forEach(point => {
                            // 確保每個點都有 t 屬性，並且是 Date 對象
                            if (point.t && !(point.t instanceof Date)) {
                                try {
                                    point.t = new Date(point.t);
                                } catch (e) {
                                    console.error('無法轉換時間格式:', point.t, e);
                                    // 使用當前時間作為後備方案
                                    point.t = new Date();
                                }
                            }
                        });
                    }
                });
            }
            
            // 檢測適合的時間單位
            let timeUnit = 'day';
            try {
                if (processedData.datasets && processedData.datasets[0] && processedData.datasets[0].data) {
                    const sampleData = processedData.datasets[0].data;
                    if (sampleData.length > 0) {
                        timeUnit = detectTimeUnit(sampleData);
                        console.log('檢測到的時間單位:', timeUnit);
                    }
                }
            } catch (e) {
                console.warn('檢測時間單位失敗:', e);
            }
            
            return {
                type: 'candlestick',
                data: processedData,
                options: {
                    ...defaultConfig,
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            enabled: true, // 確保啟用工具提示
                            mode: 'index',
                            intersect: false,
                            callbacks: {
                                label: function labelCandlestickPoint(context) {
                                    const point = context.raw;
                                    if (!point || typeof point !== 'object') return ['無效數據'];
                                    
                                    return [
                                        `開盤: ${(point.o || 0).toFixed(2)}`,
                                        `最高: ${(point.h || 0).toFixed(2)}`,
                                        `最低: ${(point.l || 0).toFixed(2)}`,
                                        `收盤: ${(point.c || 0).toFixed(2)}`
                                    ];
                                },
                                title: function formatCandlestickTitle(context) {
                                    if (!context || !context[0] || !context[0].raw || !context[0].raw.t) {
                                        return '無效時間';
                                    }
                                    try {
                                        const candleDate = new Date(context[0].raw.t);
                                        // 確認日期有效
                                        if (isNaN(candleDate.getTime())) {
                                            return '無效時間';
                                        }
                                        return candleDate.toLocaleString();
                                    } catch (e) {
                                        console.error('格式化時間出錯:', e);
                                        return '無效時間';
                                    }
                                }
                            }
                        },
                        title: {
                            display: true,
                            text: data.title || '價格圖表',
                            font: { size: 16 }
                        }
                    },
                    scales: {
                        x: {
                            type: 'time',
                            time: {
                                unit: timeUnit, // 使用檢測到的時間單位
                                displayFormats: {
                                    millisecond: 'HH:mm:ss.SSS',
                                    second: 'HH:mm:ss',
                                    minute: 'HH:mm',
                                    hour: 'HH:mm',
                                    day: 'yyyy-MM-dd',
                                    week: 'yyyy-MM-dd',
                                    month: 'yyyy-MM',
                                    quarter: 'yyyy-[Q]Q',
                                    year: 'yyyy'
                                },
                                tooltipFormat: 'yyyy-MM-dd HH:mm:ss'
                            },
                            title: {
                                display: true,
                                text: '時間'
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: '價格'
                            },
                            ticks: {
                                callback: function(value) {
                                    return value.toFixed(2);
                                }
                            }
                        }
                    }
                }
            };
            
        case 'ohlc':
            console.log('進入 OHLC 圖表處理分支');
            // 預處理 OHLC 數據，確保時間格式正確
            const ohlcData = processCandlestickData(data); // OHLC圖使用與蠟燭圖相同的數據結構
            console.log('OHLC 數據處理完成:', ohlcData ? '成功' : '失敗');

            // 檢查數據並確保時間格式正確
            if (ohlcData.datasets && ohlcData.datasets.length > 0) {
                ohlcData.datasets.forEach(dataset => {
                    if (dataset.data && Array.isArray(dataset.data)) {
                        dataset.data.forEach(point => {
                            // 確保每個點都有 t 屬性，並且是 Date 對象
                            if (point.t && !(point.t instanceof Date)) {
                                try {
                                    point.t = new Date(point.t);
                                } catch (e) {
                                    console.error('無法轉換時間格式:', point.t, e);
                                    // 使用當前時間作為後備方案
                                    point.t = new Date();
                                }
                            }
                        });
                    }
                });
            }
            
            // 檢測適合的時間單位
            let ohlcTimeUnit = 'day';
            try {
                if (ohlcData.datasets && ohlcData.datasets[0] && ohlcData.datasets[0].data) {
                    const sampleData = ohlcData.datasets[0].data;
                    if (sampleData.length > 0) {
                        ohlcTimeUnit = detectTimeUnit(sampleData);
                        console.log('檢測到的時間單位:', ohlcTimeUnit);
                    }
                }
            } catch (e) {
                console.warn('檢測時間單位失敗:', e);
            }
            
            return {
                type: 'ohlc',
                data: ohlcData,
                options: {
                    ...defaultConfig,
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            enabled: true, // 確保啟用工具提示
                            mode: 'index',
                            intersect: false,
                            callbacks: {
                                label: function labelOhlcPoint(context) {
                                    const point = context.raw;
                                    if (!point || typeof point !== 'object') return ['無效數據'];
                                    
                                    return [
                                        `開盤: ${(point.o || 0).toFixed(2)}`,
                                        `最高: ${(point.h || 0).toFixed(2)}`,
                                        `最低: ${(point.l || 0).toFixed(2)}`,
                                        `收盤: ${(point.c || 0).toFixed(2)}`
                                    ];
                                },
                                title: function formatOhlcTitle(context) {
                                    if (!context || !context[0] || !context[0].raw || !context[0].raw.t) {
                                        return '無效時間';
                                    }
                                    try {
                                        const ohlcDate = new Date(context[0].raw.t);
                                        // 確認日期有效
                                        if (isNaN(ohlcDate.getTime())) {
                                            return '無效時間';
                                        }
                                        return ohlcDate.toLocaleString();
                                    } catch (e) {
                                        console.error('格式化時間出錯:', e);
                                        return '無效時間';
                                    }
                                }
                            }
                        },
                        title: {
                            display: true,
                            text: data.title || 'OHLC價格圖表',
                            font: { size: 16 }
                        }
                    },
                    scales: {
                        x: {
                            type: 'time',
                            time: {
                                unit: ohlcTimeUnit, // 使用檢測到的時間單位
                                displayFormats: {
                                    millisecond: 'HH:mm:ss.SSS',
                                    second: 'HH:mm:ss',
                                    minute: 'HH:mm',
                                    hour: 'HH:mm',
                                    day: 'yyyy-MM-dd',
                                    week: 'yyyy-MM-dd',
                                    month: 'yyyy-MM',
                                    quarter: 'yyyy-[Q]Q',
                                    year: 'yyyy'
                                },
                                tooltipFormat: 'yyyy-MM-dd HH:mm:ss'
                            },
                            title: {
                                display: true,
                                text: '時間'
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: '價格'
                            },
                            ticks: {
                                callback: function(value) {
                                    return value.toFixed(2);
                                }
                            }
                        }
                    }
                }
            };

        case 'bar':
            return {
                type: 'bar',
                data: processBarData(data),
                options: {
                    ...defaultConfig,
                    plugins: {
                        tooltip: {
                            mode: 'index',
                            intersect: false
                        },
                        title: {
                            display: true,
                            text: data.title || '長條圖',
                            font: { size: 16 }
                        }
                    },
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: '類別'
                            }
                        },
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: '數值'
                            }
                        }
                    }
                }
            };
            
        case 'pie':
            return {
                type: 'pie',
                data: processPieData(data),
                options: {
                    ...defaultConfig,
                    plugins: {
                        tooltip: {
                            mode: 'point',
                            callbacks: {
                                label: function(context) {
                                    const label = context.label || '';
                                    const value = context.raw || 0;
                                    const total = context.dataset.data.reduce((acc, val) => acc + val, 0);
                                    const percentage = Math.round((value / total) * 100);
                                    return `${label}: ${value} (${percentage}%)`;
                                }
                            }
                        },
                        title: {
                            display: true,
                            text: data.title || '圓餅圖',
                            font: { size: 16 }
                        },
                        legend: {
                            position: 'right'
                        }
                    }
                }
            };
            
        case 'doughnut':
            return {
                type: 'doughnut',
                data: processPieData(data),
                options: {
                    ...defaultConfig,
                    plugins: {
                        tooltip: {
                            mode: 'point',
                            callbacks: {
                                label: function(context) {
                                    const label = context.label || '';
                                    const value = context.raw || 0;
                                    const total = context.dataset.data.reduce((acc, val) => acc + val, 0);
                                    const percentage = Math.round((value / total) * 100);
                                    return `${label}: ${value} (${percentage}%)`;
                                }
                            }
                        },
                        title: {
                            display: true,
                            text: data.title || '環狀圖',
                            font: { size: 16 }
                        },
                        legend: {
                            position: 'right'
                        }
                    },
                    cutout: '50%'
                }
            };
            
        case 'radar':
            return {
                type: 'radar',
                data: processRadarData(data),
                options: {
                    ...defaultConfig,
                    plugins: {
                        title: {
                            display: true,
                            text: data.title || '雷達圖',
                            font: { size: 16 }
                        }
                    },
                    scales: {
                        r: {
                            beginAtZero: true
                        }
                    }
                }
            };
            
        case 'polarArea':
            return {
                type: 'polarArea',
                data: processPieData(data), // 極座標圖數據結構與圓餅圖類似
                options: {
                    ...defaultConfig,
                    plugins: {
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const label = context.label || '';
                                    const value = context.raw || 0;
                                    const total = context.dataset.data.reduce((acc, val) => acc + val, 0);
                                    const percentage = Math.round((value / total) * 100);
                                    return `${label}: ${value} (${percentage}%)`;
                                }
                            }
                        },
                        title: {
                            display: true,
                            text: data.title || '極座標圖',
                            font: { size: 16 }
                        },
                        legend: {
                            position: 'right'
                        }
                    },
                    scales: {
                        r: {
                            beginAtZero: true,
                            // 增強極座標圖軸的配置
                            ticks: {
                                precision: 0,
                                stepSize: 10,
                                font: {
                                    size: 10
                                }
                            },
                            pointLabels: {
                                font: {
                                    size: 12
                                }
                            },
                            grid: {
                                circular: true
                            }
                        }
                    }
                }
            };
            
        case 'scatter':
            return {
                type: 'scatter',
                data: processScatterData(data),
                options: {
                    ...defaultConfig,
                    plugins: {
                        tooltip: {
                            mode: 'point',
                            callbacks: {
                                label: function(context) {
                                    const point = context.raw;
                                    return `(${point.x}, ${point.y})`;
                                }
                            }
                        },
                        title: {
                            display: true,
                            text: data.title || '散點圖',
                            font: { size: 16 }
                        }
                    },
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: 'X'
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: 'Y'
                            }
                        }
                    }
                }
            };
            
        case 'bubble':
            return {
                type: 'bubble',
                data: processBubbleData(data),
                options: {
                    ...defaultConfig,
                    plugins: {
                        tooltip: {
                            mode: 'point',
                            callbacks: {
                                label: function(context) {
                                    const point = context.raw;
                                    return `(${point.x}, ${point.y}, ${point.r})`;
                                }
                            }
                        },
                        title: {
                            display: true,
                            text: data.title || '氣泡圖',
                            font: { size: 16 }
                        }
                    },
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: 'X'
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: 'Y'
                            }
                        }
                    }
                }
            };
        
        case 'line':
            // 判斷數據是否包含時間序列
            let useTimeAxis = false;
            let hasTimeData = false;
            
            try {
                const processedLineData = processLineData(data);
                
                // 檢查是否有時間序列數據
                if (processedLineData.datasets && processedLineData.datasets.length > 0 && 
                    processedLineData.datasets[0].data && processedLineData.datasets[0].data.length > 0) {
                    
                    const samplePoint = processedLineData.datasets[0].data[0];
                    if (samplePoint && (samplePoint.x instanceof Date || typeof samplePoint.x === 'string' && !isNaN(new Date(samplePoint.x).getTime()))) {
                        hasTimeData = true;
                    }
                }
                
                // 檢查日期適配器是否可用
                useTimeAxis = hasTimeData && typeof luxon !== 'undefined' && typeof Chart.adapters._date !== 'undefined';
                
                return {
                    type: 'line',
                    data: processedLineData,
                    options: {
                        ...defaultConfig,
                        plugins: {
                            tooltip: {
                                mode: 'index',
                                intersect: false
                            },
                            title: {
                                display: true,
                                text: data.title || '折線圖',
                                font: { size: 16 }
                            }
                        },
                        scales: {
                            x: useTimeAxis ? {
                                type: 'time',
                                time: {
                                    unit: 'day',
                                    displayFormats: {
                                        day: 'yyyy-MM-dd'
                                    }
                                },
                                title: {
                                    display: true,
                                    text: '時間'
                                }
                            } : {
                                type: 'category',
                                title: {
                                    display: true,
                                    text: '類別'
                                }
                            },
                            y: {
                                beginAtZero: true,
                                title: {
                                    display: true,
                                    text: '數值'
                                }
                            }
                        }
                    }
                };
            } catch (error) {
                console.error('處理折線圖配置時出錯:', error);
                // 返回安全的備用配置，不使用時間軸
                return {
                    type: 'line',
                    data: processLineData(data),
                    options: {
                        ...defaultConfig,
                        plugins: {
                            tooltip: {
                                mode: 'index',
                                intersect: false
                            },
                            title: {
                                display: true,
                                text: data.title || '折線圖',
                                font: { size: 16 }
                            }
                        },
                        scales: {
                            x: {
                                type: 'category',
                                title: {
                                    display: true,
                                    text: '類別'
                                }
                            },
                            y: {
                                beginAtZero: true,
                                title: {
                                    display: true,
                                    text: '數值'
                                }
                            }
                        }
                    }
                };
            }
        
        default:
            console.warn(`未知圖表類型 '${chartType}'，使用折線圖替代。`);
            return {
                type: 'line',
                data: processLineData(data),
                options: {
                    ...defaultConfig,
                    plugins: {
                        tooltip: {
                            mode: 'index',
                            intersect: false
                        },
                        title: {
                            display: true,
                            text: data.title || '資料圖表',
                            font: { size: 16 }
                        }
                    },
                    scales: {
                        x: {
                            type: 'time',
                            time: {
                                unit: 'day',
                                displayFormats: {
                                    day: 'yyyy-MM-dd'
                                }
                            },
                            title: {
                                display: true,
                                text: '時間'
                            }
                        },
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: '數值'
                            }
                        }
                    }
                }
            }
        }
    }

// 處理蠟燭圖資料
function processCandlestickData(data) {
    console.log('processCandlestickData 被調用，數據類型:', typeof data);
    const processedData = {
        datasets: [{
            label: '價格',
            data: []
        }]
    };

    try {
        console.log('處理蠟燭圖數據:', data);
        // 獲取數據來源
        const sourceData = data.datasets?.[0]?.data || data.data?.datasets?.[0]?.data || data.data || [];
        
        // 如果是原始數據格式，提取數據
        if (sourceData.datasets && sourceData.datasets[0] && Array.isArray(sourceData.datasets[0].data)) {
            processedData.datasets[0].data = sourceData.datasets[0].data;
        } else {
            processedData.datasets[0].data = sourceData;
        }
        
        // 設置標籤
        if (data.datasets && data.datasets[0] && data.datasets[0].label) {
            processedData.datasets[0].label = data.datasets[0].label;
        } else if (data.data && data.data.datasets && data.data.datasets[0] && data.data.datasets[0].label) {
            processedData.datasets[0].label = data.data.datasets[0].label;
        }
        
        console.log('原始數據點數:', processedData.datasets[0].data.length);
        
        // 處理每個數據點
        processedData.datasets[0].data = processedData.datasets[0].data
            .filter(item => (
                item &&
                (item.t !== undefined || item.time !== undefined || item.x !== undefined || item.date !== undefined) &&
                (item.o !== undefined || item.open !== undefined) &&
                (item.h !== undefined || item.high !== undefined) &&
                (item.l !== undefined || item.low !== undefined) &&
                (item.c !== undefined || item.close !== undefined)
            ))
            .map(item => {
                // 處理時間字段
                let timeValue;
                try {
                    const rawTime = item.t || item.time || item.x || item.date;
                    
                    if (rawTime instanceof Date) {
                        timeValue = rawTime;
                    } else if (typeof rawTime === 'string') {
                        // 嘗試以多種格式解析日期字符串
                        if (rawTime.match(/^\d{4}-\d{2}-\d{2}$/)) {
                            // YYYY-MM-DD 格式，確保使用 UTC 時間以避免時區問題
                            const [year, month, day] = rawTime.split('-').map(Number);
                            timeValue = new Date(Date.UTC(year, month - 1, day));
                        } else {
                            // 嘗試標準解析
                            timeValue = new Date(rawTime);
                        }
                    } else if (typeof rawTime === 'number') {
                        timeValue = new Date(rawTime);
                    } else {
                        console.warn('無法識別的時間格式:', rawTime);
                        timeValue = new Date();
                    }
                    
                    // 驗證解析出的時間是否有效
                    if (isNaN(timeValue.getTime())) {
                        console.error('解析出無效的時間:', item.t || item.time || item.x || item.date);
                        throw new Error('Invalid time value');
                    }
                    
                } catch (dateError) {
                    console.error('解析日期出錯:', dateError, '原始數據:', item);
                    throw dateError; // 重新拋出錯誤，讓外層處理
                }
                
                // 標準化 OHLC 值
                return {
                    t: timeValue,
                    o: Number(item.o || item.open || 0),
                    h: Number(item.h || item.high || 0),
                    l: Number(item.l || item.low || 0),
                    c: Number(item.c || item.close || 0)
                };
            });

        console.log('處理後數據點數:', processedData.datasets[0].data.length);
        
        // 如果沒有有效數據，則生成樣本數據
        if (processedData.datasets[0].data.length === 0) {
            console.warn('沒有有效的蠟燭圖數據，使用生成的樣本數據');
            processedData.datasets[0].data = generateSampleData(30);
        }
        
        // 設置顏色風格
        if (data.datasets && data.datasets[0] && data.datasets[0].color) {
            processedData.datasets[0].color = data.datasets[0].color;
        } else {
            processedData.datasets[0].color = {
                up: 'rgba(75, 192, 75, 1)',
                down: 'rgba(255, 99, 132, 1)',
                unchanged: 'rgba(160, 160, 160, 1)'
            };
        }
        
        console.log('處理後的蠟燭圖數據:', processedData);
    } catch (error) {
        console.error('處理蠟燭圖資料時出錯:', error);
        console.log('嘗試生成樣本數據');
        processedData.datasets[0].data = generateSampleData(30);
    }

    console.log('processCandlestickData 處理完成，返回數據');
    return processedData;
}

// 生成範例資料 - 確保這是唯一的定義，移除了重複的定義
function generateSampleData(count) {
    const data = [];
    const now = Date.now();
    let price = 100;

    for (let i = 0; i < count; i++) {
        const change = price * (Math.random() * 0.1 - 0.05);
        const open = price;
        const close = price + change;
        const high = Math.max(open, close) * (1 + Math.random() * 0.02);
        const low = Math.min(open, close) * (1 - Math.random() * 0.02);

        data.push({
            t: new Date(now + i * 86400000),
            o: Number(open.toFixed(2)),
            h: Number(high.toFixed(2)),
            l: Number(low.toFixed(2)),
            c: Number(close.toFixed(2))
        });

        price = close;
    }

    return data;
}

// 處理一般線圖資料
function processLineData(data) {
    const processedData = {
        datasets: [{
            label: '數值',
            data: [],
            borderColor: 'rgb(75, 192, 192)',
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            tension: 0.1
        }]
    };

    try {
        const sourceData = data.datasets?.[0]?.data || data.data || [];
        processedData.datasets[0].data = sourceData
            .filter(item => item && (item.y || item.value))
            .map(item => ({
                x: new Date(item.x || item.time || Date.now()),
                y: Number(item.y || item.value)
            }))
            .filter(item => !isNaN(item.y));

        if (processedData.datasets[0].data.length === 0) {
            const now = Date.now();
            processedData.datasets[0].data = Array(10).fill(0).map((_, i) => ({
                x: new Date(now + i * 86400000),
                y: Math.random() * 100
            }));
        }
    } catch (error) {
        console.error('處理線圖資料時出錯:', error);
        processedData.datasets[0].data = [];
    }

    return processedData;
}

// 處理桑基圖資料
function processSankeyData(data) {
    const processedData = {
        datasets: [{
            label: '流量',
            data: [],
            colorFrom: (context) => {
                // 根據來源節點生成顏色
                const fromLabel = context.dataset.data[context.dataIndex].from;
                const hash = Array.from(fromLabel).reduce((acc, char) => {
                    return char.charCodeAt(0) + ((acc << 5) - acc);
                }, 0);
                const h = Math.abs(hash) % 360;
                return `hsla(${h}, 75%, 50%, 0.8)`;
            },
            colorTo: (context) => {
                // 根據目標節點生成顏色
                const toLabel = context.dataset.data[context.dataIndex].to;
                const hash = Array.from(toLabel).reduce((acc, char) => {
                    return char.charCodeAt(0) + ((acc << 5) - acc);
                }, 0);
                const h = Math.abs(hash) % 360;
                return `hsla(${h}, 75%, 60%, 0.8)`;
            },
            colorMode: 'gradient',
            padding: 20
        }]
    };

    try {
        // 檢查是否有 nodes/links 格式的數據（標準桑基圖格式）
        if (data.data && data.data.nodes && data.data.links) {
            const nodes = data.data.nodes;
            const links = data.data.links;
            
            // 從 nodes/links 格式轉換為 from/to/flow 格式
            processedData.datasets[0].data = links.map(link => {
                let source, target;
                
                // 處理索引或字符串類型的來源/目標
                if (typeof link.source === 'number') {
                    source = nodes[link.source].name;
                } else if (typeof link.source === 'string') {
                    source = link.source;
                }
                
                if (typeof link.target === 'number') {
                    target = nodes[link.target].name;
                } else if (typeof link.target === 'string') {
                    target = link.target;
                }
                
                return {
                    from: source || `節點${link.source}`,
                    to: target || `節點${link.target}`,
                    flow: Number(link.value)
                };
            });
            
            console.log('已處理桑基圖標準格式數據');
            return processedData;
        }
        
        // 嘗試直接使用 from/to/flow 格式
        const sourceData = data.datasets?.[0]?.data || data.data || [];
        
        if (Array.isArray(sourceData) && sourceData.length > 0) {
            // 檢查資料格式是否為 from/to/flow 格式
            const isFromToFormat = sourceData.some(item => 
                item && 
                typeof item.from === 'string' && 
                typeof item.to === 'string' && 
                !isNaN(Number(item.flow))
            );
            
            if (isFromToFormat) {
                processedData.datasets[0].data = sourceData.map(item => ({
                    from: item.from,
                    to: item.to,
                    flow: Number(item.flow)
                }));
                console.log('已處理桑基圖 from/to/flow 格式數據');
                return processedData;
            } else {
                console.warn('桑基圖資料格式無效，請確保每個資料點都有正確的格式');
            }
        }
        
        // 如果沒有有效資料，生成示範資料
        if (processedData.datasets[0].data.length === 0) {
            processedData.datasets[0].data = generateSampleSankeyData();
            console.log('使用範例桑基圖資料');
        }
    } catch (error) {
        console.error('處理桑基圖資料時出錯:', error);
        processedData.datasets[0].data = generateSampleSankeyData();
    }

    return processedData;
}

// 生成桑基圖範例資料
function generateSampleSankeyData() {
    return [
        { from: '來源A', to: '目標X', flow: 20 },
        { from: '來源A', to: '目標Y', flow: 15 },
        { from: '來源B', to: '目標X', flow: 10 },
        { from: '來源B', to: '目標Z', flow: 25 },
        { from: '來源C', to: '目標Y', flow: 30 },
        { from: '來源C', to: '目標Z', flow: 18 }
    ];
}

// 處理蠟燭圖資料
function processButterFlyData(data) {
    console.log('processButterFlyData 被調用，數據類型:', typeof data);
    const processedData = {
        datasets: [{
            label: '價格',
            data: []
        }]
    };

    try {
        console.log('處理蝴蝶圖數據:', data);
        // 獲取數據來源
        const sourceData = data.datasets?.[0]?.data || data.data?.datasets?.[0]?.data || data.data || [];
        
        // 如果是原始數據格式，提取數據
        if (sourceData.datasets && sourceData.datasets[0] && Array.isArray(sourceData.datasets[0].data)) {
            processedData.datasets[0].data = sourceData.datasets[0].data;
        } else {
            processedData.datasets[0].data = sourceData;
        }
        
        // 設置標籤
        if (data.datasets && data.datasets[0] && data.datasets[0].label) {
            processedData.datasets[0].label = data.datasets[0].label;
        } else if (data.data && data.data.datasets && data.data.datasets[0] && data.data.datasets[0].label) {
            processedData.datasets[0].label = data.data.datasets[0].label;
        }
        
        console.log('原始數據點數:', processedData.datasets[0].data.length);
        
        // 處理每個數據點
        processedData.datasets[0].data = processedData.datasets[0].data
            .filter(item => (
                item &&
                (item.t !== undefined || item.time !== undefined || item.x !== undefined || item.date !== undefined) &&
                (item.o !== undefined || item.open !== undefined) &&
                (item.h !== undefined || item.high !== undefined) &&
                (item.l !== undefined || item.low !== undefined) &&
                (item.c !== undefined || item.close !== undefined)
            ))
            .map(item => {
                // 處理時間字段
                let timeValue;
                try {
                    const rawTime = item.t || item.time || item.x || item.date;
                    
                    if (rawTime instanceof Date) {
                        timeValue = rawTime;
                    } else if (typeof rawTime === 'string') {
                        // 嘗試以多種格式解析日期字符串
                        if (rawTime.match(/^\d{4}-\d{2}-\d{2}$/)) {
                            // YYYY-MM-DD 格式，確保使用 UTC 時間以避免時區問題
                            const [year, month, day] = rawTime.split('-').map(Number);
                            timeValue = new Date(Date.UTC(year, month - 1, day));
                        } else {
                            // 嘗試標準解析
                            timeValue = new Date(rawTime);
                        }
                    } else if (typeof rawTime === 'number') {
                        timeValue = new Date(rawTime);
                    } else {
                        console.warn('無法識別的時間格式:', rawTime);
                        timeValue = new Date();
                    }
                    
                    // 驗證解析出的時間是否有效
                    if (isNaN(timeValue.getTime())) {
                        console.error('解析出無效的時間:', item.t || item.time || item.x || item.date);
                        throw new Error('Invalid time value');
                    }
                    
                } catch (dateError) {
                    console.error('解析日期出錯:', dateError, '原始數據:', item);
                    throw dateError; // 重新拋出錯誤，讓外層處理
                }
                
                // 標準化 OHLC 值
                return {
                    t: timeValue,
                    o: Number(item.o || item.open || 0),
                    h: Number(item.h || item.high || 0),
                    l: Number(item.l || item.low || 0),
                    c: Number(item.c || item.close || 0)
                };
            });

        console.log('處理後數據點數:', processedData.datasets[0].data.length);
        
        // 如果沒有有效數據，則生成樣本數據
        if (processedData.datasets[0].data.length === 0) {
            console.warn('沒有有效的蝴蝶圖數據，使用生成的樣本數據');
            processedData.datasets[0].data = generateSampleData(30);
        }
        
        // 設置顏色風格
        if (data.datasets && data.datasets[0] && data.datasets[0].color) {
            processedData.datasets[0].color = data.datasets[0].color;
        } else {
            processedData.datasets[0].color = {
                up: 'rgba(75, 192, 75, 1)',
                down: 'rgba(255, 99, 132, 1)',
                unchanged: 'rgba(160, 160, 160, 1)'
            };
        }
        
        console.log('處理後的蝴蝶圖數據:', processedData);
    } catch (error) {
        console.error('處理蝴蝶圖資料時出錯:', error);
        console.log('嘗試生成樣本數據');
        processedData.datasets[0].data = generateSampleData(30);
    }

    console.log('processButterFlyData 處理完成，返回數據');
    return processedData;
}

// 處理長條圖資料
function processBarData(data) {
    const processedData = {
        labels: [],
        datasets: [{
            label: '數值',
            data: [],
            backgroundColor: 'rgba(75, 192, 192, 0.6)',
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 1
        }]
    };

    try {
        // 處理標籤
        if (data.labels && Array.isArray(data.labels)) {
            processedData.labels = data.labels;
        }
        
        // 處理數據集
        const sourceDatasets = data.datasets || [];
        if (sourceDatasets.length > 0) {
            processedData.datasets = sourceDatasets;
        } else if (Array.isArray(data.data)) {
            processedData.datasets[0].data = data.data;
            
            // 如果沒有標籤但有數據，生成數字標籤
            if (processedData.labels.length === 0 && data.data.length > 0) {
                processedData.labels = Array.from({ length: data.data.length }, (_, i) => `項目 ${i + 1}`);
            }
        }
        
        // 確保至少有一個數據集
        if (processedData.datasets.length === 0) {
            processedData.datasets = [{
                label: '數值',
                data: Array(5).fill(0).map(() => Math.floor(Math.random() * 100)),
                backgroundColor: 'rgba(75, 192, 192, 0.6)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            }];
        }
        
        // 確保有標籤
        if (processedData.labels.length === 0 && processedData.datasets[0].data.length > 0) {
            processedData.labels = Array.from(
                { length: processedData.datasets[0].data.length }, 
                (_, i) => `項目 ${i + 1}`
            );
        }
    } catch (error) {
        console.error('處理長條圖資料時出錯:', error);
        
        // 生成範例資料
        processedData.labels = ['項目1', '項目2', '項目3', '項目4', '項目5'];
        processedData.datasets[0].data = [65, 59, 80, 81, 56];
    }

    return processedData;
}

// 處理圓餅圖和環狀圖資料
function processPieData(data) {
    const processedData = {
        labels: [],
        datasets: [{
            label: '數值',
            data: [],
            backgroundColor: [
                'rgba(255, 99, 132, 0.6)',
                'rgba(54, 162, 235, 0.6)',
                'rgba(255, 206, 86, 0.6)',
                'rgba(75, 192, 192, 0.6)',
                'rgba(153, 102, 255, 0.6)',
                'rgba(255, 159, 64, 0.6)'
            ],
            hoverOffset: 4
        }]
    };

    try {
        // 處理標籤
        if (data.labels && Array.isArray(data.labels)) {
            processedData.labels = data.labels;
        }
        
        // 處理數據集
        const sourceDatasets = data.datasets || [];
        if (sourceDatasets.length > 0) {
            processedData.datasets = sourceDatasets;
        } else if (Array.isArray(data.data)) {
            processedData.datasets[0].data = data.data;
            
            // 如果沒有標籤但有數據，生成數字標籤
            if (processedData.labels.length === 0 && data.data.length > 0) {
                processedData.labels = Array.from({ length: data.data.length }, (_, i) => `項目 ${i + 1}`);
            }
        }
        
        // 確保至少有一個數據集
        if (processedData.datasets.length === 0 || processedData.datasets[0].data.length === 0) {
            processedData.labels = ['紅色', '藍色', '黃色', '綠色', '紫色'];
            processedData.datasets[0].data = [30, 20, 25, 15, 10];
        }
        
        // 確保有標籤
        if (processedData.labels.length === 0 && processedData.datasets[0].data.length > 0) {
            processedData.labels = Array.from(
                { length: processedData.datasets[0].data.length }, 
                (_, i) => `項目 ${i + 1}`
            );
        }
        
        // 確保背景顏色陣列足夠
        const dataLength = processedData.datasets[0].data.length;
        if (processedData.datasets[0].backgroundColor.length < dataLength) {
            // 使用色輪生成足夠的顏色
            const baseColors = processedData.datasets[0].backgroundColor.slice();
            while (processedData.datasets[0].backgroundColor.length < dataLength) {
                const index = processedData.datasets[0].backgroundColor.length % baseColors.length;
                const baseColor = baseColors[index];
                // 微調顏色以增加多樣性
                const adjustedColor = baseColor.replace(/[0-9.]+\)$/, (match) => {
                    return (parseFloat(match) * 0.9).toFixed(1) + ')';
                });
                processedData.datasets[0].backgroundColor.push(adjustedColor);
            }
        }
    } catch (error) {
        console.error('處理圓餅圖資料時出錯:', error);
        
        // 生成範例資料
        processedData.labels = ['紅色', '藍色', '黃色', '綠色', '紫色'];
        processedData.datasets[0].data = [30, 20, 25, 15, 10];
    }

    return processedData;
}

// 處理雷達圖資料
function processRadarData(data) {
    const processedData = {
        labels: [],
        datasets: [{
            label: '數值',
            data: [],
            fill: true,
            backgroundColor: 'rgba(54, 162, 235, 0.2)',
            borderColor: 'rgba(54, 162, 235, 1)',
            pointBackgroundColor: 'rgba(54, 162, 235, 1)',
            pointBorderColor: '#fff',
            pointHoverBackgroundColor: '#fff',
            pointHoverBorderColor: 'rgba(54, 162, 235, 1)'
        }]
    };

    try {
        // 處理標籤
        if (data.labels && Array.isArray(data.labels)) {
            processedData.labels = data.labels;
        }
        
        // 處理數據集
        const sourceDatasets = data.datasets || [];
        if (sourceDatasets.length > 0) {
            processedData.datasets = sourceDatasets;
        } else if (Array.isArray(data.data)) {
            processedData.datasets[0].data = data.data;
            
            // 如果沒有標籤但有數據，生成數字標籤
            if (processedData.labels.length === 0 && data.data.length > 0) {
                processedData.labels = Array.from({ length: data.data.length }, (_, i) => `維度 ${i + 1}`);
            }
        }
        
        // 確保至少有一個數據集
        if (processedData.datasets.length === 0 || processedData.datasets[0].data.length === 0) {
            processedData.labels = ['速度', '耐力', '力量', '敏捷', '技巧'];
            processedData.datasets[0].data = [65, 59, 90, 81, 56];
        }
        
        // 確保有標籤且數量一致
        if (processedData.labels.length === 0 && processedData.datasets[0].data.length > 0) {
            processedData.labels = Array.from(
                { length: processedData.datasets[0].data.length }, 
                (_, i) => `維度 ${i + 1}`
            );
        } else if (processedData.labels.length < processedData.datasets[0].data.length) {
            // 補充標籤
            const additionalLabels = Array.from(
                { length: processedData.datasets[0].data.length - processedData.labels.length }, 
                (_, i) => `維度 ${processedData.labels.length + i + 1}`
            );
            processedData.labels = [...processedData.labels, ...additionalLabels];
        }
    } catch (error) {
        console.error('處理雷達圖資料時出錯:', error);
        
        // 生成範例資料
        processedData.labels = ['速度', '耐力', '力量', '敏捷', '技巧'];
        processedData.datasets[0].data = [65, 59, 90, 81, 56];
    }

    return processedData;
}

// 處理散點圖資料
function processScatterData(data) {
    const processedData = {
        datasets: [{
            label: '數值',
            data: [],
            backgroundColor: 'rgba(75, 192, 192, 0.6)',
            borderColor: 'rgba(75, 192, 192, 1)',
            pointRadius: 6
        }]
    };

    try {
        // 處理數據集
        const sourceDatasets = data.datasets || [];
        if (sourceDatasets.length > 0) {
            processedData.datasets = sourceDatasets.map(dataset => ({
                ...dataset,
                pointRadius: dataset.pointRadius || 6
            }));
        } else if (Array.isArray(data.data)) {
            // 檢查是否為有效的散點圖數據
            const isValidScatterData = data.data.every(item => 
                typeof item === 'object' && 
                (item.x !== undefined || item.y !== undefined)
            );
            
            if (isValidScatterData) {
                processedData.datasets[0].data = data.data;
            } else {
                // 如果不是有效的散點圖數據，則轉換
                processedData.datasets[0].data = data.data.map((val, idx) => ({
                    x: idx,
                    y: val
                }));
            }
        }
        
        // 確保至少有一個數據集
        if (processedData.datasets.length === 0 || processedData.datasets[0].data.length === 0) {
            // 生成範例資料
            processedData.datasets[0].data = Array(10).fill(0).map(() => ({
                x: Math.random() * 100,
                y: Math.random() * 100
            }));
        }
    } catch (error) {
        console.error('處理散點圖資料時出錯:', error);
        
        // 生成範例資料
        processedData.datasets[0].data = Array(10).fill(0).map(() => ({
            x: Math.random() * 100,
            y: Math.random() * 100
        }));
    }

    return processedData;
}

// 處理氣泡圖資料
function processBubbleData(data) {
    const processedData = {
        datasets: [{
            label: '數值',
            data: [],
            backgroundColor: 'rgba(75, 192, 192, 0.6)',
            borderColor: 'rgba(75, 192, 192, 1)'
        }]
    };

    try {
        // 處理數據集
        const sourceDatasets = data.datasets || [];
        if (sourceDatasets.length > 0) {
            processedData.datasets = sourceDatasets;
        } else if (Array.isArray(data.data)) {
            // 檢查是否為有效的氣泡圖數據
            const isValidBubbleData = data.data.every(item => 
                typeof item === 'object' && 
                (item.x !== undefined || item.y !== undefined)
            );
            
            if (isValidBubbleData) {
                // 確保所有點都有 r 屬性
                processedData.datasets[0].data = data.data.map(item => ({
                    x: item.x,
                    y: item.y,
                    r: item.r || Math.floor(Math.random() * 15) + 5
                }));
            } else {
                // 如果不是有效的氣泡圖數據，則轉換
                processedData.datasets[0].data = data.data.map((val, idx) => ({
                    x: idx,
                    y: val,
                    r: Math.floor(Math.random() * 15) + 5
                }));
            }
        }
        
        // 確保至少有一個數據集
        if (processedData.datasets.length === 0 || processedData.datasets[0].data.length === 0) {
            // 生成範例資料
            processedData.datasets[0].data = Array(10).fill(0).map(() => ({
                x: Math.random() * 100,
                y: Math.random() * 100,
                r: Math.floor(Math.random() * 15) + 5
            }));
        }
    } catch (error) {
        console.error('處理氣泡圖資料時出錯:', error);
        
        // 生成範例資料
        processedData.datasets[0].data = Array(10).fill(0).map(() => ({
            x: Math.random() * 100,
            y: Math.random() * 100,
            r: Math.floor(Math.random() * 15) + 5
        }));
    }

    return processedData;
}

/**
 * 處理圖表資料
 * @param {Object} data - 原始資料
 * @returns {Object} 處理後的資料
 */
function processChartData(data) {
    if (!data) return null;

    const chartData = {
        datasets: []
    };

    if (Array.isArray(data)) {
        // 如果是陣列，假設是單一資料集
        chartData.datasets.push({
            data: data
        });
    } else if (data.datasets) {
        // 如果有 datasets 屬性
        chartData.datasets = data.datasets;
    } else if (data.data) {
        // 如果有 data 屬性
        chartData.datasets.push({
            data: data.data
        });
    }

    return chartData;
}

// 如果 detectTimeUnit 未定義，提供基本實現
function setupDetectTimeUnit() {
    if (typeof detectTimeUnit !== 'function') {
        window.detectTimeUnit = function(data) {
            if (!Array.isArray(data) || data.length < 2) {
                return 'day';
            }
    
            const timeDiff = data[1].t - data[0].t;
            if (timeDiff < 60000) return 'second';
            if (timeDiff < 3600000) return 'minute';
            if (timeDiff < 86400000) return 'hour';
            if (timeDiff < 604800000) return 'day';
            if (timeDiff < 2592000000) return 'week';
            if (timeDiff < 31536000000) return 'month';
            return 'year';
        };
    }
}

// 確保檢測時間單位函數已設置
setupDetectTimeUnit();

/**
 * 將圖表匯出為圖片檔
 * @param {string} format - 圖片格式，如 'image/png', 'image/webp'
 * @param {object} appState - 應用狀態
 */
export function captureChart(format = 'image/png', appState) {
    if (!appState.myChart) {
        showError('無圖表可供匯出');
        return;
    }
    
    try {
        // 獲取圖表的 base64 編碼的資料 URL
        const dataURL = appState.myChart.toBase64Image(format);
        
        // 創建一個隱藏的下載連結元素
        const link = document.createElement('a');
        link.href = dataURL;
        link.download = `chart-${new Date().toISOString().slice(0, 19).replace(/[:.]/g, '-')}.${format.split('/')[1]}`;
        
        // 觸發下載
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        console.log(`已匯出圖表為 ${format} 格式`);
    } catch (error) {
        console.error('匯出圖表錯誤:', error);
        showError('匯出圖表失敗');
    }
}
