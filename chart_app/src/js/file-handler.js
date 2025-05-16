/**
 * 檔案處理模組 - 負責管理範例檔案和上傳檔案
 */
import { fetchAllDataFiles, fetchFileData, showError, showSuccess, showLoading } from './utils.js';

/**
 * 根據檔案名稱猜測適合的圖表類型
 * @param {string} filename - 檔案名稱
 * @returns {string} - 圖表類型
 */
export function guessChartTypeFromFilename(filename) {
    if (!filename) return 'line';
    
    if (filename.includes('_bar_')) return 'bar';
    if (filename.includes('_line_')) return 'line';
    if (filename.includes('_pie_')) return 'pie';
    if (filename.includes('_doughnut_')) return 'doughnut';
    if (filename.includes('_radar_')) return 'radar';
    if (filename.includes('_scatter_')) return 'scatter';
    if (filename.includes('_bubble_')) return 'bubble';
    if (filename.includes('_candlestick_')) return 'candlestick';
    if (filename.includes('_ohlc_')) return 'ohlc';
    if (filename.includes('_polarArea_') || filename.includes('_polar_area_')) return 'polarArea';
    if (filename.includes('_mixed_')) return 'mixed';
    if (filename.includes('_sankey_')) return 'sankey';
    
    return 'line'; // 預設為折線圖
}

/**
 * 獲取特定圖表類型的所有範例檔案
 * @param {object} appState - 應用狀態
 * @param {string} chartType - 圖表類型
 * @returns {Array<string>} - 匹配的範例檔案名稱列表
 */
export function getExampleFilesForChartType(appState, chartType) {
    if (!appState.availableDataFiles || !appState.availableDataFiles.json) return [];
    
    const exampleFiles = appState.availableDataFiles.json.filter(file => file.includes('example_'));
    
    if (!chartType) return exampleFiles;
    
    return exampleFiles.filter(filename => filename.includes(`example_${chartType}_`));
}

/**
 * 獲取所有範例檔案，按圖表類型分類
 * @param {object} appState - 應用狀態
 * @returns {object} - 按圖表類型分類的範例檔案
 */
export function getCategorizedExampleFiles(appState) {
    if (!appState.availableDataFiles || !appState.availableDataFiles.json) return {};
    
    const exampleFiles = appState.availableDataFiles.json.filter(file => file.includes('example_'));
    
    const categorized = {
        'bar': exampleFiles.filter(file => file.includes('example_bar_')),
        'line': exampleFiles.filter(file => file.includes('example_line_')),
        'pie': exampleFiles.filter(file => file.includes('example_pie_')),
        'doughnut': exampleFiles.filter(file => file.includes('example_doughnut_')),
        'radar': exampleFiles.filter(file => file.includes('example_radar_')),
        'scatter': exampleFiles.filter(file => file.includes('example_scatter_')),
        'bubble': exampleFiles.filter(file => file.includes('example_bubble_')),
        'candlestick': exampleFiles.filter(file => file.includes('example_candlestick_')),
        'ohlc': exampleFiles.filter(file => file.includes('example_ohlc_')),
        'polarArea': exampleFiles.filter(file => 
            file.includes('example_polarArea_') || file.includes('example_polar_area_')),
        'mixed': exampleFiles.filter(file => file.includes('example_mixed_'))
    };
    
    return categorized;
}

/**
 * 刷新可用檔案列表
 * @param {object} appState - 應用狀態
 * @returns {Promise<boolean>} - 是否成功刷新
 */
export async function refreshAvailableFiles(appState) {
    try {
        const files = await fetchAllDataFiles();
        if (files) {
            appState.availableDataFiles = files;
            return true;
        }
        return false;
    } catch (error) {
        console.error('刷新檔案列表錯誤：', error);
        return false;
    }
}

/**
 * 載入檔案內容
 * @param {string} filename - 檔案名稱
 * @param {string} fileType - 檔案類型
 * @returns {Promise<object>} - 檔案內容
 */
export async function loadFile(filename, fileType) {
    try {
        showLoading(true);
        const data = await fetchFileData(filename, fileType);
        if (data) {
            return data;
        } else {
            showError(`無法載入檔案: ${filename}`);
            return null;
        }
    } catch (error) {
        console.error('載入檔案錯誤：', error);
        showError('載入檔案時發生錯誤');
        return null;
    } finally {
        showLoading(false);
    }
}
