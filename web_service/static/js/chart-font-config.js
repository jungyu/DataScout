
/**
 * DataScout ApexCharts 中文字型配置
 * 統一配置所有 ApexCharts 圖表的字型設定
 */

// 全域字型配置
window.DataScoutChartConfig = {
    // 基礎字型設定
    fonts: {
        primary: "'Noto Sans TC', 'PingFang TC', 'Microsoft JhengHei', 'Heiti TC', sans-serif",
        fallback: "Arial, sans-serif",
        mono: "'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace"
    },
    
    // 預設 ApexCharts 配置
    getDefaultConfig: function() {
        return {
            chart: {
                fontFamily: this.fonts.primary,
                toolbar: {
                    show: true
                }
            },
            title: {
                style: {
                    fontFamily: this.fonts.primary,
                    fontSize: '16px',
                    fontWeight: '600',
                    color: '#263238'
                }
            },
            subtitle: {
                style: {
                    fontFamily: this.fonts.primary,
                    fontSize: '14px',
                    color: '#607d8b'
                }
            },
            legend: {
                fontFamily: this.fonts.primary,
                fontSize: '12px'
            },
            dataLabels: {
                style: {
                    fontFamily: this.fonts.primary,
                    fontSize: '11px'
                }
            },
            xaxis: {
                labels: {
                    style: {
                        fontFamily: this.fonts.primary,
                        fontSize: '12px',
                        colors: '#607d8b'
                    }
                },
                title: {
                    style: {
                        fontFamily: this.fonts.primary,
                        fontSize: '13px',
                        color: '#607d8b'
                    }
                }
            },
            yaxis: {
                labels: {
                    style: {
                        fontFamily: this.fonts.primary,
                        fontSize: '12px',
                        colors: '#607d8b'
                    }
                },
                title: {
                    style: {
                        fontFamily: this.fonts.primary,
                        fontSize: '13px',
                        color: '#607d8b'
                    }
                }
            },
            tooltip: {
                style: {
                    fontFamily: this.fonts.primary,
                    fontSize: '12px'
                }
            }
        };
    },
    
    // 合併自訂配置與預設配置
    mergeConfig: function(customConfig) {
        const defaultConfig = this.getDefaultConfig();
        return this.deepMerge(defaultConfig, customConfig);
    },
    
    // 深度合併物件
    deepMerge: function(target, source) {
        for (const key in source) {
            if (source[key] && typeof source[key] === 'object' && !Array.isArray(source[key])) {
                if (!target[key]) target[key] = {};
                this.deepMerge(target[key], source[key]);
            } else {
                target[key] = source[key];
            }
        }
        return target;
    },
    
    // 常用顏色配置
    colors: {
        primary: ['#1976d2', '#388e3c', '#f57c00', '#d32f2f', '#7b1fa2'],
        success: ['#4caf50', '#66bb6a', '#81c784', '#a5d6a7', '#c8e6c9'],
        warning: ['#ff9800', '#ffb74d', '#ffcc02', '#ffd54f', '#ffe082'],
        error: ['#f44336', '#ef5350', '#e57373', '#ef9a9a', '#ffcdd2'],
        info: ['#2196f3', '#42a5f5', '#64b5f6', '#90caf9', '#bbdefb'],
        neutral: ['#607d8b', '#78909c', '#90a4ae', '#b0bec5', '#cfd8dc']
    }
};

// 初始化函數
window.initDataScoutCharts = function() {
    console.log('DataScout 圖表字型配置已載入');
    
    // 檢查是否有 ApexCharts
    if (typeof ApexCharts !== 'undefined') {
        console.log('ApexCharts 已就緒，字型配置生效');
    } else {
        console.warn('ApexCharts 未載入，請確保已引入 ApexCharts 庫');
    }
};

// 頁面載入完成後自動初始化
document.addEventListener('DOMContentLoaded', function() {
    window.initDataScoutCharts();
});

// 範例使用方法
window.createExampleChart = function(elementId) {
    const config = window.DataScoutChartConfig.mergeConfig({
        series: [{
            name: '銷售額',
            data: [30, 40, 35, 50, 49, 60, 70, 91, 125]
        }],
        chart: {
            type: 'line',
            height: 350
        },
        title: {
            text: '月度銷售趨勢圖'
        },
        xaxis: {
            categories: ['一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月']
        }
    });
    
    const chart = new ApexCharts(document.querySelector(elementId), config);
    chart.render();
    
    return chart;
};
