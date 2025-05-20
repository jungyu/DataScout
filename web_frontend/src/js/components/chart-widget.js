/**
 * 圖表小部件組件
 *
 * 此組件負責處理各種圖表的創建和管理
 */
import ApexCharts from 'apexcharts';

export function initChartWidgets() {
  Alpine.data('chartWidget', () => ({
    charts: {},
    chartTypes: ['line', 'bar', 'pie', 'area', 'radar', 'bubble', 'scatter'],
    selectedType: 'bar',
    
    init() {
      this.$watch('selectedType', (value) => {
        this.updateChartType(value);
      });
    },
    
    // 創建新圖表
    createChart(element, type, data, options = {}) {
      if (!element) return;
      
      const chartId = element.id || `chart-${Date.now()}`;
      const theme = document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
      
      // 獲取圖表配置
      const chartOptions = window.chartConfig.getConfig(type, data, {
        ...options,
        theme: { mode: theme }
      });
      
      // 創建圖表實例
      this.charts[chartId] = new ApexCharts(element, chartOptions);
      this.charts[chartId].render();
      
      return this.charts[chartId];
    },
    
    // 銷毀圖表
    destroyChart(chartId) {
      if (this.charts[chartId]) {
        this.charts[chartId].destroy();
        delete this.charts[chartId];
      }
    },
    
    // 更新圖表類型
    updateChartType(type) {
      const chartElement = document.getElementById('dynamic-chart');
      if (!chartElement) return;
      
      // 獲取測試數據
      const data = this.getTestData();
      
      // 銷毀舊圖表
      this.destroyChart('dynamic-chart');
      
      // 創建新圖表
      this.createChart(chartElement, type, data, {
        height: 350,
        width: '100%'
      });
    },
    
    // 獲取測試數據
    getTestData() {
      return {
        series: [{
          name: 'Series 1',
          data: [31, 40, 28, 51, 42, 109, 100]
        }, {
          name: 'Series 2',
          data: [11, 32, 45, 32, 34, 52, 41]
        }],
        categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul']
      };
    }
  }));
}
