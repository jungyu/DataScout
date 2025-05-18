/**
 * Chart.js 擴展初始化
 * 用於解決圖表渲染和時間軸問題
 */

(function() {
    'use strict';

    console.log('初始化 Chart.js 擴展...');
    
    // 向全局環境宣告初始化函數已存在
    window._initChartExtensionsLoaded = true;

    // 全局初始化函數
    window.initChartExtensions = function() {
        console.log('執行 initChartExtensions 函數');
        
        // 檢查並初始化日期適配器
        initDateAdapter();
        
        // 檢查並初始化金融圖表
        initFinancialCharts();
        
        // 檢查並修復時間軸問題
        fixTimeAxisIssues();
    };

    // 初始化日期適配器
    function initDateAdapter() {
        if (typeof Chart === 'undefined') {
            console.error('Chart.js 未載入，無法初始化日期適配器');
            return;
        }

        // 檢查適配器是否已正確載入
        if (Chart.adapters && Chart.adapters._date && 
            typeof Chart.adapters._date.parse === 'function' &&
            typeof Chart.adapters._date.format === 'function' &&
            typeof Chart.adapters._date.add === 'function' &&
            typeof Chart.adapters._date.diff === 'function' &&
            typeof Chart.adapters._date.startOf === 'function' &&
            typeof Chart.adapters._date.endOf === 'function') {
            
            console.log('Chart.js 日期適配器已正確載入');
            return;
        }

        console.log('日期適配器未正確配置，正在修復...');
        
        // 如果沒有適配器，先確保有 Chart.adapters
        if (!Chart.adapters) {
            Chart.adapters = {};
        }
        
        // 創建內建的日期適配器
        Chart.adapters._date = {
            // 解析日期
            parse: function(value) {
                if (value instanceof Date) {
                    return value;
                }
                if (typeof value === 'string') {
                    return new Date(value);
                }
                return new Date(value);
            },
            
            // 格式化日期，增強格式支持
            format: function(timestamp, format) {
                const date = new Date(timestamp);
                
                // 根據不同格式處理
                if (format === 'yyyy-MM-dd') {
                    return formatDate(date, 'yyyy-MM-dd');
                } else if (format === 'yyyy-MM-dd HH:mm:ss') {
                    return formatDate(date, 'yyyy-MM-dd HH:mm:ss');
                } else if (format === 'HH:mm:ss') {
                    return formatTime(date);
                } else if (format === 'HH:mm') {
                    return formatTime(date).substring(0, 5);
                } else if (format === 'yyyy-MM') {
                    return formatDate(date, 'yyyy-MM');
                } else if (format === 'yyyy') {
                    return date.getFullYear().toString();
                } else if (format === 'MM-dd') {
                    return formatDate(date, 'MM-dd');
                } else if (format === 'yyyy-[Q]Q') {
                    // 處理季度格式
                    const quarter = Math.floor((date.getMonth() / 3) + 1);
                    return `${date.getFullYear()}-Q${quarter}`;
                } else if (format === 'HH:00') {
                    // 小時格式
                    const hours = date.getHours().toString().padStart(2, '0');
                    return `${hours}:00`;
                } else if (format === 'HH:mm:ss.SSS') {
                    // 毫秒格式
                    const hours = date.getHours().toString().padStart(2, '0');
                    const minutes = date.getMinutes().toString().padStart(2, '0');
                    const seconds = date.getSeconds().toString().padStart(2, '0');
                    const milliseconds = date.getMilliseconds().toString().padStart(3, '0');
                    return `${hours}:${minutes}:${seconds}.${milliseconds}`;
                }
                
                // 預設格式
                return formatDate(date, 'yyyy-MM-dd HH:mm:ss');
            },
            
            // 增加時間
            add: function(time, amount, unit) {
                const date = new Date(time);
                switch(unit) {
                    case 'millisecond': date.setMilliseconds(date.getMilliseconds() + amount); break;
                    case 'second': date.setSeconds(date.getSeconds() + amount); break;
                    case 'minute': date.setMinutes(date.getMinutes() + amount); break;
                    case 'hour': date.setHours(date.getHours() + amount); break;
                    case 'day': date.setDate(date.getDate() + amount); break;
                    case 'week': date.setDate(date.getDate() + amount * 7); break;
                    case 'month': date.setMonth(date.getMonth() + amount); break;
                    case 'quarter': date.setMonth(date.getMonth() + amount * 3); break;
                    case 'year': date.setFullYear(date.getFullYear() + amount); break;
                }
                return date;
            },
            
            // 計算時間差
            diff: function(max, min, unit) {
                const diffMs = max - min;
                switch(unit) {
                    case 'millisecond': return diffMs;
                    case 'second': return Math.floor(diffMs / 1000);
                    case 'minute': return Math.floor(diffMs / (1000 * 60));
                    case 'hour': return Math.floor(diffMs / (1000 * 60 * 60));
                    case 'day': return Math.floor(diffMs / (1000 * 60 * 60 * 24));
                    case 'week': return Math.floor(diffMs / (1000 * 60 * 60 * 24 * 7));
                    case 'month': return Math.floor(diffMs / (1000 * 60 * 60 * 24 * 30));
                    case 'quarter': return Math.floor(diffMs / (1000 * 60 * 60 * 24 * 91.25));
                    case 'year': return Math.floor(diffMs / (1000 * 60 * 60 * 24 * 365.25));
                    default: return diffMs;
                }
            },
            
            // 時間單位開始
            startOf: function(time, unit) {
                const date = new Date(time);
                switch(unit) {
                    case 'second': date.setMilliseconds(0); break;
                    case 'minute': date.setSeconds(0); date.setMilliseconds(0); break;
                    case 'hour': date.setMinutes(0); date.setSeconds(0); date.setMilliseconds(0); break;
                    case 'day': date.setHours(0); date.setMinutes(0); date.setSeconds(0); date.setMilliseconds(0); break;
                    case 'week': {
                        const day = date.getDay();
                        const diff = date.getDate() - day + (day === 0 ? -6 : 1); // 調整為週一為每週開始
                        date.setDate(diff);
                        date.setHours(0); date.setMinutes(0); date.setSeconds(0); date.setMilliseconds(0);
                        break;
                    }
                    case 'month': date.setDate(1); date.setHours(0); date.setMinutes(0); date.setSeconds(0); date.setMilliseconds(0); break;
                    case 'quarter': {
                        const month = date.getMonth();
                        const quarterStartMonth = Math.floor(month / 3) * 3;
                        date.setMonth(quarterStartMonth, 1);
                        date.setHours(0); date.setMinutes(0); date.setSeconds(0); date.setMilliseconds(0);
                        break;
                    }
                    case 'year': date.setMonth(0, 1); date.setHours(0); date.setMinutes(0); date.setSeconds(0); date.setMilliseconds(0); break;
                }
                return date;
            },
            
            // 時間單位結束
            endOf: function(time, unit) {
                const date = new Date(time);
                switch(unit) {
                    case 'second': date.setMilliseconds(999); break;
                    case 'minute': date.setSeconds(59); date.setMilliseconds(999); break;
                    case 'hour': date.setMinutes(59); date.setSeconds(59); date.setMilliseconds(999); break;
                    case 'day': date.setHours(23); date.setMinutes(59); date.setSeconds(59); date.setMilliseconds(999); break;
                    case 'week': {
                        const day = date.getDay();
                        const diff = date.getDate() - day + (day === 0 ? 0 : 7); // 調整為週日為每週結束
                        date.setDate(diff);
                        date.setHours(23); date.setMinutes(59); date.setSeconds(59); date.setMilliseconds(999);
                        break;
                    }
                    case 'month': {
                        date.setMonth(date.getMonth() + 1, 0);
                        date.setHours(23); date.setMinutes(59); date.setSeconds(59); date.setMilliseconds(999);
                        break;
                    }
                    case 'quarter': {
                        const month = date.getMonth();
                        const quarterEndMonth = Math.floor(month / 3) * 3 + 2;
                        date.setMonth(quarterEndMonth + 1, 0);
                        date.setHours(23); date.setMinutes(59); date.setSeconds(59); date.setMilliseconds(999);
                        break;
                    }
                    case 'year': date.setMonth(11, 31); date.setHours(23); date.setMinutes(59); date.setSeconds(59); date.setMilliseconds(999); break;
                }
                return date;
            }
        };
        
        console.log('內建日期適配器已成功註冊');

        // 如果有 luxon，嘗試註冊 luxon 適配器
        if (typeof luxon !== 'undefined') {
            try {
                console.log('檢測到 luxon，註冊 luxon 適配器');
                registerLuxonAdapter();
            } catch (e) {
                console.warn('註冊 luxon 適配器失敗，使用內建適配器', e);
            }
        }
    }

    // 初始化金融圖表
    function initFinancialCharts() {
        if (typeof Chart === 'undefined') {
            console.error('Chart.js 未載入，無法初始化金融圖表');
            return;
        }
        
        // 檢查是否已有金融圖表控制器
        const hasFinancialControllers = 
            (Chart.controllers && Chart.controllers.candlestick) || 
            (Chart.registry && Chart.registry.controllers && Chart.registry.controllers.candlestick);
            
        if (hasFinancialControllers) {
            console.log('金融圖表控制器已載入');
            return;
        }
        
        console.log('載入金融圖表控制器...');
        
        // 動態載入金融圖表套件
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/chartjs-chart-financial@0.1.1/dist/chartjs-chart-financial.min.js';
        script.onload = function() {
            console.log('金融圖表擴展已成功載入');
            
            // 註冊金融圖表控制器
            if (window.CandlestickController) {
                Chart.register(window.CandlestickController);
                console.log('已註冊 CandlestickController');
            }
            
            if (window.OhlcController) {
                Chart.register(window.OhlcController);
                console.log('已註冊 OhlcController');
            }
        };
        script.onerror = function() {
            console.error('金融圖表擴展載入失敗');
        };
        document.head.appendChild(script);
    }

    // 修復時間軸問題
    function fixTimeAxisIssues() {
        if (typeof Chart === 'undefined') {
            console.error('Chart.js 未載入，無法修復時間軸問題');
            return;
        }
        
        console.log('修復時間軸問題...');
        
        // 修復時間軸顯示
        if (Chart.Scale && Chart.Scale.prototype) {
            const originalBuildTicks = Chart.Scale.prototype.buildTicks;
            if (originalBuildTicks) {
                Chart.Scale.prototype.buildTicks = function() {
                    // 調用原始方法
                    const ticks = originalBuildTicks.apply(this, arguments);
                    
                    // 如果是時間軸，確保格式化正確
                    if (this.type === 'time' || this.id === 'x' && this.options.type === 'time') {
                        console.log('修復時間軸格式...');
                        
                        // 確認時間適配器存在
                        if (!Chart.adapters || !Chart.adapters._date) {
                            console.warn('時間軸格式化失敗：適配器未載入');
                            return ticks;
                        }
                        
                        // 確保所有時間都被正確格式化
                        if (Array.isArray(ticks)) {
                            ticks.forEach(tick => {
                                if (tick.value && !tick.formattedValue) {
                                    try {
                                        const date = new Date(tick.value);
                                        tick.formattedValue = formatDate(date, 'yyyy-MM-dd');
                                    } catch (e) {
                                        console.warn('格式化時間軸標籤失敗', e);
                                    }
                                }
                            });
                        }
                    }
                    
                    return ticks;
                };
                
                console.log('已修復時間軸格式化');
            }
        }
    }

    // 註冊 Luxon 適配器
    function registerLuxonAdapter() {
        if (typeof luxon === 'undefined' || typeof Chart === 'undefined') {
            return;
        }
        
        console.log('註冊 Luxon 適配器');
        
        // 創建 luxon 適配器
        const luxonAdapter = {
            parse: function(value) {
                if (value instanceof Date) {
                    return value;
                }
                
                if (typeof value === 'string') {
                    try {
                        return luxon.DateTime.fromISO(value).toJSDate();
                    } catch (e) {
                        return new Date(value);
                    }
                }
                
                return new Date(value);
            },
            format: function(timestamp, format) {
                const dt = luxon.DateTime.fromJSDate(new Date(timestamp));
                if (format === 'yyyy-MM-dd') {
                    return dt.toFormat('yyyy-MM-dd');
                } else if (format === 'yyyy-MM-dd HH:mm:ss') {
                    return dt.toFormat('yyyy-MM-dd HH:mm:ss');
                } else if (format === 'HH:mm:ss') {
                    return dt.toFormat('HH:mm:ss');
                } else if (format === 'HH:mm') {
                    return dt.toFormat('HH:mm');
                } else {
                    return dt.toLocaleString(luxon.DateTime.DATETIME_SHORT);
                }
            },
            add: function(time, amount, unit) {
                const dt = luxon.DateTime.fromJSDate(new Date(time));
                const result = dt.plus({ [unit]: amount });
                return result.toJSDate();
            },
            diff: function(max, min, unit) {
                const dtMax = luxon.DateTime.fromJSDate(new Date(max));
                const dtMin = luxon.DateTime.fromJSDate(new Date(min));
                return dtMax.diff(dtMin, unit).values[unit];
            },
            startOf: function(time, unit) {
                const dt = luxon.DateTime.fromJSDate(new Date(time));
                const result = dt.startOf(unit);
                return result.toJSDate();
            },
            endOf: function(time, unit) {
                const dt = luxon.DateTime.fromJSDate(new Date(time));
                const result = dt.endOf(unit);
                return result.toJSDate();
            }
        };
        
        // 替換 Chart.adapters._date
        Chart.adapters._date = luxonAdapter;
        
        console.log('Luxon 適配器已註冊');
    }

    // 格式化日期的輔助函數
    function formatDate(date, format) {
        const year = date.getFullYear();
        const month = (date.getMonth() + 1).toString().padStart(2, '0');
        const day = date.getDate().toString().padStart(2, '0');
        const hours = date.getHours().toString().padStart(2, '0');
        const minutes = date.getMinutes().toString().padStart(2, '0');
        const seconds = date.getSeconds().toString().padStart(2, '0');
        
        if (format === 'yyyy-MM-dd') {
            return `${year}-${month}-${day}`;
        } else if (format === 'yyyy-MM-dd HH:mm:ss') {
            return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
        } else if (format === 'yyyy-MM') {
            return `${year}-${month}`;
        } else if (format === 'MM-dd') {
            return `${month}-${day}`;
        }
        
        return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
    }
    
    // 格式化時間的輔助函數
    function formatTime(date) {
        const hours = date.getHours().toString().padStart(2, '0');
        const minutes = date.getMinutes().toString().padStart(2, '0');
        const seconds = date.getSeconds().toString().padStart(2, '0');
        return `${hours}:${minutes}:${seconds}`;
    }

    // 在載入完成後初始化
    document.addEventListener('DOMContentLoaded', function() {
        // 等待 Chart.js 載入
        if (typeof Chart !== 'undefined') {
            window.initChartExtensions();
        } else {
            console.warn('等待 Chart.js 載入中...');
            waitForChartJs();
        }
    });

    // 等待 Chart.js 載入
    function waitForChartJs() {
        let attempts = 0;
        const MAX_ATTEMPTS = 20;
        const CHECK_INTERVAL = 200;
        
        const checkInterval = setInterval(function() {
            attempts++;
            if (typeof Chart !== 'undefined') {
                clearInterval(checkInterval);
                console.log('Chart.js 已載入，初始化擴展');
                window.initChartExtensions();
            } else if (attempts >= MAX_ATTEMPTS) {
                clearInterval(checkInterval);
                console.error('Chart.js 載入超時，無法初始化擴展');
            }
        }, CHECK_INTERVAL);
    }

    // 直接進行初始化嘗試（對於已載入的情況）
    if (typeof Chart !== 'undefined') {
        window.initChartExtensions();
    }

})();
