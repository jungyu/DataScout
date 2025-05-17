/**
 * Chart.js 圖例與工具提示修復腳本
 * 專門解決 "Bo[n.position] is undefined" 等位置相關錯誤
 */

(function() {
    console.log('載入 Chart.js 圖例與工具提示修復腳本');
    
    // 等待 Chart.js 加載
    function waitForChart(callback) {
        if (typeof Chart !== 'undefined') {
            callback();
        } else {
            setTimeout(() => waitForChart(callback), 100);
        }
    }
    
    waitForChart(function() {
        try {
            // 修復圖例位置問題
            fixLegendPosition();
            
            // 安全地修復工具提示
            fixTooltipSystem();
            
            console.log('圖例與工具提示修復完成');
        } catch (e) {
            console.error('應用圖例修復時出錯:', e);
        }
    });
    
    // 修復圖例位置問題
    function fixLegendPosition() {
        if (!Chart.defaults || !Chart.defaults.plugins) return;
        
        console.log('修復圖例位置問題...');
        
        // 1. 確保默認圖例位置是有效的
        const validPositions = ['top', 'left', 'bottom', 'right', 'chartArea'];
        if (!Chart.defaults.plugins.legend) {
            Chart.defaults.plugins.legend = {};
        }
        
        if (!validPositions.includes(Chart.defaults.plugins.legend.position)) {
            console.log('將不支援的圖例位置修改為 "top"');
            Chart.defaults.plugins.legend.position = 'top';
        }
        
        // 2. 攔截 update 方法以檢查和修正無效的位置設置
        // 這將解決 "Bo[n.position] is undefined" 錯誤
        try {
            // 尋找圖例插件
            let legendPlugin = null;
            if (Chart.registry && Chart.registry.plugins) {
                if (Chart.registry.plugins.items && Array.isArray(Chart.registry.plugins.items)) {
                    // 使用數組方法
                    const plugins = Chart.registry.plugins.items;
                    legendPlugin = plugins.find(p => p.id === 'legend');
                } else if (Chart.registry.plugins._registry && Chart.registry.plugins._registry.legend) {
                    // 直接訪問註冊表
                    legendPlugin = Chart.registry.plugins._registry.legend;
                } else {
                    // 嘗試從 Chart 頂層屬性獲取
                    legendPlugin = Chart.Legend || null;
                }
            }
            
            if (legendPlugin && legendPlugin._element && legendPlugin._element.prototype) {
                // 保存原始的位置變更處理函數
                const originalPositionChanged = legendPlugin._element.prototype._positionChanged;
                
                if (originalPositionChanged) {
                    legendPlugin._element.prototype._positionChanged = function(position, prevPosition) {
                        try {
                            // 檢查並修正位置是否有效
                            if (!validPositions.includes(position)) {
                                console.warn(`圖例位置 "${position}" 無效，回退到 "top"`);
                                position = 'top';
                            }
                            
                            // 調用原始方法
                            return originalPositionChanged.call(this, position, prevPosition);
                        } catch (e) {
                            console.warn('圖例位置變更出錯:', e);
                            // 避免讓錯誤影響渲染
                            return false;
                        }
                    };
                    console.log('已修復圖例位置變更處理');
                }
            } else {
                console.warn('無法找到圖例插件，跳過圖例位置修復');
            }
        } catch (e) {
            console.error('修復圖例位置時出錯:', e);
        }
    }
    
    // 修復工具提示系統
    function fixTooltipSystem() {
        if (!Chart.Tooltip || !Chart.Tooltip.positioners) {
            return;
        }
        
        console.log('修復工具提示系統...');
        
        // 確保工具提示總是有安全的位置計算
        if (!Chart.Tooltip.positioners.fallback) {
            Chart.Tooltip.positioners.fallback = function(items, eventPosition) {
                return {
                    x: eventPosition ? eventPosition.x : 0,
                    y: eventPosition ? eventPosition.y : 0
                };
            };
            console.log('添加了 fallback 工具提示定位器');
        }
        
        // 攔截所有現有的定位器
        const positioners = Chart.Tooltip.positioners;
        Object.keys(positioners).forEach(name => {
            const originalPositioner = positioners[name];
            positioners[name] = function(items, eventPosition) {
                try {
                    const result = originalPositioner.call(this, items, eventPosition);
                    
                    // 確保返回的結果是有效的
                    if (!result || typeof result.x !== 'number' || typeof result.y !== 'number') {
                        throw new Error('定位器返回了無效的結果');
                    }
                    
                    return result;
                } catch (e) {
                    console.warn(`工具提示定位器 "${name}" 出錯:`, e);
                    
                    // 使用事件位置作為回退
                    if (eventPosition) {
                        return {
                            x: eventPosition.x,
                            y: eventPosition.y
                        };
                    }
                    
                    // 最後的回退 - 使用畫布中心
                    const canvas = document.getElementById('chartCanvas');
                    if (canvas) {
                        return {
                            x: canvas.width / 2,
                            y: canvas.height / 2
                        };
                    }
                    
                    return { x: 0, y: 0 };
                }
            };
        });
        
        console.log('已增強所有工具提示定位器');
        
        // 修復工具提示事件處理
        try {
            let tooltipPlugin = null;
            
            if (Chart.registry && Chart.registry.plugins) {
                // 嘗試多種方法獲取工具提示插件
                if (Chart.registry.plugins.items && Array.isArray(Chart.registry.plugins.items)) {
                    tooltipPlugin = Chart.registry.plugins.items.find(p => p.id === 'tooltip');
                } else if (Chart.registry.plugins._registry && Chart.registry.plugins._registry.tooltip) {
                    tooltipPlugin = Chart.registry.plugins._registry.tooltip;
                } else if (Chart.Tooltip) {
                    tooltipPlugin = Chart.Tooltip;
                }
            }
            
            if (tooltipPlugin && tooltipPlugin.afterEvent) {
                const originalAfterEvent = tooltipPlugin.afterEvent;
                tooltipPlugin.afterEvent = function(chart, args, options) {
                    try {
                        return originalAfterEvent.call(this, chart, args, options);
                    } catch (e) {
                        console.warn('工具提示事件處理出錯:', e);
                        // 不傳播錯誤，確保 UI 不會崩潰
                    }
                };
                console.log('已修復工具提示事件處理');
            }
        } catch (e) {
            console.error('修復工具提示事件處理時出錯:', e);
        }
    }
})();
