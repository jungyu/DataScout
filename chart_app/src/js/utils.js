/**
 * 獲取檔案資料
 * @param {string} filename - 檔案名稱
 * @param {string} type - 檔案類型 (json, csv, excel)
 * @returns {Promise<Object>} - 檔案資料
 */
export async function fetchFileData(filename, type) {
    try {
        console.log(`fetchFileData: 開始獲取檔案 ${filename}，類型 ${type}`);
        
        // 改進：判斷是否為上傳的檔案
        const isUploadedFile = filename.includes('uploads/') || filename.startsWith('uploads_');
        
        // 構建查詢參數
        const params = new URLSearchParams();
        params.append('filename', filename);
        params.append('type', type);
        if (isUploadedFile) {
            params.append('is_upload', 'true');
        }
        
        // 建立 URL
        const url = `/api/file-data/?${params.toString()}`;
        console.log(`請求資料的完整 URL: ${url}`);
        
        // 發送請求
        const response = await fetch(url);
        
        // 檢查響應
        if (!response.ok) {
            console.error(`獲取檔案資料失敗: ${response.status} ${response.statusText}`);
            
            // 嘗試讀取錯誤訊息
            try {
                const errorData = await response.json();
                throw new Error(errorData.detail || `伺服器響應錯誤: ${response.status}`);
            } catch (jsonError) {
                throw new Error(`HTTP 錯誤: ${response.status}`);
            }
        }
        
        // 解析響應
        const data = await response.json();
        console.log('fetchFileData: 成功獲取資料', data);
        return data;
    } catch (error) {
        console.error(`獲取檔案資料時發生錯誤: ${error.message}`, error);
        throw error;
    }
}

/**
 * 顯示錯誤訊息
 * @param {string} message - 錯誤訊息
 * @param {boolean} isDetailedLog - 是否詳細記錄錯誤 
 */
export function showError(message, isDetailedLog = false) {
    console.error('錯誤:', message);
    
    if (isDetailedLog) {
        console.trace('錯誤詳細堆疊:');
    }
    
    const errorMessage = document.getElementById('errorMessage');
    
    if (errorMessage) {
        // 設置錯誤訊息內容
        errorMessage.textContent = message;
        
        // 顯示錯誤訊息
        errorMessage.classList.remove('hidden');
        
        // 5秒後自動隱藏
        setTimeout(() => {
            errorMessage.classList.add('hidden');
        }, 5000);
    } else {
        // 如果找不到錯誤訊息元素，嘗試創建一個臨時錯誤提示
        const tempErrorDiv = document.createElement('div');
        tempErrorDiv.className = 'error-message fixed top-4 right-4 bg-red-500 text-white px-4 py-2 rounded shadow-lg z-50';
        tempErrorDiv.textContent = `錯誤: ${message}`;
        document.body.appendChild(tempErrorDiv);
        
        // 5秒後移除
        setTimeout(() => {
            document.body.removeChild(tempErrorDiv);
        }, 5000);
    }
}

/**
 * 顯示成功訊息
 * @param {string} message - 成功訊息
 */
export function showSuccess(message) {
    console.log('成功:', message);
    const successMessage = document.getElementById('successMessage');
    
    if (successMessage) {
        // 設置成功訊息內容
        successMessage.textContent = message;
        
        // 顯示成功訊息
        successMessage.classList.remove('hidden');
        
        // 3秒後自動隱藏
        setTimeout(() => {
            successMessage.classList.add('hidden');
        }, 3000);
    }
}

/**
 * 顯示或隱藏載入指示器
 * @param {boolean} isLoading - 是否正在載入
 */
export function showLoading(isLoading) {
    const loadingStatus = document.getElementById('loadingStatus');
    if (loadingStatus) {
        if (isLoading) {
            loadingStatus.classList.remove('hidden');
            // 當顯示載入提示時，隱藏圖表訊息
            hideChartMessage();
        } else {
            loadingStatus.classList.add('hidden');
        }
    }
}

/**
 * 顯示圖表訊息提示
 */
export function showChartMessage() {
    const chartMessage = document.getElementById('chartMessage');
    if (chartMessage) {
        chartMessage.classList.remove('hidden');
    }
}

/**
 * 隱藏圖表訊息提示
 */
export function hideChartMessage() {
    const chartMessage = document.getElementById('chartMessage');
    if (chartMessage) {
        chartMessage.classList.add('hidden');
    }
}

/**
 * 獲取所有可用的資料檔案
 * @returns {Promise<Object>} 所有檔案列表的索引
 */
export async function fetchAllDataFiles() {
    try {
        const response = await fetch('/api/data-files/');
        if (response.ok) {
            const data = await response.json();
            // API返回嵌套結構，獲取data_files屬性
            if (data && data.data_files) {
                return data.data_files;
            } else {
                console.warn('API返回了意外的資料結構:', data);
                return {};
            }
        } else {
            console.error('獲取檔案列表失敗');
            return {};
        }
    } catch (error) {
        console.error('獲取檔案列表錯誤：', error);
        return {};
    }
}
