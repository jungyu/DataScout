/**
 * 圖表主題管理模組
 */

// 圖表主題設定
export const CHART_THEMES = {
    default: {
        backgroundColor: 'rgba(255, 255, 255, 0)',
        fontColor: '#666',
        gridColor: 'rgba(0, 0, 0, 0.1)',
        titleColor: '#333',
        colors: [
            { background: 'rgba(75, 192, 192, 0.6)', border: 'rgba(75, 192, 192, 1)' },
            { background: 'rgba(255, 99, 132, 0.6)', border: 'rgba(255, 99, 132, 1)' },
            { background: 'rgba(54, 162, 235, 0.6)', border: 'rgba(54, 162, 235, 1)' },
            { background: 'rgba(255, 206, 86, 0.6)', border: 'rgba(255, 206, 86, 1)' },
            { background: 'rgba(153, 102, 255, 0.6)', border: 'rgba(153, 102, 255, 1)' },
            { background: 'rgba(255, 159, 64, 0.6)', border: 'rgba(255, 159, 64, 1)' },
        ]
    },
    light: {
        backgroundColor: 'rgba(255, 255, 255, 0)',
        fontColor: '#555',
        gridColor: 'rgba(0, 0, 0, 0.05)',
        titleColor: '#333',
        colors: [
            { background: 'rgba(75, 192, 192, 0.5)', border: 'rgba(75, 192, 192, 0.8)' },
            { background: 'rgba(255, 99, 132, 0.5)', border: 'rgba(255, 99, 132, 0.8)' },
            { background: 'rgba(54, 162, 235, 0.5)', border: 'rgba(54, 162, 235, 0.8)' },
            { background: 'rgba(255, 206, 86, 0.5)', border: 'rgba(255, 206, 86, 0.8)' },
            { background: 'rgba(153, 102, 255, 0.5)', border: 'rgba(153, 102, 255, 0.8)' },
            { background: 'rgba(255, 159, 64, 0.5)', border: 'rgba(255, 159, 64, 0.8)' },
        ]
    },
    dark: {
        backgroundColor: 'rgba(40, 44, 52, 0)',
        fontColor: '#ddd',
        gridColor: 'rgba(255, 255, 255, 0.1)',
        titleColor: '#fff',
        colors: [
            { background: 'rgba(95, 212, 212, 0.6)', border: 'rgba(95, 212, 212, 1)' },
            { background: 'rgba(255, 119, 152, 0.6)', border: 'rgba(255, 119, 152, 1)' },
            { background: 'rgba(74, 182, 255, 0.6)', border: 'rgba(74, 182, 255, 1)' },
            { background: 'rgba(255, 226, 106, 0.6)', border: 'rgba(255, 226, 106, 1)' },
            { background: 'rgba(173, 122, 255, 0.6)', border: 'rgba(173, 122, 255, 1)' },
            { background: 'rgba(255, 179, 84, 0.6)', border: 'rgba(255, 179, 84, 1)' },
        ]
    },
    pastel: {
        backgroundColor: 'rgba(250, 250, 250, 0)',
        fontColor: '#6c757d',
        gridColor: 'rgba(188, 223, 245, 0.5)',
        titleColor: '#5b8c85',
        colors: [
            { background: 'rgba(142, 236, 245, 0.6)', border: 'rgba(142, 236, 245, 0.9)' },
            { background: 'rgba(255, 183, 197, 0.6)', border: 'rgba(255, 183, 197, 0.9)' },
            { background: 'rgba(178, 223, 255, 0.6)', border: 'rgba(178, 223, 255, 0.9)' },
            { background: 'rgba(255, 236, 179, 0.6)', border: 'rgba(255, 236, 179, 0.9)' },
            { background: 'rgba(209, 188, 255, 0.6)', border: 'rgba(209, 188, 255, 0.9)' },
            { background: 'rgba(255, 218, 188, 0.6)', border: 'rgba(255, 218, 188, 0.9)' },
        ]
    },
    vibrant: {
        backgroundColor: 'rgba(255, 255, 255, 0)',
        fontColor: '#333',
        gridColor: 'rgba(63, 81, 181, 0.2)',
        titleColor: '#ff5722',
        colors: [
            { background: 'rgba(0, 230, 118, 0.7)', border: 'rgba(0, 230, 118, 1)' },
            { background: 'rgba(255, 23, 68, 0.7)', border: 'rgba(255, 23, 68, 1)' },
            { background: 'rgba(41, 121, 255, 0.7)', border: 'rgba(41, 121, 255, 1)' },
            { background: 'rgba(255, 196, 0, 0.7)', border: 'rgba(255, 196, 0, 1)' },
            { background: 'rgba(123, 31, 162, 0.7)', border: 'rgba(123, 31, 162, 1)' },
            { background: 'rgba(255, 111, 0, 0.7)', border: 'rgba(255, 111, 0, 1)' },
        ]
    }
};

/**
 * 根據圖表類型獲取主題數據集樣式
 * @param {string} theme - 主題名稱
 * @param {string} chartType - 圖表類型
 * @param {number} datasetCount - 數據集數量
 * @returns {Array} - 數據集樣式陣列
 */
