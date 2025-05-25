/**
 * 散點圖專用處理函數
 * 解決散點圖渲染問題
 */

(function() {
  console.log('散點圖專用處理函數已啟動');
  
  // 全局保存散點圖實例
  window.scatterChartInstances = {};
  
  // 在頁面載入完成後執行
  document.addEventListener('DOMContentLoaded', function() {
    console.log('檢查是否需要初始化散點圖');
    
    // 檢查頁面是否有散點圖容器
    const scatterChartContainer = document.getElementById('scatterChart');
    if (scatterChartContainer) {
      console.log('檢測到散點圖容器，準備初始化');
      window.initScatterChart();
    }
  });
  
  // 處理散點圖渲染
  window.handleScatterChart = function(data) {
    console.log('開始處理散點圖渲染', data);
    
    // 檢查圖表容器
    const chartContainer = document.getElementById('scatterChart');
    if (!chartContainer) {
      console.error('找不到散點圖容器元素 #scatterChart');
      if (window.chartErrorHandler) {
        window.chartErrorHandler.showError('scatterChart', '找不到散點圖容器');
      }
      return false;
    }
    
    // 清除現有的圖表實例
    if (window.ApexCharts) {
      try {
        const existingChart = ApexCharts.getChartByID('scatterChart') || window.scatterChartInstances['scatterChart'];
        if (existingChart && typeof existingChart.destroy === 'function') {
          console.log('清除既有散點圖實例');
          existingChart.destroy();
        }
      } catch (e) {
        console.warn('清除散點圖時發生錯誤:', e);
      }
    }
    
    // 確保資料結構正確
    if (!data) {
      console.error('散點圖資料無效');
      if (window.chartErrorHandler) {
        window.chartErrorHandler.showError('scatterChart', '散點圖資料無效');
      }
      return false;
    }
    
    // 確保圖表類型設置為scatter
    if (!data.chart) data.chart = {};
    data.chart.type = 'scatter';
    
    // 確保有基本設定
    if (!data.xaxis || !data.xaxis.type) {
      if (!data.xaxis) data.xaxis = {};
      data.xaxis.type = 'numeric';
    }
    
    // 確保數據存在
    if (!data.series || !Array.isArray(data.series) || data.series.length === 0) {
      console.warn('散點圖缺少系列資料，設置預設值');
      data.series = [
        {
          name: "樣本 A",
          data: generateRandomScatterData(20)
        },
        {
          name: "樣本 B",
          data: generateRandomScatterData(20)
        }
      ];
    }
    
    // 格式轉換處理
    if (data.tooltip && data.tooltip.y && typeof data.tooltip.y.formatter === 'string') {
      try {
        data.tooltip.y.formatter = new Function('val', 'return ' + data.tooltip.y.formatter.substring(data.tooltip.y.formatter.indexOf('{') + 1, data.tooltip.y.formatter.lastIndexOf('}')));
        console.log('成功將散點圖 tooltip formatter 字串轉換為函數');
      } catch (e) {
        console.error('轉換散點圖 tooltip formatter 字串為函數失敗:', e);
        delete data.tooltip.y.formatter;
      }
    }
    
    try {
      console.log('初始化散點圖', data);
      const chart = new ApexCharts(chartContainer, data);
      window.scatterChartInstances['scatterChart'] = chart;
      chart.render();
      console.log('散點圖渲染完成');
      return true;
    } catch (error) {
      console.error('渲染散點圖時發生錯誤:', error);
      
      if (window.chartErrorHandler) {
        window.chartErrorHandler.showError('scatterChart', `無法渲染散點圖: ${error.message}`);
        
        // 嘗試使用替代數據源
        const alternativeFiles = [
          'apexcharts_scatter_sample.json',
          'apexcharts_scatter_air_quality.json',
          'apexcharts_scatter_risk_return.json'
        ];
        
        window.chartErrorHandler.retryLoadData('scatter', alternativeFiles, 'scatterChart', window.handleScatterChart);
      } else {
        chartContainer.innerHTML = `
          <div class="flex flex-col items-center justify-center h-full">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-error mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <p class="text-base text-error font-medium">渲染散點圖失敗: ${error.message}</p>
            <button class="btn btn-sm btn-outline btn-error mt-4" onclick="location.reload()">重新整理頁面</button>
          </div>
        `;
      }
      return false;
    }
  };
  
  // 初始化散點圖
  window.initScatterChart = function() {
    console.log('初始化散點圖...');
    
    // 如果有預設配置則載入
    window.loadScatterData();
  };
  
  // 載入散點圖資料
  window.loadScatterData = function(dataType = 'default') {
    console.log(`載入散點圖資料 (類型: ${dataType})`);
    
    let fileName;
    switch (dataType.toLowerCase()) {
      case 'metrics':
        fileName = 'apexcharts_scatter_metrics.json';
        break;
      case 'data':
        fileName = 'apexcharts_scatter_data.json';
        break;
      case 'default':
      default:
        fileName = 'apexcharts_scatter_sample.json'; // 改用實際存在的檔案
    }
    
    // 檢查是否由統一資料載入器處理
    if (window.DataLoader && typeof window.DataLoader.loadChartData === 'function') {
      window.DataLoader.loadChartData('scatter', fileName)
        .then(data => {
          if (data) {
            window.handleScatterChart(data);
          } else {
            console.error('載入散點圖預設資料失敗 (經由統一資料載入器)');
            if (window.chartErrorHandler) {
              window.chartErrorHandler.showError('scatterChart', '載入散點圖預設資料失敗');
            }
          }
        })
        .catch(error => {
          console.error('載入散點圖預設資料時發生錯誤:', error);
          if (window.chartErrorHandler) {
            window.chartErrorHandler.showError('scatterChart', `載入散點圖預設資料失敗: ${error.message}`);
          }
        });
    } else {
      console.warn('找不到統一資料載入器，嘗試直接載入散點圖資料');
      
      // 直接載入資料的備用方法
      fetch(`assets/examples/${fileName}`)
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
              console.log('使用JSON增強工具成功解析散點圖資料');
            } else {
              // 若沒有增強工具，使用標準解析
              data = JSON.parse(text);
            }
          } catch (e) {
            console.warn(`解析散點圖JSON時發生錯誤，嘗試修復: ${e.message}`);
            
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
          
          window.handleScatterChart(data);
        })
        .catch(error => {
          console.error('直接載入散點圖資料時發生錯誤:', error);
          if (window.chartErrorHandler) {
            window.chartErrorHandler.showError('scatterChart', `載入散點圖預設資料失敗: ${error.message}`);
          }
        });
    }
  };
  
  // 生成隨機散點數據 (用於示例或備用數據)
  function generateRandomScatterData(count = 10) {
    const result = [];
    for (let i = 0; i < count; i++) {
      result.push([
        Math.floor(Math.random() * 100),
        Math.floor(Math.random() * 100)
      ]);
    }
    return result;
  }
  
  // 提供散點圖範例資料
  window.getScatterChartExamples = function() {
    return {
      basic: {
        chart: {
          type: 'scatter',
          height: 350,
          zoom: {
            enabled: true,
            type: 'xy'
          }
        },
        series: [{
          name: "樣本 A",
          data: [
            [16.4, 5.4], [21.7, 2], [25.4, 3], [19, 2], [10.9, 1], [13.6, 3.2], [10.9, 7.4], [10.9, 0], [10.9, 8.2], [16.4, 0], [16.4, 1.8], [13.6, 0.3], [13.6, 0], [29.9, 0], [27.1, 2.3], [16.4, 0], [13.6, 3.7], [10.9, 5.2], [16.4, 6.5], [10.9, 0], [24.5, 7.1], [10.9, 0], [8.1, 4.7], [19, 0], [21.7, 1.8], [27.1, 0], [24.5, 0], [27.1, 0], [29.9, 1.5], [27.1, 0.8], [22.1, 2]
          ]
        }, {
          name: "樣本 B",
          data: [
            [6.4, 13.4], [1.7, 11], [5.4, 8], [9, 17], [1.9, 4], [3.6, 12.2], [1.9, 14.4], [1.9, 9], [1.9, 13.2], [1.4, 7], [6.4, 8.8], [3.6, 4.3], [1.6, 10], [9.9, 2], [7.1, 15], [1.4, 0], [3.6, 13.7], [1.9, 15.2], [6.4, 16.5], [0.9, 10], [4.5, 17.1], [10.9, 10], [0.1, 14.7], [9, 10], [12.7, 11.8], [2.1, 10], [2.5, 10], [27.1, 10], [2.9, 11.5], [7.1, 10.8], [2.1, 12]
          ]
        }],
        xaxis: {
          type: 'numeric',
          tickAmount: 10
        },
        yaxis: {
          tickAmount: 7
        }
      }
    };
  };
})();
