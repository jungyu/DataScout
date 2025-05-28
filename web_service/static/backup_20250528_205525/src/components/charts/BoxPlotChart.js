import BaseChart from './BaseChart.js';

/**
 * 箱形圖組件
 * 支援統計分佈資料顯示、四分位數和異常值處理、多組資料比較
 */
export default class BoxPlotChart extends BaseChart {
    constructor() {
        super();
        this.chartType = 'boxPlot';
        this.config = {
            chart: {
                type: 'boxPlot',
                height: 500,
                toolbar: {
                    show: true
                }
            },
            colors: ['#008FFB'],
            plotOptions: {
                boxPlot: {
                    colors: {
                        upper: '#5C4742',
                        lower: '#A5978B'
                    }
                }
            },
            stroke: {
                colors: ['#6E8192']
            },
            fill: {
                opacity: 0.8
            },
            tooltip: {
                shared: false,
                intersect: true
            }
        };
    }

    /**
     * 處理箱形圖資料格式
     * @param {*} data - 輸入資料
     * @returns {Object} 格式化後的配置
     */
    processData(data) {
        try {
            let processedConfig = { ...this.config };
            
            if (Array.isArray(data)) {
                // 如果是簡單陣列，轉換為箱形圖格式
                processedConfig.series = this.convertArrayToBoxPlotSeries(data);
            } else if (data && typeof data === 'object') {
                if (data.series) {
                    processedConfig.series = this.formatBoxPlotSeries(data.series);
                } else {
                    // 假設是鍵值對物件
                    processedConfig.series = this.convertObjectToBoxPlotSeries(data);
                }
                
                // 合併其他配置
                if (data.chart) {
                    processedConfig.chart = { ...processedConfig.chart, ...data.chart };
                }
                if (data.xaxis) {
                    processedConfig.xaxis = data.xaxis;
                }
                if (data.yaxis) {
                    processedConfig.yaxis = data.yaxis;
                }
                if (data.title) {
                    processedConfig.title = data.title;
                }
                if (data.colors) {
                    processedConfig.colors = data.colors;
                }
                if (data.plotOptions) {
                    processedConfig.plotOptions = { 
                        ...processedConfig.plotOptions, 
                        boxPlot: { ...processedConfig.plotOptions.boxPlot, ...data.plotOptions.boxPlot }
                    };
                }
                if (data.tooltip) {
                    processedConfig.tooltip = { ...processedConfig.tooltip, ...data.tooltip };
                }
            } else {
                // 如果沒有有效資料，使用預設範例
                processedConfig.series = this.generateDefaultBoxPlotData();
            }

            // 確保圖表類型
            processedConfig.chart.type = 'boxPlot';
            
            return processedConfig;
        } catch (error) {
            console.error('處理箱形圖資料時發生錯誤:', error);
            const defaultConfig = { ...this.config };
            defaultConfig.series = this.generateDefaultBoxPlotData();
            return defaultConfig;
        }
    }

    /**
     * 轉換陣列為箱形圖系列資料
     * @param {Array} data - 陣列資料
     * @returns {Array} 箱形圖系列資料
     */
    convertArrayToBoxPlotSeries(data) {
        if (data.length === 0) {
            return this.generateDefaultBoxPlotData();
        }

        // 如果是數字陣列，計算統計值
        if (typeof data[0] === 'number') {
            const stats = this.calculateBoxPlotStats(data);
            return [{
                name: '資料分佈',
                type: 'boxPlot',
                data: [{
                    x: '資料集',
                    y: [stats.min, stats.q1, stats.median, stats.q3, stats.max]
                }]
            }];
        }

        // 如果是二維陣列，每個子陣列是一組資料
        if (Array.isArray(data[0])) {
            return [{
                name: '資料分佈',
                type: 'boxPlot',
                data: data.map((dataset, index) => {
                    if (typeof dataset[0] === 'number') {
                        const stats = this.calculateBoxPlotStats(dataset);
                        return {
                            x: `組別 ${index + 1}`,
                            y: [stats.min, stats.q1, stats.median, stats.q3, stats.max]
                        };
                    } else if (dataset.length === 5) {
                        // 假設已經是 [min, q1, median, q3, max] 格式
                        return {
                            x: `組別 ${index + 1}`,
                            y: dataset
                        };
                    }
                    return null;
                }).filter(item => item !== null)
            }];
        }

        return this.generateDefaultBoxPlotData();
    }

