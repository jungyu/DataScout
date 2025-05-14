/**
 * Chart.js 圖表應用前端 JavaScript
 */

// 全局變數儲存 Chart 實例
let myChart = null;

/**
 * 從 API 獲取圖表數據
 */
async function fetchChartData() {
    try {
        const response = await fetch('/api/chart-data/');
        if (!response.ok) {
            throw new Error(`API 請求失敗: ${response.status} ${response.statusText}`);
        }
        return await response.json();
    } catch (error) {
        console.error('獲取圖表數據錯誤:', error);
        return null;
    }
}

/**
 * 渲染圖表
 * @param {Object} data - 圖表數據
 * @param {string} chartType - 圖表類型
 */
function renderChart(data, chartType = 'bar') {
    // 獲取 canvas 元素
    const ctx = document.getElementById('myChart').getContext('2d');
    
    // 如果已經有圖表實例，先銷毀它
    if (myChart) {
        myChart.destroy();
    }
    
    // 創建圖表配置
    const config = {
        type: chartType,
        data: {
            labels: data.labels,
            datasets: data.datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: data.chartTitle || '圖表',
                    font: {
                        size: 18
                    }
                },
                legend: {
                    position: 'top',
                }
            },
            scales: {}
        }
    };
    
    // 根據圖表類型調整配置
    if (['pie', 'radar'].includes(chartType)) {
        // 圓餅圖和雷達圖不需要坐標軸
        delete config.options.scales;
    } else {
        // 為長條圖和折線圖添加坐標軸配置
        config.options.scales = {
            y: {
                beginAtZero: true,
                title: {
                    display: true,
                    text: '銷售額'
                }
            },
            x: {
                title: {
                    display: true,
                    text: '月份'
                }
            }
        };
    }
    
    // 建立新的圖表實例
    myChart = new Chart(ctx, config);
    
    return myChart;
}

/**
 * 擷取圖表為圖片並觸發下載
 * @param {string} format - 圖片格式 'image/png' 或 'image/webp'
 * @param {number} quality - 圖片品質 (0-1)
 */
function captureChart(format, quality = 1.0) {
    // 確認圖表存在
    if (!myChart) {
        console.error('沒有找到圖表實例');
        return;
    }
    
    // 確認格式是否支援
    if (format === 'image/webp') {
        // 檢查瀏覽器是否支援 WebP
        const canvas = document.createElement('canvas');
        const isWebPSupported = canvas.toDataURL('image/webp').indexOf('data:image/webp') === 0;
        
        if (!isWebPSupported) {
            alert('您的瀏覽器不支援 WebP 格式，將改用 PNG 格式。');
            format = 'image/png';
        }
    }
    
    // 取得 Canvas 元素
    const canvas = document.getElementById('myChart');
    
    // 將圖表轉換為 Data URL
    const dataURL = canvas.toDataURL(format, quality);
    
    // 創建格式對應的副檔名
    const extension = format === 'image/png' ? 'png' : 'webp';
    
    // 創建下載連結
    const downloadLink = document.createElement('a');
    downloadLink.href = dataURL;
    downloadLink.download = `chart_${new Date().toISOString().slice(0,10)}.${extension}`;
    
    // 觸發下載
    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);
}

/**
 * 上傳圖表到伺服器
 * @param {string} format - 圖片格式 'image/png' 或 'image/webp'
 * @param {number} quality - 圖片品質 (0-1)
 */
function uploadChart(format = 'image/png', quality = 1.0) {
    // 確認圖表存在
    if (!myChart) {
        console.error('沒有找到圖表實例');
        return;
    }
    
    // 取得 Canvas 元素
    const canvas = document.getElementById('myChart');
    
    // 使用 toBlob 取得二進位資料
    canvas.toBlob(async (blob) => {
        // 建立 FormData 物件
        const formData = new FormData();
        
        // 創建格式對應的副檔名
        const extension = format === 'image/png' ? 'png' : 'webp';
        const filename = `chart_${new Date().toISOString().slice(0,10)}.${extension}`;
        
        // 將 blob 加入 FormData
        formData.append('file', blob, filename);
        
        try {
            // 發送到伺服器
            const response = await fetch('/upload-chart-image/', {
                method: 'POST',
                body: formData
            });
            
            // 處理回應
            const result = await response.json();
            
            // 顯示上傳結果
            const uploadStatus = document.getElementById('uploadStatus');
            const uploadMessage = document.getElementById('uploadMessage');
            
            uploadStatus.classList.remove('hidden');
            
            if (result.status === 'success') {
                uploadMessage.textContent = `圖片上傳成功: ${result.filepath}`;
                uploadMessage.className = 'text-green-600';
            } else {
                uploadMessage.textContent = `圖片上傳失敗: ${result.message}`;
                uploadMessage.className = 'text-red-600';
            }
            
            // 5秒後隱藏訊息
            setTimeout(() => {
                uploadStatus.classList.add('hidden');
            }, 5000);
            
        } catch (error) {
            console.error('上傳圖片時發生錯誤:', error);
            alert('上傳圖片時發生錯誤，請查看控制台了解詳情。');
        }
    }, format, quality);
}

/**
 * 初始化頁面
 */
async function initPage() {
    // 從 API 獲取資料
    const data = await fetchChartData();
    
    // 如果成功獲取資料，渲染圖表
    if (data) {
        renderChart(data, 'bar');
    }
    
    // 設置圖表類型選擇器事件
    const chartTypeSelector = document.getElementById('chartType');
    chartTypeSelector.addEventListener('change', async () => {
        const selectedType = chartTypeSelector.value;
        const data = await fetchChartData();
        if (data) {
            renderChart(data, selectedType);
        }
    });
    
    // 設置下載 PNG 按鈕事件
    document.getElementById('capturePngBtn').addEventListener('click', () => {
        captureChart('image/png');
    });
    
    // 設置下載 WebP 按鈕事件
    document.getElementById('captureWebpBtn').addEventListener('click', () => {
        captureChart('image/webp');
    });
    
    // 設置上傳按鈕事件
    document.getElementById('uploadChartBtn').addEventListener('click', () => {
        uploadChart();
    });
}

// 頁面加載完成後初始化
document.addEventListener('DOMContentLoaded', initPage);
