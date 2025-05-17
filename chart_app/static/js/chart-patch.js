/**
 * Chart.js 修補腳本
 * 緊急修復圖表渲染問題
 */

(function() {
    console.log('載入 Chart.js 緊急修補腳本');
    
    document.addEventListener('DOMContentLoaded', function() {
        console.log('應用圖表修補...');
        
        // 確保圖表畫布存在
        const chartCanvas = document.getElementById('chartCanvas');
        if (!chartCanvas) {
            console.error('找不到圖表畫布元素');
            return;
        }
        
        // 等待一段時間確保其他腳本已載入
        setTimeout(function() {
            // 檢查是否有顯示圖表的訊息
            const chartMessage = document.getElementById('chartMessage');
            if (chartMessage && !chartMessage.classList.contains('hidden')) {
                console.log('發現圖表訊息顯示，嘗試緊急修復圖表渲染');
                     // 創建簡單的示例圖表
                    try {
                        // 修復 Window.getComputedStyle 問題
                        if (window.getComputedStyle && !window._originalGetComputedStyle) {
                            window._originalGetComputedStyle = window.getComputedStyle;
                            window.getComputedStyle = function(element, pseudoElt) {
                                if (!element || !element.nodeType) {
                                    console.warn('getComputedStyle 被調用時提供了無效的元素');
                                    return { getPropertyValue: () => '' };
                                }
                                return window._originalGetComputedStyle(element, pseudoElt);
                            };
                        }
                        
                        // 顯示調試信息
                        const debugInfo = document.getElementById('debug-info');
                        if (debugInfo) {
                            debugInfo.innerText = '圖表修補腳本: 嘗試緊急渲染圖表...';
                        }
                    
                    if (typeof Chart === 'undefined') {
                        console.error('Chart.js 仍未載入，嘗試從 CDN 加載');
                        
                        const script = document.createElement('script');
                        script.src = 'https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js';
                        document.head.appendChild(script);
                        
                        script.onload = function() {
                            renderEmergencyChart();
                        };
                        
                        return;
                    }
                    
                    renderEmergencyChart();
                    
                } catch (error) {
                    console.error('緊急圖表渲染失敗:', error);
                    
                    // 更新調試信息
                    const debugInfo = document.getElementById('debug-info');
                    if (debugInfo) {
                        debugInfo.innerText = '圖表修補失敗: ' + error.message;
                    }
                }
            } else {
                console.log('圖表可能已正確渲染，無需修補');
            }
        }, 2000); // 等待 2 秒以確保其他腳本已加載
    });
    
    // 渲染緊急圖表的函數
    function renderEmergencyChart() {
        const chartCanvas = document.getElementById('chartCanvas');
        if (!chartCanvas) return;
        
        // 加強版圖表實例清理
        console.log('開始進行圖表實例深度清理');
        
        // 方法 1: 使用 Chart.getChart API
        try {
            const existingChart = Chart.getChart(chartCanvas);
            if (existingChart) {
                console.log('使用 Chart.getChart 找到圖表實例，ID: ' + existingChart.id);
                try {
                    // 先停止任何動畫
                    if (existingChart.stop) {
                        existingChart.stop();
                    }
                    
                    // 分離事件監聽器
                    if (existingChart.canvas) {
                        const events = ['click', 'mousemove', 'mouseout', 'mouseenter', 'touchstart', 'touchmove', 'touchend'];
                        events.forEach(eventType => {
                            existingChart.canvas.removeEventListener(eventType, null);
                        });
                    }
                    
                    // 銷毀圖表
                    existingChart.destroy();
                    
                    // 清理全局引用
                    if (Chart.instances && existingChart.id) {
                        delete Chart.instances[existingChart.id];
                    }
                    
                    console.log('圖表實例已通過 Chart.getChart 成功清理');
                    } catch (e) {
                    console.error('清理舊圖表實例時出錯:', e);
                }
            }
        } catch (chartError) {
            console.warn('使用 Chart.getChart 尋找實例失敗:', chartError);
        }
        
        // 方法 2: 檢查並清理所有關聯同一畫布的實例
        try {
            if (Chart.instances) {
                const canvasId = chartCanvas.id;
                console.log(`檢查是否有其他圖表實例使用畫布 #${canvasId}`);
                
                Object.values(Chart.instances).forEach(instance => {
                    if (instance && instance.canvas && instance.canvas.id === canvasId) {
                        console.log(`找到使用相同畫布的實例: ${instance.id}`);
                        try {
                            instance.destroy();
                            delete Chart.instances[instance.id];
                            console.log(`成功清理圖表實例: ${instance.id}`);
                        } catch (e) {
                            console.warn(`清理圖表實例 ${instance.id} 時出錯:`, e);
                        }
                    }
                });
            }
        } catch (e) {
            console.error('清理畫布關聯的圖表實例時出錯:', e);
        }
        
        // 方法 3: 最後的備用方案 - 重置畫布
        console.log('執行最終畫布重置');
        try {
            // 備份畫布屬性
            const canvasId = chartCanvas.id;
            const width = chartCanvas.width;
            const height = chartCanvas.height;
            const className = chartCanvas.className;
            const style = chartCanvas.getAttribute('style');
            
            // 創建替代畫布
            const newCanvas = document.createElement('canvas');
            newCanvas.id = canvasId;
            newCanvas.width = width;
            newCanvas.height = height;
            newCanvas.className = className;
            if (style) newCanvas.setAttribute('style', style);
            
            // 替換畫布
            if (chartCanvas.parentNode) {
                chartCanvas.parentNode.replaceChild(newCanvas, chartCanvas);
                console.log('已使用新畫布替換舊畫布');
                chartCanvas = newCanvas;
            } else {
                // 如果無法替換，至少清理畫布
                const ctx = chartCanvas.getContext('2d');
                if (ctx) {
                    ctx.clearRect(0, 0, chartCanvas.width, chartCanvas.height);
                    console.log('已清理畫布內容');
                }
            }
        } catch (e) {
            console.error('替換/清理畫布時出錯:', e);
        }
        
        // 示例數據
        const data = {
            labels: ['第一季', '第二季', '第三季', '第四季'],
            datasets: [{
                label: '2025年度收入',
                data: [18500, 23400, 19250, 27800],
                backgroundColor: 'rgba(54, 162, 235, 0.5)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 2
            }]
        };
        
        // 創建圖表
        const chart = new Chart(chartCanvas, {
            type: 'bar',
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: '季度收入圖表 (示例數據)',
                        font: { size: 16 }
                    },
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    tooltip: {
                        enabled: true
                    }
                }
            }
        });
        
        console.log('緊急圖表已渲染');
        
        // 隱藏圖表訊息
        const chartMessage = document.getElementById('chartMessage');
        if (chartMessage) {
            chartMessage.classList.add('hidden');
        }
        
        // 更新調試信息
        const debugInfo = document.getElementById('debug-info');
        if (debugInfo) {
            debugInfo.innerText = '圖表修補成功: 已顯示示例圖表';
        }
    }
})();
