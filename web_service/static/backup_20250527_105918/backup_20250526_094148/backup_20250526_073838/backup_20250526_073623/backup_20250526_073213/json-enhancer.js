/**
 * JSON格式增強工具
 * 用於處理ApexCharts中的特殊JSON格式問題
 * 特別是處理字串化的函數
 */

(function() {
  console.log('JSON格式增強工具已載入');
  
  // 處理字符串化的函數
  function handleStringifiedFunctions(jsonObj) {
    if (!jsonObj || typeof jsonObj !== 'object') {
      return jsonObj;
    }
    
    // 遍歷所有屬性
    Object.keys(jsonObj).forEach(key => {
      const value = jsonObj[key];
      
      // 如果值是字符串並且看起來像是函數
      if (typeof value === 'string' && (value.startsWith('function(') || value.startsWith('function (') || value.includes('=>'))) {
        try {
          // 將字符串轉換為真實函數
          jsonObj[key] = new Function('return ' + value)();
          console.log(`成功將 ${key} 的字符串轉換為函數`);
        } catch (e) {
          console.warn(`無法將 ${key} 轉換為函數:`, e);
        }
      } 
      // 如果值是對象或數組，則遞歸處理
      else if (typeof value === 'object' && value !== null) {
        jsonObj[key] = handleStringifiedFunctions(value);
      }
    });
    
    return jsonObj;
  }
  
  // 完整的JSON解析處理函數
  function parseExtendedJSON(jsonText) {
    if (!jsonText) {
      return null;
    }
    
    try {
      // 首先嘗試標準JSON解析
      return JSON.parse(jsonText);
    } catch (e) {
      console.warn('標準JSON解析失敗，嘗試進行修復:', e);
      
      let processedText = jsonText;
      
      // 1. 移除註釋
      processedText = processedText.replace(/\/\/.*$/gm, '');
      processedText = processedText.replace(/\/\*[\s\S]*?\*\//g, '');
      
      // 2. 嘗試修復尾隨逗號
      processedText = processedText.replace(/,(\s*[\]}])/g, '$1');
      
      // 3. 修復缺少的引號
      processedText = processedText.replace(/([{,]\s*)(\w+)(\s*:)/g, '$1"$2"$3');
      
      try {
        // 再次嘗試解析
        const parsed = JSON.parse(processedText);
        console.log('修復後的JSON成功解析');
        return parsed;
      } catch (e2) {
        console.error('無法修復和解析JSON:', e2);
        throw e2;
      }
    }
  }
  
  // 將工具函數暴露到全局範圍
  window.JSONEnhancer = {
    // 解析JSON並處理函數
    parse: function(jsonText) {
      const parsed = parseExtendedJSON(jsonText);
      if (parsed) {
        return handleStringifiedFunctions(parsed);
      }
      return null;
    },
    
    // 只處理函數而不解析
    handleFunctions: handleStringifiedFunctions,
    
    // 只進行增強的JSON解析
    parseJSON: parseExtendedJSON,
    
    // 將對象轉換為格式化的JSON
    stringify: function(obj, beautify = true) {
      try {
        // 首先創建一個副本以防止修改原始對象
        const copy = JSON.parse(JSON.stringify(obj, function(key, value) {
          // 如果值是函數，則轉換為字符串
          if (typeof value === 'function') {
            return value.toString();
          }
          return value;
        }));
        
        // 返回格式化的JSON
        return JSON.stringify(copy, null, beautify ? 2 : 0);
      } catch (e) {
        console.error('轉換對象為JSON時發生錯誤:', e);
        return null;
      }
    }
  };
  
  console.log('JSON格式增強工具初始化完成');
})();
