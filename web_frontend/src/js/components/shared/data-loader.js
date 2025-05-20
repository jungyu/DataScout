/**
 * 資料加載器組件
 * 
 * 處理資料加載、錯誤處理和重試邏輯的公共組件
 */

export function initDataLoader() {
  Alpine.data('dataLoader', () => ({
    /**
     * 資料狀態
     */
    loading: false,
    error: null,
    data: null,
    lastUpdated: null,
    
    /**
     * 初始化
     */
    init() {
      this.$watch('loading', value => {
        if (value) {
          this.error = null;
        }
      });
    },
    
    /**
     * 加載資料
     * @param {Function} fetchFunction - 加載資料的非同步函數
     * @param {Function} dataProcessor - 資料處理函數 (可選)
     * @returns {Promise} 資料加載結果
     */
    async load(fetchFunction, dataProcessor = null) {
      try {
        this.loading = true;
        
        // 非同步資料獲取
        const result = await fetchFunction();
        
        // 可選的資料處理
        if (dataProcessor && typeof dataProcessor === 'function') {
          this.data = dataProcessor(result);
        } else {
          this.data = result;
        }
        
        this.lastUpdated = new Date();
        return this.data;
      } catch (err) {
        this.error = {
          message: err.message || '資料加載失敗',
          details: err.toString()
        };
        console.error('資料加載錯誤:', err);
        throw err;
      } finally {
        this.loading = false;
      }
    },
    
    /**
     * 重新加載資料
     * @returns {Promise}
     */
    async reload() {
      if (!this.loading && this._lastFetchFunction) {
        return this.load(this._lastFetchFunction, this._lastDataProcessor);
      }
    },
    
    /**
     * 格式化更新時間
     * @returns {string}
     */
    getLastUpdatedText() {
      if (!this.lastUpdated) return '尚未更新';
      
      return new Intl.DateTimeFormat('zh-TW', {
        year: 'numeric',
        month: 'numeric',
        day: 'numeric',
        hour: 'numeric',
        minute: 'numeric',
        second: 'numeric'
      }).format(this.lastUpdated);
    }
  }));
}
