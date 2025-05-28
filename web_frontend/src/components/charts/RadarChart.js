/**
 * 雷達圖組件 - Alpine.js 實現
 * 繼承自 BaseChart，專門處理雷達圖的渲染和交互
 * 
 * 功能特色：
 * - 支援多維度資料展示
 * - 可配置的多邊形樣式
 * - 多系列比較功能
 * - 自動類別標籤處理
 * - 動態數值範圍調整
 */

import BaseChart from './BaseChart.js';

class RadarChart extends BaseChart {
    constructor() {
        super();
        
        // 雷達圖特有的配置
        this.defaultConfig = {
            chart: {
                type: 'radar',
                height: 350,
                animations: {
                    enabled: true,
                    easing: 'easeinout',
                    speed: 800
                },
                toolbar: {
                    show: true,
                    tools: {
                        download: true,
                        reset: true
                    }
                }
            },
            series: [],
            xaxis: {
                categories: []
            },
            yaxis: {
                show: true,
                tickAmount: 4,
                labels: {
                    formatter: function(val) {
                        return Math.round(val);
                    }
                },
                min: 0,
                max: 100
            },
            plotOptions: {
                radar: {
                    size: 140,
                    polygons: {
                        strokeColors: '#e9e9e9',
                        strokeWidth: 1,
                        connectorColors: '#d0d0d0',
                        fill: {
                            colors: ['#f8f9fa', '#f1f3f4']
                        }
                    }
                }
            },
            fill: {
                opacity: 0.1
            },
            stroke: {
                show: true,
                width: 2
            },
            markers: {
                size: 4,
                colors: ['#fff'],
                strokeColors: '#ff8c00',
                strokeWidth: 2
            },
            legend: {
                show: true,
                position: 'top',
                horizontalAlign: 'left'
            },
            tooltip: {
                y: {
                    formatter: function(val) {
                        return val.toString();
                    }
                }
            }
        };
    }

    /**
     * 處理雷達圖專用的資料格式轉換
     * @param {Array|Object} data - 輸入資料
     * @returns {Object} - 格式化後的圖表配置
     */
    processRadarData(data) {
        if (!data) {
            console.warn('雷達圖資料為空，使用預設樣本資料');
            return this.getExampleData().basic;
        }

        // 如果已經是完整的圖表配置
        if (data.chart && data.series && data.xaxis) {
            return {
                ...this.defaultConfig,
                ...data,
                chart: { ...this.defaultConfig.chart, ...data.chart }
            };
        }

        // 如果是系列資料格式
        if (Array.isArray(data) && data.length > 0 && data[0].name && data[0].data) {
            return {
                ...this.defaultConfig,
                series: data.map(series => ({
                    name: series.name,
                    data: this.normalizeRadarData(series.data)
                })),
                xaxis: {
                    categories: this.extractCategories(data)
                }
            };
        }

        // 如果是簡單的資料物件格式 {類別: 數值}
        if (typeof data === 'object' && !Array.isArray(data)) {
            const categories = Object.keys(data);
            const values = Object.values(data).map(val => parseFloat(val) || 0);
            
            return {
                ...this.defaultConfig,
                series: [{
                    name: '數值',
                    data: values
                }],
                xaxis: {
                    categories: categories
                }
            };
        }

        console.warn('無法識別的雷達圖資料格式，使用預設樣本資料');
        return this.getExampleData().basic;
    }

    /**
     * 標準化雷達圖資料
     * @param {Array} data - 原始資料
     * @returns {Array} - 標準化的數值陣列
     */
    normalizeRadarData(data) {
        if (!Array.isArray(data)) return [];

        return data.map(value => {
            if (typeof value === 'number') {
                return value;
            }
            if (typeof value === 'string') {
                return parseFloat(value) || 0;
            }
            if (typeof value === 'object' && value.value !== undefined) {
                return parseFloat(value.value) || 0;
            }
            return 0;
        });
    }

