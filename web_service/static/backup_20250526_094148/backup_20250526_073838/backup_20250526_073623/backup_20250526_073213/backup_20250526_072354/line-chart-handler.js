/**
 * 折線圖特殊處理函數
 * 解決折線圖在動態載入時無法正確渲染的問題
 */

// 特別處理線圖渲染
window.handleLineChart = function(data) {
  console.log('開始特殊處理折線圖的渲染', data);
  
  // 檢查圖表容器
  const chartContainer = document.getElementById('lineChart');
  if (!chartContainer) {
    console.error('找不到折線圖容器元素 #lineChart');
    if (window.showNotification) {
      window.showNotification('找不到折線圖容器，無法載入資料', 'error');
    }
    return;
  }
  
  // 清除現有的圖表實例
  if (window.ApexCharts) {
    const existingChart = ApexCharts.getChartByID('lineChart');
    if (existingChart) {
      console.log('清除既有折線圖實例');
      existingChart.destroy();
    }
  }
  
  // 確保資料結構正確
  if (!data) {
    console.error('折線圖資料無效');
    if (window.showNotification) {
      window.showNotification('折線圖資料格式無效', 'error');
    }
    return;
  }
  
  // 確保圖表類型設置為line
  if (!data.chart) data.chart = {};
  data.chart.type = 'line';
  
  try {
    console.log('初始化折線圖', data);
    const chart = new ApexCharts(chartContainer, data);
    chart.render();
    console.log('折線圖渲染完成');
    
    if (window.showNotification) {
      window.showNotification('折線圖載入成功', 'success');
    }
    
    // 記錄實例以便後續清理
    window.chartInstances = window.chartInstances || {};
    window.chartInstances['lineChart'] = chart;
  } catch (error) {
    console.error('渲染折線圖時發生錯誤:', error);
    
    if (window.showNotification) {
      window.showNotification(`折線圖渲染失敗: ${error.message}`, 'error');
    }
    
    // 顯示錯誤在圖表容器中
    chartContainer.innerHTML = `
      <div class="flex flex-col items-center justify-center h-full">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-error mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <p class="text-base text-error font-medium">渲染折線圖失敗: ${error.message}</p>
        <button class="btn btn-sm btn-outline btn-error mt-4" onclick="location.reload()">重新整理頁面</button>
      </div>
    `;
  }
};
