
/**
 * 顯示錯誤訊息
 * @param {string} message - 錯誤訊息
 */
export function showError(message) {
    console.error(message);
    
    // 獲取錯誤訊息容器
    const errorMessage = document.getElementById('errorMessage');
    if (errorMessage) {
        errorMessage.textContent = message;
        errorMessage.classList.remove('hidden');
        
        // 淡入效果
        errorMessage.style.opacity = '0';
        setTimeout(() => {
            errorMessage.style.opacity = '1';
        }, 10);
        
        // 3 秒後自動隱藏錯誤訊息
        setTimeout(() => {
            errorMessage.style.opacity = '0';
            setTimeout(() => {
                errorMessage.classList.add('hidden');
            }, 300);
        }, 3000);
    }
}

/**
 * 顯示成功訊息
 * @param {string} message - 成功訊息
 */
export function showSuccess(message) {
    console.log(message);
    
    // 獲取成功訊息容器
    const successMessage = document.getElementById('successMessage');
    if (successMessage) {
        successMessage.textContent = message;
        successMessage.classList.remove('hidden');
        
        // 淡入效果
        successMessage.style.opacity = '0';
        setTimeout(() => {
            successMessage.style.opacity = '1';
        }, 10);
        
        // 3 秒後自動隱藏成功訊息
        setTimeout(() => {
            successMessage.style.opacity = '0';
            setTimeout(() => {
                successMessage.classList.add('hidden');
            }, 300);
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
        } else {
            loadingStatus.classList.add('hidden');
        }
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

/**
 * 根據檔案類型獲取檔案
 * @param {string} filename - 檔案名稱
 * @param {string} type - 檔案類型 (csv, json, excel)
 * @returns {Promise<Object>} - 解析後的資料
 */
export async function fetchFileData(filename, type = 'json') {
    try {
        // 使用新的API端點
        const apiEndpoint = `/api/file-data/?filename=${encodeURIComponent(filename)}&file_type=${type}`;
        console.log(`正在從 ${apiEndpoint} 獲取資料...`);
        
        const response = await fetch(apiEndpoint);
        if (response.ok) {
            const contentType = response.headers.get("content-type");
            
            if (contentType && contentType.indexOf("application/json") !== -1) {
                const data = await response.json();
                return data;
            } else {
                showError('伺服器回應非 JSON 格式');
                return null;
            }
        } else {
            // 嘗試讀取錯誤訊息
            let errorMessage = `獲取檔案資料失敗: ${response.status} ${response.statusText}`;
            try {
                const errorData = await response.json();
                if (errorData && errorData.error) {
                    errorMessage = errorData.error;
                }
            } catch (e) {
                console.warn('無法解析錯誤訊息:', e);
            }
            
            showError(errorMessage);
            return null;
        }
    } catch (error) {
        console.error('獲取檔案資料錯誤：', error);
        showError('獲取檔案資料時發生錯誤');
        return null;
    }
}
