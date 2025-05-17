/**
 * Chart.js 安全包裝器
 * 整合所有修復並提供安全的圖表創建、更新和刪除功能
 */

(function() {
    console.log('載入圖表安全包裝器');

    // 等待 DOM 和 Chart.js 載入完成
    document.addEventListener('DOMContentLoaded', function() {
        console.log('DOM 已載入，初始化圖表安全包裝器');
        
        // 等待 Chart.js 加載完成
        waitForChartJs(function() {
            initializeChartSafety();
        });
    });
    
    // 等待 Chart.js 加載
    function waitForChartJs(callback, attempts = 0) {
        if (typeof Chart !== 'undefined') {
            console.log('Chart.js 已載入，版本:', Chart.version);
            callback();
            return;
        }
        
        if (attempts > 20) {
            console.error('Chart.js 載入超時');
            return;
        }
        
        console.log(`等待 Chart.js 載入... (${attempts}/20)`);
        setTimeout(function() {
            waitForChartJs(callback, attempts + 1);
        }, 200);
    }
    
    // 初始化圖表安全機制
    function initializeChartSafety() {
        // 確保 Chart.js 已經可用
        if (typeof Chart === 'undefined') {
            console.error('無法初始化圖表安全包裝器: Chart.js 未載入');
            return;
        }
        
        console.log('初始化圖表安全機制');
        
        // 1. 增強 Chart.js 的錯誤處理能力
        enhanceChartErrorHandling();
        
        // 2. 創建安全的圖表渲染函數
        createSafeRenderFunction();
        
        // 3. 修復所有常見問題
        applyChartFixes();
        
        // 4. 創建全局代理
        createChartProxy();
        
        console.log('圖表安全包裝器初始化完成');
    }
    
    // 增強 Chart.js 的錯誤處理能力
    function enhanceChartErrorHandling() {
        try {
            // 修復圖表構造函數
            const originalChartConstructor = Chart;
            window.Chart = function(canvas, config) {
                try {
                    // 檢查是否傳入的是 CanvasRenderingContext2D 而不是 Canvas 元素
                    if (canvas && canvas instanceof CanvasRenderingContext2D) {
                        console.warn('傳入的是 CanvasRenderingContext2D，正在獲取關聯的 Canvas 元素');
                        canvas = canvas.canvas;
                    }
                    
                    // 檢查畫布元素
                    if (!canvas || (!canvas.getContext && typeof canvas !== 'string')) {
                        console.error('無效的畫布元素:', canvas);
                        return createDummyChart(null);
                    }
                    
                    // 如果是字符串ID，獲取實際的畫布元素
                    if (typeof canvas === 'string') {
                        const canvasElement = document.getElementById(canvas);
                        if (!canvasElement) {
                            console.error(`找不到ID為 "${canvas}" 的畫布元素`);
                            return createDummyChart(null);
                        }
                        canvas = canvasElement;
                    }
                    
                    // 檢查畫布元素的有效性
                    if (!canvas.getContext) {
                        console.error('所提供的元素不是有效的畫布:', canvas);
                        return createDummyChart(canvas);
                    }
                    
                    // 確保畫布大小合理
                    if (canvas.width <= 0 || canvas.height <= 0) {
                        console.warn('畫布大小為零，調整為默認大小');
                        canvas.width = canvas.width || 200;
                        canvas.height = canvas.height || 200;
                    }
                    
                    // 應用安全配置
                    config = applyConfigSafety(config);
                    
                    // 檢查圖表類型
                    if (config.type && !Chart.controllers[config.type]) {
                        console.warn(`未知的圖表類型 "${config.type}"，回退到 "line"`);
                        config.type = 'line';
                    }
                    
                    // 調用原始構造函數
                    return new originalChartConstructor(canvas, config);
                } catch (e) {
                    console.error('創建圖表時出錯:', e);
                    logCanvasState(canvas);
                    
                    // 顯示友好的錯誤訊息
                    showErrorOnCanvas(canvas, e);
                    
                    // 返回一個無功能的假圖表對象，避免進一步的錯誤
                    return createDummyChart(canvas);
                }
            };
            
            // 複製原始 Chart 的所有屬性
            for (const key in originalChartConstructor) {
                if (originalChartConstructor.hasOwnProperty(key)) {
                    Chart[key] = originalChartConstructor[key];
                }
            }
            
            // 創建安全版本的 getChart 方法
            const originalGetChart = Chart.getChart;
            Chart.getChart = function(canvas) {
                try {
                    return originalGetChart(canvas);
                } catch (e) {
                    console.warn('獲取圖表實例時出錯:', e);
                    return null;
                }
            };
            
            console.log('已增強 Chart.js 錯誤處理能力');
        } catch (e) {
            console.error('增強 Chart.js 錯誤處理時出錯:', e);
        }
    }
    
    // 創建安全的渲染函數
    function createSafeRenderFunction() {
        // 暴露全局安全渲染函數
        window.safeRenderChart = function(config, canvasId) {
            console.log('使用安全渲染函數創建圖表');
            
            try {
                // 獲取畫布
                const canvas = typeof canvasId === 'string' ? 
                    document.getElementById(canvasId) : 
                    canvasId;
                
                if (!canvas) {
                    console.error('找不到畫布元素:', canvasId);
                    return null;
                }
                
                // 清理現有圖表
                const existingChart = Chart.getChart(canvas);
                if (existingChart) {
                    try {
                        console.log('銷毀現有圖表:', existingChart.id);
                        existingChart.destroy();
                    } catch (e) {
                        console.warn('銷毀現有圖表時出錯:', e);
                        // 強制清理畫布
                        const ctx = canvas.getContext('2d');
                        if (ctx) {
                            ctx.clearRect(0, 0, canvas.width, canvas.height);
                        }
                    }
                }
                
                // 確保配置安全
                const safeConfig = applyConfigSafety(config);
                
                // 創建新圖表
                console.log('創建新圖表, 類型:', safeConfig.type);
                return new Chart(canvas, safeConfig);
            } catch (e) {
                console.error('安全渲染圖表時出錯:', e);
                return null;
            }
        };
        
        console.log('已創建安全圖表渲染函數');
    }
    
    // 應用所有修復
    function applyChartFixes() {
        try {
            // 如果修復函數存在，調用它們
            if (window.chartFix) {
                if (typeof window.chartFix.fixDateAdapter === 'function') {
                    window.chartFix.fixDateAdapter();
                }
                
                if (typeof window.chartFix.fixChartDestroy === 'function') {
                    window.chartFix.fixChartDestroy();
                }
            }
            
            // 修復默認配置
            fixDefaultConfigs();
            
            console.log('已應用所有圖表修復');
        } catch (e) {
            console.error('應用圖表修復時出錯:', e);
        }
    }
    
    // 創建圖表代理
    function createChartProxy() {
        // 導出安全的圖表API
        window.safeChartApi = {
            create: window.safeRenderChart,
            getChart: function(canvasId) {
                try {
                    const canvas = typeof canvasId === 'string' ? 
                        document.getElementById(canvasId) : 
                        canvasId;
                    return Chart.getChart(canvas);
                } catch (e) {
                    console.warn('獲取圖表時出錯:', e);
                    return null;
                }
            },
            destroy: function(chartOrCanvasId) {
                try {
                    let chart;
                    
                    // 如果傳入的是 Canvas ID 或元素
                    if (typeof chartOrCanvasId === 'string' || chartOrCanvasId instanceof HTMLCanvasElement) {
                        const canvas = typeof chartOrCanvasId === 'string' ? 
                            document.getElementById(chartOrCanvasId) : 
                            chartOrCanvasId;
                        
                        chart = Chart.getChart(canvas);
                    } else {
                        chart = chartOrCanvasId;
                    }
                    
                    if (chart && typeof chart.destroy === 'function') {
                        chart.destroy();
                        return true;
                    }
                } catch (e) {
                    console.warn('安全銷毀圖表時出錯:', e);
                    
                    // 嘗試清理畫布
                    try {
                        const canvas = 
                            (typeof chartOrCanvasId === 'string') ? document.getElementById(chartOrCanvasId) :
                            (chartOrCanvasId instanceof HTMLCanvasElement) ? chartOrCanvasId :
                            (chartOrCanvasId && chartOrCanvasId.canvas) ? chartOrCanvasId.canvas :
                            null;
                        
                        if (canvas) {
                            const ctx = canvas.getContext('2d');
                            ctx.clearRect(0, 0, canvas.width, canvas.height);
                        }
                    } catch (cleanupError) {
                        console.error('清理畫布時出錯:', cleanupError);
                    }
                }
                
                return false;
            },
            update: function(chart) {
                if (!chart) return false;
                
                try {
                    if (typeof chart.update === 'function') {
                        chart.update();
                        return true;
                    }
                } catch (e) {
                    console.warn('更新圖表時出錯:', e);
                }
                
                return false;
            }
        };
        
        console.log('已創建安全圖表API');
    }
    
    // 輔助函數
    
    // 應用配置安全性
    function applyConfigSafety(config) {
        if (!config) config = {};
        
        // 確保基本屬性存在
        if (!config.type) config.type = 'line'; // 默認為線圖
        if (!config.data) config.data = {};
        if (!config.data.datasets) config.data.datasets = [];
        if (!config.options) config.options = {};
        if (!config.options.plugins) config.options.plugins = {};
        
        // 確保選項和插件配置安全
        ensureOptionsSafety(config.options);
        
        // 確保數據集安全
        ensureDatasetsSafety(config.data.datasets);
        
        // 添加安全的錯誤處理機制
        addErrorHandlers(config);
        
        // 確保圖例位置有效
        if (config.options.plugins.legend) {
            const validPositions = ['top', 'left', 'bottom', 'right', 'chartArea'];
            if (!validPositions.includes(config.options.plugins.legend.position)) {
                config.options.plugins.legend.position = 'top';
            }
        }
        
        // 確保動畫設置正確
        if (config.options.animation) {
            config.options.animation.duration = Math.min(
                config.options.animation.duration || 1000, 
                2000
            ); // 限制動畫時間
        }
        
        // 備份原始配置的重要部分
        const originalType = config.type || 'bar';
        
        // 添加全局錯誤處理
        const originalOnError = config.options.onError;
        config.options.onError = function(err) {
            console.error('圖表錯誤:', err);
            
            // 調用原始錯誤處理函數
            if (typeof originalOnError === 'function') {
                originalOnError(err);
            }
        };
        
        return config;
    }
    
    // 修復默認配置
    function fixDefaultConfigs() {
        if (!Chart.defaults) return;
        
        // 確保圖例位置正確
        if (Chart.defaults.plugins && Chart.defaults.plugins.legend) {
            const validPositions = ['top', 'left', 'bottom', 'right', 'chartArea'];
            const position = Chart.defaults.plugins.legend.position;
            
            if (!validPositions.includes(position)) {
                console.log(`修復: 將默認圖例位置從 "${position}" 改為 "top"`);
                Chart.defaults.plugins.legend.position = 'top';
            }
        }
        
        // 全局設置合理的動畫時間
        if (Chart.defaults.animation) {
            Chart.defaults.animation.duration = Math.min(
                Chart.defaults.animation.duration || 1000, 
                2000
            );
        }
        
        console.log('已修復默認配置');
    }
    
    // 確保選項配置安全
    function ensureOptionsSafety(options) {
        // 處理常見的錯誤點
        
        // 1. 確保響應式選項安全
        if (!options.responsive) {
            options.responsive = true; // 默認啟用響應式
        }
        
        // 2. 確保圖例配置安全
        if (!options.plugins.legend) {
            options.plugins.legend = {};
        }
        
        // 確保圖例位置有效
        const validLegendPositions = ['top', 'left', 'bottom', 'right', 'chartArea'];
        if (!validLegendPositions.includes(options.plugins.legend.position)) {
            options.plugins.legend.position = 'top';
        }
        
        // 3. 確保提示工具配置安全
        if (!options.plugins.tooltip) {
            options.plugins.tooltip = {};
        }
        
        // 確保提示工具定位器安全
        if (options.plugins.tooltip.position && typeof options.plugins.tooltip.position === 'string') {
            const validTooltipPositioners = ['average', 'nearest', 'cursor'];
            if (!validTooltipPositioners.includes(options.plugins.tooltip.position)) {
                options.plugins.tooltip.position = 'nearest';
            }
        }
        
        // 4. 確保動畫配置安全
        if (!options.animation) {
            options.animation = {};
        }
        
        // 5. 確保佈局配置安全
        if (!options.layout) {
            options.layout = {};
        }
        
        if (!options.layout.padding) {
            options.layout.padding = {
                top: 0,
                right: 0,
                bottom: 0,
                left: 0
            };
        } else if (typeof options.layout.padding === 'number') {
            const padding = options.layout.padding;
            options.layout.padding = {
                top: padding,
                right: padding,
                bottom: padding,
                left: padding
            };
        }
        
        return options;
    }
    
    // 確保數據集安全
    function ensureDatasetsSafety(datasets) {
        if (!datasets || !Array.isArray(datasets)) {
            return [];
        }
        
        // 處理每個數據集
        return datasets.map((dataset, index) => {
            if (!dataset) {
                return { data: [] };
            }
            
            // 確保數據存在
            if (!dataset.data) {
                dataset.data = [];
            }
            
            // 處理金融圖表數據格式
            if (['candlestick', 'ohlc'].includes(dataset.type)) {
                dataset.data = dataset.data.map(item => {
                    // 確保財務數據點有所有必需的屬性
                    if (typeof item === 'object') {
                        if (item.o === undefined) item.o = 0;
                        if (item.h === undefined) item.h = 0;
                        if (item.l === undefined) item.l = 0;
                        if (item.c === undefined) item.c = 0;
                    }
                    return item;
                });
            }
            
            return dataset;
        });
    }
    
    // 添加錯誤處理程序
    function addErrorHandlers(config) {
        const originalOnResize = config.options.onResize;
        const originalOnHover = config.options.onHover;
        
        // 安全的窗口調整大小處理
        config.options.onResize = function(chart, size) {
            try {
                if (originalOnResize) {
                    originalOnResize.call(this, chart, size);
                }
            } catch (e) {
                console.warn('圖表大小調整處理出錯:', e);
            }
        };
        
        // 安全的懸停處理
        config.options.onHover = function(event, elements, chart) {
            try {
                if (originalOnHover) {
                    originalOnHover.call(this, event, elements, chart);
                }
            } catch (e) {
                console.warn('圖表懸停處理出錯:', e);
            }
        };
        
        return config;
    }
    
    // 在畫布上顯示錯誤
    function showErrorOnCanvas(canvas, error) {
        try {
            if (!canvas) return;
            
            const ctx = canvas.getContext('2d');
            if (!ctx) return;
            
            // 清除畫布
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // 繪製錯誤訊息
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            
            // 錯誤標題
            ctx.font = '16px Arial';
            ctx.fillStyle = 'red';
            ctx.fillText('圖表渲染錯誤', canvas.width / 2, canvas.height / 2 - 20);
            
            // 錯誤信息
            ctx.font = '12px Arial';
            ctx.fillStyle = '#666';
            const errorMessage = error ? (error.message || '未知錯誤') : '未知錯誤';
            ctx.fillText(errorMessage, canvas.width / 2, canvas.height / 2 + 10);
            
            // 提示
            ctx.fillStyle = '#999';
            ctx.font = '10px Arial';
            ctx.fillText('請檢查控制台獲取詳細錯誤訊息', canvas.width / 2, canvas.height / 2 + 30);
        } catch (e) {
            console.error('無法在畫布上顯示錯誤:', e);
        }
    }
    
    // 記錄畫布狀態
    function logCanvasState(canvas) {
        try {
            if (!canvas) {
                console.error('畫布對象為空');
                return;
            }
            
            console.log('畫布狀態:', {
                id: canvas.id,
                width: canvas.width,
                height: canvas.height,
                className: canvas.className,
                hasContext: !!canvas.getContext('2d')
            });
        } catch (e) {
            console.error('記錄畫布狀態時出錯:', e);
        }
    }
    
    // 創建假圖表對象，避免後續錯誤
    function createDummyChart(canvasOrContext) {
        let ctx = null;
        let canvasEl = null;
        
        // 嘗試安全地獲取 canvas 和 ctx
        try {
            // 處理各種可能的輸入類型
            if (canvasOrContext) {
                // 如果是 Canvas 元素
                if (canvasOrContext instanceof HTMLCanvasElement) {
                    canvasEl = canvasOrContext;
                    try { ctx = canvasEl.getContext('2d'); } catch (e) {}
                }
                // 如果是 CanvasRenderingContext2D
                else if (canvasOrContext instanceof CanvasRenderingContext2D) {
                    ctx = canvasOrContext;
                    canvasEl = ctx.canvas;
                }
                // 如果是圖表對象，可能包含 canvas 和 ctx 屬性
                else if (canvasOrContext.canvas) {
                    if (canvasOrContext.canvas instanceof HTMLCanvasElement) {
                        canvasEl = canvasOrContext.canvas;
                        ctx = canvasOrContext instanceof CanvasRenderingContext2D ? 
                            canvasOrContext : canvasEl.getContext('2d');
                    }
                }
                // 如果有 getContext 方法，假設是 canvas 元素
                else if (typeof canvasOrContext.getContext === 'function') {
                    canvasEl = canvasOrContext;
                    try { ctx = canvasEl.getContext('2d'); } catch (e) {}
                }
            }
            
            // 如果以上都無法獲取 canvas，尋找頁面上的第一個 canvas 元素
            if (!canvasEl) {
                const firstCanvas = document.querySelector('canvas');
                if (firstCanvas) {
                    canvasEl = firstCanvas;
                    try { ctx = canvasEl.getContext('2d'); } catch (e) {}
                    console.warn('無法確定 canvas 元素，使用文檔中的第一個 canvas');
                }
            }
        } catch (e) {
            console.warn('創建假圖表時出錯:', e);
        }
        
        // 創建一個安全的假圖表對象
        return {
            id: 'dummy-' + Math.random().toString(36).substring(2, 9),
            canvas: canvasEl,
            ctx: ctx,
            chartArea: { 
                left: 0, 
                top: 0, 
                right: canvasEl ? canvasEl.width : 0, 
                bottom: canvasEl ? canvasEl.height : 0,
                width: canvasEl ? canvasEl.width : 0,
                height: canvasEl ? canvasEl.height : 0
            },
            boxes: [],
            _metasets: [],
            data: { datasets: [] },
            options: { 
                plugins: {},
                animation: { duration: 0 },
                responsive: true
            },
            _padding: { top: 0, left: 0, right: 0, bottom: 0 }, // 防止 _padding is undefined 錯誤
            update: function() { 
                console.warn('嘗試更新假圖表對象'); 
                return this; 
            },
            destroy: function() { 
                console.warn('嘗試銷毀假圖表對象'); 
                if (this.canvas && this.ctx) {
                    try {
                        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
                    } catch (e) {
                        console.warn('清除畫布時出錯:', e);
                    }
                }
                return true; 
            },
            render: function() { 
                console.warn('嘗試渲染假圖表對象'); 
                return this; 
            },
            stop: function() { return this; },
            resize: function() { return this; },
            clear: function() { 
                if (this.canvas) {
                    const ctx = this.canvas.getContext('2d');
                    if (ctx) {
                        ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
                    }
                }
                return this; 
            },
            toBase64Image: function() { return ''; },
            getElementAtEvent: function() { return []; },
            getDatasetAtEvent: function() { return []; },
            getElementsAtEvent: function() { return []; }
        };
    }
})();
