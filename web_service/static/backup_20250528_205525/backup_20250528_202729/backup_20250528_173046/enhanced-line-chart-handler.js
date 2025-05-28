/**
 * 增強版折線圖處理腳本
 * 解決「載入預設資料失敗」和「Failed to execute 'json' on 'Response'」錯誤
 */

(function() {
  console.log('增強版折線圖處理腳本已啟動');
  
  // 全局保存折線圖實例
  window.lineChartInstances = {};
  
  // 處理折線圖渲染
  window.handleLineChart = function(data) {
    console.log('開始處理折線圖的渲染', data);
    
    const chartElement = document.getElementById('lineChart');
    if (!chartElement) {
      console.error('找不到折線圖容器元素 #lineChart');
      if (window.showNotification) {
        window.showNotification('找不到折線圖容器，無法載入資料', 'error');
      }
      return;
    }
    
    // 清除現有的圖表實例
    if (window.ApexCharts && window.lineChartInstances && window.lineChartInstances['lineChart']) {
      try {
        const existingChart = window.lineChartInstances['lineChart'];
        if (existingChart && typeof existingChart.destroy === 'function') {
          existingChart.destroy();
        }
      } catch (e) {
        console.error('清除舊圖表時發生錯誤:', e);
      }
    }
    
    // 確保資料結構正確
    if (!data) {
      console.error('折線圖資料無效');
      if (window.chartErrorHandler) {
        window.chartErrorHandler.showError('lineChart', '折線圖資料無效');
      }
      return;
    }
    
    // 確保圖表類型設置為line
    if (!data.chart) data.chart = {};
    data.chart.type = 'line';
    
    // 添加 formatter 字串轉換邏輯
    if (data && data.yaxis && data.yaxis.labels && typeof data.yaxis.labels.formatter === 'string') {
      try {
        data.yaxis.labels.formatter = new Function('val', 'return ' + data.yaxis.labels.formatter.substring(data.yaxis.labels.formatter.indexOf('{') + 1, data.yaxis.labels.formatter.lastIndexOf('}')));
        console.log('成功將線圖 yaxis formatter 字串轉換為函數 (enhanced handler)');
      } catch (e) {
        console.error('轉換線圖 yaxis formatter 字串為函數失敗 (enhanced handler):', e);
        delete data.yaxis.labels.formatter;
      }
    }
    
    if (data && data.tooltip && data.tooltip.y && typeof data.tooltip.y.formatter === 'string') {
      try {
        data.tooltip.y.formatter = new Function('val', 'options', 'return ' + data.tooltip.y.formatter.substring(data.tooltip.y.formatter.indexOf('{') + 1, data.tooltip.y.formatter.lastIndexOf('}')));
        console.log('成功將線圖 tooltip formatter 字串轉換為函數 (enhanced handler)');
      } catch (e) {
        console.error('轉換線圖 tooltip formatter 字串為函數失敗 (enhanced handler):', e);
        delete data.tooltip.y.formatter;
      }
    }

    try {
      console.log('渲染折線圖', data);
      
      // 創建新圖表實例
      const chart = new ApexCharts(chartElement, data);
      chart.render();
      
      // 儲存實例以便後續操作
      window.lineChartInstances['lineChart'] = chart;
      
      console.log('折線圖渲染成功');
      
      if (window.showNotification) {
        window.showNotification('折線圖渲染成功', 'success');
      }
    } catch (error) {
      console.error('渲染折線圖時發生錯誤:', error);
      
      if (window.chartErrorHandler) {
        window.chartErrorHandler.showError('lineChart', `渲染折線圖失敗: ${error.message}`);
      } else {
        chartElement.innerHTML = `
          <div class="flex flex-col items-center justify-center h-full">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-error mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <p class="text-base text-error font-medium">渲染折線圖失敗: ${error.message}</p>
            <button class="btn btn-sm btn-outline btn-error mt-4" onclick="location.reload()">重新整理頁面</button>
          </div>
        `;
      }
    }
  };
  
  // 在頁面載入完成後執行
  document.addEventListener('DOMContentLoaded', function() {
    // 檢查是否在折線圖頁面
    if (window.location.pathname.toLowerCase().includes('line.html')) {
      console.log('檢測到折線圖頁面，啟動增強處理');
      
      // 監聽組件載入完成事件
      document.addEventListener('component-loaded', function(e) {
        if (e.detail && e.detail.componentPath && e.detail.componentPath.includes('LineChartContent.html')) {
          console.log('折線圖組件已載入，初始化增強處理');
          setTimeout(initLineChartHandler, 500);
        }
      });
    }
  });
  
  // 初始化折線圖處理
  function initLineChartHandler() {
    console.log('初始化折線圖增強處理');

    // 獲取當前載入的範例資料元素
    const activeExample = document.querySelector('.chart-data-item.active');
    if (!activeExample) {
      console.log('找不到活躍的範例資料，嘗試載入預設範例');
      loadDefaultLineExample();
      return;
    }
    
    // 獲取範例文件路徑
    const filePath = activeExample.dataset.file;
    if (!filePath) {
      console.error('範例資料缺少檔案路徑');
      loadDefaultLineExample();
      return;
    }
    
    // 加載並渲染圖表
    console.log(`嘗試載入折線圖資料: ${filePath}`);
    loadLineChartData(filePath);
  }
  
  // 加載並處理折線圖數據
  function loadLineChartData(fileName) {
    fetch(`/static/assets/examples/${fileName}`)
      .then(response => {
        if (!response.ok) throw new Error(`無法載入檔案 ${fileName}`);
        return response.text(); // 先以文本形式獲取
      })
      .then(text => {
        // 嘗試使用增強版JSON解析
        let data;
        
        try {
          // 首先使用原始方式嘗試解析
          data = JSON.parse(text);
        } catch (parseError) {
          console.warn('標準JSON解析失敗，嘗試修復:', parseError);
          
          // 嘗試使用修復工具處理
          if (window.chartErrorHandler) {
            data = window.chartErrorHandler.fixJsonFormatting(text);
          } else if (typeof handleFunctionStrings === 'function') {
            const processed = handleFunctionStrings(text);
            data = JSON.parse(processed);
          } else {
            throw new Error(`JSON解析失敗: ${parseError.message}`);
          }
        }
        
        if (!data) {
          throw new Error('無法解析JSON資料');
        }
        
        // 渲染折線圖
        window.handleLineChart(data);
      })
      .catch(error => {
        console.error('載入折線圖資料時發生錯誤:', error);
        loadDefaultLineExample();
      });
  }
  
  // 載入預設折線圖範例
  function loadDefaultLineExample() {
    if (window.chartErrorHandler) {
      // 使用通用錯誤處理工具載入多個備用文件
      const alternatives = [
        'apexcharts_line_sales.json',
        'apexcharts_line_weather.json',
        'apexcharts_line_interest_rate.json',
        'apexcharts_timeseries_line_unemployment.json'
      ];
      window.chartErrorHandler.retryLoadData('line', alternatives, 'lineChart', window.handleLineChart);
      return;
    }
    
    console.log('載入預設折線圖範例');
    
    // 嘗試依序載入備用文件
    const tryLoadFile = (index = 0) => {
      const files = [
        'apexcharts_line_sales.json',
        'apexcharts_line_weather.json',
        'apexcharts_line_interest_rate.json'
      ];
      
      if (index >= files.length) {
        const chartContainer = document.getElementById('lineChart');
        if (chartContainer) {
          chartContainer.innerHTML = `
            <div class="flex flex-col items-center justify-center h-full">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-error mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <p class="text-base text-error font-medium">無法載入任何折線圖資料</p>
              <button class="btn btn-sm btn-outline btn-error mt-4" onclick="location.reload()">重新整理頁面</button>
            </div>
          `;
        }
        return;
      }
      
      const fileName = files[index];
      
      fetch(`/static/assets/examples/${fileName}`)
        .then(response => {
          if (!response.ok) throw new Error(`無法載入檔案 ${fileName}`);
          return response.text(); // 先以文本形式獲取
        })
        .then(text => {
          // 嘗試使用增強版JSON解析
          let data;
          
          try {
            data = JSON.parse(text);
          } catch (parseError) {
            console.warn('嘗試修復JSON格式');
            if (typeof handleFunctionStrings === 'function') {
              const processed = handleFunctionStrings(text);
              data = JSON.parse(processed);
            } else {
              throw parseError;
            }
          }
          
          // 渲染折線圖
          window.handleLineChart(data);
        })
        .catch(error => {
          console.error(`載入備用文件 ${fileName} 失敗:`, error);
          tryLoadFile(index + 1);
        });
    };
    
    tryLoadFile();
  }
})();