    /**
     * 轉換物件為箱形圖系列資料
     * @param {Object} data - 物件資料
     * @returns {Array} 箱形圖系列資料
     */
    convertObjectToBoxPlotSeries(data) {
        const keys = Object.keys(data);
        if (keys.length === 0) {
            return this.generateDefaultBoxPlotData();
        }

        return [{
            name: '資料分佈',
            type: 'boxPlot',
            data: keys.map(key => {
                const values = data[key];
                if (Array.isArray(values)) {
                    if (values.length === 5) {
                        // 假設已經是 [min, q1, median, q3, max] 格式
                        return { x: key, y: values };
                    } else if (values.every(v => typeof v === 'number')) {
                        // 計算統計值
                        const stats = this.calculateBoxPlotStats(values);
                        return {
                            x: key,
                            y: [stats.min, stats.q1, stats.median, stats.q3, stats.max]
                        };
                    }
                }
                return null;
            }).filter(item => item !== null)
        }];
    }

    /**
     * 格式化箱形圖系列資料
     * @param {Array} series - 系列資料
     * @returns {Array} 格式化後的系列資料
     */
    formatBoxPlotSeries(series) {
        if (!Array.isArray(series) || series.length === 0) {
            return this.generateDefaultBoxPlotData();
        }

        return series.map(item => {
            const formattedSeries = {
                name: item.name || '資料分佈',
                type: 'boxPlot',
                data: []
            };

            if (item.data && Array.isArray(item.data)) {
                formattedSeries.data = item.data.map(point => {
                    if (typeof point === 'object' && point.x !== undefined && point.y !== undefined) {
                        return point;
                    } else if (Array.isArray(point) && point.length >= 2) {
                        return { x: point[0], y: point[1] };
                    }
                    return null;
                }).filter(item => item !== null);
            }

            return formattedSeries;
        });
    }

    /**
     * 計算箱形圖統計值
     * @param {Array} values - 數值陣列
     * @returns {Object} 統計值物件
     */
    calculateBoxPlotStats(values) {
        const sorted = [...values].sort((a, b) => a - b);
        const n = sorted.length;
        
        const q1Index = Math.floor(n * 0.25);
        const medianIndex = Math.floor(n * 0.5);
        const q3Index = Math.floor(n * 0.75);
        
        return {
            min: sorted[0],
            q1: sorted[q1Index],
            median: n % 2 === 0 ? (sorted[medianIndex - 1] + sorted[medianIndex]) / 2 : sorted[medianIndex],
            q3: sorted[q3Index],
            max: sorted[n - 1]
        };
    }

    /**
     * 生成預設箱形圖資料
     * @returns {Array} 預設系列資料
     */
    generateDefaultBoxPlotData() {
        return [{
            name: '數據分佈',
            type: 'boxPlot',
            data: [
                {
                    x: 'Q1',
                    y: [54, 66, 69, 75, 88]
                },
                {
                    x: 'Q2', 
                    y: [43, 65, 69, 76, 81]
                },
                {
                    x: 'Q3',
                    y: [31, 39, 45, 51, 59]
                },
                {
                    x: 'Q4',
                    y: [39, 46, 55, 65, 71]
                }
            ]
        }];
    }

    /**
     * 獲取預設範例配置
     * @returns {Object} 範例配置
     */
    getExamples() {
        return {
            basic: {
                title: { 
                    text: '基本箱形圖',
                    align: 'center'
                },
                series: this.generateDefaultBoxPlotData(),
                colors: ['#008FFB'],
                yaxis: {
                    title: {
                        text: '分數'
                    }
                }
            },
            multiSeries: {
                title: { 
                    text: '多系列箱形圖比較',
                    align: 'center'
                },
                series: [
                    {
                        name: '產品 A',
                        type: 'boxPlot',
                        data: [
                            { x: '一月', y: [45, 55, 62, 68, 75] },
                            { x: '二月', y: [48, 58, 65, 70, 78] },
                            { x: '三月', y: [50, 60, 67, 72, 80] },
                            { x: '四月', y: [52, 62, 69, 74, 82] }
                        ]
                    },
                    {
                        name: '產品 B',
                        type: 'boxPlot',
                        data: [
                            { x: '一月', y: [40, 50, 57, 63, 70] },
                            { x: '二月', y: [42, 52, 59, 65, 72] },
                            { x: '三月', y: [44, 54, 61, 67, 74] },
                            { x: '四月', y: [46, 56, 63, 69, 76] }
                        ]
                    }
                ],
                colors: ['#008FFB', '#00E396'],
                yaxis: {
                    title: {
                        text: '銷售額'
                    }
                }
            },
            performance: {
                title: { 
                    text: '績效評估分佈',
                    align: 'center'
                },
                series: [{
                    name: '員工績效',
                    type: 'boxPlot',
                    data: [
                        { x: '業務部', y: [60, 70, 75, 80, 90] },
                        { x: '技術部', y: [65, 73, 78, 83, 92] },
                        { x: '行銷部', y: [58, 68, 73, 78, 88] },
                        { x: '人資部', y: [62, 71, 76, 81, 89] },
                        { x: '財務部', y: [64, 72, 77, 82, 91] }
                    ]
                }],
                colors: ['#FF4560'],
                plotOptions: {
                    boxPlot: {
                        colors: {
                            upper: '#FF4560',
                            lower: '#FFA5A5'
                        }
                    }
                },
                yaxis: {
                    title: {
                        text: '績效分數'
                    },
                    min: 50,
                    max: 100
                }
            },
            temperature: {
                title: { 
                    text: '月度溫度分佈',
                    align: 'center'
                },
                series: [{
                    name: '溫度分佈',
                    type: 'boxPlot',
                    data: this.generateTemperatureData()
                }],
                colors: ['#FEB019'],
                yaxis: {
                    title: {
                        text: '溫度 (°C)'
                    }
                }
            }
        };
    }

