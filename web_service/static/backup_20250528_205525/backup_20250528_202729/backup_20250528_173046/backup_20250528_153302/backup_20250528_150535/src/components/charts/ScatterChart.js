/**
 * 散點圖組件 - Alpine.js 實現
 * 繼承自 BaseChart，專門處理散點圖的渲染和交互
 * 
 * 功能特色：
 * - 支援數值型資料的雙軸顯示
 * - 縮放和平移交互功能
 * - 多系列資料支援
 * - 自動資料格式轉換
 * - 動態圖例管理
 */

import BaseChart from './BaseChart.js';

class ScatterChart extends BaseChart {
    constructor() {
        super();
        
        // 散點圖特有的配置
        this.defaultConfig = {
            chart: {
                type: 'scatter',
                height: 350,
                animations: {
                    enabled: true,
                    easing: 'easeinout',
                    speed: 800
                },
                zoom: {
                    enabled: true,
                    type: 'xy',
                    autoScaleYaxis: true
                },
                toolbar: {
                    show: true,
                    tools: {
                        download: true,
                        selection: true,
                        zoom: true,
                        zoomin: true,
                        zoomout: true,
                        pan: true,
                        reset: true
                    }
                }
            },
            series: [],
            xaxis: {
                type: 'numeric',
                tickAmount: 10,
                labels: {
                    formatter: function(val) {
                        return parseFloat(val).toFixed(2);
                    }
                },
                title: {
                    text: 'X 軸值'
                }
            },
            yaxis: {
                tickAmount: 7,
                labels: {
                    formatter: function(val) {
                        return parseFloat(val).toFixed(2);
                    }
                },
                title: {
                    text: 'Y 軸值'
                }
            },
            grid: {
                show: true,
                xaxis: {
                    lines: {
                        show: true
                    }
                },
                yaxis: {
                    lines: {
                        show: true
                    }
                }
            },
            legend: {
                show: true,
                position: 'top',
                horizontalAlign: 'left'
            },
            tooltip: {
                shared: false,
                intersect: true,
                custom: function({series, seriesIndex, dataPointIndex, w}) {
                    const data = w.globals.initialSeries[seriesIndex].data[dataPointIndex];
                    const seriesName = w.globals.seriesNames[seriesIndex];
                    
                    return `
                        <div class="bg-white p-3 rounded shadow-lg border">
                            <div class="font-medium text-gray-800 mb-1">${seriesName}</div>
                            <div class="text-sm text-gray-600">
                                X: <span class="font-medium">${Array.isArray(data) ? data[0] : data.x}</span><br>
                                Y: <span class="font-medium">${Array.isArray(data) ? data[1] : data.y}</span>
                            </div>
                        </div>
                    `;
                }
            },
            markers: {
                size: 6,
                hover: {
                    size: 8
                }
            }
        };
    }

    /**
     * 處理散點圖專用的資料格式轉換
     * @param {Array|Object} data - 輸入資料
     * @returns {Array} - 格式化後的系列資料
     */
    processScatterData(data) {
        if (!data) {
            console.warn('散點圖資料為空，使用預設樣本資料');
            return this.getExampleData().basic.series;
        }

        // 如果已經是正確的系列格式
        if (Array.isArray(data) && data.length > 0 && data[0].data) {
            return data.map(series => ({
                name: series.name || `系列 ${series.index || 1}`,
                data: this.normalizeDataPoints(series.data)
            }));
        }

        // 如果是簡單的數據點陣列
        if (Array.isArray(data) && data.length > 0) {
            return [{
                name: '散點資料',
                data: this.normalizeDataPoints(data)
            }];
        }

        // 如果是包含多個陣列的物件
        if (typeof data === 'object' && !Array.isArray(data)) {
            const series = [];
            
            Object.keys(data).forEach((key, index) => {
                if (Array.isArray(data[key])) {
                    series.push({
                        name: key,
                        data: this.normalizeDataPoints(data[key])
                    });
                }
            });
            
            return series.length > 0 ? series : this.getExampleData().basic.series;
        }

        console.warn('無法識別的散點圖資料格式，使用預設樣本資料');
        return this.getExampleData().basic.series;
    }

    /**
     * 標準化資料點格式
     * @param {Array} dataPoints - 原始資料點
     * @returns {Array} - 標準化的資料點 [x, y] 格式
     */
    normalizeDataPoints(dataPoints) {
        if (!Array.isArray(dataPoints)) return [];

        return dataPoints.map(point => {
            // 如果已經是 [x, y] 格式
            if (Array.isArray(point) && point.length >= 2) {
                return [parseFloat(point[0]) || 0, parseFloat(point[1]) || 0];
            }
            
            // 如果是 {x, y} 物件格式
            if (typeof point === 'object' && point.x !== undefined && point.y !== undefined) {
                return [parseFloat(point.x) || 0, parseFloat(point.y) || 0];
            }
            
            // 如果是單一數值，將索引作為 X 值
            if (typeof point === 'number') {
                return [dataPoints.indexOf(point), point];
            }
            
            // 預設情況
            console.warn('無法處理的資料點格式:', point);
            return [0, 0];
        });
    }

