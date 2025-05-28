/**
 * 蠟燭圖專用處理函數
 * 解決蠟燭圖渲染問題
 */

(function() {
  console.log('蠟燭圖專用處理函數已啟動');
  
  // 全局保存圖表實例
  if (!window.chartInstances) {
    window.chartInstances = {};
  }
  
  // 處理蠟燭圖渲染
  window.handleCandlestickChart = function(data) {
    console.log('開始處理蠟燭圖渲染', data);
    
    const chartContainerId = 'candlestickChart';
    const chartContainer = document.getElementById(chartContainerId);
    if (!chartContainer) {
      console.error(`找不到蠟燭圖容器元素 #${chartContainerId}`);
      if (window.showNotification) {
        window.showNotification('找不到蠟燭圖容器，無法載入資料', 'error');
      }
      return false;
    }
    
    // 清除現有的圖表實例
    if (window.ApexCharts) {
      try {
        const existingChart = ApexCharts.getChartByID(chartContainerId) || (window.chartInstances && window.chartInstances[chartContainerId]);
        if (existingChart && typeof existingChart.destroy === 'function') {
          console.log('清除既有蠟燭圖實例');
          existingChart.destroy();
        }
        if (window.chartInstances && window.chartInstances[chartContainerId]) {
          delete window.chartInstances[chartContainerId];
        }
      } catch (e) {
        console.warn('清除蠟燭圖時發生錯誤:', e);
      }
    }
    
    if (!data) {
      console.error('蠟燭圖資料無效');
      if (window.showNotification) {
        window.showNotification('蠟燭圖資料格式無效', 'error');
      }
      // Display error in container
      if (chartContainer) {
        chartContainer.innerHTML = `
          <div class="flex flex-col items-center justify-center h-full">
            <p class="text-base text-error font-medium">蠟燭圖資料無效或未提供。</p>
          </div>
        `;
      }
      return false;
    }
    
    // 確保圖表類型為蠟燭圖
    if (!data.chart) data.chart = {};
    data.chart.type = 'candlestick';
    
    // 設置默認的響應式配置
    if (!data.responsive) {
      data.responsive = [{
        breakpoint: 480,
        options: {
          chart: { width: '100%' },
          legend: { position: 'bottom' }
        }
      }];
    }
    
    // 確保 series 存在且為陣列
    if (!Array.isArray(data.series)) {
      console.warn('蠟燭圖 series 資料不是陣列，將使用預設空陣列');
      data.series = [];
    }
    
    // 蠟燭圖特有的數據驗證
    if (data.series.length > 0) {
      data.series.forEach((series, index) => {
        if (!Array.isArray(series.data)) {
          console.warn(`蠟燭圖 series[${index}] 的 data 不是陣列，將使用空陣列`);
          series.data = [];
        }
        
        // 驗證蠟燭圖數據格式 (每個數據點應該有 x 和 y 屬性，其中 y 是 [open, high, low, close] 陣列)
        series.data.forEach((dataPoint, dataIndex) => {
          if (!dataPoint.x || !Array.isArray(dataPoint.y) || dataPoint.y.length !== 4) {
            console.warn(`蠟燭圖數據點 series[${index}].data[${dataIndex}] 格式不正確，需要 x 和 y=[open,high,low,close] 格式`);
          }
        });
      });
    }
    
    try {
      console.log('初始化蠟燭圖', data);
      const chart = new ApexCharts(chartContainer, data);
      chart.render();
      console.log('蠟燭圖渲染完成');
      
      window.chartInstances[chartContainerId] = chart; // Store instance
      
      if (window.showNotification) {
        window.showNotification('蠟燭圖載入成功', 'success');
      }
      return true;
    } catch (error) {
      console.error('渲染蠟燭圖時發生錯誤:', error);
      if (window.showNotification) {
        window.showNotification(`蠟燭圖渲染失敗: ${error.message}`, 'error');
      }
      // Display error in container
      chartContainer.innerHTML = `
        <div class="flex flex-col items-center justify-center h-full">
          <p class="text-base text-error font-medium">蠟燭圖渲染失敗</p>
          <p class="text-sm text-error">${error.message}</p>
        </div>
      `;
      return false;
    }
  };
  
  // 註冊全局圖表清理函數
  if (!window.cleanupChartInstances) {
    window.cleanupChartInstances = function(chartId) {
      if (chartId && window.chartInstances && window.chartInstances[chartId]) {
        try {
          window.chartInstances[chartId].destroy();
          delete window.chartInstances[chartId];
          console.log(`清理圖表實例: ${chartId}`);
        } catch (e) {
          console.warn(`清理圖表實例 ${chartId} 時發生錯誤:`, e);
        }
      } else if (!chartId) {
        // 清理所有實例
        for (const id in window.chartInstances) {
          try {
            window.chartInstances[id].destroy();
            delete window.chartInstances[id];
            console.log(`清理圖表實例: ${id}`);
          } catch (e) {
            console.warn(`清理圖表實例 ${id} 時發生錯誤:`, e);
          }
        }
      }
    };
  }
  
  // 註冊圖表實例
  if (!window.registerChartInstance) {
    window.registerChartInstance = function(chartId, chartInstance) {
      if (chartId && chartInstance) {
        window.chartInstances[chartId] = chartInstance;
        console.log(`註冊圖表實例: ${chartId}`);
      }
    };
  }
  
  // 當頁面準備好時，嘗試連接 data-loader
  document.addEventListener('DOMContentLoaded', function() {
    console.log('蠟燭圖處理器：DOM 已載入');
    
    // 如果 data-loader 已經設置了圖表類型處理器，則註冊此處理器
    if (window.setChartTypeHandler) {
      window.setChartTypeHandler('candlestick', window.handleCandlestickChart);
      console.log('已註冊蠟燭圖類型處理器');
    }
    
    // 檢查是否需要立即初始化蠟燭圖
    const candlestickContainer = document.getElementById('candlestickChart');
    if (candlestickContainer && candlestickContainer.getAttribute('data-auto-init') === 'true') {
      console.log('檢測到需要自動初始化蠟燭圖');
      // 可以在這裡添加自動初始化邏輯
    }
  });
  
  console.log('蠟燭圖專用處理函數初始化完成');
})();
