/**
 * 蝴蝶圖助手模組 - 提供蝴蝶圖數據處理功能
 */

/**
 * 處理蝴蝶圖數據
 * @param {Object} data - 原始數據
 * @returns {Object} 處理後的數據，適合繪製蝴蝶圖
 */
function processButterFlyData(data) {
    console.log('processButterFlyData 被調用，數據類型:', typeof data);
    
    // 標準化數據結構
    const processedData = {
        labels: [],
        datasets: [
            {
                label: '男性',
                data: [],
                backgroundColor: 'rgba(54, 162, 235, 0.6)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            },
            {
                label: '女性',
                data: [],
                backgroundColor: 'rgba(255, 99, 132, 0.6)',
                borderColor: 'rgba(255, 99, 132, 1)',
                borderWidth: 1
            }
        ]
    };

    try {
        console.log('處理蝴蝶圖數據:', data);
        
        // 處理標籤
        if (data.labels && Array.isArray(data.labels)) {
            processedData.labels = data.labels;
        }
        
        // 處理數據集
        const sourceDatasets = data.datasets || [];
        if (sourceDatasets.length >= 2) {
            // 取得原始資料集中的標籤
            if (sourceDatasets[0].label) processedData.datasets[0].label = sourceDatasets[0].label;
            if (sourceDatasets[1].label) processedData.datasets[1].label = sourceDatasets[1].label;
            
            // 取得數據
            processedData.datasets[0].data = sourceDatasets[0].data || [];
            
            // 確保第二個數據集的值為負數（視覺化蝴蝶圖需要）
            if (sourceDatasets[1].data) {
                processedData.datasets[1].data = sourceDatasets[1].data.map(val => 
                    val > 0 ? -Math.abs(val) : val
                );
            }
        } else if (data.data && Array.isArray(data.data)) {
            // 若只有單一資料集，拆分為兩部分
            const midPoint = Math.floor(data.data.length / 2);
            processedData.datasets[0].data = data.data.slice(0, midPoint);
            processedData.datasets[1].data = data.data.slice(midPoint).map(val => 
                val > 0 ? -Math.abs(val) : val
            );
        }
        
        // 確保標籤數量與數據一致
        if (processedData.labels.length === 0) {
            const maxDataLength = Math.max(
                processedData.datasets[0].data.length,
                processedData.datasets[1].data.length
            );
            
            processedData.labels = Array.from({ length: maxDataLength }, (_, i) => `項目 ${i + 1}`);
        }
        
        // 確保數據不為空
        if (processedData.datasets[0].data.length === 0 && processedData.datasets[1].data.length === 0) {
            // 生成範例資料
            processedData.labels = ['0-10', '11-20', '21-30', '31-40', '41-50', '51-60', '61-70', '71-80', '81+'];
            processedData.datasets[0].data = [5, 10, 15, 20, 25, 20, 15, 10, 5];
            processedData.datasets[1].data = [-5, -10, -15, -20, -25, -20, -15, -10, -5];
        }
        
        // 確保兩個數據集有相同數量的數據點
        const maxLength = Math.max(
            processedData.datasets[0].data.length,
            processedData.datasets[1].data.length
        );
        
        // 補足不足的數據點
        while (processedData.datasets[0].data.length < maxLength) {
            processedData.datasets[0].data.push(0);
        }
        
        while (processedData.datasets[1].data.length < maxLength) {
            processedData.datasets[1].data.push(0);
        }
        
        console.log('處理後的蝴蝶圖數據:', processedData);
    } catch (error) {
        console.error('處理蝴蝶圖資料時出錯:', error);
        
        // 生成範例資料
        processedData.labels = ['0-10', '11-20', '21-30', '31-40', '41-50', '51-60', '61-70', '71-80', '81+'];
        processedData.datasets[0].data = [5, 10, 15, 20, 25, 20, 15, 10, 5];
        processedData.datasets[1].data = [-5, -10, -15, -20, -25, -20, -15, -10, -5];
    }

    // 將函數暴露到全局
    window.processButterFlyData = processButterFlyData;
    
    console.log('processButterFlyData 處理完成，返回數據');
    return processedData;
}

// 函數作為全局函數暴露
window.processButterFlyData = processButterFlyData;
