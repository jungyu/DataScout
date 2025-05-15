/**
 * Chart.js 圖表應用前端 JavaScript
 */

// 全局變數儲存 Chart 實例
let myChart = null;
let currentDataFile = null;
let currentDataType = null;
let currentChartType = 'line';
let currentChartTheme = 'default';
let availableDataFiles = {};
let dataColumnInfo = null;

// 色彩主題配置
const chartThemes = {
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
        "rgba(0, 102, 255, 0.8)",     // 鮮藍色
        "rgba(255, 0, 102, 0.8)",     // 鮮粉色
        "rgba(255, 204, 0, 0.8)"      // 鮮黃色
    ]
};

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
 * 獲取所有可用的數據文件
 */
async function fetchAllDataFiles() {
    try {
        const response = await fetch('/api/data-files/');
        if (!response.ok) {
            throw new Error(`API 請求失敗: ${response.status} ${response.statusText}`);
        }
        const data = await response.json();
        return data.data_files;
    } catch (error) {
        console.error('獲取數據文件列表錯誤:', error);
        return {};
    }
}

/**
 * 從 API 獲取文件數據
 * @param {string} filename - 文件名
 * @param {string} fileType - 文件類型 (csv, json, excel, persistence, uploaded)
 */
async function fetchFileData(filename, fileType) {
    try {
        console.log(`fetchFileData 調用: 檔案名=${filename}, 類型=${fileType}`);
        showLoading(true);
        
        // 對於 JSON 文件類型，首先檢查是否符合 Chart.js 格式
        if (fileType === 'json') {
            try {
                // 先嘗試獲取原始 JSON 內容
                const contentResponse = await fetch(`/api/file-content/?filename=${encodeURIComponent(filename)}&file_type=${fileType}`);
                if (!contentResponse.ok) {
                    console.warn(`無法使用 file-content API，狀態碼: ${contentResponse.status}，回退到標準處理方式`);
                    // 如果 file-content API 失敗，直接跳到標準處理方式
                } else {
                    const contentData = await contentResponse.json();
                    
                    // 使用 chart-json.js 中的函數處理 JSON 資料
                    if (contentData && contentData.data) {
                        // 確保 validateChartJsJSON 函數存在
                        if (typeof validateChartJsJSON === 'function') {
                            // 驗證 JSON 是否符合 Chart.js 格式
                            const validation = validateChartJsJSON(contentData.data);
                            
                            if (validation.isValid) {
                                console.log('使用 Chart.js 標準 JSON 格式處理資料');
                                // 處理 JSON 資料為標準 Chart.js 格式
                                const processedData = processChartJsJSON(contentData.data);
                                showLoading(false);
                                return processedData;
                            } else {
                                console.warn('JSON 驗證失敗，錯誤:', validation.errors);
                            }
                        } else {
                            console.error('找不到 validateChartJsJSON 函數，可能 chart-json.js 沒有正確載入');
                        }
                    }
                    // 如果不是有效的 Chart.js 格式，則回退到標準處理方式
                }
            } catch (error) {
                console.warn('處理 JSON 檔案時發生錯誤，回退到標準處理方式:', error);
                // 錯誤處理，回退到標準處理方式
            }
        }
        
        // 標準處理方式（用於非 Chart.js JSON 或其他檔案類型）
        console.log(`正在呼叫 API 獲取檔案資料: /api/file-data/?filename=${encodeURIComponent(filename)}&file_type=${fileType}`);
        
        const response = await fetch(`/api/file-data/?filename=${encodeURIComponent(filename)}&file_type=${fileType}`);
        if (!response.ok) {
            const errorText = await response.text();
            console.error(`API 請求失敗: ${response.status} ${response.statusText}, 回應內容: ${errorText}`);
            throw new Error(`API 請求失敗: ${response.status} ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('檔案資料載入成功:', data);
        showLoading(false);
        return data;
    } catch (error) {
        console.error('獲取數據錯誤:', error);
        showLoading(false);
        showError(`獲取數據時發生錯誤: ${error.message}`);
        return null;
    }
}

/**
 * 獲取文件結構信息
 * @param {string} filename - 文件名
 * @param {string} fileType - 文件類型 (csv, json, excel, persistence, uploaded)
 */
async function fetchFileStructure(filename, fileType) {
    try {
        const response = await fetch(`/api/file-structure/?filename=${encodeURIComponent(filename)}&file_type=${fileType}`);
        if (!response.ok) {
            throw new Error(`API 請求失敗: ${response.status} ${response.statusText}`);
        }
        return await response.json();
    } catch (error) {
        console.error('獲取文件結構錯誤:', error);
        showError(`獲取文件結構時發生錯誤: ${error.message}`);
        return null;
    }
}

/**
 * 獲取 CSV 文件結構信息
 * @param {string} filename - CSV 文件名
 */
async function fetchCSVStructure(filename) {
    try {
        const response = await fetch(`/api/csv-structure/?filename=${encodeURIComponent(filename)}`);
        if (!response.ok) {
            throw new Error(`API 請求失敗: ${response.status} ${response.statusText}`);
        }
        return await response.json();
    } catch (error) {
        console.error('獲取 CSV 結構錯誤:', error);
        return null;
    }
}

/**
 * 顯示或隱藏載入狀態
 * @param {boolean} isLoading - 是否正在載入
 */
function showLoading(isLoading) {
    const loadingStatus = document.getElementById('loadingStatus');
    const chartContainer = document.getElementById('chartContainer');
    
    if (isLoading) {
        loadingStatus.classList.remove('hidden');
        chartContainer.classList.add('hidden');
    } else {
        loadingStatus.classList.add('hidden');
        chartContainer.classList.remove('hidden');
    }
}

/**
 * 顯示錯誤訊息
 * @param {string} message - 錯誤訊息
 */
function showError(message) {
    const uploadStatus = document.getElementById('uploadStatus');
    const uploadMessage = document.getElementById('uploadMessage');
    
    uploadMessage.textContent = message;
    uploadMessage.className = 'text-red-600';
    uploadStatus.classList.remove('hidden');
    
    // 5秒後隱藏訊息
    setTimeout(() => {
        uploadStatus.classList.add('hidden');
    }, 5000);
}

/**
 * 更新資料摘要區域
 * @param {Object} structure - CSV 文件結構信息
 */
function updateDataInfo(structure) {
    const dataInfoContent = document.getElementById('dataInfoContent');
    
    if (!structure) {
        dataInfoContent.innerHTML = '無法獲取資料摘要';
        return;
    }
    
    // 建立摘要內容 HTML
    let html = `
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
                <p><strong>文件名稱:</strong> ${structure.filename}</p>
                <p><strong>資料列數:</strong> ${structure.row_count}</p>
                <p><strong>欄位數量:</strong> ${structure.column_count}</p>
            </div>
            <div>
                <p><strong>資料欄位:</strong></p>
                <ul class="list-disc pl-5">
    `;
    
    // 最多顯示10個欄位
    const columns = structure.columns.slice(0, 10);
    columns.forEach(col => {
        html += `<li>${col.name} (${col.dtype})</li>`;
    });
    
    if (structure.columns.length > 10) {
        html += `<li>...等共 ${structure.columns.length} 個欄位</li>`;
    }
    
    html += `
                </ul>
            </div>
        </div>
    `;
    
    // 更新內容
    dataInfoContent.innerHTML = html;
}

/**
 * 渲染圖表
 * @param {Object} data - 圖表數據
 * @param {string} chartType - 圖表類型
 */
function renderChart(data, chartType = 'line') {
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
            animation: {
                duration: 1000  // 1秒動畫
            },
            plugins: {
                title: {
                    display: true,
                    text: data.chartTitle || '圖表',
                    font: {
                        size: 18,
                        weight: 'bold'
                    },
                    padding: {
                        top: 10,
                        bottom: 20
                    }
                },
                legend: {
                    position: 'top',
                    labels: {
                        boxWidth: 12,
                        font: {
                            size: 11
                        }
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(0, 0, 0, 0.7)',
                    padding: 10,
                    titleFont: {
                        size: 14
                    },
                    bodyFont: {
                        size: 13
                    }
                }
            },
            scales: {}
        }
    };
    
    // 根據圖表類型調整配置
    if (['pie', 'radar'].includes(chartType)) {
        // 圓餅圖和雷達圖不需要坐標軸
        delete config.options.scales;
    } else if (chartType === 'scatter') {
        // 散點圖配置
        config.options.scales = {
            x: {
                type: 'linear',
                position: 'bottom',
                title: {
                    display: true,
                    text: '數值'
                }
            },
            y: {
                title: {
                    display: true,
                    text: '數值'
                }
            }
        };
    } else {
        // 為長條圖和折線圖添加坐標軸配置
        config.options.scales = {
            y: {
                beginAtZero: false,  // 允許 Y 軸從數據的最小值開始
                title: {
                    display: true,
                    text: '數值'
                },
                ticks: {
                    // 使用 callback 自動格式化大數字
                    callback: function(value) {
                        if (Math.abs(value) >= 1000000) {
                            return (value / 1000000) + 'M';
                        } else if (Math.abs(value) >= 1000) {
                            return (value / 1000) + 'k';
                        } else {
                            return value;
                        }
                    }
                }
            },
            x: {
                title: {
                    display: true,
                    text: '時間'
                },
                ticks: {
                    maxRotation: 45, // 標籤旋轉角度
                    minRotation: 0,
                    autoSkip: true,  // 自動跳過標籤以避免擁擠
                    maxTicksLimit: 20 // 最大標籤數量
                }
            }
        };
        
        // 為折線圖添加特定配置
        if (chartType === 'line') {
            // 對每個數據集設置平滑曲線
            data.datasets.forEach(dataset => {
                dataset.tension = 0.2;  // 添加平滑度
                dataset.pointRadius = 2; // 設置較小的點
                dataset.pointHoverRadius = 5;
                dataset.borderWidth = 2;
            });
        }
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
        showError('沒有找到圖表實例');
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
    
    // 獲取文件名
    let filename = 'chart';
    if (currentDataFile) {
        filename = currentDataFile.replace('.csv', '');
    }
    
    // 創建下載連結
    const downloadLink = document.createElement('a');
    downloadLink.href = dataURL;
    downloadLink.download = `${filename}_${new Date().toISOString().slice(0,10)}.${extension}`;
    
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
        showError('沒有找到圖表實例');
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
        
        // 獲取文件名
        let filename = 'chart';
        if (currentDataFile) {
            filename = currentDataFile.replace('.csv', '');
        }
        
        const fullFilename = `${filename}_${new Date().toISOString().slice(0,10)}.${extension}`;
        
        // 將 blob 加入 FormData
        formData.append('file', blob, fullFilename);
        
        try {
            // 顯示上傳中狀態
            const uploadStatus = document.getElementById('uploadStatus');
            const uploadMessage = document.getElementById('uploadMessage');
            
            uploadStatus.classList.remove('hidden');
            uploadMessage.textContent = '正在上傳圖片...';
            uploadMessage.className = 'text-blue-600';
            
            // 發送到伺服器
            const response = await fetch('/upload-chart-image/', {
                method: 'POST',
                body: formData
            });
            
            // 處理回應
            const result = await response.json();
            
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
            showError(`上傳圖片時發生錯誤: ${error.message}`);
        }
    }, format, quality);
}

/**
 * 使用 Chart.js 創建圖表
 * @param {object} data - 圖表數據
 * @param {string} type - 圖表類型
 * @param {string} theme - 圖表主題
 */
function createChart(data, type = 'line', theme = 'default') {
    const chartArea = document.getElementById('chartArea');
    const chartCanvas = document.getElementById('myChart');
    const chartTitle = document.getElementById('chartTitle');
    
    // 更新圖表標題
    if (data.chartTitle) {
        chartTitle.textContent = data.chartTitle;
    } else {
        chartTitle.textContent = '圖表';
    }
    
    // 如果已經有圖表實例，先銷毀它
    if (myChart !== null) {
        myChart.destroy();
    }
    
    // 檢查圖表類型有效性（防止XSS）
    const validTypes = [
        'line', 'bar', 'pie', 'radar', 'polarArea', 'doughnut', 'scatter', 'bubble',
        'candlestick', 'ohlc', 'sankey', 'barLine', 'ohlcVolume', 'ohlcMaKd'
    ];
    
    if (!validTypes.includes(type)) {
        type = 'line'; // 預設為折線圖
    }
    
    // 處理特殊混合圖表類型
    let mixedType = false;
    let baseType = type;
    
    if (type === 'barLine') {
        baseType = 'bar';  // 使用柱狀圖作為基礎類型
        mixedType = true;
    } else if (type === 'ohlcVolume' || type === 'ohlcMaKd') {
        baseType = 'bar';  // 使用柱狀圖作為基礎類型
        mixedType = true;
    }
    
    // 獲取主題色彩
    const themeColors = chartThemes[theme] || chartThemes.default;
    
    // 應用主題色彩到數據集
    if (data.datasets && Array.isArray(data.datasets)) {
        data.datasets.forEach((dataset, index) => {
            const colorIndex = index % themeColors.length;
            const color = themeColors[colorIndex];
            
            dataset.backgroundColor = dataset.backgroundColor || color;
            dataset.borderColor = dataset.borderColor || color.replace("0.6", "1.0");
            
            // 為不同圖表類型設置特定屬性
            if (type === 'line') {
                dataset.fill = false;
                dataset.tension = 0.3;
            } else if (type === 'pie' || type === 'doughnut' || type === 'polarArea') {
                dataset.backgroundColor = themeColors.map(color => color);
            } else if (type === 'radar') {
                dataset.fill = true;
            } else if (type === 'scatter' || type === 'bubble') {
                dataset.pointRadius = dataset.pointRadius || 6;
            }
        });
    }
    
    // 根據圖表類型設置配置
    const config = {
        type: mixedType ? baseType : type,  // 混合圖表使用基礎類型
        data: {
            labels: data.labels,
            datasets: data.datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            },
            animation: {
                duration: 1000,
                easing: 'easeOutQuart'
            }
        }
    };
    
    // 為金融圖表設置特殊配置
    if (type === 'candlestick' || type === 'ohlc') {
        // 金融圖表需要時間軸
        config.options.scales = {
            x: {
                type: 'time',
                time: {
                    unit: 'day'
                },
                adapters: {
                    date: {
                        locale: 'zh-TW'
                    }
                }
            },
            y: {
                position: 'right'
            }
        };
    }
    
    // 為特定圖表類型添加特殊配置
    if (type === 'pie' || type === 'doughnut' || type === 'polarArea') {
        // 餅圖系列的特殊配置
        config.options.plugins.legend.position = 'right';
    } else if (type === 'radar') {
        // 雷達圖特殊配置
        config.options.scales = {
            r: {
                angleLines: {
                    display: true
                },
                ticks: {
                    beginAtZero: true
                }
            }
        };
    } else if (type === 'scatter' || type === 'bubble') {
        // 散點圖和氣泡圖特殊配置
        config.options.scales = {
            x: {
                type: 'linear',
                position: 'bottom'
            },
            y: {
                beginAtZero: false
            }
        };
    } else if (type === 'barLine') {
        // 柱狀圖+折線圖混合
        config.options.scales = {
            y: {
                beginAtZero: false,
                ticks: {
                    callback: function(value) {
                        if (value >= 1000000) {
                            return (value / 1000000).toFixed(1) + 'M';
                        } else if (value >= 1000) {
                            return (value / 1000).toFixed(1) + 'K';
                        }
                        return value;
                    }
                }
            },
            x: {
                ticks: {
                    maxRotation: 45,
                    minRotation: 0
                }
            }
        };
    } else if (type === 'ohlcVolume') {
        // OHLC+成交量混合圖
        config.options.scales = {
            x: {
                type: 'time',
                time: {
                    unit: 'day'
                },
                adapters: {
                    date: {
                        locale: 'zh-TW'
                    }
                }
            },
            price: {
                position: 'left',
                type: 'linear',
            },
            volume: {
                position: 'right',
                type: 'linear',
                grid: {
                    drawOnChartArea: false
                }
            }
        };
    } else if (type === 'ohlcMaKd') {
        // OHLC+移動平均線+KD線
        config.options.scales = {
            x: {
                type: 'time',
                time: {
                    unit: 'day'
                },
                adapters: {
                    date: {
                        locale: 'zh-TW'
                    }
                }
            },
            price: {
                position: 'left',
                type: 'linear',
            },
            kd: {
                position: 'right',
                type: 'linear',
                min: 0,
                max: 100,
                grid: {
                    drawOnChartArea: false
                }
            }
        };
    } else {
        // 為折線圖和長條圖添加座標軸配置
        config.options.scales = {
            y: {
                beginAtZero: false,
                ticks: {
                    // 使用回調確保標籤格式化正確
                    callback: function(value) {
                        if (value >= 1000000) {
                            return (value / 1000000).toFixed(1) + 'M';
                        } else if (value >= 1000) {
                            return (value / 1000).toFixed(1) + 'K';
                        }
                        return value;
                    }
                }
            },
            x: {
                ticks: {
                    maxRotation: 45,
                    minRotation: 0
                }
            }
        };
    }
    
    // 創建圖表
    myChart = new Chart(chartCanvas, config);
    
    // 顯示圖表區域
    chartArea.classList.remove('hidden');
}

/**
 * 初始化頁面
 */
async function initPage() {
    // 初始隱藏圖表容器
    document.getElementById('chartContainer').classList.add('hidden');
    
    // 載入所有可用的數據文件
    availableDataFiles = await fetchAllDataFiles();
    
    // 設置資料類型選擇器事件
    const dataSourceTypeSelector = document.getElementById('dataSourceType');
    const dataSourceSelector = document.getElementById('dataSource');
    const dataSourceContainer = document.getElementById('dataSourceContainer');
    
    dataSourceTypeSelector.addEventListener('change', async () => {
        const selectedType = dataSourceTypeSelector.value;
        currentDataType = selectedType;
        
        // 清空並重新填充檔案選擇器
        dataSourceSelector.innerHTML = '<option value="" disabled selected>-- 請選擇資料檔案 --</option>';
        
        // 顯示/隱藏檔案上傳區域（只在選擇"自行上傳"時顯示）
        const uploadSection = document.getElementById('uploadSection');
        const uploadNewFileSection = document.getElementById('uploadNewFileSection');
        
        if (selectedType === 'uploaded') {
            // 顯示檔案上傳區域
            uploadSection.classList.remove('hidden');
            
            // 隱藏檔案選擇器
            dataSourceContainer.classList.add('hidden');
            
            console.log('已切換到「自行上傳資料」模式，顯示檔案拖放區域');
            
            // 移除之前選擇的檔案資訊
            const fileNameDisplay = document.getElementById('selectedFileName');
            if (fileNameDisplay) {
                fileNameDisplay.textContent = '';
                fileNameDisplay.classList.add('hidden');
            }
            
            // 重設檔案上傳按鈕
            const uploadFileBtn = document.getElementById('uploadFileBtn');
            if (uploadFileBtn) {
                uploadFileBtn.disabled = true;
            }
            
            // 清空圖表區域
            const chartContainer = document.getElementById('chartContainer');
            if (chartContainer && !chartContainer.classList.contains('hidden')) {
                chartContainer.classList.add('hidden');
            }
            
            // 重設 Alpine.js 狀態
            const fileUploadArea = document.getElementById('fileUploadArea');
            if (fileUploadArea && window.Alpine) {
                try {
                    const alpineComponent = Alpine.$data(fileUploadArea);
                    if (alpineComponent) {
                        alpineComponent.fileSelected = false;
                        alpineComponent.fileName = '';
                        alpineComponent.dragOver = false;
                    }
                } catch (error) {
                    console.warn('無法重設 Alpine.js 狀態:', error);
                }
            }
        } else if (selectedType === 'json') {
            uploadSection.classList.add('hidden');
            
            // 對於範例資料，只顯示 S&P 500 範例
            if (availableDataFiles[selectedType]) {
                // 尋找 S&P 500 範例檔案
                const sp500File = availableDataFiles[selectedType].find(
                    file => file.filename === 'sp500_sample.json'
                );
                
                if (sp500File) {
                    // 自動選中範例檔案
                    currentDataFile = sp500File.filename;
                    
                    // 載入並顯示圖表
                    const data = await fetchFileData(currentDataFile, currentDataType);
                    if (data) {
                        // 獲取當前選擇的圖表類型和主題
                        const chartType = document.getElementById('chartType').value;
                        const chartTheme = document.getElementById('chartTheme').value;
                        
                        // 渲染圖表
                        createChart(data, chartType, chartTheme);
                        document.getElementById('chartContainer').classList.remove('hidden');
                        
                        // 隱藏資料檔案選擇器
                        dataSourceContainer.classList.add('hidden');
                    }
                } else {
                    // 如果沒有找到 S&P 500 範例，顯示所有範例檔案
                    dataSourceContainer.classList.remove('hidden');
                    const files = availableDataFiles[selectedType];
                    files.forEach(file => {
                        const option = document.createElement('option');
                        option.value = file.filename;
                        option.textContent = file.display_name;
                        dataSourceSelector.appendChild(option);
                    });
                }
            } else {
                dataSourceContainer.classList.add('hidden');
            }
        } else {
            uploadSection.classList.add('hidden');
            dataSourceContainer.classList.add('hidden');
        }
    });
    
    // 設置資料檔案選擇器事件
    dataSourceSelector.addEventListener('change', async () => {
        const selectedFile = dataSourceSelector.value;
        if (selectedFile && currentDataType) {
            currentDataFile = selectedFile;
            
            // 顯示 OLAP 操作區域
            document.getElementById('olapOperationArea').classList.remove('hidden');
            
            // 獲取所選文件的數據
            const data = await fetchFileData(selectedFile, currentDataType);
            if (data) {
                // 獲取當前選擇的圖表類型
                const chartType = document.getElementById('chartType').value;
                const chartTheme = document.getElementById('chartTheme').value;
                
                // 渲染圖表
                createChart(data, chartType, chartTheme);
                
                // 獲取並顯示文件結構信息
                const structure = await fetchFileStructure(selectedFile, currentDataType);
                updateDataInfo(structure);
                
                // 保存數據列信息，用於 OLAP 操作
                dataColumnInfo = structure;
                
                // 更新 OLAP 操作的欄位選項
                updateOlapFieldOptions(structure);
            }
        }
    });
    
    // 設置圖表類型選擇器事件
    const chartTypeSelector = document.getElementById('chartType');
    chartTypeSelector.addEventListener('change', async () => {
        currentChartType = chartTypeSelector.value;
        updateChart();
    });
    
    // 設置圖表主題選擇器事件
    const chartThemeSelector = document.getElementById('chartTheme');
    chartThemeSelector.addEventListener('change', async () => {
        currentChartTheme = chartThemeSelector.value;
        updateChart();
    });
    
    // 設置 OLAP 操作類型選擇器事件
    const olapOperationSelector = document.getElementById('olapOperation');
    olapOperationSelector.addEventListener('change', () => {
        const operation = olapOperationSelector.value;
        
        // 顯示/隱藏相關欄位
        const groupbyFields = document.querySelectorAll('.groupby-field');
        const pivotFields = document.querySelectorAll('.pivot-field');
        const rollingFields = document.querySelectorAll('.rolling-field');
        
        // 隱藏所有相關欄位
        groupbyFields.forEach(field => field.classList.add('hidden'));
        pivotFields.forEach(field => field.classList.add('hidden'));
        rollingFields.forEach(field => field.classList.add('hidden'));
        
        // 顯示相關欄位
        if (operation === 'groupby') {
            groupbyFields.forEach(field => field.classList.remove('hidden'));
        } else if (operation === 'pivot_table') {
            groupbyFields.forEach(field => field.classList.remove('hidden'));
            pivotFields.forEach(field => field.classList.remove('hidden'));
        } else if (operation === 'rolling') {
            rollingFields.forEach(field => field.classList.remove('hidden'));
        }
    });
    
    // 設置執行 OLAP 按鈕事件
    document.getElementById('runOlapBtn').addEventListener('click', async () => {
        if (!currentDataFile || !currentDataType) {
            showError('請先選擇資料來源');
            return;
        }
        
        // 獲取 OLAP 參數
        const operation = document.getElementById('olapOperation').value;
        const groupColumns = document.getElementById('groupColumns').value;
        const valueColumn = document.getElementById('valueColumn').value;
        const aggFunction = document.getElementById('aggFunction').value;
        let rollingWindow = null, pivotIndex = null, pivotColumns = null;
        
        // 獲取操作特定的參數
        if (operation === 'rolling') {
            rollingWindow = parseInt(document.getElementById('rollingWindow').value);
            if (isNaN(rollingWindow) || rollingWindow <= 0) {
                showError('滾動窗口大小必須大於0');
                return;
            }
        } else if (operation === 'pivot_table') {
            pivotIndex = document.getElementById('pivotIndex').value;
            pivotColumns = document.getElementById('pivotColumns').value;
            
            if (!pivotIndex || !pivotColumns) {
                showError('透視表操作需要指定列索引和列標題');
                return;
            }
        }
        
        if (!valueColumn) {
            showError('請指定數值欄位');
            return;
        }
        
        // 準備表單數據
        const formData = new FormData();
        formData.append('filename', currentDataFile);
        formData.append('file_type', currentDataType);
        formData.append('operation', operation);
        formData.append('group_columns', groupColumns);
        formData.append('value_column', valueColumn);
        formData.append('agg_function', aggFunction);
        
        if (rollingWindow) {
            formData.append('rolling_window', rollingWindow);
        }
        
        if (pivotIndex) {
            formData.append('pivot_index', pivotIndex);
        }
        
        if (pivotColumns) {
            formData.append('pivot_columns', pivotColumns);
        }
        
        try {
            showLoading(true);
            
            // 發送 OLAP 請求
            const response = await fetch('/api/olap-operation/', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error(`API 請求失敗: ${response.status} ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.error) {
                showError(`OLAP 操作失敗: ${data.error}`);
                showLoading(false);
                return;
            }
            
            // 渲染 OLAP 結果圖表
            createChart(data, currentChartType, currentChartTheme);
            showLoading(false);
            
        } catch (error) {
            console.error('執行 OLAP 操作錯誤:', error);
            showLoading(false);
            showError(`執行 OLAP 操作錯誤: ${error.message}`);
        }
    });
    
    // 檔案上傳相關事件處理
    const fileUploadInput = document.getElementById('fileUpload');
    const uploadFileBtn = document.getElementById('uploadFileBtn');
    
    // 上傳按鈕事件處理 - 現在主要由 Alpine.js 處理檔案選擇和拖放邏輯
    
    // 檔案上傳按鈕事件
    uploadFileBtn.addEventListener('click', async () => {
        const file = fileUploadInput.files[0];
        if (!file) return;
        
        const fileType = document.getElementById('uploadFileType').value;
        const formData = new FormData();
        
        // 如果是 JSON 檔案，先檢查是否符合 Chart.js 格式
        if (fileType === 'json') {
            try {
                // 讀取檔案內容
                const reader = new FileReader();
                
                // 使用 Promise 包裝檔案讀取操作
                const fileContent = await new Promise((resolve, reject) => {
                    reader.onload = (e) => resolve(e.target.result);
                    reader.onerror = (e) => reject(e);
                    reader.readAsText(file);
                });
                
                // 解析 JSON
                const jsonData = JSON.parse(fileContent);
                
                // 驗證是否為有效的 Chart.js 格式
                const validation = validateChartJsJSON(jsonData);
                
                if (!validation.isValid) {
                    // 顯示驗證錯誤
                    showError(`JSON 格式無效: ${validation.errors.join('; ')}
                               請使用符合 Chart.js 標準的 JSON 格式`);
                    return;
                }
                
                // 處理為標準 Chart.js 格式
                const processedData = processChartJsJSON(jsonData);
                
                // 將處理後的資料轉換回字串
                const processedBlob = new Blob([JSON.stringify(processedData, null, 2)], {type: 'application/json'});
                
                // 使用處理後的資料替換原始檔案
                formData.append('file', processedBlob, file.name);
            } catch (error) {
                showError(`解析 JSON 檔案時發生錯誤: ${error.message}`);
                return;
            }
        } else {
            // 非 JSON 檔案直接附加
            formData.append('file', file);
        }
        
        formData.append('file_type', fileType);
        
        try {
            // 顯示上傳狀態
            const uploadProgress = document.getElementById('uploadProgress');
            const uploadProgressBar = document.getElementById('uploadProgressBar');
            const uploadStatus = document.getElementById('uploadStatus');
            
            uploadProgress.classList.remove('hidden');
            uploadProgressBar.style.width = '25%';
            uploadStatus.textContent = '上傳中...';
            
            const response = await fetch('/api/upload-file/', {
                method: 'POST',
                body: formData
            });
            
            uploadProgressBar.style.width = '75%';
            
            if (!response.ok) {
                throw new Error(`API 請求失敗: ${response.status} ${response.statusText}`);
            }
            
            const result = await response.json();
            uploadProgressBar.style.width = '100%';
            
            if (result.error) {
                showError(`上傳失敗: ${result.error}`);
            } else {
                // 更新可用文件列表
                availableDataFiles = await fetchAllDataFiles();
                
                uploadStatus.textContent = `檔案上傳成功 (${result.row_count} 列, ${result.column_count} 欄)`;
                uploadStatus.classList.add('text-green-600');
                
                // 清空檔案輸入並更新 UI
                fileUploadInput.value = '';
                
                // 更新上傳區域的 Alpine.js 狀態
                const fileUploadArea = document.getElementById('fileUploadArea');
                if (fileUploadArea && window.Alpine) {
                    // 使用 Alpine.js 的 Alpine.$data 來設置狀態
                    const alpineComponent = Alpine.$data(fileUploadArea);
                    if (alpineComponent) {
                        alpineComponent.fileSelected = true;
                        alpineComponent.fileName = `「${file.name}」已成功上傳`;
                        
                        // 5秒後重置狀態
                        setTimeout(() => {
                            alpineComponent.fileSelected = false;
                            alpineComponent.fileName = '';
                        }, 5000);
                    }
                }
                
                // 5秒後隱藏進度條
                setTimeout(() => {
                    uploadProgress.classList.add('hidden');
                    uploadStatus.classList.remove('text-green-600');
                }, 5000);
                
                // 自動載入上傳的檔案並顯示圖表
                if (result.filename) {
                    try {
                        currentDataFile = result.filename;
                        currentDataType = result.file_type; // 確保使用正確的文件類型
                        
                        console.log(`準備載入上傳的檔案: ${currentDataFile}, 類型: ${currentDataType}`);
                        
                        // 顯示載入狀態
                        const loadingStatus = document.getElementById('loadingStatus');
                        if (loadingStatus) loadingStatus.classList.remove('hidden');
                        
                        // 獲取檔案數據
                        const data = await fetchFileData(currentDataFile, currentDataType);
                        
                        // 隱藏載入狀態
                        if (loadingStatus) loadingStatus.classList.add('hidden');
                        
                        if (data) {
                            console.log('檔案數據載入成功，準備渲染圖表');
                            
                            // 獲取當前選擇的圖表類型和主題
                            const chartType = document.getElementById('chartType').value;
                            const chartTheme = document.getElementById('chartTheme').value;
                            
                            // 渲染圖表
                            createChart(data, chartType, chartTheme);
                            
                            // 顯示圖表區域
                            const chartContainer = document.getElementById('chartContainer');
                            if (chartContainer) chartContainer.classList.remove('hidden');
                            
                            // 設置圖表標題
                            const chartTitle = document.getElementById('chartTitle');
                            if (chartTitle) {
                                chartTitle.textContent = data.chartTitle || `${currentDataFile} 圖表`;
                            }
                            
                            // 獲取並顯示文件結構信息
                            const structure = await fetchFileStructure(currentDataFile, currentDataType);
                            updateDataInfo(structure);
                            
                            // 保存數據列信息，用於 OLAP 操作
                            dataColumnInfo = structure;
                            
                            // 更新 OLAP 操作的欄位選項
                            updateOlapFieldOptions(structure);
                            
                            // 顯示 OLAP 操作區域
                            document.getElementById('olapOperationArea').classList.remove('hidden');
                        }
                    } catch (error) {
                        console.error('載入上傳檔案錯誤:', error);
                        showError(`載入上傳檔案錯誤: ${error.message}`);
                    }
                }
            }
        } catch (error) {
            console.error('檔案上傳錯誤:', error);
            showError(`檔案上傳錯誤: ${error.message}`);
        }
    });
    
    // 設置下載 PNG 按鈕事件
    document.getElementById('capturePngBtn').addEventListener('click', () => {
        if (!myChart) {
            showError('請先選擇資料來源並生成圖表');
            return;
        }
        captureChart('image/png');
    });
    
    // 設置下載 WebP 按鈕事件
    document.getElementById('captureWebpBtn').addEventListener('click', () => {
        if (!myChart) {
            showError('請先選擇資料來源並生成圖表');
            return;
        }
        captureChart('image/webp');
    });
    
    // 設置上傳按鈕事件
    document.getElementById('uploadChartBtn').addEventListener('click', () => {
        if (!myChart) {
            showError('請先選擇資料來源並生成圖表');
            return;
        }
        uploadChart();
    });
    
    // 設置顯示資料摘要按鈕事件
    const toggleDataInfoBtn = document.getElementById('toggleDataInfo');
    const dataInfoDiv = document.getElementById('dataInfo');
    
    if (toggleDataInfoBtn && dataInfoDiv) {
        toggleDataInfoBtn.addEventListener('click', () => {
            if (dataInfoDiv.classList.contains('hidden')) {
                dataInfoDiv.classList.remove('hidden');
                toggleDataInfoBtn.textContent = '隱藏資料摘要';
            } else {
                dataInfoDiv.classList.add('hidden');
                toggleDataInfoBtn.textContent = '顯示資料摘要';
            }
        });
    }
    
    // 設置顯示 JSON 格式範例按鈕事件
    const showJsonFormatBtn = document.getElementById('showJsonFormatBtn');
    const jsonFormatExample = document.getElementById('jsonFormatExample');
    
    if (showJsonFormatBtn && jsonFormatExample) {
        showJsonFormatBtn.addEventListener('click', () => {
            if (jsonFormatExample.classList.contains('hidden')) {
                jsonFormatExample.classList.remove('hidden');
                showJsonFormatBtn.textContent = '隱藏 Chart.js JSON 格式範例';
            } else {
                jsonFormatExample.classList.add('hidden');
                showJsonFormatBtn.textContent = '顯示 Chart.js JSON 格式範例';
            }
        });
    }
    
    // 設置 CSV 匯出按鈕事件
    document.getElementById('exportCsvBtn').addEventListener('click', () => {
        if (!myChart) {
            showError('請先選擇資料來源並生成圖表');
            return;
        }
        exportDataToCSV();
    });
    
    // 設置 JSON 匯出按鈕事件
    document.getElementById('exportJsonBtn').addEventListener('click', () => {
        if (!myChart) {
            showError('請先選擇資料來源並生成圖表');
            return;
        }
        exportDataToJSON();
    });
    
    // 設置 Excel 匯出按鈕事件
    document.getElementById('exportExcelBtn').addEventListener('click', () => {
        if (!myChart) {
            showError('請先選擇資料來源並生成圖表');
            return;
        }
        exportDataToExcel();
    });
    
    // 設置下載 PNG 按鈕事件
    document.getElementById('capturePngBtn').addEventListener('click', () => {
        if (!myChart) {
            showError('請先選擇資料來源並生成圖表');
            return;
        }
        captureChart('image/png');
    });

    // 檔案上傳區塊初始化
    const uploadNewFileSection = document.getElementById('uploadNewFileSection');
    
    // 確保 uploadNewFileSection 在頁面加載時隱藏
    if (uploadNewFileSection) {
        uploadNewFileSection.classList.add('hidden');
    }
    
    // 設置顯示上傳區域按鈕事件
    // ...existing code...
}

