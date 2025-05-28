/**
 * 圖表通用錯誤處理與修復工具 (增強版)
 * 提供統一的圖表錯誤處理與響應機制
 * 加強JSON解析錯誤處理
 */

(function() {
  console.log('圖表通用錯誤處理工具增強版已載入');

  // 提供一個獲取默認圖表數據的函數
  function getDefaultChartData(chartType = 'line') {
    console.log(`生成${chartType}圖表默認數據`);
    
    // 基本圖表結構
    const baseConfig = {
      chart: {
        type: chartType || 'line',
        height: 350,
        toolbar: {
          show: true
        }
      },
      title: {
        text: '預設資料圖表',
        align: 'center'
      }
    };
    
    // 根據不同圖表類型提供不同的默認數據
    switch (chartType) {
      case 'line':
      case 'area':
        baseConfig.series = [{
          name: '範例數據',
          data: [30, 40, 35, 50, 49, 60, 70, 91, 125]
        }];
        baseConfig.xaxis = {
          categories: ['一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月']
        };
        break;
        
      case 'bar':
      case 'column':
        baseConfig.series = [{
          name: '範例數據',
          data: [44, 55, 41, 67, 22, 43]
        }];
        baseConfig.xaxis = {
          categories: ['一月', '二月', '三月', '四月', '五月', '六月']
        };
        break;
        
      case 'pie':
      case 'donut':
      case 'polarArea':
        baseConfig.series = [44, 55, 41, 17, 15];
        baseConfig.labels = ['產品A', '產品B', '產品C', '產品D', '產品E'];
        break;
        
      case 'radar':
        baseConfig.series = [{
          name: '系列1',
          data: [80, 50, 30, 40, 100, 20]
        }];
        baseConfig.xaxis = {
          categories: ['項目A', '項目B', '項目C', '項目D', '項目E', '項目F']
        };
        break;
        
      case 'scatter':
        baseConfig.series = [{
          name: "範例A",
          data: [
            [16.4, 5.4], [21.7, 2.1], [25.4, 3.5],
            [19.0, 2.6], [10.9, 1.0], [13.6, 3.2]
          ]
        }];
        break;
        
      case 'heatmap':
        const series = [];
        const categories = ['01', '02', '03', '04', '05', '06'];
        for (let i = 0; i < 5; i++) {
          const data = [];
          for (let j = 0; j < categories.length; j++) {
            data.push({
              x: categories[j],
              y: Math.floor(Math.random() * 90) + 10
            });
          }
          series.push({
            name: `系列 ${i+1}`,
            data: data
          });
        }
        baseConfig.series = series;
        break;
        
      case 'treemap':
        baseConfig.series = [
          {
            data: [
              { x: 'A', y: 218 },
              { x: 'B', y: 149 },
              { x: 'C', y: 184 },
              { x: 'D', y: 55 }
            ]
          }
        ];
        break;
        
      default:
        baseConfig.series = [{
          name: '範例數據',
          data: [30, 40, 35, 50, 49, 60, 70]
        }];
    }
    
    return baseConfig;
  }
  
  // 修復JSON格式問題
  function fixJsonFormatting(jsonText) {
    console.log('嘗試修復JSON格式問題');
    
    // 如果JSON增強器可用，則使用它
    if (window.JSONEnhancer && typeof window.JSONEnhancer.parse === 'function') {
      try {
        return window.JSONEnhancer.parse(jsonText);
      } catch (e) {
        console.warn('JSONEnhancer解析失敗，嘗試備用方法', e);
      }
    }
    
    // 以下是備用方法
    if (!jsonText) {
      return null;
    }
    
    // 移除可能的註釋
    let processed = jsonText.replace(/\/\/.*$/gm, '');
    processed = processed.replace(/\/\*[\s\S]*?\*\//g, '');
    
    // 處理尾隨逗號
    processed = processed.replace(/,(\s*[\]}])/g, '$1');
    
    try {
      return JSON.parse(processed);
    } catch (e) {
      console.error('無法修復JSON格式:', e);
      return null;
    }
  }
  
  // 處理函數字串
  function processFunctionStrings(chartConfig) {
    if (!chartConfig || typeof chartConfig !== 'object') {
      return chartConfig;
    }
    
    // 如果JSONEnhancer存在，使用它來處理
    if (window.JSONEnhancer && typeof window.JSONEnhancer.handleFunctions === 'function') {
      return window.JSONEnhancer.handleFunctions(chartConfig);
    }
    
    // 否則使用備用方法
    const processFunctions = (obj) => {
      if (!obj || typeof obj !== 'object') return obj;
      
      Object.keys(obj).forEach(key => {
        const value = obj[key];
        
        if (typeof value === 'string' && (value.startsWith('function(') || value.startsWith('function (') || value.includes('=>'))) {
          try {
            obj[key] = new Function('return ' + value)();
          } catch (e) {
            console.warn(`無法將屬性 ${key} 轉換為函數:`, e);
          }
        } else if (typeof value === 'object' && value !== null) {
          processFunctions(value);
        }
      });
      
      return obj;
    };
    
    return processFunctions(chartConfig);
  }
  
  // 顯示錯誤訊息的函數
  function showError(message, elementId = 'error-message') {
    const errorElement = document.getElementById(elementId);
    if (errorElement) {
      errorElement.innerText = message;
      errorElement.style.display = 'block';
    } else {
      console.error('錯誤訊息元素未找到:', message);
    }
  }

  // 重試載入數據的增強版
  function retryLoadData(chartType, alternativeFiles, elementId, handlerFunction) {
    console.log(`嘗試重新載入${chartType}圖表數據`);
    
    // 如果沒有提供備用文件，使用預設值
    if (!alternativeFiles || alternativeFiles.length === 0) {
      alternativeFiles = [
        `apexcharts_${chartType}_default.json`,
        // 添加一些通用的備用選項
        `apexcharts_${chartType}_sample.json`,
        `apexcharts_${chartType}_basic.json`
      ];
    }
    
    // 依序嘗試每個備用文件
    const tryNextFile = (index = 0) => {
      if (index >= alternativeFiles.length) {
        console.warn(`所有備用文件嘗試失敗，使用默認數據`);
        const defaultData = getDefaultChartData(chartType);
        
        if (typeof handlerFunction === 'function') {
          handlerFunction(defaultData);
          return;
        } else if (typeof window[`handle${chartType.charAt(0).toUpperCase() + chartType.slice(1)}Chart`] === 'function') {
          window[`handle${chartType.charAt(0).toUpperCase() + chartType.slice(1)}Chart`](defaultData);
          return;
        } else {
          console.error(`找不到${chartType}圖的處理函數，無法渲染默認數據`);
          return;
        }
      }
      
      const fileName = alternativeFiles[index];
      console.log(`嘗試載入備用檔案: ${fileName}`);
      
      fetch(`/static/assets/examples/${fileName}`)
        .then(response => {
          if (!response.ok) {
            throw new Error(`無法載入檔案 ${fileName}`);
          }
          return response.text(); // 先以文本形式獲取，以便處理可能的JSON錯誤
        })
        .then(text => {
          // 嘗試解析JSON
          const data = fixJsonFormatting(text);
          
          if (!data) {
            throw new Error('資料為空或格式錯誤');
          }
          
          console.log(`成功載入備用資料: ${fileName}`);
          
          // 確保圖表類型正確
          if (!data.chart) data.chart = {};
          data.chart.type = chartType;
          
          // 使用提供的處理函數渲染圖表
          if (typeof handlerFunction === 'function') {
            handlerFunction(data);
          } else if (typeof window[`handle${chartType.charAt(0).toUpperCase() + chartType.slice(1)}Chart`] === 'function') {
            window[`handle${chartType.charAt(0).toUpperCase() + chartType.slice(1)}Chart`](data);
          } else {
            console.error(`找不到${chartType}圖的處理函數`);
            throw new Error(`找不到${chartType}圖的處理函數`);
          }
        })
        .catch(error => {
          console.warn(`載入備用文件 ${fileName} 失敗: ${error.message}，嘗試下一個`);
          tryNextFile(index + 1);
        });
    };
    
    // 開始嘗試第一個備用文件
    tryNextFile();
  }
  
  // 處理圖表錯誤的增強版
  function processChartError(error, chartType, elementId) {
    console.error('處理圖表錯誤:', error);
    
    // 顯示錯誤訊息
    showError('圖表載入失敗，正在嘗試修復...', elementId);
    
    // 嘗試修復JSON格式
    if (error.message.includes('JSON')) {
      console.log('嘗試修復JSON格式錯誤');
      const fixedData = fixJsonFormatting(error.data);
      
      if (fixedData) {
        console.log('成功修復JSON格式錯誤');
        
        // 嘗試重新載入圖表
        if (typeof window[`handle${chartType.charAt(0).toUpperCase() + chartType.slice(1)}Chart`] === 'function') {
          window[`handle${chartType.charAt(0).toUpperCase() + chartType.slice(1)}Chart`](fixedData);
          return;
        }
      } else {
        console.warn('無法修復的JSON格式錯誤');
      }
    }
    
    // 嘗試重新載入數據
    retryLoadData(chartType, [], elementId, null);
  }

  // 將工具暴露到全局範圍
  window.chartErrorHandlerEnhanced = {
    getDefaultChartData: getDefaultChartData,
    fixJsonFormatting: fixJsonFormatting,
    processFunctionStrings: processFunctionStrings,
    showError: showError,
    retryLoadData: retryLoadData,
    processChartError: processChartError
  };
  
  console.log('圖表通用錯誤處理工具增強版準備就緒');
})();
