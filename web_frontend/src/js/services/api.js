/**
 * API 服務
 * 
 * 負責處理與後端 FastAPI 服務的所有通信
 */

export const apiService = {
  /**
   * 基本 API 路徑
   */
  baseUrl: '/api',
  
  /**
   * 通用請求函數
   * @param {string} endpoint - API 端點
   * @param {Object} options - 請求選項
   * @returns {Promise<any>}
   */
  async request(endpoint, options = {}) {
    try {
      const url = `${this.baseUrl}/${endpoint.replace(/^\//, '')}`;
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers
        }
      });
      
      if (!response.ok) {
        throw new Error(`API 請求失敗: ${response.status} ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('API 請求錯誤:', error);
      throw error;
    }
  },
  
  /**
   * 獲取儀表板數據
   * @returns {Promise<Object>}
   */
  getDashboardData() {
    return this.request('chart-data');
  },
  
  /**
   * 獲取可用的數據文件
   * @returns {Promise<Array>}
   */
  getDataFiles() {
    return this.request('data-files');
  },
  
  /**
   * 獲取特定文件的數據
   * @param {string} filename - 文件名稱
   * @returns {Promise<Object>}
   */
  getFileData(filename) {
    return this.request(`file-data?filename=${encodeURIComponent(filename)}`);
  },
  
  /**
   * 獲取原始文件內容
   * @param {string} filename - 文件名稱
   * @returns {Promise<Object>}
   */
  getFileContent(filename) {
    return this.request(`file-content?filename=${encodeURIComponent(filename)}`);
  },
  
  /**
   * 執行 OLAP 操作
   * @param {Object} data - OLAP 操作數據
   * @returns {Promise<Object>}
   */
  executeOlap(data) {
    return this.request('olap-operation', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },
  
  /**
   * 從 JSON 數據生成圖表
   * @param {Object} data - 圖表數據
   * @returns {Promise<Object>}
   */
  chartFromJson(data) {
    return this.request('chart-from-json', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },
  
  /**
   * 上傳圖表截圖
   * @param {string} imageDataUrl - 圖表圖片的 Data URL
   * @param {string} chartName - 圖表名稱
   * @returns {Promise<Object>}
   */
  uploadChartImage(imageDataUrl, chartName) {
    const formData = new FormData();
    // 將 Data URL 轉換為 Blob
    const blobData = this.dataURLtoBlob(imageDataUrl);
    formData.append('file', blobData, `${chartName}.png`);
    
    return this.request('upload-chart-image', {
      method: 'POST',
      body: formData,
      headers: {} // 讓瀏覽器自動設置 multipart/form-data
    });
  },
  
  /**
   * 將 Data URL 轉換為 Blob
   * @param {string} dataURL - Data URL 字符串
   * @returns {Blob}
   */
  dataURLtoBlob(dataURL) {
    const parts = dataURL.split(';base64,');
    const contentType = parts[0].split(':')[1];
    const raw = window.atob(parts[1]);
    const rawLength = raw.length;
    const uInt8Array = new Uint8Array(rawLength);
    
    for (let i = 0; i < rawLength; ++i) {
      uInt8Array[i] = raw.charCodeAt(i);
    }
    
    return new Blob([uInt8Array], { type: contentType });
  }
};