    /**
     * 從系列資料中提取類別標籤
     * @param {Array} seriesData - 系列資料
     * @returns {Array} - 類別標籤陣列
     */
    extractCategories(seriesData) {
        if (!Array.isArray(seriesData) || seriesData.length === 0) {
            return ['類別1', '類別2', '類別3', '類別4', '類別5'];
        }

        const firstSeries = seriesData[0];
        if (firstSeries.categories) {
            return firstSeries.categories;
        }

        // 如果沒有明確的類別標籤，生成預設標籤
        const dataLength = firstSeries.data ? firstSeries.data.length : 5;
        return Array.from({ length: dataLength }, (_, i) => `維度 ${i + 1}`);
    }

    /**
     * 更新雷達圖配置選項
     * @param {Object} options - 配置選項
     */
    updateRadarOptions(options = {}) {
        const config = { ...this.defaultConfig };

        // 處理雷達圖大小
        if (options.size) {
            config.plotOptions.radar.size = options.size;
        }

        // 處理多邊形樣式
        if (options.polygons) {
            config.plotOptions.radar.polygons = {
                ...config.plotOptions.radar.polygons,
                ...options.polygons
            };
        }

        // 處理填充透明度
        if (options.fillOpacity !== undefined) {
            config.fill.opacity = options.fillOpacity;
        }

        // 處理線條樣式
        if (options.stroke) {
            config.stroke = { ...config.stroke, ...options.stroke };
        }

        // 處理標記點樣式
        if (options.markers) {
            config.markers = { ...config.markers, ...options.markers };
        }

        // 處理 Y 軸範圍
        if (options.yAxisMin !== undefined) {
            config.yaxis.min = options.yAxisMin;
        }
        if (options.yAxisMax !== undefined) {
            config.yaxis.max = options.yAxisMax;
        }

        // 處理圖例選項
        if (options.legend) {
            config.legend = { ...config.legend, ...options.legend };
        }

        return config;
    }

    /**
     * 載入並渲染雷達圖
     * @param {Array|Object} data - 資料或配置物件
     * @param {Object} options - 額外選項
     */
    async loadChart(data, options = {}) {
        try {
            this.showLoading();

            const chartConfig = this.processRadarData(data);
            const finalConfig = options ? this.updateRadarOptions(options) : chartConfig;

            // 合併處理後的資料和選項
            if (chartConfig.series) {
                finalConfig.series = chartConfig.series;
            }
            if (chartConfig.xaxis) {
                finalConfig.xaxis = chartConfig.xaxis;
            }

            await this.initChart(finalConfig);
            this.hideLoading();

            this.showNotification('雷達圖載入完成', 'success');

        } catch (error) {
            this.hideLoading();
            console.error('載入雷達圖失敗:', error);
            this.showNotification(`載入雷達圖失敗: ${error.message}`, 'error');
            throw error;
        }
    }

    /**
     * 新增資料系列
     * @param {Object} seriesData - 新的系列資料 {name, data}
     */
    addSeries(seriesData) {
        if (!this.chart) {
            console.error('圖表未初始化');
            return;
        }

        const normalizedData = this.normalizeRadarData(seriesData.data || []);
        
        this.chart.appendSeries({
            name: seriesData.name || `系列 ${Date.now()}`,
            data: normalizedData
        });

        this.showNotification(`已新增系列: ${seriesData.name}`, 'success');
    }

    /**
     * 更新類別標籤
     * @param {Array} categories - 新的類別標籤
     */
    updateCategories(categories) {
        if (!this.chart || !Array.isArray(categories)) {
            console.error('圖表未初始化或類別資料無效');
            return;
        }

        this.chart.updateOptions({
            xaxis: {
                categories: categories
            }
        });

        this.showNotification('已更新類別標籤', 'success');
    }

    /**
     * 設置 Y 軸範圍
     * @param {number} min - 最小值
     * @param {number} max - 最大值
     */
    setYAxisRange(min = 0, max = 100) {
        if (!this.chart) {
            console.error('圖表未初始化');
            return;
        }

        this.chart.updateOptions({
            yaxis: {
                min: min,
                max: max
            }
        });

        this.showNotification(`已設置 Y 軸範圍: ${min} - ${max}`, 'success');
    }

