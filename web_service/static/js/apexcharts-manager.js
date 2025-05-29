/**
 * DataScout ApexCharts 管理器
 * 統一管理所有 ApexCharts 圖表的創建、配置和渲染
 * 
 * 功能：
 * - 自動字型配置（優先使用思源黑體字）
 * - 安全的圖表初始化
 * - 統一的主題和樣式
 * - 錯誤處理和重試機制
 */

class ApexChartsManager {
    constructor() {
        this.charts = new Map(); // 存儲所有圖表實例
        this.defaultConfig = this.getBaseConfig();
        this.isApexChartsReady = false;
        
        // 初始化
        this.init();
    }
    
    /**
     * 初始化管理器
     */
    async init() {
        console.log('ApexCharts 管理器初始化中...');
        
        try {
            await this.waitForApexCharts();
            await this.loadGoogleFonts();
            this.setupGlobalDefaults();
            this.isApexChartsReady = true;
            console.log('ApexCharts 管理器初始化完成');
        } catch (error) {
            console.error('ApexCharts 管理器初始化失敗:', error);
        }
    }
    
    /**
     * 等待 ApexCharts 庫加載完成
     */
    waitForApexCharts() {
        return new Promise((resolve, reject) => {
            let attempts = 0;
            const maxAttempts = 50;
            
            const checkApexCharts = () => {
                attempts++;
                
                if (window.ApexCharts && typeof window.ApexCharts === 'function') {
                    console.log('ApexCharts 庫已成功加載');
                    resolve(window.ApexCharts);
                } else if (attempts >= maxAttempts) {
                    console.error('ApexCharts 庫加載失敗，已達到最大嘗試次數');
                    reject(new Error('ApexCharts 庫加載超時'));
                } else {
                    console.log(`正在等待 ApexCharts 庫加載... (嘗試 ${attempts}/${maxAttempts})`);
                    setTimeout(checkApexCharts, 100);
                }
            };
            
            checkApexCharts();
        });
    }
    
    /**
     * 載入 Google Fonts（思源黑體字）
     */
    async loadGoogleFonts() {
        return new Promise((resolve) => {
            // 檢查是否已載入
            if (document.querySelector('link[href*="Noto+Sans+TC"]')) {
                resolve();
                return;
            }
            
            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = 'https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500;600;700&display=swap';
            
            link.onload = () => {
                console.log('思源黑體字 Google Fonts 已載入');
                resolve();
            };
            
            link.onerror = () => {
                console.warn('思源黑體字 Google Fonts 載入失敗，將使用本地字型');
                resolve();
            };
            
            document.head.appendChild(link);
        });
    }
    
    /**
     * 設定全域預設配置
     */
    setupGlobalDefaults() {
        if (window.ApexCharts && window.ApexCharts.setGlobalOptions) {
            window.ApexCharts.setGlobalOptions({
                chart: {
                    fontFamily: this.getFontFamily()
                }
            });
        }
    }
    
    /**
     * 取得字型家族設定
     */
    getFontFamily() {
        return "'Noto Sans TC', 'Noto Sans CJK TC', 'PingFang TC', 'Microsoft JhengHei', 'Heiti TC', 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif";
    }
    
    /**
     * 取得基礎配置
     */
    getBaseConfig() {
        const fontFamily = this.getFontFamily();
        
        return {
            chart: {
                fontFamily: fontFamily,
                toolbar: {
                    show: true,
                    tools: {
                        download: true,
                        selection: true,
                        zoom: true,
                        zoomin: true,
                        zoomout: true,
                        pan: true,
                        reset: true
                    }
                },
                animations: {
                    enabled: true,
                    easing: 'easeinout',
                    speed: 800
                }
            },
            theme: {
                mode: 'light',
                palette: 'palette1'
            },
            title: {
                style: {
                    fontFamily: fontFamily,
                    fontSize: '18px',
                    fontWeight: '600',
                    color: '#263238'
                }
            },
            subtitle: {
                style: {
                    fontFamily: fontFamily,
                    fontSize: '14px',
                    fontWeight: '400',
                    color: '#607d8b'
                }
            },
            legend: {
                fontFamily: fontFamily,
                fontSize: '13px',
                fontWeight: '400'
            },
            dataLabels: {
                style: {
                    fontFamily: fontFamily,
                    fontSize: '11px',
                    fontWeight: '500'
                }
            },
            xaxis: {
                labels: {
                    style: {
                        fontFamily: fontFamily,
                        fontSize: '12px',
                        fontWeight: '400',
                        colors: '#607d8b'
                    }
                },
                title: {
                    style: {
                        fontFamily: fontFamily,
                        fontSize: '13px',
                        fontWeight: '500',
                        color: '#455a64'
                    }
                }
            },
            yaxis: {
                labels: {
                    style: {
                        fontFamily: fontFamily,
                        fontSize: '12px',
                        fontWeight: '400',
                        colors: '#607d8b'
                    }
                },
                title: {
                    style: {
                        fontFamily: fontFamily,
                        fontSize: '13px',
                        fontWeight: '500',
                        color: '#455a64'
                    }
                }
            },
            tooltip: {
                style: {
                    fontFamily: fontFamily,
                    fontSize: '12px'
                }
            },
            grid: {
                borderColor: '#e0e0e0',
                strokeDashArray: 3
            },
            stroke: {
                width: 2
            }
        };
    }
    
