// Debug Toggle 功能
document.addEventListener('DOMContentLoaded', function() {
  // 等待 Alpine.js 初始化完成
  setTimeout(function() {
    console.log('檢查 Toggle 按鈕');
    
    // 尋找 Toggle 按鈕
    const toggleElement = document.querySelector('input[x-model="showExamples"]');
    if (toggleElement) {
      console.log('找到 Toggle 按鈕:', toggleElement);
      
      // 手動觸發點擊事件測試 Toggle 功能
      console.log('Toggle 初始狀態:', toggleElement.checked);
      
      // 確認 Alpine.js 是否已初始化
      const alpineComponent = document.querySelector('[x-data="DataSelector()"]');
      if (alpineComponent) {
        console.log('Alpine.js 組件已初始化');
        
        // 檢查全局數據
        console.log('Window.Alpine:', window.Alpine);
        if (window.Alpine) {
          console.log('Alpine.js 版本:', window.Alpine.version);
        }
      } else {
        console.error('找不到 Alpine.js 組件');
      }
    } else {
      console.error('找不到 Toggle 按鈕');
    }
    
    // 確保全局 data 函數可用
    if (window.Alpine && window.Alpine.data) {
      console.log('Alpine.data 可用');
    } else {
      console.error('Alpine.data 不可用');
    }
  }, 1000);
});
