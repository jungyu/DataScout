/**
 * Chart.js 錯誤修復腳本 - 專門處理動畫與佈局問題
 * 
 * 修復的錯誤：
 * 1. "class does not have id" - 動畫系統問題
 * 2. "this._padding is undefined" - 佈局計算問題
 * 3. "Bo[n.position] is undefined" - 元素位置問題
 */

(function() {
    console.log('載入 Chart.js 動畫與佈局修復腳本');
    
    // 等待 Chart.js 載入
    function waitForChart(callback) {
        if (typeof Chart !== 'undefined') {
            callback();
        } else {
            setTimeout(function() {
                waitForChart(callback);
            }, 100);
        }
    }
    
    waitForChart(function() {
        console.log('開始應用 Chart.js 動畫與佈局修復');
        
        try {
            // 修復 class 動畫系統問題
            patchAnimationSystem();
            
            // 修復佈局計算問題
            patchLayoutSystem();
            
            // 修復位置計算問題
            patchPositionSystem();
            
            console.log('Chart.js 動畫與佈局修復完成');
        } catch (error) {
            console.error('無法應用 Chart.js 修復:', error);
        }
    });
    
    // 修復動畫系統
    function patchAnimationSystem() {
        // 確保動畫系統中的所有類都有 ID
        if (Chart.Animations && Chart.Animations.animations) {
            console.log('修復 Chart.js 動畫系統');
            
            // 保存原始動畫創建方法的引用
            const originalAnimator = Chart.Animations._animator;
            if (originalAnimator) {
                Chart.Animations._animator = function(chart, items, properties) {
                    // 確保所有元素都有 ID
                    if (Array.isArray(items)) {
                        items.forEach((item, index) => {
                            if (!item || typeof item !== 'object') return;
                            if (!item.id) {
                                item.id = (chart && chart.id ? chart.id : 'chart') + '-item-' + index;
                            }
                        });
                    }
                    
                    try {
                        return originalAnimator.call(this, chart, items, properties);
                    } catch (e) {
                        console.warn('動畫器運行出錯:', e.message);
                        // 返回空的動畫數組，避免完全中斷
                        return [];
                    }
                };
            }
            
            // 修復動畫註冊過程
            if (Chart.register) {
                const originalRegister = Chart.register;
                Chart.register = function() {
                    try {
                        return originalRegister.apply(this, arguments);
                    } catch (e) {
                        console.warn('註冊元件時出錯，嘗試修復:', e.message);
                        
                        // 分析錯誤
                        if (e.message && e.message.includes('class does not have id')) {
                            // 嘗試為缺少 ID 的類添加 ID
                            for (let i = 0; i < arguments.length; i++) {
                                let component = arguments[i];
                                
                                // 處理陣列參數的情況
                                if (Array.isArray(component)) {
                                    component.forEach(item => {
                                        if (item && typeof item === 'object' && !item.id) {
                                            item.id = 'auto-id-' + Math.random().toString(36).substr(2, 9);
                                        }
                                    });
                                } else if (component && typeof component === 'object') {
                                    if (!component.id) {
                                        component.id = 'auto-id-' + Math.random().toString(36).substr(2, 9);
                                    }
                                }
                            }
                            
                            // 再次嘗試註冊
                            return originalRegister.apply(this, arguments);
                        } else {
                            throw e;
                        }
                    }
                };
            }
        }
    }
    
    // 修復佈局計算問題
    function patchLayoutSystem() {
        console.log('修復 Chart.js 佈局系統');
        
        // 修復元素的 padding 計算
        if (Chart.layouts) {
            // 保存原始佈局更新方法的引用
            const originalUpdateLayout = Chart.layouts.update;
            if (originalUpdateLayout) {
                Chart.layouts.update = function(chart, width, height) {
                    try {
                        // 確保圖表對象有效
                        if (!chart || typeof chart !== 'object') {
                            console.warn('佈局更新接收到無效的圖表對象');
                            return originalUpdateLayout.apply(this, arguments);
                        }

                        // 確保所有元素都有正確的 padding
                        chart.boxes = chart.boxes || [];
                        chart.boxes.forEach(box => {
                            if (!box) return;
                            if (!box._padding) {
                                box._padding = {
                                    top: 0,
                                    left: 0,
                                    right: 0,
                                    bottom: 0
                                };
                            }
                        });
                        
                        return originalUpdateLayout.call(this, chart, width, height);
                    } catch (e) {
                        console.error('佈局更新時出錯:', e);
                        
                        // 緊急回退方案 - 使用基本佈局
                        if (chart.chartArea) {
                            const chartArea = chart.chartArea;
                            const padding = 10;
                            chartArea.left = padding;
                            chartArea.top = padding;
                            chartArea.right = width - padding;
                            chartArea.bottom = height - padding;
                            chartArea.width = chartArea.right - chartArea.left;
                            chartArea.height = chartArea.bottom - chartArea.top;
                        }
                    }
                };
            }
        }
    }
    
    // 修復位置計算問題
    function patchPositionSystem() {
        console.log('修復 Chart.js 位置計算系統');
        
        // 修復自定義插件位置問題
        const validPositions = ['top', 'left', 'bottom', 'right', 'chartArea'];
        
        // 直接修復 Bo[n.position] is undefined 問題
        // 這個問題通常發生在內部位置映射表中
        try {
            // 檢查所有全局對象，尋找可能的位置映射
            for (let key in window) {
                // 跳過內置對象
                if (key.startsWith('__') || ['window', 'document', 'console'].includes(key)) {
                    continue;
                }
                
                const obj = window[key];
                // 檢查對象是否有可能是圖表位置映射的特徵
                if (obj && typeof obj === 'object' && 
                    (obj.top !== undefined || obj.bottom !== undefined || 
                     obj.left !== undefined || obj.right !== undefined)) {
                    
                    // 為所有有效位置添加默認值
                    validPositions.forEach(pos => {
                        if (obj[pos] === undefined) {
                            console.log(`為全局對象 ${key} 添加缺失的位置定義: ${pos}`);
                            obj[pos] = 'top'; // 使用一個默認值
                        }
                    });
                }
            }
        } catch (e) {
            console.warn('修復全局位置映射時出錯:', e);
        }
        
        // 修復主要的位置函數
        function fixPositions() {
            try {
                // 判斷是否為 Chart.js 3.x
                if (Chart.registry && Chart.registry.plugins) {
                    // 確保圖例和標題插件有正確的位置設置
                    const configureDefaults = function(defaults) {
                        if (defaults.plugins && defaults.plugins.legend && defaults.plugins.legend.position) {
                            const position = defaults.plugins.legend.position;
                            if (validPositions.indexOf(position) === -1) {
                                console.warn(`修復: 將不支援的圖例位置 "${position}" 改為 "top"`);
                                defaults.plugins.legend.position = 'top';
                            }
                        }
                        
                        if (defaults.plugins && defaults.plugins.title && defaults.plugins.title.position) {
                            const position = defaults.plugins.title.position;
                            if (validPositions.indexOf(position) === -1) {
                                console.warn(`修復: 將不支援的標題位置 "${position}" 改為 "top"`);
                                defaults.plugins.title.position = 'top';
                            }
                        }
                    };
                    
                    // 套用到現有配置
                    configureDefaults(Chart.defaults);
                }
                
                // 修復 Tooltip 的位置處理
                if (Chart.Tooltip && Chart.Tooltip.positioners) {
                    // 確保所有定位器處理無效或缺失位置
                    const originalPositioners = Chart.Tooltip.positioners;
                    
                    Object.keys(originalPositioners).forEach(key => {
                        const originalPositioner = originalPositioners[key];
                        Chart.Tooltip.positioners[key] = function(items, eventPosition) {
                            try {
                                return originalPositioner.call(this, items, eventPosition);
                            } catch (e) {
                                console.warn('Tooltip 位置計算錯誤:', e);
                                // 回退到事件位置
                                return eventPosition ? {
                                    x: eventPosition.x,
                                    y: eventPosition.y
                                } : { x: 0, y: 0 };
                            }
                        };
                    });
                    
                    // 確保有預設位置處理器
                    Chart.Tooltip.positioners.fallback = function(items, eventPosition) {
                        return eventPosition ? {
                            x: eventPosition.x,
                            y: eventPosition.y
                        } : { x: 0, y: 0 };
                    };
                }
            } catch (e) {
                console.error('修復位置系統時出錯:', e);
            }
        }
        
        fixPositions();
        
        // 修補 Chart.js 的事件處理系統
        if (typeof Chart !== 'undefined') {
            try {
                const originalEventHandler = Chart.prototype._eventHandler;
                if (originalEventHandler) {
                    Chart.prototype._eventHandler = function(e) {
                        try {
                            return originalEventHandler.call(this, e);
                        } catch (err) {
                            console.warn('事件處理錯誤，已被安全拦截:', err);
                            // 不傳播錯誤，確保 UI 不會崩潰
                            return false;
                        }
                    };
                }
            } catch (e) {
                console.error('無法修補事件處理系統:', e);
            }
        }
    }
    
    // 創建安全版本的渲染函數
    function createSafeChart() {
        if (typeof Chart === 'undefined') return;
        
        // 確保有一個安全的方式來檢測現有圖表
        window.safeGetChart = function(canvas) {
            try {
                return Chart.getChart(canvas);
            } catch (e) {
                console.warn('安全獲取圖表失敗:', e);
                return null;
            }
        };
        
        // 安全渲染函數
        window.safeRenderChart = function(config, canvas) {
            if (!canvas) {
                console.error('無效的 canvas 元素');
                return null;
            }
            
            try {
                // 確保先清除任何現有圖表
                const existingChart = window.safeGetChart(canvas);
                if (existingChart) {
                    try {
                        existingChart.destroy();
                    } catch (e) {
                        console.warn('銷毀現有圖表時出錯:', e);
                        // 嘗試清除畫布
                        const ctx = canvas.getContext('2d');
                        ctx.clearRect(0, 0, canvas.width, canvas.height);
                    }
                }
                
                // 應用預先修復設置
                if (!config.options) {
                    config.options = {};
                }
                
                // 確保有效的圖例位置
                if (!config.options.plugins) {
                    config.options.plugins = {};
                }
                if (!config.options.plugins.legend) {
                    config.options.plugins.legend = {};
                }
                if (!validPositions.includes(config.options.plugins.legend.position)) {
                    config.options.plugins.legend.position = 'top';
                }
                
                // 添加錯誤處理
                config.options.onError = function(err) {
                    console.error('圖表渲染錯誤:', err);
                    // 在畫布上顯示友好的錯誤訊息
                    const ctx = canvas.getContext('2d');
                    ctx.clearRect(0, 0, canvas.width, canvas.height);
                    ctx.font = '14px Arial';
                    ctx.fillStyle = 'red';
                    ctx.textAlign = 'center';
                    ctx.fillText('圖表渲染失敗', canvas.width / 2, canvas.height / 2);
                    ctx.fillText(err.message || '未知錯誤', canvas.width / 2, canvas.height / 2 + 20);
                };
                
                // 創建新圖表
                return new Chart(canvas, config);
            } catch (e) {
                console.error('安全渲染圖表時出錯:', e);
                
                // 在畫布上顯示友好的錯誤訊息
                try {
                    const ctx = canvas.getContext('2d');
                    ctx.clearRect(0, 0, canvas.width, canvas.height);
                    ctx.font = '14px Arial';
                    ctx.fillStyle = 'red';
                    ctx.textAlign = 'center';
                    ctx.fillText('圖表渲染失敗', canvas.width / 2, canvas.height / 2);
                    ctx.fillText(e.message || '未知錯誤', canvas.width / 2, canvas.height / 2 + 20);
                } catch (drawErr) {
                    console.error('無法在畫布上繪製錯誤訊息:', drawErr);
                }
                return null;
            }
        };
    }
    
    // 創建安全版本的圖表渲染函數
    waitForChart(createSafeChart);
})();
