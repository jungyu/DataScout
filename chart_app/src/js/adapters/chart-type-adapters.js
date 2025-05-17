/**
 * 圖表類型適配器模組
 * 處理各種特殊圖表類型的資料轉換與格式化，支援財務圖表、混合圖表等
 */

/**
 * 圖表類型適配器類別 - 提供所有圖表類型的統一介面
 */
export class ChartTypeAdapter {
    /**
     * 根據圖表類型獲取適配器
     * @param {string} chartType - 圖表類型
     * @returns {Object} - 適配器物件
     */
    static getAdapter(chartType) {
        switch (chartType.toLowerCase()) {
            case 'candlestick':
            case 'ohlc':
                return new FinancialChartAdapter();
            case 'sankey':
                return new SankeyChartAdapter();
            case 'mixed':
                return new MixedChartAdapter();
            case 'butterfly':
                return new ButterflyChartAdapter();
            default:
                return new BaseChartAdapter();
        }
    }
    
    /**
     * 驗證圖表資料
     * @param {Object} data - 圖表資料
     * @returns {boolean} - 是否合法
     */
    validateData(data) {
        // 基礎驗證邏輯
        return data && (data.datasets || data.data);
    }
    
    /**
     * 轉換資料為所需格式
     * @param {Object} data - 原始資料
     * @returns {Object} - 處理後的資料
     */
    transformData(data) {
        // 基礎轉換邏輯
        return data;
    }
    
    /**
     * 獲取圖表配置
     * @returns {Object} - 圖表配置
     */
    getChartConfig() {
        // 基礎配置
        return {};
    }
}

/**
 * 基礎圖表適配器 - 適用於標準圖表型別
 */
export class BaseChartAdapter extends ChartTypeAdapter {
    validateData(data) {
        return super.validateData(data);
    }
    
    transformData(data) {
        // 如果數據已經是 Chart.js 格式，直接返回
        if (data && data.datasets && Array.isArray(data.datasets)) {
            return data;
        }
        
        // 如果只是一個簡單的數據陣列，轉換為 Chart.js 格式
        if (Array.isArray(data)) {
            return {
                labels: data.map((_, index) => `項目 ${index + 1}`),
                datasets: [{
                    label: '資料系列',
                    data: data
                }]
            };
        }
        
        return data;
    }
    
    getChartConfig() {
        return {
            responsive: true,
            maintainAspectRatio: false
        };
    }
}

/**
 * 財務圖表適配器 - 處理蠟燭圖和 OHLC 圖
 */
export class FinancialChartAdapter extends ChartTypeAdapter {
    /**
     * 驗證蠟燭圖資料格式
     * @param {Array} data - 蠟燭圖資料
     * @returns {boolean} 是否為有效的蠟燭圖資料
     */
    validateData(data) {
        if (!Array.isArray(data) || data.length === 0) {
            console.error('財務圖表資料必須是非空陣列');
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
            console.error('財務圖表資料缺少必要的 OHLC 欄位');
            return false;
        }
        
        if (!hasTime) {
            console.error('財務圖表資料缺少必要的時間欄位');
            return false;
        }
        
        return true;
    }
    
    /**
     * 標準化蠟燭圖資料
     * @param {Array} data - 原始蠟燭圖資料
     * @returns {Object} 標準化的資料
     */
    transformData(data) {
        if (!this.validateData(data)) {
            return { datasets: [] };
        }
        
        // 獲取時間單位
        const timeUnit = this.detectTimeUnit(data);
        
        // 標準化資料，確保時間格式一致
        const normalizedData = data.map(item => {
            // 處理不同的時間欄位
            let time;
            if (item.t !== undefined) time = item.t;
            else if (item.x !== undefined) time = item.x;
            else if (item.time !== undefined) time = item.time;
            else if (item.date !== undefined) time = item.date;
            
            // 確保時間為 Date 物件
            let timeObj;
            if (typeof time === 'string') {
                timeObj = new Date(time);
            } else if (time instanceof Date) {
                timeObj = time;
            } else {
                // 如果是時間戳
                timeObj = new Date(time);
            }
            
            return {
                t: timeObj,
                o: item.o,
                h: item.h,
                l: item.l,
                c: item.c,
                v: item.v || 0 // 成交量，如果有的話
            };
        });
        
        // 建立 Chart.js 資料格式
        return {
            datasets: [{
                label: '價格',
                data: normalizedData
            }]
        };
    }
    
