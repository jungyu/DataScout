import BaseChart from './BaseChart.js';

/**
 * 熱力圖組件
 * 支援矩陣資料顯示、時間序列熱力圖和多色彩範圍
 */
export default class HeatMapChart extends BaseChart {
    constructor() {
        super();
        this.chartType = 'heatmap';
        this.config = {
            chart: {
                type: 'heatmap',
                height: 350,
                toolbar: {
                    show: true
                }
            },
            dataLabels: {
                enabled: false
            },
            colors: ["#3B82F6"],
            stroke: {
                width: 0
            },
            plotOptions: {
                heatmap: {
                    shadeIntensity: 0.5,
                    radius: 0,
                    useFillColorAsStroke: true,
                    colorScale: {
                        ranges: [{
                            from: 0,
                            to: 25,
                            color: '#00A100',
                            name: '低'
                        }, {
                            from: 26,
                            to: 50,
                            color: '#128FD9',
                            name: '中等'
                        }, {
                            from: 51,
                            to: 75,
                            color: '#FFB200',
                            name: '高'
                        }, {
                            from: 76,
                            to: 100,
                            color: '#FF0000',
                            name: '極高'
                        }]
                    }
                }
            },
            grid: {
                padding: {
                    right: 20
                }
            },
            tooltip: {
                y: {
                    formatter: function(val) {
                        return val;
                    }
                }
            }
        };
    }

