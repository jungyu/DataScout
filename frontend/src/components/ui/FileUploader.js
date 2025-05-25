// filepath: /Users/aaron/Downloads/Techwind_v3.0.0/HTML/Dashboard/frontend/src/components/ui/FileUploader.js
// DataScout 檔案上傳元件
export const FileUploader = () => {
  return {
    showExamples: true,
    dragActive: false,
    selectedFile: null,
    fileError: '',
    allowedExtensions: ['csv', 'json', 'xlsx', 'xls'],
    
    init() {
      // 確保範例資料的 Toggle 按鈕初始化為開啟狀態
      this.showExamples = true;
      console.log('FileUploader initialized with showExamples:', this.showExamples);
      
      // 檢查是否有URL參數控制顯示
      const urlParams = new URLSearchParams(window.location.search);
      if (urlParams.has('examples') && urlParams.get('examples') === 'false') {
        this.showExamples = false;
      }
    },
    
    toggleExamples() {
      this.showExamples = !this.showExamples;
      console.log('切換範例資料狀態:', this.showExamples);
      
      // 同步更新 Toggle 按鈕狀態並觸發 change 事件
      const toggleBtn = document.getElementById('example-data-toggle');
      if (toggleBtn) {
        toggleBtn.checked = this.showExamples;
        // 觸發 change 事件，讓 example-toggle.js 中的事件監聽器能夠響應
        const event = new Event('change');
        toggleBtn.dispatchEvent(event);
        console.log('已觸發 Toggle 按鈕的 change 事件');
      }
      
      // 明確更新 UI，確保切換後立即顯示正確的區塊 (備用方案)
      setTimeout(() => {
        console.log('延遲檢查 - 顯示範例資料:', this.showExamples);
        
        // 主頁面元素
        const mainExampleSection = document.getElementById('example-data-section');
        const mainFileUploadSection = document.getElementById('file-upload-section');
        
        // Alpine 組件元素
        const dataSelectorEl = document.querySelector('[x-data="DataSelector()"]');
        const alpineExampleSection = dataSelectorEl ? dataSelectorEl.querySelector('#example-data-section') : null;
        const alpineFileUploadSection = dataSelectorEl ? dataSelectorEl.querySelector('#file-upload-section') : null;
        
        // 更新所有相關元素的顯示狀態
        const updateElement = (el, show) => {
          if (el) el.style.display = show ? 'block' : 'none';
        };
        
        // 更新主頁面和 Alpine 組件元素
        updateElement(mainExampleSection, this.showExamples);
        updateElement(mainFileUploadSection, !this.showExamples);
        updateElement(alpineExampleSection, this.showExamples);
        updateElement(alpineFileUploadSection, !this.showExamples);
        
        console.log('手動更新了所有 DOM 顯示狀態');
      }, 50);
      
      // 切換到上傳區域時清除之前的檔案狀態
      if (!this.showExamples) {
        this.selectedFile = null;
        this.fileError = '';
      }
    },
    
    handleDragOver(e) {
      e.preventDefault();
      this.dragActive = true;
    },
    
    handleDragLeave() {
      this.dragActive = false;
    },
    
    handleDrop(e) {
      e.preventDefault();
      this.dragActive = false;
      this.processFiles(e.dataTransfer.files);
    },
    
    handleFileSelect(e) {
      this.processFiles(e.target.files);
    },
    
    processFiles(files) {
      if (files.length > 0) {
        const file = files[0];
        const extension = file.name.split('.').pop().toLowerCase();
        
        if (this.allowedExtensions.includes(extension)) {
          this.selectedFile = file;
          this.fileError = '';
          // 自動顯示檔案預覽
          this.previewFile();
        } else {
          this.selectedFile = null;
          this.fileError = '只接受 CSV, JSON 或 Excel 檔案';
        }
      }
    },
    
    // 取得檔案類型
    getFileType(file) {
      const extension = file.name.split('.').pop().toLowerCase();
      if (['csv'].includes(extension)) return 'csv';
      if (['json'].includes(extension)) return 'json';
      if (['xlsx', 'xls'].includes(extension)) return 'excel';
      return 'unknown';
    },
    
    // 預覽檔案內容
    previewFile() {
      if (!this.selectedFile) return;
      
      const fileType = this.getFileType(this.selectedFile);
      console.log('預覽檔案:', this.selectedFile.name, '類型:', fileType);
      
      // 建立讀取器
      const reader = new FileReader();
      
      // 設定完成讀取後的處理
      reader.onload = (event) => {
        let previewData = null;
        let previewError = null;
        
        try {
          // 根據檔案類型處理預覽
          if (fileType === 'csv') {
            // 簡單解析 CSV (完整解析需要使用專用庫)
            const lines = event.target.result.split('\n');
            const headers = lines[0].split(',');
            const sampleRow = lines.length > 1 ? lines[1].split(',') : [];
            
            previewData = {
              headers: headers,
              sampleRow: sampleRow,
              rowCount: lines.length - 1
            };
          } else if (fileType === 'json') {
            // 解析 JSON
            const jsonData = JSON.parse(event.target.result);
            previewData = {
              structure: Array.isArray(jsonData) ? '陣列' : '物件',
              sampleKeys: Array.isArray(jsonData) && jsonData.length > 0 
                ? Object.keys(jsonData[0]).slice(0, 5) 
                : Object.keys(jsonData).slice(0, 5),
              itemCount: Array.isArray(jsonData) ? jsonData.length : '非陣列結構'
            };
          } else if (fileType === 'excel') {
            // Excel 檔案需要專門的庫處理，這裡只顯示基本資訊
            previewData = {
              fileSize: Math.round(this.selectedFile.size / 1024) + ' KB',
              note: 'Excel 檔案需要額外處理，上傳後將自動解析'
            };
          }
          
          // 顯示預覽資訊
          this.showFilePreview(fileType, previewData);
          
        } catch (error) {
          console.error('檔案預覽錯誤:', error);
          previewError = '檔案格式錯誤或無法讀取';
          this.showFilePreview(fileType, null, previewError);
        }
      };
      
      // 根據檔案類型讀取內容
      if (fileType === 'json' || fileType === 'csv') {
        reader.readAsText(this.selectedFile);
      } else {
        // 對於 Excel 文件，只讀取為二進制數據但不做進一步處理
        reader.readAsArrayBuffer(this.selectedFile);
        this.showFilePreview(fileType, {
          fileSize: Math.round(this.selectedFile.size / 1024) + ' KB',
          note: 'Excel 檔案需要額外處理，上傳後將自動解析'
        });
      }
    },
    
    // 顯示檔案預覽區域
    showFilePreview(fileType, previewData, error) {
      // 查找預覽區域
      let previewArea = document.querySelector('#file-preview-area');
      
      // 如果不存在則建立
      if (!previewArea) {
        previewArea = document.createElement('div');
        previewArea.id = 'file-preview-area';
        previewArea.className = 'mt-4 p-3 bg-gray-50 dark:bg-slate-800 rounded-md';
        
        // 添加到檔案上傳區域後面
        const uploadSection = document.querySelector('#file-upload-section');
        if (uploadSection) {
          uploadSection.appendChild(previewArea);
        }
      }
      
      // 如果有錯誤，顯示錯誤訊息
      if (error) {
        previewArea.innerHTML = `
          <div class="text-error text-sm p-2 bg-error/10 rounded-md">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 inline mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            ${error}
          </div>
        `;
        return;
      }
      
      // 根據檔案類型生成不同預覽內容
      let previewContent = '';
      
      if (fileType === 'csv' && previewData) {
        previewContent = `
          <h3 class="font-medium text-sm mb-2">CSV 檔案預覽</h3>
          <div class="overflow-x-auto">
            <table class="table table-compact w-full">
              <thead>
                <tr>
                  ${previewData.headers.slice(0, 5).map(header => `<th class="text-xs">${header}</th>`).join('')}
                </tr>
              </thead>
              <tbody>
                <tr>
                  ${previewData.sampleRow.slice(0, 5).map(cell => `<td class="text-xs">${cell}</td>`).join('')}
                </tr>
                <tr>
                  <td colspan="${Math.min(previewData.headers.length, 5)}" class="text-xs text-gray-500">總計約 ${previewData.rowCount} 筆資料</td>
                </tr>
              </tbody>
            </table>
          </div>
        `;
      } else if (fileType === 'json' && previewData) {
        previewContent = `
          <h3 class="font-medium text-sm mb-2">JSON 檔案預覽</h3>
          <div class="text-xs">
            <p>結構: ${previewData.structure}</p>
            <p>欄位: ${previewData.sampleKeys.join(', ')}</p>
            <p>資料數: ${previewData.itemCount}</p>
          </div>
        `;
      } else if (fileType === 'excel' && previewData) {
        previewContent = `
          <h3 class="font-medium text-sm mb-2">Excel 檔案資訊</h3>
          <div class="text-xs">
            <p>檔案大小: ${previewData.fileSize}</p>
            <p>${previewData.note}</p>
          </div>
        `;
      }
      
      // 設置預覽內容
      previewArea.innerHTML = previewContent;
    },
    
    uploadFile() {
      if (this.selectedFile) {
        // 這裡處理檔案上傳邏輯
        console.log('正在上傳檔案:', this.selectedFile);
        
        // 顯示上傳中狀態
        const uploadButton = document.querySelector('#file-upload-section button');
        if (uploadButton) {
          uploadButton.innerHTML = `
            <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            上傳中...
          `;
          uploadButton.disabled = true;
        }
        
        // 模擬上傳處理
        const formData = new FormData();
        formData.append('file', this.selectedFile);
        
        // 模擬 API 請求延遲
        setTimeout(() => {
          // 解析檔案
          this.parseFileData();
          
          // 復原上傳按鈕狀態
          if (uploadButton) {
            uploadButton.innerHTML = '上傳檔案';
            uploadButton.disabled = false;
          }
          
          // 顯示成功訊息
          this.showUploadSuccess();
        }, 1500);
      }
    },
    
    // 解析檔案數據並存入全局狀態
    parseFileData() {
      const fileType = this.getFileType(this.selectedFile);
      const reader = new FileReader();
      
      reader.onload = (event) => {
        try {
          let parsedData = null;
          
          if (fileType === 'csv') {
            // 簡單解析 CSV (僅供演示，實際應用需用專門庫)
            const lines = event.target.result.split('\n');
            const headers = lines[0].split(',');
            
            parsedData = [];
            for (let i = 1; i < lines.length; i++) {
              if (!lines[i].trim()) continue;
              
              const values = lines[i].split(',');
              const row = {};
              
              headers.forEach((header, index) => {
                row[header.trim()] = values[index]?.trim() || '';
              });
              
              parsedData.push(row);
            }
          } else if (fileType === 'json') {
            parsedData = JSON.parse(event.target.result);
          }
          
          // 存入全局狀態
          if (parsedData) {
            window.appData = window.appData || {};
            window.appData.currentDataset = {
              type: 'custom',
              name: this.selectedFile.name,
              data: parsedData
            };
            
            // 觸發資料載入事件
            window.dispatchEvent(new CustomEvent('data-loaded', { 
              detail: { datasetType: 'custom', source: 'file' } 
            }));
          }
        } catch (error) {
          console.error('檔案解析錯誤:', error);
          // 顯示錯誤訊息
          this.showUploadError('檔案格式錯誤或無法解析');
        }
      };
      
      if (fileType === 'csv' || fileType === 'json') {
        reader.readAsText(this.selectedFile);
      }
      // Excel 檔案處理會在實際應用中使用專門的庫
    },
    
    // 顯示上傳成功訊息
    showUploadSuccess() {
      // 創建一個成功通知
      const toast = document.createElement('div');
      toast.className = 'fixed bottom-4 right-4 bg-success text-white px-4 py-2 rounded shadow-lg z-50 animate-fade-in';
      toast.innerHTML = `
        <div class="flex items-center">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
          <span>檔案「${this.selectedFile.name}」已成功上傳並處理</span>
        </div>
      `;
      document.body.appendChild(toast);
      
      // 3秒後自動移除
      setTimeout(() => {
        toast.classList.add('animate-fade-out');
        setTimeout(() => {
          document.body.removeChild(toast);
        }, 500);
      }, 3000);
    },
    
    // 顯示上傳錯誤訊息
    showUploadError(message) {
      // 創建一個錯誤通知
      const toast = document.createElement('div');
      toast.className = 'fixed bottom-4 right-4 bg-error text-white px-4 py-2 rounded shadow-lg z-50 animate-fade-in';
      toast.innerHTML = `
        <div class="flex items-center">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
          <span>${message || '上傳處理失敗，請檢查檔案格式'}</span>
        </div>
      `;
      document.body.appendChild(toast);
      
      // 3秒後自動移除
      setTimeout(() => {
        toast.classList.add('animate-fade-out');
        setTimeout(() => {
          document.body.removeChild(toast);
        }, 500);
      }, 3000);
    }
  }
}