    /**
     * 生成溫度資料範例
     * @returns {Array} 溫度箱形圖資料
     */
    generateTemperatureData() {
        const months = ['一月', '二月', '三月', '四月', '五月', '六月', 
                       '七月', '八月', '九月', '十月', '十一月', '十二月'];
        const baseTemps = [5, 8, 15, 22, 28, 32, 35, 33, 28, 20, 12, 7];
        
        return months.map((month, index) => {
            const baseTemp = baseTemps[index];
            const variation = 5;
            return {
                x: month,
                y: [
                    baseTemp - variation,     // min
                    baseTemp - variation/2,   // q1
                    baseTemp,                 // median
                    baseTemp + variation/2,   // q3
                    baseTemp + variation      // max
                ]
            };
        });
    }

    /**
     * 添加新的資料系列
     * @param {String} name - 系列名稱
     * @param {Array} data - 系列資料
     */
    addSeries(name, data) {
        if (this.chart) {
            const formattedData = {
                name: name,
                type: 'boxPlot',
                data: data
            };
            this.chart.appendSeries(formattedData);
        }
    }

    /**
     * 移除指定系列
     * @param {String} seriesName - 要移除的系列名稱
     */
    removeSeries(seriesName) {
        if (this.chart) {
            // 找到系列索引
            const seriesIndex = this.chart.w.config.series.findIndex(s => s.name === seriesName);
            if (seriesIndex !== -1) {
                this.chart.hideSeries(seriesName);
            }
        }
    }

    /**
     * 更新箱形圖資料
     * @param {Array} newSeries - 新的系列資料
     * @param {boolean} animate - 是否動畫
     */
    updateSeries(newSeries, animate = true) {
        if (this.chart) {
            const formattedSeries = this.formatBoxPlotSeries(newSeries);
            this.chart.updateSeries(formattedSeries, animate);
        }
    }

    /**
     * 設定 Y 軸範圍
     * @param {number} min - 最小值
     * @param {number} max - 最大值
     */
    setYAxisRange(min, max) {
        if (this.chart) {
            this.chart.updateOptions({
                yaxis: {
                    min: min,
                    max: max
                }
            });
        }
    }
}

// 向後相容的全域處理函數
window.handleBoxplotChart = function(data) {
    console.log('使用新的 BoxPlotChart 組件處理箱形圖');
    
    const chartContainer = document.getElementById('boxplotChart');
    if (!chartContainer) {
        console.error('找不到箱形圖容器元素 #boxplotChart');
        return false;
    }

    try {
        const boxplotChart = new BoxPlotChart();
        boxplotChart.render(chartContainer, data);
        
        // 保存實例以供後續使用
        window.boxplotChartInstances = window.boxplotChartInstances || {};
        window.boxplotChartInstances['boxplotChart'] = boxplotChart;
        
        return true;
    } catch (error) {
        console.error('渲染箱形圖時發生錯誤:', error);
        return false;
    }
};

// 初始化箱形圖
window.initBoxplotChart = function() {
    console.log('初始化箱形圖...');
    const boxplotChart = new BoxPlotChart();
    const examples = boxplotChart.getExamples();
    window.handleBoxplotChart(examples.basic);
};

// 載入箱形圖資料
window.loadBoxplotData = function(dataType = 'default') {
    console.log(`載入箱形圖資料 (類型: ${dataType})`);
    const boxplotChart = new BoxPlotChart();
    const examples = boxplotChart.getExamples();
    
    let exampleData;
    switch (dataType.toLowerCase()) {
        case 'multiseries':
            exampleData = examples.multiSeries;
            break;
        case 'performance':
            exampleData = examples.performance;
            break;
        case 'temperature':
            exampleData = examples.temperature;
            break;
        case 'default':
        default:
            exampleData = examples.basic;
    }
    
    window.handleBoxplotChart(exampleData);
};

// 獲取箱形圖範例
window.getBoxplotChartExamples = function() {
    const boxplotChart = new BoxPlotChart();
    return boxplotChart.getExamples();
};
