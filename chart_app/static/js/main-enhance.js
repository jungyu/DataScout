/**
 * Chart.js 增強腳本
 * 提供額外的圖表類型支援和功能增強
 */

(function() {
    console.log('Chart.js 增強腳本已載入');
    
    // 金融圖表控制器檢測函數
    function checkFinancialControllers() {
        if (typeof Chart === 'undefined') {
            console.warn('Chart.js 尚未載入，稍後再試');
            return false;
        }
        
        const controllers = Chart.controllers || {};
        const hasFinancialControllers = controllers.candlestick && controllers.ohlc;
        
        console.log('金融圖表控制器檢測:', 
            hasFinancialControllers ? '已註冊' : '未註冊',
            '控制器列表:', Object.keys(controllers));
        
        return hasFinancialControllers;
    }
    
    // 自定義時間單位檢測
    function detectTimeUnit(data) {
        if (!Array.isArray(data) || data.length < 2) {
            return 'day'; // 預設時間單位
        }
        
        try {
            // 確保有時間屬性
            if (!data[0].t || !data[1].t) {
                return 'day';
            }
            
            // 計算時間差 (毫秒)
            const time1 = data[0].t instanceof Date ? data[0].t.getTime() : new Date(data[0].t).getTime();
            const time2 = data[1].t instanceof Date ? data[1].t.getTime() : new Date(data[1].t).getTime();
            const timeDiff = Math.abs(time2 - time1);
            
            // 根據時間差決定適合的時間單位
            if (timeDiff < 60000) return 'second';         // 小於1分鐘
            if (timeDiff < 3600000) return 'minute';       // 小於1小時
            if (timeDiff < 86400000) return 'hour';        // 小於1天
            if (timeDiff < 604800000) return 'day';        // 小於1週
            if (timeDiff < 2592000000) return 'week';      // 小於1個月
            if (timeDiff < 31536000000) return 'month';    // 小於1年
            return 'year';
        } catch (error) {
            console.error('檢測時間單位時出錯:', error);
            return 'day'; // 發生錯誤時的預設值
        }
    }
    
    // 金融圖表數據正規化
    function normalizeCandlestickData(data) {
        if (!data || !Array.isArray(data)) return [];
        
        return data.map(item => {
            try {
                // 標準化時間
                let timeValue;
                const rawTime = item.t || item.time || item.x || item.date;
                
                if (rawTime instanceof Date) {
                    timeValue = rawTime;
                } else if (typeof rawTime === 'string') {
                    // 特別處理 YYYY-MM-DD 格式，避免時區問題
                    if (rawTime.match(/^\d{4}-\d{2}-\d{2}$/)) {
                        const [year, month, day] = rawTime.split('-').map(Number);
                        timeValue = new Date(Date.UTC(year, month - 1, day));
                    } else {
                        timeValue = new Date(rawTime);
                    }
                } else if (typeof rawTime === 'number') {
                    timeValue = new Date(rawTime);
                } else {
                    // 無效時間值使用當前時間
                    timeValue = new Date();
                }
                
                // 返回標準化後的數據點
                return {
                    t: timeValue,
                    o: Number(item.o || item.open || 0),
                    h: Number(item.h || item.high || 0),
                    l: Number(item.l || item.low || 0),
                    c: Number(item.c || item.close || 0)
                };
            } catch (error) {
                console.error('正規化數據點時出錯:', error);
                return null;
            }
        }).filter(Boolean); // 過濾掉轉換失敗的項目
    }
    
    // 將方法暴露給全局作用域
    window.chartEnhance = {
        checkFinancialControllers: checkFinancialControllers,
        detectTimeUnit: detectTimeUnit,
        normalizeCandlestickData: normalizeCandlestickData
    };
    
    // 當文檔載入完成後執行
    document.addEventListener('DOMContentLoaded', function() {
        console.log('Chart.js 增強腳本初始化');
        
        // 如果有 chartFix，先調用它的註冊函數
        if (window.chartFix && typeof window.chartFix.registerSpecialChartTypes === 'function') {
            setTimeout(window.chartFix.registerSpecialChartTypes, 500);
        }
        
        // 檢查金融圖表控制器
        setTimeout(checkFinancialControllers, 1000);
    });
})();
