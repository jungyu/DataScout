/**
 * 重構模組的單元測試
 */

import { expect } from 'chai';
import sinon from 'sinon';

import { getAppState, setStateValue, initializeAppState } from '../src/js/state-manager.js';
import { createOrUpdateChart, updateChartTheme } from '../src/js/chart-manager.js';
import { loadDataFile } from '../src/js/data-loader.js';

describe('重構模組單元測試', () => {
    // 在每個測試前重置狀態
    beforeEach(() => {
        // 清除 DOM 元素
        document.body.innerHTML = `
            <div id="chartContainer">
                <canvas id="chartCanvas"></canvas>
            </div>
            <select id="chartType">
                <option value="bar">長條圖</option>
                <option value="line">折線圖</option>
                <option value="radar">雷達圖</option>
            </select>
            <select id="chartTheme">
                <option value="default">預設主題</option>
                <option value="dark">黑暗主題</option>
            </select>
        `;
        
        // 初始化應用程式狀態
        initializeAppState();
    });
    
    describe('state-manager 模組測試', () => {
        it('應正確初始化應用程式狀態', () => {
            const appState = getAppState();
            expect(appState).to.be.an('object');
            expect(appState.currentChartType).to.equal('radar');
            expect(appState.currentDataType).to.equal('json');
            expect(appState.myChart).to.be.null;
        });
        
        it('應能正確設置和獲取狀態值', () => {
            setStateValue('currentChartType', 'bar');
            const appState = getAppState();
            expect(appState.currentChartType).to.equal('bar');
        });
    });
    
    describe('chart-manager 模組測試', () => {
        it('應能正確創建圖表', () => {
            // 模擬圖表數據
            const mockData = {
                labels: ['項目1', '項目2', '項目3'],
                datasets: [{
                    label: '測試數據',
                    data: [10, 20, 30],
                    backgroundColor: 'rgba(0, 123, 255, 0.5)'
                }]
            };
            
            // 模擬 createChart 函數
            global.createChart = sinon.stub().returns({
                data: mockData,
                destroy: sinon.spy()
            });
            
            const chart = createOrUpdateChart(mockData, 'bar', 'default');
            expect(chart).to.not.be.null;
            
            // 驗證狀態已更新
            const appState = getAppState();
            expect(appState.myChart).to.not.be.null;
        });
    });
    
    describe('data-loader 模組測試', () => {
        it('應能處理資料格式轉換', () => {
            // 導入要測試的函數
            const { ensureValidChartData } = require('../src/js/data-loader.js');
            
            // 測試原始陣列數據格式轉換
            const rawData = [
                { label: '系列1', A: 10, B: 20, C: 30, color: '#ff0000' },
                { label: '系列2', A: 15, B: 25, C: 35, color: '#00ff00' }
            ];
            
            const formattedData = ensureValidChartData(rawData, 'bar');
            
            expect(formattedData).to.be.an('object');
            expect(formattedData.labels).to.be.an('array');
            expect(formattedData.datasets).to.be.an('array');
            expect(formattedData.datasets[0].label).to.equal('系列1');
            expect(formattedData.datasets[0].backgroundColor).to.equal('#ff0000');
            expect(formattedData.datasets[0].data).to.deep.equal([10, 20, 30]);
        });
    });
});
