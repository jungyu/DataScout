// 手動實現 Toggle 功能
window.addEventListener('DOMContentLoaded', function() {
  console.log('設置手動 Toggle 功能');
  
  // 全局變數，控制是否顯示範例資料
  window.showExamplesState = true;
  
  // 手動切換函數
  window.toggleForceButton = function() {
    window.showExamplesState = !window.showExamplesState;
    console.log('手動切換狀態為:', window.showExamplesState);
    
    // 更新顯示
    const exampleSection = document.querySelectorAll('[x-show="showExamples"]')[0];
    const uploadSection = document.querySelectorAll('[x-show="!showExamples"]')[0];
    
    if (exampleSection && uploadSection) {
      if (window.showExamplesState) {
        exampleSection.style.display = 'block';
        uploadSection.style.display = 'none';
      } else {
        exampleSection.style.display = 'none';
        uploadSection.style.display = 'block';
      }
      console.log('手動更新 UI 成功');
    } else {
      console.error('找不到需要更新的區塊');
    }
    
    // 嘗試同步 Alpine.js 中的狀態（如果可能）
    const toggleCheckbox = document.getElementById('toggle-checkbox');
    if (toggleCheckbox) {
      toggleCheckbox.checked = window.showExamplesState;
      console.log('同步 checkbox 狀態為:', toggleCheckbox.checked);
    }
  };
});
