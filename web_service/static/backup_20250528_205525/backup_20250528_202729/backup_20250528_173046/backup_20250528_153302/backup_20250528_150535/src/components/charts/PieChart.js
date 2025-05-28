
import { BaseChart } from './BaseChart.js';

/**
 * 圓餅圖組件 - 基於 Alpine.js 和 ApexCharts
 * 支援分類資料的比例顯示
 */
export class PieChart extends BaseChart {
    constructor() {
        super();
        this.chartType = 'pie';
        this.chartId = 'pieChart';
    }

    /**
     * 初始化 Alpine.js 組件
     */
    init() {
        return {
            ...super.init(),
            chartType: 'pie',
            
            // 圓餅圖特定配置
            defaultOptions: {
                chart: {
                    type: 'pie',
                    height: 350,
                    animations: {
                        enabled: true,
                        easing: 'easeinout',
                        speed: 800
                    }
                },
                labels: [],
                legend: {
                    position: 'bottom',
                    horizontalAlign: 'center'
                },
                dataLabels: {
                    enabled: true,
                    formatter: function (val, opts) {
                        return opts.w.config.series[opts.seriesIndex] + ' (' + val.toFixed(1) + '%)';
                    }
                },
                tooltip: {
                    y: {
                        formatter: function(val, opts) {
                            const total = opts.series.reduce((a, b) => a + b, 0);
                            const percentage = ((val / total) * 100).toFixed(1);
                            return val + ' (' + percentage + '%)';
                        }
                    }
                },
                plotOptions: {
                    pie: {
                        donut: {
                            size: '0%'
                        },
                        expandOnClick: true,
                        customScale: 1
                    }
                },
                colors: ['#00E396', '#008FFB', '#FEB019', '#FF4560', '#775DD0', '#3F51B5', '#546E7A']
            },

            /**
             * 處理圓餅圖特定的資料格式
             */
            processPieData(rawData) {
                if (!rawData) {
                    this.showError('沒有提供資料');
                    return null;
                }

                // 如果是簡單的標籤-數值對陣列
                if (Array.isArray(rawData) && rawData[0] && typeof rawData[0] === 'object') {
                    if (rawData[0].label && rawData[0].value !== undefined) {
                        return {
                            series: rawData.map(item => parseFloat(item.value) || 0),
                            labels: rawData.map(item => item.label || '未知')
                        };
                    }
                    
                    // 如果是 name-value 格式
                    if (rawData[0].name && rawData[0].value !== undefined) {
                        return {
                            series: rawData.map(item => parseFloat(item.value) || 0),
                            labels: rawData.map(item => item.name || '未知')
                        };
                    }
                    
                    // 如果是 category-value 格式
                    if (rawData[0].category && rawData[0].value !== undefined) {
                        return {
                            series: rawData.map(item => parseFloat(item.value) || 0),
                            labels: rawData.map(item => item.category || '未知')
                        };
                    }
                }

                // 如果是物件格式 {label1: value1, label2: value2}
                if (typeof rawData === 'object' && !Array.isArray(rawData)) {
                    return {
                        series: Object.values(rawData).map(val => parseFloat(val) || 0),
                        labels: Object.keys(rawData)
                    };
                }

                // 如果已經是正確的格式 {series: [], labels: []}
                if (rawData.series && rawData.labels) {
                    return {
                        series: rawData.series.map(val => parseFloat(val) || 0),
                        labels: rawData.labels
                    };
                }

                this.showError('不支援的資料格式');
                return null;
            },

            /**
             * 載入並渲染圓餅圖
             */
            async loadChart(data = null, options = {}) {
                try {
                    this.loading = true;
                    this.error = null;

                    const chartData = data || this.sampleData;
                    const processedData = this.processPieData(chartData);
                    
                    if (!processedData) return;

                    const chartOptions = {
                        ...this.defaultOptions,
                        ...options,
                        series: processedData.series,
                        labels: processedData.labels
                    };

                    await this.renderChart(chartOptions);
                    this.showSuccess('圓餅圖載入成功');
                    
                } catch (error) {
                    console.error('圓餅圖載入失敗:', error);
                    this.showError('圓餅圖載入失敗: ' + error.message);
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
                    const processedData = this.processPieData(newData);
                    if (processedData) {
                        await this.chart.updateSeries(processedData.series);
                        await this.chart.updateOptions({
                            labels: processedData.labels
                        });
                        this.showSuccess('圓餅圖更新成功');
                    }
                } catch (error) {
                    console.error('更新圓餅圖失敗:', error);
                    this.showError('更新失敗: ' + error.message);
                }
            },

            /**
             * 切換為環形圖模式
             */
            toggleDonutMode(donutSize = '50%') {
                if (!this.chart) {
                    this.showError('圖表尚未初始化');
                    return;
                }

                try {
                    const currentSize = this.chart.opts.plotOptions?.pie?.donut?.size || '0%';
                    const newSize = currentSize === '0%' ? donutSize : '0%';
                    
                    this.chart.updateOptions({
                        plotOptions: {
                            pie: {
                                donut: {
                                    size: newSize
                                }
                            }
                        }
                    });
                    
                    const mode = newSize === '0%' ? '圓餅圖' : '環形圖';
                    this.showSuccess(`已切換為${mode}模式`);
                    
                } catch (error) {
                    console.error('切換模式失敗:', error);
                    this.showError('切換模式失敗');
                }
            },

            /**
             * 設定圖例位置
             */
            setLegendPosition(position = 'bottom') {
                if (!this.chart) {
                    this.showError('圖表尚未初始化');
                    return;
                }

                try {
                    this.chart.updateOptions({
                        legend: {
                            position: position,
                            horizontalAlign: position === 'top' || position === 'bottom' ? 'center' : 'left'
                        }
                    });
                    this.showSuccess(`圖例位置已設定為: ${position}`);
                } catch (error) {
                    console.error('設定圖例位置失敗:', error);
                    this.showError('設定圖例位置失敗');
                }
            },

            /**
             * 高亮特定扇形
             */
            highlightSlice(sliceIndex) {
                if (!this.chart) {
                    this.showError('圖表尚未初始化');
                    return;
                }

                try {
                    // 重置所有高亮
                    this.chart.toggleDataPointSelection(-1, -1);
                    // 高亮指定扇形
                    this.chart.toggleDataPointSelection(sliceIndex);
                } catch (error) {
                    console.error('高亮扇形失敗:', error);
                    this.showError('高亮扇形失敗');
                }
            },

            /**
             * 生成示範資料
             */
            generateSampleData() {
                const categories = ['產品A', '產品B', '產品C', '產品D', '產品E'];
                return categories.map(category => ({
                    label: category,
                    value: Math.floor(Math.random() * 100) + 20
                }));
            },

            /**
             * 預設示範資料
             */
            sampleData: [
                { label: '桌面電腦', value: 44 },
                { label: '行動裝置', value: 55 },
                { label: '平板電腦', value: 13 },
                { label: '其他', value: 8 }
            ]
        };
    }
}

// 全域函數支援（向後相容）
window.handlePieChart = function(data, options = {}) {
    console.log('全域 handlePieChart 被呼叫', data);
    
    // 創建臨時組件實例
    const pieChart = new PieChart();
    const component = pieChart.init();
    
    // 設定圖表容器
    component.chartId = 'pieChart';
    
    // 載入圖表
    component.loadChart(data, options);
    
    return component;
};

// 匯出類別
export default PieChart;
