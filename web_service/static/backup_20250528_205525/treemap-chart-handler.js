/**
 * 樹狀圖專用處理函數
 * 解決樹狀圖渲染問題
 */

(function() {
  console.log('樹狀圖專用處理函數已啟動');
  
  // 全局保存樹狀圖實例
  window.treemapChartInstances = {};
  
  // 在頁面載入完成後執行
  document.addEventListener('DOMContentLoaded', function() {
    console.log('檢查是否需要初始化樹狀圖');
    
    // 檢查頁面是否有樹狀圖容器
    const treemapChartContainer = document.getElementById('treemapChart');
    if (treemapChartContainer) {
      console.log('檢測到樹狀圖容器，準備初始化');
      window.initTreemapChart();
    }
  });
  
  // 處理樹狀圖渲染
  window.handleTreemapChart = function(data) {
    console.log('開始處理樹狀圖渲染', data);
    
    // 檢查圖表容器
    const chartContainer = document.getElementById('treemapChart');
    if (!chartContainer) {
      console.error('找不到樹狀圖容器元素 #treemapChart');
      if (window.chartErrorHandler) {
        window.chartErrorHandler.showError('treemapChart', '找不到樹狀圖容器');
      }
      return false;
    }
    
    // 清除現有的圖表實例
    if (window.ApexCharts) {
      try {
        const existingChart = ApexCharts.getChartByID('treemapChart') || window.treemapChartInstances['treemapChart'];
        if (existingChart && typeof existingChart.destroy === 'function') {
          console.log('清除既有樹狀圖實例');
          existingChart.destroy();
        }
      } catch (e) {
        console.warn('清除樹狀圖時發生錯誤:', e);
      }
    }
    
    // 確保資料結構正確
    if (!data) {
      console.error('樹狀圖資料無效');
      if (window.chartErrorHandler) {
        window.chartErrorHandler.showError('treemapChart', '樹狀圖資料無效');
      }
      return false;
    }
    
    // 確保圖表類型設置為treemap
    if (!data.chart) data.chart = {};
    data.chart.type = 'treemap';
    
    // 設置基本配置項
    if (!data.chart.height) data.chart.height = 350;
    if (!data.chart.toolbar) data.chart.toolbar = { show: true };
    
    try {
      console.log('開始渲染樹狀圖', data);
      const chart = new ApexCharts(chartContainer, data);
      chart.render();
      
      // 保存實例引用
      window.treemapChartInstances['treemapChart'] = chart;
      console.log('樹狀圖渲染完成');
      return true;
    } catch (error) {
      console.error('樹狀圖渲染失敗:', error);
      if (window.chartErrorHandler) {
        window.chartErrorHandler.showError('treemapChart', `樹狀圖渲染錯誤: ${error.message}`);
      }
      return false;
    }
  };
  
  // 初始化樹狀圖
  window.initTreemapChart = function(data) {
    console.log('初始化樹狀圖');
    
    // 如果有提供資料，直接使用
    if (data) {
      return window.handleTreemapChart(data);
    }
    
    // 否則加載預設範例資料
    loadTreemapData();
  };
  
  // 加載樹狀圖資料
  function loadTreemapData() {
    console.log('加載樹狀圖資料');
    
    // 嘗試從資料庫或API載入
    const dataUrl = '/static/assets/examples/apexcharts_treemap_server_storage.json';
    
    // 定義備用資料，以備API調用失敗時使用
    const alternativeFiles = [
      'apexcharts_treemap_server_storage.json',
      'apexcharts_treemap_website_content.json',
      'apexcharts_treemap_population.json'
    ];
    
    fetch(dataUrl)
      .then(response => {
        if (!response.ok) throw new Error('載入樹狀圖預設資料失敗');
        return response.json();
      })
      .then(data => {
        window.handleTreemapChart(data);
      })
      .catch(error => {
        console.error('載入樹狀圖資料失敗:', error);
        if (window.chartErrorHandler) {
          window.chartErrorHandler.retryLoadData('treemap', alternativeFiles, 'treemapChart', window.handleTreemapChart);
        } else {
          // 使用內建默認資料
          const defaultData = window.getTreemapChartExamples().basic;
          window.handleTreemapChart(defaultData);
        }
      });
  }
  
  // 載入特定樹狀圖範例
  window.loadTreemapChartExample = function(exampleFile) {
    console.log(`載入樹狀圖範例: ${exampleFile}`);
    
    fetch(`/static/assets/examples/${exampleFile}`)
      .then(response => {
        if (!response.ok) throw new Error(`範例檔案 ${exampleFile} 不存在`);
        return response.json();
      })
      .then(data => {
        window.handleTreemapChart(data);
      })
      .catch(error => {
        console.error(`載入樹狀圖範例失敗: ${exampleFile}`, error);
        if (window.chartErrorHandler) {
          window.chartErrorHandler.showError('treemapChart', `載入範例失敗: ${error.message}`);
        }
      });
  };
  
  // 生成默認的樹狀圖資料
  function generateDefaultTreemapData() {
    return [
      {
        data: [
          {
            x: '服務器A',
            y: 218
          },
          {
            x: '服務器B',
            y: 149
          },
          {
            x: '服務器C',
            y: 184
          },
          {
            x: '服務器D',
            y: 55
          },
          {
            x: '服務器E',
            y: 84
          },
          {
            x: '服務器F',
            y: 31
          },
          {
            x: '服務器G',
            y: 70
          },
          {
            x: '服務器H',
            y: 30
          },
          {
            x: '服務器I',
            y: 44
          },
          {
            x: '服務器J',
            y: 68
          },
          {
            x: '服務器K',
            y: 28
          }
        ]
      }
    ];
  }
  
  // 提供樹狀圖範例資料
  window.getTreemapChartExamples = function() {
    return {
      basic: {
        chart: {
          type: 'treemap',
          height: 350,
          toolbar: {
            show: false
          }
        },
        series: generateDefaultTreemapData(),
        title: {
          text: '伺服器儲存空間使用情況'
        },
        plotOptions: {
          treemap: {
            distributed: true,
            enableShades: false
          }
        }
      },
      colorRange: {
        chart: {
          type: 'treemap',
          height: 350,
          toolbar: {
            show: false
          }
        },
        series: generateDefaultTreemapData(),
        title: {
          text: '伺服器儲存空間視覺化'
        },
        colors: [
          '#3B82F6',
          '#22C55E',
          '#EAB308',
          '#EC4899',
          '#8B5CF6',
          '#14B8A6',
          '#F97316',
          '#F43F5E'
        ],
        plotOptions: {
          treemap: {
            distributed: true,
            enableShades: false
          }
        }
      }
    };
  };
})();
