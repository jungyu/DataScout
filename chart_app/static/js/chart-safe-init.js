/**
 * Chart.js 安全初始化腳本
 * 提供一個安全的圖表創建函數，確保所有修復都被正確應用
 */

(function() {
    console.log('載入 Chart.js 安全初始化腳本');
    
    // 等待 Chart.js 和所有修復腳本載入
    function waitForDependencies(callback) {
        // 確保 Chart.js 和所有修復已經載入
        if (typeof Chart !== 'undefined') {
            setTimeout(callback, 300); // 給其他修復腳本一些時間載入
        } else {
            setTimeout(() => waitForDependencies(callback), 100);
        }
    }
    
    // 安全地獲取正確的畫布元素
    function getCanvas(canvasOrCtxOrId) {
        if (!canvasOrCtxOrId) return null;
        
        // 如果是字符串，假設它是元素ID
        if (typeof canvasOrCtxOrId === 'string') {
            return document.getElementById(canvasOrCtxOrId);
        }
        
        // 如果是 Canvas 元素
        if (canvasOrCtxOrId instanceof HTMLCanvasElement) {
            return canvasOrCtxOrId;
        }
        
        // 如果是 CanvasRenderingContext2D
        if (canvasOrCtxOrId instanceof CanvasRenderingContext2D) {
            return canvasOrCtxOrId.canvas;
        }
        
        // 如果有 canvas 屬性
        if (canvasOrCtxOrId && canvasOrCtxOrId.canvas) {
            return getCanvas(canvasOrCtxOrId.canvas);
        }
        
        return null;
    }
    
    // 安全的圖表創建函數
    window.createSafeChart = function(canvasOrCtxOrId, config) {
        // 等待依賴項載入
        waitForDependencies(function() {
            try {
                console.log('使用安全初始化創建圖表');
                
                // 獲取畫布元素
                const canvas = getCanvas(canvasOrCtxOrId);
                
                if (!canvas) {
                    console.error('找不到有效的畫布元素:', canvasOrCtxOrId);
                    return null;
                }
                
                // 確保是 Canvas 元素，不是 Context
                if (!(canvas instanceof HTMLCanvasElement)) {
                    console.error('提供的對象不是有效的 Canvas 元素:', canvas);
                    return null;
                }
                
                // 清除現有圖表
                const existingChart = Chart.getChart && Chart.getChart(canvas);
                if (existingChart) {
                    console.log('銷毀現有圖表');
                    existingChart.destroy();
                }
                
                // 強化配置，確保有所有必要的屬性
                if (!config) config = {};
                if (!config.type) config.type = 'line';
                if (!config.data) config.data = { datasets: [] };
                if (!config.options) config.options = {};
                if (!config.options.plugins) config.options.plugins = {};
                
                // 確保正確的 padding 配置
                if (!config.options.layout) config.options.layout = {};
                if (!config.options.layout.padding) {
                    config.options.layout.padding = { top: 5, right: 5, bottom: 5, left: 5 };
                }
                
                // 添加錯誤處理
                const originalOnResize = config.options.onResize;
                config.options.onResize = function(chart, size) {
                    try {
                        // 確保圖表有 _padding
                        if (!chart._padding) {
                            chart._padding = { top: 0, left: 0, right: 0, bottom: 0 };
                        }
                        
                        // 調用原始處理程序
                        if (originalOnResize) {
                            originalOnResize.call(this, chart, size);
                        }
                    } catch (e) {
                        console.warn('圖表大小調整處理出錯:', e);
                    }
                };
                
                // 創建圖表
                try {
                    console.log('創建新圖表');
                    const chart = new Chart(canvas, config);
                    
                    // 立即修復 padding
                    if (!chart._padding) {
                        chart._padding = { top: 0, left: 0, right: 0, bottom: 0 };
                    }
                    
                    // 修復所有盒子的 padding
                    if (chart.boxes && Array.isArray(chart.boxes)) {
                        chart.boxes.forEach(box => {
                            if (box && !box._padding) {
                                box._padding = { top: 0, left: 0, right: 0, bottom: 0 };
                            }
                        });
                    }
                    
                    return chart;
                } catch (e) {
                    console.error('創建圖表時出錯:', e);
                    
                    // 顯示友好的錯誤訊息
                    const ctx = canvas.getContext('2d');
                    if (ctx) {
                        ctx.clearRect(0, 0, canvas.width, canvas.height);
                        ctx.fillStyle = '#f8d7da';
                        ctx.fillRect(0, 0, canvas.width, canvas.height);
                        ctx.font = '14px Arial';
                        ctx.fillStyle = '#721c24';
                        ctx.textAlign = 'center';
                        ctx.fillText('圖表創建失敗', canvas.width / 2, canvas.height / 2);
                        ctx.font = '12px Arial';
                        ctx.fillText('請查看控制台了解詳情', canvas.width / 2, canvas.height / 2 + 20);
                    }
                    
                    return null;
                }
            } catch (e) {
                console.error('安全初始化圖表時出錯:', e);
                return null;
            }
        });
    };
    
    // 創建圖表元素輔助函數
    window.createChartElement = function(containerId, chartId, width, height) {
        try {
            const container = document.getElementById(containerId);
            if (!container) {
                console.error(`找不到容器: ${containerId}`);
                return null;
            }
            
            // 創建畫布元素
            const canvas = document.createElement('canvas');
            canvas.id = chartId;
            canvas.width = width || 400;
            canvas.height = height || 300;
            canvas.style.width = '100%';
            canvas.style.height = '100%';
            
            // 清除容器並添加畫布
            container.innerHTML = '';
            container.appendChild(canvas);
            
            return canvas;
        } catch (e) {
            console.error('創建圖表元素時出錯:', e);
            return null;
        }
    };

    // 通知已加載
    document.addEventListener('DOMContentLoaded', function() {
        console.log('Chart.js 安全初始化腳本已準備就緒');
    });
})();
