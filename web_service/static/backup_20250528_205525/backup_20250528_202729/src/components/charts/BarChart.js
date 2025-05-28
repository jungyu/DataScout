   // 長條圖組件
import { BaseChart } from './BaseChart.js';

/**
 * 長條圖組件
 * 繼承自 BaseChart，提供長條圖的專門功能
 */
export class BarChart extends BaseChart {
  constructor(containerId, data, options = {}) {
    super(containerId, data, options);
    this.chartType = 'bar';
  }

  /**
   * 獲取長條圖的預設配置
   */
  getDefaultOptions() {
    const baseOptions = super.getDefaultOptions();
    
    return {
      ...baseOptions,
      chart: {
        ...baseOptions.chart,
        type: 'bar',
        height: 350,
        toolbar: {
          ...baseOptions.chart.toolbar,
          show: true
        }
      },
      plotOptions: {
        bar: {
          borderRadius: 4,
          horizontal: false, // 垂直長條圖，設為 true 則為水平
          columnWidth: '60%',
          dataLabels: {
            position: 'top'
          }
        }
      },
      dataLabels: {
        enabled: false
      },
      stroke: {
        show: true,
        width: 2,
        colors: ['transparent']
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
        categories: [],
        labels: {
          style: {
            fontSize: '12px'
          }
        }
      },
      yaxis: {
        title: {
          text: this.options.yAxisTitle || '數值'
        },
        labels: {
          formatter: (value) => {
            return value ? value.toFixed(2) : '0.00';
          }
        }
      },
      fill: {
        opacity: 1
      },
      tooltip: {
        y: {
          formatter: (val) => {
            return val ? val.toFixed(2) : '0.00';
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
   * 格式化長條圖資料
   */
  formatData(data) {
    try {
      // 如果已經是 ApexCharts 格式，直接返回
      if (Array.isArray(data) && data.length > 0 && data[0].name && data[0].data) {
        return data;
      }

      // 如果是單一資料集
      if (Array.isArray(data) && data.length > 0) {
        const firstItem = data[0];
        
        // 檢查是否有類別和值的物件陣列
        if (typeof firstItem === 'object' && firstItem.category !== undefined && firstItem.value !== undefined) {
          // { category: 'A', value: 100 } 格式
          const categories = data.map(item => item.category);
          const values = data.map(item => parseFloat(item.value) || 0);
          
          // 更新 x 軸類別
          this.updateCategories(categories);
          
          return [{
            name: this.options.seriesName || '數值',
            data: values
          }];
        }
        
        // 檢查是否有 label 和 value 的物件陣列
        if (typeof firstItem === 'object' && firstItem.label !== undefined && firstItem.value !== undefined) {
          // { label: 'A', value: 100 } 格式
          const categories = data.map(item => item.label);
          const values = data.map(item => parseFloat(item.value) || 0);
          
          this.updateCategories(categories);
          
          return [{
            name: this.options.seriesName || '數值',
            data: values
          }];
        }
        
        // 檢查是否有 name 和 data 的物件陣列（分組長條圖）
        if (typeof firstItem === 'object' && firstItem.name !== undefined && firstItem.data !== undefined) {
          return data.map(series => ({
            name: series.name,
            data: Array.isArray(series.data) ? series.data.map(val => parseFloat(val) || 0) : []
          }));
        }
        
        // 純數值陣列，產生假的類別
        if (typeof firstItem === 'number') {
          const categories = data.map((_, index) => `類別 ${index + 1}`);
          const values = data.map(val => parseFloat(val) || 0);
          
          this.updateCategories(categories);
          
          return [{
            name: this.options.seriesName || '數值',
            data: values
          }];
        }
      }

      // 預設情況：回傳空資料
      console.warn('BarChart: 無法識別的資料格式，使用預設空資料');
      return [{
        name: this.options.seriesName || '數值',
        data: []
      }];

    } catch (error) {
      console.error('BarChart formatData 錯誤:', error);
      return [{
        name: this.options.seriesName || '數值',
        data: []
      }];
    }
  }

  /**
   * 更新 x 軸類別
   */
  updateCategories(categories) {
    if (this.chart) {
      this.chart.updateOptions({
        xaxis: {
          categories: categories
        }
      });
    } else {
      // 如果圖表還沒初始化，儲存到選項中
      this.options.xaxis = {
        ...this.options.xaxis,
        categories: categories
      };
    }
  }

  /**
   * 設定長條圖方向
   */
  setOrientation(horizontal = false) {
    this.updateOptions({
      plotOptions: {
        bar: {
          horizontal: horizontal
        }
      }
    });
  }

  /**
   * 設定長條圖樣式
   */
  setBarStyle(columnWidth = '60%', borderRadius = 4) {
    this.updateOptions({
      plotOptions: {
        bar: {
          columnWidth: columnWidth,
          borderRadius: borderRadius
        }
      }
    });
  }

  /**
   * 啟用/停用資料標籤
   */
  setDataLabelsEnabled(enabled = true, position = 'top') {
    this.updateOptions({
      dataLabels: {
        enabled: enabled,
        position: position
      }
    });
  }

  /**
   * 設定圖表為堆疊模式
   */
  setStacked(enabled = true) {
    this.updateOptions({
      chart: {
        stacked: enabled
      }
    });
  }

  /**
   * 設定圖表為分組模式
   */
  setGrouped() {
    this.updateOptions({
      chart: {
        stacked: false
      },
      plotOptions: {
        bar: {
          columnWidth: '60%'
        }
      }
    });
  }

  /**
   * 新增新的類別和資料
   */
  addCategory(category, value, seriesIndex = 0) {
    if (!this.chart) return;

    try {
      // 更新類別
      const currentOptions = this.chart.options;
      const newCategories = [...(currentOptions.xaxis.categories || []), category];
      
      // 更新資料
      const currentSeries = this.chart.options.series || [];
      const updatedSeries = currentSeries.map((series, index) => {
        if (index === seriesIndex) {
          return {
            ...series,
            data: [...series.data, parseFloat(value) || 0]
          };
        }
        return {
          ...series,
          data: [...series.data, 0] // 其他系列補 0
        };
      });

      this.chart.updateOptions({
        xaxis: {
          categories: newCategories
        }
      });
      
      this.chart.updateSeries(updatedSeries);

      console.log('BarChart: 新增類別和資料成功');
    } catch (error) {
      this.handleError(error, '新增類別');
    }
  }

  /**
   * 清除所有資料
   */
  clearData() {
    if (!this.chart) return;

    this.updateOptions({
      xaxis: {
        categories: []
      }
    });

    this.updateData([{
      name: this.options.seriesName || '數值',
      data: []
    }]);
  }
}

/**
 * 工廠函數：建立長條圖實例
 */
export function createBarChart(containerId, data, options = {}) {
  return new BarChart(containerId, data, options);
}

/**
 * 全域處理函數 (兼容舊的實現)
 */
if (typeof window !== 'undefined') {
  window.handleBarChart = function(data) {
    console.log('使用全域 handleBarChart 函數');
    
    const chartContainer = document.getElementById('barChart');
    if (!chartContainer) {
      console.error('找不到長條圖容器元素 #barChart');
      return;
    }

    try {
      // 建立 BarChart 實例
      const barChart = new BarChart('barChart', data);
      barChart.init();
      
      // 儲存到全域以便其他地方使用
      window.currentBarChart = barChart;
      window.barChartInstances = window.barChartInstances || {};
      window.barChartInstances['barChart'] = barChart;
      
    } catch (error) {
      console.error('全域 handleBarChart 錯誤:', error);
    }
  };
  
  // 初始化長條圖函數
  window.initBarChart = function() {
    console.log('初始化長條圖...');
    window.loadBarData();
  };
  
  // 載入長條圖資料函數
  window.loadBarData = function(dataType = 'default') {
    console.log(`載入長條圖資料 (類型: ${dataType})`);
    
    // 模擬資料
    const sampleData = [
      { category: '一月', value: 50 },
      { category: '二月', value: 75 },
      { category: '三月', value: 100 },
      { category: '四月', value: 85 },
      { category: '五月', value: 90 }
    ];
    
    if (window.handleBarChart) {
      window.handleBarChart(sampleData);
    }
  };
}