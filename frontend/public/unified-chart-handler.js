/**
 * 統一圖表處理器
 * 提供各種圖表類型渲染的統一介面與修復功能
 */

(function() {
  console.log('統一圖表處理器已啟用');
  
  // 全局存儲圖表實例
  window.chartInstances = window.chartInstances || {};
  
  // 圖表類型與處理函數對應表
  const chartHandlers = {
    'area': handleAreaChart,        // 區域圖
    'line': handleLineChart,
    'column': handleColumnChart,
    'candlestick': handleCandlestickChart,
    'boxplot': handleBoxplotChart,
    'bar': handleBarChart,
    'bubble': handleBubbleChart,
    'donut': handleDonutChart,
    'funnel': handleFunnelChart,
    'heatmap': handleHeatmapChart,
    'mixed': handleMixedChart,
    'pie': handlePieChart,
    'polarArea': handlePolarAreaChart, // 注意這裡使用駝峰式命名，與 ChartType.POLAR_AREA 保持一致
    'radar': handleRadarChart,
    'scatter': handleScatterChart,
    'stacked_bar': handleStackedBarChart,
    'treemap': handleTreemapChart
  };
  
  // 統一處理圖表渲染
  window.handleChart = function(data, chartType) {
    console.log(`統一處理${chartType}類型的圖表渲染`, data);
    
    // 檢查是否存在對應的處理函數
    const handler = chartHandlers[chartType];
    if (typeof handler === 'function') {
      return handler(data);
    }
    
    // 如果沒有特定處理函數，使用通用處理邏輯
    return handleGenericChart(data, chartType);
  };
  
  // 通用圖表處理邏輯
  function handleGenericChart(data, chartType) {
    const chartElementId = `${chartType}Chart`;
    console.log(`通用處理: ${chartType} 圖表 (容器ID: ${chartElementId})`);
    
    // 檢查圖表容器
    const chartContainer = document.getElementById(chartElementId);
    if (!chartContainer) {
      const errorMsg = `找不到圖表容器元素 #${chartElementId}`;
      console.error(errorMsg);
      if (window.chartErrorHandler) {
        window.chartErrorHandler.showError(chartElementId, errorMsg);
      }
      return false;
    }
    
    // 清除現有的圖表實例
    if (window.ApexCharts) {
      try {
        // 使用 ApexCharts API 清除
        const existingChart = ApexCharts.getChartByID(chartElementId) || window.chartInstances[chartElementId];
        if (existingChart && typeof existingChart.destroy === 'function') {
          console.log(`清除既有${chartType}圖表實例`);
          existingChart.destroy();
          delete window.chartInstances[chartElementId];
        }
      } catch (e) {
        console.warn(`清除圖表時發生錯誤 (${chartElementId}):`, e);
      }
    }
    
    // 確保資料結構正確
    if (!data) {
      const errorMsg = `${chartType}圖表資料無效`;
      console.error(errorMsg);
      if (window.chartErrorHandler) {
        window.chartErrorHandler.showError(chartElementId, errorMsg);
      }
      return false;
    }
    
    // 處理 yaxis.labels.formatter 字串轉換為函數
    if (data.yaxis && Array.isArray(data.yaxis)) {
        data.yaxis = data.yaxis.map(yAxisConfig => {
            if (yAxisConfig && yAxisConfig.labels && typeof yAxisConfig.labels.formatter === 'string') {
                try {
                    // 使用 eval 將字串轉換為函數
                    yAxisConfig.labels.formatter = eval(`(${yAxisConfig.labels.formatter})`);
                } catch (e) {
                    console.error('轉換 yaxis.labels.formatter 字串為函數時出錯:', e);
                }
            }
            return yAxisConfig;
        });
    }
    
    // 確保圖表類型設置正確
    if (!data.chart) data.chart = {};
    
    // 設置正確的圖表類型
    switch (chartType) {
      case 'area':
        data.chart.type = 'area';
        break;
      case 'line':
        data.chart.type = 'line';
        break;
      case 'column':
        data.chart.type = 'bar'; // ApexCharts 中的 column 是 bar 的一種
        if (!data.plotOptions) data.plotOptions = {};
        if (!data.plotOptions.bar) data.plotOptions.bar = {};
        data.plotOptions.bar.horizontal = false;
        break;
      case 'bar':
        data.chart.type = 'bar';
        if (!data.plotOptions) data.plotOptions = {};
        if (!data.plotOptions.bar) data.plotOptions.bar = {};
        data.plotOptions.bar.horizontal = true;
        break;
      case 'candlestick':
        data.chart.type = 'candlestick';
        break;
      case 'boxplot':
        data.chart.type = 'boxPlot';
        break;
      case 'bubble':
        data.chart.type = 'bubble';
        break;
      case 'donut':
        data.chart.type = 'donut';
        break;
      case 'pie':
        data.chart.type = 'pie';
        break;
      case 'polarArea':
        data.chart.type = 'polarArea';
        break;
      case 'radar':
        data.chart.type = 'radar';
        break;
      case 'scatter':
        data.chart.type = 'scatter';
        break;
      case 'heatmap':
        data.chart.type = 'heatmap';
        break;
      default:
        data.chart.type = chartType.replace('_', '');
    }
    
    try {
      console.log(`初始化${chartType}圖表`, data);
      const chart = new ApexCharts(chartContainer, data);
      window.chartInstances[chartElementId] = chart;
      chart.render();
      console.log(`${chartType}圖表渲染完成`);
      return true;
    } catch (error) {
      console.error(`渲染${chartType}圖表時發生錯誤:`, error);
      
      if (window.chartErrorHandler) {
        window.chartErrorHandler.showError(chartElementId, `無法渲染${chartType}圖表: ${error.message}`);
        
        // 嘗試使用替代數據源
        window.chartErrorHandler.retryLoadData(chartType, null, chartElementId, handleGenericChart);
      }
      return false;
    }
  }
  
  // 處理面積圖
  function handleAreaChart(data) {
    console.log('處理面積圖');
    
    // 確保相應的處理函數存在
    if (window.handleAreaChart && window.handleAreaChart !== handleAreaChart) {
      return window.handleAreaChart(data);
    }
    
    return handleGenericChart(data, 'area');
  }
  
  // 處理折線圖
  function handleLineChart(data) {
    console.log('處理折線圖');
    
    // 確保相應的處理函數存在
    if (window.handleLineChart && window.handleLineChart !== handleLineChart) {
      return window.handleLineChart(data);
    }
    
    return handleGenericChart(data, 'line');
  }
  
  // 處理柱狀圖
  function handleColumnChart(data) {
    console.log('處理柱狀圖');
    
    // 確保相應的處理函數存在
    if (window.handleColumnChart && window.handleColumnChart !== handleColumnChart) {
      return window.handleColumnChart(data);
    }
    
    return handleGenericChart(data, 'column');
  }
  
  // 處理蠟燭圖
  function handleCandlestickChart(data) {
    console.log('處理蠟燭圖');
    
    // 確保相應的處理函數存在
    if (window.handleCandlestickChart && window.handleCandlestickChart !== handleCandlestickChart) {
      return window.handleCandlestickChart(data);
    }
    
    return handleGenericChart(data, 'candlestick');
  }
  
  // 處理箱型圖
  function handleBoxplotChart(data) {
    return handleGenericChart(data, 'boxplot');
  }
  
  // 處理條形圖
  function handleBarChart(data) {
    return handleGenericChart(data, 'bar');
  }
  
  // 處理氣泡圖
  function handleBubbleChart(data) {
    return handleGenericChart(data, 'bubble');
  }
  
  // 處理甜甜圈圖
  function handleDonutChart(data) {
    return handleGenericChart(data, 'donut');
  }
  
  // 處理漏斗圖
  function handleFunnelChart(data) {
    return handleGenericChart(data, 'funnel');
  }
  
  // 處理熱點圖
  function handleHeatmapChart(data) {
    return handleGenericChart(data, 'heatmap');
  }
  
  // 處理混合圖
  function handleMixedChart(data) {
    return handleGenericChart(data, 'mixed');
  }
  
  // 處理圓餅圖
  function handlePieChart(data) {
    return handleGenericChart(data, 'pie');
  }
  
  // 處理極區圖
  function handlePolarAreaChart(data) {
    return handleGenericChart(data, 'polararea');
  }
  
  // 處理雷達圖
  function handleRadarChart(data) {
    return handleGenericChart(data, 'radar');
  }
  
  // 處理散點圖
  function handleScatterChart(data) {
    return handleGenericChart(data, 'scatter');
  }
  
  // 處理堆疊條形圖
  function handleStackedBarChart(data) {
    return handleGenericChart(data, 'stacked_bar');
  }
  
  // 處理樹形圖
  function handleTreemapChart(data) {
    return handleGenericChart(data, 'treemap');
  }
  
  // 修復 data-loader.js 中 applyChartData 函數的問題
  if (window.applyChartData) {
    const originalApplyChartData = window.applyChartData;
    window.applyChartData = function(data, chartType) {
      console.log(`增強的 applyChartData: ${chartType}`);
      
      if (window.handleChart) {
        return window.handleChart(data, chartType);
      }
      
      return originalApplyChartData(data, chartType);
    };
  }
})();
