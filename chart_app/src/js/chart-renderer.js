import { showError } from './utils.js';
import { validateChartJsJSON, processChartJsJSON } from './json-validator.js';

// 色彩主題配置
export const chartThemes = {
    default: [
        "rgba(75, 192, 192, 0.6)",    // 綠松石色
        "rgba(153, 102, 255, 0.6)",   // 紫色
        "rgba(255, 159, 64, 0.6)",    // 橙色
        "rgba(54, 162, 235, 0.6)",    // 藍色
        "rgba(255, 99, 132, 0.6)",    // 粉色
        "rgba(255, 206, 86, 0.6)"     // 黃色
    ],
    light: [
        "rgba(100, 200, 200, 0.5)",   // 淺綠松石
        "rgba(150, 150, 250, 0.5)",   // 淺紫藍
        "rgba(250, 180, 100, 0.5)",   // 淺橙
        "rgba(100, 180, 250, 0.5)",   // 淺天藍
        "rgba(250, 150, 150, 0.5)",   // 淺粉
        "rgba(250, 230, 150, 0.5)"    // 淺黃
    ],
    dark: [
        "rgba(20, 120, 120, 0.8)",    // 深綠松石
        "rgba(80, 50, 170, 0.8)",     // 深紫色
        "rgba(200, 100, 20, 0.8)",    // 深橙色
        "rgba(20, 80, 170, 0.8)",     // 深藍色
        "rgba(180, 30, 50, 0.8)",     // 深粉色
        "rgba(180, 150, 10, 0.8)"     // 深黃色
    ],
    pastel: [
        "rgba(173, 216, 230, 0.7)",   // 淺藍
        "rgba(221, 160, 221, 0.7)",   // 淺紫
        "rgba(255, 182, 193, 0.7)",   // 淺粉紅
        "rgba(152, 251, 152, 0.7)",   // 淺綠
        "rgba(255, 218, 185, 0.7)",   // 淺桃
        "rgba(230, 230, 250, 0.7)"    // 薰衣草
    ],
    vibrant: [
        "rgba(0, 204, 204, 0.8)",     // 鮮綠松石
        "rgba(153, 51, 255, 0.8)",    // 鮮紫色
        "rgba(255, 102, 0, 0.8)",     // 鮮橙色
        "rgba(0, 102, 204, 0.8)",     // 鮮藍色
        "rgba(255, 0, 102, 0.8)",     // 鮮粉色
        "rgba(255, 204, 0, 0.8)"      // 鮮黃色
    ]
};

/**
 * 創建圖表
 * @param {Object} data - 圖表資料
 * @param {string} chartType - 圖表類型
 * @param {string} theme - 主題名稱
 * @param {object} appState - 應用狀態
 */
export function createChart(data, chartType = 'line', theme = 'default', appState) {
    // 獲取圖表容器
    const canvas = document.getElementById('chartCanvas');
    if (!canvas) {
        showError('未找到圖表容器');
        return;
    }
    
    // 如果已有圖表實例，則銷毀它
    if (appState.myChart) {
        appState.myChart.destroy();
    }
    
    // 驗證和處理數據
    const validData = processChartJsJSON(data);
    
    // 提取圖表設定
    const chartConfig = prepareChartConfig(validData, chartType, theme);
    
    // 創建新圖表
    appState.myChart = new Chart(canvas, chartConfig);
    
    // 更新目前的圖表類型和主題
    appState.currentChartType = chartType;
    appState.currentChartTheme = theme;
    
    console.log(`已創建 ${chartType} 圖表，使用 ${theme} 主題`);
}

/**
 * 準備圖表設定
 * @param {Object} data - 圖表資料
 * @param {string} chartType - 圖表類型
 * @param {string} theme - 主題名稱
 * @returns {Object} - 圖表設定物件
 */
