/**
 * 根據檔案名稱猜測最適合的圖表類型
 * @param {string} filename - 檔案名稱
 * @returns {string|null} - 猜測的圖表類型，如果無法猜測則返回 null
 */
export function guessChartTypeFromFilename(filename) {
    if (!filename) return null;
    
    // 將檔案名稱轉換為小寫以便比較
    const lowerFilename = filename.toLowerCase();
    
    // 根據關鍵字猜測圖表類型
    if (lowerFilename.includes('line') || lowerFilename.includes('trend')) {
        return 'line';
    } else if (lowerFilename.includes('bar') || lowerFilename.includes('column')) {
        return 'bar';
    } else if (lowerFilename.includes('pie') || lowerFilename.includes('donut')) {
        return 'pie';
    } else if (lowerFilename.includes('radar') || lowerFilename.includes('spider')) {
        return 'radar';
    } else if (lowerFilename.includes('scatter') || lowerFilename.includes('bubble')) {
        return 'scatter';
    } else if (lowerFilename.includes('candlestick') || lowerFilename.includes('ohlc')) {
        return 'candlestick';
    } else if (lowerFilename.includes('polar') || lowerFilename.includes('rose')) {
        return 'polarArea';
    } else if (lowerFilename.includes('sankey') || lowerFilename.includes('flow')) {
        return 'sankey';
    }
    
    return null;
} 