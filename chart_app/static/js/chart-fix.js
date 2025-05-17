/**
 * Chart.js 特殊圖表類型和渲染問題修復腳本
 * 用於確保金融圖表和極座標圖等特殊圖表能正常渲染，並解決圖表銷毀和日期適配器問題
 */

(function() {
    console.log('載入 Chart.js 修復腳本');
    
    // 等待 Chart.js 載入完成
    function waitForChartJs(callback, maxAttempts = 20, interval = 200) {
        let attempts = 0;
        
        const checkChartJs = function() {
            attempts++;
            if (typeof Chart !== 'undefined') {
                console.log('找到 Chart.js，版本:', Chart.version);
                callback();
                return;
            } else if (attempts >= maxAttempts) {
                console.error('等待 Chart.js 載入超時');
                return;
            }
            
            setTimeout(checkChartJs, interval);
        };
        
        checkChartJs();
    }
    
    // 修復圖表佈局問題
    function fixChartLayout() {
        if (typeof Chart === 'undefined' || !Chart.prototype) return;
        
        console.log('修復圖表佈局...');
        
        // 修復 padding 未定義的問題
        try {
            // 確保所有圖表元素初始化時都有有效的 padding
            const originalUpdateLayout = Chart.layouts && Chart.layouts.update;
            if (originalUpdateLayout) {
                Chart.layouts.update = function(chart, width, height) {
                    try {
                        // 確保所有盒子都有 padding
                        if (chart.boxes && Array.isArray(chart.boxes)) {
                            chart.boxes.forEach(box => {
                                if (box && !box._padding) {
                                    box._padding = { top: 0, left: 0, right: 0, bottom: 0 };
                                }
                            });
                        }
                        
                        return originalUpdateLayout.call(this, chart, width, height);
                    } catch (e) {
                        console.error('佈局更新錯誤:', e);
                    }
                };
                console.log('已修復佈局更新函數');
            }
            
            // 修復位置錯誤
            if (Chart.Tooltip && Chart.Tooltip.positioners) {
                // 保存所有原始定位器
                const originalPositioners = Object.assign({}, Chart.Tooltip.positioners);
                
                // 創建安全的定位器包裝器
                Object.keys(originalPositioners).forEach(key => {
                    const originalPositioner = originalPositioners[key];
                    Chart.Tooltip.positioners[key] = function(...args) {
                        try {
                            return originalPositioner.apply(this, args);
                        } catch (e) {
                            console.warn(`Tooltip 位置計算 '${key}' 失敗:`, e.message);
                            // 回退到視窗中央
                            return {
                                x: window.innerWidth / 2,
                                y: window.innerHeight / 2
                            };
                        }
                    };
                });
                
                // 添加 fallback 定定位器
                Chart.Tooltip.positioners.fallback = function(items, eventPosition) {
                    if (!eventPosition) {
                        return {
                            x: window.innerWidth / 2,
                            y: window.innerHeight / 2
                        };
                    }
                    return {
                        x: eventPosition.x,
                        y: eventPosition.y
                    };
                };
                
                console.log('已修復 Tooltip 定位器');
            }
        } catch (e) {
            console.error('修復佈局系統時出錯:', e);
        }
    }
    
    // 修復圖表銷毀問題
    function fixChartDestroy() {
        if (typeof Chart === 'undefined' || !Chart.prototype) return;
        
        // 保存對原始方法的引用
        const originalDestroy = Chart.prototype.destroy;
        
        // 增強版銷毀方法
        Chart.prototype.destroy = function() {
            try {
                console.log(`增強版銷毀方法被調用，圖表ID: ${this.id || 'unknown'}`);
                
                const canvasId = this.canvas ? this.canvas.id : 'unknown';
                const chartId = this.id || 'unknown';
                
                // 確保存在有效的 canvas
                if (this.canvas) {
                    // 清理所有事件監聽器
                    const events = ['click', 'mousemove', 'mouseout', 'mouseenter', 'mouseleave', 'touchstart', 'touchmove', 'touchend'];
                    events.forEach(eventType => {
                        try {
                            // 使用 cloneNode(false) 來移除所有事件監聽器
                            // 但保留 DOM 屬性
                            const parent = this.canvas.parentNode;
                            if (parent) {
                                const newCanvas = this.canvas.cloneNode(false);
                                parent.replaceChild(newCanvas, this.canvas);
                                
                                // 將新畫布引用存回實例
                                this.canvas = newCanvas;
                                
                                // 重新獲取 2D 上下文
                                this.ctx = newCanvas.getContext('2d');
                            }
                        } catch (e) {
                            console.warn(`清理事件過程中出錯: ${e.message}`);
                        }
                    });
                    
                    // 清除畫布
                    try {
                        const ctx = this.canvas.getContext('2d');
                        if (ctx) {
                            ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
                        }
                    } catch (e) {
                        console.warn(`清理畫布時出錯: ${e.message}`);
                    }
                }
                
                // 停止所有動畫
                if (typeof this.stop === 'function') {
                    this.stop();
                }
                
                // 斷開數據引用
                if (this.data) {
                    if (this.data.datasets) {
                        this.data.datasets.length = 0;
                    }
                    this.data = null;
                }
                
                // 調用原始銷毀方法
                originalDestroy.apply(this, arguments);
                
                // 確保在全局實例註冊表中刪除實例
                if (Chart.instances) {
                    if (this.id) {
                        delete Chart.instances[this.id];
                    }
                    
                    // 查找並清除任何相同畫布的圖表實例
                    if (this.canvas && this.canvas.id) {
                        Object.keys(Chart.instances).forEach(instanceId => {
                            const instance = Chart.instances[instanceId];
                            if (instance && instance.canvas && instance.canvas.id === this.canvas.id) {
                                delete Chart.instances[instanceId];
                            }
                        });
                    }
                }
                
                console.log(`圖表實例已完全銷毀 (ID: ${chartId}, Canvas: ${canvasId})`);
            } catch (e) {
                console.error('增強銷毀方法出錯:', e);
                
                // 如果增強銷毀失敗，嘗試調用原始銷毀方法
                try {
                    originalDestroy.apply(this, arguments);
                } catch (innerError) {
                    console.error('原始銷毀方法也失敗:', innerError);
                    
                    // 最後的清理嘗試
                    try {
                        if (this.canvas && typeof this.canvas.getContext === 'function') {
                            const ctx = this.canvas.getContext('2d');
                            if (ctx) {
                                ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
                            }
                        }
                        
                        // 清除實例引用
                        if (Chart.instances && this.id) {
                            delete Chart.instances[this.id];
                        }
                    } catch (finalError) {
                        console.error('最終清理嘗試失敗:', finalError);
                    }
                }
            }
        };
        console.log('已增強 Chart.js 的銷毀方法');
    }
    
    // 註冊特殊圖表類型
    function registerSpecialChartTypes() {
        if (typeof Chart === 'undefined') {
            console.error('Chart.js 未載入，無法註冊特殊圖表類型');
            return;
        }
        
        try {
            console.log('嘗試註冊特殊圖表類型');
            
            // 註冊極座標圖
            if (!Chart.controllers.polarArea) {
                if (Chart.PolarAreaController) {
                    Chart.register(Chart.PolarAreaController);
                    console.log('成功註冊 PolarAreaController');
                } else {
                    console.warn('找不到 PolarAreaController');
                }
            }
            
            // 檢查金融圖表擴展是否已載入
            const hasFinancialExtension = typeof window.CandlestickController !== 'undefined' || 
                (window.Chart && window.Chart.controllers && window.Chart.controllers.financial);
            
            if (!hasFinancialExtension) {
                console.warn('未找到金融圖表擴展，嘗試動態載入');
                
                // 動態載入金融圖表擴展
                const script = document.createElement('script');
                script.src = 'https://cdn.jsdelivr.net/npm/chartjs-chart-financial@0.1.1/dist/chartjs-chart-financial.min.js';
                script.onload = function() {
                    console.log('金融圖表擴展已動態載入');
                    registerFinancialControllers();
                };
                script.onerror = function() {
                    console.error('金融圖表擴展載入失敗');
                };
                document.head.appendChild(script);
            } else {
                registerFinancialControllers();
            }
            
        } catch (error) {
            console.error('註冊特殊圖表類型時出錯:', error);
        }
    }
    
    // 註冊金融圖表控制器
    function registerFinancialControllers() {
        try {
            // 註冊蠟燭圖控制器
            if (!Chart.controllers.candlestick) {
                if (window.CandlestickController) {
                    Chart.register(window.CandlestickController);
                    console.log('已註冊 CandlestickController');
                } else if (window.Chart && window.Chart.controllers && window.Chart.controllers.financial && 
                          window.Chart.controllers.financial.CandlestickController) {
                    Chart.register(window.Chart.controllers.financial.CandlestickController);
                    console.log('已從 financial 套件註冊 CandlestickController');
                } else {
                    console.warn('找不到 CandlestickController');
                }
            }
            
            // 註冊 OHLC 控制器
            if (!Chart.controllers.ohlc) {
                if (window.OhlcController) {
                    Chart.register(window.OhlcController);
                    console.log('已註冊 OhlcController');
                } else if (window.Chart && window.Chart.controllers && window.Chart.controllers.financial && 
                          window.Chart.controllers.financial.OhlcController) {
                    Chart.register(window.Chart.controllers.financial.OhlcController);
                    console.log('已從 financial 套件註冊 OhlcController');
                } else {
                    console.warn('找不到 OhlcController');
                }
            }
            
            // 檢查控制器是否已註冊
            console.log('已註冊的控制器:', Object.keys(Chart.controllers || {}));
            
            // 添加全局混合設定，增強金融圖表處理
            Chart.defaults.set('elements.candlestick', {
                color: {
                    up: 'rgba(75, 192, 75, 1)',
                    down: 'rgba(255, 99, 132, 1)',
                    unchanged: 'rgba(160, 160, 160, 1)'
                }
            });
            
            Chart.defaults.set('elements.ohlc', {
                color: {
                    up: 'rgba(75, 192, 75, 1)',
                    down: 'rgba(255, 99, 132, 1)',
                    unchanged: 'rgba(160, 160, 160, 1)'
                }
            });
            
        } catch (error) {
            console.error('註冊金融圖表控制器時出錯:', error);
        }
    }
    
    // 修復日期適配器問題
    function fixDateAdapter() {
        if (typeof Chart === 'undefined') return;
        
        // 檢查日期適配器是否已正確載入
        const hasDateAdapter = Chart.adapters && 
                              Chart.adapters._date && 
                              typeof Chart.adapters._date.add === 'function';
        
        if (hasDateAdapter) {
            console.log('日期適配器檢查: 已正確載入');
            return;
        }
        
        console.warn('日期適配器檢查: 發現問題，嘗試修復');
        
        // 如果 Luxon 已載入但適配器有問題，嘗試手動註冊
        if (typeof luxon !== 'undefined') {
            try {
                Chart.register({
                    id: 'fixedLuxonAdapter',
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
                console.log('已手動註冊修復版日期適配器');
            } catch (error) {
                console.error('日期適配器修復失敗:', error);
                loadExternalAdapter();
            }
        } else {
            // 如果 Luxon 未載入，先載入它
            loadExternalAdapter();
        }
    }
    
    // 載入外部適配器
    function loadExternalAdapter() {
        console.log('嘗試載入外部日期適配器...');
        
        // 如果需要載入 Luxon
        if (typeof luxon === 'undefined') {
            const luxonScript = document.createElement('script');
            luxonScript.src = 'https://cdn.jsdelivr.net/npm/luxon@3.2.1/build/global/luxon.min.js';
            luxonScript.onload = function() {
                console.log('Luxon 載入成功');
                
                // 然後載入適配器
                const adapterScript = document.createElement('script');
                adapterScript.src = 'https://cdn.jsdelivr.net/npm/chartjs-adapter-luxon@1.3.0/dist/chartjs-adapter-luxon.min.js';
                adapterScript.onload = function() {
                    console.log('Luxon 適配器載入成功');
                };
                document.head.appendChild(adapterScript);
            };
            document.head.appendChild(luxonScript);
        } else {
            // 只載入適配器
            const adapterScript = document.createElement('script');
            adapterScript.src = 'https://cdn.jsdelivr.net/npm/chartjs-adapter-luxon@1.3.0/dist/chartjs-adapter-luxon.min.js';
            adapterScript.onload = function() {
                console.log('Luxon 適配器載入成功');
            };
            document.head.appendChild(adapterScript);
        }
    }
    
    // 在文檔載入完成後執行
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            waitForChartJs(function() {
                registerSpecialChartTypes();
                fixSpecialChartTypes();  // 修復特殊圖表類型
                fixChartDestroy();
                fixDateAdapter();
            });
        });
    } else {
        waitForChartJs(function() {
            registerSpecialChartTypes();
            fixChartLayout();  // 先修復佈局問題
            fixSpecialChartTypes();  // 修復特殊圖表類型
            fixChartDestroy();
            fixDateAdapter();
        });
    }
    
    // 設置金融圖表偵測
    function setupFinancialChartDetection() {
        document.addEventListener('DOMContentLoaded', function() {
            const buttonContainer = document.querySelector('.chart-type-buttons');
            if (buttonContainer) {
                buttonContainer.addEventListener('click', function(event) {
                    if (event.target.tagName === 'BUTTON') {
                        const chartType = event.target.dataset.type;
                        if (['candlestick', 'ohlc'].includes(chartType)) {
                            console.log('檢測到金融圖表選擇:', chartType);
                            registerFinancialControllers();
                        }
                    }
                });
            }
        });
    }
    
    // 啟動金融圖表偵測
    setupFinancialChartDetection();
    
    // 修復特殊圖表類型問題
    function fixSpecialChartTypes() {
        console.log('修復特殊圖表類型...');
        
        // 1. 修復蝴蝶圖處理
        if (typeof window.processButterFlyData !== 'function') {
            console.warn('未找到蝴蝶圖處理函數，正在提供默認實現');
            
            // 提供默認的處理函數
            window.processButterFlyData = function(data) {
                console.log('使用默認的蝴蝶圖處理函數');
                
                // 規範化數據格式
                let chartData = {
                    labels: [],
                    datasets: []
                };
                
                try {
                    // 嘗試獲取標籤
                    if (data.labels) {
                        chartData.labels = [...data.labels];
                    } else if (data.data && data.data.labels) {
                        chartData.labels = [...data.data.labels];
                    } else {
                        chartData.labels = ['類別1', '類別2', '類別3', '類別4', '類別5'];
                    }
                    
                    // 嘗試獲取數據集
                    let dataSets = [];
                    if (data.datasets && Array.isArray(data.datasets)) {
                        dataSets = data.datasets;
                    } else if (data.data && data.data.datasets && Array.isArray(data.data.datasets)) {
                        dataSets = data.data.datasets;
                    }
                    
                    // 確保我們有兩個數據集（蝴蝶圖需要兩個）
                    if (dataSets.length >= 2) {
                        // 複製前兩個數據集
                        const firstSet = { ...dataSets[0] };
                        const secondSet = { ...dataSets[1] };
                        
                        // 確保第二個數據集是負數（蝴蝶圖效果）
                        if (Array.isArray(secondSet.data)) {
                            secondSet.data = secondSet.data.map(val => -Math.abs(Number(val || 0)));
                        }
                        
                        chartData.datasets.push(firstSet, secondSet);
                    } else if (dataSets.length === 1) {
                        // 只有一個數據集時，複製它並創建對稱數據
                        const firstSet = { ...dataSets[0] };
                        const secondSet = { ...dataSets[0] };
                        
                        secondSet.label = secondSet.label ? `${secondSet.label} (反向)` : '反向數據';
                        secondSet.backgroundColor = 'rgba(255, 99, 132, 0.6)';
                        secondSet.borderColor = 'rgba(255, 99, 132, 1)';
                        
                        if (Array.isArray(secondSet.data)) {
                            secondSet.data = secondSet.data.map(val => -Math.abs(Number(val || 0)));
                        }
                        
                        chartData.datasets.push(firstSet, secondSet);
                    } else {
                        // 沒有數據集時創建示例數據
                        chartData.datasets = [
                            {
                                label: '組別 A',
                                backgroundColor: 'rgba(54, 162, 235, 0.6)',
                                borderColor: 'rgba(54, 162, 235, 1)',
                                borderWidth: 1,
                                data: [65, 59, 80, 81, 56]
                            },
                            {
                                label: '組別 B',
                                backgroundColor: 'rgba(255, 99, 132, 0.6)',
                                borderColor: 'rgba(255, 99, 132, 1)',
                                borderWidth: 1,
                                data: [-45, -50, -60, -35, -30]
                            }
                        ];
                    }
                } catch (error) {
                    console.error('處理蝴蝶圖數據時出錯:', error);
                    
                    // 返回預設數據
                    chartData = {
                        labels: ['類別1', '類別2', '類別3', '類別4', '類別5'],
                        datasets: [
                            {
                                label: '組別 A',
                                backgroundColor: 'rgba(54, 162, 235, 0.6)',
                                borderColor: 'rgba(54, 162, 235, 1)',
                                borderWidth: 1,
                                data: [65, 59, 80, 81, 56]
                            },
                            {
                                label: '組別 B',
                                backgroundColor: 'rgba(255, 99, 132, 0.6)',
                                borderColor: 'rgba(255, 99, 132, 1)',
                                borderWidth: 1,
                                data: [-45, -50, -60, -35, -30]
                            }
                        ]
                    };
                }
                
                return chartData;
            };
        }
        
        // 2. 確保桑基圖控制器註冊
        if (typeof Chart !== 'undefined' && !Chart.controllers.sankey) {
            console.log('未找到桑基圖控制器，嘗試初始化...');
            if (typeof window.initChartExtensions === 'function') {
                try {
                    window.initChartExtensions();
                    console.log('已初始化圖表擴展');
                } catch (e) {
                    console.error('初始化圖表擴展時出錯:', e);
                }
            }
        }
    }

    // 修復所有已知的圖表問題
    function applyAllFixes() {
        try {
            fixChartLayout();
            fixSpecialChartTypes();
            console.log('所有圖表修復已套用');
        } catch (e) {
            console.error('套用圖表修復時出錯:', e);
        }
    }

    // 當 Chart.js 載入完成後套用修復
    waitForChartJs(applyAllFixes);
    
    // 暴露全局方法以便其他腳本調用
    window.chartFix = {
        registerSpecialChartTypes: registerSpecialChartTypes,
        registerFinancialControllers: registerFinancialControllers,
        fixDateAdapter: fixDateAdapter,
        fixChartDestroy: fixChartDestroy
    };
})();
