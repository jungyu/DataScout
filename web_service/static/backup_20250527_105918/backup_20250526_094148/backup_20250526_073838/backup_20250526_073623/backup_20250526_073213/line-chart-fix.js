/**
 * 折線圖修復腳本
 * 解決「無法套用未知的圖表類型: line」錯誤
 * 改進折線圖的渲染邏輯
 */

(function() {
  console.log('折線圖修復腳本已載入');
  
  // 在頁面載入完成後執行
  document.addEventListener('DOMContentLoaded', function() {
    // 檢查是否在折線圖頁面
    if (window.location.pathname.toLowerCase().includes('line.html')) {
      console.log('檢測到折線圖頁面，啟用修復機制');
      
      // 監聽組件載入完成事件
      document.addEventListener('component-loaded', function(e) {
        if (e.detail && e.detail.componentPath && e.detail.componentPath.includes('LineChartContent.html')) {
          console.log('折線圖組件已載入，初始化修復');
          setTimeout(fixLineChart, 500);
        }
      });
    }
  });
  
  // 修復折線圖渲染問題
  function fixLineChart() {
    console.log('開始修復折線圖渲染問題');
    
    // 確認圖表容器存在
    const chartContainer = document.getElementById('lineChart');
    if (!chartContainer) {
      console.error('找不到折線圖容器元素');
      return;
    }
    
    // 確保清除任何已存在的圖表實例
    if (window.ApexCharts) {
      const existingChart = ApexCharts.getChartByID('lineChart');
      if (existingChart) {
        console.log('清除既有折線圖實例');
        existingChart.destroy();
      }
    }
    
    // 獲取當前載入的範例資料元素
    const activeExample = document.querySelector('.chart-data-item.active');
    if (!activeExample) {
      console.log('找不到活躍的範例資料，嘗試載入預設範例');
      loadDefaultLineChartExample();
      return;
    }
    
    // 獲取範例文件路徑
    const filePath = activeExample.dataset.file;
    if (!filePath) {
      console.error('範例資料缺少檔案路徑');
      return;
    }
    
    // 加載並渲染圖表
    console.log(`嘗試載入折線圖資料: ${filePath}`);
    fetch(`/assets/examples/${filePath}`)
      .then(response => {
        if (!response.ok) throw new Error(`無法載入檔案 ${filePath}`);
        return response.json();
      })
      .then(data => {
        renderLineChart(data);
      })
      .catch(error => {
        console.error('載入折線圖資料時發生錯誤:', error);
        showErrorMessage(chartContainer, `載入資料失敗: ${error.message}`);
      });
  }
  
  // 載入預設折線圖範例
  function loadDefaultLineChartExample() {
    console.log('載入預設折線圖範例');
    fetch('/assets/examples/apexcharts_line_sales.json')
      .then(response => {
        if (!response.ok) throw new Error('無法載入預設折線圖資料');
        return response.json();
      })
      .then(data => {
        renderLineChart(data);
      })
      .catch(error => {
        console.error('載入預設折線圖資料時發生錯誤:', error);
        const chartContainer = document.getElementById('lineChart');
        if (chartContainer) {
          showErrorMessage(chartContainer, `載入預設資料失敗: ${error.message}`);
        }
      });
  }
  
  // 渲染折線圖
  function renderLineChart(data) {
    console.log('開始渲染折線圖', data);
    const chartContainer = document.getElementById('lineChart');
    if (!chartContainer) return;
    
    // 確保 data.chart.type 為 'line'
    if (!data.chart) data.chart = {};
    data.chart.type = 'line';
    
    try {
      // 創建並渲染圖表
      const chart = new ApexCharts(chartContainer, data);
      chart.render();
      console.log('折線圖渲染完成');
    } catch (error) {
      console.error('渲染折線圖時發生錯誤:', error);
      showErrorMessage(chartContainer, `渲染圖表失敗: ${error.message}`);
    }
  }
  
  // 顯示錯誤訊息
  function showErrorMessage(container, message) {
    container.innerHTML = `
      <div class="flex flex-col items-center justify-center h-full">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-error mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <p class="text-base text-error font-medium">${message}</p>
        <button class="btn btn-sm btn-outline btn-error mt-4" onclick="location.reload()">重新整理頁面</button>
      </div>
    `;
  }
})();