    /**
     * 設置雷達圖大小
     * @param {number} size - 雷達圖大小
     */
    setRadarSize(size = 140) {
        if (!this.chart) {
            console.error('圖表未初始化');
            return;
        }

        this.chart.updateOptions({
            plotOptions: {
                radar: {
                    size: size
                }
            }
        });

        this.showNotification(`已設置雷達圖大小: ${size}`, 'success');
    }

    /**
     * 設置填充透明度
     * @param {number} opacity - 透明度 (0-1)
     */
    setFillOpacity(opacity = 0.1) {
        if (!this.chart) {
            console.error('圖表未初始化');
            return;
        }

        this.chart.updateOptions({
            fill: {
                opacity: opacity
            }
        });

        this.showNotification(`已設置填充透明度: ${opacity}`, 'success');
    }

    /**
     * 生成隨機雷達圖資料
     * @param {Array} categories - 類別標籤
     * @param {number} seriesCount - 系列數量
     * @param {Object} range - 數值範圍
     * @returns {Object} - 雷達圖配置
     */
    generateRandomData(categories = null, seriesCount = 2, range = {min: 0, max: 100}) {
        const defaultCategories = categories || ['技能A', '技能B', '技能C', '技能D', '技能E', '技能F'];
        const series = [];

        for (let i = 0; i < seriesCount; i++) {
            const data = defaultCategories.map(() => {
                return Math.floor(Math.random() * (range.max - range.min + 1)) + range.min;
            });

            series.push({
                name: `系列 ${i + 1}`,
                data: data
            });
        }

        return {
            series: series,
            xaxis: {
                categories: defaultCategories
            }
        };
    }

    /**
     * 獲取雷達圖範例資料
     * @returns {Object} - 包含各種範例的物件
     */
    getExampleData() {
        return {
            basic: {
                chart: {
                    type: 'radar',
                    height: 350
                },
                series: [{
                    name: '技能評估',
                    data: [80, 50, 30, 40, 100, 20]
                }],
                xaxis: {
                    categories: ['溝通', '技術', '創意', '領導', '分析', '執行']
                }
            },
            comparison: {
                chart: {
                    type: 'radar',
                    height: 350
                },
                series: [{
                    name: '團隊 A',
                    data: [80, 50, 30, 40, 100, 20]
                }, {
                    name: '團隊 B',
                    data: [20, 30, 40, 80, 20, 80]
                }, {
                    name: '團隊 C',
                    data: [44, 76, 78, 13, 43, 10]
                }],
                xaxis: {
                    categories: ['創新', '品質', '效率', '合作', '靈活性', '可靠性']
                }
            },
            performance: {
                chart: {
                    type: 'radar',
                    height: 350
                },
                series: [{
                    name: '本季表現',
                    data: [85, 72, 90, 68, 95, 80]
                }, {
                    name: '目標值',
                    data: [90, 80, 85, 75, 90, 85]
                }],
                xaxis: {
                    categories: ['銷售', '服務', '品質', '創新', '效率', '滿意度']
                }
            }
        };
    }
}