    /**
     * 檢測時間資料的單位
     * @param {Array} data - OHLC 資料
     * @returns {string} 時間單位 (day, hour, minute, second)
     */
    detectTimeUnit(data) {
        if (!Array.isArray(data) || data.length < 2) {
            return 'day'; // 默認為天
        }
        
        // 獲取前兩個時間點
        let time1, time2;
        
        // 處理不同的時間欄位
        if (data[0].t !== undefined) {
            time1 = new Date(data[0].t);
            time2 = new Date(data[1].t);
        } else if (data[0].x !== undefined) {
            time1 = new Date(data[0].x);
            time2 = new Date(data[1].x);
        } else if (data[0].time !== undefined) {
            time1 = new Date(data[0].time);
            time2 = new Date(data[1].time);
        } else if (data[0].date !== undefined) {
            time1 = new Date(data[0].date);
            time2 = new Date(data[1].date);
        } else {
            return 'day';
        }
        
        // 計算時間差 (毫秒)
        const diffMs = Math.abs(time2 - time1);
        
        // 根據時間差判斷單位
        if (diffMs < 1000 * 60) {
            return 'second'; // 小於 1 分鐘
        } else if (diffMs < 1000 * 60 * 60) {
            return 'minute'; // 小於 1 小時
        } else if (diffMs < 1000 * 60 * 60 * 24) {
            return 'hour'; // 小於 1 天
        } else if (diffMs < 1000 * 60 * 60 * 24 * 7) {
            return 'day'; // 小於 1 週
        } else if (diffMs < 1000 * 60 * 60 * 24 * 30) {
            return 'week'; // 小於 1 個月
        } else if (diffMs < 1000 * 60 * 60 * 24 * 365) {
            return 'month'; // 小於 1 年
        } else {
            return 'year'; // 大於 1 年
        }
    }
    
    /**
     * 獲取蠟燭圖配置
     * @returns {Object} 圖表配置
     */
    getChartConfig() {
        return {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'day',
                        displayFormats: {
                            day: 'MMM d'
                        }
                    },
                    title: {
                        display: true,
                        text: '日期'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: '價格'
                    }
                }
            }
        };
    }
}

/**
 * 桑基圖表適配器 - 處理桑基(Sankey)圖
 */
export class SankeyChartAdapter extends ChartTypeAdapter {
    validateData(data) {
        if (!data || !data.nodes || !data.links) {
            console.error('桑基圖資料必須包含 nodes 和 links 欄位');
            return false;
        }
        
        return true;
    }
    
    transformData(data) {
        if (!this.validateData(data)) {
            return { data: { datasets: [{ data: [] }] } };
        }
        
        // 已標準化的桑基圖資料
        if (data.data && data.data.datasets) {
            return data;
        }
        
        // 標準化資料
        return {
            data: {
                datasets: [{
                    label: '桑基圖',
                    data: data.links.map(link => ({
                        source: link.source,
                        target: link.target,
                        value: link.value || link.weight || 1
                    }))
                }]
            },
            options: {
                ...this.getChartConfig()
            }
        };
    }
    
    getChartConfig() {
        return {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                tooltip: {
                    callbacks: {
                        title: items => {
                            return '';
                        },
                        label: context => {
                            return `${context.raw.source} → ${context.raw.target}: ${context.raw.value}`;
                        }
                    }
                },
                legend: {
                    display: false
                }
            }
        };
    }
}

/**
 * 混合圖表適配器 - 處理包含多種圖表類型的組合
 */
export class MixedChartAdapter extends ChartTypeAdapter {
    validateData(data) {
        if (!data || !data.datasets || !Array.isArray(data.datasets)) {
            console.error('混合圖表資料必須包含 datasets 陣列');
            return false;
        }
        
        // 檢查每個數據集是否指定了圖表類型
        const allHaveType = data.datasets.every(dataset => dataset.type);
        if (!allHaveType) {
            console.warn('混合圖表中的某些數據集未指定圖表類型，將使用默認類型');
        }
        
        return true;
    }
    
    transformData(data) {
        if (!this.validateData(data)) {
            return { datasets: [] };
        }
        
        // 確保每個數據集都有圖表類型
        const processedData = { ...data };
        processedData.datasets = data.datasets.map(dataset => {
            return {
                ...dataset,
                type: dataset.type || 'line'  // 默認使用折線圖
            };
        });
        
        return processedData;
    }
    
    getChartConfig() {
        return {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                tooltip: {
                    mode: 'index',
                    intersect: false
                },
                legend: {
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        };
    }
}

/**
 * 蝴蝶圖(人口金字塔)適配器
 */
export class ButterflyChartAdapter extends ChartTypeAdapter {
    validateData(data) {
        if (!data || !data.datasets || !Array.isArray(data.datasets) || data.datasets.length < 2) {
            console.error('蝴蝶圖必須包含至少兩個數據集');
            return false;
        }
        
        return true;
    }
    
    transformData(data) {
        if (!this.validateData(data)) {
            return { datasets: [] };
        }
        
        // 蝴蝶圖特殊處理：確保一側為負值
        const processedData = { ...data };
        
        // 只處理第一個數據集，將其值轉為負數
        if (processedData.datasets && processedData.datasets.length >= 2) {
            processedData.datasets[0].data = processedData.datasets[0].data.map(value => 
                typeof value === 'number' ? -Math.abs(value) : value
            );
        }
        
        return processedData;
    }
    
    getChartConfig() {
        return {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            scales: {
                x: {
                    ticks: {
                        callback: function(value) {
                            return Math.abs(value);
                        }
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const value = context.raw;
                            return `${context.dataset.label}: ${Math.abs(value)}`;
                        }
                    }
                }
            }
        };
    }
}
