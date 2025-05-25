// 範例資料 Toggle 功能
document.addEventListener('DOMContentLoaded', function() {
  // 等待一段時間確保DOM和其他腳本已載入
  setTimeout(function() {
    console.log('執行範例資料Toggle功能');
    
    // 獲取 Toggle 按鈕元素
    const toggleBtn = document.getElementById('example-data-toggle');
    
    // 檢測當前頁面的圖表類型
    const currentPath = window.location.pathname;
    let chartType = 'candlestick'; // 默認為蠟燭圖
    
    // 更精確的路徑檢測
    if (currentPath.endsWith('/') || currentPath.endsWith('/index.html')) {
      chartType = 'candlestick'; // 首頁是蠟燭圖
      console.log('[Toggle] 偵測到首頁，設定圖表類型為：蠟燭圖');
    } else if (currentPath.includes('/line')) {
      chartType = 'line';
      console.log('[Toggle] 偵測到路徑包含 line，設定圖表類型為：折線圖');
    } else if (currentPath.includes('/area')) {
      chartType = 'area';
      console.log('[Toggle] 偵測到路徑包含 area，設定圖表類型為：區域圖');
    } else if (currentPath.includes('/polararea')) {
      chartType = 'polarArea';
      console.log('[Toggle] 偵測到路徑包含 polararea，設定圖表類型為：極區圖');
    } else if (currentPath.includes('/column')) {
      chartType = 'column';
      console.log('[Toggle] 偵測到路徑包含 column，設定圖表類型為：柱狀圖');
    }
    
    // 查找檔案上傳區域
    const fileUploadSection = document.getElementById('file-upload-section');
    
    // 等待足夠時間確保 chart-data-loader.js 已處理完組件
    setTimeout(function() {
      // 根據圖表類型找到相應的數據區塊
      // 使用新的選擇器格式，透過 data-chart-type 屬性
      const dataSelector = document.getElementById('chart-data-selector-component');
      const chartDataSections = {};
      
      if (dataSelector) {
        // 在資料選擇器組件中找資料區塊
        chartDataSections[chartType] = dataSelector.querySelector(`.chart-data-block[data-chart-type="${chartType}"]`);
      } else {
        // 舊的方式，向下相容
        chartDataSections[chartType] = document.querySelector(`.${chartType}-chart-data`);
      }
      
      // 當前圖表類型的數據區塊
      const exampleDataSection = chartDataSections[chartType];
      console.log('[Toggle] 找到的數據區塊:', chartType, exampleDataSection ? '找到了' : '未找到');
      
      // 確保找到必要元素
      if (toggleBtn && fileUploadSection) {
        console.log('[Toggle] 找到切換按鈕和上傳區域');
        
        // 確保找到數據區塊
        if (exampleDataSection) {
          console.log('[Toggle] 找到數據區塊，設置處理邏輯');
          
          // 初始狀態
          let showExamples = toggleBtn.checked;
          
          // 初始更新顯示
          updateDisplay();
          
          // 監聽切換事件
          toggleBtn.addEventListener('change', function() {
            showExamples = toggleBtn.checked;
            updateDisplay();
            console.log('[Toggle] 範例資料顯示狀態切換為:', showExamples ? '顯示' : '隱藏');
          });
          
          // 更新顯示函數
          function updateDisplay() {
            // 移除重複的範例項目
            const exampleItems = document.querySelectorAll(`[data-chart-type="${chartType}"]`);
            const processedIds = new Set();
            
            exampleItems.forEach(item => {
              const id = item.id;
              if (id && processedIds.has(id)) {
                // 如果ID已經處理過，表示是重複項目，移除它
                item.remove();
                console.log('[Toggle] 移除重複項目:', id);
              } else if (id) {
                // 第一次遇到此ID，記錄下來
                processedIds.add(id);
              }
            });
            
            // 更新顯示狀態
            if (showExamples) {
              // 顯示範例資料
              exampleDataSection.style.display = 'block';
              fileUploadSection.style.display = 'none';
            } else {
              // 顯示檔案上傳區塊
              exampleDataSection.style.display = 'none';
              fileUploadSection.style.display = 'block';
            }
            
            console.log('[Toggle] 更新顯示狀態完成:', showExamples ? '顯示範例資料' : '顯示檔案上傳區塊');
          }
        } else {
          console.error('[Toggle] 找不到對應的數據區塊:', chartType);
        }
      } else {
        console.error('[Toggle] 找不到所需元素', {
          toggleBtn: !!toggleBtn,
          fileUploadSection: !!fileUploadSection
        });
      }
    }, 300); // 等待 300ms 確保其他腳本已處理完 DOM
  }, 500); // 等待 500ms 確保 DOM 完全載入
});