export function getDatasetStyles(theme, chartType, datasetCount) {
    // 獲取主題配置
    const themeConfig = CHART_THEMES[theme] || CHART_THEMES.default;
    const styles = [];
    
    // 根據數據集數量生成樣式
    for (let i = 0; i < datasetCount; i++) {
        const colorIndex = i % themeConfig.colors.length;
        const color = themeConfig.colors[colorIndex];
        
        // 根據圖表類型調整樣式
        switch (chartType) {
            case 'line':
                styles.push({
                    backgroundColor: color.background,
                    borderColor: color.border,
                    borderWidth: 2,
                    pointBackgroundColor: color.border,
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: color.border,
                    pointRadius: 3,
                    pointHoverRadius: 5,
                    fill: false
                });
                break;
                
            case 'bar':
                styles.push({
                    backgroundColor: color.background,
                    borderColor: color.border,
                    borderWidth: 1,
                    hoverBackgroundColor: color.border,
                    hoverBorderColor: color.border
                });
                break;
                
            case 'pie':
            case 'doughnut':
            case 'polarArea':
                // 餅圖等需要為每個數據點提供不同的顏色
                const backgroundColors = [];
                const borderColors = [];
                
                for (let j = 0; j < themeConfig.colors.length; j++) {
                    backgroundColors.push(themeConfig.colors[j].background);
                    borderColors.push(themeConfig.colors[j].border);
                }
                
                styles.push({
                    backgroundColor: backgroundColors,
                    borderColor: borderColors,
                    borderWidth: 1
                });
                break;
                
            case 'radar':
                styles.push({
                    backgroundColor: color.background,
                    borderColor: color.border,
                    borderWidth: 2,
                    pointBackgroundColor: color.border,
                    pointBorderColor: '#fff',
                    pointHoverBackgroundColor: '#fff',
                    pointHoverBorderColor: color.border
                });
                break;
                
            case 'scatter':
                styles.push({
                    backgroundColor: color.border,
                    borderColor: color.border,
                    pointRadius: 5,
                    pointHoverRadius: 7
                });
                break;
                
            case 'bubble':
                styles.push({
                    backgroundColor: color.background,
                    borderColor: color.border,
                    borderWidth: 1,
                    hoverBackgroundColor: color.border,
                    hoverBorderColor: color.border
                });
                break;
                
            default:
                styles.push({
                    backgroundColor: color.background,
                    borderColor: color.border,
                    borderWidth: 1
                });
        }
    }
    
    return styles;
}

/**
 * 根據主題獲取圖表全局配置
 * @param {string} theme - 主題名稱
 * @param {string} chartType - 圖表類型
 * @returns {Object} - 圖表配置對象
 */
export function getChartConfig(theme, chartType) {
    // 獲取主題配置
    const themeConfig = CHART_THEMES[theme] || CHART_THEMES.default;
    
    // 基本配置
    const config = {
        plugins: {
            legend: {
                labels: {
                    color: themeConfig.fontColor,
                    font: {
                        family: "'Noto Sans TC', sans-serif"
                    }
                }
            },
            title: {
                color: themeConfig.titleColor,
                font: {
                    family: "'Noto Sans TC', sans-serif",
                    size: 16,
                    weight: 'bold'
                }
            },
            tooltip: {
                backgroundColor: theme === 'dark' ? 'rgba(50, 50, 50, 0.8)' : 'rgba(255, 255, 255, 0.8)',
                titleColor: theme === 'dark' ? '#fff' : '#333',
                bodyColor: theme === 'dark' ? '#eee' : '#555',
                borderColor: theme === 'dark' ? 'rgba(255, 255, 255, 0.2)' : 'rgba(0, 0, 0, 0.1)',
                borderWidth: 1
            }
        },
        scales: {}
    };
    
    // 根據圖表類型調整配置
    switch (chartType) {
        case 'line':
        case 'bar':
            config.scales.x = {
                grid: {
                    color: themeConfig.gridColor
                },
                ticks: {
                    color: themeConfig.fontColor
                }
            };
            config.scales.y = {
                grid: {
                    color: themeConfig.gridColor
                },
                ticks: {
                    color: themeConfig.fontColor
                }
            };
            break;
            
        case 'radar':
            config.scales.r = {
                angleLines: {
                    color: themeConfig.gridColor
                },
                grid: {
                    color: themeConfig.gridColor
                },
                pointLabels: {
                    color: themeConfig.fontColor
                },
                ticks: {
                    color: themeConfig.fontColor,
                    backdropColor: 'transparent'
                }
            };
            break;
            
        case 'scatter':
        case 'bubble':
            config.scales.x = {
                grid: {
                    color: themeConfig.gridColor
                },
                ticks: {
                    color: themeConfig.fontColor
                }
            };
            config.scales.y = {
                grid: {
                    color: themeConfig.gridColor
                },
                ticks: {
                    color: themeConfig.fontColor
                }
            };
            break;
    }
    
    return config;
}
