# 手動修復步驟

## 1. main.js 修改

在 main.js 的導入部分添加以下代碼行：

```javascript
import { fetchAvailableExamples } from './data-handling/examples/index.js';
import { updateExampleFileList as updateUIExampleFileList } from './core/ui-controller.js';
```

## 2. 修復 main.js 中的更新範例函數

替換 main.js 中的 `updateExampleFileList` 函數：

```javascript
/**
 * 更新範例檔案列表
 * @returns {Promise<void>}
 */
async function updateExampleFileList() {
    try {
        // 使用新的 API 獲取範例檔案
        const exampleData = await fetchAvailableExamples();
        
        // 使用從 ui-controller.js 直接導入的函數
        if (exampleData && exampleData.examples) {
            updateUIExampleFileList(exampleData.examples);
        } else {
            updateUIExampleFileList([]);
        }
    } catch (error) {
        console.error('獲取範例文件列表時發生錯誤:', error);
        showError('載入範例檔案列表時發生錯誤');
    }
}
```

## 3. 解決 ui-controller.js 中的函數重複定義問題

在 ui-controller.js 中找到兩個 `updateExampleFileList` 函數定義，將第一個更名為 `updateLegacyExampleFileList`：

```javascript
/**
 * 更新舊版範例檔案列表 (舊版實作，保留用於相容)
 */
function updateLegacyExampleFileList() {
    // 原有函數內容不變
}
```

## 4. 確保 ui-controller.js 包含範例文件列表更新函數

確認 ui-controller.js 中新增了以下函數：

```javascript
/**
 * 更新範例檔案列表
 * @param {Array<string>} exampleFiles - 範例檔案陣列
 */
export function updateExampleFileList(exampleFiles = []) {
    console.log('更新範例檔案列表', exampleFiles);
    const exampleFileList = document.getElementById('exampleFileList');
    if (!exampleFileList) return;
    
    // 清空現有列表
    exampleFileList.innerHTML = '';
    
    try {
        // 當前選中的圖表類型
        const appState = getAppState();
        const currentChartType = appState.currentChartType || 'line';
        
        // 如果沒有範例檔案
        if (!exampleFiles || exampleFiles.length === 0) {
            const noFilesMsg = document.createElement('p');
            noFilesMsg.textContent = '沒有可用的範例檔案';
            noFilesMsg.className = 'text-sm text-gray-500 p-2 text-center';
            exampleFileList.appendChild(noFilesMsg);
            return;
        }
        
        // 略...
    } catch (error) {
        console.error('更新範例檔案列表錯誤:', error);
        const errorMsg = document.createElement('p');
        errorMsg.textContent = '載入範例檔案列表時發生錯誤';
        errorMsg.className = 'text-sm text-red-500 p-2 text-center';
        exampleFileList.appendChild(errorMsg);
    }
}
```

## 3. main.js 中的 updateExampleFileList 函數修改

將 main.js 中的 `updateExampleFileList` 函數替換為：

```javascript
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
```