/**
 * 更新 OLAP 欄位選項
 * @param {Object} structure - 文件結構信息
 */
function updateOlapFieldOptions(structure) {
    if (!structure || !structure.columns) return;
    
    // 數值欄位清單
    const numericColumns = structure.columns.filter(col => 
        col.dtype.includes('int') || 
        col.dtype.includes('float') || 
        col.dtype.includes('double')
    );
    
    // 日期欄位清單
    const dateColumns = structure.columns.filter(col => 
        col.dtype.includes('date') || 
        col.dtype.includes('time') || 
        col.name.toLowerCase().includes('date') || 
        col.name.toLowerCase().includes('time')
    );
    
    // 分類欄位清單
    const categoricalColumns = structure.columns.filter(col => 
        !numericColumns.includes(col) && !dateColumns.includes(col)
    );
    
    // 更新數值欄位輸入框的佔位符和自動完成
    const valueColumnInput = document.getElementById('valueColumn');
    if (valueColumnInput) {
        if (numericColumns.length > 0) {
            valueColumnInput.placeholder = `例如: ${numericColumns[0].name}`;
            // 創建 datalist 元素
            let datalist = document.getElementById('valueColumnOptions');
            if (!datalist) {
                datalist = document.createElement('datalist');
                datalist.id = 'valueColumnOptions';
                valueColumnInput.setAttribute('list', 'valueColumnOptions');
                valueColumnInput.parentNode.appendChild(datalist);
            } else {
                datalist.innerHTML = '';
            }
            
            // 填充 datalist
            numericColumns.forEach(col => {
                const option = document.createElement('option');
                option.value = col.name;
                datalist.appendChild(option);
            });
        }
    }
    
    // 更新分組欄位輸入框
    const groupColumnsInput = document.getElementById('groupColumns');
    if (groupColumnsInput) {
        // 優先選擇日期和分類欄位
        const suggestedColumns = [...dateColumns, ...categoricalColumns];
        if (suggestedColumns.length > 0) {
            groupColumnsInput.placeholder = `例如: ${suggestedColumns[0].name}`;
            
            // 創建 datalist 元素
            let datalist = document.getElementById('groupColumnsOptions');
            if (!datalist) {
                datalist = document.createElement('datalist');
                datalist.id = 'groupColumnsOptions';
                groupColumnsInput.setAttribute('list', 'groupColumnsOptions');
                groupColumnsInput.parentNode.appendChild(datalist);
            } else {
                datalist.innerHTML = '';
            }
            
            // 填充 datalist
            suggestedColumns.forEach(col => {
                const option = document.createElement('option');
                option.value = col.name;
                datalist.appendChild(option);
            });
        }
    }
    
    // 更新透視表欄位
    const pivotIndexInput = document.getElementById('pivotIndex');
    const pivotColumnsInput = document.getElementById('pivotColumns');
    
    if (pivotIndexInput && categoricalColumns.length > 0) {
        pivotIndexInput.placeholder = `例如: ${categoricalColumns[0].name}`;
    }
    
    if (pivotColumnsInput && categoricalColumns.length > 1) {
        pivotColumnsInput.placeholder = `例如: ${categoricalColumns[1].name}`;
    }
}

