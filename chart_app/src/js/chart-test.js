/**
 * 圖表模組測試腳本
 * 此腳本用於測試各種圖表類型是否正確渲染
 */

import { createChart } from './chart-renderer.js';

// 範例資料
const testData = {
    // 線圖範例資料
    line: {
        title: '測試折線圖',
        datasets: [{
            label: '銷售額',
            data: [
                { x: new Date('2025-01-01'), y: 12800 },
                { x: new Date('2025-02-01'), y: 19500 },
                { x: new Date('2025-03-01'), y: 15200 },
                { x: new Date('2025-04-01'), y: 18100 },
                { x: new Date('2025-05-01'), y: 23000 }
            ],
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            borderColor: 'rgb(75, 192, 192)',
            tension: 0.1
        }]
    },
    
    // 長條圖範例資料
    bar: {
        title: '測試長條圖',
        labels: ['一月', '二月', '三月', '四月', '五月'],
        datasets: [{
            label: '銷售額',
            data: [12800, 19500, 15200, 18100, 23000],
            backgroundColor: 'rgba(75, 192, 192, 0.6)'
        }]
    },
    
    // 圓餅圖範例資料
    pie: {
        title: '測試圓餅圖',
        labels: ['紅色', '藍色', '黃色', '綠色', '紫色'],
        datasets: [{
            data: [30, 20, 25, 15, 10],
            backgroundColor: [
                'rgba(255, 99, 132, 0.6)',
                'rgba(54, 162, 235, 0.6)',
                'rgba(255, 206, 86, 0.6)',
                'rgba(75, 192, 192, 0.6)',
                'rgba(153, 102, 255, 0.6)'
            ]
        }]
    },
    
    // 環狀圖範例資料
    doughnut: {
        title: '測試環狀圖',
        labels: ['紅色', '藍色', '黃色', '綠色', '紫色'],
        datasets: [{
            data: [30, 20, 25, 15, 10],
            backgroundColor: [
                'rgba(255, 99, 132, 0.6)',
                'rgba(54, 162, 235, 0.6)',
                'rgba(255, 206, 86, 0.6)',
                'rgba(75, 192, 192, 0.6)',
                'rgba(153, 102, 255, 0.6)'
            ]
        }]
    },
    
    // 極座標圖範例資料
    polarArea: {
        title: '測試極座標圖',
        labels: ['紅色', '藍色', '黃色', '綠色', '紫色'],
        datasets: [{
            data: [30, 20, 25, 15, 10],
            backgroundColor: [
                'rgba(255, 99, 132, 0.6)',
                'rgba(54, 162, 235, 0.6)',
                'rgba(255, 206, 86, 0.6)',
                'rgba(75, 192, 192, 0.6)',
                'rgba(153, 102, 255, 0.6)'
            ]
        }]
    },
    
    // 蠟燭圖範例資料
    candlestick: {
        title: '測試蠟燭圖',
        datasets: [{
            label: '股價',
            data: [
                { t: new Date('2025-01-01'), o: 150, h: 160, l: 145, c: 155 },
                { t: new Date('2025-01-02'), o: 155, h: 165, l: 150, c: 160 },
                { t: new Date('2025-01-03'), o: 160, h: 168, l: 153, c: 157 },
                { t: new Date('2025-01-04'), o: 157, h: 165, l: 150, c: 163 },
                { t: new Date('2025-01-05'), o: 163, h: 170, l: 158, c: 168 }
            ]
        }]
    },
    
    // OHLC圖範例資料
    ohlc: {
        title: '測試OHLC圖',
        datasets: [{
            label: '股價',
            data: [
                { t: new Date('2025-01-01'), o: 150, h: 160, l: 145, c: 155 },
                { t: new Date('2025-01-02'), o: 155, h: 165, l: 150, c: 160 },
                { t: new Date('2025-01-03'), o: 160, h: 168, l: 153, c: 157 },
                { t: new Date('2025-01-04'), o: 157, h: 165, l: 150, c: 163 },
                { t: new Date('2025-01-05'), o: 163, h: 170, l: 158, c: 168 }
            ]
        }]
    },
    
    // 雷達圖範例資料
    radar: {
        title: '測試雷達圖',
        labels: ['速度', '耐力', '力量', '敏捷', '技巧'],
        datasets: [{
            label: '運動員A',
            data: [65, 59, 90, 81, 56],
            fill: true,
            backgroundColor: 'rgba(54, 162, 235, 0.2)',
            borderColor: 'rgb(54, 162, 235)',
            pointBackgroundColor: 'rgb(54, 162, 235)',
            pointBorderColor: '#fff',
            pointHoverBackgroundColor: '#fff',
            pointHoverBorderColor: 'rgb(54, 162, 235)'
        }]
    },
    
    // 散點圖範例資料
    scatter: {
        title: '測試散點圖',
        datasets: [{
            label: '散點數據',
            data: [
                { x: 10, y: 20 },
                { x: 15, y: 30 },
                { x: 25, y: 10 },
                { x: 35, y: 40 },
                { x: 40, y: 20 }
            ],
            backgroundColor: 'rgba(255, 99, 132, 0.6)'
        }]
    },
    
    // 氣泡圖範例資料
    bubble: {
        title: '測試氣泡圖',
        datasets: [{
            label: '氣泡數據',
            data: [
                { x: 10, y: 20, r: 5 },
                { x: 15, y: 30, r: 10 },
                { x: 25, y: 10, r: 15 },
                { x: 35, y: 40, r: 8 },
                { x: 40, y: 20, r: 12 }
            ],
            backgroundColor: 'rgba(75, 192, 192, 0.6)'
        }]
    }
};

