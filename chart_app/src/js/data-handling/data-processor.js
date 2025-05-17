/**
 * 資料處理模組
 * 負責資料驗證、轉換和格式化
 */

import { showError } from '../utils/utils.js';

/**
 * 驗證 JSON 資料是否符合 Chart.js 標準格式
 * @param {Object} data - 要驗證的數據
 * @returns {Object} - 包含驗證結果和錯誤訊息
 */
export function validateChartJsFormat(data) {
    const result = {
        isValid: true,
        errors: []
    };
    
    // 檢查是否為物件
    if (!data || typeof data !== 'object') {
        result.isValid = false;
        result.errors.push('資料必須是一個有效的 JSON 物件');
        return result;
    }
    
    // 檢查是否有 datasets 陣列
    if (!Array.isArray(data.datasets)) {
        result.isValid = false;
        result.errors.push('資料必須包含 datasets 陣列');
        return result;
    }
    
    // 檢查 datasets 是否為空
    if (data.datasets.length === 0) {
        result.isValid = false;
        result.errors.push('datasets 陣列不能為空');
        return result;
    }
    
    // 檢查每個 dataset
    const datasetErrors = [];
    data.datasets.forEach((dataset, index) => {
        if (!Array.isArray(dataset.data)) {
            datasetErrors.push(`數據集 ${index + 1} 必須包含 data 陣列`);
        }
    });
    
    if (datasetErrors.length > 0) {
        result.isValid = false;
        result.errors = [...result.errors, ...datasetErrors];
    }
    
    return result;
}

/**
 * 將各種格式的資料轉換為標準 Chart.js 格式
 * @param {Object} data - 原始資料
 * @param {string} format - 資料格式 ('json', 'csv', 'excel')
 * @returns {Object} - 標準格式的資料
 */
export function convertToChartJsFormat(data, format = 'json') {
    try {
        // 如果已經是標準格式，直接返回
        const validation = validateChartJsFormat(data);
        if (validation.isValid) {
            return data;
        }
        
        // 根據不同格式進行轉換
        switch (format.toLowerCase()) {
            case 'json':
                return convertJsonData(data);
                
            case 'csv':
                return convertCsvData(data);
                
            case 'excel':
                return convertExcelData(data);
                
            default:
                throw new Error(`不支援的資料格式: ${format}`);
        }
    } catch (error) {
        console.error('轉換資料格式時發生錯誤:', error);
        showError(`無法轉換資料格式: ${error.message}`);
        
        // 返回最小有效的資料結構
        return {
            labels: [],
            datasets: [{
                label: '無效資料',
                data: []
            }]
        };
    }
}

/**
 * 轉換 JSON 格式資料
 * @param {Object} data - JSON 資料
 * @returns {Object} - Chart.js 格式資料
 */
function convertJsonData(data) {
    // 如果是陣列，假設是資料點陣列
    if (Array.isArray(data)) {
        // 檢查是否為物件陣列
        if (data.length > 0 && typeof data[0] === 'object') {
            return convertObjectArrayData(data);
        }
        
        // 單一數值陣列
        return {
            labels: data.map((_, index) => `項目 ${index + 1}`),
            datasets: [{
                label: '資料系列',
                data: data
            }]
        };
    }
    
    // 已經有 labels 和 datasets 結構，但格式可能不完全符合
    if (data.labels && data.datasets) {
        return {
            labels: data.labels,
            datasets: data.datasets.map(dataset => ({
                label: dataset.label || '未命名資料系列',
                data: dataset.data || [],
                backgroundColor: dataset.backgroundColor || 'rgba(75, 192, 192, 0.2)',
                borderColor: dataset.borderColor || 'rgba(75, 192, 192, 1)',
                borderWidth: dataset.borderWidth || 1
            }))
        };
    }
    
    // 其他 JSON 結構
    if (data && typeof data === 'object') {
        // 將物件轉為 labels (鍵) 和 data (值)
        const keys = Object.keys(data);
        const values = Object.values(data);
        
        return {
            labels: keys,
            datasets: [{
                label: '資料系列',
                data: values
            }]
        };
    }
    
    throw new Error('無法識別的 JSON 資料格式');
}

/**
 * 將物件陣列轉換為 Chart.js 格式
 * @param {Array} data - 物件陣列
 * @returns {Object} - Chart.js 格式資料
 */
function convertObjectArrayData(data) {
    // 獲取第一個物件的所有鍵
    const firstItem = data[0];
    const keys = Object.keys(firstItem);
    
    // 尋找可能的標籤欄位
    let labelField = null;
    ['name', 'label', 'category', 'x', 'id'].forEach(field => {
        if (!labelField && keys.includes(field)) {
            labelField = field;
        }
    });
    
    // 尋找可能的資料欄位
    let dataFields = keys.filter(key => {
        return key !== labelField &&
               typeof firstItem[key] === 'number';
    });
    
    // 如果沒有可識別的資料欄位，使用除了標籤欄位外的所有欄位
    if (dataFields.length === 0) {
        dataFields = keys.filter(key => key !== labelField);
    }
    
    // 建立標籤
    const labels = labelField ? data.map(item => item[labelField]) : data.map((_, i) => `項目 ${i + 1}`);
    
    // 建立資料集
    const datasets = dataFields.map(field => {
        const fieldData = data.map(item => item[field]);
        return {
            label: field,
            data: fieldData
        };
    });
    
    return {
        labels,
        datasets
    };
}

