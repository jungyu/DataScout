/**
 * 圖表數據載入器
 * 用於從 JSON 文件中加載圖表數據並初始化圖表
 */

document.addEventListener('DOMContentLoaded', () => {
  // 檢測當前頁面的圖表類型
  const currentPath = window.location.pathname;
  let chartType = 'candlestick'; // 默認為蠟燭圖

  // 更精確的路徑檢測
  if (currentPath.endsWith('/') || currentPath.endsWith('/index.html')) {
    chartType = 'candlestick'; // 首頁是蠟燭圖
    console.log('偵測到首頁，設定圖表類型為：蠟燭圖');
  } else if (currentPath.includes('/line')) {
    chartType = 'line';
    console.log('偵測到路徑包含 line，設定圖表類型為：折線圖');
  } else if (currentPath.includes('/polararea')) {
    chartType = 'polararea';
    console.log('偵測到路徑包含 polararea，設定圖表類型為：極區域圖');
  } else if (currentPath.includes('/area')) {
    chartType = 'area';
    console.log('偵測到路徑包含 area，設定圖表類型為：區域圖');
  } else if (currentPath.includes('/column')) {
    chartType = 'column';
    console.log('偵測到路徑包含 column，設定圖表類型為：柱狀圖');
  } else if (currentPath.includes('/pie')) {
    chartType = 'pie';
    console.log('偵測到路徑包含 pie，設定圖表類型為：圓餅圖');
  } else if (currentPath.includes('/donut')) {
    chartType = 'donut';
    console.log('偵測到路徑包含 donut，設定圖表類型為：環形圖');
  } else if (currentPath.includes('/radar')) {
    chartType = 'radar';
    console.log('偵測到路徑包含 radar，設定圖表類型為：雷達圖');
  } else if (currentPath.includes('/polararea')) {
    chartType = 'polarArea';
    console.log('偵測到路徑包含 polararea，設定圖表類型為：極區域圖');
  }
  
  console.log('當前頁面路徑:', currentPath, '圖表類型:', chartType);
  
  // 資料選擇器組件監聽
  document.addEventListener('component-loaded', function(e) {
    if (e.detail.componentPath === 'components/ui/ChartDataSelector.html') {
      console.log('資料選擇器組件已載入，等待組件自初始化...');
      
      // 為每個數據項添加點擊事件，在組件完全初始化後
      setTimeout(() => {
        attachDataItemListeners();
      }, 500);
    }
  });
  
  // 監聽資料選擇器初始化事件
  document.addEventListener('chart-data-selector-initialized', function(e) {
    console.log('收到資料選擇器初始化事件:', e.detail);
    
    // 檢查資料選擇器是否正確顯示了對應圖表類型的數據
    const dataBlocks = document.querySelectorAll('.chart-data-block');
    dataBlocks.forEach(block => {
      const blockType = block.getAttribute('data-chart-type');
      console.log(`數據區塊 [${blockType}] 顯示狀態:`, window.getComputedStyle(block).display);
    });
  });
  
  // 為數據項添加點擊事件
  function attachDataItemListeners() {
    // 獲取所有具有 data-chart-type 屬性的數據項
    const dataItems = document.querySelectorAll('[data-chart-type]');
    console.log('找到數據項數量:', dataItems.length);
    
    dataItems.forEach(item => {
      const itemChartType = item.getAttribute('data-chart-type');
      const itemId = item.getAttribute('id');
      
      // 只處理與當前圖表類型相符的數據項
      if (itemChartType === chartType) {
        const loadButton = item.querySelector('button');
        
        if (loadButton && !loadButton._hasClickListener) {
          loadButton._hasClickListener = true;
          loadButton.addEventListener('click', () => {
            // 根據數據項ID確定要加載的JSON文件
            let jsonFile = '';
            
            switch(itemId) {
              // 線圖數據
              case 'sales-data':
                jsonFile = '/static/assets/examples/apexcharts_line_sales.json';
                break;
              case 'revenue-data':
                jsonFile = '/static/assets/examples/apexcharts_timeseries_line_unemployment.json';
                break;
              case 'web-traffic-data':
                jsonFile = '/static/assets/examples/apexcharts_line_sales.json';
                break;
              
              // 區域圖數據
              case 'webstat-data':
                jsonFile = '/static/assets/examples/apexcharts_area_webstat.json';
                break;
              case 'traffic-data':
                jsonFile = '/static/assets/examples/apexcharts_timeseries_area_debt.json';
                break;
              case 'engagement-data':
                jsonFile = '/static/assets/examples/apexcharts_area_webstat.json';
                break;
              
              // 柱狀圖數據
              case 'finance-data':
                jsonFile = '/static/assets/examples/apexcharts_column_finance.json';
                break;
              case 'product-data':
                jsonFile = '/static/assets/examples/apexcharts_grouped_bar_sales.json';
                break;
              case 'comparison-data':
                jsonFile = '/static/assets/examples/apexcharts_stacked_bar_finance.json';
                break;
              
              // 蠟燭圖數據
              case 'apple-data':
                jsonFile = '/static/assets/examples/apexcharts_candlestick_stock.json';
                break;
              case 'tsmc-data':
                jsonFile = '/static/assets/examples/apexcharts_candlestick_stock.json';
                break;
              case 'btc-data':
                jsonFile = '/static/assets/examples/apexcharts_candlestick_stock.json';
                break;
              
              default:
                console.error('未知的數據項ID:', itemId);
                return;
            }
            
            // 加載並處理JSON數據
            loadChartData(jsonFile);
            
            // 顯示通知
            showNotification(`正在載入 ${item.querySelector('.font-medium').textContent} 範例資料...`);
          });
          console.log('為數據項添加了點擊事件:', itemId);
        }
      }
    });
  }
  
  // 加載圖表數據
  function loadChartData(jsonFile) {
    fetch(jsonFile)
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => {
        // 根據圖表類型處理數據
        switch(chartType) {
          case 'line':
            updateLineChart(data);
            break;
          case 'area':
            updateAreaChart(data);
            break;
          case 'column':
            updateColumnChart(data);
            break;
          case 'candlestick':
            updateCandlestickChart(data);
            break;
          case 'pie':
            updatePieChart(data);
            break;
          case 'donut':
            updateDonutChart(data);
            break;
          case 'radar':
            updateRadarChart(data);
            break;
          case 'polarArea':
            updatePolarAreaChart(data);
            break;
          default:
            console.error('未支援的圖表類型:', chartType);
        }
      })
      .catch(error => {
        console.error('加載圖表數據時出錯:', error);
        showNotification('載入資料失敗，請重試', 'error');
      });
  }
  
  // 更新線圖
  function updateLineChart(data) {
    const chart = ApexCharts.getChartByID('lineChart');
    if (chart) {
      // 檢查並轉換 formatter 字串為函數
      if (data && data.yaxis && data.yaxis.labels && typeof data.yaxis.labels.formatter === 'string') {
        try {
          // 使用 new Function 將字串轉換為函數
          data.yaxis.labels.formatter = new Function('val', 'return ' + data.yaxis.labels.formatter.substring(data.yaxis.labels.formatter.indexOf('{') + 1, data.yaxis.labels.formatter.lastIndexOf('}')));
          console.log('成功將線圖 formatter 字串轉換為函數');
        } catch (e) {
          console.error('轉換線圖 formatter 字串為函數失敗:', e);
          // 如果轉換失敗，移除 formatter 選項以避免錯誤
          delete data.yaxis.labels.formatter;
        }
      }
      
      chart.updateOptions(data);
      showNotification('線圖資料已成功載入');
    } else {
      console.error('找不到線圖實例');
    }
  }
  
  // 更新區域圖
  function updateAreaChart(data) {
    const chart = ApexCharts.getChartByID('areaChart');
    if (chart) {
      // 移除所有 formatter 函數以避免錯誤
      removeAllFormatters(data);
      console.log('已移除所有區域圖 formatter 函數');
      
      chart.updateOptions(data);
      showNotification('區域圖資料已成功載入');
    } else {
      console.error('找不到區域圖實例');
    }
  }
  
  // 更新柱狀圖
  function updateColumnChart(data) {
    const chart = ApexCharts.getChartByID('columnChart');
    if (chart) {
      // 檢查並轉換 formatter 字串為函數
      if (data && data.yaxis && data.yaxis.labels && typeof data.yaxis.labels.formatter === 'string') {
        try {
          // 使用 new Function 將字串轉換為函數
          data.yaxis.labels.formatter = new Function('val', 'return ' + data.yaxis.labels.formatter.substring(data.yaxis.labels.formatter.indexOf('{') + 1, data.yaxis.labels.formatter.lastIndexOf('}')));
          console.log('成功將柱狀圖 formatter 字串轉換為函數');
        } catch (e) {
          console.error('轉換柱狀圖 formatter 字串為函數失敗:', e);
          // 如果轉換失敗，移除 formatter 選項以避免錯誤
          delete data.yaxis.labels.formatter;
        }
      }
      
      chart.updateOptions(data);
      showNotification('柱狀圖資料已成功載入');
    } else {
      console.error('找不到柱狀圖實例');
    }
  }
  
  // 更新蠟燭圖
  function updateCandlestickChart(data) {
    const chart = ApexCharts.getChartByID('candlestickChart');
    if (chart) {
      // 檢查並轉換 formatter 字串為函數
      if (data && data.yaxis && data.yaxis.labels && typeof data.yaxis.labels.formatter === 'string') {
        try {
          // 使用 new Function 將字串轉換為函數
          data.yaxis.labels.formatter = new Function('val', 'return ' + data.yaxis.labels.formatter.substring(data.yaxis.labels.formatter.indexOf('{') + 1, data.yaxis.labels.formatter.lastIndexOf('}')));
          console.log('成功將蠟燭圖 formatter 字串轉換為函數');
        } catch (e) {
          console.error('轉換蠟燭圖 formatter 字串為函數失敗:', e);
          // 如果轉換失敗，移除 formatter 選項以避免錯誤
          delete data.yaxis.labels.formatter;
        }
      }
      
      // 蠟燭圖可能還有 tooltip formatter
      chart.updateOptions(data);
      showNotification('蠟燭圖資料已成功載入');
    } else {
      console.error('找不到蠟燭圖實例');
    }
  }
  
  // 更新圓餅圖
  function updatePieChart(data) {
    const chart = ApexCharts.getChartByID('pieChart');
    if (chart) {
      // 移除所有 formatter 函數以避免錯誤
      removeAllFormatters(data);
      console.log('已移除所有圓餅圖 formatter 函數');
      
      // 確保圖表類型設置為pie
      if (!data.chart) data.chart = {};
      data.chart.type = 'pie';
      
      // 更新圖表
      chart.updateOptions(data);
      showNotification('圓餅圖資料已成功載入');
    } else {
      console.error('找不到圓餅圖實例，嘗試初始化新圖表');
      // 若找不到圖表實例，則嘗試重新初始化
      if (window.initPieChart) {
        window.initPieChart(data);
        showNotification('已初始化新的圓餅圖');
      } else {
        console.error('無法初始化圓餅圖：找不到 initPieChart 函數');
        showNotification('無法初始化圓餅圖', 'error');
      }
    }
  }
  
  // 更新環形圖
  function updateDonutChart(data) {
    const chart = ApexCharts.getChartByID('donutChart');
    if (chart) {
      // 移除所有 formatter 函數以避免錯誤
      removeAllFormatters(data);
      console.log('已移除所有環形圖 formatter 函數');
      
      // 確保圖表類型設置為donut
      if (!data.chart) data.chart = {};
      data.chart.type = 'donut';
      
      // 更新圖表
      chart.updateOptions(data);
      showNotification('環形圖資料已成功載入');
    } else {
      console.error('找不到環形圖實例');
    }
  }
  
  // 更新雷達圖
  function updateRadarChart(data) {
    const chart = ApexCharts.getChartByID('radarChart');
    if (chart) {
      // 移除所有 formatter 函數以避免錯誤
      removeAllFormatters(data);
      console.log('已移除所有雷達圖 formatter 函數');
      
      // 確保圖表類型設置為radar
      if (!data.chart) data.chart = {};
      data.chart.type = 'radar';
      
      // 更新圖表
      chart.updateOptions(data);
      showNotification('雷達圖資料已成功載入');
    } else {
      console.error('找不到雷達圖實例');
    }
  }
  
  // 更新極區域圖
  function updatePolarAreaChart(data) {
    const chart = ApexCharts.getChartByID('polarAreaChart');
    if (chart) {
      // 移除所有 formatter 函數以避免錯誤
      removeAllFormatters(data);
      console.log('已移除所有極區域圖 formatter 函數');
      
      // 確保圖表類型設置為polarArea
      if (!data.chart) data.chart = {};
      data.chart.type = 'polarArea';
      
      // 更新圖表
      chart.updateOptions(data);
      showNotification('極區域圖資料已成功載入');
    } else {
      console.error('找不到極區域圖實例，嘗試初始化新圖表');
      // 若找不到圖表實例，則嘗試重新初始化
      if (window.initPolarAreaChart) {
        window.initPolarAreaChart(data);
        showNotification('已初始化新的極區域圖');
      } else {
        console.error('無法初始化極區域圖：找不到 initPolarAreaChart 函數');
        showNotification('無法初始化極區域圖', 'error');
      }
    }
  }
  
  // 顯示通知
  function showNotification(message, type = 'success') {
    // 檢查是否已存在通知元素
    let notification = document.getElementById('chart-notification');
    
    if (!notification) {
      // 創建通知元素
      notification = document.createElement('div');
      notification.id = 'chart-notification';
      notification.className = 'fixed bottom-4 right-4 px-4 py-2 rounded-lg shadow-lg z-50 transition-opacity duration-300';
      document.body.appendChild(notification);
    }
    
    // 設置通知樣式
    if (type === 'success') {
      notification.className = 'fixed bottom-4 right-4 px-4 py-2 rounded-lg shadow-lg z-50 transition-opacity duration-300 bg-green-500 text-white';
    } else if (type === 'error') {
      notification.className = 'fixed bottom-4 right-4 px-4 py-2 rounded-lg shadow-lg z-50 transition-opacity duration-300 bg-red-500 text-white';
    } else if (type === 'warning') {
      notification.className = 'fixed bottom-4 right-4 px-4 py-2 rounded-lg shadow-lg z-50 transition-opacity duration-300 bg-yellow-500 text-white';
    } else if (type === 'info') {
      notification.className = 'fixed bottom-4 right-4 px-4 py-2 rounded-lg shadow-lg z-50 transition-opacity duration-300 bg-blue-500 text-white';
    }
    
    // 設置通知內容
    notification.textContent = message;
    
    // 顯示通知
    notification.style.opacity = 1;
    
    // 3秒後隱藏通知
    setTimeout(() => {
      notification.style.opacity = 0;
      
      // 完全淡出後移除元素
      setTimeout(() => {
        if (notification && notification.parentNode) {
          notification.parentNode.removeChild(notification);
        }
      }, 300);
    }, 3000);
  }

  // 檢測並啟用適當的圖表插件
  function enableChartPlugins() {
    console.log('啟用圖表插件，當前圖表類型:', chartType);
    
    // 更新圖表工具欄選項
    document.dispatchEvent(new CustomEvent('chart-type-changed', { 
      detail: { chartType }
    }));
  }
  
  // 初始化圖表插件
  enableChartPlugins();
});