    /**
     * 處理熱力圖資料格式
     * @param {*} data - 輸入資料
     * @returns {Object} 格式化後的配置
     */
    processData(data) {
        try {
            let processedConfig = { ...this.config };
            
            if (Array.isArray(data)) {
                // 如果是簡單陣列，轉換為熱力圖格式
                processedConfig.series = this.convertArrayToHeatmapSeries(data);
            } else if (data && typeof data === 'object') {
                if (data.series) {
                    processedConfig.series = this.formatHeatmapSeries(data.series);
                } else {
                    // 假設是鍵值對物件
                    processedConfig.series = this.convertObjectToHeatmapSeries(data);
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
                        heatmap: { ...processedConfig.plotOptions.heatmap, ...data.plotOptions.heatmap }
                    };
                }
                if (data.tooltip) {
                    processedConfig.tooltip = { ...processedConfig.tooltip, ...data.tooltip };
                }
            } else {
                // 如果沒有有效資料，使用預設範例
                processedConfig.series = this.generateDefaultHeatmapData();
            }

            // 確保圖表類型
            processedConfig.chart.type = 'heatmap';
            
            return processedConfig;
        } catch (error) {
            console.error('處理熱力圖資料時發生錯誤:', error);
            const defaultConfig = { ...this.config };
            defaultConfig.series = this.generateDefaultHeatmapData();
            return defaultConfig;
        }
    }

    /**
     * 轉換陣列為熱力圖系列資料
     * @param {Array} data - 陣列資料
     * @returns {Array} 熱力圖系列資料
     */
    convertArrayToHeatmapSeries(data) {
        if (data.length === 0) {
            return this.generateDefaultHeatmapData();
        }

        // 如果第一個元素是數字，建立單一系列
        if (typeof data[0] === 'number') {
            const categories = data.map((_, index) => `項目 ${index + 1}`);
            return [{
                name: '資料系列',
                data: data.map((value, index) => ({
                    x: categories[index],
                    y: value
                }))
            }];
        }

        // 如果是物件陣列
        if (Array.isArray(data[0])) {
            return data.map((row, rowIndex) => ({
                name: `行 ${rowIndex + 1}`,
                data: row.map((value, colIndex) => ({
                    x: `列 ${colIndex + 1}`,
                    y: value
                }))
            }));
        }

        return this.generateDefaultHeatmapData();
    }

    /**
     * 轉換物件為熱力圖系列資料
     * @param {Object} data - 物件資料
     * @returns {Array} 熱力圖系列資料
     */
    convertObjectToHeatmapSeries(data) {
        const keys = Object.keys(data);
        if (keys.length === 0) {
            return this.generateDefaultHeatmapData();
        }

        // 如果值是陣列，每個鍵作為一個系列
        if (Array.isArray(data[keys[0]])) {
            return keys.map(key => ({
                name: key,
                data: data[key].map((value, index) => ({
                    x: `項目 ${index + 1}`,
                    y: value
                }))
            }));
        }

        // 如果值是數字，建立單一系列
        return [{
            name: '資料系列',
            data: keys.map(key => ({
                x: key,
                y: data[key]
            }))
        }];
    }

    /**
     * 格式化熱力圖系列資料
     * @param {Array} series - 系列資料
     * @returns {Array} 格式化後的系列資料
     */
    formatHeatmapSeries(series) {
        if (!Array.isArray(series) || series.length === 0) {
            return this.generateDefaultHeatmapData();
        }

        return series.map(item => {
            if (!item.data) {
                return {
                    name: item.name || '系列',
                    data: []
                };
            }

            const formattedData = item.data.map(point => {
                if (typeof point === 'object' && point.x !== undefined && point.y !== undefined) {
                    return point;
                } else if (Array.isArray(point) && point.length >= 2) {
                    return { x: point[0], y: point[1] };
                } else {
                    return { x: '未知', y: point || 0 };
                }
            });

            return {
                name: item.name || '系列',
                data: formattedData
            };
        });
    }

    /**
     * 生成預設熱力圖資料
     * @returns {Array} 預設系列資料
     */
    generateDefaultHeatmapData() {
        const categories = ['00:00', '01:00', '02:00', '03:00', '04:00', '05:00', '06:00', '07:00', '08:00', '09:00', '10:00', '11:00'];
        const series = [];
        
        for (let i = 0; i < 8; i++) {
            const data = [];
            for (let j = 0; j < categories.length; j++) {
                data.push({
                    x: categories[j],
                    y: Math.floor(Math.random() * 100) + 10
                });
            }
            series.push({
                name: `項目 ${i + 1}`,
                data: data
            });
        }
        
        return series;
    }

    /**
     * 獲取預設範例配置
     * @returns {Object} 範例配置
     */
    getExamples() {
        return {
            basic: {
                title: { text: '基本熱力圖' },
                series: this.generateDefaultHeatmapData(),
                colors: ["#3B82F6"],
                plotOptions: {
                    heatmap: {
                        shadeIntensity: 0.5,
                        colorScale: {
                            ranges: [{
                                from: 0,
                                to: 25,
                                color: '#00A100',
                                name: '低'
                            }, {
                                from: 26,
                                to: 50,
                                color: '#128FD9',
                                name: '中等'
                            }, {
                                from: 51,
                                to: 75,
                                color: '#FFB200',
                                name: '高'
                            }, {
                                from: 76,
                                to: 100,
                                color: '#FF0000',
                                name: '極高'
                            }]
                        }
                    }
                },
                tooltip: {
                    y: {
                        formatter: function(val) {
                            return val + " 單位";
                        }
                    }
                }
            },
            colorRange: {
                title: { text: '多色熱力圖' },
                series: this.generateDefaultHeatmapData(),
                colors: ["#F3B415", "#F27036", "#663F59", "#6A6E94", "#4E88B4", "#00A7C6", "#18D8D8"],
                plotOptions: {
                    heatmap: {
                        shadeIntensity: 0.5,
                        distributed: false
                    }
                },
                tooltip: {
                    y: {
                        formatter: function(val) {
                            return val + " 點";
                        }
                    }
                }
            },
            temperature: {
                title: { text: '溫度分佈熱力圖' },
                series: this.generateTemperatureData(),
                colors: ["#FF0000"],
                plotOptions: {
                    heatmap: {
                        shadeIntensity: 0.5,
                        colorScale: {
                            ranges: [{
                                from: 0,
                                to: 10,
                                color: '#0000FF',
                                name: '冷'
                            }, {
                                from: 11,
                                to: 20,
                                color: '#00FFFF',
                                name: '涼'
                            }, {
                                from: 21,
                                to: 30,
                                color: '#00FF00',
                                name: '適中'
                            }, {
                                from: 31,
                                to: 40,
                                color: '#FFFF00',
                                name: '溫暖'
                            }, {
                                from: 41,
                                to: 50,
                                color: '#FF0000',
                                name: '熱'
                            }]
                        }
                    }
                },
                tooltip: {
                    y: {
                        formatter: function(val) {
                            return val + "°C";
                        }
                    }
                }
            }
        };
    }

    /**
     * 生成溫度資料範例
     * @returns {Array} 溫度系列資料
     */
    generateTemperatureData() {
        const hours = Array.from({length: 24}, (_, i) => String(i).padStart(2, '0') + ':00');
        const days = ['週一', '週二', '週三', '週四', '週五', '週六', '週日'];
        
        return days.map(day => ({
            name: day,
            data: hours.map(hour => ({
                x: hour,
                y: Math.floor(Math.random() * 40) + 5 // 5-45度溫度範圍
            }))
        }));
    }

    /**
     * 設定色彩範圍
     * @param {Array} colorRanges - 色彩範圍配置
     */
    setColorRanges(colorRanges) {
        if (this.chart && this.chart.w) {
            const newOptions = {
                plotOptions: {
                    heatmap: {
                        colorScale: {
                            ranges: colorRanges
                        }
                    }
                }
            };
            this.chart.updateOptions(newOptions);
        }
    }

    /**
     * 更新熱力圖資料
     * @param {Array} newSeries - 新的系列資料
     * @param {boolean} animate - 是否動畫
     */
    updateSeries(newSeries, animate = true) {
        if (this.chart) {
            const formattedSeries = this.formatHeatmapSeries(newSeries);
            this.chart.updateSeries(formattedSeries, animate);
        }
    }
}

