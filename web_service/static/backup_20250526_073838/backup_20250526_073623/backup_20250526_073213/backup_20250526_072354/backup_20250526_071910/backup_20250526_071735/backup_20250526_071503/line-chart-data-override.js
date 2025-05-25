/**
 * 擴展 data-loader.js 中的函數，處理折線圖類型
 */

// 保存原始的 applyChartData 函數
const originalApplyChartData = window.applyChartData;

// 覆蓋 applyChartData 函數以添加對折線圖的特殊處理
window.applyChartData = function(data, chartType) {
  console.log('擴展的 applyChartData 被調用，圖表類型:', chartType);
  
  // 檢查是否為折線圖類型
  if (chartType === 'line') {
    console.log('檢測到折線圖類型，使用特殊處理邏輯');
    if (window.handleLineChart) {
      window.handleLineChart(data);
      return;
    }
  }
  
  // 對其他圖表類型使用原始函數
  if (originalApplyChartData) {
    originalApplyChartData(data, chartType);
  }
};

// 創建一個直接調用的特殊處理函數
window.handleLineChartData = function(data) {
  if (window.handleLineChart) {
    window.handleLineChart(data);
  } else {
    console.error('找不到折線圖處理函數');
  }
};
