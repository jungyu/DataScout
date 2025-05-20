/**
 * 進階圖表組件
 * 
 * 提供更多的圖表功能，包括圖表匯出、調整尺寸等
 */

import ApexCharts from 'apexcharts';

export function initAdvancedCharts() {
  Alpine.data('advancedChart', () => ({
    // 圖表實例
    chart: null,
    
    // 圖表配置項
    chartOptions: {},
    
    // 圖表初始尺寸
    width: 0,
    height: 0,
    
    // 初始化方法
    init() {
      // 延遲初始化，確保 DOM 已完全載入
      this.$nextTick(() => {
        // 初始化圖表寬高
        const rect = this.$el.getBoundingClientRect();
        this.width = rect.width;
        this.height = this.height || rect.height;
        
        // 設置主題顏色
        if (this.chartOptions) {
          this.chartOptions.theme = {
            mode: document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light'
          };
        }
        
        // 創建圖表
        if (this.chartOptions) {
          this.createChart();
        }
      });
      
      // 監聽主題變化
      this.setupThemeObserver();
      
      // 監聽視窗大小變化
      this.setupResizeListener();
    },
    
    // 創建圖表
    createChart() {
      if (!this.$refs.chartContainer || !this.chartOptions) return;
      
      const options = {
        ...this.chartOptions,
        chart: {
          ...(this.chartOptions.chart || {}),
          height: this.height,
          width: this.width,
          animations: {
            enabled: true,
            easing: 'easeinout',
            speed: 800
          },
          fontFamily: 'Noto Sans TC, sans-serif',
          background: 'transparent'
        }
      };
      
      this.chart = new ApexCharts(this.$refs.chartContainer, options);
      this.chart.render();
    },
    
    // 更新圖表數據
    updateData(series) {
      if (!this.chart) return;
      this.chart.updateSeries(series, true);
    },
    
    // 更新圖表選項
    updateOptions(options, redraw = false) {
      if (!this.chart) return;
      this.chart.updateOptions(options, redraw);
    },
    
    // 設置主題監聽
    setupThemeObserver() {
      const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
          if (mutation.attributeName === 'data-theme' && this.chart) {
            this.chart.updateOptions({
              theme: {
                mode: document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light'
              }
            });
          }
        });
      });
      
      observer.observe(document.documentElement, { attributes: true });
      this._themeObserver = observer;
    },
    
    // 設置視窗大小調整監聽
    setupResizeListener() {
      const resizeHandler = () => {
        if (!this.$refs.chartContainer || !this.chart) return;
        
        const rect = this.$refs.chartContainer.getBoundingClientRect();
        this.width = rect.width;
        
        this.chart.updateOptions({
          chart: {
            width: this.width
          }
        });
      };
      
      window.addEventListener('resize', resizeHandler);
      this._resizeHandler = resizeHandler;
    },
    
    // 匯出圖表為圖像
    exportChart(format = 'png', filename = 'chart') {
      if (!this.chart) return;
      
      this.chart.dataURI().then(({ imgURI, blob }) => {
        // 創建下載鏈接
        const link = document.createElement('a');
        link.href = imgURI;
        link.download = `${filename}.${format}`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      });
    },
    
    // 清理
    destroy() {
      if (this._themeObserver) {
        this._themeObserver.disconnect();
      }
      
      if (this._resizeHandler) {
        window.removeEventListener('resize', this._resizeHandler);
      }
      
      if (this.chart) {
        this.chart.destroy();
        this.chart = null;
      }
    }
  }));
}
