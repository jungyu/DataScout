/**
 * 資料選擇器修復工具
 * 此腳本會直接針對資料選擇器組件進行修復，確保它在所有頁面上正確渲染
 */

// 立即執行修復，不等待 DOMContentLoaded
(function() {
  console.log('%c🔧 資料選擇器修復工具已啟動', 'background:#2563eb;color:white;padding:2px 5px;border-radius:3px');
  
  // 延時執行以確保組件已載入
  executeWithRetry(fixDataSelector, 5, 500);
  
  /**
   * 修復資料選擇器組件
   */
  function fixDataSelector() {
    // 檢測當前頁面的圖表類型
    const currentPath = window.location.pathname;
    let chartType = 'candlestick'; // 默認為蠟燭圖
    
    if (currentPath.endsWith('/') || currentPath.endsWith('/index.html')) {
      chartType = 'candlestick';
    } else if (currentPath.includes('line')) {
      chartType = 'line';
    } else if (currentPath.includes('area')) {
      chartType = 'area';
    } else if (currentPath.includes('column')) {
      chartType = 'column';
    }
    
    console.log(`🔍 檢測到圖表類型: ${chartType} (路徑: ${currentPath})`);
    
    // 找到資料選擇器組件
    const dataSelector = document.getElementById('chart-data-selector-component');
    if (!dataSelector) {
      console.log('⏳ 資料選擇器尚未載入，等待中...');
      return false; // 返回 false 表示需要重試
    }
    
    console.log('✅ 找到資料選擇器組件，開始修復');
    
    try {
      // 確保所有數據區塊都有正確的數據屬性
      const dataBlocks = dataSelector.querySelectorAll('.line-chart-data, .area-chart-data, .column-chart-data, .candlestick-chart-data');
      dataBlocks.forEach(block => {
        // 從類名中提取圖表類型
        const className = Array.from(block.classList).find(cls => cls.endsWith('-chart-data'));
        if (className) {
          const type = className.replace('-chart-data', '');
          block.setAttribute('data-chart-type', type);
          
          // 添加統一的圖表數據區塊類名
          if (!block.classList.contains('chart-data-block')) {
            block.classList.add('chart-data-block');
          }
          
          // 強制設置顯示或隱藏，確保正確的顯示狀態
          const shouldDisplay = type === chartType;
          console.log(`設置 ${type} 區塊顯示狀態為: ${shouldDisplay ? '顯示' : '隱藏'}`);
          
          // 移除任何內聯樣式
          block.style.removeProperty('display');
          // 然後設置新的樣式
          block.style.setProperty('display', shouldDisplay ? 'block' : 'none', 'important');
          
          // 雙重保險：確保區塊內的內容也正確顯示
          if (shouldDisplay) {
            const childItems = block.querySelectorAll('*');
            childItems.forEach(item => {
              if (item.style.display === 'none') {
                item.style.setProperty('display', '', 'important');
              }
            });
          }
        }
      });
      
      // 標記組件已修復
      dataSelector.setAttribute('data-fixed', 'true');
      dataSelector.setAttribute('data-active-chart', chartType);
      
      // 確保上傳區域的顯示狀態正確
      const toggleBtn = dataSelector.querySelector('#example-data-toggle');
      const uploadSection = dataSelector.querySelector('#file-upload-section');
      if (toggleBtn && uploadSection) {
        uploadSection.style.setProperty('display', toggleBtn.checked ? 'none' : 'block', 'important');
      }
      
      console.log('%c✨ 資料選擇器修復完成!', 'background:green;color:white;padding:2px 5px;border-radius:3px');
      
      // 添加通知指示器
      showNotification('資料選擇器已修復', 'success');
      
      return true; // 返回 true 表示修復成功，不需要重試
    } catch (error) {
      console.error('❌ 修復過程中出錯:', error);
      showNotification('修復嘗試失敗: ' + error.message, 'error');
      return false; // 返回 false 表示需要重試
    }
  }
  
  /**
   * 帶重試機制的執行函數
   */
  function executeWithRetry(fn, maxAttempts, delay) {
    let attempts = 0;
    
    function attempt() {
      if (attempts >= maxAttempts) {
        console.log(`❌ 已重試 ${maxAttempts} 次，但仍未成功`);
        showNotification(`修復失敗，已嘗試 ${maxAttempts} 次`, 'error');
        return;
      }
      
      attempts++;
      console.log(`🔄 嘗試修復 (#${attempts})`);
      
      const result = fn();
      if (!result) {
        // 如果返回 false，則重試
        setTimeout(attempt, delay);
      }
    }
    
    // 首次嘗試
    attempt();
  }
  
  /**
   * 顯示通知
   */
  function showNotification(message, type = 'info') {
    // 檢查是否已存在通知元素
    let notification = document.getElementById('fix-notification');
    
    if (!notification) {
      // 創建通知元素
      notification = document.createElement('div');
      notification.id = 'fix-notification';
      document.body.appendChild(notification);
    }
    
    // 設置通知樣式
    notification.style.position = 'fixed';
    notification.style.bottom = '80px';
    notification.style.right = '20px';
    notification.style.padding = '10px 15px';
    notification.style.borderRadius = '4px';
    notification.style.zIndex = '9999';
    notification.style.fontSize = '14px';
    notification.style.boxShadow = '0 3px 6px rgba(0,0,0,0.16)';
    
    // 根據類型設置不同顏色
    if (type === 'success') {
      notification.style.backgroundColor = '#4CAF50';
      notification.style.color = 'white';
    } else if (type === 'error') {
      notification.style.backgroundColor = '#F44336';
      notification.style.color = 'white';
    } else {
      notification.style.backgroundColor = '#2196F3';
      notification.style.color = 'white';
    }
    
    // 設置通知內容
    notification.textContent = message;
    
    // 顯示通知
    notification.style.opacity = 1;
    
    // 3秒後隱藏通知
    setTimeout(() => {
      notification.style.opacity = 0;
      notification.style.transition = 'opacity 0.5s';
      
      // 完全淡出後移除元素
      setTimeout(() => {
        if (notification && notification.parentNode) {
          notification.parentNode.removeChild(notification);
        }
      }, 500);
    }, 3000);
  }
  
  // 添加 DOM 變化觀察器，確保在組件動態載入時也能修復
  function setupMutationObserver() {
    // 建立一個觀察器實例
    const observer = new MutationObserver(mutations => {
      mutations.forEach(mutation => {
        if (mutation.type === 'childList' && mutation.addedNodes.length) {
          // 檢查是否添加了資料選擇器組件
          const selector = document.getElementById('chart-data-selector-component');
          if (selector && !selector.hasAttribute('data-fixed')) {
            console.log('🔄 檢測到資料選擇器被添加到 DOM，開始修復');
            fixDataSelector();
          }
        }
      });
    });
    
    // 配置觀察器選項
    const config = { childList: true, subtree: true };
    
    // 開始觀察 body
    observer.observe(document.body, config);
    
    // 為了避免無限運行，10 秒後停止觀察
    setTimeout(() => {
      observer.disconnect();
      console.log('🛑 DOM 觀察器已停止');
    }, 10000);
  }
  
  // 啟動 DOM 變化觀察器
  setupMutationObserver();
  
  // 添加組件載入事件監聽
  document.addEventListener('component-loaded', function(e) {
    if (e.detail.componentPath === 'components/ui/ChartDataSelector.html') {
      console.log('🔄 檢測到資料選擇器組件載入事件，開始修復');
      // 短暫延遲確保 DOM 完全更新
      setTimeout(fixDataSelector, 100);
    }
  });
})();
