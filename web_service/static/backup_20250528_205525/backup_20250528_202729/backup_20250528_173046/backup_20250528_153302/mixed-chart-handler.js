/**
 * 混合圖表專用處理函數
 * 解決混合型圖表渲染問題
 */

(function() {
  console.log('混合圖表專用處理函數已啟動');
  
  // 全局保存混合圖表實例
  window.mixedChartInstances = {};
  
  // 在頁面載入完成後執行
  document.addEventListener('DOMContentLoaded', function() {
    console.log('檢查是否需要初始化混合圖表');
    
    // 檢查頁面是否有混合圖表容器
    const mixedChartContainer = document.getElementById('mixedChart');
    if (mixedChartContainer) {
      console.log('檢測到混合圖表容器，準備初始化');
      window.initMixedChart();
    }
  });
  
  // 處理混合圖表渲染
  window.handleMixedChart = function(data) {
    console.log('開始處理混合圖表渲染', data);
    
    // 檢查圖表容器
    const chartContainer = document.getElementById('mixedChart');
    if (!chartContainer) {
      console.error('找不到混合圖表容器元素 #mixedChart');
      if (window.chartErrorHandler) {
        window.chartErrorHandler.showError('mixedChart', '找不到混合圖表容器');
      }
      return false;
    }
    
    // 清除現有的圖表實例
    if (window.ApexCharts) {
      try {
        const existingChart = ApexCharts.getChartByID('mixedChart') || window.mixedChartInstances['mixedChart'];
        if (existingChart && typeof existingChart.destroy === 'function') {
          console.log('清除既有混合圖表實例');
          existingChart.destroy();
        }
      } catch (e) {
        console.warn('清除混合圖表時發生錯誤:', e);
      }
    }
    
    // 確保資料結構正確
    if (!data) {
      console.error('混合圖表資料無效');
      if (window.chartErrorHandler) {
        window.chartErrorHandler.showError('mixedChart', '混合圖表資料無效');
      }
      return false;
    }
    
    // 確保圖表基本設置
    if (!data.chart) data.chart = {};
    
    // 混合圖表不設置單一類型，而是在系列中設置
    // data.chart.type = 'mixed'; 
    
    // 確保系列資料包含類型
    if (data.series && Array.isArray(data.series)) {
      let hasError = false;
      
      data.series.forEach((series, index) => {
        if (!series.type) {
          console.warn(`混合圖表第 ${index+1} 系列缺少類型設定，預設設為 'column'`);
          series.type = 'column';
        }
      });
      
      if (hasError) {
        console.error('混合圖表存在無效的系列設定');
        if (window.chartErrorHandler) {
          window.chartErrorHandler.showError('mixedChart', '混合圖表存在無效的系列設定');
        }
        return false;
      }
    } else {
      console.error('混合圖表缺少系列資料');
      if (window.chartErrorHandler) {
        window.chartErrorHandler.showError('mixedChart', '混合圖表缺少系列資料');
      }
      return false;
    }
    
    // 格式轉換處理
    if (data.yaxis && Array.isArray(data.yaxis)) {
      data.yaxis.forEach((axis, index) => {
        if (axis && axis.labels && axis.labels.formatter && typeof axis.labels.formatter === 'string') {
          try {
            axis.labels.formatter = new Function('val', 'return ' + axis.labels.formatter.substring(axis.labels.formatter.indexOf('{') + 1, axis.labels.formatter.lastIndexOf('}')));
            console.log(`成功將混合圖表 yaxis[${index}] formatter 字串轉換為函數`);
          } catch (e) {
            console.error(`轉換混合圖表 yaxis[${index}] formatter 字串為函數失敗:`, e);
            delete axis.labels.formatter;
          }
        }
      });
    }
    
    if (data.tooltip && data.tooltip.y && Array.isArray(data.tooltip.y)) {
      data.tooltip.y.forEach((tooltip, index) => {
        if (tooltip && tooltip.formatter && typeof tooltip.formatter === 'string') {
          try {
            tooltip.formatter = new Function('val', 'return ' + tooltip.formatter.substring(tooltip.formatter.indexOf('{') + 1, tooltip.formatter.lastIndexOf('}')));
            console.log(`成功將混合圖表 tooltip.y[${index}] formatter 字串轉換為函數`);
          } catch (e) {
            console.error(`轉換混合圖表 tooltip.y[${index}] formatter 字串為函數失敗:`, e);
            delete tooltip.formatter;
          }
        }
      });
    } else if (data.tooltip && data.tooltip.y && data.tooltip.y.formatter && typeof data.tooltip.y.formatter === 'string') {
      try {
        data.tooltip.y.formatter = new Function('val', 'seriesIndex', 'return ' + data.tooltip.y.formatter.substring(data.tooltip.y.formatter.indexOf('{') + 1, data.tooltip.y.formatter.lastIndexOf('}')));
        console.log('成功將混合圖表 tooltip formatter 字串轉換為函數');
      } catch (e) {
        console.error('轉換混合圖表 tooltip formatter 字串為函數失敗:', e);
        delete data.tooltip.y.formatter;
      }
    }
    
    try {
      console.log('初始化混合圖表', data);
      const chart = new ApexCharts(chartContainer, data);
      window.mixedChartInstances['mixedChart'] = chart;
      chart.render();
      console.log('混合圖表渲染完成');
      return true;
    } catch (error) {
      console.error('渲染混合圖表時發生錯誤:', error);
      
      if (window.chartErrorHandler) {
        window.chartErrorHandler.showError('mixedChart', `無法渲染混合圖表: ${error.message}`);
        
        // 嘗試使用替代數據源
        const alternativeFiles = [
          'apexcharts_mixed_basic.json',
          'apexcharts_mixed_line_column.json',
          'apexcharts_mixed_line_area.json'
        ];
        
        window.chartErrorHandler.retryLoadData('mixed', alternativeFiles, 'mixedChart', window.handleMixedChart);
      } else {
        chartContainer.innerHTML = `
          <div class="flex flex-col items-center justify-center h-full">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-error mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <p class="text-base text-error font-medium">渲染混合圖表失敗: ${error.message}</p>
            <button class="btn btn-sm btn-outline btn-error mt-4" onclick="location.reload()">重新整理頁面</button>
          </div>
        `;
      }
      return false;
    }
  };
  
  // 初始化混合圖表
  window.initMixedChart = function() {
    console.log('初始化混合圖表...');
    
    // 如果有預設配置則載入
    window.loadMixedData();
  };
  
  // 載入混合圖表資料
  window.loadMixedData = function(dataType = 'default') {
    console.log(`載入混合圖表資料 (類型: ${dataType})`);
    
    let fileName;
    switch (dataType.toLowerCase()) {
      case 'line_column':
        fileName = 'apexcharts_mixed_line_column.json';
        break;
      case 'line_area':
        fileName = 'apexcharts_mixed_line_area.json';
        break;
      case 'default':
      default:
        fileName = 'apexcharts_mixed_basic.json';
    }
    
    // 檢查是否由統一資料載入器處理
    if (window.DataLoader && typeof window.DataLoader.loadChartData === 'function') {
      window.DataLoader.loadChartData('mixed', fileName)
        .then(data => {
          if (data) {
            window.handleMixedChart(data);
          } else {
            console.error('載入混合圖表預設資料失敗 (經由統一資料載入器)');
            if (window.chartErrorHandler) {
              window.chartErrorHandler.showError('mixedChart', '載入混合圖表預設資料失敗');
            }
          }
        })
        .catch(error => {
          console.error('載入混合圖表預設資料時發生錯誤:', error);
          if (window.chartErrorHandler) {
            window.chartErrorHandler.showError('mixedChart', `載入混合圖表預設資料失敗: ${error.message}`);
          }
        });
    } else {
      console.warn('找不到統一資料載入器，嘗試直接載入混合圖表資料');
      
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
              console.log('使用JSON增強工具成功解析混合圖資料');
            } else {
              // 若沒有增強工具，使用標準解析
              data = JSON.parse(text);
            }
          } catch (e) {
            console.warn(`解析混合圖JSON時發生錯誤，嘗試修復: ${e.message}`);
            
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
          
          window.handleMixedChart(data);
        })
        .catch(error => {
          console.error('直接載入混合圖表資料時發生錯誤:', error);
          if (window.chartErrorHandler) {
            window.chartErrorHandler.showError('mixedChart', `載入混合圖表預設資料失敗: ${error.message}`);
          }
        });
    }
  };
  
  // 提供混合圖表範例資料
  window.getMixedChartExamples = function() {
    return {
      lineColumn: {
        chart: {
          height: 350,
          toolbar: {
            show: true
          }
        },
        stroke: {
          width: [0, 4]
        },
        title: {
          text: '流量與轉換率'
        },
        series: [{
          name: '網站訪問量',
          type: 'column',
          data: [440, 505, 414, 671, 227, 413, 201, 352, 752, 320, 257, 160]
        }, {
          name: '轉換率',
          type: 'line',
          data: [23, 42, 35, 27, 43, 22, 17, 31, 22, 22, 12, 16]
        }],
        labels: ['01 Jan 2023', '02 Jan 2023', '03 Jan 2023', '04 Jan 2023', '05 Jan 2023', '06 Jan 2023', '07 Jan 2023', '08 Jan 2023', '09 Jan 2023', '10 Jan 2023', '11 Jan 2023', '12 Jan 2023'],
        xaxis: {
          type: 'datetime'
        },
        yaxis: [{
          title: {
            text: '網站訪問量'
          }
        }, {
          opposite: true,
          title: {
            text: '轉換率 (%)'
          }
        }]
      },
      lineArea: {
        chart: {
          height: 350,
          toolbar: {
            show: true
          }
        },
        stroke: {
          curve: 'smooth'
        },
        fill: {
          type: 'solid',
          opacity: [0.35, 1]
        },
        series: [{
          name: '團隊 A',
          type: 'area',
          data: [44, 55, 31, 47, 31, 43, 26, 41, 31, 47, 33]
        }, {
          name: '團隊 B',
          type: 'line',
          data: [55, 69, 45, 61, 43, 54, 37, 52, 44, 61, 43]
        }],
        labels: ['01/01/2023', '02/01/2023', '03/01/2023', '04/01/2023', '05/01/2023', '06/01/2023', '07/01/2023', '08/01/2023', '09/01/2023', '10/01/2023', '11/01/2023'],
        markers: {
          size: 0
        },
        yaxis: [{
          title: {
            text: '系列 A'
          },
        }, {
          opposite: true,
          title: {
            text: '系列 B'
          }
        }],
        tooltip: {
          shared: true,
          intersect: false,
          y: {
            formatter: function(y) {
              if (typeof y !== "undefined") {
                return y.toFixed(0) + " 點";
              }
              return y;
            }
          }
        }
      }
    };
  };
})();
