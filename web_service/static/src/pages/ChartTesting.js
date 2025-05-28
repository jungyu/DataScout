// 圖表測試頁面 - 測試新的 Alpine.js 圖表組件
import { LineChart } from '../components/charts/LineChart.js';
import { BarChart } from '../components/charts/BarChart.js';
import { CandlestickChart } from '../components/charts/CandlestickChart.js';
import { AreaChart } from '../components/charts/AreaChart.js';

export const ChartTesting = () => {
  return {
    activeTab: 'line',
    lineChart: null,
    barChart: null,
    candlestickChart: null,
    areaChart: null,
    isLoading: false,
    error: null,
    
    init() {
      console.log('圖表測試頁面初始化');
      this.initCharts();
    },
    
    initCharts() {
      try {
        this.isLoading = true;
        
        // 初始化折線圖
        this.initLineChart();
        
        // 初始化長條圖
        this.initBarChart();
        
        // 初始化蠟燭圖
        this.initCandlestickChart();
        
        // 初始化區域圖
        this.initAreaChart();
        
        this.isLoading = false;
        console.log('所有圖表初始化完成');
        
      } catch (error) {
        this.handleError(error, '圖表初始化');
      }
    },
    
    initLineChart() {
      // 模擬折線圖資料
      const lineData = [
        { x: '2024-01-01', y: 100 },
        { x: '2024-01-02', y: 120 },
        { x: '2024-01-03', y: 95 },
        { x: '2024-01-04', y: 140 },
        { x: '2024-01-05', y: 110 },
        { x: '2024-01-06', y: 165 },
        { x: '2024-01-07', y: 145 }
      ];
      
      this.lineChart = new LineChart('test-line-chart', lineData, {
        seriesName: '測試資料',
        colors: ['#008FFB']
      });
      
      // 延遲初始化以確保 DOM 元素存在
      this.$nextTick(() => {
        this.lineChart.init();
      });
    },
    
    initBarChart() {
      // 模擬長條圖資料
      const barData = [
        { category: '產品A', value: 50 },
        { category: '產品B', value: 75 },
        { category: '產品C', value: 100 },
        { category: '產品D', value: 85 },
        { category: '產品E', value: 90 }
      ];
      
      this.barChart = new BarChart('test-bar-chart', barData, {
        seriesName: '銷售量',
        yAxisTitle: '銷售數量',
        colors: ['#00E396']
      });
      
      this.$nextTick(() => {
        this.barChart.init();
      });
    },
    
    initCandlestickChart() {
      // 模擬蠟燭圖資料
      const candlestickData = [
        { x: new Date('2024-01-01'), y: [100, 110, 95, 105] },
        { x: new Date('2024-01-02'), y: [105, 120, 100, 115] },
        { x: new Date('2024-01-03'), y: [115, 125, 110, 120] },
        { x: new Date('2024-01-04'), y: [120, 135, 115, 130] },
        { x: new Date('2024-01-05'), y: [130, 140, 125, 135] }
      ];
      
      this.candlestickChart = new CandlestickChart('test-candlestick-chart', candlestickData, {
        title: '股價走勢測試'
      });
      
      this.$nextTick(() => {
        this.candlestickChart.init();
      });
    },
    
    initAreaChart() {
      // 模擬區域圖資料
      const areaData = [
        { x: '2024-01-01', y: 50 },
        { x: '2024-01-02', y: 70 },
        { x: '2024-01-03', y: 60 },
        { x: '2024-01-04', y: 90 },
        { x: '2024-01-05', y: 80 },
        { x: '2024-01-06', y: 120 },
        { x: '2024-01-07', y: 100 }
      ];
      
      this.areaChart = new AreaChart('test-area-chart', areaData, {
        seriesName: '測試區域資料',
        colors: ['#FF4560']
      });
      
      this.$nextTick(() => {
        this.areaChart.init();
      });
    },
    
    switchTab(tab) {
      this.activeTab = tab;
      console.log(`切換到 ${tab} 標籤頁`);
      
      // 延遲重新渲染圖表以確保容器可見
      this.$nextTick(() => {
        this.resizeCharts();
      });
    },
    
    resizeCharts() {
      // 重新調整所有圖表大小
      if (this.lineChart && this.lineChart.isReady()) {
        this.lineChart.resize();
      }
      if (this.barChart && this.barChart.isReady()) {
        this.barChart.resize();
      }
      if (this.candlestickChart && this.candlestickChart.isReady()) {
        this.candlestickChart.resize();
      }
      if (this.areaChart && this.areaChart.isReady()) {
        this.areaChart.resize();
      }
      if (this.areaChart && this.areaChart.isReady()) {
        this.areaChart.resize();
      }
    },
    
    refreshChart(chartType) {
      try {
        this.isLoading = true;
        
        switch (chartType) {
          case 'line':
            if (this.lineChart) {
              const newData = this.generateRandomLineData();
              this.lineChart.updateData(newData);
            }
            break;
            
          case 'bar':
            if (this.barChart) {
              const newData = this.generateRandomBarData();
              this.barChart.updateData(newData);
            }
            break;
            
          case 'candlestick':
            if (this.candlestickChart) {
              const newData = this.generateRandomCandlestickData();
              this.candlestickChart.updateData(newData);
            }
            break;
            
          case 'area':
            if (this.areaChart) {
              const newData = this.generateRandomAreaData();
              this.areaChart.updateData(newData);
            }
            break;
        }
        
        this.isLoading = false;
        console.log(`${chartType} 圖表已更新`);
        
      } catch (error) {
        this.handleError(error, '圖表更新');
      }
    },
    
    generateRandomLineData() {
      const data = [];
      const baseDate = new Date('2024-01-01');
      
      for (let i = 0; i < 10; i++) {
        const date = new Date(baseDate);
        date.setDate(date.getDate() + i);
        data.push({
          x: date.toISOString().split('T')[0],
          y: Math.floor(Math.random() * 200) + 50
        });
      }
      
      return data;
    },
    
    generateRandomBarData() {
      const categories = ['產品A', '產品B', '產品C', '產品D', '產品E'];
      return categories.map(category => ({
        category: category,
        value: Math.floor(Math.random() * 150) + 25
      }));
    },
    
    generateRandomCandlestickData() {
      const data = [];
      const baseDate = new Date('2024-01-01');
      let lastClose = 100;
      
      for (let i = 0; i < 7; i++) {
        const date = new Date(baseDate);
        date.setDate(date.getDate() + i);
        
        const open = lastClose + (Math.random() - 0.5) * 10;
        const high = open + Math.random() * 20;
        const low = open - Math.random() * 15;
        const close = low + Math.random() * (high - low);
        
        data.push({
          x: date,
          y: [open, high, low, close]
        });
        
        lastClose = close;
      }
      
      return data;
    },
    
    generateRandomAreaData() {
      const data = [];
      const baseDate = new Date('2024-01-01');
      
      for (let i = 0; i < 10; i++) {
        const date = new Date(baseDate);
        date.setDate(date.getDate() + i);
        data.push({
          x: date.toISOString().split('T')[0],
          y: Math.floor(Math.random() * 100) + 10
        });
      }
      
      return data;
    },
    
    exportChart(chartType, format = 'png') {
      try {
        switch (chartType) {
          case 'line':
            if (this.lineChart && this.lineChart.isReady()) {
              if (format === 'svg') {
                this.lineChart.exportToSVG();
              } else {
                this.lineChart.exportToPNG();
              }
            }
            break;
            
          case 'bar':
            if (this.barChart && this.barChart.isReady()) {
              if (format === 'svg') {
                this.barChart.exportToSVG();
              } else {
                this.barChart.exportToPNG();
              }
            }
            break;
            
          case 'candlestick':
            if (this.candlestickChart && this.candlestickChart.isReady()) {
              if (format === 'svg') {
                this.candlestickChart.exportToSVG();
              } else {
                this.candlestickChart.exportToPNG();
              }
            }
            break;
            
          case 'area':
            if (this.areaChart && this.areaChart.isReady()) {
              if (format === 'svg') {
                this.areaChart.exportToSVG();
              } else {
                this.areaChart.exportToPNG();
              }
            }
            break;
        }
        
        console.log(`${chartType} 圖表已匯出為 ${format.toUpperCase()}`);
        
      } catch (error) {
        this.handleError(error, '圖表匯出');
      }
    },
    
    handleError(error, context = '操作') {
      console.error(`圖表測試頁面錯誤 (${context}):`, error);
      this.error = `${context}失敗: ${error.message}`;
      this.isLoading = false;
      
      // 3秒後清除錯誤訊息
      setTimeout(() => {
        this.error = null;
      }, 3000);
    },
    
    clearError() {
      this.error = null;
    },
    
    destroy() {
      // 清理圖表資源
      if (this.lineChart) {
        this.lineChart.destroy();
      }
      if (this.barChart) {
        this.barChart.destroy();
      }
      if (this.candlestickChart) {
        this.candlestickChart.destroy();
      }
      if (this.areaChart) {
        this.areaChart.destroy();
      }
      
      console.log('圖表測試頁面已清理');
    }
  };
};
