/**
 * 統計卡片組件
 * 
 * 基於 DaisyUI 的統計卡片組件，包含標題、數值、描述和趨勢指標
 */

export function initStatCards() {
  Alpine.data('statCard', () => ({
    /**
     * 格式化數字
     * @param {number} value - 要格式化的數字
     * @param {string} type - 格式化類型 ('number', 'currency', 'percent')
     * @returns {string} 格式化後的數字
     */
    formatValue(value, type = 'number') {
      if (value === null || value === undefined) return '—';
      
      switch (type) {
        case 'currency':
          return new Intl.NumberFormat('zh-TW', {
            style: 'currency',
            currency: 'TWD',
            maximumFractionDigits: 0
          }).format(value);
          
        case 'percent':
          return new Intl.NumberFormat('zh-TW', {
            style: 'percent',
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
          }).format(value / 100);
          
        case 'number':
        default:
          return new Intl.NumberFormat('zh-TW').format(value);
      }
    },
    
    /**
     * 取得趨勢指標類別
     * @param {number} trend - 趨勢值
     * @returns {string} CSS 類別名稱
     */
    getTrendClass(trend) {
      if (trend === null || trend === undefined || trend === 0) return 'text-info';
      return trend > 0 ? 'text-success' : 'text-error';
    },
    
    /**
     * 取得趨勢指標符號
     * @param {number} trend - 趨勢值
     * @returns {string} HTML 符號
     */
    getTrendIcon(trend) {
      if (trend === null || trend === undefined || trend === 0) return '—';
      return trend > 0 ? '↑' : '↓';
    }
  }));
}
