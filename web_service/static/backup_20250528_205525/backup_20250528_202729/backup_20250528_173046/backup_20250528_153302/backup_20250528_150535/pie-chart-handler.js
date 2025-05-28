/**
 * 餅圖專用處理函數
 * 解決餅圖渲染問題
 */

(function() {
  console.log('餅圖專用處理函數已啟動');
  
  // 全局保存圖表實例 (與 area-chart-handler.js 一致)
  if (!window.chartInstances) {
    window.chartInstances = {};
  }
  
  // 處理餅圖渲染
  window.handlePieChart = function(data) {
    console.log('開始處理餅圖渲染', data);
    
    const chartContainerId = 'pieChart';
    const chartContainer = document.getElementById(chartContainerId);
    if (!chartContainer) {
      console.error(`找不到餅圖容器元素 #${chartContainerId}`);
      if (window.showNotification) {
        window.showNotification('找不到餅圖容器，無法載入資料', 'error');
      }
      return false;
    }
    
    // 清除現有的圖表實例
    if (window.ApexCharts) {
      try {
        const existingChart = ApexCharts.getChartByID(chartContainerId) || (window.chartInstances && window.chartInstances[chartContainerId]);
        if (existingChart && typeof existingChart.destroy === 'function') {
          console.log('清除既有餅圖實例');
          existingChart.destroy();
        }
        if (window.chartInstances && window.chartInstances[chartContainerId]) {
          delete window.chartInstances[chartContainerId];
        }
      } catch (e) {
        console.warn('清除餅圖時發生錯誤:', e);
      }
    }
    
    if (!data) {
      console.error('餅圖資料無效');
      if (window.showNotification) {
        window.showNotification('餅圖資料格式無效', 'error');
      }
      // Display error in container
      if (chartContainer) {
        chartContainer.innerHTML = `
          <div class="flex flex-col items-center justify-center h-full">
            <p class="text-base text-error font-medium">餅圖資料無效或未提供。</p>
          </div>
        `;
      }
      return false;
    }
    
    if (!data.chart) data.chart = {};
    data.chart.type = 'pie'; // 確保圖表類型為 pie
    
    if (!data.responsive) {
      data.responsive = [{
        breakpoint: 480,
        options: {
          chart: { width: 300 },
          legend: { position: 'bottom' }
        }
      }];
    }
     // 確保 series 和 labels 存在且為陣列
    if (!Array.isArray(data.series)) {
        console.warn('餅圖 series 資料不是陣列，將使用預設空陣列');
        data.series = [];
    }
    if (!Array.isArray(data.labels)) {
        console.warn('餅圖 labels 資料不是陣列，將使用預設空陣列');
        data.labels = [];
    }


    try {
      console.log('初始化餅圖', data);
      const chart = new ApexCharts(chartContainer, data);
      chart.render();
      console.log('餅圖渲染完成');
      
      window.chartInstances[chartContainerId] = chart; // Store instance
      
      if (window.showNotification) {
        window.showNotification('餅圖載入成功', 'success');
      }
      return true;
    } catch (error) {
      console.error('渲染餅圖時發生錯誤:', error);
      if (window.showNotification) {
        window.showNotification(`餅圖渲染失敗: ${error.message}`, 'error');
      }
      // Display error in container, similar to area-chart-handler
      chartContainer.innerHTML = `
        <div class="flex flex-col items-center justify-center h-full">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-error mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <p class="text-base text-error font-medium">渲染餅圖失敗: ${error.message}</p>
          <button class="btn btn-sm btn-outline btn-error mt-4" onclick="window.loadPieData && window.loadPieData()">重試載入資料</button>
        </div>
      `;
      return false;
    }
  };
  
  // 載入餅圖資料 (模仿 loadAreaData)
  window.loadPieData = function(dataType = 'default') {
    console.log(`載入餅圖資料 (類型: ${dataType})`);
    const chartContainerId = 'pieChart';
    
    let fileName;
    switch (dataType.toLowerCase()) {
      case 'teamcontribution':
      case 'default':
        fileName = 'apexcharts_pie_team.json';
        break;
      default:
        console.warn(`未知的餅圖資料類型: ${dataType}, 將使用預設資料。`);
        fileName = 'apexcharts_pie_team.json';
    }
    
    const dataUrl = `/static/assets/examples/${fileName}`;

    // 檢查是否由統一資料載入器處理
    if (window.DataLoader && typeof window.DataLoader.loadChartData === 'function') {
      window.DataLoader.loadChartData('pie', fileName)
        .then(data => {
          if (data) {
            window.handlePieChart(data);
          } else {
            console.error(`載入餅圖資料失敗 (經由統一資料載入器): ${fileName}`);
            if (window.chartErrorHandler) {
              window.chartErrorHandler.showError(chartContainerId, `無法透過 DataLoader 載入 ${fileName}`);
            }
            // Fallback to error display
            window.handlePieChart(null);
          }
        })
        .catch(error => {
          console.error(`載入餅圖資料時發生錯誤 (DataLoader): ${fileName}`, error);
          if (window.chartErrorHandler) {
            window.chartErrorHandler.showError(chartContainerId, `載入 ${fileName} 失敗: ${error.message}`);
          }
           window.handlePieChart(null);
        });
    } else {
      console.warn('找不到統一資料載入器，嘗試直接載入餅圖資料');
      fetch(dataUrl)
        .then(response => {
          if (!response.ok) throw new Error(`無法載入檔案 ${fileName} (狀態碼: ${response.status})`);
          return response.text();
        })
        .then(text => {
          let data;
          try {
            data = JSON.parse(text);
          } catch (e) {
            console.warn(`解析餅圖JSON (${fileName}) 時發生錯誤，嘗試修復: ${e.message}`);
            // Attempt to fix JSON (basic fixes, more advanced might be in processJsonFunctions or a dedicated parser)
            const processedText = text.replace(/\/\/.*$/gm, '').trim(); // Remove comments
            try {
                data = JSON.parse(processedText);
            } catch (e2) {
                console.error(`即使移除註釋也無法解析JSON (${fileName}): ${e2.message}`);
                throw e2; // Rethrow to be caught by outer catch
            }
          }
          
          if (data && window.processJsonFunctions) {
            data = window.processJsonFunctions(data);
            console.log(`餅圖資料 (${fileName}) 已透過 processJsonFunctions 處理`);
          }
          
          window.handlePieChart(data);
        })
        .catch(error => {
          console.error(`直接載入餅圖資料 (${fileName}) 時發生錯誤:`, error);
          if (window.chartErrorHandler) {
            window.chartErrorHandler.showError(chartContainerId, `載入餅圖資料 ${fileName} 失敗: ${error.message}`);
          }
          // Fallback to default data or error display
          const defaultPieData = {
            series: [44, 55, 13, 43, 22],
            chart: { type: 'pie', height: 350 },
            labels: ['產品A', '產品B', '產品C', '產品D', '產品E'],
            title: { text: '預設餅圖資料', align: 'center' },
            responsive: [{ breakpoint: 480, options: { chart: { width: 300 }, legend: { position: 'bottom' }}}]
          };
          console.log('由於載入失敗，使用預設餅圖資料');
          window.handlePieChart(defaultPieData);
        });
    }
  };

  // 初始化餅圖的函數
  window.initPieChart = function(externalData) {
    console.log('初始化餅圖函數已被調用');
    const chartContainer = document.getElementById('pieChart');
    if (!chartContainer) {
      console.warn('找不到餅圖容器 #pieChart，延遲初始化或等待 component-loaded 事件');
      return; 
    }
    
    if (externalData) {
      console.log('使用外部數據初始化餅圖');
      // Ensure processJsonFunctions is called for external data if it contains function strings
      if (window.processJsonFunctions) {
        externalData = window.processJsonFunctions(externalData);
      }
      // 使用修復版本處理餅圖
      if (window.handlePieChartFixed) {
        return window.handlePieChartFixed(externalData);
      } else {
        return window.handlePieChart(externalData);
      }
    }
    
    // 從預設路徑載入資料
    window.loadPieData('default'); 
  };

  // 監聽DOMContentLoaded和component-loaded事件
  function pieChartSetup() {
    if (document.getElementById('pieChart')) {
        console.log('餅圖容器已存在於DOM，嘗試初始化餅圖。');
        window.initPieChart();
    } else {
        console.log('餅圖容器不存在於DOM，等待 component-loaded 事件。');
    }
  }

  // 確保在 pie.html 或相關頁面執行
  if (window.location.pathname.toLowerCase().includes('pie.html') || 
      document.querySelector('[data-chart-type="pie"]')) { // More generic check
    
    document.addEventListener('DOMContentLoaded', pieChartSetup);

    document.addEventListener('component-loaded', function(e) {
      if (e.detail && e.detail.id === 'PieChartContent' && document.getElementById('pieChart')) {
        console.log('PieChartContent 組件已載入，初始化餅圖。');
        window.initPieChart();
      } else if (e.detail && e.detail.containerId === 'pieChart') {
        console.log('事件指示餅圖容器已載入，初始化餅圖。');
        window.initPieChart();
      }
    });
  }

})();

// 保留 getPieChartExamples 以便其他可能的用途 (例如 UI 選擇器)
window.getPieChartExamples = function() {
  return [
    { name: '團隊貢獻度', file: 'apexcharts_pie_team.json', dataType: 'teamcontribution' }
  ];
};
