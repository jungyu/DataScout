/**
 * 修復圓餅圖的相關問題
 * 此文件解決圓餅圖找不到統一資料載入器的問題
 */

(function() {
  console.log('圓餅圖修復工具已啟動');

  // 設置全局的 removeAllFormatters 函數
  window.removeAllFormatters = function(data) {
    if (!data) return data;
    
    // 移除yaxis中的formatter
    if (data.yaxis) {
      // 如果是單一y軸
      if (data.yaxis.labels && data.yaxis.labels.formatter) {
        data.yaxis.labels.formatter = null;
      }
      
      // 如果是多個y軸
      if (Array.isArray(data.yaxis)) {
        data.yaxis.forEach(axis => {
          if (axis.labels && axis.labels.formatter) {
            axis.labels.formatter = null;
          }
        });
      }
    }
    
    // 移除tooltip中的formatter
    if (data.tooltip) {
      if (data.tooltip.y && data.tooltip.y.formatter) {
        data.tooltip.y.formatter = null;
      }
      
      if (data.tooltip.x && data.tooltip.x.formatter) {
        data.tooltip.x.formatter = null;
      }
    }
    
    // 移除dataLabels中的formatter
    if (data.dataLabels && data.dataLabels.formatter) {
      data.dataLabels.formatter = null;
    }
    
    // 移除legend中的formatter
    if (data.legend && data.legend.formatter) {
      data.legend.formatter = null;
    }
    
    return data;
  };

  // 修改loadPieData函數
  const originalLoadPieData = window.loadPieData;
  window.loadPieData = function(dataType = 'default') {
    console.log(`修復後的載入餅圖資料 (類型: ${dataType})`);
    
    let fileName;
    switch (dataType.toLowerCase()) {
      case 'marketshare':
      case 'default':
        fileName = 'apexcharts_pie_market_share.json';
        break;
      case 'saleschannels':
        fileName = 'apexcharts_pie_sales_channels.json';
        break;
      case 'teamcontribution':
        fileName = 'apexcharts_pie_team.json';
        break;
      default:
        console.warn(`未知的餅圖資料類型: ${dataType}, 將使用預設資料。`);
        fileName = 'apexcharts_pie_market_share.json';
    }
    
    const dataUrl = `assets/examples/${fileName}`;
    const chartContainerId = 'pieChart';
    
    console.log(`嘗試載入餅圖資料: ${dataUrl}`);
    
    // 直接使用fetch加載數據並處理
    fetch(dataUrl)
      .then(response => {
        if (!response.ok) throw new Error(`無法載入檔案 ${fileName} (狀態碼: ${response.status})`);
        return response.json();
      })
      .then(data => {
        console.log('餅圖資料載入成功');
        
        // 移除所有的 formatter 函數避免錯誤
        data = window.removeAllFormatters(data);
        console.log('已移除餅圖資料中的 formatter 函數');
        
        // 確保圖表類型為 pie
        if (!data.chart) data.chart = {};
        data.chart.type = 'pie';
        
        // 處理餅圖數據 - 使用修復版本
        if (window.handlePieChartFixed) {
          window.handlePieChartFixed(data);
        } else {
          window.handlePieChart(data);
        }
      })
      .catch(error => {
        console.error(`載入餅圖資料時發生錯誤: ${fileName}`, error);
        if (window.chartErrorHandler) {
          window.chartErrorHandler.showError(chartContainerId, `載入餅圖資料 ${fileName} 失敗: ${error.message}`);
        }
        
        // 使用預設資料
        const defaultPieData = {
          series: [44, 55, 13, 43, 22],
          chart: { type: 'pie', height: 350 },
          labels: ['產品A', '產品B', '產品C', '產品D', '產品E'],
          title: { text: '預設餅圖資料', align: 'center' },
          responsive: [{ breakpoint: 480, options: { chart: { width: 300 }, legend: { position: 'bottom' }}}]
        };
        console.log('由於載入失敗，使用預設餅圖資料');
        if (window.handlePieChartFixed) {
          window.handlePieChartFixed(defaultPieData);
        } else {
          window.handlePieChart(defaultPieData);
        }
      });
  };

  // 添加到圖表類型處理中
  if (window.handleChart) {
    const originalHandleChart = window.handleChart;
    window.handleChart = function(data, chartType) {
      // 檢查是否為圓餅圖
      if (chartType === 'pie') {
        console.log('使用修復後的圓餅圖處理邏輯');
        
        // 移除所有 formatter
        data = window.removeAllFormatters(data);
        
        // 確保圖表類型為 pie
        if (!data.chart) data.chart = {};
        data.chart.type = 'pie';
      }
      
      return originalHandleChart(data, chartType);
    };
  }
  
  console.log('圓餅圖修復工具初始化完成');
})();
