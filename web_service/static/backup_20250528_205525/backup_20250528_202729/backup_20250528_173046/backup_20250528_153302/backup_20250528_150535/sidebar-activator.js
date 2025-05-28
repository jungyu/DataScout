/**
 * 側邊欄選單激活器
 * 根據當前頁面路徑自動展開相應的側邊欄折疊選單
 */

(function() {
  document.addEventListener('DOMContentLoaded', function() {
    console.log('側邊欄選單激活器已啟動');
    activateSidebar();
  });
  
  // 當組件加載完成後也嘗試激活側邊欄
  document.addEventListener('component-loaded', function(e) {
    if (e.detail && e.detail.componentPath === 'components/layout/Sidebar.html') {
      console.log('側邊欄組件加載完成，準備激活相應選單');
      // 稍微延遲以確保 DOM 已完全渲染
      setTimeout(activateSidebar, 100);
    }
  });
  
  // 全域函數，以便於外部調用
  window.activateSidebar = activateSidebar;

  function activateSidebar() {
    // 獲取當前頁面路徑
    const currentPath = window.location.pathname;
    console.log('當前頁面路徑:', currentPath);
    
    // 映射頁面路徑到對應的折疊選單索引
    let accordionIndex = 0; // 預設激活第一個選單（基本圖表類型）
    
    // 進階圖表類型 (索引 1)
    if (currentPath.includes('candlestick.html') || 
        currentPath.includes('boxplot.html') || 
        currentPath.includes('histogram.html') || 
        currentPath.includes('bubble.html') || 
        currentPath.includes('funnel.html') || 
        currentPath.includes('polar.html')) {
      accordionIndex = 1;
      console.log('檢測到進階圖表類型，自動展開進階圖表選單');
    }
    
    // 時間序列與監控圖表 (索引 2)
    else if (currentPath.includes('/timeseries') || 
             currentPath.includes('/synchronized') || 
             currentPath.includes('/stepline') || 
             currentPath.includes('/mixed-time')) {
      accordionIndex = 2;
    }
    
    // 比較與分析圖表 (索引 3)
    else if (currentPath.includes('/grouped-bar') || 
             currentPath.includes('/stacked-bar') || 
             currentPath.includes('/percent-stacked') || 
             currentPath.includes('/mixed-chart') || 
             currentPath.includes('/mixed.html') ||
             currentPath.includes('/heatmap-line') || 
             currentPath.includes('/multi-y-axis') || 
             currentPath.includes('/technical')) {
      accordionIndex = 3;
    }
    
    // 動態更新圖表 (索引 4)
    else if (currentPath.includes('/realtime') || 
             currentPath.includes('/dynamic') || 
             currentPath.includes('/streaming')) {
      accordionIndex = 4;
    }
    
    // 激活相應的折疊選單
    const accordionInputs = document.querySelectorAll('input[name="accordion-charts"]');
    if (accordionInputs && accordionInputs.length > accordionIndex) {
      console.log(`激活折疊選單: 索引 ${accordionIndex}`);
      accordionInputs[accordionIndex].checked = true;
    }
    
    // 高亮顯示當前活動的選單項
    highlightActiveMenuItem(currentPath);
  }
  
  function highlightActiveMenuItem(currentPath) {
    // 移除所有現有的活動狀態
    const allMenuItems = document.querySelectorAll('.menu a');
    allMenuItems.forEach(item => {
      item.classList.remove('bg-accent', 'text-white');
    });
    
    // 根據當前路徑查找相應的選單項並高亮
    const currentPathClean = currentPath.split('?')[0]; // 移除 URL 查詢參數
    const matchingItem = document.querySelector(`.menu a[href="${currentPathClean}"]`);
    
    if (matchingItem) {
      console.log('高亮顯示選單項:', currentPathClean);
      matchingItem.classList.add('bg-accent', 'text-white');
    } else {
      // 特殊處理：燭台圖表頁面
      if (currentPathClean.includes('candlestick.html')) {
        const candlestickItem = document.querySelector('.menu a[data-chart-type="candlestick"]');
        if (candlestickItem) {
          console.log('高亮顯示燭台圖表選單項');
          candlestickItem.classList.add('bg-accent', 'text-white');
        }
      }
    }
  }
})();