/**
 * 轉換 CSV 格式資料
 * @param {Array} data - CSV 資料 (已解析為二維陣列)
 * @returns {Object} - Chart.js 格式資料
 */
function convertCsvData(data) {
    if (!Array.isArray(data) || data.length === 0) {
        throw new Error('無效的 CSV 資料');
    }
    
    // 假設第一行是標題
    const headers = data[0];
    const rows = data.slice(1);
    
    // 第一列作為標籤
    const labels = rows.map(row => row[0]);
    
    // 其他列作為數據系列
    const datasets = [];
    for (let i = 1; i < headers.length; i++) {
        const datasetData = rows.map(row => {
            // 嘗試轉換為數字
            const value = row[i];
            if (!isNaN(value) && value !== '') {
                return Number(value);
            }
            return null;
        });
        
        datasets.push({
            label: headers[i] || `資料系列 ${i}`,
            data: datasetData
        });
    }
    
    return {
        labels,
        datasets
    };
}

/**
 * 轉換 Excel 格式資料
 * @param {Object} data - Excel 資料 (已解析為結構化物件)
 * @returns {Object} - Chart.js 格式資料
 */
function convertExcelData(data) {
    // Excel 資料結構可能已經類似 CSV 的二維陣列
    if (Array.isArray(data)) {
        return convertCsvData(data);
    }
    
    // 或者已經解析為帶有工作表和單元格的對象
    if (data.sheets && data.activeSheet) {
        const activeSheet = data.sheets[data.activeSheet];
        
        // 轉換為二維陣列格式
        const headers = activeSheet.headers || [];
        const rows = activeSheet.rows || [];
        
        // 建立 CSV 格式，然後轉換
        const csvData = [headers, ...rows];
        return convertCsvData(csvData);
    }
    
    throw new Error('不支援的 Excel 資料格式');
}

/**
 * 補充缺失的圖表資訊
 * @param {Object} data - 圖表資料
 * @param {string} chartType - 圖表類型
 * @returns {Object} - 補充後的資料
 */
export function enrichChartData(data, chartType) {
    // 深拷貝，避免修改原始資料
    const enrichedData = JSON.parse(JSON.stringify(data));
    
    // 確保基本結構存在
    if (!enrichedData.labels) {
        enrichedData.labels = Array(10).fill(0).map((_, i) => `項目 ${i + 1}`);
    }
    
    if (!enrichedData.datasets || !Array.isArray(enrichedData.datasets)) {
        enrichedData.datasets = [{
            label: '資料系列',
            data: Array(10).fill(0).map(() => Math.floor(Math.random() * 100))
        }];
    }
    
    // 為每個資料集添加樣式
    const colorPalette = [
        { bg: 'rgba(255, 99, 132, 0.2)', border: 'rgba(255, 99, 132, 1)' },
        { bg: 'rgba(54, 162, 235, 0.2)', border: 'rgba(54, 162, 235, 1)' },
        { bg: 'rgba(255, 206, 86, 0.2)', border: 'rgba(255, 206, 86, 1)' },
        { bg: 'rgba(75, 192, 192, 0.2)', border: 'rgba(75, 192, 192, 1)' },
        { bg: 'rgba(153, 102, 255, 0.2)', border: 'rgba(153, 102, 255, 1)' },
        { bg: 'rgba(255, 159, 64, 0.2)', border: 'rgba(255, 159, 64, 1)' }
    ];
    
    enrichedData.datasets.forEach((dataset, index) => {
        const colorIndex = index % colorPalette.length;
        const color = colorPalette[colorIndex];
        
        // 如果沒有標籤，添加默認標籤
        if (!dataset.label) {
            dataset.label = `資料系列 ${index + 1}`;
        }
        
        // 根據圖表類型設定樣式
        if (['pie', 'doughnut', 'polarArea'].includes(chartType)) {
            // 這些圖表類型需要一組背景顏色
            if (!dataset.backgroundColor || !Array.isArray(dataset.backgroundColor)) {
                dataset.backgroundColor = Array(dataset.data.length).fill(0)
                    .map((_, i) => colorPalette[i % colorPalette.length].bg);
            }
        } else {
            // 線形圖表可以使用單一顏色
            if (!dataset.backgroundColor) {
                dataset.backgroundColor = color.bg;
            }
            
            if (!dataset.borderColor) {
                dataset.borderColor = color.border;
            }
            
            // 為折線圖設定線寬
            if (chartType === 'line' && !dataset.borderWidth) {
                dataset.borderWidth = 2;
            }
        }
    });
    
    return enrichedData;
}
