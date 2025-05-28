/**
 * 圖表格式器修復工具
 * 用來處理所有圖表中的formatter函數問題
 */

(function() {
  console.log('圖表格式器修復工具已啟動');

  // 修復JSON文件中的formatter函數
  window.fixChartFormatters = function(jsonData) {
    if (!jsonData) return jsonData;
    
    // 處理所有可能的formatter位置
    
    // 處理yaxis formatter
    if (jsonData.yaxis) {
      if (Array.isArray(jsonData.yaxis)) {
        // 多個y軸
        jsonData.yaxis.forEach(axis => {
          if (axis.labels && axis.labels.formatter) {
            axis.labels.formatter = null;
          }
        });
      } else if (jsonData.yaxis.labels && jsonData.yaxis.labels.formatter) {
        // 單一y軸
        jsonData.yaxis.labels.formatter = null;
      }
    }
    
    // 處理xaxis formatter
    if (jsonData.xaxis && jsonData.xaxis.labels && jsonData.xaxis.labels.formatter) {
      jsonData.xaxis.labels.formatter = null;
    }
    
    // 處理tooltip formatter
    if (jsonData.tooltip) {
      if (jsonData.tooltip.y && jsonData.tooltip.y.formatter) {
        jsonData.tooltip.y.formatter = null;
      }
      if (jsonData.tooltip.x && jsonData.tooltip.x.formatter) {
        jsonData.tooltip.x.formatter = null;
      }
    }
    
    // 處理dataLabels formatter
    if (jsonData.dataLabels && jsonData.dataLabels.formatter) {
      jsonData.dataLabels.formatter = null;
    }
    
    // 處理legend formatter
    if (jsonData.legend && jsonData.legend.formatter) {
      jsonData.legend.formatter = null;
    }
    
    console.log('已修復所有formatter函數');
    return jsonData;
  };
  
  // 替換原先的JSON解析方法
  const originalJSONParse = JSON.parse;
  JSON.parse = function(text) {
    const result = originalJSONParse.apply(this, arguments);
    return window.fixChartFormatters(result);
  };
  
  // 修改fetch方法
  const originalFetch = window.fetch;
  window.fetch = function(input, init) {
    return originalFetch.apply(this, arguments)
      .then(response => {
        const clonedResponse = response.clone();
        // 檢查是否為JSON響應並且來自examples目錄
        if (typeof input === 'string' && 
            input.includes('/examples/') && 
            input.endsWith('.json')) {
          return clonedResponse.json()
            .then(data => {
              const fixedData = window.fixChartFormatters(data);
              
              // 創建新的響應以替換原始響應
              const jsonStr = JSON.stringify(fixedData);
              const blob = new Blob([jsonStr], {type: 'application/json'});
              const init = {
                status: response.status,
                statusText: response.statusText,
                headers: response.headers
              };
              return new Response(blob, init);
            })
            .catch(() => {
              // 如果不是有效的JSON，返回原始響應
              return response;
            });
        }
        return response;
      });
  };
  
  console.log('圖表格式器修復工具初始化完成');
})();
