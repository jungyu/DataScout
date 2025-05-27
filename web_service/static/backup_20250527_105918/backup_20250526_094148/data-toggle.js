// Toggle 範例資料顯示功能
document.addEventListener('DOMContentLoaded', function() {
  const toggle = document.getElementById('example-data-toggle');
  
  if (toggle) {
    // 初始化狀態
    let showExamples = true;
    
    // 設置初始狀態
    toggle.checked = showExamples;
    updateDataDisplay();
    
    // 監聽 Toggle 變化
    toggle.addEventListener('change', function() {
      showExamples = toggle.checked;
      updateDataDisplay();
      console.log('範例資料顯示狀態:', showExamples);
    });
    
    // 更新數據顯示
    function updateDataDisplay() {
      const dataSelector = document.getElementById('data-selector');
      
      if (dataSelector) {
        // 獲取 Alpine.js 實例
        const alpineInstance = window.Alpine && window.Alpine.getComponentsByName && 
                             window.Alpine.getComponentsByName('DataSelector')[0];
        
        if (alpineInstance) {
          alpineInstance.showExamples = showExamples;
        }
        
        // 手動更新 UI
        const exampleItems = dataSelector.querySelectorAll('[x-show="showExamples"]');
        const uploadItems = dataSelector.querySelectorAll('[x-show="!showExamples"]');
        
        exampleItems.forEach(item => {
          item.style.display = showExamples ? 'block' : 'none';
        });
        
        uploadItems.forEach(item => {
          item.style.display = !showExamples ? 'block' : 'none';
        });
      }
    }
  }
});