export function prepareChartConfig(data, chartType, theme) {
    // 確保 data 包含必要的結構
    if (!data || !data.data || !Array.isArray(data.data.datasets)) {
        console.error('資料格式不符合要求');
        return null;
    }
    
    // 從全域色彩主題中選擇顏色
    const colors = chartThemes[theme] || chartThemes.default;
    
    // 處理股票圖表的特殊情況
    if (chartType === 'ohlc' || chartType === 'candlestick') {
        return prepareStockChartConfig(data, chartType, theme);
    }
    
    // 為每個數據集指定顏色
    for (let i = 0; i < data.data.datasets.length; i++) {
        const colorIndex = i % colors.length;
        const dataset = data.data.datasets[i];
        
        if (chartType === 'pie' || chartType === 'doughnut' || chartType === 'polarArea') {
            // 圓餅圖、環形圖和極區圖使用多種顏色
            dataset.backgroundColor = colors;
        } else {
            // 其他圖表類型為每個數據集使用單一顏色
            dataset.backgroundColor = dataset.backgroundColor || colors[colorIndex];
            dataset.borderColor = dataset.borderColor || colors[colorIndex].replace(/[^,]+(?=\))/, '1');
        }
    }
    
    // 基本圖表設定
    const chartConfig = {
        type: chartType,
        data: data.data,
        options: data.options || {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: data.title || '圖表標題'
                },
                legend: {
                    display: true,
                    position: 'top'
                }
            }
        }
    };
    
    return chartConfig;
}

/**
 * 準備股票圖表設定
 * @param {Object} data - 圖表資料
 * @param {string} chartType - 圖表類型 ('ohlc' 或 'candlestick')
 * @param {string} theme - 主題名稱
 * @returns {Object} - 股票圖表設定物件
 */
function prepareStockChartConfig(data, chartType, theme) {
    // 從全域色彩主題中選擇顏色
    const colors = chartThemes[theme] || chartThemes.default;
    
    // 設定漲跌顏色
    const upColor = colors[4] || 'rgba(255, 99, 132, 0.8)';  // 紅色（漲）
    const downColor = colors[0] || 'rgba(75, 192, 192, 0.8)'; // 綠色（跌）
    
    // 遍歷每個數據集，設定顏色
    data.data.datasets.forEach(dataset => {
        dataset.color = {
            up: upColor,
            down: downColor,
            unchanged: 'rgba(180, 180, 180, 0.8)'
        };
    });
    
    // 股票圖表特殊選項
    const stockChartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            x: {
                type: 'time',
                time: {
                    unit: 'day'
                },
                title: {
                    display: true,
                    text: '日期'
                }
            },
            y: {
                title: {
                    display: true,
                    text: '價格'
                }
            }
        },
        plugins: {
            title: {
                display: true,
                text: data.title || 'OHLC + Volume'
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        const point = context.raw;
                        return [
                            `開盤: ${point.o}`,
                            `最高: ${point.h}`,
                            `最低: ${point.l}`,
                            `收盤: ${point.c}`
                        ];
                    }
                }
            }
        }
    };
    
    // 合併來自資料的選項
    const options = data.options ? { ...stockChartOptions, ...data.options } : stockChartOptions;
    
    // 基本股票圖表設定
    const chartConfig = {
        type: chartType,
        data: data.data,
        options: options
    };
    
    return chartConfig;
}

/**
 * 將圖表匯出為圖片檔
 * @param {string} format - 圖片格式，如 'image/png', 'image/webp'
 * @param {object} appState - 應用狀態
 */
export function captureChart(format = 'image/png', appState) {
    if (!appState.myChart) {
        showError('無圖表可供匯出');
        return;
    }
    
    try {
        // 獲取圖表的 base64 編碼的資料 URL
        const dataURL = appState.myChart.toBase64Image(format);
        
        // 創建一個隱藏的下載連結元素
        const link = document.createElement('a');
        link.href = dataURL;
        link.download = `chart-${new Date().toISOString().slice(0, 19).replace(/[:.]/g, '-')}.${format.split('/')[1]}`;
        
        // 觸發下載
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        console.log(`已匯出圖表為 ${format} 格式`);
    } catch (error) {
        console.error('匯出圖表錯誤:', error);
        showError('匯出圖表時發生錯誤');
    }
}