// Alpine.js 組件定義
window.RadarChart = () => ({
    // 組件狀態
    chartInstance: null,
    isLoading: false,
    error: null,
    
    // 雷達圖特有狀態
    currentDataType: 'basic',
    seriesList: [],
    categories: [],
    yAxisMin: 0,
    yAxisMax: 100,

    // 初始化
    init() {
        console.log('雷達圖組件初始化');
        this.chartInstance = new RadarChart();
        this.setupEventListeners();
        this.loadDefaultChart();
    },

    // 事件監聽器設置
    setupEventListeners() {
        // 監聽視窗大小變化
        window.addEventListener('resize', () => {
            if (this.chartInstance && this.chartInstance.chart) {
                this.chartInstance.resize();
            }
        });
    },

    // 載入預設圖表
    async loadDefaultChart() {
        try {
            const exampleData = this.chartInstance.getExampleData().basic;
            await this.chartInstance.loadChart(exampleData);
            this.updateComponentState();
        } catch (error) {
            console.error('載入預設雷達圖失敗:', error);
            this.error = error.message;
        }
    },

    // 更新組件狀態
    updateComponentState() {
        if (this.chartInstance && this.chartInstance.chart) {
            this.seriesList = this.chartInstance.chart.w.globals.seriesNames.map((name, index) => ({
                name: name,
                index: index,
                visible: true
            }));

            this.categories = this.chartInstance.chart.w.globals.categoryLabels || [];
            this.yAxisMin = this.chartInstance.chart.w.globals.minY || 0;
            this.yAxisMax = this.chartInstance.chart.w.globals.maxY || 100;
        }
    },

    // 載入範例資料
    async loadExample(type = 'basic') {
        this.isLoading = true;
        this.error = null;
        
        try {
            const exampleData = this.chartInstance.getExampleData()[type];
            if (exampleData) {
                await this.chartInstance.loadChart(exampleData);
                this.currentDataType = type;
                this.updateComponentState();
            } else {
                throw new Error(`找不到範例類型: ${type}`);
            }
        } catch (error) {
            console.error('載入範例失敗:', error);
            this.error = error.message;
        } finally {
            this.isLoading = false;
        }
    },

    // 新增隨機系列
    addRandomSeries() {
        if (!this.chartInstance) return;
        
        const randomData = this.categories.map(() => 
            Math.floor(Math.random() * (this.yAxisMax - this.yAxisMin + 1)) + this.yAxisMin
        );
        
        this.chartInstance.addSeries({
            name: `隨機系列 ${Date.now().toString().slice(-4)}`,
            data: randomData
        });
        
        this.updateComponentState();
    },

    // 設置 Y 軸範圍
    setYAxisRange() {
        if (this.chartInstance) {
            this.chartInstance.setYAxisRange(this.yAxisMin, this.yAxisMax);
        }
    },

    // 設置雷達圖大小
    setRadarSize(size) {
        if (this.chartInstance) {
            this.chartInstance.setRadarSize(size);
        }
    },

    // 設置填充透明度
    setFillOpacity(opacity) {
        if (this.chartInstance) {
            this.chartInstance.setFillOpacity(opacity);
        }
    },

    // 切換系列顯示
    toggleSeries(seriesName) {
        if (!this.chartInstance || !this.chartInstance.chart) return;
        
        this.chartInstance.chart.toggleSeries(seriesName);
        
        // 更新列表中的可見狀態
        const series = this.seriesList.find(s => s.name === seriesName);
        if (series) {
            series.visible = !series.visible;
        }
    },

    // 匯出圖表
    async exportChart(format = 'png') {
        if (this.chartInstance) {
            await this.chartInstance.exportChart(format);
        }
    },

    // 更新圖表
    async updateChart(newData) {
        if (!this.chartInstance) return;
        
        this.isLoading = true;
        this.error = null;
        
        try {
            await this.chartInstance.updateChart(newData);
            this.updateComponentState();
        } catch (error) {
            console.error('更新雷達圖失敗:', error);
            this.error = error.message;
        } finally {
            this.isLoading = false;
        }
    },

    // 銷毀組件
    destroy() {
        if (this.chartInstance) {
            this.chartInstance.destroy();
            this.chartInstance = null;
        }
    }
});

// 全域處理函數（向後相容）
window.handleRadarChart = function(data) {
    console.log('全域雷達圖處理函數被呼叫');
    
    // 查找第一個雷達圖組件實例
    const radarComponent = document.querySelector('[x-data*="RadarChart"]');
    if (radarComponent && radarComponent._x_dataStack) {
        const componentData = radarComponent._x_dataStack[0];
        if (componentData && componentData.updateChart) {
            componentData.updateChart(data);
            return true;
        }
    }
    
    console.warn('找不到雷達圖組件實例');
    return false;
};

export default RadarChart;
