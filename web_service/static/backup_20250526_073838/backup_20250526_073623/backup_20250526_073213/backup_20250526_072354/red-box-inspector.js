/**
 * 紅色虛線框檢查器
 * 專門用於找到並設置紅色虛線框內的內容
 */

(function() {
  console.log('紅色虛線框檢查器已啟動');
  
  // 頁面載入時執行
  document.addEventListener('DOMContentLoaded', function() {
    setTimeout(findRedBox, 500);
  });
  
  // 組件載入後執行
  document.addEventListener('component-loaded', function() {
    setTimeout(findRedBox, 300);
  });
  
  function findRedBox() {
    console.log('開始尋找紅色虛線框');
    
    // 紅色虛線框可能有的選擇器
    const redBoxSelectors = [
      '.red-dashed-box',
      '[style*="border: 2px dashed red"]',
      '[style*="border:2px dashed red"]'
    ];
    
    let redBox = null;
    
    // 尋找紅色虛線框
    for (const selector of redBoxSelectors) {
      const elements = document.querySelectorAll(selector);
      if (elements.length > 0) {
        redBox = elements[0];
        console.log(`找到紅色虛線框：${selector}`);
        break;
      }
    }
    
    // 如果沒找到，則嘗試查找左側內容區域並添加紅色虛線框
    if (!redBox) {
      console.log('未找到紅色虛線框，嘗試創建');
      
      // 查找可能包含數據選擇器的元素
      const contentElements = document.querySelectorAll('.col-span-1');
      contentElements.forEach(el => {
        if (el.parentElement && el.parentElement.classList.contains('grid')) {
          console.log('找到可能的內容區域，添加紅色虛線框');
          el.style.border = '2px dashed red';
          el.style.padding = '2px';
          el.classList.add('red-dashed-box');
          redBox = el;
        }
      });
    }
    
    // 如果找到紅色虛線框但它是空的，填充它
    if (redBox) {
      // 檢查是否為空或只包含空格
      const isEmpty = !redBox.innerHTML.trim();
      
      if (isEmpty || !redBox.querySelector('#chart-data-selector-component, #direct-selector')) {
        console.log('紅色虛線框為空或沒有資料選擇器，填充它');
        
        // 嘗試在頁面中找到資料選擇器
        const selector = document.getElementById('chart-data-selector-component');
        
        if (selector) {
          console.log('找到資料選擇器，複製到紅色虛線框');
          const clone = selector.cloneNode(true);
          clone.id = 'chart-data-selector-in-red-box';
          
          // 清空紅色框
          while (redBox.firstChild) {
            redBox.removeChild(redBox.firstChild);
          }
          
          // 添加複製的選擇器
          redBox.appendChild(clone);
          
          // 確保顯示面積圖數據區塊
          const areaBlock = clone.querySelector('#area-chart-data');
          if (areaBlock) {
            // 隱藏所有數據區塊
            const allBlocks = clone.querySelectorAll('.chart-data-block');
            allBlocks.forEach(block => {
              block.style.display = 'none';
            });
            
            // 顯示面積圖數據區塊
            areaBlock.style.display = 'block';
          } else {
            console.error('在複製的選擇器中找不到面積圖數據區塊');
          }
        } else {
          console.log('未找到現有資料選擇器，創建新的');
          // 直接創建資料選擇器
          redBox.innerHTML = `
            <div class="bg-base-100 p-4 rounded-lg shadow-md border border-base-300" id="direct-selector">
              <div class="flex items-center justify-between mb-4">
                <div class="flex items-center">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1 text-accent" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M5 4a1 1 0 00-2 0v7.268a2 2 0 000 3.464V16a1 1 0 102 0v-1.268a2 2 0 000-3.464V4zM11 4a1 1 0 10-2 0v1.268a2 2 0 000 3.464V16a1 1 0 102 0V8.732a2 2 0 000-3.464V4zM16 3a1 1 0 011 1v7.268a2 2 0 010 3.464V16a1 1 0 11-2 0v-1.268a2 2 0 010-3.464V4a1 1 0 011-1z" />
                  </svg>
                  <span class="text-base font-semibold text-base-content">範例資料</span>
                </div>
                <label class="relative inline-flex items-center cursor-pointer">
                  <input type="checkbox" id="auto-toggle" class="sr-only peer" checked>
                  <div class="w-11 h-6 bg-gray-200 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-accent"></div>
                </label>
              </div>
              
              <div class="space-y-3">
                <div class="bg-base-200 p-4 mb-4 rounded-lg hover:bg-base-300 transition-colors border border-base-300">
                  <div class="font-medium mb-1 text-base-content">網站統計資料</div>
                  <div class="text-sm text-base-content opacity-80 mb-2">每月訪問量與轉換率</div>
                  <button class="text-accent hover:text-accent-focus text-sm font-medium btn-sm btn-ghost px-2 py-0.5 rounded">點擊載入</button>
                </div>
                
                <div class="bg-base-200 p-4 mb-4 rounded-lg hover:bg-base-300 transition-colors border border-base-300">
                  <div class="font-medium mb-1 text-base-content">流量來源分析</div>
                  <div class="text-sm text-base-content opacity-80 mb-2">不同管道的訪問量趨勢</div>
                  <button class="text-accent hover:text-accent-focus text-sm font-medium btn-sm btn-ghost px-2 py-0.5 rounded">點擊載入</button>
                </div>
                
                <div class="bg-base-200 p-4 mb-4 rounded-lg hover:bg-base-300 transition-colors border border-base-300">
                  <div class="font-medium mb-1 text-base-content">使用者參與度</div>
                  <div class="text-sm text-base-content opacity-80 mb-2">每週頁面瀏覽時間統計</div>
                  <button class="text-accent hover:text-accent-focus text-sm font-medium btn-sm btn-ghost px-2 py-0.5 rounded">點擊載入</button>
                </div>
              </div>
            </div>
          `;
        }
        
        console.log('紅色虛線框內容已填充');
      } else {
        console.log('紅色虛線框已有內容，檢查資料區塊可見性');
        
        // 檢查框內是否有選擇器
        const boxSelector = redBox.querySelector('#chart-data-selector-component, #direct-selector, #chart-data-selector-in-red-box');
        if (boxSelector) {
          // 確保顯示面積圖數據區塊
          const areaBlock = boxSelector.querySelector('#area-chart-data');
          if (areaBlock) {
            // 隱藏所有數據區塊
            const allBlocks = boxSelector.querySelectorAll('.chart-data-block');
            allBlocks.forEach(block => {
              block.style.display = 'none';
            });
            
            // 顯示面積圖數據區塊
            areaBlock.style.display = 'block';
            console.log('確保紅色虛線框中的面積圖數據區塊可見');
          }
        }
      }
    } else {
      console.error('無法找到或創建紅色虛線框');
    }
  }
  
  // 定期檢查紅色虛線框
  setInterval(findRedBox, 3000);
})();
