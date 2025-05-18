/**
 * Chart.js 除錯工具
 * 用於診斷和修復 Chart.js 圖表問題，特別是時間軸相關問題
 */

(function() {
    'use strict';
    
    console.log('載入 Chart.js 除錯工具');
    
    // 創建 ChartDebugger 全局對象
    window.ChartDebugger = {
        // 顯示基本的圖表庫信息
        showInfo: function() {
            if (typeof Chart === 'undefined') {
                console.error('Chart.js 未載入');
                return {
                    loaded: false,
                    message: 'Chart.js 未載入'
                };
            }
            
            // 收集基本信息
            const info = {
                loaded: true,
                version: Chart.version,
                adapters: !!Chart.adapters,
                dateAdapter: Chart.adapters && !!Chart.adapters._date,
                controllers: Chart.controllers ? Object.keys(Chart.controllers) : (
                    Chart.registry && Chart.registry.controllers ? Object.keys(Chart.registry.controllers) : []
                ),
                initialized: !!window._initChartExtensionsLoaded
            };
            
            console.log('Chart.js 資訊:', info);
            return info;
        },
        
        // 檢查圖表是否正常運作
        diagnose: function() {
            const issues = [];
            
            // 檢查 Chart.js 是否已載入
            if (typeof Chart === 'undefined') {
                issues.push({
                    severity: 'error',
                    component: 'core',
                    message: 'Chart.js 未載入',
                    fix: 'script 標籤中加載 Chart.js'
                });
                return {
                    status: 'failure',
                    issues
                };
            }
            
            // 檢查圖表版本
            const version = Chart.version || 'unknown';
            if (version.startsWith('2.') && parseInt(version.split('.')[1], 10) < 9) {
                issues.push({
                    severity: 'warning',
                    component: 'version',
                    message: `Chart.js 版本 ${version} 較舊`,
                    fix: '升級到最新的 Chart.js'
                });
            }
            
            // 檢查 adapters 系統
            if (!Chart.adapters) {
                issues.push({
                    severity: 'error',
                    component: 'adapters',
                    message: 'Chart.adapters 不存在',
                    fix: '載入 chart-globals.js 或執行 window.initChartExtensions()'
                });
            } else if (!Chart.adapters._date) {
                issues.push({
                    severity: 'error',
                    component: 'dateAdapter',
                    message: 'Chart.adapters._date 不存在',
                    fix: '載入 chart-extensions-init.js 或執行 window.initChartExtensions()'
                });
            } else {
                // 檢查日期適配器方法
                const requiredMethods = ['parse', 'format', 'add', 'diff', 'startOf', 'endOf'];
                const missingMethods = requiredMethods.filter(
                    method => !Chart.adapters._date[method] || typeof Chart.adapters._date[method] !== 'function'
                );
                
                if (missingMethods.length > 0) {
                    issues.push({
                        severity: 'error',
                        component: 'dateAdapter',
                        message: `Chart.adapters._date 缺少方法: ${missingMethods.join(', ')}`,
                        fix: '載入 chart-extensions-init.js 或執行 window.initChartExtensions()'
                    });
                }
            }
        
        // 如果 Chart.js 已載入，嘗試創建一個簡單的圖表
        if (isChartJsLoaded) {
            console.log('Chart.js 版本:', Chart.version);
            console.log('已註冊的控制器:', Object.keys(Chart.controllers || {}));
            
            if (debugInfo) {
                debugInfo.innerText += ` | 版本: ${Chart.version}`;
            }
            
            // 嘗試獲取並渲染圖表
            setTimeout(function() {
                try {
                    // 獲取畫布元素
                    const chartCanvas = document.getElementById('chartCanvas');
                    if (!chartCanvas) {
                        console.error('找不到圖表畫布元素 #chartCanvas');
                        if (debugInfo) {
                            debugInfo.innerText += ' | 錯誤: 找不到畫布元素';
                        }
                        return;
                    }
                    
                    // 測試渲染一個簡單的圖表
                    console.log('嘗試渲染除錯圖表...');
                    
                    // 清理任何可能存在的圖表實例
                    const existingChartInstance = Chart.getChart(chartCanvas);
                    if (existingChartInstance) {
                        existingChartInstance.destroy();
                        console.log('銷毀了現有圖表實例');
                    }
                    
                    // 創建簡單的測試數據
                    const testData = {
                        labels: ['紅色', '藍色', '黃色', '綠色', '紫色'],
                        datasets: [{
                            label: '測試數據',
                            data: [12, 19, 3, 5, 2],
                            backgroundColor: [
                                'rgba(255, 99, 132, 0.6)',
                                'rgba(54, 162, 235, 0.6)',
                                'rgba(255, 206, 86, 0.6)',
                                'rgba(75, 192, 192, 0.6)',
                                'rgba(153, 102, 255, 0.6)'
                            ]
                        }]
                    };
                    
                    // 嘗試創建一個簡單的圖表
                    const debugChart = new Chart(chartCanvas, {
                        type: 'bar',  // 使用最基本的長條圖
                        data: testData,
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                title: {
                                    display: true,
                                    text: '除錯測試圖表',
                                    font: { size: 16 }
                                }
                            }
                        }
                    });
                    
                    console.log('除錯圖表已創建:', debugChart);
                    
                    if (debugInfo) {
                        debugInfo.innerText += ' | 測試圖表渲染: 成功';
                    }
                    
                    // 隱藏圖表訊息
                    const chartMessage = document.getElementById('chartMessage');
                    if (chartMessage) {
                        chartMessage.classList.add('hidden');
                    }
                    
                } catch (error) {
                    console.error('渲染除錯圖表時出錯:', error);
                    
                    if (debugInfo) {
                        debugInfo.innerText += ` | 錯誤: ${error.message}`;
                    }
                }
            }, 1000);
        } else {
            // Chart.js 未載入，嘗試診斷原因
            console.error('Chart.js 未載入，檢查相關腳本的引用');
            
            if (debugInfo) {
                debugInfo.innerText += ' | 錯誤: Chart.js 未載入，請檢查網路連接和腳本引用';
            }
            
            // 嘗試手動載入 Chart.js
            const script = document.createElement('script');
            script.src = 'https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js';
            script.onload = function() {
                console.log('已手動載入 Chart.js');
                
                if (debugInfo) {
                    debugInfo.innerText += ' | 手動載入 Chart.js 成功';
                }
                
                // 重新嘗試初始化
                setTimeout(function() {
                    try {
                        const chartCanvas = document.getElementById('chartCanvas');
                        if (chartCanvas) {
                            // 簡單測試圖表
                            const ctx = chartCanvas.getContext('2d');
                            new Chart(ctx, {
                                type: 'bar',
                                data: {
                                    labels: ['測試1', '測試2'],
                                    datasets: [{
                                        label: '測試數據',
                                        data: [10, 20],
                                        backgroundColor: 'rgba(75, 192, 192, 0.6)'
                                    }]
                                }
                            });
                            
                            console.log('已創建備用測試圖表');
                            
                            if (debugInfo) {
                                debugInfo.innerText += ' | 備用圖表渲染: 成功';
                            }
                        }
                    } catch (err) {
                        console.error('備用圖表創建失敗:', err);
                        
                        if (debugInfo) {
                            debugInfo.innerText += ' | 備用圖表錯誤: ' + err.message;
                        }
                    }
                }, 500);
            };
            script.onerror = function() {
                console.error('手動載入 Chart.js 失敗');
                
                if (debugInfo) {
                    debugInfo.innerText += ' | 手動載入 Chart.js 失敗';
                }
            };
            document.head.appendChild(script);
        }
    });
})();
