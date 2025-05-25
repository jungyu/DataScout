/**
 * 圖表渲染驗證腳本
 * 用於測試修復後的圖表是否能夠正確渲染
 */

(function() {
  console.log('圖表驗證腳本已啟動');

  // 在頁面載入完成後執行
  document.addEventListener('DOMContentLoaded', function() {
    console.log('開始圖表驗證測試');

    // 等待組件載入完成
    document.addEventListener('component-loaded', function() {
      // 等待頁面上所有組件載入完成
      setTimeout(function() {
        // 檢測當前頁面類型
        const currentUrl = window.location.pathname;
        
        if (currentUrl.includes('index.html') || currentUrl === '/' || currentUrl.endsWith('/')) {
          console.log('檢測到蠟燭圖頁面，開始驗證蠟燭圖渲染');
          verifyCandlestickChart();
        } else if (currentUrl.includes('line.html')) {
          console.log('檢測到折線圖頁面，開始驗證折線圖渲染');
          verifyLineChart();
        } else if (currentUrl.includes('polararea.html')) {
          console.log('檢測到極區圖頁面，開始驗證極區圖渲染');
          verifyPolarAreaChart();
        } else if (currentUrl.includes('area.html')) {
          console.log('檢測到區域圖頁面，開始驗證區域圖渲染');
          verifyAreaChart();
        } else if (currentUrl.includes('bar.html')) {
          console.log('檢測到條形圖頁面，開始驗證條形圖渲染');
          verifyBarChart();
        } else if (currentUrl.includes('column.html')) {
          console.log('檢測到柱狀圖頁面，開始驗證柱狀圖渲染');
          verifyColumnChart();
        } else if (currentUrl.includes('pie.html')) {
          console.log('檢測到餅圖頁面，開始驗證餅圖渲染');
          verifyPieChart();
        } else if (currentUrl.includes('donut.html')) {
          console.log('檢測到甜甜圈圖頁面，開始驗證甜甜圈圖渲染');
          verifyDonutChart();
        } else if (currentUrl.includes('radar.html')) {
          console.log('檢測到雷達圖頁面，開始驗證雷達圖渲染');
          verifyRadarChart();
        } else if (currentUrl.includes('heatmap.html')) {
          console.log('檢測到熱力圖頁面，開始驗證熱力圖渲染');
          verifyHeatmapChart();
        } else if (currentUrl.includes('treemap.html')) {
          console.log('檢測到樹狀圖頁面，開始驗證樹狀圖渲染');
          verifyTreemapChart();
        } else if (currentUrl.includes('scatter.html')) {
          console.log('檢測到散點圖頁面，開始驗證散點圖渲染');
          verifyScatterChart();
        } else if (currentUrl.includes('mixed.html')) {
          console.log('檢測到混合圖頁面，開始驗證混合圖渲染');
          verifyMixedChart();
        }
      }, 1000);
    });
  });

  // 通用圖表驗證函數
  function verifyChartRendering(chartType, containerId) {
    const chartContainer = document.getElementById(containerId);
    if (!chartContainer) {
      console.error(`${chartType}驗證失敗：找不到圖表容器 #${containerId}`);
      return false;
    }

    // 檢查圖表實例
    const instanceVarName = `${containerId}Instances`;
    if (window[instanceVarName] && window[instanceVarName][containerId]) {
      console.log(`${chartType}驗證成功：找到有效的圖表實例`);
      return true;
    } else {
      console.warn(`${chartType}驗證警告：圖表實例未找到，可能需要修復`);
      
      // 檢查錯誤處理器狀態
      const errorContainer = chartContainer.querySelector('.chart-error-container');
      if (errorContainer) {
        console.warn(`${chartType}發現錯誤容器，錯誤處理器已啟動`);
        return false;
      }
      
      // 檢查圖表的內部元素
      const hasApexChart = chartContainer.querySelector('.apexcharts-canvas');
      if (hasApexChart) {
        console.log(`${chartType}驗證：發現ApexCharts畫布元素，圖表可能已渲染`);
        return true;
      }
      
      return false;
    }
  }

  // 以下是各種圖表的專用驗證函數
  
  // 驗證蠟燭圖渲染
  function verifyCandlestickChart() {
    return verifyChartRendering('蠟燭圖', 'candlestickChart');
  }

  // 驗證折線圖渲染
  function verifyLineChart() {
    return verifyChartRendering('折線圖', 'lineChart');
  }
  
  // 驗證區域圖渲染
  function verifyAreaChart() {
    return verifyChartRendering('區域圖', 'areaChart');
  }
  
  // 驗證條形圖渲染
  function verifyBarChart() {
    return verifyChartRendering('條形圖', 'barChart');
  }
  
  // 驗證柱狀圖渲染
  function verifyColumnChart() {
    return verifyChartRendering('柱狀圖', 'columnChart');
  }
  
  // 驗證餅圖渲染
  function verifyPieChart() {
    return verifyChartRendering('餅圖', 'pieChart');
  }
  
  // 驗證甜甜圈圖渲染
  function verifyDonutChart() {
    return verifyChartRendering('甜甜圈圖', 'donutChart');
  }
  
  // 驗證雷達圖渲染
  function verifyRadarChart() {
    return verifyChartRendering('雷達圖', 'radarChart');
  }
  
  // 驗證極區域圖渲染
  function verifyPolarAreaChart() {
    return verifyChartRendering('極區域圖', 'polarAreaChart');  // 使用正確的 ID
  }
  
  // 驗證熱力圖渲染
  function verifyHeatmapChart() {
    return verifyChartRendering('熱力圖', 'heatmapChart');
  }
  
  // 驗證樹狀圖渲染
  function verifyTreemapChart() {
    return verifyChartRendering('樹狀圖', 'treemapChart');
  }
  
  // 驗證散點圖渲染
  function verifyScatterChart() {
    return verifyChartRendering('散點圖', 'scatterChart');
  }
  
  // 驗證混合圖渲染
  function verifyMixedChart() {
    return verifyChartRendering('混合圖', 'mixedChart');
  }

  // 將驗證函數暴露到全局範圍
  window.ChartVerification = {
    verifyChart: verifyChartRendering,
    runVerification: function(chartType) {
      console.log(`手動執行${chartType}圖表驗證`);
      switch(chartType.toLowerCase()) {
        case 'candlestick': return verifyCandlestickChart();
        case 'line': return verifyLineChart();
        case 'area': return verifyAreaChart();
        case 'bar': return verifyBarChart();
        case 'column': return verifyColumnChart();
        case 'pie': return verifyPieChart();
        case 'donut': return verifyDonutChart();
        case 'radar': return verifyRadarChart();
        case 'polararea': 
        case 'polarArea': 
        case 'polar_area': 
          return verifyPolarAreaChart();
        case 'heatmap': return verifyHeatmapChart();
        case 'treemap': return verifyTreemapChart();
        case 'scatter': return verifyScatterChart();
        case 'mixed': return verifyMixedChart();
        default: 
          console.error(`未知的圖表類型: ${chartType}`);
          return false;
      }
    }
  };
})();