    /**
     * 合併配置
     */
    mergeConfig(customConfig) {
        return this.deepMerge(JSON.parse(JSON.stringify(this.defaultConfig)), customConfig);
    }
    
    /**
     * 深度合併物件
     */
    deepMerge(target, source) {
        for (const key in source) {
            if (source[key] && typeof source[key] === 'object' && !Array.isArray(source[key])) {
                if (!target[key]) target[key] = {};
                target[key] = this.deepMerge(target[key], source[key]);
            } else {
                target[key] = source[key];
            }
        }
        return target;
    }
    
    /**
     * 安全創建圖表
     */
    async createChart(containerId, options, chartId = null) {
        try {
            if (!this.isApexChartsReady) {
                await this.init();
            }
            
            const container = typeof containerId === 'string' ? 
                document.getElementById(containerId) : containerId;
                
            if (!container) {
                throw new Error(`圖表容器不存在: ${containerId}`);
            }
            
            // 合併配置
            const finalConfig = this.mergeConfig(options);
            
            // 清理容器
            container.innerHTML = '';
            
            // 創建圖表
            const chart = new ApexCharts(container, finalConfig);
            
            // 渲染圖表
            await chart.render();
            
            // 存儲圖表實例
            const id = chartId || containerId;
            this.charts.set(id, chart);
            
            console.log(`圖表創建成功: ${id}`);
            return chart;
            
        } catch (error) {
            console.error(`圖表創建失敗: ${containerId}`, error);
            throw error;
        }
    }
    
    /**
     * 更新圖表數據
     */
    updateChart(chartId, newData, options = {}) {
        const chart = this.charts.get(chartId);
        if (chart) {
            if (options.updateOptions) {
                chart.updateOptions(options.updateOptions);
            }
            if (newData) {
                chart.updateSeries(newData);
            }
        } else {
            console.warn(`圖表不存在: ${chartId}`);
        }
    }
    
    /**
     * 銷毀圖表
     */
    destroyChart(chartId) {
        const chart = this.charts.get(chartId);
        if (chart) {
            chart.destroy();
            this.charts.delete(chartId);
            console.log(`圖表已銷毀: ${chartId}`);
        }
    }
    
    /**
     * 銷毀所有圖表
     */
    destroyAllCharts() {
        this.charts.forEach((chart, id) => {
            chart.destroy();
        });
        this.charts.clear();
        console.log('所有圖表已銷毀');
    }
    
    /**
     * 取得圖表實例
     */
    getChart(chartId) {
        return this.charts.get(chartId);
    }
    
    /**
     * 檢查字型是否可用
     */
    checkFontAvailability() {
        const testFonts = [
            'Noto Sans TC',
            'Noto Sans CJK TC',
            'PingFang TC',
            'Microsoft JhengHei',
            'Heiti TC'
        ];
        
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        const testText = '測試字型 ABC 123';
        
        const results = {};
        
        testFonts.forEach(font => {
            context.font = `16px ${font}`;
            const metrics = context.measureText(testText);
            results[font] = metrics.width;
        });
        
        console.log('字型可用性檢查結果:', results);
        return results;
    }
    
    /**
     * 創建股價預測圖表
     */
    async createStockPredictionChart(containerId, data, options = {}) {
        const defaultOptions = {
            chart: {
                type: 'line',
                height: 400,
                zoom: {
                    enabled: true
                }
            },
            title: {
                text: options.title || '股價預測分析',
                align: 'center'
            },
            series: data.series || [],
            xaxis: {
                categories: data.categories || [],
                title: {
                    text: '時間'
                }
            },
            yaxis: {
                title: {
                    text: '股價 (元)'
                }
            },
            colors: ['#008FFB', '#00E396', '#FEB019', '#FF4560'],
            stroke: {
                curve: 'smooth'
            },
            markers: {
                size: 4
            }
        };
        
        const mergedOptions = this.deepMerge(defaultOptions, options);
        return await this.createChart(containerId, mergedOptions);
    }
    
    /**
     * 創建技術指標圖表
     */
    async createTechnicalIndicatorChart(containerId, data, options = {}) {
        const defaultOptions = {
            chart: {
                type: 'candlestick',
                height: 350
            },
            title: {
                text: options.title || '技術指標分析',
                align: 'center'
            },
            series: data.series || [],
            xaxis: {
                type: 'datetime'
            },
            yaxis: {
                tooltip: {
                    enabled: true
                }
            }
        };
        
        const mergedOptions = this.deepMerge(defaultOptions, options);
        return await this.createChart(containerId, mergedOptions);
    }
}

// 創建全域實例
window.apexChartsManager = new ApexChartsManager();

// 提供便利函數
window.createChart = (containerId, options, chartId) => {
    return window.apexChartsManager.createChart(containerId, options, chartId);
};

window.updateChart = (chartId, newData, options) => {
    return window.apexChartsManager.updateChart(chartId, newData, options);
};

window.destroyChart = (chartId) => {
    return window.apexChartsManager.destroyChart(chartId);
};

// DOM 載入完成後執行字型檢查
document.addEventListener('DOMContentLoaded', () => {
    console.log('DataScout ApexCharts 管理器已載入');
    
    // 延遲執行字型檢查，確保 Google Fonts 有時間載入
    setTimeout(() => {
        window.apexChartsManager.checkFontAvailability();
    }, 2000);
});

console.log('ApexCharts 管理器腳本已載入');
