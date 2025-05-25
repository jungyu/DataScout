/**
 * 資料選擇器調試控制面板
 * 提供即時診斷和修復工具
 */

document.addEventListener('DOMContentLoaded', function() {
  // 等待頁面完全載入
  setTimeout(function() {
    // 建立控制面板容器
    const panel = document.createElement('div');
    panel.className = 'debug-control-panel';
    panel.style.display = 'none'; // 初始隱藏
    
    // 添加標題
    const title = document.createElement('h3');
    title.textContent = '調試控制面板';
    title.style.margin = '0 0 10px 0';
    title.style.fontSize = '14px';
    title.style.fontWeight = 'bold';
    panel.appendChild(title);
    
    // 添加狀態顯示
    const status = document.createElement('div');
    status.id = 'debug-status';
    status.style.marginBottom = '10px';
    status.style.fontSize = '12px';
    status.style.padding = '5px';
    status.style.backgroundColor = 'rgba(0, 0, 0, 0.2)';
    status.style.borderRadius = '3px';
    panel.appendChild(status);
    
    // 添加按鈕組
    const buttonGroup = document.createElement('div');
    panel.appendChild(buttonGroup);
    
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
    
    updateStatus(`當前頁面：${currentPath}<br>圖表類型：${chartType}`);
    
    // 建立按鈕
    const buttons = [
      {
        text: '檢測問題',
        action: detectIssues
      },
      {
        text: '修復資料選擇器',
        action: fixDataSelector
      },
      {
        text: '顯示隱藏元素',
        action: toggleHiddenElements
      },
      {
        text: '重載選擇器組件',
        action: reloadDataSelector
      },
      {
        text: '關閉面板',
        action: function() {
          panel.style.display = 'none';
        }
      }
    ];
    
    // 添加按鈕到面板
    buttons.forEach(btn => {
      const button = document.createElement('button');
      button.textContent = btn.text;
      button.addEventListener('click', btn.action);
      buttonGroup.appendChild(button);
    });
    
    // 添加控制面板到頁面
    document.body.appendChild(panel);
    
    // 創建一個懸浮按鈕來顯示/隱藏面板
    const toggleButton = document.createElement('button');
    toggleButton.textContent = '🛠️ 調試';
    toggleButton.style.position = 'fixed';
    toggleButton.style.top = '10px';
    toggleButton.style.left = '10px';
    toggleButton.style.zIndex = '9999';
    toggleButton.style.background = '#4CAF50';
    toggleButton.style.color = 'white';
    toggleButton.style.border = 'none';
    toggleButton.style.borderRadius = '5px';
    toggleButton.style.padding = '5px 10px';
    toggleButton.style.cursor = 'pointer';
    toggleButton.style.fontSize = '12px';
    
    toggleButton.addEventListener('click', function() {
      panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
    });
    
    document.body.appendChild(toggleButton);
    
    // 更新狀態函數
    function updateStatus(message) {
      const statusEl = document.getElementById('debug-status');
      if (statusEl) {
        statusEl.innerHTML = message;
      }
    }
    
    // 檢測問題函數
    function detectIssues() {
      updateStatus('正在檢測問題...');
      
      // 檢查資料選擇器是否存在
      const dataSelector = document.getElementById('chart-data-selector-component');
      if (!dataSelector) {
        updateStatus('❌ 找不到資料選擇器元素！');
        return;
      }
      
      // 檢查圖表數據區塊是否存在
      const dataBlocks = dataSelector.querySelectorAll('.chart-data-block');
      if (dataBlocks.length === 0) {
        updateStatus('⚠️ 找不到任何數據區塊元素！');
        return;
      }
      
      // 檢查當前圖表類型的數據區塊是否可見
      const currentBlock = dataSelector.querySelector(`.chart-data-block[data-chart-type="${chartType}"]`);
      if (!currentBlock) {
        updateStatus(`⚠️ 找不到 ${chartType} 類型的數據區塊！`);
        return;
      }
      
      const isVisible = window.getComputedStyle(currentBlock).display !== 'none';
      if (!isVisible) {
        updateStatus(`❌ ${chartType} 類型的數據區塊被隱藏了！`);
        return;
      }
      
      // 檢查其他類型的數據區塊是否都被隱藏
      let otherBlocksHidden = true;
      dataBlocks.forEach(block => {
        const blockType = block.getAttribute('data-chart-type');
        if (blockType !== chartType && window.getComputedStyle(block).display !== 'none') {
          otherBlocksHidden = false;
        }
      });
      
      if (!otherBlocksHidden) {
        updateStatus('⚠️ 有非當前圖表類型的數據區塊未被隱藏！');
        return;
      }
      
      // 一切正常
      updateStatus('✅ 資料選擇器工作正常！');
    }
    
    // 修復資料選擇器函數
    function fixDataSelector() {
      updateStatus('正在修復資料選擇器...');
      
      // 找到資料選擇器元素
      const dataSelector = document.getElementById('chart-data-selector-component');
      if (!dataSelector) {
        updateStatus('❌ 找不到資料選擇器元素，無法修復！');
        return;
      }
      
      try {
        // 檢測當前頁面的圖表類型
        const currentPath = window.location.pathname;
        let chartType = 'candlestick'; // 默認為蠟燭圖
        
        // 更精確地檢測頁面類型
        if (currentPath.endsWith('/') || currentPath.endsWith('/index.html')) {
          chartType = 'candlestick';
        } else if (currentPath.endsWith('line.html')) {
          chartType = 'line';
        } else if (currentPath.endsWith('area.html')) {
          chartType = 'area';
        } else if (currentPath.endsWith('column.html')) {
          chartType = 'column';
        }
        
        updateStatus(`檢測到頁面類型: ${chartType} (路徑: ${currentPath})`);
        
        // 確保所有區塊都有正確的數據屬性
        const dataBlocks = dataSelector.querySelectorAll('.line-chart-data, .area-chart-data, .column-chart-data, .candlestick-chart-data');
        dataBlocks.forEach(block => {
          // 從類名中提取圖表類型
          const className = Array.from(block.classList).find(cls => cls.endsWith('-chart-data'));
          if (className && !block.hasAttribute('data-chart-type')) {
            const type = className.replace('-chart-data', '');
            block.setAttribute('data-chart-type', type);
          }
          
          // 添加統一的圖表數據區塊類名
          if (!block.classList.contains('chart-data-block')) {
            block.classList.add('chart-data-block');
          }
          
          // 移除任何內聯 display 樣式
          block.style.removeProperty('display');
        });
        
        // 重設所有數據區塊的顯示狀態
        const allDataBlocks = dataSelector.querySelectorAll('.chart-data-block');
        updateStatus(`找到 ${allDataBlocks.length} 個數據區塊，設置顯示狀態...`);
        
        allDataBlocks.forEach(block => {
          const blockType = block.getAttribute('data-chart-type');
          const shouldShow = blockType === chartType;
          
          // 移除可能影響顯示的內聯樣式
          block.removeAttribute('style');
          // 然後設置新的顯示狀態
          block.style.setProperty('display', shouldShow ? 'block' : 'none', 'important');
          
          updateStatus(`${blockType} 類型區塊 (${block.id || '無ID'}) 顯示狀態設為: ${shouldShow ? '顯示' : '隱藏'}`);
        });
        
        // 特別處理面積圖的區塊，確保它在 area.html 頁面中顯示
        if (currentPath.endsWith('area.html')) {
          const areaBlock = dataSelector.querySelector('#area-chart-data');
          if (areaBlock) {
            areaBlock.style.setProperty('display', 'block', 'important');
            updateStatus('✅ 特別處理：確保面積圖數據區塊可見');
            
            // 確保區塊內的子元素也是可見的
            const areaItems = areaBlock.querySelectorAll('.bg-base-200');
            areaItems.forEach(item => {
              item.style.removeProperty('display');
            });
          } else {
            updateStatus('⚠️ 找不到面積圖數據區塊 (#area-chart-data)');
          }
        }
        
        // 確保上傳區域的顯示狀態正確
        const toggleBtn = dataSelector.querySelector('#example-data-toggle');
        const uploadSection = dataSelector.querySelector('#file-upload-section');
        if (toggleBtn && uploadSection) {
          uploadSection.style.setProperty('display', toggleBtn.checked ? 'none' : 'block', 'important');
        }
        
        // 更新狀態
        updateStatus('✅ 資料選擇器已修復！');
        
        // 添加特殊視覺標記
        dataSelector.style.animation = 'none';
        setTimeout(() => {
          dataSelector.style.animation = 'pulse-blue 2s infinite';
        }, 10);
      } catch (error) {
        updateStatus(`❌ 修復過程中出錯：${error.message}`);
      }
    }
    
    // 顯示隱藏元素函數
    function toggleHiddenElements() {
      const body = document.body;
      if (body.classList.contains('debug-show-hidden')) {
        body.classList.remove('debug-show-hidden');
        updateStatus('已關閉隱藏元素顯示');
      } else {
        body.classList.add('debug-show-hidden');
        updateStatus('⚠️ 顯示隱藏元素模式已啟用（半透明紅色邊框的元素）');
      }
    }
    
    // 重載資料選擇器組件
    function reloadDataSelector() {
      updateStatus('正在重載資料選擇器組件...');
      
      // 找到資料選擇器容器
      const selectorContainer = document.querySelector('[data-component="components/ui/ChartDataSelector.html"]');
      if (!selectorContainer) {
        updateStatus('❌ 找不到資料選擇器容器！');
        return;
      }
      
      // 重新載入組件
      fetch('components/ui/ChartDataSelector.html')
        .then(response => {
          if (!response.ok) {
            throw new Error('Failed to load component');
          }
          return response.text();
        })
        .then(html => {
          selectorContainer.innerHTML = html;
          
          // 觸發組件載入完成事件
          const event = new CustomEvent('component-loaded', { 
            detail: { 
              container: selectorContainer,
              componentPath: 'components/ui/ChartDataSelector.html'
            }
          });
          document.dispatchEvent(event);
          
          // 延遲檢測
          setTimeout(detectIssues, 500);
          
          updateStatus('✅ 資料選擇器組件已重載！');
        })
        .catch(error => {
          updateStatus(`❌ 重載失敗：${error.message}`);
        });
    }
  }, 1000);
});