    /**
     * 更新散點圖配置選項
     * @param {Object} options - 配置選項
     */
    updateScatterOptions(options = {}) {
        const config = { ...this.defaultConfig };

        // 處理軸標題
        if (options.xAxisTitle) {
            config.xaxis.title.text = options.xAxisTitle;
        }
        if (options.yAxisTitle) {
            config.yaxis.title.text = options.yAxisTitle;
        }

        // 處理縮放選項
        if (options.zoom !== undefined) {
            config.chart.zoom.enabled = Boolean(options.zoom);
        }

        // 處理圖例選項
        if (options.legend) {
            config.legend = { ...config.legend, ...options.legend };
        }

        // 處理標記點樣式
        if (options.markers) {
            config.markers = { ...config.markers, ...options.markers };
        }

        // 處理網格選項
        if (options.grid !== undefined) {
            config.grid.show = Boolean(options.grid);
        }

        // 處理工具列選項
        if (options.toolbar !== undefined) {
            config.chart.toolbar.show = Boolean(options.toolbar);
        }

        return config;
    }

    /**
     * 載入並渲染散點圖
     * @param {Array|Object} data - 資料或配置物件
     * @param {Object} options - 額外選項
     */
    async loadChart(data, options = {}) {
        try {
            this.showLoading();

            let chartData;
            let config;

            // 如果 data 包含完整的圖表配置
            if (data && data.chart && data.series) {
                config = { ...this.defaultConfig, ...data };
                chartData = this.processScatterData(data.series);
            } else {
                // 否則將 data 視為純資料
                chartData = this.processScatterData(data);
                config = this.updateScatterOptions(options);
            }

            config.series = chartData;

            await this.initChart(config);
            this.hideLoading();

            this.showNotification('散點圖載入完成', 'success');

        } catch (error) {
            this.hideLoading();
            console.error('載入散點圖失敗:', error);
            this.showNotification(`載入散點圖失敗: ${error.message}`, 'error');
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

        const normalizedData = this.normalizeDataPoints(seriesData.data || []);
        
        this.chart.appendSeries({
            name: seriesData.name || `系列 ${Date.now()}`,
            data: normalizedData
        });

        this.showNotification(`已新增系列: ${seriesData.name}`, 'success');
    }

    /**
     * 移除資料系列
     * @param {string} seriesName - 系列名稱
     */
    removeSeries(seriesName) {
        if (!this.chart) {
            console.error('圖表未初始化');
            return;
        }

        // 找到系列索引
        const seriesIndex = this.chart.w.globals.seriesNames.indexOf(seriesName);
        if (seriesIndex !== -1) {
            this.chart.removeSeries(seriesName);
            this.showNotification(`已移除系列: ${seriesName}`, 'success');
        } else {
            this.showNotification(`找不到系列: ${seriesName}`, 'warning');
        }
    }

    /**
     * 生成隨機散點資料
     * @param {number} count - 資料點數量
     * @param {Object} range - 資料範圍 {xMin, xMax, yMin, yMax}
     * @returns {Array} - 隨機資料點
     */
    generateRandomData(count = 20, range = {xMin: 0, xMax: 100, yMin: 0, yMax: 100}) {
        const data = [];
        
        for (let i = 0; i < count; i++) {
            const x = Math.random() * (range.xMax - range.xMin) + range.xMin;
            const y = Math.random() * (range.yMax - range.yMin) + range.yMin;
            data.push([parseFloat(x.toFixed(2)), parseFloat(y.toFixed(2))]);
        }
        
        return data;
    }

    /**
     * 重置縮放
     */
    resetZoom() {
        if (this.chart) {
            this.chart.resetSeries();
            this.showNotification('已重置縮放', 'info');
        }
    }

    /**
     * 獲取散點圖範例資料
     * @returns {Object} - 包含各種範例的物件
     */
    getExampleData() {
        return {
            basic: {
                chart: {
                    type: 'scatter',
                    height: 350
                },
                series: [{
                    name: "樣本 A",
                    data: [
                        [16.4, 5.4], [21.7, 2], [25.4, 3], [19, 2], [10.9, 1], 
                        [13.6, 3.2], [10.9, 7.4], [10.9, 0], [10.9, 8.2], [16.4, 0], 
                        [16.4, 1.8], [13.6, 0.3], [13.6, 0], [29.9, 0], [27.1, 2.3], 
                        [16.4, 0], [13.6, 3.7], [10.9, 5.2], [16.4, 6.5], [10.9, 0]
                    ]
                }, {
                    name: "樣本 B",
                    data: [
                        [6.4, 13.4], [1.7, 11], [5.4, 8], [9, 17], [1.9, 4], 
                        [3.6, 12.2], [1.9, 14.4], [1.9, 9], [1.9, 13.2], [1.4, 7], 
                        [6.4, 8.8], [3.6, 4.3], [1.6, 10], [9.9, 2], [7.1, 15], 
                        [1.4, 0], [3.6, 13.7], [1.9, 15.2], [6.4, 16.5], [0.9, 10]
                    ]
                }],
                xaxis: {
                    type: 'numeric',
                    title: {
                        text: 'X 軸數值'
                    }
                },
                yaxis: {
                    title: {
                        text: 'Y 軸數值'
                    }
                }
            },
            correlation: {
                chart: {
                    type: 'scatter',
                    height: 350
                },
                series: [{
                    name: "正相關",
                    data: this.generateCorrelationData(30, 0.8, {xMin: 0, xMax: 50, yMin: 0, yMax: 50})
                }, {
                    name: "負相關",
                    data: this.generateCorrelationData(30, -0.7, {xMin: 50, xMax: 100, yMin: 0, yMax: 50})
                }],
                xaxis: {
                    title: {
                        text: '變數 X'
                    }
                },
                yaxis: {
                    title: {
                        text: '變數 Y'
                    }
                }
            }
        };
    }

    /**
     * 生成相關性資料（用於範例）
     * @param {number} count - 資料點數量
     * @param {number} correlation - 相關係數 (-1 到 1)
     * @param {Object} range - 資料範圍
     * @returns {Array} - 具有指定相關性的資料點
     */
    generateCorrelationData(count, correlation, range) {
        const data = [];
        
        for (let i = 0; i < count; i++) {
            const x = Math.random() * (range.xMax - range.xMin) + range.xMin;
            
            // 基於相關係數生成 y 值
            const noise = (Math.random() - 0.5) * 20; // 添加噪音
            const y = correlation * x + (range.yMax - range.yMin) / 2 + noise;
            
            // 確保 y 值在範圍內
            const clampedY = Math.max(range.yMin, Math.min(range.yMax, y));
            
            data.push([
                parseFloat(x.toFixed(2)), 
                parseFloat(clampedY.toFixed(2))
            ]);
        }
        
        return data;
    }
}

// Alpine.js 組件定義
window.ScatterChart = () => ({
    // 組件狀態
    chartInstance: null,
    isLoading: false,
    error: null,
    
    // 散點圖特有狀態
    currentDataType: 'basic',
    showZoomControls: true,
    seriesList: [],

    // 初始化
    init() {
        console.log('散點圖組件初始化');
        this.chartInstance = new ScatterChart();
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
            this.updateSeriesList();
        } catch (error) {
            console.error('載入預設散點圖失敗:', error);
            this.error = error.message;
        }
    },

    // 更新系列列表
    updateSeriesList() {
        if (this.chartInstance && this.chartInstance.chart) {
            this.seriesList = this.chartInstance.chart.w.globals.seriesNames.map((name, index) => ({
                name: name,
                index: index,
                visible: true
            }));
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
                this.updateSeriesList();
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
        
        const randomData = this.chartInstance.generateRandomData(
            Math.floor(Math.random() * 20) + 10, // 10-30 個點
            {xMin: 0, xMax: 100, yMin: 0, yMax: 100}
        );
        
        this.chartInstance.addSeries({
            name: `隨機系列 ${Date.now().toString().slice(-4)}`,
            data: randomData
        });
        
        this.updateSeriesList();
    },

    // 移除系列
    removeSeries(seriesName) {
        if (!this.chartInstance) return;
        
        this.chartInstance.removeSeries(seriesName);
        this.updateSeriesList();
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

    // 重置縮放
    resetZoom() {
        if (this.chartInstance) {
            this.chartInstance.resetZoom();
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
            this.updateSeriesList();
        } catch (error) {
            console.error('更新散點圖失敗:', error);
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
window.handleScatterChart = function(data) {
    console.log('全域散點圖處理函數被呼叫');
    
    // 查找第一個散點圖組件實例
    const scatterComponent = document.querySelector('[x-data*="ScatterChart"]');
    if (scatterComponent && scatterComponent._x_dataStack) {
        const componentData = scatterComponent._x_dataStack[0];
        if (componentData && componentData.updateChart) {
            componentData.updateChart(data);
            return true;
        }
    }
    
    console.warn('找不到散點圖組件實例');
    return false;
};

export default ScatterChart;
