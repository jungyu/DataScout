/**
 * 更新範例檔案列表
 * @returns {Promise<void>}
 */
async function updateExampleFileList() {
    const exampleFileList = document.getElementById('exampleFileList');
    if (!exampleFileList) return;
    
    // 清空現有列表並顯示加載中
    exampleFileList.innerHTML = '';
    const loadingMsg = document.createElement('p');
    loadingMsg.textContent = '載入範例檔案中...';
    loadingMsg.className = 'text-sm text-gray-500 p-2 text-center';
    exampleFileList.appendChild(loadingMsg);
    
    try {
        // 使用新的 API 獲取範例檔案
        const exampleData = await fetchAvailableExamples();
        
        // 清空加載訊息
        exampleFileList.innerHTML = '';
        
        // 從 ui-controller.js 導入新的範例列表更新函數
        const uiController = await import('./core/ui-controller.js');
        if (exampleData && exampleData.examples) {
            uiController.updateExampleFileList(exampleData.examples);
        } else {
            uiController.updateExampleFileList([]);
        }
    } catch (error) {
        console.error('獲取範例文件列表時發生錯誤:', error);
        exampleFileList.innerHTML = '';
        const errorMsg = document.createElement('p');
        errorMsg.textContent = '載入範例檔案列表時發生錯誤';
        errorMsg.className = 'text-sm text-red-500 p-2 text-center';
        exampleFileList.appendChild(errorMsg);
    }
}
