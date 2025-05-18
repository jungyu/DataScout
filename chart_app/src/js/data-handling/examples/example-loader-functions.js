/**
 * 載入範例檔案
 * @param {string} filename - 檔案名稱
 */
async function loadExampleFile(filename) {
    try {
        showLoading(true);
        
        // 獲取檔案資料
        const data = await fetchExampleData(filename);
        if (data) {
            // 獲取目前主題和圖表類型
            const chartTypeElement = document.getElementById('chartType');
            const chartThemeElement = document.getElementById('chartTheme');
            
            // 檢測檔案類型以自動選擇適合的圖表類型
            let chartType = chartTypeElement ? chartTypeElement.value : appState.currentChartType;
            
            // 使用輔助函數根據檔案名稱判斷最適合的圖表類型
            const detectedType = guessChartTypeFromFilename(filename);
            if (detectedType) {
                chartType = detectedType;
            }
            
            // 更新圖表類型選擇器（如果圖表類型有變）
            if (chartTypeElement && chartType !== chartTypeElement.value) {
                chartTypeElement.value = chartType;
                appState.currentChartType = chartType;
                console.log(`圖表類型已根據檔案名稱自動更新為: ${chartType}`);
            }
            
            const chartTheme = chartThemeElement ? chartThemeElement.value : appState.currentChartTheme;
            
            // 根據頁面主題同步圖表主題
            const effectiveTheme = syncChartThemeWithPageTheme(appState);
            
            // 渲染圖表
            createChart(data, chartType, effectiveTheme, appState);
            
            // 儲存目前檔案和類型
            appState.currentDataFile = filename;
            appState.currentDataType = 'json';
            
            // 更新範例檔案列表中的選中狀態
            updateExampleFileList();
            
            showSuccess(`已載入範例: ${filename}`);
        } else {
            showError('無法載入範例檔案');
        }
    } catch (error) {
        console.error('載入範例檔案錯誤：', error);
        showError('載入範例檔案時發生錯誤');
    } finally {
        showLoading(false);
    }
}
