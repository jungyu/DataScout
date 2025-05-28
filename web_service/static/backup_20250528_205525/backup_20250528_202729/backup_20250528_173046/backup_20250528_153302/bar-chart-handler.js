/**
 * 長條圖專用處理函數
 * 解決長條圖渲染問題
 */

(function() {
  console.log('長條圖專用處理函數已啟動');
  
  // 全局保存長條圖實例
  window.barChartInstances = {};
  
  // 在頁面載入完成後執行
  document.addEventListener('DOMContentLoaded', function() {
    console.log('檢查是否需要初始化長條圖');
    
    // 檢查頁面是否有長條圖容器
    const barChartContainer = document.getElementById('barChart');
    if (barChartContainer) {
      console.log('檢測到長條圖容器，準備初始化');
      window.initBarChart();
    }
  });
  
  // 處理長條圖渲染
  window.handleBarChart = function(data) {
    console.log('開始處理長條圖渲染', data);
    
    // 檢查圖表容器
    const chartContainer = document.getElementById('barChart');
    if (!chartContainer) {
      console.error('找不到長條圖容器元素 #barChart');
      if (window.chartErrorHandler) {
        window.chartErrorHandler.showError('barChart', '找不到長條圖容器');
      }
      return false;
    }
    
    // 清除現有的圖表實例
    if (window.ApexCharts) {
      try {
        const existingChart = ApexCharts.getChartByID('barChart') || window.barChartInstances['barChart'];
        if (existingChart && typeof existingChart.destroy === 'function') {
          console.log('清除既有長條圖實例');
          existingChart.destroy();
        }
      } catch (e) {
        console.warn('清除長條圖時發生錯誤:', e);
      }
    }
    
    // 確保資料結構正確
    if (!data) {
      console.error('長條圖資料無效');
      if (window.chartErrorHandler) {
        window.chartErrorHandler.showError('barChart', '長條圖資料無效');
      }
      return false;
    }
    
    // 確保圖表類型設置為bar
    if (!data.chart) data.chart = {};
    data.chart.type = 'bar';
    
    // 確保有基本配置
    if (!data.plotOptions) {
      data.plotOptions = {
        bar: {
          horizontal: false,
          columnWidth: '55%',
          endingShape: 'rounded'
        }
      };
    }      // 使用通用 JSON 函數處理工具處理格式化器
    if (data && window.processJsonFunctions) {
      data = window.processJsonFunctions(data);
      console.log('使用通用 JSON 函數處理工具處理長條圖數據');
    }
    
    try {
      console.log('初始化長條圖', data);
      const chart = new ApexCharts(chartContainer, data);
      window.barChartInstances['barChart'] = chart;
      chart.render();
      console.log('長條圖渲染完成');
      return true;
    } catch (error) {
      console.error('渲染長條圖時發生錯誤:', error);
      
      if (window.chartErrorHandler) {
        window.chartErrorHandler.showError('barChart', `無法渲染長條圖: ${error.message}`);
        
        // 嘗試使用替代數據源
        const alternativeFiles = [
          'apexcharts_bar_budget.json',
          'apexcharts_bar_performance.json',
          'apexcharts_grouped_bar_sales.json',
          'apexcharts_stacked_bar_finance.json',
          'apexcharts_stacked_bar_city.json'
        ];
        
        window.chartErrorHandler.retryLoadData('bar', alternativeFiles, 'barChart', window.handleBarChart);
      } else {
        chartContainer.innerHTML = `
          <div class="flex flex-col items-center justify-center h-full">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-error mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <p class="text-base text-error font-medium">渲染長條圖失敗: ${error.message}</p>
            <button class="btn btn-sm btn-outline btn-error mt-4" onclick="location.reload()">重新整理頁面</button>
          </div>
        `;
      }
      return false;
    }
  };
  
  // 初始化長條圖
  window.initBarChart = function() {
    console.log('初始化長條圖...');
    
    // 如果有預設配置則載入
    window.loadBarData();
  };
  
  // 載入長條圖資料
  window.loadBarData = function(dataType = 'default') {
    console.log(`載入長條圖資料 (類型: ${dataType})`);
    
    let fileName;
    switch (dataType.toLowerCase()) {
      case 'budget':
        fileName = 'apexcharts_bar_budget.json';
        break;
      case 'performance':
        fileName = 'apexcharts_bar_performance.json';
        break;
      case 'sales':
        fileName = 'apexcharts_grouped_bar_sales.json';
        break;
      case 'stacked':
        fileName = 'apexcharts_stacked_bar_finance.json';
        break;
      case 'default':
      default:
        fileName = 'apexcharts_bar_budget.json';
    }
    
    // 檢查是否由統一資料載入器處理
    if (window.DataLoader && typeof window.DataLoader.loadChartData === 'function') {
      window.DataLoader.loadChartData('bar', fileName)
        .then(data => {
          if (data) {
            window.handleBarChart(data);
          } else {
            console.error('載入長條圖預設資料失敗 (經由統一資料載入器)');
            if (window.chartErrorHandler) {
              window.chartErrorHandler.showError('barChart', '載入長條圖預設資料失敗');
            }
          }
        })
        .catch(error => {
          console.error('載入長條圖預設資料時發生錯誤:', error);
          if (window.chartErrorHandler) {
            window.chartErrorHandler.showError('barChart', `載入長條圖預設資料失敗: ${error.message}`);
          }
        });
    } else {
      console.warn('找不到統一資料載入器，嘗試直接載入長條圖資料');
      
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
              console.log('使用JSON增強工具成功解析長條圖資料');
            } else {
              // 若沒有增強工具，使用標準解析
              data = JSON.parse(text);
            }
          } catch (e) {
            console.warn(`解析長條圖JSON時發生錯誤，嘗試修復: ${e.message}`);
            
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
          
          window.handleBarChart(data);
        })
        .catch(error => {
          console.error('直接載入長條圖資料時發生錯誤:', error);
          if (window.chartErrorHandler) {
            window.chartErrorHandler.showError('barChart', `載入長條圖預設資料失敗: ${error.message}`);
          }
        });
    }
  };
  
  // 提供長條圖範例資料
  window.getBarChartExamples = function() {
    return {
      basic: {
        chart: {
          type: 'bar',
          height: 350
        },
        plotOptions: {
          bar: {
            horizontal: false,
            columnWidth: '55%',
            endingShape: 'rounded'
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
        series: [{
          name: '淨利',
          data: [44, 55, 57, 56, 61, 58, 63, 60, 66]
        }, {
          name: '營收',
          data: [76, 85, 101, 98, 87, 105, 91, 114, 94]
        }],
        xaxis: {
          categories: ['Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct']
        },
        yaxis: {
          title: {
            text: '$ (thousands)'
          }
        },
        fill: {
          opacity: 1
        },
        tooltip: {
          y: {
            formatter: function(val) {
              return "$ " + val + " thousands"
            }
          }
        }
      }
    };
  };
})();
