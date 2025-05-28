/**
 * 圖表初始化兼容腳本
 * 用於確保所有圖表類型都能正確顯示數據
 */

(function() {
  console.log('圖表兼容腳本已啟動');
  
  // 統一初始化所有圖表的方法
  window.initAllCharts = function() {
    console.log('初始化所有圖表');
    
    // 偵測當前頁面的圖表類型
    const pathname = window.location.pathname.toLowerCase();
    
    if (pathname.includes('area.html')) {
      if (typeof window.initAreaChart === 'function') {
        window.initAreaChart();
      } else {
        console.warn('函數 initAreaChart 未定義');
      }
    } else if (pathname.includes('line.html')) {
      if (typeof window.initLineChart === 'function') {
        window.initLineChart();
      } else {
        console.warn('函數 initLineChart 未定義');
      }
    } else if (pathname.includes('column.html')) {
      if (typeof window.initColumnChart === 'function') {
        window.initColumnChart();
      } else {
        console.warn('函數 initColumnChart 未定義');
      }
    } else if (pathname.includes('index.html') || pathname.endsWith('/')) {
      if (typeof window.initCandlestickChart === 'function') {
        window.initCandlestickChart();
      } else {
        console.warn('函數 initCandlestickChart 未定義');
      }
    } else if (pathname.includes('polararea.html')) {
      if (typeof window.initPolarAreaChart === 'function') {
        window.initPolarAreaChart();
      } else {
        console.warn('函數 initPolarAreaChart 未定義');
      }
    } else if (pathname.includes('pie.html')) {
      if (typeof window.initPieChart === 'function') {
        window.initPieChart();
      } else {
        console.warn('函數 initPieChart 未定義');
      }
    } else if (pathname.includes('donut.html')) {
      if (typeof window.initDonutChart === 'function') {
        window.initDonutChart();
      } else {
        console.warn('函數 initDonutChart 未定義');
      }
    } else if (pathname.includes('radar.html')) {
      if (typeof window.initRadarChart === 'function') {
        window.initRadarChart();
      } else {
        console.warn('函數 initRadarChart 未定義');
      }
    } else if (pathname.includes('heatmap.html')) {
      if (typeof window.initHeatmapChart === 'function') {
        window.initHeatmapChart();
      } else {
        console.warn('函數 initHeatmapChart 未定義');
      }
    } else if (pathname.includes('treemap.html')) {
      if (typeof window.initTreemapChart === 'function') {
        window.initTreemapChart();
      } else {
        console.warn('函數 initTreemapChart 未定義');
      }
    } else if (pathname.includes('scatter.html')) {
      if (typeof window.initScatterChart === 'function') {
        window.initScatterChart();
      } else {
        console.warn('函數 initScatterChart 未定義');
      }
    } else if (pathname.includes('mixed.html')) {
      if (typeof window.initMixedChart === 'function') {
        window.initMixedChart();
      } else {
        console.warn('函數 initMixedChart 未定義');
      }
    } else {
      console.log('無法確定當前頁面圖表類型');
    }
  };
  
  // 頁面載入時執行
  document.addEventListener('DOMContentLoaded', function() {
    console.log('DOMContentLoaded: 頁面載入完成');
    
    // 只有當當前頁面有對應的圖表容器時才初始化
    const pathname = window.location.pathname.toLowerCase();
    const chartTypeMatches = [
      { pattern: 'area.html', container: 'areaChart' },
      { pattern: 'line.html', container: 'lineChart' },
      { pattern: 'column.html', container: 'columnChart' },
      { pattern: 'bar.html', container: 'barChart' },
      { pattern: 'polararea.html', container: 'polarAreaChart' },
      { pattern: 'pie.html', container: 'pieChart' },
      { pattern: 'donut.html', container: 'donutChart' },
      { pattern: 'radar.html', container: 'radarChart' },
      { pattern: 'scatter.html', container: 'scatterChart' },
      { pattern: 'heatmap.html', container: 'heatmapChart' },
      { pattern: 'mixed.html', container: 'mixedChart' },
      { pattern: 'treemap.html', container: 'treemapChart' }
    ];
    
    // 檢查當前頁面是否應該初始化圖表
    const shouldInit = chartTypeMatches.some(match => {
      if (pathname.includes(match.pattern)) {
        const containerExists = document.getElementById(match.container) !== null;
        if (!containerExists) {
          // 針對 pie.html 的特殊處理：容器是動態載入的
          if (match.pattern === 'pie.html' || match.pattern === 'donut.html' || match.pattern === 'radar.html' || match.pattern === 'polararea.html' || match.pattern === 'heatmap.html' || match.pattern === 'treemap.html' || match.pattern === 'scatter.html' || match.pattern === 'mixed.html') {
            console.log(`chart-compat: 頁面符合 ${match.pattern}，容器 #${match.container} 為動態載入，將等待 component-loaded 事件。`);
          } else {
            console.warn(`chart-compat: 頁面符合 ${match.pattern}，但找不到容器 #${match.container} (應於 DOMContentLoaded 時存在)`);
          }
        }
        return containerExists; // shouldInit 為 true 若容器已存在 (主要針對非動態載入的圖表)
      }
      return false;
    });

    if (shouldInit || pathname.endsWith('/') || pathname.includes('index.html')) {
      // 對於主頁或已有容器的頁面，仍嘗試初始化
      console.log('chart-compat: DOMContentLoaded - 準備初始化靜態或主頁圖表。');
      setTimeout(window.initAllCharts, 500);
    } else {
      console.log('chart-compat: DOMContentLoaded - 無需立即初始化圖表，部分圖表將等待 component-loaded 事件。');
    }
  });

  // 組件載入後執行
  document.addEventListener('component-loaded', function(e) {
    const componentPath = e.detail.componentPath;
    console.log(`chart-compat: component-loaded - 組件 ${componentPath} 已載入。`);

    let specificChartInitFunction = null;
    let chartType = '';

    if (componentPath.includes('AreaChartContent.html')) { chartType = 'Area'; specificChartInitFunction = window.initAreaChart; }
    else if (componentPath.includes('LineChartContent.html')) { chartType = 'Line'; specificChartInitFunction = window.initLineChart; }
    else if (componentPath.includes('ColumnChartContent.html')) { chartType = 'Column'; specificChartInitFunction = window.initColumnChart; }
    else if (componentPath.includes('CandlestickContent.html')) { chartType = 'Candlestick'; specificChartInitFunction = window.initCandlestickChart; }
    else if (componentPath.includes('PieChartContent.html')) { chartType = 'Pie'; specificChartInitFunction = window.initPieChart; }
    else if (componentPath.includes('DonutChartContent.html')) { chartType = 'Donut'; specificChartInitFunction = window.initDonutChart; }
    else if (componentPath.includes('RadarChartContent.html')) { chartType = 'Radar'; specificChartInitFunction = window.initRadarChart; }
    else if (componentPath.includes('PolarareaChartContent.html')) { chartType = 'PolarArea'; specificChartInitFunction = window.initPolarAreaChart; }
    else if (componentPath.includes('HeatmapChartContent.html')) { chartType = 'Heatmap'; specificChartInitFunction = window.initHeatmapChart; }
    else if (componentPath.includes('TreemapChartContent.html')) { chartType = 'Treemap'; specificChartInitFunction = window.initTreemapChart; }
    else if (componentPath.includes('ScatterChartContent.html')) { chartType = 'Scatter'; specificChartInitFunction = window.initScatterChart; }
    else if (componentPath.includes('MixedChartContent.html')) { chartType = 'Mixed'; specificChartInitFunction = window.initMixedChart; }
    // 可以為其他動態載入內容的圖表頁面添加更多 else if

    if (specificChartInitFunction && typeof specificChartInitFunction === 'function') {
      console.log(`chart-compat: component-loaded - 準備延遲初始化 ${chartType} 圖表。`);
      setTimeout(specificChartInitFunction, 300); // 給予一點緩衝時間確保DOM完全準備好
    } else if (componentPath.includes('Content.html')) {
      // 如果是一個圖表內容組件，但沒有特定的初始化函數被匹配到
      // 可以考慮是否需要一個通用的回退，或者記錄下來以便添加特定處理
      console.log(`chart-compat: component-loaded - ${componentPath} 已載入，但無特定圖表初始化函數與之對應。`);
    }
  });
  
})();
