/**
 * 面積圖資料選擇器緊急修復腳本
 * 這個腳本專門用於確保面積圖數據選擇器在 area.html 頁面上正確顯示
 */

(function() {
  console.log('%c🔧 面積圖修復工具已啟動', 'background:#10b981;color:white;padding:2px 5px;border-radius:3px');
  
  // 立即執行面積圖修復
  setTimeout(fixAreaChartSelector, 500);
  
  // 在組件載入事件後再次執行
  document.addEventListener('component-loaded', function(e) {
    if (e.detail.componentPath === 'components/ui/ChartDataSelector.html') {
      console.log('🔄 檢測到資料選擇器組件載入事件，開始面積圖專用修復');
      setTimeout(fixAreaChartSelector, 200);
    }
  });
  
  /**
   * 面積圖數據選擇器專用修復函數
   */
  function fixAreaChartSelector() {
    const currentPath = window.location.pathname;
    
    // 只在 area.html 頁面運行
    if (!currentPath.endsWith('area.html')) {
      console.log('不是面積圖頁面，無需執行專用修復');
      return;
    }
    
    console.log('✅ 確認為面積圖頁面，開始執行專用修復');
    
    // 找到資料選擇器組件
    const dataSelector = document.getElementById('chart-data-selector-component');
    if (!dataSelector) {
      console.log('⏳ 資料選擇器尚未載入，稍後再試...');
      setTimeout(fixAreaChartSelector, 500);
      return;
    }
    
    console.log('找到資料選擇器組件，執行面積圖數據區塊顯示修復');
    
    try {
      // 隱藏所有數據區塊
      const allDataBlocks = dataSelector.querySelectorAll('.chart-data-block');
      allDataBlocks.forEach(block => {
        const type = block.getAttribute('data-chart-type');
        if (type !== 'area') {
          block.style.setProperty('display', 'none', 'important');
          console.log(`隱藏非面積圖數據區塊: ${type}`);
        }
      });
      
      // 特定處理面積圖數據區塊
      const areaBlock = dataSelector.querySelector('#area-chart-data');
      if (areaBlock) {
        console.log('找到面積圖數據區塊，設置為顯示狀態');
        // 移除所有可能影響顯示的樣式
        areaBlock.removeAttribute('style');
        // 強制顯示
        areaBlock.style.setProperty('display', 'block', 'important');
        
        // 標記元素以便調試
        areaBlock.setAttribute('data-fixed-by', 'area-fix.js');
        areaBlock.setAttribute('data-fixed-time', new Date().toISOString());
        
        // 確保子元素可見
        const children = areaBlock.querySelectorAll('*');
        children.forEach(child => {
          if (child.style && child.style.display === 'none') {
            child.style.removeProperty('display');
          }
        });
        
        // 添加視覺提示
        areaBlock.style.setProperty('border-left', '3px solid #10b981', 'important');
        
        // 確保父元素和組件容器都是可見的
        let parent = areaBlock.parentElement;
        while (parent) {
          if (parent.style && (parent.style.display === 'none' || parent.style.visibility === 'hidden')) {
            parent.style.removeProperty('display');
            parent.style.removeProperty('visibility');
          }
          parent = parent.parentElement;
        }
        
        // 處理紅色虛線框區域 - 嘗試尋找紅色虛線框並顯示選擇器
        const redBoxes = document.querySelectorAll('.red-dashed-box, [style*="border: 2px dashed red"], [style*="border:2px dashed red"]');
        console.log(`找到 ${redBoxes.length} 個紅色虛線框元素`);
        
        if (redBoxes.length > 0) {
          redBoxes.forEach(box => {
            console.log('處理紅色虛線框元素:', box);
            
            // 檢查這個虛線框是否已經包含資料選擇器
            const existingSelector = box.querySelector('#chart-data-selector-component');
            if (existingSelector) {
              console.log('紅色虛線框已包含資料選擇器，確保它是可見的');
              // 確保其顯示正確的區塊
              const existingAreaBlock = existingSelector.querySelector('#area-chart-data');
              if (existingAreaBlock) {
                existingAreaBlock.style.setProperty('display', 'block', 'important');
                console.log('確保紅色虛線框中的面積圖數據區塊是可見的');
              }
              return;
            }
            
            // 將選擇器複製到紅色框中
            const clonedSelector = dataSelector.cloneNode(true);
            clonedSelector.id = 'chart-data-selector-in-red-box';
            
            // 確保複製的選擇器可見
            clonedSelector.style.removeProperty('display');
            clonedSelector.style.setProperty('display', 'block', 'important');
            
            // 確保面積圖區塊在複製的選擇器中可見
            const clonedAreaBlock = clonedSelector.querySelector('#area-chart-data');
            if (clonedAreaBlock) {
              clonedAreaBlock.style.removeProperty('display');
              clonedAreaBlock.style.setProperty('display', 'block', 'important');
              console.log('確保複製的選擇器中的面積圖區塊可見');
            }
            
            // 如果紅色框是空的，直接添加；否則替換內容
            if (box.children.length === 0) {
              box.appendChild(clonedSelector);
              console.log('將資料選擇器添加到空的紅色框中');
            } else {
              console.log('紅色框不為空，替換內容');
              // 清除所有子元素
              while (box.firstChild) {
                box.removeChild(box.firstChild);
              }
              box.appendChild(clonedSelector);
            }
            
            console.log('紅色虛線框處理完成');
          });
        } else {
          console.warn('未找到紅色虛線框元素，尋找其他可能的容器');
          // 尋找其他可能的容器
          const containers = document.querySelectorAll('.col-span-1');
          containers.forEach(container => {
            if (!container.querySelector('#chart-data-selector-component')) {
              console.log('找到一個可能的容器，嘗試添加資料選擇器');
              const clonedSelector = dataSelector.cloneNode(true);
              
              // 添加紅色虛線邊框
              container.style.setProperty('border', '2px dashed red', 'important');
              container.style.setProperty('padding', '2px', 'important');
              
              // 清除容器內容
              while (container.firstChild) {
                container.removeChild(container.firstChild);
              }
              
              // 添加選擇器
              container.appendChild(clonedSelector);
              console.log('已將資料選擇器添加到找到的容器中');
            }
          });
        }
        
        console.log('%c✨ 面積圖數據區塊修復完成!', 'background:#10b981;color:white;padding:2px 5px;border-radius:3px');
      } else {
        console.error('❌ 找不到面積圖數據區塊 (#area-chart-data)');
        
        // 尋找可能有類似功能的區塊
        const possibleAreaBlocks = dataSelector.querySelectorAll('[class*="area"]');
        console.log(`找到 ${possibleAreaBlocks.length} 個可能的面積圖相關區塊`);
        
        // 如果找到可能的區塊，嘗試顯示它們
        if (possibleAreaBlocks.length > 0) {
          possibleAreaBlocks.forEach(block => {
            block.removeAttribute('style');
            block.style.setProperty('display', 'block', 'important');
            block.style.setProperty('border', '2px dashed #f43f5e', 'important');
            console.log(`嘗試顯示可能的面積圖區塊: ${block.id || block.className}`);
          });
        }
      }
    } catch (error) {
      console.error('面積圖數據選擇器修復失敗:', error);
    }
    
    // 設置定期檢查，確保修復持續生效
    setInterval(function() {
      const areaBlock = dataSelector.querySelector('#area-chart-data');
      if (areaBlock && window.getComputedStyle(areaBlock).display === 'none') {
        console.log('檢測到面積圖區塊被隱藏，重新修復');
        areaBlock.style.setProperty('display', 'block', 'important');
      }
    }, 2000);
  }
  
  // 監聽 DOM 變化，確保在動態更新時及時修復
  if (typeof MutationObserver !== 'undefined') {
    const observer = new MutationObserver(function(mutations) {
      mutations.forEach(function(mutation) {
        if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
          // 檢查是否有資料選擇器相關元素被添加
          mutation.addedNodes.forEach(function(node) {
            if (node.nodeType === 1 && (
                node.id === 'chart-data-selector-component' || 
                node.querySelector && node.querySelector('#chart-data-selector-component')
            )) {
              console.log('🔄 檢測到 DOM 變化，重新執行修復');
              fixAreaChartSelector();
            }
          });
        }
      });
    });
    
    // 開始監聽 document.body 的變化
    observer.observe(document.body, { childList: true, subtree: true });
    console.log('已設置 DOM 變化監聽');
  }
})();
