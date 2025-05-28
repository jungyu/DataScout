/**
 * 熱力圖專用處理函數
 * 解決熱力圖渲染問題
 */

(function() {
  console.log('熱力圖專用處理函數已啟動');
  
  // 全局保存熱力圖實例
  window.heatmapChartInstances = {};
  
  // 在頁面載入完成後執行
  document.addEventListener('DOMContentLoaded', function() {
    console.log('檢查是否需要初始化熱力圖');
    
    // 檢查頁面是否有熱力圖容器
    const heatmapChartContainer = document.getElementById('heatmapChart');
    if (heatmapChartContainer) {
      console.log('檢測到熱力圖容器，準備初始化');
      window.initHeatmapChart();
    }
  });
  
  // 處理熱力圖渲染
  window.handleHeatmapChart = function(data) {
    console.log('開始處理熱力圖渲染', data);
    
    // 檢查圖表容器
    const chartContainer = document.getElementById('heatmapChart');
    if (!chartContainer) {
      console.error('找不到熱力圖容器元素 #heatmapChart');
      if (window.chartErrorHandler) {
        window.chartErrorHandler.showError('heatmapChart', '找不到熱力圖容器');
      }
      return false;
    }
    
    // 清除現有的圖表實例
    if (window.ApexCharts) {
      try {
        const existingChart = ApexCharts.getChartByID('heatmapChart') || window.heatmapChartInstances['heatmapChart'];
        if (existingChart && typeof existingChart.destroy === 'function') {
          console.log('清除既有熱力圖實例');
          existingChart.destroy();
        }
      } catch (e) {
        console.warn('清除熱力圖時發生錯誤:', e);
      }
    }
    
    // 確保資料結構正確
    if (!data) {
      console.error('熱力圖資料無效');
      if (window.chartErrorHandler) {
        window.chartErrorHandler.showError('heatmapChart', '熱力圖資料無效');
      }
      return false;
    }
    
    // 確保圖表類型設置為heatmap
    if (!data.chart) data.chart = {};
    data.chart.type = 'heatmap';
    
    // 確保系列資料
    if (!data.series || !Array.isArray(data.series) || data.series.length === 0) {
      console.warn('熱力圖缺少系列資料，設置預設值');
      data.series = generateDefaultHeatmapData();
    }
    
    // 格式轉換處理
    if (data.tooltip && data.tooltip.y && typeof data.tooltip.y.formatter === 'string') {
      try {
        data.tooltip.y.formatter = new Function('val', 'return ' + data.tooltip.y.formatter.substring(data.tooltip.y.formatter.indexOf('{') + 1, data.tooltip.y.formatter.lastIndexOf('}')));
        console.log('成功將熱力圖 tooltip formatter 字串轉換為函數');
      } catch (e) {
        console.error('轉換熱力圖 tooltip formatter 字串為函數失敗:', e);
        delete data.tooltip.y.formatter;
      }
    }
    
    try {
      console.log('初始化熱力圖', data);
      const chart = new ApexCharts(chartContainer, data);
      window.heatmapChartInstances['heatmapChart'] = chart;
      chart.render();
      console.log('熱力圖渲染完成');
      return true;
    } catch (error) {
      console.error('渲染熱力圖時發生錯誤:', error);
      
      if (window.chartErrorHandler) {
        window.chartErrorHandler.showError('heatmapChart', `無法渲染熱力圖: ${error.message}`);
        
        // 嘗試使用替代數據源
        const alternativeFiles = [
          'apexcharts_heatmap_store_traffic.json',
          'apexcharts_heatmap_humidity.json',
          'apexcharts_heatmap_temperature.json'
        ];
        
        window.chartErrorHandler.retryLoadData('heatmap', alternativeFiles, 'heatmapChart', window.handleHeatmapChart);
      } else {
        chartContainer.innerHTML = `
          <div class="flex flex-col items-center justify-center h-full">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-error mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <p class="text-base text-error font-medium">渲染熱力圖失敗: ${error.message}</p>
            <button class="btn btn-sm btn-outline btn-error mt-4" onclick="location.reload()">重新整理頁面</button>
          </div>
        `;
      }
      return false;
    }
  };
  
  // 初始化熱力圖
  window.initHeatmapChart = function() {
    console.log('初始化熱力圖...');
    
    // 如果有預設配置則載入
    window.loadHeatmapData();
  };
  
  // 載入熱力圖資料
  window.loadHeatmapData = function(dataType = 'default') {
    console.log(`載入熱力圖資料 (類型: ${dataType})`);
    
    let fileName;
    switch (dataType.toLowerCase()) {
      case 'temperature':
        fileName = 'apexcharts_heatmap_temperature.json';
        break;
      case 'humidity':
        fileName = 'apexcharts_heatmap_humidity.json';
        break;
      case 'default':
      default:
        fileName = 'apexcharts_heatmap_store_traffic.json';
    }
    
    // 檢查是否由統一資料載入器處理
    if (window.DataLoader && typeof window.DataLoader.loadChartData === 'function') {
      window.DataLoader.loadChartData('heatmap', fileName)
        .then(data => {
          if (data) {
            window.handleHeatmapChart(data);
          } else {
            console.error('載入熱力圖預設資料失敗 (經由統一資料載入器)');
            if (window.chartErrorHandler) {
              window.chartErrorHandler.showError('heatmapChart', '載入熱力圖預設資料失敗');
            }
          }
        })
        .catch(error => {
          console.error('載入熱力圖預設資料時發生錯誤:', error);
          if (window.chartErrorHandler) {
            window.chartErrorHandler.showError('heatmapChart', `載入熱力圖預設資料失敗: ${error.message}`);
          }
        });
    } else {
      console.warn('找不到統一資料載入器，嘗試直接載入熱力圖資料');
      
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
              console.log('使用JSON增強工具成功解析熱圖資料');
            } else {
              // 若沒有增強工具，使用標準解析
              data = JSON.parse(text);
            }
          } catch (e) {
            console.warn(`解析熱圖JSON時發生錯誤，嘗試修復: ${e.message}`);
            
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
          
          window.handleHeatmapChart(data);
        })
        .catch(error => {
          console.error('直接載入熱力圖資料時發生錯誤:', error);
          if (window.chartErrorHandler) {
            window.chartErrorHandler.showError('heatmapChart', `載入熱力圖預設資料失敗: ${error.message}`);
          }
        });
    }
  };

  // 生成預設熱力圖資料
  function generateDefaultHeatmapData() {
    const series = [];
    const categories = ['00:00', '01:00', '02:00', '03:00', '04:00', '05:00', '06:00', '07:00', '08:00', '09:00', '10:00', '11:00', '12:00'];
    
    for (let i = 0; i < 8; i++) {
      const data = [];
      for (let j = 0; j < categories.length; j++) {
        data.push({
          x: categories[j],
          y: Math.floor(Math.random() * 100) + 10
        });
      }
      series.push({
        name: `項目 ${i+1}`,
        data: data
      });
    }
    
    return series;
  }
  
  // 提供熱力圖範例資料
  window.getHeatmapChartExamples = function() {
    return {
      basic: {
        chart: {
          type: 'heatmap',
          height: 350,
          toolbar: {
            show: false
          }
        },
        dataLabels: {
          enabled: false
        },
        colors: ["#3B82F6"],
        series: generateDefaultHeatmapData(),
        title: {
          text: '基本熱力圖'
        },
        tooltip: {
          y: {
            formatter: function(val) {
              return val + " 單位";
            }
          }
        }
      },
      colorRange: {
        chart: {
          type: 'heatmap',
          height: 350,
          toolbar: {
            show: false
          }
        },
        dataLabels: {
          enabled: false
        },
        colors: ["#F3B415", "#F27036", "#663F59", "#6A6E94", "#4E88B4", "#00A7C6", "#18D8D8"],
        series: generateDefaultHeatmapData(),
        title: {
          text: '多色熱力圖'
        },
        tooltip: {
          y: {
            formatter: function(val) {
              return val + " 單位";
            }
          }
        }
      }
    };
  };
})();
