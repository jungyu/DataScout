/**
 * 甜甜圈圖專用處理函數
 * 解決甜甜圈圖渲染問題
 */

(function() {
  console.log('甜甜圈圖專用處理函數已啟動');
  
  // 全局保存甜甜圈圖實例
  window.donutChartInstances = {};
  
  // 在頁面載入完成後執行
  document.addEventListener('DOMContentLoaded', function() {
    console.log('檢查是否需要初始化甜甜圈圖');
    
    // 檢查頁面是否有甜甜圈圖容器
    const donutChartContainer = document.getElementById('donutChart');
    if (donutChartContainer) {
      console.log('檢測到甜甜圈圖容器，準備初始化');
      window.initDonutChart();
    }
  });
  
  // 處理甜甜圈圖渲染
  window.handleDonutChart = function(data) {
    console.log('開始處理甜甜圈圖渲染', data);
    
    // 檢查圖表容器
    const chartContainer = document.getElementById('donutChart');
    if (!chartContainer) {
      console.error('找不到甜甜圈圖容器元素 #donutChart');
      if (window.chartErrorHandler) {
        window.chartErrorHandler.showError('donutChart', '找不到甜甜圈圖容器');
      }
      return false;
    }
    
    // 清除現有的圖表實例
    if (window.ApexCharts) {
      try {
        const existingChart = ApexCharts.getChartByID('donutChart') || window.donutChartInstances['donutChart'];
        if (existingChart && typeof existingChart.destroy === 'function') {
          console.log('清除既有甜甜圈圖實例');
          existingChart.destroy();
        }
      } catch (e) {
        console.warn('清除甜甜圈圖時發生錯誤:', e);
      }
    }
    
    // 確保資料結構正確
    if (!data) {
      console.error('甜甜圈圖資料無效');
      if (window.chartErrorHandler) {
        window.chartErrorHandler.showError('donutChart', '甜甜圈圖資料無效');
      }
      return false;
    }
    
    // 確保圖表類型設置為donut
    if (!data.chart) data.chart = {};
    data.chart.type = 'donut';
    
    // 確保有基本配置
    if (!data.responsive) {
      data.responsive = [{
        breakpoint: 480,
        options: {
          chart: {
            width: 280
          },
          legend: {
            position: 'bottom'
          }
        }
      }];
    }
    
    // 確保有標籤配置
    if (!data.dataLabels) {
      data.dataLabels = {
        enabled: true,
        formatter: function(val) {
          return val.toFixed(1) + "%"
        }
      };
    }
    
    // 使用通用 JSON 函數處理工具處理格式化器
    if (data && window.processJsonFunctions) {
      data = window.processJsonFunctions(data);
      console.log('使用通用 JSON 函數處理工具處理甜甜圈圖數據');
    }
    
    try {
      console.log('初始化甜甜圈圖', data);
      const chart = new ApexCharts(chartContainer, data);
      window.donutChartInstances['donutChart'] = chart;
      chart.render();
      console.log('甜甜圈圖渲染完成');
      return true;
    } catch (error) {
      console.error('渲染甜甜圈圖時發生錯誤:', error);
      
      if (window.chartErrorHandler) {
        window.chartErrorHandler.showError('donutChart', `無法渲染甜甜圈圖: ${error.message}`);
        
        // 嘗試使用替代數據源
        const alternativeFiles = [
          'apexcharts_donut_timealloc.json'
        ];
        
        window.chartErrorHandler.retryLoadData('donut', alternativeFiles, 'donutChart', window.handleDonutChart);
      } else {
        chartContainer.innerHTML = `
          <div class="flex flex-col items-center justify-center h-full">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-error mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <p class="text-base text-error font-medium">渲染甜甜圈圖失敗: ${error.message}</p>
            <button class="btn btn-sm btn-outline btn-error mt-4" onclick="location.reload()">重新整理頁面</button>
          </div>
        `;
      }
      return false;
    }
  };
  
  // 初始化甜甜圈圖
  window.initDonutChart = function() {
    console.log('初始化甜甜圈圖...');
    
    // 如果有預設配置則載入
    window.loadDonutData();
  };
  
  // 載入甜甜圈圖資料
  window.loadDonutData = function(dataType = 'default') {
    console.log(`載入甜甜圈圖資料 (類型: ${dataType})`);
    
    let fileName;
    switch (dataType.toLowerCase()) {
      case 'timealloc':
      case 'default':
        fileName = 'apexcharts_donut_timealloc.json';
        break;
      default:
        fileName = 'apexcharts_donut_timealloc.json';
    }
    
    // 檢查是否由統一資料載入器處理
    if (window.DataLoader && typeof window.DataLoader.loadChartData === 'function') {
      window.DataLoader.loadChartData('donut', fileName)
        .then(data => {
          if (data) {
            window.handleDonutChart(data);
          } else {
            console.error('載入甜甜圈圖預設資料失敗 (經由統一資料載入器)');
            if (window.chartErrorHandler) {
              window.chartErrorHandler.showError('donutChart', '載入甜甜圈圖預設資料失敗');
            }
          }
        })
        .catch(error => {
          console.error('載入甜甜圈圖預設資料時發生錯誤:', error);
          if (window.chartErrorHandler) {
            window.chartErrorHandler.showError('donutChart', `載入甜甜圈圖預設資料失敗: ${error.message}`);
          }
        });
    } else {
      console.warn('找不到統一資料載入器，嘗試直接載入甜甜圈圖資料');
      
      // 直接載入資料的備用方法
      fetch(`/static/assets/examples/${fileName}`)
        .then(response => {
          if (!response.ok) throw new Error(`無法載入檔案 ${fileName} (狀態碼: ${response.status})`);
          return response.text(); // 先取得文本再解析，以便處理JSON格式問題
        })
        .then(text => {
          // 嘗試解析JSON，處理可能的格式問題
          let data;
          
          try {
            // 首先嘗試透過JSON增強工具解析
            if (window.JSONEnhancer && typeof window.JSONEnhancer.parse === 'function') {
              data = window.JSONEnhancer.parse(text);
              console.log('使用JSON增強工具成功解析甜甜圈圖資料');
            } else {
              // 若沒有增強工具，使用標準解析
              data = JSON.parse(text);
            }
          } catch (e) {
            console.warn(`解析甜甜圈圖JSON時發生錯誤，嘗試修復: ${e.message}`);
            
            try {
              // 移除註釋並嘗試再次解析
              const processedText = text.replace(/\/\/.*$/gm, '').trim();
              data = JSON.parse(processedText);
            } catch (e2) {
              console.error(`即使移除註釋也無法解析JSON: ${e2.message}`);
              throw e2;
            }
          }
          
          // 處理JSON中的函數字串
          if (data && window.processJsonFunctions) {
            data = window.processJsonFunctions(data);
          }
          
          window.handleDonutChart(data);
        })
        .catch(error => {
          console.error('直接載入甜甜圈圖資料時發生錯誤:', error);
          if (window.chartErrorHandler) {
            window.chartErrorHandler.showError('donutChart', `載入甜甜圈圖預設資料失敗: ${error.message}`);
          }
        });
    }
  };
  
  // 提供甜甜圈圖範例資料
  window.getDonutChartExamples = function() {
    return {
      basic: {
        chart: {
          type: 'donut',
          height: 350
        },
        series: [44, 55, 41, 17, 15],
        labels: ['團隊A', '團隊B', '團隊C', '團隊D', '團隊E'],
        colors: ['#3B82F6', '#10B981', '#F97316', '#8B5CF6', '#EC4899'],
        responsive: [{
          breakpoint: 480,
          options: {
            chart: {
              width: 280
            },
            legend: {
              position: 'bottom'
            }
          }
        }],
        dataLabels: {
          enabled: true,
          formatter: function(val) {
            return val.toFixed(1) + "%"
          }
        },
        legend: {
          position: 'right'
        }
      }
    };
  };
})();
