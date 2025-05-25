/**
 * JSON格式修復工具
 * 處理圖表JSON文件中的函數字符串問題
 */

(function() {
  console.log('JSON格式修復工具已啟動');
  
  // 原始JSON.parse方法
  const originalJSONParse = JSON.parse;
  
  // 替換JSON.parse方法，添加對函數字符串的處理
  JSON.parse = function(text, reviver) {
    // 首先嘗試進行標準解析
    try {
      return originalJSONParse(text, reviver);
    } catch (e) {
      // 如果解析失敗，可能是因為包含函數字符串，嘗試預處理
      console.warn('標準JSON解析失敗，嘗試處理函數字符串:', e);
      
      try {
        // 處理常見的函數字符串模式
        const processedText = handleFunctionStrings(text);
        
        // 再次嘗試解析
        return originalJSONParse(processedText, reviver);
      } catch (e2) {
        // 如果依然失敗，嘗試更深入的修復
        console.warn('預處理後仍然無法解析JSON，嘗試深層修復:', e2);
        
        try {
          // 更進階的修復嘗試
          const deepFixText = deepJsonRepair(text);
          return originalJSONParse(deepFixText, reviver);
        } catch (e3) {
          // 所有修復嘗試都失敗
          console.error('所有修復嘗試都失敗:', e3);
          throw e3; // 拋出最新的錯誤
        }
      }
    }
  };
  
  // 處理函數字符串
  function handleFunctionStrings(jsonText) {
    if (typeof jsonText !== 'string') return jsonText;
    
    let processed = jsonText;
    
    // 先移除所有註解以避免干擾解析
    processed = processed.replace(/\/\/.*$/gm, '');
    processed = processed.replace(/\/\*[\s\S]*?\*\//g, '');
    
    // 修復常見的JSON格式問題
    processed = processed.replace(/,(\s*[\]}])/g, '$1'); // 移除JSON最後一個元素後的逗號
    processed = processed.replace(/([^"])(')([^']*?)(')/g, '$1"$3"'); // 將單引號轉換為雙引號
    processed = processed.replace(/(\w+)(\s*:)/g, '"$1"$2'); // 確保屬性名稱使用雙引號
    
    // 修復格式化器(formatter)函數字符串
    processed = processed.replace(/"formatter"\s*:\s*function\s*\(/g, '"formatter": "function(');
    processed = processed.replace(/(\n\s*}"?)(\s*[,}])/g, '$1"$2'); // 修復多行函數結尾
    
    // 處理其他常見函數字符串模式
    processed = processed.replace(/:\s*function\s*\(/g, ': "function(');
    processed = processed.replace(/}(\s*[,}])/g, '}"$1');
    
    // 處理更多特殊情況
    processed = processed.replace(/(\w+)\s*:\s*function\s*\(/g, '"$1": "function('); // 無引號的函數屬性
    processed = processed.replace(/("[\w]+")\s*:\s*(\w+)(?=\s*[,}])/g, '$1: "$2"'); // 引號屬性名稱但值無引號
    processed = processed.replace(/undefined/g, '"undefined"'); // undefined 值
    processed = processed.replace(/NaN/g, '"NaN"'); // NaN 值
    processed = processed.replace(/Infinity/g, '"Infinity"'); // Infinity 值
    
    // 處理其他常見的函數模式
    const functionPropRegex = /"(\w+)"\s*:\s*function\s*\(/g;
    let match;
    while ((match = functionPropRegex.exec(processed)) !== null) {
      const propName = match[1];
      console.log(`找到可能的函數屬性: ${propName}`);
      
      // 查找這個函數的結束位置
      const startPos = match.index;
      const propNameLength = propName.length;
      let bracketCount = 0;
      let inString = false;
      let stringChar = '';
      let endPos = -1;
      
      for (let i = startPos + propNameLength + 4; i < processed.length; i++) {
        const char = processed[i];
        
        // 字符串處理
        if ((char === '"' || char === "'") && (i === 0 || processed[i-1] !== '\\')) {
          if (!inString) {
            inString = true;
            stringChar = char;
          } else if (char === stringChar) {
            inString = false;
          }
        }
        
        // 跳過字符串內容
        if (inString) continue;
        
        // 大括號計數
        if (char === '{') {
          bracketCount++;
        } else if (char === '}') {
          bracketCount--;
          if (bracketCount === 0) {
            endPos = i;
            break;
          }
        }
      }
      
      // 如果找到閉合的大括號，將這個函數轉換為字符串
      if (endPos !== -1) {
        // 提取整個函數體
        const funcStr = processed.substring(startPos, endPos + 1);
        // 轉換為字符串表示
        const stringifiedFunc = funcStr.replace(/function\s*\(/, '"function(').replace(/}$/, '}"');
        // 替換原文本
        processed = processed.substring(0, startPos) + stringifiedFunc + processed.substring(endPos + 1);
      }
    }
    
    return processed;
  }
  
  // 深度 JSON 修復，處理更複雜的情況
  function deepJsonRepair(jsonText) {
    if (typeof jsonText !== 'string') return jsonText;
    
    let processed = jsonText;
    
    // 基本清理
    processed = processed.trim();
    
    // 確保 JSON 以 { 開頭和 } 結尾，或以 [ 開頭和 ] 結尾
    if (!processed.startsWith('{') && !processed.startsWith('[')) {
      processed = '{' + processed;
    }
    if (!processed.endsWith('}') && !processed.endsWith(']')) {
      processed = processed + '}';
    }
    
    // 確保所有的屬性名都有雙引號
    processed = processed.replace(/(\s*)(\w+)(\s*):(\s*)/g, '$1"$2"$3:$4');
    
    // 處理函數定義
    processed = processed.replace(/:\s*function\s*\(/g, ': "function(');
    
    // 處理特殊字符和值
    processed = processed.replace(/(\s*:\s*)(true|false|null)(\s*[,}])/g, '$1"$2"$3');
    
    // 處理數字值作為字符串
    processed = processed.replace(/(\s*:\s*)(\d+(\.\d+)?)(\s*[,}])/g, '$1"$2"$4');
    
    // 處理無引號的字符串值
    processed = processed.replace(/(\s*:\s*)([a-zA-Z0-9_]+)(\s*[,}])/g, '$1"$2"$3');
    
    // 處理尾隨逗號
    processed = processed.replace(/,(\s*[\]}])/g, '$1');
    
    // 嘗試確保開閉括號數量匹配
    let openBraces = (processed.match(/{/g) || []).length;
    let closeBraces = (processed.match(/}/g) || []).length;
    while (openBraces > closeBraces) {
      processed += '}';
      closeBraces++;
    }
    while (closeBraces > openBraces) {
      processed = processed.replace(/}([^}]*)$/, '$1');
      closeBraces--;
    }
    
    let openBrackets = (processed.match(/\[/g) || []).length;
    let closeBrackets = (processed.match(/\]/g) || []).length;
    while (openBrackets > closeBrackets) {
      processed += ']';
      closeBrackets++;
    }
    while (closeBrackets > openBrackets) {
      processed = processed.replace(/\]([^\]]*)$/, '$1');
      closeBrackets--;
    }
    
    return processed;
  }

  // 導出全局修復功能
  window.jsonFormatterFix = {
    handleFunctionStrings: handleFunctionStrings,
    deepJsonRepair: deepJsonRepair
  };
})();
