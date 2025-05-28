   
import { BaseChart } from './BaseChart.js';

/**
 * 區域圖組件 - 基於 Alpine.js 和 ApexCharts
 * 支援時間序列資料和填充區域顯示
 */
export class AreaChart extends BaseChart {
    constructor() {
        super();
        this.chartType = 'area';
        this.chartId = 'areaChart';
    }

    /**
     * 初始化 Alpine.js 組件
     */
    init() {
        return {
            ...super.init(),
            chartType: 'area',
            
            // 區域圖特定配置
            defaultOptions: {
                chart: {
                    type: 'area',
                    height: 350,
                    zoom: { enabled: true },
                    toolbar: { show: true }
                },
                dataLabels: { enabled: false },
                stroke: { 
                    curve: 'smooth', 
                    width: 2 
                },
                fill: {
                    type: 'gradient',
                    gradient: {
                        shadeIntensity: 1,
                        opacityFrom: 0.7,
                        opacityTo: 0.3,
                        stops: [0, 90, 100]
                    }
                },
                xaxis: {
                    type: 'datetime',
                    labels: {
                        datetimeUTC: false
                    }
                },
                yaxis: {
                    title: { text: '數值' }
                },
                tooltip: {
                    x: { format: 'dd/MM/yy HH:mm' }
                },
                legend: {
                    position: 'top',
                    horizontalAlign: 'left'
                }
            },

            /**
             * 處理區域圖特定的資料格式
             */
            processAreaData(rawData) {
                if (!rawData) {
                    this.showError('沒有提供資料');
                    return null;
                }

                // 如果是時間序列資料 (常見格式)
                if (Array.isArray(rawData) && rawData[0] && rawData[0].x) {
                    return [{
                        name: this.seriesName || '數據系列',
                        data: rawData.map(item => ({
                            x: new Date(item.x).getTime(),
                            y: parseFloat(item.y) || 0
                        }))
                    }];
                }

                // 如果是簡單的 x,y 陣列
                if (Array.isArray(rawData) && rawData[0] && Array.isArray(rawData[0])) {
                    return [{
                        name: this.seriesName || '數據系列',
                        data: rawData.map(([x, y]) => ({
                            x: new Date(x).getTime(),
                            y: parseFloat(y) || 0
                        }))
                    }];
                }

                // 如果已經是正確的 ApexCharts 格式
                if (Array.isArray(rawData) && rawData[0] && rawData[0].name) {
                    return rawData.map(series => ({
                        ...series,
                        data: series.data.map(point => ({
                            x: typeof point.x === 'string' ? new Date(point.x).getTime() : point.x,
                            y: parseFloat(point.y) || 0
                        }))
                    }));
                }

                this.showError('不支援的資料格式');
                return null;
            },

            /**
             * 載入並渲染區域圖
             */
            async loadChart(data = null, options = {}) {
                try {
                    this.loading = true;
                    this.error = null;

                    const chartData = data || this.sampleData;
                    const processedData = this.processAreaData(chartData);
                    
                    if (!processedData) return;

                    const chartOptions = {
                        ...this.defaultOptions,
                        ...options,
                        series: processedData
                    };

                    await this.renderChart(chartOptions);
                    this.showSuccess('區域圖載入成功');
                    
                } catch (error) {
                    console.error('區域圖載入失敗:', error);
                    this.showError('區域圖載入失敗: ' + error.message);
                } finally {
                    this.loading = false;
                }
            },

            /**
             * 更新圖表資料
             */
            async updateChart(newData) {
                if (!this.chart) {
                    this.showError('圖表尚未初始化');
                    return;
                }

                try {
                    const processedData = this.processAreaData(newData);
                    if (processedData) {
                        await this.chart.updateSeries(processedData);
                        this.showSuccess('區域圖更新成功');
                    }
                } catch (error) {
                    console.error('更新區域圖失敗:', error);
                    this.showError('更新失敗: ' + error.message);
                }
            },

            /**
             * 設定填充樣式
             */
            setFillStyle(fillType = 'gradient', options = {}) {
                if (!this.chart) {
                    this.showError('圖表尚未初始化');
                    return;
                }

                const fillOptions = {
                    gradient: {
                        type: 'gradient',
                        gradient: {
                            shadeIntensity: 1,
                            opacityFrom: 0.7,
                            opacityTo: 0.3,
                            stops: [0, 90, 100],
                            ...options
                        }
                    },
                    solid: {
                        type: 'solid',
                        opacity: options.opacity || 0.5
                    },
                    pattern: {
                        type: 'pattern',
                        pattern: {
                            style: options.style || 'slantedLines',
                            width: options.width || 6,
                            height: options.height || 6,
                            strokeWidth: options.strokeWidth || 2
                        }
                    }
                };

                try {
                    this.chart.updateOptions({
                        fill: fillOptions[fillType] || fillOptions.gradient
                    });
                    this.showSuccess(`填充樣式已設定為: ${fillType}`);
                } catch (error) {
                    console.error('設定填充樣式失敗:', error);
                    this.showError('設定填充樣式失敗');
                }
            },

            /**
             * 生成示範資料
             */
            generateSampleData() {
                const data = [];
                const startDate = new Date();
                startDate.setDate(startDate.getDate() - 30);

                for (let i = 0; i < 30; i++) {
                    const date = new Date(startDate);
                    date.setDate(date.getDate() + i);
                    
                    data.push({
                        x: date.getTime(),
                        y: Math.floor(Math.random() * 100) + 50
                    });
                }

                return data;
            },

            /**
             * 預設示範資料
             */
            sampleData: [
                {
                    x: new Date('2024-01-01').getTime(),
                    y: 30
                },
                {
                    x: new Date('2024-01-02').getTime(),
                    y: 40
                },
                {
                    x: new Date('2024-01-03').getTime(),
                    y: 35
                },
                {
                    x: new Date('2024-01-04').getTime(),
                    y: 50
                },
                {
                    x: new Date('2024-01-05').getTime(),
                    y: 49
                },
                {
                    x: new Date('2024-01-06').getTime(),
                    y: 60
                },
                {
                    x: new Date('2024-01-07').getTime(),
                    y: 70
                }
            ]
        };
    }
}

// 全域函數支援（向後相容）
window.handleAreaChart = function(data, options = {}) {
    console.log('全域 handleAreaChart 被呼叫', data);
    
    // 創建臨時組件實例
    const areaChart = new AreaChart();
    const component = areaChart.init();
    
    // 設定圖表容器
    component.chartId = 'areaChart';
    
    // 載入圖表
    component.loadChart(data, options);
    
    return component;
};

// 匯出類別
export default AreaChart;