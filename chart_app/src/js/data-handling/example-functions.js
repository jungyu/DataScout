import { showError, showSuccess, showLoading } from '../utils/utils.js';
import { fetchExampleData, fetchAvailableExamples } from './example-loader.js';
import { createChart } from '../core/chart-manager.js';
import { syncChartThemeWithPageTheme } from '../utils/theme-handler.js';
import { updateExampleFileList } from '../core/ui-controller.js';
import { getAppState } from '../core/state-manager.js';
import { guessChartTypeFromFilename } from '../utils/chart-type-guesser.js';

/**
 * 載入範例檔案
 * @param {string} filename - 檔案名稱
 */
export async function loadExampleFile(filename) {
    try {
        showLoading(true);
        
        // 獲取應用程式狀態
        const appState = getAppState();
        
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

/**
 * 根據圖表類型載入範例資料
 * @param {string} chartType - 圖表類型
 * @param {Object} appState - 應用程式狀態
 * @returns {Promise<boolean>} - 是否成功載入
 */
export async function loadExampleDataForChartType(chartType, appState) {
    try {
        showLoading(true);
        console.log(`開始載入 ${chartType} 類型的範例資料`);
        
        // 獲取該類型的所有範例
        const examples = await fetchAvailableExamples(chartType);
        
        if (!examples || !examples.examples || examples.examples.length === 0) {
            console.warn(`沒有找到 ${chartType} 類型的範例`);
            showError(`沒有找到 ${chartType} 類型的範例`);
            return false;
        }
        
        // 選擇第一個範例
        const firstExample = examples.examples[0];
        console.log(`選擇範例: ${firstExample.filename}`);
        
        // 載入範例資料
        const data = await fetchExampleData(firstExample.filename);
        
        if (!data) {
            console.error('無法載入範例資料');
            showError('無法載入範例資料');
            return false;
        }
        
        // 更新應用程式狀態
        appState.currentChartType = chartType;
        appState.currentDataFile = firstExample.filename;
        appState.currentDataType = 'json';
        
        // 根據頁面主題同步圖表主題
        const effectiveTheme = syncChartThemeWithPageTheme(appState);
        
        // 渲染圖表
        const chart = createChart(data, chartType, effectiveTheme, appState);
        
        if (chart) {
            console.log('範例圖表渲染成功');
            showSuccess(`已載入 ${chartType} 範例`);
            return true;
        } else {
            console.warn('範例圖表可能未成功渲染');
            showError('範例圖表渲染失敗');
            return false;
        }
    } catch (error) {
        console.error('載入範例資料時發生錯誤:', error);
        showError(`載入範例資料時發生錯誤: ${error.message}`);
        return false;
    } finally {
        showLoading(false);
    }
}
