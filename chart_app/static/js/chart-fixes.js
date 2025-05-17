/**
 * Chart.js 綜合修復腳本
 * 
 * 整合了多個修復腳本的功能：
 * - 動畫與佈局問題修復
 * - DOM 操作錯誤修復
 * - 圖例與工具提示位置修復
 * - Padding 相關錯誤修復
 * - 緊急渲染問題修復
 * 
 * 這個檔案取代了以下原始檔案：
 * - chart-anim-fix.js
 * - chart-dom-fix.js
 * - chart-legend-fix.js
 * - chart-padding-fix.js
 * - chart-patch.js
 */

(function() {
    console.log('載入 Chart.js 綜合修復腳本 v1.0');
    
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
    
    // 在 DOM 載入完成後初始化
    document.addEventListener('DOMContentLoaded', function() {
        console.log('初始化 Chart.js 修復程序');
        initFixes();
    });

    /**
     * 初始化所有修復功能
     */
    function initFixes() {
        waitForChart(function() {
            console.log('Chart.js 已載入，版本：', Chart.version);
            
            // 修復 DOM 操作問題
            fixDOMOperations();
            
            // 修復動畫與佈局問題
            fixAnimationAndLayout();
            
            // 修復圖例與工具提示位置
            fixLegendAndTooltip();
            
            // 修復 Padding 問題
            fixPaddingIssues();
            
            // 應用緊急修補
            applyEmergencyPatches();
            
            console.log('所有 Chart.js 修復已應用');
        });
    }

    /**
     * 修復 DOM 操作相關問題
     */
    function fixDOMOperations() {
        console.log('應用 DOM 操作修復');
        
        // 修復 Window.getComputedStyle 問題
        if (window.getComputedStyle && !window._originalGetComputedStyle) {
            window._originalGetComputedStyle = window.getComputedStyle;
            window.getComputedStyle = function(element, pseudoElt) {
                if (!element || !element.nodeType) {
                    console.warn('Chart.js 修復: getComputedStyle 收到無效元素');
                    // 返回空對象以避免錯誤
                    return {
                        getPropertyValue: function() { return ''; }
                    };
                }
                return window._originalGetComputedStyle(element, pseudoElt);
            };
        }
        
        // 增強 DOM 元素檢查
        const originalQuerySelector = Element.prototype.querySelector;
        Element.prototype.querySelector = function(selector) {
            try {
                return originalQuerySelector.call(this, selector);
            } catch (e) {
                console.warn('Chart.js 修復: querySelector 錯誤', e);
                return null;
            }
        };
    }

    /**
     * 修復動畫與佈局問題
     */
    function fixAnimationAndLayout() {
        console.log('應用動畫與佈局修復');
        
        if (Chart && Chart.defaults) {
            // 確保動畫 ID 總是可用
            const originalAnimationObject = Chart.animate && Chart.animate.target;
            if (originalAnimationObject) {
                console.log('增強動畫系統');
                Chart.animate.target = function(target) {
                    if (!target.id) {
                        target.id = '_chart_anim_' + (Math.random().toString(36).substr(2, 9));
                    }
                    return originalAnimationObject(target);
                };
            }
            
            // 修復佈局計算問題
            if (Chart.layouts) {
                const originalUpdate = Chart.layouts.update;
                Chart.layouts.update = function(chart, width, height) {
                    // 確保在計算佈局前有有效的 padding
                    if (chart && chart.chartArea && !chart.chartArea._padding) {
                        chart.chartArea._padding = {
                            left: 0,
                            top: 0,
                            right: 0,
                            bottom: 0
                        };
                    }
                    return originalUpdate(chart, width, height);
                };
            }
        }
    }

    /**
     * 修復圖例與工具提示位置
     */
    function fixLegendAndTooltip() {
        console.log('應用圖例與工具提示修復');
        
        if (Chart && Chart.defaults) {
            // 確保圖例總是有有效的位置
            if (Chart.defaults.plugins && Chart.defaults.plugins.legend) {
                const originalLegendPositionHandler = Chart.defaults.plugins.legend.position;
                if (originalLegendPositionHandler === undefined || originalLegendPositionHandler === 'top') {
                    Chart.defaults.plugins.legend.position = 'top';
                }
            }
            
            // 確保工具提示有有效的位置
            if (Chart.defaults.plugins && Chart.defaults.plugins.tooltip) {
                // 增強工具提示位置計算
                const originalTooltipPositioner = Chart.defaults.plugins.tooltip.position;
                Chart.defaults.plugins.tooltip.position = function(chart, options, point) {
                    try {
                        if (originalTooltipPositioner) {
                            return originalTooltipPositioner(chart, options, point);
                        }
                        return { x: point.x, y: point.y };
                    } catch (e) {
                        console.warn('Chart.js 修復: 工具提示位置計算錯誤', e);
                        return { x: point.x, y: point.y };
                    }
                };
            }
        }
    }

    /**
     * 修復 Padding 問題
     */
    function fixPaddingIssues() {
        console.log('應用 Padding 問題修復');
        
        if (Chart && Chart.layouts) {
            // 確保所有圖表元素有正確的 padding
            const originalPaddingObject = Chart.layouts.addPadding;
            if (originalPaddingObject) {
                Chart.layouts.addPadding = function(chart, left, top, right, bottom) {
                    // 確保所有參數都是數字
                    left = typeof left === 'number' ? left : 0;
                    top = typeof top === 'number' ? top : 0;
                    right = typeof right === 'number' ? right : 0;
                    bottom = typeof bottom === 'number' ? bottom : 0;
                    
                    // 確保 chart 對象有效
                    if (!chart || !chart.chartArea) {
                        console.warn('Chart.js 修復: addPadding 收到無效圖表對象');
                        return;
                    }
                    
                    // 確保 _padding 存在
                    if (!chart.chartArea._padding) {
                        chart.chartArea._padding = {
                            left: 0,
                            top: 0,
                            right: 0,
                            bottom: 0
                        };
                    }
                    
                    return originalPaddingObject(chart, left, top, right, bottom);
                };
            }
        }
    }

    /**
     * 應用緊急修補
     */
    function applyEmergencyPatches() {
        console.log('應用緊急修補');
        
        // 確保 Chart 對象有正確初始化
        if (typeof Chart !== 'undefined') {
            // 增強 destroy 方法
            const originalDestroy = Chart.prototype.destroy;
            Chart.prototype.destroy = function() {
                try {
                    // 確保清除所有事件監聽器
                    if (this.canvas) {
                        this.canvas.removeEventListener('click', null);
                        this.canvas.removeEventListener('mouseout', null);
                        this.canvas.removeEventListener('mousemove', null);
                    }
                    
                    // 調用原始方法
                    return originalDestroy.call(this);
                } catch (e) {
                    console.warn('Chart.js 修復: destroy 方法執行錯誤', e);
                    // 手動清理
                    if (this.canvas && this.canvas.parentNode) {
                        this.canvas.parentNode.removeChild(this.canvas);
                    }
                }
            };
            
            // 檢查圖表畫布
            const chartCanvas = document.getElementById('chartCanvas');
            if (chartCanvas) {
                // 確保畫布已準備好繪製
                chartCanvas.getContext = chartCanvas.getContext || function(type) {
                    if (type !== '2d') {
                        console.warn('Chart.js 修復: 只支援 2d 上下文');
                        return null;
                    }
                    
                    // 如果原始方法失敗，返回模擬的上下文對象
                    try {
                        return HTMLCanvasElement.prototype.getContext.call(this, type);
                    } catch (e) {
                        console.warn('Chart.js 修復: getContext 執行錯誤', e);
                        return null;
                    }
                };
            }
        }
    }
    
    // 導出修復程式到全局對象，方便進行測試和調試
    window.chartFixTools = {
        fixDOMOperations,
        fixAnimationAndLayout,
        fixLegendAndTooltip,
        fixPaddingIssues,
        applyEmergencyPatches,
        initFixes
    };
})();
