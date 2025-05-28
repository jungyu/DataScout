   // 折線圖組件
import { BaseChart } from './BaseChart.js';

/**
 * 折線圖組件
 * 繼承自 BaseChart，提供折線圖的專門功能
 */
export class LineChart extends BaseChart {
  constructor(containerId, data, options = {}) {
    super(containerId, data, options);
    this.chartType = 'line';
  }

  /**
   * 獲取折線圖的預設配置
   */
  getDefaultOptions() {
    const baseOptions = super.getDefaultOptions();
    
    return {
      ...baseOptions,
      chart: {
        ...baseOptions.chart,
        type: 'line',
        height: 350,
        zoom: {
          enabled: true,
          type: 'x',
          autoScaleYaxis: true
        },
        toolbar: {
          ...baseOptions.chart.toolbar,
          autoSelected: 'zoom'
        }
      },
      stroke: {
        curve: 'smooth',
        width: 2
      },
      markers: {
        size: 4,
        hover: {
          size: 6
        }
      },
      grid: {
        show: true,
        borderColor: '#e0e0e0',
        strokeDashArray: 4,
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
      xaxis: {
        type: 'datetime',
        labels: {
          format: 'yyyy-MM-dd'
        }
      },
      yaxis: {
        labels: {
          formatter: (value) => {
            return value ? value.toFixed(2) : '0.00';
          }
        }
      },
      tooltip: {
        enabled: true,
        x: {
          format: 'yyyy-MM-dd'
        },
        y: {
          formatter: (value) => {
            return value ? value.toFixed(2) : '0.00';
          }
        }
      },
      legend: {
        position: 'top',
        horizontalAlign: 'left'
      }
    };
  }

  /**
   * 格式化折線圖資料
   */
  formatData(data) {
    try {
      // 如果已經是 ApexCharts 格式，直接返回
      if (Array.isArray(data) && data.length > 0 && data[0].name && data[0].data) {
        return data;
      }

      // 如果是單一資料集
      if (Array.isArray(data) && data.length > 0) {
        // 檢查資料格式
        const firstItem = data[0];
        
        if (typeof firstItem === 'object' && firstItem.x !== undefined && firstItem.y !== undefined) {
          // { x: date, y: value } 格式
          return [{
            name: this.options.seriesName || '數值',
            data: data.map(item => ({
              x: new Date(item.x).getTime(),
              y: parseFloat(item.y) || 0
            }))
          }];
        }
        
        if (typeof firstItem === 'object' && firstItem.date !== undefined && firstItem.value !== undefined) {
          // { date: date, value: value } 格式
          return [{
            name: this.options.seriesName || '數值',
            data: data.map(item => ({
              x: new Date(item.date).getTime(),
              y: parseFloat(item.value) || 0
            }))
          }];
        }
        
        if (typeof firstItem === 'number') {
          // 純數值陣列，產生假的日期
          return [{
            name: this.options.seriesName || '數值',
            data: data.map((value, index) => ({
              x: new Date(Date.now() + index * 24 * 60 * 60 * 1000).getTime(),
              y: parseFloat(value) || 0
            }))
          }];
        }
      }

      // 預設情況：回傳空資料
      console.warn('LineChart: 無法識別的資料格式，使用預設空資料');
      return [{
        name: this.options.seriesName || '數值',
        data: []
      }];

    } catch (error) {
      console.error('LineChart formatData 錯誤:', error);
      return [{
        name: this.options.seriesName || '數值',
        data: []
      }];
    }
  }

  /**
   * 設定折線圖的顏色主題
   */
  setColorTheme(colors) {
    if (!Array.isArray(colors)) {
      colors = [colors];
    }
    
    this.updateOptions({
      colors: colors
    });
  }

  /**
   * 設定資料點標記樣式
   */
  setMarkerStyle(size = 4, hoverSize = 6) {
    this.updateOptions({
      markers: {
        size: size,
        hover: {
          size: hoverSize
        }
      }
    });
  }

  /**
   * 設定折線樣式
   */
  setStrokeStyle(curve = 'smooth', width = 2) {
    this.updateOptions({
      stroke: {
        curve: curve,
        width: width
      }
    });
  }

  /**
   * 啟用/停用縮放功能
   */
  setZoomEnabled(enabled = true, type = 'x') {
    this.updateOptions({
      chart: {
        zoom: {
          enabled: enabled,
          type: type,
          autoScaleYaxis: true
        }
      }
    });
  }

  /**
   * 新增新的資料點
   */
  addDataPoint(seriesIndex = 0, dataPoint) {
    if (!this.chart) return;

    try {
      const formattedPoint = {
        x: new Date(dataPoint.x || dataPoint.date).getTime(),
        y: parseFloat(dataPoint.y || dataPoint.value) || 0
      };

      this.chart.appendData([{
        data: [formattedPoint]
      }]);

      console.log('LineChart: 新增資料點成功');
    } catch (error) {
      this.handleError(error, '新增資料點');
    }
  }

  /**
   * 清除所有資料
   */
  clearData() {
    if (!this.chart) return;

    this.updateData([{
      name: this.options.seriesName || '數值',
      data: []
    }]);
  }
}

/**
 * 工廠函數：建立折線圖實例
 */
export function createLineChart(containerId, data, options = {}) {
  return new LineChart(containerId, data, options);
}

/**
 * 全域處理函數 (兼容舊的實現)
 */
if (typeof window !== 'undefined') {
  window.handleLineChart = function(data) {
    console.log('使用全域 handleLineChart 函數');
    
    const chartContainer = document.getElementById('lineChart');
    if (!chartContainer) {
      console.error('找不到折線圖容器元素 #lineChart');
      return;
    }

    try {
      // 建立 LineChart 實例
      const lineChart = new LineChart('lineChart', data);
      lineChart.init();
      
      // 儲存到全域以便其他地方使用
      window.currentLineChart = lineChart;
      
    } catch (error) {
      console.error('全域 handleLineChart 錯誤:', error);
    }
  };
}