/**
 * 測試各種圖表類型的渲染情況
 * @param {HTMLCanvasElement} canvas - Canvas元素
 * @param {Object} appState - 應用程式狀態
 */
export function testAllChartTypes(canvas, appState) {
    // 測試各種圖表類型
    const chartTypes = ['line', 'bar', 'pie', 'doughnut', 'polarArea', 'radar', 'scatter', 'bubble', 'candlestick', 'ohlc'];
    let currentIndex = 0;
    
    // 顯示第一個圖表
    renderTestChart(chartTypes[currentIndex], canvas, appState);
    
    // 添加測試UI
    const testUI = document.createElement('div');
    testUI.style.position = 'fixed';
    testUI.style.top = '10px';
    testUI.style.right = '10px';
    testUI.style.backgroundColor = 'rgba(255,255,255,0.8)';
    testUI.style.padding = '10px';
    testUI.style.borderRadius = '5px';
    testUI.style.boxShadow = '0 2px 5px rgba(0,0,0,0.2)';
    testUI.style.zIndex = '1000';
    
    const label = document.createElement('div');
    label.textContent = `目前圖表：${chartTypes[currentIndex]}`;
    label.style.marginBottom = '10px';
    label.style.fontWeight = 'bold';
    
    const prevBtn = document.createElement('button');
    prevBtn.textContent = '上一個圖表';
    prevBtn.style.marginRight = '5px';
    prevBtn.style.padding = '5px 10px';
    prevBtn.addEventListener('click', () => {
        currentIndex = (currentIndex - 1 + chartTypes.length) % chartTypes.length;
        renderTestChart(chartTypes[currentIndex], canvas, appState);
        label.textContent = `目前圖表：${chartTypes[currentIndex]}`;
    });
    
    const nextBtn = document.createElement('button');
    nextBtn.textContent = '下一個圖表';
    nextBtn.style.padding = '5px 10px';
    nextBtn.addEventListener('click', () => {
        currentIndex = (currentIndex + 1) % chartTypes.length;
        renderTestChart(chartTypes[currentIndex], canvas, appState);
        label.textContent = `目前圖表：${chartTypes[currentIndex]}`;
    });
    
    testUI.appendChild(label);
    testUI.appendChild(prevBtn);
    testUI.appendChild(nextBtn);
    document.body.appendChild(testUI);
    
    console.log('圖表測試模組已啟動，使用右上角控制項切換不同圖表類型');
}

/**
 * 渲染測試圖表
 * @param {string} chartType - 圖表類型
 * @param {object} appState - 應用狀態
 * @param {string} theme - 圖表主題
 */
export function renderTestChart(chartType, appState, theme = 'default') {
    try {
        console.log(`-------------------------------------`);
        console.log(`開始測試 ${chartType} 圖表渲染`);
        console.log(`-------------------------------------`);
        
        // 檢查圖表是否支援
        if (!testData[chartType]) {
            console.error(`圖表類型 ${chartType} 沒有測試數據`);
            throw new Error(`無法測試 ${chartType} 圖表：缺少測試數據`);
        }
        
        // 取得測試數據
        const data = testData[chartType];
        console.log(`測試數據:`, data);
        
        // 特殊處理 - 確保金融圖表插件已載入
        if (['candlestick', 'ohlc'].includes(chartType)) {
            console.log('檢查金融圖表插件是否已載入');
            if (typeof Chart !== 'undefined') {
                const availableControllers = Object.keys(Chart.controllers || {});
                console.log('可用控制器:', availableControllers);
                
                if (!availableControllers.includes(chartType)) {
                    console.warn(`${chartType} 控制器不可用，嘗試手動註冊`);
                    
                    // 檢查是否有 window.CandlestickController 或 window.OhlcController
                    if (window.CandlestickController && chartType === 'candlestick') {
                        console.log('註冊 CandlestickController');
                        Chart.register(window.CandlestickController);
                    } else if (window.OhlcController && chartType === 'ohlc') {
                        console.log('註冊 OhlcController');
                        Chart.register(window.OhlcController);
                    } else if (window.Chart && window.Chart.controllers && window.Chart.controllers.financial) {
                        // 嘗試從 window.Chart.controllers.financial 獲取控制器
                        console.log('從財務插件註冊控制器');
                        if (chartType === 'candlestick' && window.Chart.controllers.financial.CandlestickController) {
                            Chart.register(window.Chart.controllers.financial.CandlestickController);
                        } else if (chartType === 'ohlc' && window.Chart.controllers.financial.OhlcController) {
                            Chart.register(window.Chart.controllers.financial.OhlcController);
                        }
                    } else {
                        console.error(`無法找到 ${chartType} 控制器，渲染可能失敗`);
                    }
                }
            } else {
                console.error('Chart.js 未加載，無法渲染圖表');
                throw new Error('Chart.js 庫未載入');
            }
        }
        
        // 嘗試渲染圖表
        console.log(`嘗試渲染 ${chartType} 圖表`);
        createChart(data, chartType, theme, appState);
        console.log(`${chartType} 圖表渲染完成`);
        
        // 更新狀態
        return true;
    } catch (error) {
        console.error(`測試 ${chartType} 圖表時出錯:`, error);
        alert(`無法渲染 ${chartType} 圖表: ${error.message}`);
        return false;
    }
}
