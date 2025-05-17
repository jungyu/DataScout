/**
 * 圖表測試腳本
 * 用於測試圖表功能是否正確工作
 * 
 * 此文件已從 static/js 移動到 tests/js 目錄，
 * 作為適當的測試代碼結構管理。
 */

(function() {
    // 在頁面載入完成後執行
    document.addEventListener('DOMContentLoaded', function() {
        console.log('圖表測試腳本啟動...');
        
        // 延遲執行，確保所有圖表腳本都已載入
        setTimeout(runTests, 500);
    });
    
    function runTests() {
        console.log('開始圖表功能測試...');
        
        // 測試 Chart.js 是否正確載入
        testChartJsLoaded();
        
        // 測試特殊圖表類型
        testSpecialChartTypes();
        
        // 測試錯誤處理機制
        testErrorHandling();
    }
    
    // 測試 Chart.js 是否正確載入
    function testChartJsLoaded() {
        console.log('測試 Chart.js 載入狀態...');
        
        if (typeof Chart !== 'undefined') {
            console.log('Chart.js 已成功載入，版本：', Chart.version);
            console.log('支援的控制器：', Object.keys(Chart.controllers || {}));
        } else {
            console.error('Chart.js 未載入！');
        }
    }
    
    // 測試特殊圖表類型
    function testSpecialChartTypes() {
        console.log('測試特殊圖表類型...');
        
        // 測試蝴蝶圖處理函數
        if (typeof window.processButterFlyData === 'function') {
            console.log('蝴蝶圖處理函數已就緒');
            
            // 嘗試執行處理函數
            try {
                const testData = {
                    labels: ['測試1', '測試2', '測試3'],
                    datasets: [
                        {
                            label: '測試數據集1',
                            data: [10, 20, 30]
                        }
                    ]
                };
                
                const processedData = window.processButterFlyData({data: testData});
                console.log('蝴蝶圖數據處理結果：', processedData);
                
                if (processedData.datasets && processedData.datasets.length >= 2) {
                    console.log('蝴蝶圖處理函數工作正常');
                } else {
                    console.warn('蝴蝶圖處理函數可能未正確生成第二個數據集');
                }
            } catch (e) {
                console.error('蝴蝶圖處理函數執行出錯：', e);
            }
        } else {
            console.error('蝴蝶圖處理函數未載入！');
        }
        
        // 測試桑基圖控制器
        if (typeof Chart !== 'undefined') {
            if (Chart.controllers.sankey) {
                console.log('桑基圖控制器已就緒');
            } else {
                console.error('桑基圖控制器未載入！');
                
                // 嘗試初始化擴展
                if (typeof window.initChartExtensions === 'function') {
                    console.log('嘗試初始化圖表擴展...');
                    window.initChartExtensions();
                    
                    // 再次檢查
                    if (Chart.controllers.sankey) {
                        console.log('桑基圖控制器已成功初始化');
                    } else {
                        console.error('無法初始化桑基圖控制器');
                    }
                }
            }
        }
    }
    
    // 測試錯誤處理機制
    function testErrorHandling() {
        console.log('測試錯誤處理機制...');
        
        // 測試帶有無效數據的圖表處理
        try {
            const invalidData = null;
            
            // 嘗試處理蝴蝶圖
            if (typeof window.processButterFlyData === 'function') {
                console.log('測試蝴蝶圖處理函數錯誤恢復能力...');
                const result = window.processButterFlyData(invalidData);
                
                if (result && result.datasets && result.labels) {
                    console.log('蝴蝶圖處理函數成功處理了無效數據：', result);
                } else {
                    console.warn('蝴蝶圖處理函數未能正確處理無效數據');
                }
            }
            
        } catch (e) {
            console.error('錯誤處理測試失敗：', e);
        }
    }
    
    // 輸出測試結果
    function logTestResults(success, message) {
        if (success) {
            console.log('✅ 測試通過:', message);
        } else {
            console.error('❌ 測試失敗:', message);
        }
    }
})();
