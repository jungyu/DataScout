   // 蠟燭圖元件
import ApexCharts from 'apexcharts';

/**
 * 蠟燭圖元件
 * @param {string} containerId - 圖表容器ID
 * @param {object} data - 圖表數據
 * @param {object} options - 自訂選項
 */
export class CandlestickChart {
  constructor(containerId, data, options = {}) {
    this.containerId = containerId;
    this.data = data;
    this.options = options;
    this.chart = null;
  }

  // 初始化圖表
  init() {
    const defaultOptions = {
      chart: {
        type: 'candlestick',
        height: 350,
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
      title: {
        text: this.options.title || '蠟燭圖',
        align: 'left'
      },
      xaxis: {
        type: 'datetime',
        labels: {
          formatter: function(val) {
            return new Date(val).toLocaleTimeString('zh-TW', {hour: '2-digit', minute:'2-digit'});
          }
        }
      },
      yaxis: {
        tooltip: {
          enabled: true
        }
      },
      plotOptions: {
        candlestick: {
          colors: {
            upward: '#22c55e',
            downward: '#ef4444'
          }
        }
      },
      tooltip: {
        enabled: true,
        theme: 'light',
        x: {
          format: 'HH:mm dd MMM'
        }
      }
    };

    // 合併自訂選項
    const chartOptions = {
      ...defaultOptions,
      series: [{
        name: this.options.seriesName || '價格',
        data: this.data
      }]
    };

    // 如果存在圖表實例，先銷毀
    if (this.chart) {
      this.chart.destroy();
    }

    // 建立新的圖表實例
    this.chart = new ApexCharts(document.querySelector(`#${this.containerId}`), chartOptions);
    this.chart.render();
  }

  // 更新圖表數據
  updateData(newData) {
    if (!this.chart) return;
    this.data = newData;
    this.chart.updateSeries([{
      name: this.options.seriesName || '價格',
      data: this.data
    }]);
  }

  // 導出圖表為 PNG
  exportToPNG() {
    if (!this.chart) return;
    this.chart.dataURI().then(({ imgURI }) => {
      const link = document.createElement('a');
      link.href = imgURI;
      link.download = `${this.options.title || 'candlestick-chart'}.png`;
      link.click();
    });
  }

  // 導出圖表為 SVG
  exportToSVG() {
    if (!this.chart) return;
    this.chart.dataURI('svg').then(({ imgURI }) => {
      const link = document.createElement('a');
      link.href = imgURI;
      link.download = `${this.options.title || 'candlestick-chart'}.svg`;
      link.click();
    });
  }
}