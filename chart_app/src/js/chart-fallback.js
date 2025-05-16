/**
 * 圖表降級處理模組 - 處理當特定圖表類型無法顯示時的替代方案
 */

/**
 * 將蠟燭圖數據轉換為折線圖數據
 * @param {Array} ohlcData - OHLC數據
 * @param {string} valueType - 要使用的值類型（'o','h','l','c'）
 * @returns {Array} 折線圖數據
 */
export function convertOHLCToLineData(ohlcData, valueType = 'c') {
    if (!Array.isArray(ohlcData)) {
        return [];
    }

    return ohlcData.map(item => {
        // 選擇要使用的值
        let value;
        switch (valueType) {
            case 'o': value = item.o || item.open; break;
            case 'h': value = item.h || item.high; break;
            case 'l': value = item.l || item.low; break;
            default: value = item.c || item.close; break;
        }

        // 處理日期
        const timestamp = item.t || item.x || item.time || item.date;
        const date = timestamp instanceof Date ? timestamp : new Date(timestamp);

        return {
            x: date,
            y: value
        };
    });
}

/**
 * 生成簡單的折線圖配置，用於替代無法顯示的圖表類型
 * @param {Object} data - 原始圖表數據
 * @param {string} title - 圖表標題
 * @returns {Object} Chart.js配置對象
 */
export function createBasicLineChart(data, title = '圖表') {
    // 嘗試從各種可能的數據結構中提取數據
    let finalData = [];

    if (Array.isArray(data)) {
        finalData = data;
    } else if (data.datasets && Array.isArray(data.datasets)) {
        if (data.datasets[0] && Array.isArray(data.datasets[0].data)) {
            finalData = data.datasets[0].data;
        }
    } else if (data.data && Array.isArray(data.data)) {
        finalData = data.data;
    } else if (data.data && data.data.datasets && Array.isArray(data.data.datasets)) {
        if (data.data.datasets[0] && Array.isArray(data.data.datasets[0].data)) {
            finalData = data.data.datasets[0].data;
        }
    }

    // 確定資料是否可能是OHLC格式
    const isOHLC = finalData.length > 0 && (
        finalData[0].o !== undefined || finalData[0].open !== undefined
    );

    // 如果是OHLC資料，轉換為折線圖格式
    if (isOHLC) {
        finalData = convertOHLCToLineData(finalData);
    }

    // 如果仍然沒有數據，生成一些虛擬數據
    if (!finalData.length) {
        finalData = Array.from({ length: 10 }, (_, i) => ({
            x: new Date(Date.now() + i * 86400000),
            y: Math.random() * 100
        }));
    }

    // 建立折線圖配置
    return {
        type: 'line',
        data: {
            datasets: [{
                label: title,
                data: finalData,
                borderColor: 'rgb(75, 192, 192)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                tension: 0.1,
                pointRadius: 3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: title + ' (備用視圖)'
                },
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            }
        }
    };
}

/**
 * 生成範例蠟燭圖數據
 * @param {number} pointCount - 資料點數量
 * @returns {Array} 蠟燭圖數據
 */
export function generateSampleOHLCData(pointCount = 30) {
    const data = [];
    let price = 100;
    const today = new Date();

    for (let i = 0; i < pointCount; i++) {
        const volatility = (Math.random() * 10 - 5) / 100;
        const open = price;
        const close = price * (1 + volatility);
        const high = Math.max(open, close) * (1 + Math.random() * 0.02);
        const low = Math.min(open, close) * (1 - Math.random() * 0.02);

        data.push({
            t: new Date(today.getTime() - (pointCount - i) * 24 * 60 * 60 * 1000),
            o: parseFloat(open.toFixed(2)),
            h: parseFloat(high.toFixed(2)),
            l: parseFloat(low.toFixed(2)),
            c: parseFloat(close.toFixed(2)),
            v: Math.floor(Math.random() * 1000) + 100
        });

        price = close;
    }

    return data;
}
