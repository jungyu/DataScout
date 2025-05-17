import { showError, showLoading, showSuccess } from '../utils/utils.js';

/**
 * 上傳圖表到伺服器
 * @param {object} appState - 應用狀態
 */
export async function uploadChart(appState) {
    if (!appState.myChart) {
        showError('無圖表可供上傳');
        return;
    }
    
    try {
        showLoading(true);
        
        // 獲取圖表的 base64 編碼的資料 URL
        const dataURL = appState.myChart.toBase64Image();
        
        // 將 base64 資料發送到伺服器
        const response = await fetch('/api/upload_chart', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                chart_data: dataURL,
                chart_type: appState.currentChartType
            })
        });
        
        if (response.ok) {
            const result = await response.json();
            console.log('上傳成功:', result);
            showSuccess('圖表已成功上傳');
        } else {
            const errorData = await response.json();
            showError(`上傳失敗: ${errorData.message || '未知錯誤'}`);
        }
    } catch (error) {
        console.error('上傳圖表錯誤:', error);
        showError('上傳圖表時發生錯誤');
    } finally {
        showLoading(false);
    }
}

/**
 * 將資料匯出為 CSV 檔案
 * @param {object} appState - 應用狀態
 */
export function exportDataToCSV(appState) {
    if (!appState.myChart || !appState.myChart.data) {
        showError('無資料可供匯出');
        return;
    }
    
    try {
        const chartData = appState.myChart.data;
        let csvContent = 'data:text/csv;charset=utf-8,';
        
        // 添加標頭行
        const headers = ['categories'];
        chartData.datasets.forEach(dataset => {
            headers.push(dataset.label || 'Series');
        });
        
        csvContent += headers.join(',') + '\n';
        
        // 添加資料行
        chartData.labels.forEach((label, i) => {
            const row = [label];
            chartData.datasets.forEach(dataset => {
                row.push(dataset.data[i] || '');
            });
            csvContent += row.join(',') + '\n';
        });
        
        // 創建一個下載連結
        const encodedUri = encodeURI(csvContent);
        const link = document.createElement('a');
        link.href = encodedUri;
        link.download = `chart-data-${new Date().toISOString().slice(0, 19).replace(/[:.]/g, '-')}.csv`;
        
        // 觸發下載
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        console.log('資料已匯出為 CSV 檔案');
    } catch (error) {
        console.error('匯出 CSV 錯誤:', error);
        showError('匯出 CSV 檔案時發生錯誤');
    }
}

/**
 * 將資料匯出為 JSON 檔案
 * @param {object} appState - 應用狀態
 */
export function exportDataToJSON(appState) {
    if (!appState.myChart || !appState.myChart.data) {
        showError('無資料可供匯出');
        return;
    }
    
    try {
        // 創建包含資料的 JSON 物件
        const exportData = {
            data: appState.myChart.data,
            options: appState.myChart.options,
            type: appState.myChart.config.type,
            title: appState.myChart.options.plugins && appState.myChart.options.plugins.title ? appState.myChart.options.plugins.title.text : '圖表標題'
        };
        
        // 轉換為 JSON 字串
        const jsonString = JSON.stringify(exportData, null, 2);
        const blob = new Blob([jsonString], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        
        // 創建一個下載連結
        const link = document.createElement('a');
        link.href = url;
        link.download = `chart-data-${new Date().toISOString().slice(0, 19).replace(/[:.]/g, '-')}.json`;
        
        // 觸發下載
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        console.log('資料已匯出為 JSON 檔案');
    } catch (error) {
        console.error('匯出 JSON 錯誤:', error);
        showError('匯出 JSON 檔案時發生錯誤');
    }
}

/**
 * 將資料匯出為 Excel 檔案
 * @param {object} appState - 應用狀態
 */
export function exportDataToExcel(appState) {
    if (!appState.myChart || !appState.myChart.data) {
        showError('無資料可供匯出');
        return;
    }
    
    try {
        showLoading(true);
        
        // 準備要傳送到後端的資料
        const exportData = {
            data: appState.myChart.data,
            chartType: appState.myChart.config.type,
            title: appState.myChart.options.plugins && appState.myChart.options.plugins.title ? appState.myChart.options.plugins.title.text : '圖表標題'
        };
        
        // 發送資料到後端轉換為 Excel
        fetch('/api/export_excel', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(exportData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('匯出 Excel 檔案失敗');
            }
            return response.blob();
        })
        .then(blob => {
            // 創建一個下載連結
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = `chart-data-${new Date().toISOString().slice(0, 19).replace(/[:.]/g, '-')}.xlsx`;
            
            // 觸發下載
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            console.log('資料已匯出為 Excel 檔案');
        })
        .catch(error => {
            console.error('匯出 Excel 錯誤:', error);
            showError('匯出 Excel 檔案時發生錯誤');
        })
        .finally(() => {
            showLoading(false);
        });
    } catch (error) {
        console.error('匯出 Excel 錯誤:', error);
        showError('匯出 Excel 檔案時發生錯誤');
        showLoading(false);
    }
}
