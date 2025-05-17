/**
 * 圖表修復程序 - 解決極座標圖、蠟燭圖和OHLC圖的渲染問題
 * 
 * 這個腳本用於修復圖表渲染過程中的"Canvas is already in use"錯誤，
 * 尤其針對極座標圖(PolarArea)、蠟燭圖(Candlestick)和OHLC圖三種特殊圖表類型。
 * 
 * 修復方法:
 * 1. 增強圖表實例的銷毀機制
 * 2. 確保控制器正確註冊
 * 3. 改進時間格式處理
 * 4. 增加錯誤恢復機制
 * 
 * 注意: 此檔案在建置過程中會被複製到 static/js 目錄，
 * 然後通過 HTML 的 script 標籤直接引用，而不是透過 JavaScript 模組系統。
 * 請勿移除此檔案，因為它是圖表應用程式的核心組件之一。
 */

// 執行修復
(function() {
    console.log('正在初始化圖表修復程序...');
    
    // 檢查Chart.js是否存在
    if (typeof Chart === 'undefined') {
        console.error('Chart.js未載入，無法執行修復');
        return;
    }
    
    console.log('Chart.js版本:', Chart.version);
    
    // 備份原始函數
    const originalDestroyMethod = Chart.prototype.destroy;
    
    // 增強銷毀方法
    Chart.prototype.destroy = function() {
        try {
            console.log(`增強銷毀圖表 ID:${this.id}`);
            
            // 清除事件監聽器
            if (this.canvas) {
                // 使用null處理函數解除所有綁定的事件
                ['click', 'mousemove', 'mouseout', 'mouseover', 'mouseenter', 'mouseleave'].forEach(eventType => {
                    this.canvas.removeEventListener(eventType, null);
                });
            }
            
            // 停止任何動畫
            if (typeof this.stop === 'function') {
                this.stop();
            }
            
            // 移除from Chart.instances
            if (Chart.instances && Chart.instances[this.id]) {
                delete Chart.instances[this.id];
            }
            
            // 調用原始的銷毀方法
            return originalDestroyMethod.apply(this, arguments);
        } catch (e) {
            console.error('銷毀圖表時發生錯誤:', e);
            
            // 確保圖表被移除，即使有錯誤發生
            if (Chart.instances && Chart.instances[this.id]) {
                delete Chart.instances[this.id];
            }
            
            // 清理 canvas
            if (this.canvas) {
                const ctx = this.canvas.getContext('2d');
                if (ctx) {
                    ctx.save();
                    ctx.resetTransform();
                    ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
                    ctx.restore();
                }
            }
        }
    };
    
    // 確保控制器註冊
    function ensureControllersRegistered() {
        console.log('檢查並確保特殊圖表控制器已註冊');
        
        // 檢查當前註冊的控制器
        const registeredControllers = Object.keys(Chart.controllers || {});
        console.log('當前已註冊控制器:', registeredControllers);
        
        const missingControllers = [];
        
        // 檢查極座標圖控制器
        if (!registeredControllers.includes('polarArea')) {
            missingControllers.push('polarArea');
            try {
                if (Chart.PolarAreaController) {
                    Chart.register(Chart.PolarAreaController);
                    console.log('註冊成功: PolarAreaController');
                }
            } catch (e) {
                console.warn('註冊 PolarAreaController 失敗:', e);
            }
        }
        
        // 檢查蠟燭圖控制器
        if (!registeredControllers.includes('candlestick')) {
            missingControllers.push('candlestick');
            try {
                if (window.CandlestickController) {
                    Chart.register(window.CandlestickController);
                    console.log('註冊成功: CandlestickController');
                } else if (window.Chart && window.Chart.controllers && window.Chart.controllers.financial) {
                    if (window.Chart.controllers.financial.CandlestickController) {
                        Chart.register(window.Chart.controllers.financial.CandlestickController);
                        console.log('註冊成功: financial.CandlestickController');
                    }
                }
            } catch (e) {
                console.warn('註冊 CandlestickController 失敗:', e);
            }
        }
        
        // 檢查 OHLC 控制器
        if (!registeredControllers.includes('ohlc')) {
            missingControllers.push('ohlc');
            try {
                if (window.OhlcController) {
                    Chart.register(window.OhlcController);
                    console.log('註冊成功: OhlcController');
                } else if (window.Chart && window.Chart.controllers && window.Chart.controllers.financial) {
                    if (window.Chart.controllers.financial.OhlcController) {
                        Chart.register(window.Chart.controllers.financial.OhlcController);
                        console.log('註冊成功: financial.OhlcController');
                    }
                }
            } catch (e) {
                console.warn('註冊 OhlcController 失敗:', e);
            }
        }
        
        // 報告缺少的控制器
        if (missingControllers.length > 0) {
            console.warn(`以下控制器尚未註冊或註冊失敗: ${missingControllers.join(', ')}`);
            console.log('圖表庫將自動回退到替代圖表類型');
        } else {
            console.log('所有必要的控制器均已註冊');
        }
    }
    
    // 增強 Canvas 清理函數
    function enhanceCanvasCleanup() {
        // 監聽圖表創建前的事件
        document.addEventListener('DOMContentLoaded', function() {
            // 初始檢查控制器
            ensureControllersRegistered();
            
            // 獲取 canvas 元素
            const canvas = document.getElementById('chartCanvas');
            if (!canvas) {
                console.warn('找不到圖表 Canvas 元素，跳過增強清理');
                return;
            }
            
            console.log('已增強 Canvas 清理機制');
            
            // 為 canvas 添加重置方法
            canvas.resetForNextChart = function() {
                const ctx = this.getContext('2d');
                ctx.save();
                ctx.resetTransform();
                ctx.clearRect(0, 0, this.width, this.height);
                ctx.restore();
                
                // 移除任何可能殘留的事件監聽器
                ['click', 'mousemove', 'mouseout', 'mouseover', 'mouseenter', 'mouseleave'].forEach(eventType => {
                    this.removeEventListener(eventType, null);
                });
                
                console.log('Canvas 已重置，準備創建新圖表');
            };
        });
    }
    
    // 修復時間數據處理
    function fixTimeDataProcessing() {
        // 檢查原始函數是否存在
        if (typeof window.normalizeCandlestickData !== 'function') {
            console.log('原始 normalizeCandlestickData 函數不可用，跳過修復');
            return;
        }
        
        // 備份原始函數
        const originalNormalize = window.normalizeCandlestickData;
        
        // 增強版本
        window.normalizeCandlestickData = function(data) {
            if (!Array.isArray(data)) return [];
            
            return data.map(item => {
                if (!item) return null;
                
                // 標準化時間欄位 - 增強版
                const timestamp = item.t || item.x || item.time || item.date;
                let timeValue;
                
                try {
                    if (timestamp instanceof Date) {
                        timeValue = timestamp;
                    } else if (typeof timestamp === 'string') {
                        // 增強對字符串日期格式的處理
                        if (timestamp.match(/^\d{4}-\d{2}-\d{2}$/)) {
                            // YYYY-MM-DD 格式，使用 UTC 時間避免時區問題
                            const [year, month, day] = timestamp.split('-').map(Number);
                            timeValue = new Date(Date.UTC(year, month - 1, day));
                        } else if (timestamp.match(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/)) {
                            // ISO 格式 (YYYY-MM-DDTHH:MM:SS)
                            timeValue = new Date(timestamp);
                        } else if (timestamp.match(/^\d+$/)) {
                            // 純數字時間戳
                            timeValue = new Date(parseInt(timestamp, 10));
                        } else {
                            // 其他格式嘗試標準解析
                            timeValue = new Date(timestamp);
                        }
                        
                        // 檢查是否解析成功
                        if (isNaN(timeValue.getTime())) {
                            console.warn(`無法解析日期字符串 "${timestamp}"，將使用當前時間`);
                            timeValue = new Date();
                        }
                    } else if (typeof timestamp === 'number') {
                        timeValue = new Date(timestamp);
                    } else {
                        // 如果沒有有效的時間欄位，使用當前時間
                        console.warn('無法識別的時間格式，將使用當前時間');
                        timeValue = new Date();
                    }
                } catch (error) {
                    console.error('解析時間格式出錯:', error, '原始值:', timestamp);
                    timeValue = new Date(); // 出錯時使用當前時間作為備用
                }
                
                // 標準化 OHLC 欄位
                return {
                    t: timeValue,
                    o: Number(item.o || item.open || 0),
                    h: Number(item.h || item.high || 0),
                    l: Number(item.l || item.low || 0),
                    c: Number(item.c || item.close || 0),
                    // 可選欄位：成交量
                    v: item.v !== undefined ? Number(item.v) : undefined
                };
            }).filter(item => item !== null && !isNaN(item.t.getTime()));
        };
        
        console.log('已增強時間數據處理機制');
    }
    
    // 執行所有修復
    enhanceCanvasCleanup();
    fixTimeDataProcessing();
    
    console.log('圖表修復程序初始化完成');
    
    // 在 window 上公開修復函數，以便可以在其他地方調用
    window.chartFix = {
        ensureControllersRegistered: ensureControllersRegistered,
        enhanceCanvasCleanup: enhanceCanvasCleanup,
        fixTimeDataProcessing: fixTimeDataProcessing
    };
})();
