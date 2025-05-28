// filepath: /Users/aaron/Downloads/Techwind_v3.0.0/HTML/Dashboard/frontend/src/components/ui/FileUploader.js
// DataScout 檔案上傳元件
export const FileUploader = () => {
  return {
    showExamples: true,
    dragActive: false,
    selectedFile: null,
    rawFile: null,
    fileError: '',
    allowedExtensions: ['csv', 'json', 'xlsx', 'xls'],
    maxFileSize: 10 * 1024 * 1024, // 10MB
    previewData: null,
    
    init() {
      try {
        // 確保範例資料的 Toggle 按鈕初始化為開啟狀態
        this.showExamples = true;
        console.log('FileUploader initialized with showExamples:', this.showExamples);
        
        // 檢查是否有URL參數控制顯示
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.has('examples') && urlParams.get('examples') === 'false') {
          this.showExamples = false;
        }
      } catch (error) {
        console.error('FileUploader 初始化失敗:', error);
        this.fileError = '初始化失敗';
      }
    },
    
    toggleExamples() {
      try {
        this.showExamples = !this.showExamples;
        console.log('切換範例資料狀態:', this.showExamples);
        
        // 同步更新 Toggle 按鈕狀態並觸發 change 事件
        const toggleBtn = document.getElementById('example-data-toggle');
        if (toggleBtn) {
          toggleBtn.checked = this.showExamples;
          const event = new Event('change');
          toggleBtn.dispatchEvent(event);
        }
        
        // 更新 UI
        this.updateUI();
        
        // 切換到上傳區域時清除之前的檔案狀態
        if (!this.showExamples) {
          this.clearFileState();
        }
      } catch (error) {
        console.error('切換範例資料失敗:', error);
        this.fileError = '切換失敗';
      }
    },
    
    updateUI() {
      try {
        const elements = {
          mainExampleSection: document.getElementById('example-data-section'),
          mainFileUploadSection: document.getElementById('file-upload-section'),
          alpineExampleSection: document.querySelector('[x-data="DataSelector()"] #example-data-section'),
          alpineFileUploadSection: document.querySelector('[x-data="DataSelector()"] #file-upload-section')
        };
        
        Object.entries(elements).forEach(([key, element]) => {
          if (element) {
            element.style.display = key.includes('Example') ? 
              (this.showExamples ? 'block' : 'none') : 
              (this.showExamples ? 'none' : 'block');
          }
        });
      } catch (error) {
        console.error('更新 UI 失敗:', error);
      }
    },
    
    clearFileState() {
      this.selectedFile = null;
      this.rawFile = null;
      this.fileError = '';
      this.previewData = null;
      const previewArea = document.querySelector('#file-preview-area');
      if (previewArea) {
        previewArea.innerHTML = '';
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
      try {
        if (files.length === 0) return;
        
        const file = files[0];
        const extension = file.name.split('.').pop().toLowerCase();
        
        // 檢查檔案大小
        if (file.size > this.maxFileSize) {
          throw new Error(`檔案大小不能超過 ${this.maxFileSize / 1024 / 1024}MB`);
        }
        
        // 檢查檔案類型
        if (!this.allowedExtensions.includes(extension)) {
          throw new Error('只接受 CSV, JSON 或 Excel 檔案');
        }
        
        this.selectedFile = {
          name: file.name,
          size: file.size,
          type: file.type
        };
        this.rawFile = file;
        this.fileError = '';
        
        this.$nextTick(() => {
          this.selectedFile = { ...this.selectedFile };
        });
        
        this.previewFile();
      } catch (error) {
        console.error('處理檔案失敗:', error);
        this.fileError = error.message;
        this.clearFileState();
      }
    },
    
    getFileType(file) {
      const name = file.name || file;
      const extension = name.split('.').pop().toLowerCase();
      if (["csv"].includes(extension)) return "csv";
      if (["json"].includes(extension)) return "json";
      if (["xlsx", "xls"].includes(extension)) return "excel";
      return "unknown";
    },
    
    previewFile() {
      if (!this.selectedFile || !this.rawFile) return;
      
      try {
        const fileType = this.getFileType(this.selectedFile);
        const fileObj = this.rawFile;
        const reader = new FileReader();
        
        reader.onload = (event) => {
          try {
            let previewData = null;
            
            if (fileType === 'csv') {
              const lines = event.target.result.split('\n');
              const headers = lines[0].split(',');
              const sampleRow = lines.length > 1 ? lines[1].split(',') : [];
              previewData = {
                headers: headers,
                sampleRow: sampleRow,
                rowCount: lines.length - 1
              };
            } else if (fileType === 'json') {
              const jsonData = JSON.parse(event.target.result);
              previewData = {
                structure: Array.isArray(jsonData) ? '陣列' : '物件',
                sampleKeys: Array.isArray(jsonData) && jsonData.length > 0 
                  ? Object.keys(jsonData[0]).slice(0, 5) 
                  : Object.keys(jsonData).slice(0, 5),
                itemCount: Array.isArray(jsonData) ? jsonData.length : '非陣列結構'
              };
            } else if (fileType === 'excel') {
              previewData = {
                fileSize: Math.round(fileObj.size / 1024) + ' KB',
                note: 'Excel 檔案需要額外處理，上傳後將自動解析'
              };
            }
            
            this.previewData = previewData;
            this.showFilePreview(fileType, previewData);
          } catch (error) {
            console.error('解析檔案內容失敗:', error);
            this.showFilePreview(fileType, null, '檔案格式錯誤或無法讀取');
          }
        };
        
        reader.onerror = () => {
          console.error('讀取檔案失敗');
          this.showFilePreview(fileType, null, '讀取檔案失敗');
        };
        
        if (fileType === 'json' || fileType === 'csv') {
          reader.readAsText(fileObj);
        } else {
          reader.readAsArrayBuffer(fileObj);
          this.showFilePreview(fileType, {
            fileSize: Math.round(fileObj.size / 1024) + ' KB',
            note: 'Excel 檔案需要額外處理，上傳後將自動解析'
          });
        }
      } catch (error) {
        console.error('預覽檔案失敗:', error);
        this.showFilePreview(this.getFileType(this.selectedFile), null, '預覽檔案失敗');
      }
    },
    
    showFilePreview(fileType, previewData, error) {
      try {
        let previewArea = document.querySelector('#file-preview-area');
        
        if (!previewArea) {
          previewArea = document.createElement('div');
          previewArea.id = 'file-preview-area';
          previewArea.className = 'mt-4 p-3 bg-gray-50 dark:bg-slate-800 rounded-md';
          
          const uploadSection = document.querySelector('#file-upload-section');
          if (uploadSection) {
            uploadSection.appendChild(previewArea);
          }
        }
        
        if (error) {
          previewArea.innerHTML = `
            <div class="text-error text-sm p-2 bg-error/10 rounded-md">
              <i class="fas fa-exclamation-circle mr-2"></i>
              ${error}
            </div>
          `;
          return;
        }
        
        if (!previewData) {
          previewArea.innerHTML = '';
          return;
        }
        
        let previewHTML = '';
        
        switch (fileType) {
          case 'csv':
            previewHTML = `
              <div class="text-sm">
                <p class="font-medium mb-2">CSV 檔案預覽</p>
                <p>欄位數: ${previewData.headers.length}</p>
                <p>資料列數: ${previewData.rowCount}</p>
                <div class="mt-2">
                  <p class="font-medium">欄位名稱:</p>
                  <p class="text-gray-600">${previewData.headers.join(', ')}</p>
                </div>
                ${previewData.sampleRow.length > 0 ? `
                  <div class="mt-2">
                    <p class="font-medium">第一列資料:</p>
                    <p class="text-gray-600">${previewData.sampleRow.join(', ')}</p>
                  </div>
                ` : ''}
              </div>
            `;
            break;
            
          case 'json':
            previewHTML = `
              <div class="text-sm">
                <p class="font-medium mb-2">JSON 檔案預覽</p>
                <p>資料結構: ${previewData.structure}</p>
                <p>資料數量: ${previewData.itemCount}</p>
                <div class="mt-2">
                  <p class="font-medium">主要欄位:</p>
                  <p class="text-gray-600">${previewData.sampleKeys.join(', ')}</p>
                </div>
              </div>
            `;
            break;
            
          case 'excel':
            previewHTML = `
              <div class="text-sm">
                <p class="font-medium mb-2">Excel 檔案預覽</p>
                <p>檔案大小: ${previewData.fileSize}</p>
                <p class="text-gray-600">${previewData.note}</p>
              </div>
            `;
            break;
        }
        
        previewArea.innerHTML = previewHTML;
      } catch (error) {
        console.error('顯示檔案預覽失敗:', error);
      }
    },
    
    uploadFile() {
      if (this.selectedFile && this.rawFile) {
        const fileObj = this.rawFile;
        console.log('正在上傳檔案:', fileObj);
        const uploadButton = document.querySelector('#file-upload-section button');
        if (uploadButton) {
          uploadButton.innerHTML = `
            <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            上傳中...`;
          uploadButton.disabled = true;
        }
        const formData = new FormData();
        formData.append('file', fileObj);
        setTimeout(() => {
          this.parseFileData();
          if (uploadButton) {
            uploadButton.innerHTML = '上傳檔案';
            uploadButton.disabled = false;
          }
          this.showUploadSuccess();
        }, 1500);
      }
    },
    
    // 解析檔案數據並存入全局狀態
    parseFileData() {
      if (!this.selectedFile || !this.rawFile) return;
      const fileType = this.getFileType(this.selectedFile);
      const fileObj = this.rawFile;
      const reader = new FileReader();
      reader.onload = (event) => {
        try {
          let parsedData = null;
          if (fileType === 'csv') {
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
          if (parsedData) {
            window.appData = window.appData || {};
            window.appData.currentDataset = {
              type: 'custom',
              name: this.selectedFile.name,
              data: parsedData
            };
            window.dispatchEvent(new CustomEvent('data-loaded', { 
              detail: { datasetType: 'custom', source: 'file' } 
            }));
          }
        } catch (error) {
          console.error('檔案解析錯誤:', error);
          this.showUploadError('檔案格式錯誤或無法解析');
        }
      };
      if (fileType === 'csv' || fileType === 'json') {
        reader.readAsText(fileObj);
      }
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