/**
 * 更新圖表
 */
async function updateChart() {
    if (!currentDataFile || !currentDataType) {
        return;
    }
    
    // 獲取文件數據
    const data = await fetchFileData(currentDataFile, currentDataType);
    if (data) {
        // 渲染圖表
        createChart(data, currentChartType, currentChartTheme);
    }
}

/**
 * 匯出圖表資料為 CSV 格式
 */
function exportDataToCSV() {
    if (!myChart || !myChart.data) {
        showError('沒有可匯出的圖表資料');
        return;
    }
    
    const data = myChart.data;
    const labels = data.labels;
    const datasets = data.datasets;
    
    // 創建 CSV 資料
    let csvContent = "data:text/csv;charset=utf-8,";
    
    // 添加標題行
    let headerRow = ["labels"];
    datasets.forEach(dataset => headerRow.push(dataset.label || "Data"));
    csvContent += headerRow.join(",") + "\r\n";
    
    // 添加資料行
    labels.forEach((label, index) => {
        let row = [label];
        datasets.forEach(dataset => {
            row.push(dataset.data[index]);
        });
        csvContent += row.join(",") + "\r\n";
    });
    
    // 建立下載連結
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `chart_data_${new Date().toISOString().slice(0,10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

/**
 * 匯出圖表資料為 JSON 格式
 */
function exportDataToJSON() {
    if (!myChart || !myChart.data) {
        showError('沒有可匯出的圖表資料');
        return;
    }
    
    // 準備 JSON 資料
    const chartData = {
        type: myChart.config.type,
        labels: myChart.data.labels,
        datasets: myChart.data.datasets,
        chartTitle: document.getElementById('chartTitle').textContent || '圖表'
    };
    
    // 轉換為 JSON 字串
    const jsonString = JSON.stringify(chartData, null, 2);
    const blob = new Blob([jsonString], {type: 'application/json'});
    const url = URL.createObjectURL(blob);
    
    // 建立下載連結
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `chart_data_${new Date().toISOString().slice(0,10)}.json`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

/**
 * 匯出圖表資料為 Excel 格式
 */
function exportDataToExcel() {
    if (!myChart || !myChart.data) {
        showError('沒有可匯出的圖表資料');
        return;
    }
    
    // 通過 API 匯出 Excel
    try {
        const chartData = {
            type: myChart.config.type,
            labels: myChart.data.labels,
            datasets: myChart.data.datasets,
            chartTitle: document.getElementById('chartTitle').textContent || '圖表'
        };
        
        fetch('/api/export-excel/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(chartData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`API 請求失敗: ${response.status} ${response.statusText}`);
            }
            return response.blob();
        })
        .then(blob => {
            // 建立 Blob URL
            const url = window.URL.createObjectURL(blob);
            
            // 建立下載連結
            const link = document.createElement("a");
            link.href = url;
            link.download = `chart_data_${new Date().toISOString().slice(0,10)}.xlsx`;
            document.body.appendChild(link);
            link.click();
            
            // 清理
            window.URL.revokeObjectURL(url);
            document.body.removeChild(link);
        })
        .catch(error => {
            console.error('匯出 Excel 錯誤:', error);
            showError(`匯出 Excel 錯誤: ${error.message}`);
            
            // 如果 API 失敗，嘗試客戶端下載 CSV 作為替代方案
            showError('匯出 Excel 失敗，將以 CSV 格式匯出', 3000);
            setTimeout(() => {
                exportDataToCSV();
            }, 1000);
        });
    } catch (error) {
        console.error('匯出 Excel 錯誤:', error);
        showError(`匯出 Excel 錯誤: ${error.message}`);
    }
}

// 頁面加載完成後初始化
document.addEventListener('DOMContentLoaded', initPage);
