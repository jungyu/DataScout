/**
 * 資料選擇器專用調試工具
 */

document.addEventListener('DOMContentLoaded', function() {
  // 立即執行一次（快速響應）
  checkAndFixSelector();
  
  // 然後延遲執行以確保所有組件都已完全載入
  setTimeout(checkAndFixSelector, 1000);
  // 再次檢查，確保處理組件載入延遲的情況
  setTimeout(checkAndFixSelector, 2000);
});

// 提取為函數，以便多次調用
function checkAndFixSelector() {
  console.group('===== 資料選擇器狀態檢查 =====');
  
  // 檢查頁面路徑
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
    
    console.log('當前路徑:', currentPath);
    console.log('預期圖表類型:', chartType);
    
    // 獲取資料選擇器組件
    const dataSelector = document.getElementById('chart-data-selector-component');
    console.log('找到資料選擇器組件:', !!dataSelector);
    
    if (dataSelector) {
      // 深入檢查組件結構
      const dataBlocks = dataSelector.querySelectorAll('.chart-data-block');
      console.log('找到資料區塊數量:', dataBlocks.length);
      
      // 輸出每個區塊的狀態
      dataBlocks.forEach(block => {
        const blockType = block.getAttribute('data-chart-type');
        const isVisible = window.getComputedStyle(block).display !== 'none';
        console.log(`資料區塊 [${blockType}] -`, isVisible ? '可見' : '隱藏', 
                    `(預期: ${blockType === chartType ? '可見' : '隱藏'})`,
                    `ID: ${block.id}`);
      });
      
      // 取得切換按鈕狀態
      const toggleBtn = dataSelector.querySelector('#example-data-toggle');
      console.log('Toggle 按鈕:', toggleBtn ? '找到' : '未找到', 
                  toggleBtn ? (toggleBtn.checked ? '開啟' : '關閉') : '');
      
      // 檢查檔案上傳區域
      const uploadSection = dataSelector.querySelector('#file-upload-section');
      console.log('上傳區域:', uploadSection ? '找到' : '未找到',
                 uploadSection ? `顯示狀態: ${window.getComputedStyle(uploadSection).display}` : '');
    }
    
    // 嘗試恢復問題
    console.log('嘗試恢復任何顯示問題...');
    
    try {
      if (dataSelector) {
        // 強制根據當前頁面類型顯示正確的區塊
        const dataBlocks = dataSelector.querySelectorAll('.chart-data-block');
        dataBlocks.forEach(block => {
          const blockType = block.getAttribute('data-chart-type');
          block.style.display = blockType === chartType ? 'block' : 'none';
        });
        
        // 確保上傳區域隱藏（如果 Toggle 為開啟狀態）
        const toggleBtn = dataSelector.querySelector('#example-data-toggle');
        const uploadSection = dataSelector.querySelector('#file-upload-section');
        if (toggleBtn && toggleBtn.checked && uploadSection) {
          uploadSection.style.display = 'none';
        } else if (toggleBtn && !toggleBtn.checked && uploadSection) {
          uploadSection.style.display = 'block';
        }
        
        console.log('修復完成');
      }
    } catch (error) {
      console.error('修復過程中出錯:', error);
    }
    
    // 檢查生效的樣式
    console.log('檢查 CSS 樣式:');
    if (dataSelector) {
      const styles = window.getComputedStyle(dataSelector);
      console.log('選擇器寬度:', styles.width);
      console.log('選擇器可見性:', styles.visibility);
      console.log('選擇器顯示狀態:', styles.display);
    }
    
    console.groupEnd();
    
    // 在頁面上添加視覺指示
    const indicator = document.createElement('div');
    indicator.className = 'selector-debug-indicator'; // 添加類名以便識別
    indicator.style.position = 'fixed';
    indicator.style.bottom = '20px';
    indicator.style.right = '20px';
    indicator.style.padding = '10px';
    indicator.style.background = 'rgba(0, 0, 0, 0.7)';
    indicator.style.color = 'white';
    indicator.style.borderRadius = '4px';
    indicator.style.fontSize = '12px';
    indicator.style.zIndex = '9999';
    indicator.textContent = `圖表類型: ${chartType} | 選擇器: ${dataSelector ? '已載入' : '未載入'} | 修復狀態: ${dataSelector ? '已執行' : '等待組件載入'}`;
    
    // 移除舊的指示器（如果有）
    const oldIndicators = document.querySelectorAll('.selector-debug-indicator');
    oldIndicators.forEach(old => old.remove());
    
    // 添加新指示器
    document.body.appendChild(indicator);
    
    // 5秒後移除指示器
    setTimeout(() => {
      indicator.remove();
    }, 5000);
    
    // 監聽組件載入事件，如果尚未找到選擇器
    if (!dataSelector) {
      document.addEventListener('component-loaded', function handleComponentLoad(e) {
        if (e.detail.componentPath === 'components/ui/ChartDataSelector.html') {
          console.log('資料選擇器已載入，重新執行檢查');
          // 移除事件監聽器，避免重複執行
          document.removeEventListener('component-loaded', handleComponentLoad);
          // 延遲執行，確保DOM更新
          setTimeout(checkAndFixSelector, 100);
        }
      });
    }
    
    // 直接觀察DOM變化以捕獲資料選擇器的載入
    if (!dataSelector) {
      const observer = new MutationObserver(function(mutations) {
        const newlyLoadedSelector = document.getElementById('chart-data-selector-component');
        if (newlyLoadedSelector) {
          console.log('透過 DOM 觀察者檢測到資料選擇器，重新執行檢查');
          observer.disconnect();
          // 延遲執行，確保DOM完全更新
          setTimeout(checkAndFixSelector, 100);
        }
      });
      
      observer.observe(document.body, { childList: true, subtree: true });
      
      // 5秒後停止觀察，避免無限監控
      setTimeout(() => observer.disconnect(), 5000);
    }
}
