/**
 * 蠟燭圖輔助模組 - 提供蠟燭圖資料處理與轉換功能
 */

/**
 * 驗證蠟燭圖資料格式
 * @param {Array} data - 蠟燭圖資料
 * @returns {boolean} 是否為有效的蠟燭圖資料
 */
export function validateCandlestickData(data) {
    if (!Array.isArray(data) || data.length === 0) {
        console.error('蠟燭圖資料必須是非空陣列');
        return false;
    }
    
    // 檢查第一個元素，判斷資料格式
    const sample = data[0];
    
    // 檢查必要的 OHLC 欄位
    const hasOHLC = sample && 
                   typeof sample.o === 'number' && 
                   typeof sample.h === 'number' && 
                   typeof sample.l === 'number' && 
                   typeof sample.c === 'number';
                   
    // 檢查時間欄位 (支援多種格式)
    const hasTime = sample && (
                   sample.t !== undefined || 
                   sample.x !== undefined || 
                   sample.time !== undefined || 
                   sample.date !== undefined);
    
    if (!hasOHLC) {
        console.error('蠟燭圖資料缺少必要的 OHLC 欄位');
        console.debug('資料樣本:', sample);
        return false;
    }
    
    if (!hasTime) {
        console.error('蠟燭圖資料缺少必要的時間欄位');
        console.debug('資料樣本:', sample);
        return false;
    }
    
    return true;
}

/**
 * 標準化蠟燭圖資料
 * @param {Array} data - 原始蠟燭圖資料
 * @returns {Array} 標準化後的蠟燭圖資料
 */
export function normalizeCandlestickData(data) {
    if (!Array.isArray(data)) return [];
    
    return data.map(item => {
        if (!item) return null;
        
        // 標準化時間欄位
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
}

/**
 * 自動檢測蠟燭圖時間間隔並建議合適的時間單位
 * @param {Array} data - 蠟燭圖資料
 * @returns {string} Chart.js 時間單位
 */
export function detectTimeUnit(data) {
    if (!Array.isArray(data) || data.length < 2) {
        return 'day';  // 預設
    }
    
    try {
        // 對資料按時間排序
        const sortedData = [...data].sort((a, b) => {
            const dateA = a.t instanceof Date ? a.t : new Date(a.t);
            const dateB = b.t instanceof Date ? b.t : new Date(b.t);
            return dateA - dateB;
        });
        
        const firstDate = new Date(sortedData[0].t);
        const lastDate = new Date(sortedData[sortedData.length - 1].t);
        const timeSpan = lastDate - firstDate;
        
        // 避免除以零
        if (sortedData.length <= 1) {
            return 'day';
        }
        
        // 計算平均間隔
        const avgInterval = timeSpan / (sortedData.length - 1);
        
        // 根據平均間隔決定時間單位
        if (avgInterval < 60000) return 'second';        // 小於1分鐘，使用秒
        if (avgInterval < 3600000) return 'minute';      // 小於1小時，使用分鐘
        if (avgInterval < 86400000) return 'hour';       // 小於1天，使用小時
        if (avgInterval < 604800000) return 'day';       // 小於1週，使用天
        if (avgInterval < 2592000000) return 'week';     // 小於1月，使用週
        if (avgInterval < 31536000000) return 'month';   // 小於1年，使用月
        return 'year';                                  // 大於1年，使用年
    } catch (error) {
        console.warn('決定時間單位時出錯:', error);
        return 'day';  // 錯誤時使用預設值
    }
}
