/**
 * Chart.js JSON 資料驗證處理模組
 * 用於將標準 JSON 資料格式轉換為 Chart.js 所需的格式
 */

/**
 * 檢查 JSON 資料是否符合 Chart.js 格式要求
 * @param {Object} data - JSON 資料
 * @returns {Object} 包含驗證結果和錯誤訊息的物件
 */
export function validateChartJsJSON(data) {
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
    if (!data.data || !Array.isArray(data.data.datasets) || data.data.datasets.length === 0) {
        result.isValid = false;
        result.errors.push('資料必須包含非空的 datasets 陣列');
        return result;
    }
    
    // 檢查 type 是否為有效的圖表類型 (如果提供)
    const validChartTypes = ['line', 'bar', 'pie', 'radar', 'doughnut', 'polarArea', 'scatter', 'bubble', 'ohlc', 'candlestick', 'sankey'];
    if (data.type && !validChartTypes.includes(data.type)) {
        result.isValid = false;
        result.errors.push(`未知的圖表類型: ${data.type}. 有效的類型: ${validChartTypes.join(', ')}`);
    }
    
    // 檢查每個數據集是否有 data 屬性
    for (let i = 0; i < data.data.datasets.length; i++) {
        const dataset = data.data.datasets[i];
        
        if (!dataset.data) {
            result.isValid = false;
            result.errors.push(`數據集 #${i + 1} 缺少 'data' 屬性`);
            continue;
        }
        
        if (!Array.isArray(dataset.data)) {
            result.isValid = false;
            result.errors.push(`數據集 #${i + 1} 的 'data' 必須是一個陣列`);
        }
    }
    
    // 檢查散點圖或氣泡圖的特殊格式
    if (data.type === 'scatter' || data.type === 'bubble') {
        for (let i = 0; i < data.data.datasets.length; i++) {
            const dataset = data.data.datasets[i];
            
            if (Array.isArray(dataset.data)) {
                for (let j = 0; j < dataset.data.length; j++) {
                    const point = dataset.data[j];
                    
                    if (typeof point !== 'object' || point === null) {
                        result.isValid = false;
                        result.errors.push(`數據集 #${i + 1} 的 'data[${j}]' 必須是一個物件`);
                        continue;
                    }
                    
                    if (typeof point.x === 'undefined' || typeof point.y === 'undefined') {
                        result.isValid = false;
                        result.errors.push(`數據集 #${i + 1} 的 'data[${j}]' 必須包含 'x' 和 'y' 屬性`);
                    }
                    
                    if (data.type === 'bubble' && typeof point.r === 'undefined') {
                        result.isValid = false;
                        result.errors.push(`氣泡圖的數據集 #${i + 1} 的 'data[${j}]' 必須包含 'r' 屬性（氣泡半徑）`);
                    }
                }
            }
        }
    }
    
    return result;
}

/**
 * 處理 JSON 資料，確保符合 Chart.js 格式要求
 * @param {Object} data - 輸入的 JSON 資料
 * @returns {Object} 處理後的 Chart.js 格式資料
 */
export function processChartJsJSON(data) {
    // 首先驗證資料格式
    const validation = validateChartJsJSON(data);
    if (!validation.isValid) {
        console.error('JSON 資料格式無效:', validation.errors);
        // 返回一個基本的有效圖表資料，避免應用程式崩潰
        return {
            data: {
                labels: ['錯誤'],
                datasets: [{
                    label: '無效資料',
                    data: [0],
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1
                }]
            },
            title: '錯誤: ' + validation.errors.join('; ')
        };
    }
    
    return data;
}
