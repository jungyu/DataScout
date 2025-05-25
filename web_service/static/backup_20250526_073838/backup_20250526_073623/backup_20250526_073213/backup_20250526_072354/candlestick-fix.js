/**
 * 蠟燭圖專用修復腳本
 * 解決「蠟燭圖顯示3個範例但無法渲染」的問題
 */

(function() {
  console.log('蠟燭圖修復腳本已啟動');
  
  // 全局保存蠟燭圖實例
  window.candlestickChartInstances = {};
  
  // 在頁面載入完成後執行
  document.addEventListener('DOMContentLoaded', function() {
    // 檢查是否在蠟燭圖頁面 (index.html)
    if (window.location.pathname.toLowerCase().endsWith('index.html') || window.location.pathname === '/') {
      console.log('檢測到蠟燭圖頁面，啟用蠟燭圖修復機制');
      
      // 監聽組件載入完成事件
      document.addEventListener('component-loaded', function(e) {
        if (e.detail && e.detail.componentPath && e.detail.componentPath.includes('CandlestickContent.html')) {
          console.log('蠟燭圖組件已載入，初始化修復');
          setTimeout(fixCandlestickChart, 500);
        }
      });
    }
  });
  
  // 特別處理蠟燭圖渲染
  window.handleCandlestickChart = function(data) {
    console.log('開始特殊處理蠟燭圖的渲染', data);
    
    // 檢查圖表容器
    const chartContainer = document.getElementById('candlestickChart');
    if (!chartContainer) {
      console.error('找不到蠟燭圖容器元素 #candlestickChart');
      if (window.showNotification) {
        window.showNotification('找不到蠟燭圖容器，無法載入資料', 'error');
      }
      return;
    }
    
    // 清除現有的圖表實例
    if (window.ApexCharts) {
      const existingChart = window.candlestickChartInstances['candlestickChart'];
      if (existingChart && typeof existingChart.destroy === 'function') {
        console.log('清除既有蠟燭圖實例');
        existingChart.destroy();
        delete window.candlestickChartInstances['candlestickChart'];
      }
    }
    
    // 確保資料結構正確
    if (!data) {
      console.error('蠟燭圖資料無效');
      if (window.showNotification) {
        window.showNotification('蠟燭圖資料格式無效', 'error');
      }
      return;
    }
    
    // 確保圖表類型設置為candlestick
    if (!data.chart) data.chart = {};
    data.chart.type = 'candlestick';
    
    // 確保有正確的時間格式轉換
    if (data.xaxis && data.xaxis.type === 'datetime') {
      if (!data.tooltip) data.tooltip = {};
      if (!data.tooltip.x) data.tooltip.x = {};
      
      // 確保日期格式正確
      if (!data.tooltip.x.format) {
        data.tooltip.x.format = 'yyyy-MM-dd';
      }
    }
    
    // 確保蠟燭圖顏色設定存在
    if (!data.plotOptions) data.plotOptions = {};
    if (!data.plotOptions.candlestick) data.plotOptions.candlestick = {};
    if (!data.plotOptions.candlestick.colors) {
      data.plotOptions.candlestick.colors = {
        upward: '#00B746',
        downward: '#EF403C'
      };
    }
    
    try {
      console.log('初始化蠟燭圖', data);
      const chart = new ApexCharts(chartContainer, data);
      chart.render();
      
      // 保存實例以便後續操作
      window.candlestickChartInstances['candlestickChart'] = chart;
      
      console.log('蠟燭圖渲染完成');
      
      if (window.showNotification) {
        window.showNotification('蠟燭圖載入成功', 'success');
      }
    } catch (error) {
      console.error('渲染蠟燭圖時發生錯誤:', error);
      
      if (window.showNotification) {
        window.showNotification(`蠟燭圖渲染失敗: ${error.message}`, 'error');
      }
      
      // 顯示錯誤在圖表容器中
      chartContainer.innerHTML = `
        <div class="flex flex-col items-center justify-center h-full">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-error mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <p class="text-base text-error font-medium">渲染蠟燭圖失敗: ${error.message}</p>
          <button class="btn btn-sm btn-outline btn-error mt-4" onclick="location.reload()">重新整理頁面</button>
        </div>
      `;
    }
  };
  
  // 修復蠟燭圖渲染問題
  function fixCandlestickChart() {
    console.log('開始修復蠟燭圖渲染問題');
    
    // 重定向標準蠟燭圖渲染函數
    if (window.data-loader && typeof window.applyChartData === 'function') {
      const originalApplyChartData = window.applyChartData;
      window.applyChartData = function(data, chartType) {
        if (chartType === 'candlestick') {
          console.log('使用專用處理函數處理蠟燭圖');
          window.handleCandlestickChart(data);
          return;
        }
        
        // 其他圖表類型使用原函數處理
        originalApplyChartData(data, chartType);
      };
      console.log('已重定向圖表渲染函數');
    }
    
    // 獲取當前載入的範例資料元素
    const activeExample = document.querySelector('.chart-data-item.active');
    if (!activeExample) {
      console.log('找不到活躍的範例資料，嘗試載入預設範例');
      loadDefaultCandlestickExample();
      return;
    }
    
    // 獲取範例文件路徑
    const filePath = activeExample.dataset.file;
    if (!filePath) {
      console.error('範例資料缺少檔案路徑');
      return;
    }
    
    // 加載並渲染圖表
    console.log(`嘗試載入蠟燭圖資料: ${filePath}`);
    fetch(`/static/assets/examples/${filePath}`)
      .then(response => {
        if (!response.ok) throw new Error(`無法載入檔案 ${filePath}`);
        return response.json();
      })
      .then(data => {
        window.handleCandlestickChart(data);
      })
      .catch(error => {
        console.error('載入蠟燭圖資料時發生錯誤:', error);
        loadDefaultCandlestickExample();
      });
  }
  
  // 載入預設蠟燭圖範例
  function loadDefaultCandlestickExample() {
    console.log('載入預設蠟燭圖範例');
    fetch('/static/assets/examples/apexcharts_candlestick_bitcoin.json')
      .then(response => {
        if (!response.ok) throw new Error('無法載入預設蠟燭圖資料');
        return response.json();
      })
      .then(data => {
        window.handleCandlestickChart(data);
      })
      .catch(error => {
        console.error('載入預設蠟燭圖資料時發生錯誤:', error);
        const chartContainer = document.getElementById('candlestickChart');
        if (chartContainer) {
          chartContainer.innerHTML = `
            <div class="flex flex-col items-center justify-center h-full">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-error mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <p class="text-base text-error font-medium">無法載入蠟燭圖資料</p>
              <button class="btn btn-sm btn-outline btn-error mt-4" onclick="location.reload()">重新整理頁面</button>
            </div>
          `;
        }
      });
  }
})();
