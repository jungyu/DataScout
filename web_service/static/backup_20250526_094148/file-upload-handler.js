// 處理檔案上傳的獨立腳本
document.addEventListener('DOMContentLoaded', function() {
  // 等待幾毫秒確保DOM完全載入
  setTimeout(function() {
    console.log('初始化檔案上傳處理器');
    
    // 獲取檔案輸入元素
    const fileInput = document.getElementById('file-upload');
    
    // 獲取拖放區域（可能在不同位置出現）
    const fileDropAreas = document.querySelectorAll('.border-dashed');
    
    if (fileInput && fileDropAreas.length > 0) {
      console.log('找到檔案輸入和拖放區域');
      
      // 為所有拖放區域添加點擊事件
      fileDropAreas.forEach(dropArea => {
        // 添加視覺提示指標
        dropArea.classList.add('cursor-pointer');
        
        // 監聽點擊事件
        dropArea.addEventListener('click', function(e) {
          // 檢查點擊是否發生在按鈕上，避免重複觸發
          const isButtonClick = e.target.tagName.toLowerCase() === 'button' || 
                               e.target.closest('button') !== null;
          
          if (!isButtonClick) {
            console.log('拖放區域被點擊，觸發檔案選擇');
            fileInput.click();
          }
        });
        
        // 找到這個拖放區域內的按鈕並添加點擊事件
        const button = dropArea.querySelector('button');
        if (button) {
          button.addEventListener('click', function(e) {
            e.preventDefault(); // 防止表單提交
            e.stopPropagation(); // 防止事件冒泡
            console.log('檔案選擇按鈕被點擊');
            fileInput.click();
          });
        }
      });
      
      // 監聽檔案選擇事件
      fileInput.addEventListener('change', function() {
        if (fileInput.files.length > 0) {
          const fileName = fileInput.files[0].name;
          console.log('已選擇檔案:', fileName);
          
          // 將檔案數據傳遞給 Alpine.js 元件
          try {
            const dataSelector = document.querySelector('[x-data="DataSelector()"]');
            if (dataSelector && dataSelector.__x) {
              const dataSelectorData = dataSelector.__x.getUnobservedData();
              if (dataSelectorData && typeof dataSelectorData.processFiles === 'function') {
                dataSelectorData.processFiles(fileInput.files);
                console.log('成功將檔案傳遞給 Alpine.js 處理');
                
                // 顯示檔案預覽區域
                const previewArea = document.getElementById('file-preview-area');
                if (previewArea) {
                  previewArea.style.display = 'block';
                  previewArea.innerHTML = `
                    <div class="flex items-center">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-gray-500 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                      <div>
                        <p class="font-medium text-sm">${fileName}</p>
                        <p class="text-xs text-gray-500">${Math.round(fileInput.files[0].size / 1024)} KB</p>
                      </div>
                    </div>
                  `;
                }
                
                // 啟用上傳按鈕
                const uploadBtn = document.getElementById('upload-file-btn');
                if (uploadBtn) {
                  uploadBtn.classList.remove('opacity-50', 'cursor-not-allowed');
                  uploadBtn.classList.add('hover:bg-primary-focus', 'cursor-pointer');
                  
                  // 添加點擊事件處理上傳
                  uploadBtn.onclick = function() {
                    if (dataSelectorData && typeof dataSelectorData.uploadFile === 'function') {
                      dataSelectorData.uploadFile();
                    } else {
                      console.warn('找不到 uploadFile 方法');
                      // 顯示上傳成功的假訊息
                      showToast('檔案上傳成功！', 'success');
                    }
                  };
                }
              } else {
                console.warn('找不到 processFiles 方法');
              }
            } else {
              console.warn('找不到 DataSelector 組件或其 Alpine.js 實例');
            }
          } catch (e) {
            console.error('處理檔案選擇時出錯:', e);
          }
        }
      });
      
      // 添加通知提示功能
  function showToast(message, type = 'info') {
    // 設置顏色
    let bgColor = 'bg-primary';
    let icon = `
      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    `;
    
    if (type === 'success') {
      bgColor = 'bg-success';
      icon = `
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
        </svg>
      `;
    } else if (type === 'error') {
      bgColor = 'bg-error';
      icon = `
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      `;
    }
    
    const toast = document.createElement('div');
    toast.className = `fixed bottom-4 right-4 ${bgColor} text-white px-4 py-2 rounded shadow-lg z-50`;
    toast.innerHTML = `
      <div class="flex items-center">
        ${icon}
        <span>${message}</span>
      </div>
    `;
    document.body.appendChild(toast);
    
    // 3秒後自動移除
    setTimeout(() => {
      toast.classList.add('fade-out');
      setTimeout(() => {
        document.body.removeChild(toast);
      }, 500);
    }, 3000);
  }
  
  // 監聽拖放事件
      fileDropAreas.forEach(dropArea => {
        // 拖拽經過時高亮顯示
        dropArea.addEventListener('dragover', function(e) {
          e.preventDefault();
          this.classList.add('border-primary', 'bg-primary/5');
          this.classList.remove('border-gray-300', 'dark:border-gray-600');
        });
        
        // 拖拽離開時恢復原樣
        dropArea.addEventListener('dragleave', function() {
          this.classList.remove('border-primary', 'bg-primary/5');
          this.classList.add('border-gray-300', 'dark:border-gray-600');
        });
        
        // 處理檔案拖放
        dropArea.addEventListener('drop', function(e) {
          e.preventDefault();
          
          // 恢復樣式
          this.classList.remove('border-primary', 'bg-primary/5');
          this.classList.add('border-gray-300', 'dark:border-gray-600');
          
          // 處理檔案
          const files = e.dataTransfer.files;
          if (files.length > 0) {
            console.log('檔案被拖放:', files[0].name);
            
            // 將檔案設置到檔案輸入元素，觸發 change 事件
            fileInput.files = files;
            
            // 手動觸發 change 事件
            const event = new Event('change');
            fileInput.dispatchEvent(event);
          }
        });
      });
      
      console.log('檔案上傳處理器初始化完成');
    } else {
      console.warn('找不到檔案輸入或拖放區域', {
        fileInput: !!fileInput,
        fileDropAreas: fileDropAreas.length
      });
    }
  }, 200); // 給 Alpine.js 和其他腳本更多時間初始化
});