// 向後相容的全域處理函數
window.handleHeatmapChart = function(data) {
    console.log('使用新的 HeatMapChart 組件處理熱力圖');
    
    const chartContainer = document.getElementById('heatmapChart');
    if (!chartContainer) {
        console.error('找不到熱力圖容器元素 #heatmapChart');
        return false;
    }

    try {
        const heatmapChart = new HeatMapChart();
        heatmapChart.render(chartContainer, data);
        
        // 保存實例以供後續使用
        window.heatmapChartInstances = window.heatmapChartInstances || {};
        window.heatmapChartInstances['heatmapChart'] = heatmapChart;
        
        return true;
    } catch (error) {
        console.error('渲染熱力圖時發生錯誤:', error);
        return false;
    }
};

// 初始化熱力圖
window.initHeatmapChart = function() {
    console.log('初始化熱力圖...');
    const heatmapChart = new HeatMapChart();
    const examples = heatmapChart.getExamples();
    window.handleHeatmapChart(examples.basic);
};

// 載入熱力圖資料
window.loadHeatmapData = function(dataType = 'default') {
    console.log(`載入熱力圖資料 (類型: ${dataType})`);
    const heatmapChart = new HeatMapChart();
    const examples = heatmapChart.getExamples();
    
    let exampleData;
    switch (dataType.toLowerCase()) {
        case 'temperature':
            exampleData = examples.temperature;
            break;
        case 'colorrange':
            exampleData = examples.colorRange;
            break;
        case 'default':
        default:
            exampleData = examples.basic;
    }
    
    window.handleHeatmapChart(exampleData);
};

// 獲取熱力圖範例
window.getHeatmapChartExamples = function() {
    const heatmapChart = new HeatMapChart();
    return heatmapChart.getExamples();
};
