/**
 * Chart.js 全局配置
 * 
 * 設置圖表庫的全局選項，提高渲染穩定性和提供一致的視覺風格
 */

(function() {
    console.log('載入 Chart.js 全局配置');
    
    // 檢查 Chart.js 是否已載入
    if (typeof Chart === 'undefined') {
        console.error('Chart.js 尚未載入，全局配置將在 DOMContentLoaded 後重試');
        document.addEventListener('DOMContentLoaded', initGlobals);
    } else {
        initGlobals();
    }
    
    function initGlobals() {
        if (typeof Chart === 'undefined') {
            console.error('Chart.js 仍未載入，無法設置全局配置');
            return;
        }
        
        console.log('設置 Chart.js 全局配置');
        
        // 修復 Animation 系統以防止 class ID 錯誤
        if (Chart.register) {
            console.log('為 Chart.register 添加安全機制，處理 class does not have id 錯誤');
            
            const originalRegister = Chart.register;
            Chart.register = function() {
                try {
                    return originalRegister.apply(this, arguments);
                } catch (e) {
                    // 如果是 class ID 錯誤，嘗試添加缺失的 ID
                    if (e.message && e.message.includes('class does not have id')) {
                        for (let i = 0; i < arguments.length; i++) {
                            const arg = arguments[i];
                            if (arg && typeof arg === 'object' && !arg.id) {
                                arg.id = 'auto-' + Math.random().toString(36).substring(2, 11);
                            }
                        }
                        // 嘗試重新註冊
                        try {
                            return originalRegister.apply(this, arguments);
                        } catch (innerError) {
                            console.error('嘗試修復後註冊元件時仍出錯:', innerError);
                        }
                    }
                    throw e; // 重新拋出其他錯誤
                }
            };
        }
        
        // 檢查日期適配器
        console.log('檢查Chart.js日期適配器狀態');
        
        // 檢查日期適配器是否已正確載入（通過npm打包的版本）
        if (Chart.adapters && Chart.adapters._date) {
            console.log('檢測到Chart.js日期適配器，確認支援的方法:');
            const methods = ['parse', 'format', 'add', 'diff', 'startOf', 'endOf'];
            const missingMethods = methods.filter(m => typeof Chart.adapters._date[m] !== 'function');
            
            if (missingMethods.length === 0) {
                console.log('日期適配器所有必要方法都已存在，無需額外註冊');
            } else {
                console.warn('日期適配器缺少方法:', missingMethods.join(', '));
                registerBuiltInDateAdapter();
            }
        } else {
            console.warn('未檢測到 Chart.adapters._date，將註冊內建適配器');
            
            // 如果 Chart.adapters 不存在，先創建
            if (!Chart.adapters) {
                Chart.adapters = {};
            }
            
            registerBuiltInDateAdapter();
        }
        
        // 設置全局配置
        Chart.defaults.responsive = true;
        Chart.defaults.maintainAspectRatio = false;
        
        // 全局動畫配置
        Chart.defaults.animation = {
            duration: 1000,
            easing: 'easeOutQuad'
        };
        
        // 全局字體配置
        Chart.defaults.font = {
            family: "'Noto Sans TC', Arial, sans-serif",
            size: 12
        };
        
        // 修正工具提示顯示問題
        Chart.defaults.plugins.tooltip = {
            enabled: true,
            mode: 'index',
            intersect: false,
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            titleColor: '#ffffff',
            bodyColor: '#ffffff',
            borderColor: 'rgba(0, 0, 0, 0.1)',
            borderWidth: 1,
            padding: 10,
            cornerRadius: 4
        };
        
        // 全局標籤配置
        Chart.defaults.plugins.title = {
            display: false,
            padding: {
                top: 10,
                bottom: 10
            },
            font: {
                size: 16,
                weight: 'bold'
            }
        };
        
        // 修復 Animation 系統以防止 class ID 錯誤
        try {
            // 首先確保註冊函數是安全的
            const originalRegister = Chart.register;
            if (originalRegister) {
                Chart.register = function() {
                    try {
                        return originalRegister.apply(this, arguments);
                    } catch (e) {
                        console.warn('安全註冊：攔截到錯誤', e.message);
                        // 如果是 class ID 錯誤，我們會嘗試解決它
                        if (e.message && e.message.includes('class does not have id')) {
                            for (let i = 0; i < arguments.length; i++) {
                                const arg = arguments[i];
                                // 為缺少 ID 的組件添加一個 ID
                                if (arg && typeof arg === 'object' && !arg.id) {
                                    arg.id = 'auto-' + Math.random().toString(36).substring(2, 11);
                                    console.log('為組件添加自動 ID:', arg.id);
                                }
                            }
                            // 再次嘗試註冊，但忽略進一步的錯誤
                            try {
                                return originalRegister.apply(this, arguments);
                            } catch (innerError) {
                                console.error('第二次註冊嘗試也失敗:', innerError);
                            }
                        } else {
                            // 其他類型的錯誤，重新拋出
                            throw e;
                        }
                    }
                };
                console.log('已增強 Chart.register 以處理 class ID 錯誤');
            }
            
            // 現在嘗試安全地註冊動畫
            if (Chart.Animations) {
                try {
                    // 為動畫組件添加 ID 如果缺少
                    if (!Chart.Animations.id) {
                        Chart.Animations.id = 'animations';
                    }
                    Chart.register(Chart.Animations);
                    console.log('已安全註冊 Chart.Animations');
                } catch (e) {
                    console.warn('註冊動畫時出錯，但已被安全處理:', e);
                }
            }
        } catch (e) {
            console.error('修復動畫系統時出錯:', e);
        }
        
        console.log('Chart.js 全局配置設置完成');
    }
    
    // 內建日期適配器實現
    function registerBuiltInDateAdapter() {
        console.log('註冊內建日期適配器');
        
        // 創建日期適配器
        Chart.adapters._date = {
            // 將各種格式解析為日期
            parse: function(value) {
                if (value instanceof Date) {
                    return value;
                }
                if (typeof value === 'string') {
                    return new Date(value);
                }
                return new Date(value);
            },
            
            // 格式化日期
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
        
        console.log('內建日期適配器已註冊完成');
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
})();
