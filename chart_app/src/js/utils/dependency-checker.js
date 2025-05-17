/**
 * 依賴檢查模組
 * 檢查圖表應用所需的依賴項目是否正確載入
 */

/**
 * 檢查 Chart.js 及其擴展是否正確載入
 * @returns {Object} 檢查結果
 */
export function checkChartJsDependencies() {
    const results = {
        chartJs: false,
        candlestick: false,
        ohlc: false,
        sankey: false,
        availableControllers: [],
        missingPlugins: []
    };
    
    // 檢查 Chart.js 是否正確載入
    if (typeof Chart === 'undefined') {
        console.error('Chart.js 未正確載入，圖表將無法顯示');
    } else {
        results.chartJs = true;
        
        // 檢查是否有蠟燭圖擴展
        if (!Chart.controllers.candlestick) {
            console.error('Chart.js 蠟燭圖擴展未正確載入，請確保已引入 chartjs-chart-financial.js');
            results.missingPlugins.push('candlestick');
        } else {
            results.candlestick = true;
        }
        
        // 檢查是否有OHLC圖擴展
        if (!Chart.controllers.ohlc) {
            console.error('Chart.js OHLC圖擴展未正確載入，請確保已引入 chartjs-chart-financial.js');
            results.missingPlugins.push('ohlc');
        } else {
            results.ohlc = true;
        }
        
        // 檢查是否有桑基圖擴展
        if (!Chart.controllers.sankey) {
            console.error('Chart.js 桑基圖擴展未正確載入，請確保已引入 chartjs-chart-sankey.js');
            results.missingPlugins.push('sankey');
        } else {
            results.sankey = true;
        }
        
        // 確認可用的圖表類型
        if (Chart.controllers) {
            results.availableControllers = Object.keys(Chart.controllers);
            console.log('可用圖表類型:', results.availableControllers);
        }
    }
    
    return results;
}

/**
 * 檢查是否瀏覽器支援 Canvas
 * @returns {boolean} 是否支援 Canvas
 */
export function checkCanvasSupport() {
    const canvas = document.createElement('canvas');
    const isSupported = !!(canvas.getContext && canvas.getContext('2d'));
    
    if (!isSupported) {
        console.error('您的瀏覽器不支援 Canvas，圖表將無法顯示');
    }
    
    return isSupported;
}

/**
 * 檢查所有依賴
 * 包括 Chart.js、擴展和瀏覽器功能支援
 */
export function checkAllDependencies() {
    console.log('檢查應用程式依賴...');
    
    const canvasSupport = checkCanvasSupport();
    const chartResults = checkChartJsDependencies();
    
    // 驗證結果
    if (canvasSupport && chartResults.chartJs) {
        console.log('基本圖表功能正常');
        
        // 檢查擴展支援
        if (chartResults.missingPlugins.length > 0) {
            console.warn(`部分圖表擴展未載入: ${chartResults.missingPlugins.join(', ')}`);
        } else {
            console.log('所有圖表擴展皆已正確載入');
        }
    } else {
        console.error('圖表核心功能不可用，請檢查依賴或瀏覽器支援');
    }
    
    console.log('依賴檢查完成');
}
