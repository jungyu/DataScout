/**
 * JSON函數處理工具
 * 用於處理JSON字串中的函數，使其能夠被正確解析和執行
 */

(function() {
  console.log('JSON函數處理工具已載入');
  
  // 處理JSON中的函數字串
  window.processJsonFunctions = function(obj) {
    if (!obj || typeof obj !== 'object') return obj;
    
    // 遍歷所有屬性
    for (const key in obj) {
      if (Object.prototype.hasOwnProperty.call(obj, key)) {
        const value = obj[key];
        
        // 處理字串函數
        if (typeof value === 'string' && 
            (value.startsWith('function(') || 
             value.startsWith('function (') || 
             value.includes('=>'))) {
          try {
            console.log(`嘗試將屬性 ${key} 的字串轉換為函數: ${value.substring(0, 30)}...`);
            obj[key] = new Function('return ' + value)();
            console.log(`成功轉換 ${key} 為函數`);
          } catch (e) {
            console.warn(`無法將 ${key} 轉換為函數: ${e.message}`);
          }
        } 
        // 遞歸處理子物件或陣列
        else if (typeof value === 'object' && value !== null) {
          obj[key] = window.processJsonFunctions(value);
        }
      }
    }
    
    return obj;
  };
})();
