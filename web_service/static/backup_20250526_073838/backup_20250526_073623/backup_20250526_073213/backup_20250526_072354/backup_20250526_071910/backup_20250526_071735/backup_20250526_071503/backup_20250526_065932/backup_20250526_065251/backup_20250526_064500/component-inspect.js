/**
 * 組件檢查工具
 * 提供一種方法來檢查和調試組件結構和渲染
 */
document.addEventListener('DOMContentLoaded', function() {
  // 延遲添加检查按鈕，確保DOM完全載入
  setTimeout(function() {
    // 創建检查按鈕
    const inspectButton = document.createElement('button');
    inspectButton.textContent = '檢查組件';
    inspectButton.classList.add('fixed', 'top-4', 'right-4', 'z-50', 'bg-blue-600', 'text-white', 'px-3', 'py-1', 'rounded', 'shadow-md', 'text-sm');
    document.body.appendChild(inspectButton);
    
    // 當前檢查狀態
    let isInspecting = false;
    
    // 創建信息面板
    const infoPanel = document.createElement('div');
    infoPanel.classList.add('fixed', 'bottom-4', 'right-4', 'bg-white', 'p-4', 'rounded', 'shadow-lg', 'z-50', 'border', 'border-gray-300', 'text-sm', 'max-w-md', 'max-h-80', 'overflow-auto');
    infoPanel.style.display = 'none';
    document.body.appendChild(infoPanel);
    
    // 點擊按鈕切換檢查模式
    inspectButton.addEventListener('click', function() {
      isInspecting = !isInspecting;
      inspectButton.textContent = isInspecting ? '關閉檢查' : '檢查組件';
      inspectButton.classList.toggle('bg-red-600', isInspecting);
      inspectButton.classList.toggle('bg-blue-600', !isInspecting);
      
      // 檢查模式下改變鼠標樣式
      document.body.style.cursor = isInspecting ? 'crosshair' : '';
      
      // 如果關閉檢查，隱藏信息面板
      if (!isInspecting) {
        infoPanel.style.display = 'none';
        
        // 移除所有臨時高亮
        const highlightedElements = document.querySelectorAll('.temp-highlight');
        highlightedElements.forEach(el => el.classList.remove('temp-highlight'));
      }
    });
    
    // 鼠標懸停事件
    document.addEventListener('mouseover', function(e) {
      if (!isInspecting) return;
      
      // 高亮當前元素
      e.target.classList.add('temp-highlight');
      
      // 生成元素信息
      const elementInfo = getElementInfo(e.target);
      
      // 顯示信息面板
      infoPanel.innerHTML = elementInfo;
      infoPanel.style.display = 'block';
    });
    
    // 鼠標移出事件
    document.addEventListener('mouseout', function(e) {
      if (!isInspecting) return;
      
      // 移除高亮
      e.target.classList.remove('temp-highlight');
    });
    
    // 點擊事件，記錄被點擊的元素
    document.addEventListener('click', function(e) {
      if (!isInspecting) return;
      
      // 阻止默認行為和事件冒泡
      e.preventDefault();
      e.stopPropagation();
      
      // 生成詳細的元素信息
      const detailedInfo = getDetailedElementInfo(e.target);
      
      // 更新信息面板
      infoPanel.innerHTML = detailedInfo;
      
      // 記錄到控制台
      console.group('元素檢查');
      console.log('檢查元素:', e.target);
      console.log('ID:', e.target.id);
      console.log('類名:', e.target.className);
      console.log('標籤名:', e.target.tagName);
      console.log('子元素數量:', e.target.children.length);
      console.log('顯示狀態:', window.getComputedStyle(e.target).display);
      console.log('可見性:', window.getComputedStyle(e.target).visibility);
      console.log('寬度:', window.getComputedStyle(e.target).width);
      console.log('高度:', window.getComputedStyle(e.target).height);
      console.groupEnd();
    });
    
    // 獲取元素基本信息
    function getElementInfo(element) {
      return `
        <div>
          <p><strong>元素:</strong> ${element.tagName.toLowerCase()}</p>
          <p><strong>ID:</strong> ${element.id || '無'}</p>
          <p><strong>類名:</strong> ${element.className || '無'}</p>
          <p><strong>顯示狀態:</strong> ${window.getComputedStyle(element).display}</p>
        </div>
      `;
    }
    
    // 獲取元素詳細信息
    function getDetailedElementInfo(element) {
      const styles = window.getComputedStyle(element);
      let attributes = '';
      for(let i = 0; i < element.attributes.length; i++) {
        const attr = element.attributes[i];
        attributes += `<li>${attr.name}="${attr.value}"</li>`;
      }
      
      return `
        <div>
          <h3 class="font-bold text-lg mb-2">元素詳情</h3>
          <p><strong>標籤:</strong> ${element.tagName.toLowerCase()}</p>
          <p><strong>ID:</strong> ${element.id || '無'}</p>
          <p><strong>類名:</strong> ${element.className || '無'}</p>
          <p><strong>子元素數量:</strong> ${element.children.length}</p>
          <p><strong>內部文字:</strong> ${element.textContent.slice(0, 50)}${element.textContent.length > 50 ? '...' : ''}</p>
          
          <h4 class="font-bold mt-3">樣式</h4>
          <p><strong>顯示:</strong> ${styles.display}</p>
          <p><strong>可見性:</strong> ${styles.visibility}</p>
          <p><strong>位置:</strong> ${styles.position}</p>
          <p><strong>尺寸:</strong> ${styles.width} x ${styles.height}</p>
          <p><strong>z-index:</strong> ${styles.zIndex}</p>
          
          <h4 class="font-bold mt-3">屬性</h4>
          <ul class="list-disc list-inside">
            ${attributes}
          </ul>
          
          <div class="mt-3 flex justify-between">
            <button id="highlight-btn" class="bg-yellow-500 text-white px-2 py-1 rounded text-xs">持續高亮</button>
            <button id="log-btn" class="bg-blue-500 text-white px-2 py-1 rounded text-xs">記錄到控制台</button>
          </div>
        </div>
      `;
    }
    
    // 添加高亮樣式
    const style = document.createElement('style');
    style.textContent = `
      .temp-highlight {
        outline: 2px dashed red !important;
        outline-offset: 2px !important;
        background-color: rgba(255, 0, 0, 0.1) !important;
      }
    `;
    document.head.appendChild(style);
    
    // 委托處理信息面板內的按鈕點擊
    infoPanel.addEventListener('click', function(e) {
      if (e.target.id === 'highlight-btn') {
        const highlightedElements = document.querySelectorAll('.temp-highlight');
        highlightedElements.forEach(el => {
          el.classList.add('persistent-highlight');
          el.style.outline = '3px solid orange';
          el.style.outlineOffset = '3px';
          el.style.backgroundColor = 'rgba(255, 165, 0, 0.2)';
        });
        
        // 提供還原操作
        const clearHighlightBtn = document.createElement('button');
        clearHighlightBtn.textContent = '清除所有高亮';
        clearHighlightBtn.classList.add('mt-3', 'bg-gray-500', 'text-white', 'px-2', 'py-1', 'rounded', 'text-xs', 'w-full');
        e.target.parentNode.appendChild(clearHighlightBtn);
        
        clearHighlightBtn.addEventListener('click', function() {
          const persistentHighlights = document.querySelectorAll('.persistent-highlight');
          persistentHighlights.forEach(el => {
            el.classList.remove('persistent-highlight');
            el.style.outline = '';
            el.style.outlineOffset = '';
            el.style.backgroundColor = '';
          });
          
          clearHighlightBtn.remove();
        });
      }
      else if (e.target.id === 'log-btn') {
        const highlightedElements = document.querySelectorAll('.temp-highlight');
        highlightedElements.forEach(el => {
          console.group('元素詳細信息');
          console.log(el);
          console.log('innerHTML:', el.innerHTML);
          console.log('outerHTML:', el.outerHTML);
          console.log('計算樣式:', window.getComputedStyle(el));
          console.log('位置:', el.getBoundingClientRect());
          console.groupEnd();
        });
      }
    });
    
  }, 1000);
});
