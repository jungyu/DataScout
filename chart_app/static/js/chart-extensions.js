/**
 * Chart.js 擴展函數庫
 * 用於增強 Chart.js 的功能，提供自定義圖表類型和輔助功能
 */

(function() {
    'use strict';
    
    // 確保 Chart 存在
    if (typeof Chart === 'undefined') {
        console.error('Chart.js 未載入，擴展將不可用');
        return;
    }
    
    console.log('Chart.js 擴展模組已載入');

    // 註冊全局默認配置
    Chart.defaults.responsive = true;
    Chart.defaults.maintainAspectRatio = false;
    
    // 添加金融圖表的插件支持
    if (Chart.registry && !Chart.registry.controllers.candlestick && window.CandlestickController) {
        Chart.register(window.CandlestickController);
        console.log('已註冊 CandlestickController');
    }
    
    if (Chart.registry && !Chart.registry.controllers.ohlc && window.OhlcController) {
        Chart.register(window.OhlcController);
        console.log('已註冊 OhlcController');
    }
    
    // 添加公用工具函數
    const ChartExtensions = {
        /**
         * 優化圖表配置以改善顯示效果
         * @param {Object} config - Chart.js 配置對象
         * @param {string} theme - 主題名稱 ('light', 'dark', 'blue', 'green')
         * @returns {Object} 優化後的配置
         */
        optimizeConfig: function(config, theme = 'light') {
            if (!config) return {};
            
            // 深拷貝配置以避免修改原始對象
            const newConfig = JSON.parse(JSON.stringify(config));
            
            // 設置主題顏色
            const themes = {
                light: {
                    backgroundColor: 'rgba(255, 255, 255, 0.8)',
                    borderColor: '#ddd',
                    textColor: '#333',
                    gridColor: '#eee'
                },
                dark: {
                    backgroundColor: 'rgba(35, 35, 35, 0.8)',
                    borderColor: '#444',
                    textColor: '#eee',
                    gridColor: '#444'
                },
                blue: {
                    backgroundColor: 'rgba(231, 246, 255, 0.8)',
                    borderColor: '#b0d8ff',
                    textColor: '#0056b3',
                    gridColor: '#deefff'
                },
                green: {
                    backgroundColor: 'rgba(232, 255, 235, 0.8)',
                    borderColor: '#b1e5b7',
                    textColor: '#0a6b20',
                    gridColor: '#e0f2e2'
                }
            };
            
            const themeColors = themes[theme] || themes.light;
            
            // 應用主題顏色
            if (!newConfig.options) newConfig.options = {};
            if (!newConfig.options.plugins) newConfig.options.plugins = {};
            if (!newConfig.options.scales) newConfig.options.scales = {};
            
            // 配置標題
            if (!newConfig.options.plugins.title) newConfig.options.plugins.title = {};
            newConfig.options.plugins.title.color = themeColors.textColor;
            
            // 配置圖例
            if (!newConfig.options.plugins.legend) newConfig.options.plugins.legend = {};
            newConfig.options.plugins.legend.labels = {
                color: themeColors.textColor
            };
            
            // 配置坐標軸
            if (newConfig.options.scales.x) {
                newConfig.options.scales.x.grid = {
                    color: themeColors.gridColor
                };
                newConfig.options.scales.x.ticks = {
                    color: themeColors.textColor
                };
            }
            
            if (newConfig.options.scales.y) {
                newConfig.options.scales.y.grid = {
                    color: themeColors.gridColor
                };
                newConfig.options.scales.y.ticks = {
                    color: themeColors.textColor
                };
            }
            
            // 為雷達和極座標圖表配置 r 軸
            if (newConfig.options.scales.r) {
                newConfig.options.scales.r.grid = {
                    color: themeColors.gridColor
                };
                newConfig.options.scales.r.ticks = {
                    color: themeColors.textColor
                };
            }
            
            // 如果需要，為數據集添加默認顏色
            if (newConfig.data && newConfig.data.datasets) {
                const defaultColors = [
                    'rgba(75, 192, 192, 0.6)',    // 綠松石色
                    'rgba(153, 102, 255, 0.6)',   // 紫色
                    'rgba(255, 159, 64, 0.6)',    // 橙色
                    'rgba(54, 162, 235, 0.6)',    // 藍色
                    'rgba(255, 99, 132, 0.6)',    // 粉色
                    'rgba(255, 206, 86, 0.6)'     // 黃色
                ];
                
                newConfig.data.datasets.forEach((dataset, index) => {
                    if (!dataset.backgroundColor) {
                        dataset.backgroundColor = defaultColors[index % defaultColors.length];
                    }
                    if (!dataset.borderColor && dataset.backgroundColor) {
                        dataset.borderColor = dataset.backgroundColor.replace('0.6', '1.0');
                    }
                });
            }
            
            return newConfig;
        },
        
        /**
         * 自動檢測適合數據的圖表類型
         * @param {Object} data - 圖表資料
         * @returns {string} 建議的圖表類型
         */
        suggestChartType: function(data) {
            if (!data || !data.datasets || data.datasets.length === 0) {
                return 'bar'; // 默認為柱狀圖
            }
            
            // 檢查數據點格式
            const firstDataset = data.datasets[0];
            
            // 檢查是否有 OHLC 格式數據
            if (firstDataset.data && firstDataset.data[0] && 
               (firstDataset.data[0].o !== undefined || firstDataset.data[0].open !== undefined) &&
               (firstDataset.data[0].h !== undefined || firstDataset.data[0].high !== undefined) &&
               (firstDataset.data[0].l !== undefined || firstDataset.data[0].low !== undefined) &&
               (firstDataset.data[0].c !== undefined || firstDataset.data[0].close !== undefined)) {
                return 'candlestick';
            }
            
            // 檢查是否有座標點數據 (x, y)
            if (firstDataset.data && firstDataset.data[0] && 
                firstDataset.data[0].x !== undefined && firstDataset.data[0].y !== undefined) {
                // 檢查是否有氣泡半徑
                if (firstDataset.data[0].r !== undefined) {
                    return 'bubble';
                }
                return 'scatter';
            }
            
            // 檢查數據集數量
            if (data.datasets.length >= 5) {
                return 'radar'; // 很多數據集時，雷達圖可能更適合
            }
            
            // 檢查標籤數量
            if (data.labels && data.labels.length <= 8) {
                return 'bar'; // 標籤少時，使用柱狀圖
            } else {
                return 'line'; // 標籤多時，使用折線圖
            }
        },
        
        /**
         * 創建混合類型圖表 (例如柱狀圖+折線圖)
         * @param {string} canvasId - Canvas 元素 ID
         * @param {Object} data - 圖表資料
         * @param {string} primaryType - 主要圖表類型
         * @param {string} secondaryType - 次要圖表類型
         * @param {Object} options - 額外選項
         * @returns {Chart} 創建的圖表實例
         */
        createMixedChart: function(canvasId, data, primaryType, secondaryType, options = {}) {
            const canvas = document.getElementById(canvasId);
            if (!canvas) {
                console.error(`找不到ID為 ${canvasId} 的canvas元素`);
                return null;
            }
            
            // 深拷貝數據以避免修改原始對象
            const chartData = JSON.parse(JSON.stringify(data));
            
            // 設置主圖表類型
            chartData.datasets[0].type = primaryType;
            
            // 如果有多個數據集，設置次圖表類型
            if (chartData.datasets.length > 1) {
                for (let i = 1; i < chartData.datasets.length; i++) {
                    chartData.datasets[i].type = secondaryType;
                }
            }
            
            // 創建圖表
            const ctx = canvas.getContext('2d');
            return new Chart(ctx, {
                data: chartData,
                options: options
            });
        },
        
        /**
         * 格式化數據標籤
         * @param {number|Date} value - 要格式化的值
         * @param {string} type - 值的類型 ('number', 'currency', 'percent', 'date')
         * @param {Object} options - 格式化選項
         * @returns {string} 格式化後的值
         */
        formatLabel: function(value, type = 'number', options = {}) {
            if (value === null || value === undefined) {
                return '無數據';
            }
            
            switch (type) {
                case 'number':
                    const precision = options.precision !== undefined ? options.precision : 2;
                    return Number(value).toFixed(precision);
                    
                case 'currency':
                    const currency = options.currency || 'TWD';
                    const locale = options.locale || 'zh-TW';
                    return new Intl.NumberFormat(locale, {
                        style: 'currency',
                        currency: currency
                    }).format(value);
                    
                case 'percent':
                    return `${(Number(value) * 100).toFixed(options.precision || 2)}%`;
                    
                case 'date':
                    const dateValue = value instanceof Date ? value : new Date(value);
                    const dateFormat = options.format || 'YYYY-MM-DD';
                    
                    // 簡單的日期格式化
                    const year = dateValue.getFullYear();
                    const month = (dateValue.getMonth() + 1).toString().padStart(2, '0');
                    const day = dateValue.getDate().toString().padStart(2, '0');
                    const hours = dateValue.getHours().toString().padStart(2, '0');
                    const minutes = dateValue.getMinutes().toString().padStart(2, '0');
                    
                    let formatted = dateFormat
                        .replace('YYYY', year)
                        .replace('MM', month)
                        .replace('DD', day)
                        .replace('HH', hours)
                        .replace('mm', minutes);
                        
                    return formatted;
                    
                default:
                    return String(value);
            }
        }
    };
    
    // 將擴展公開為全局對象
    window.ChartExtensions = ChartExtensions;
    
    console.log('Chart.js 擴展模組已初始化完成');
})();
