/**
 * Chart.js Padding 專用修復腳本
 * 專門針對 "this._padding is undefined" 錯誤提供深度修復
 */

(function() {
    console.log('載入 Chart.js Padding 專用修復腳本');
    
    // 等待 Chart.js 載入
    function waitForChart(callback) {
        if (typeof Chart !== 'undefined') {
            callback();
        } else {
            setTimeout(() => waitForChart(callback), 100);
        }
    }
    
    waitForChart(function() {
        try {
            console.log('應用 padding 相關的全方位修復');
            
            // 1. 深度修復圖表繪製時的 padding 問題
            patchChartDrawing();
            
            // 2. 修復所有盒子元素的 padding
            patchBoxPadding();
            
            // 3. 修復佈局計算的 padding
            patchLayoutPadding();
            
            console.log('Padding 修復完成');
        } catch (e) {
            console.error('應用 padding 修復時出錯:', e);
        }
    });
    
    // 深度修復圖表繪製問題
    function patchChartDrawing() {
        if (!Chart.prototype) return;
        
        // 修補圖表繪製方法
        const originalDraw = Chart.prototype.draw;
        if (originalDraw) {
            Chart.prototype.draw = function() {
                try {
                    // 確保圖表本身有 _padding
                    if (!this._padding) {
                        this._padding = { 
                            top: 0, 
                            left: 0, 
                            right: 0, 
                            bottom: 0 
                        };
                    }
                    
                    // 確保所有數據集都有 _padding
                    if (this._metasets) {
                        for (let i = 0; i < this._metasets.length; i++) {
                            const metaset = this._metasets[i];
                            if (metaset && !metaset._padding) {
                                metaset._padding = {
                                    top: 0, 
                                    left: 0, 
                                    right: 0, 
                                    bottom: 0
                                };
                            }
                        }
                    }
                    
                    // 應用原始繪製方法
                    return originalDraw.apply(this, arguments);
                } catch (e) {
                    // 如果是 padding 未定義錯誤
                    if (e.message && e.message.includes('_padding is undefined')) {
                        console.warn('捕獲 _padding 未定義錯誤，應用緊急修復');
                        
                        // 給所有可能的對象添加 _padding
                        this._padding = { top: 0, left: 0, right: 0, bottom: 0 };
                        
                        // 再次嘗試繪製
                        try {
                            return originalDraw.apply(this, arguments);
                        } catch (retryError) {
                            console.error('再次嘗試繪製時發生錯誤:', retryError);
                            // 不傳播錯誤，避免 UI 崩潰
                        }
                    } else {
                        console.error('繪製時出錯 (非 padding 相關):', e);
                    }
                }
            };
        }
    }
    
    // 修復所有盒子元素的 padding
    function patchBoxPadding() {
        // 遍歷所有圖表實例
        function applyPaddingToChartsAndBoxes() {
            // 檢查是否有獲取所有圖表的函數
            if (typeof Chart.getChart !== 'function') return;
            
            // 獲取所有畫布元素
            const canvases = document.querySelectorAll('canvas');
            
            // 遍歷每個畫布
            canvases.forEach(canvas => {
                try {
                    // 嘗試獲取圖表實例
                    const chart = Chart.getChart(canvas);
                    if (!chart) return;
                    
                    // 修復圖表的 padding
                    if (!chart._padding) {
                        chart._padding = { top: 0, left: 0, right: 0, bottom: 0 };
                    }
                    
                    // 修復所有盒子的 padding
                    if (chart.boxes && Array.isArray(chart.boxes)) {
                        chart.boxes.forEach(box => {
                            if (box && !box._padding) {
                                box._padding = { 
                                    top: 0, 
                                    left: 0, 
                                    right: 0, 
                                    bottom: 0 
                                };
                            }
                        });
                    }
                } catch (e) {
                    console.warn('修復圖表 padding 時出錯:', e);
                }
            });
        }
        
        // 初始修復
        applyPaddingToChartsAndBoxes();
        
        // 設置定期檢查，確保新創建的圖表也被修復
        setInterval(applyPaddingToChartsAndBoxes, 2000);
    }
    
    // 修復佈局計算的 padding
    function patchLayoutPadding() {
        if (!Chart.layouts) return;
        
        // 保存原始佈局方法的引用
        const layoutFunctions = [
            'update', 'configure', 'addBox', 'removeBox'
        ];
        
        layoutFunctions.forEach(funcName => {
            if (typeof Chart.layouts[funcName] === 'function') {
                const originalFunc = Chart.layouts[funcName];
                
                Chart.layouts[funcName] = function() {
                    try {
                        // 確保第一個參數 (通常是圖表) 有 _padding
                        if (arguments[0] && typeof arguments[0] === 'object' && !arguments[0]._padding) {
                            arguments[0]._padding = { 
                                top: 0, 
                                left: 0, 
                                right: 0, 
                                bottom: 0 
                            };
                        }
                        
                        // 確保第二個參數 (通常是盒子) 有 _padding (如果是物件)
                        if (arguments[1] && typeof arguments[1] === 'object' && !arguments[1]._padding) {
                            arguments[1]._padding = { 
                                top: 0, 
                                left: 0, 
                                right: 0, 
                                bottom: 0 
                            };
                        }
                        
                        return originalFunc.apply(this, arguments);
                    } catch (e) {
                        console.warn(`執行佈局函數 ${funcName} 時出錯:`, e);
                        
                        // 嘗試執行原始函數，即使出錯也保持靜默
                        try {
                            return originalFunc.apply(this, arguments);
                        } catch (innerError) {
                            // 靜默失敗
                            console.error(`執行原始佈局函數 ${funcName} 也失敗:`, innerError);
                        }
                    }
                };
            }
        });
    }
})();
