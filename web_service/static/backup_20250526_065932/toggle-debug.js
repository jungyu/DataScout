// 測試腳本，用來確認 Toggle 按鈕的狀態
document.addEventListener('DOMContentLoaded', function() {
  setTimeout(function() {
    console.log('Toggle 狀態檢查');
    const toggleElement = document.querySelector('input[x-model="showExamples"]');
    if (toggleElement) {
      console.log('找到 Toggle 元素:', toggleElement);
      console.log('Toggle 狀態:', toggleElement.checked);
    } else {
      console.error('找不到 Toggle 元素');
    }
    
    // 檢查是否有 Alpine.js 初始化的元素
    const alpineElements = document.querySelectorAll('[x-data]');
    console.log('Alpine.js 元素數量:', alpineElements.length);
    
    // 檢查 DataSelector 是否被正確初始化
    const selectorElement = document.getElementById('data-selector');
    if (selectorElement) {
      console.log('Selector 元素內容:', selectorElement.innerHTML.substring(0, 100) + '...');
    }
  }, 1000);
});
