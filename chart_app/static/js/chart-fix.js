/**
 * Chart.js 特殊圖表類型修復腳本
 * 用於確保金融圖表和極座標圖等特殊圖表能正常渲染
 */

(function() {
    console.log('載入 Chart.js 修復腳本');
    
    // 等待 Chart.js 載入完成
    function waitForChartJs(callback, maxAttempts = 20, interval = 200) {
        let attempts = 0;
        
        const checkChartJs = function() {
            attempts++;
            if (typeof Chart !== 'undefined') {
                console.log('找到 Chart.js，版本:', Chart.version);
                callback();
                return;
            } else if (attempts >= maxAttempts) {
                console.error('等待 Chart.js 載入超時');
                return;
            }
            
            setTimeout(checkChartJs, interval);
        };
        
        checkChartJs();
    }
    
    // 註冊特殊圖表類型
    function registerSpecialChartTypes() {
        if (typeof Chart === 'undefined') {
            console.error('Chart.js 未載入，無法註冊特殊圖表類型');
            return;
        }
        
        try {
            console.log('嘗試註冊特殊圖表類型');
            
            // 註冊極座標圖
            if (!Chart.controllers.polarArea) {
                if (Chart.PolarAreaController) {
                    Chart.register(Chart.PolarAreaController);
                    console.log('成功註冊 PolarAreaController');
                } else {
                    console.warn('找不到 PolarAreaController');
                }
            }
            
            // 檢查金融圖表擴展是否已載入
            const hasFinancialExtension = typeof window.CandlestickController !== 'undefined' || 
                (window.Chart && window.Chart.controllers && window.Chart.controllers.financial);
            
            if (!hasFinancialExtension) {
                console.warn('未找到金融圖表擴展，嘗試動態載入');
                
                // 動態載入金融圖表擴展
                const script = document.createElement('script');
                script.src = 'https://cdn.jsdelivr.net/npm/chartjs-chart-financial@0.1.1/dist/chartjs-chart-financial.min.js';
                script.onload = function() {
                    console.log('金融圖表擴展已動態載入');
                    registerFinancialControllers();
                };
                script.onerror = function() {
                    console.error('金融圖表擴展載入失敗');
                };
                document.head.appendChild(script);
            } else {
                registerFinancialControllers();
            }
            
        } catch (error) {
            console.error('註冊特殊圖表類型時出錯:', error);
        }
    }
    
    // 註冊金融圖表控制器
    function registerFinancialControllers() {
        try {
            // 註冊蠟燭圖控制器
            if (!Chart.controllers.candlestick) {
                if (window.CandlestickController) {
                    Chart.register(window.CandlestickController);
                    console.log('已註冊 CandlestickController');
                } else if (window.Chart && window.Chart.controllers && window.Chart.controllers.financial && 
                          window.Chart.controllers.financial.CandlestickController) {
                    Chart.register(window.Chart.controllers.financial.CandlestickController);
                    console.log('已從 financial 套件註冊 CandlestickController');
                } else {
                    console.warn('找不到 CandlestickController');
                }
            }
            
            // 註冊 OHLC 控制器
            if (!Chart.controllers.ohlc) {
                if (window.OhlcController) {
                    Chart.register(window.OhlcController);
                    console.log('已註冊 OhlcController');
                } else if (window.Chart && window.Chart.controllers && window.Chart.controllers.financial && 
                          window.Chart.controllers.financial.OhlcController) {
                    Chart.register(window.Chart.controllers.financial.OhlcController);
                    console.log('已從 financial 套件註冊 OhlcController');
                } else {
                    console.warn('找不到 OhlcController');
                }
            }
            
            // 檢查控制器是否已註冊
            console.log('已註冊的控制器:', Object.keys(Chart.controllers || {}));
            
            // 添加全局混合設定，增強金融圖表處理
            Chart.defaults.set('elements.candlestick', {
                color: {
                    up: 'rgba(75, 192, 75, 1)',
                    down: 'rgba(255, 99, 132, 1)',
                    unchanged: 'rgba(160, 160, 160, 1)'
                }
            });
            
            Chart.defaults.set('elements.ohlc', {
                color: {
                    up: 'rgba(75, 192, 75, 1)',
                    down: 'rgba(255, 99, 132, 1)',
                    unchanged: 'rgba(160, 160, 160, 1)'
                }
            });
            
        } catch (error) {
            console.error('註冊金融圖表控制器時出錯:', error);
        }
    }
    
    // 在文檔載入完成後執行
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            waitForChartJs(registerSpecialChartTypes);
        });
    } else {
        waitForChartJs(registerSpecialChartTypes);
    }
    
    // 暴露全局方法以便其他腳本調用
    window.chartFix = {
        registerSpecialChartTypes: registerSpecialChartTypes,
        registerFinancialControllers: registerFinancialControllers
    };
})();
