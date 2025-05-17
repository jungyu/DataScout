/**
 * Chart.js DOM 操作修復腳本
 * 專門處理 DOM 操作相關錯誤，如 "Window.getComputedStyle: Argument 1 is not an object"
 */

(function() {
    console.log('載入 Chart.js DOM 操作修復腳本');
    
    // 等待 Chart.js 載入
    function waitForChart(callback) {
        if (typeof Chart !== 'undefined') {
            callback();
        } else {
            setTimeout(() => waitForChart(callback), 100);
        }
    }
    
    waitForChart(function() {
        console.log('開始應用 Chart.js DOM 操作修復');
        
        try {
            // 修復 getComputedStyle 的操作
            patchDomOperations();
            
            // 修復畫布渲染問題
            patchCanvasRendering();
            
            // 修復圖表中的 _padding 問題
            fixPaddingIssue();
            
            console.log('DOM 操作修復完成');
        } catch (e) {
            console.error('應用 DOM 操作修復時出錯:', e);
        }
    });
    
    // 修復 DOM 操作問題
    function patchDomOperations() {
        // 如果 Chart.js 沒有載入，則退出
        if (typeof Chart === 'undefined') return;
        
        console.log('修復 Chart.js DOM 操作');
        
        // 保存原始 getComputedStyle 方法
        const originalGetComputedStyle = window.getComputedStyle;
        
        // 重寫 getComputedStyle 以增加安全檢查
        window.getComputedStyle = function(element, pseudoElt) {
            // 檢查元素是否為有效的 DOM 對象
            if (!element || typeof element !== 'object' || !element.nodeType) {
                console.warn('getComputedStyle 被調用時提供了無效的元素:', element);
                // 返回安全的空樣式對象
                return {
                    getPropertyValue: function() { return ''; },
                    setProperty: function() {},
                };
            }
            
            try {
                return originalGetComputedStyle(element, pseudoElt);
            } catch (e) {
                console.warn('getComputedStyle 操作出錯:', e);
                // 返回安全的空樣式對象
                return {
                    getPropertyValue: function() { return ''; },
                    setProperty: function() {},
                };
            }
        };
        
        // 如果存在 Chart.helpers.dom，修復相關 DOM 操作
        if (Chart.helpers && Chart.helpers.dom) {
            const dom = Chart.helpers.dom;
            
            // 修復可能的 DOM 元素訪問方法
            const domMethods = ['getStyle', 'getRelativePosition', 'getMaximumSize', 'retinaScale'];
            
            domMethods.forEach(method => {
                if (typeof dom[method] === 'function') {
                    const original = dom[method];
                    dom[method] = function() {
                        try {
                            // 檢查第一個參數是否為有效的 DOM 元素
                            if (arguments[0] && 
                                (arguments[0].nodeType === undefined || !arguments[0].nodeType)) {
                                console.warn(`${method} 調用時提供了無效的元素:`, arguments[0]);
                                
                                // 對不同方法返回適當的默認值
                                switch(method) {
                                    case 'getStyle': return '';
                                    case 'getRelativePosition': return {x: 0, y: 0};
                                    case 'getMaximumSize': return {width: 0, height: 0};
                                    case 'retinaScale': return;
                                    default: return;
                                }
                            }
                            
                            return original.apply(this, arguments);
                        } catch (e) {
                            console.warn(`調用 dom.${method} 時出錯:`, e);
                            
                            // 根據方法返回安全的默認值
                            switch(method) {
                                case 'getStyle': return '';
                                case 'getRelativePosition': return {x: 0, y: 0};
                                case 'getMaximumSize': return {width: 0, height: 0};
                                case 'retinaScale': return;
                                default: return;
                            }
                        }
                    };
                }
            });
        }
    }
    
    // 修復畫布渲染問題
    function patchCanvasRendering() {
        if (typeof Chart === 'undefined' || !Chart.prototype) return;
        
        console.log('修復畫布渲染問題');
        
        // 保存原始的繪圖方法
        const originalDraw = Chart.prototype.draw;
        if (originalDraw) {
            Chart.prototype.draw = function() {
                try {
                    // 檢查畫布元素的可用性
                    const canvas = this.canvas;
                    if (!canvas || !canvas.getContext) {
                        console.warn('圖表繪製時畫布不可用');
                        return;
                    }
                    
                    // 檢查上下文
                    const ctx = this.ctx;
                    if (!ctx) {
                        console.warn('圖表繪製時上下文不可用');
                        return;
                    }
                    
                    // 檢查繪圖區域是否有效
                    const chartArea = this.chartArea;
                    if (!chartArea || chartArea.width <= 0 || chartArea.height <= 0) {
                        console.warn('圖表繪製區域無效，重建佈局');
                        
                        // 嘗試重建佈局
                        if (typeof this.resize === 'function') {
                            this.resize();
                        }
                    }
                    
                    // 執行繪圖
                    return originalDraw.apply(this, arguments);
                } catch (e) {
                    console.error('圖表繪製時出錯:', e);
                }
            };
        }
        
        // 修復圖表更新過程中的 DOM 操作
        const originalUpdate = Chart.prototype.update;
        if (originalUpdate) {
            Chart.prototype.update = function(mode) {
                try {
                    // 確保元素仍在 DOM 中
                    const canvas = this.canvas;
                    if (canvas && !document.body.contains(canvas)) {
                        console.warn('圖表更新時畫布不在 DOM 中，放棄更新');
                        return;
                    }
                    
                    return originalUpdate.apply(this, arguments);
                } catch (e) {
                    console.error('圖表更新時出錯:', e);
                }
            };
        }
    }
    
    // 修復圖表繪製時的 padding 問題
    function fixPaddingIssue() {
        console.log('修復圖表中的 _padding 問題');
        
        // 首先修復畫布元素的檢查邏輯
        function safeGetCanvas(canvasOrContext) {
            if (!canvasOrContext) return null;
            
            // 檢查是否是 CanvasRenderingContext2D
            if (canvasOrContext instanceof CanvasRenderingContext2D) {
                return canvasOrContext.canvas;
            }
            
            // 檢查是否是 Canvas 元素
            if (canvasOrContext instanceof HTMLCanvasElement) {
                return canvasOrContext;
            }
            
            // 如果是具有 canvas 屬性的物件（如圖表對象）
            if (canvasOrContext.canvas) {
                return safeGetCanvas(canvasOrContext.canvas);
            }
            
            return null;
        }
        
        // 註冊一個全局輔助函數，用於安全獲取Canvas元素
        window.safeGetCanvasElement = safeGetCanvas;
        
        // 針對圖表原型添加 _padding 安全檢查
        if (Chart && Chart.prototype) {
            // 在繪製前檢查並修復 padding
            const originalDraw = Chart.prototype.draw;
            if (originalDraw) {
                Chart.prototype.draw = function() {
                    try {
                        // 確保畫布元素是正確的
                        if (this.ctx && this.ctx instanceof CanvasRenderingContext2D && (!this.canvas || !(this.canvas instanceof HTMLCanvasElement))) {
                            this.canvas = this.ctx.canvas;
                        }
                        
                        // 檢查 _padding 是否存在
                        if (this && this._padding === undefined) {
                            console.log('修復圖表 _padding 未定義問題');
                            this._padding = { top: 0, left: 0, right: 0, bottom: 0 };
                        }
                        
                        // 檢查所有框體的 _padding
                        if (this.boxes && Array.isArray(this.boxes)) {
                            this.boxes.forEach(box => {
                                if (box && box._padding === undefined) {
                                    box._padding = { top: 0, left: 0, right: 0, bottom: 0 };
                                }
                            });
                        }
                        
                        // 檢查所有數據集以確保沒有 _padding 問題
                        if (this._metasets && Array.isArray(this._metasets)) {
                            this._metasets.forEach(metaset => {
                                if (metaset && metaset._padding === undefined) {
                                    metaset._padding = { top: 0, left: 0, right: 0, bottom: 0 };
                                }
                            });
                        }
                        
                        // 應用原始繪製邏輯
                        return originalDraw.apply(this, arguments);
                    } catch (e) {
                        console.error('在修復 _padding 過程中出錯:', e);
                        
                        // 恢復原始邏輯
                        try {
                            return originalDraw.apply(this, arguments);
                        } catch (innerError) {
                            console.error('嘗試原始繪製也出錯:', innerError);
                        }
                    }
                };
            }
            
            // 修復計算尺寸方法
            if (Chart.layouts && Chart.layouts.addBox) {
                const originalAddBox = Chart.layouts.addBox;
                Chart.layouts.addBox = function(chart, box) {
                    // 確保 box 有 _padding
                    if (box && box._padding === undefined) {
                        box._padding = { top: 0, left: 0, right: 0, bottom: 0 };
                    }
                    
                    return originalAddBox.apply(this, arguments);
                };
            }
        }
    }
})();
