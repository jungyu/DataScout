/**
 * 蠟燭圖與金融圖表輔助函數
 * 處理蠟燭圖和OHLC圖的特殊需求
 */

(function() {
    console.log('載入蠟燭圖輔助函數');
    
    /**
     * 檢測時間序列資料的適合時間單位
     * @param {Array} data - 時間序列數據，包含 t 屬性表示時間
     * @returns {string} - 適合的時間單位 (second, minute, hour, day, week, month, year)
     */
    function detectTimeUnit(data) {
        if (!Array.isArray(data) || data.length < 2) {
            return 'day'; // 預設時間單位
        }
        
        try {
            // 確保有時間屬性且是有效的日期對象
            const getValidTime = (item) => {
                if (!item || !item.t) return null;
                
                if (item.t instanceof Date) {
                    return item.t.getTime();
                } 
                
                try {
                    return new Date(item.t).getTime();
                } catch (e) {
                    return null;
                }
            };
            
            // 找出有效的時間點
            const validTimes = data
                .map(getValidTime)
                .filter(time => time !== null && !isNaN(time));
            
            if (validTimes.length < 2) {
                return 'day';
            }
            
            // 計算平均時間間隔
            validTimes.sort((a, b) => a - b);
            let totalDiff = 0;
            for (let i = 1; i < validTimes.length; i++) {
                totalDiff += validTimes[i] - validTimes[i-1];
            }
            const avgDiff = totalDiff / (validTimes.length - 1);
            
            // 根據平均時間差決定適合的時間單位
            if (avgDiff < 60000) return 'second';         // 小於1分鐘
            if (avgDiff < 3600000) return 'minute';       // 小於1小時
            if (avgDiff < 86400000) return 'hour';        // 小於1天
            if (avgDiff < 604800000) return 'day';        // 小於1週
            if (avgDiff < 2592000000) return 'week';      // 小於1個月
            if (avgDiff < 31536000000) return 'month';    // 小於1年
            return 'year';
        } catch (error) {
            console.error('檢測時間單位時出錯:', error);
            return 'day'; // 發生錯誤時的預設值
        }
    }
    
    /**
     * 驗證蠟燭圖數據格式是否有效
     * @param {Array} data - 要驗證的數據
     * @returns {boolean} - 是否為有效的蠟燭圖數據
     */
    function validateCandlestickData(data) {
        if (!Array.isArray(data) || data.length === 0) {
            return false;
        }
        
        return data.every(item => {
            return (
                item &&
                typeof item === 'object' &&
                (item.t !== undefined || item.time !== undefined || item.x !== undefined || item.date !== undefined) &&
                (item.o !== undefined || item.open !== undefined) &&
                (item.h !== undefined || item.high !== undefined) &&
                (item.l !== undefined || item.low !== undefined) &&
                (item.c !== undefined || item.close !== undefined)
            );
        });
    }
    
    /**
     * 將各種蠟燭圖數據格式標準化
     * @param {Array} data - 原始數據
     * @returns {Array} - 標準化後的數據
     */
    function normalizeCandlestickData(data) {
        if (!Array.isArray(data)) return [];
        
        return data.map(item => {
            try {
                if (!item || typeof item !== 'object') return null;
                
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
                    
                    if (isNaN(timeValue.getTime())) {
                        console.warn('無效的時間值:', rawTime);
                        return null;
                    }
                } else if (typeof rawTime === 'number') {
                    timeValue = new Date(rawTime);
                } else {
                    console.warn('缺少時間值');
                    return null;
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
                console.error('正規化數據點時出錯:', error, '對應數據:', item);
                return null;
            }
        }).filter(item => item !== null); // 過濾掉處理失敗的項目
    }
    
    /**
     * 生成蠟燭圖範例數據
     * @param {number} count - 數據點數量
     * @returns {Array} - 生成的範例數據
     */
    function generateSampleCandlestickData(count) {
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
    
    // 暴露函數到全局空間，以便Chart.js使用
    window.detectTimeUnit = detectTimeUnit;
    window.validateCandlestickData = validateCandlestickData;
    window.normalizeCandlestickData = normalizeCandlestickData;
    window.generateSampleCandlestickData = generateSampleCandlestickData;
    
    // 對於模組化導入
    if (typeof exports !== 'undefined') {
        exports.detectTimeUnit = detectTimeUnit;
        exports.validateCandlestickData = validateCandlestickData;
        exports.normalizeCandlestickData = normalizeCandlestickData;
        exports.generateSampleCandlestickData = generateSampleCandlestickData;
    }
})();
