// 調試工具 - 顯示組件狀態
document.addEventListener('DOMContentLoaded', function() {
  // 等待足夠時間確保所有組件都已加載
  setTimeout(function() {
    console.group('===== 組件載入狀態檢查 =====');
    
    // 檢查頁面路徑
    const currentPath = window.location.pathname;
    console.log('當前頁面路徑:', currentPath);
    
    // 檢查 toggleBtn
    const toggleBtn = document.getElementById('example-data-toggle');
    console.log('找到 Toggle 按鈕:', !!toggleBtn);
    
    // 檢查數據區塊
    const lineChartData = document.querySelector('.line-chart-data');
    const areaChartData = document.querySelector('.area-chart-data');
    const columnChartData = document.querySelector('.column-chart-data');
    const candlestickChartData = document.querySelector('.candlestick-chart-data');
    
    console.log('找到線圖數據區塊:', !!lineChartData);
    console.log('找到區域圖數據區塊:', !!areaChartData);
    console.log('找到柱狀圖數據區塊:', !!columnChartData);
    console.log('找到蠟燭圖數據區塊:', !!candlestickChartData);
    
    // 檢查圖表容器
    const lineChart = document.getElementById('lineChart');
    const areaChart = document.getElementById('areaChart');
    const columnChart = document.getElementById('columnChart');
    const candlestickChart = document.getElementById('candlestickChart');
    
    console.log('找到線圖容器:', !!lineChart);
    console.log('找到區域圖容器:', !!areaChart);
    console.log('找到柱狀圖容器:', !!columnChart);
    console.log('找到蠟燭圖容器:', !!candlestickChart);
    
    // 檢查數據選擇器組件
    const chartDataSelector = document.querySelector('[data-component="components/ui/ChartDataSelector.html"]');
    console.log('找到數據選擇器組件:', !!chartDataSelector);
    
    // 檢查 data-chart-type 屬性的元素
    const dataChartTypeElements = document.querySelectorAll('[data-chart-type]');
    console.log('找到具有 data-chart-type 屬性的元素數量:', dataChartTypeElements.length);
    
    // 輸出所有 data-chart-type 元素
    if (dataChartTypeElements.length > 0) {
      console.group('data-chart-type 元素詳情:');
      dataChartTypeElements.forEach((el, index) => {
        console.log(`元素 ${index + 1}:`, {
          id: el.id,
          type: el.getAttribute('data-chart-type'),
          display: window.getComputedStyle(el).display,
          visible: el.offsetParent !== null
        });
      });
      console.groupEnd();
    }
    
    console.groupEnd();
  }, 1000);
});
