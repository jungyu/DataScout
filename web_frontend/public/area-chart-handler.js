/**
 * 面積圖特殊處理函數
 * 解決面積圖在動態載入時消失的問題
 */

// 特別處理面積圖渲染
window.handleAreaChart = function(data) {
  console.log('開始特殊處理面積圖的渲染', data);
  
  // 檢查圖表容器
  const chartContainer = document.getElementById('areaChart');
  if (!chartContainer) {
    console.error('找不到面積圖容器元素 #areaChart');
    if (window.showNotification) {
      window.showNotification('找不到面積圖容器，無法載入資料', 'error');
    }
    return;
  }
  
  // 清除現有的圖表實例
  if (window.ApexCharts) {
    const existingChart = ApexCharts.getChartByID('areaChart');
    if (existingChart) {
      console.log('清除既有面積圖實例');
      existingChart.destroy();
    }
    
    // 也清除可能的實例緩存
    if (window.chartInstances && window.chartInstances['areaChart']) {
      delete window.chartInstances['areaChart'];
    }
  }
  
  // 確保資料結構正確
  if (!data) {
    console.error('面積圖資料無效');
    if (window.showNotification) {
      window.showNotification('面積圖資料格式無效', 'error');
    }
    return;
  }
  
  // 確保圖表類型設置為area
  if (!data.chart) data.chart = {};
  data.chart.type = 'area';
  
  // 確保基本配置存在
  if (!data.dataLabels) data.dataLabels = { enabled: false };
  if (!data.stroke) data.stroke = { curve: 'smooth', width: 2 };
  
  try {
    console.log('初始化面積圖', data);
    const chart = new ApexCharts(chartContainer, data);
    chart.render();
    console.log('面積圖渲染完成');
    
    // 儲存實例以便後續操作
    if (!window.chartInstances) window.chartInstances = {};
    window.chartInstances['areaChart'] = chart;
    
    if (window.showNotification) {
      window.showNotification('面積圖載入成功', 'success');
    }
    
    // 修復尺寸問題
    setTimeout(function() {
      if (chart && typeof chart.updateOptions === 'function') {
        chart.updateOptions({
          chart: {
            redrawOnWindowResize: true
          }
        }, false, true);
      }
    }, 300);
  } catch (error) {
    console.error('渲染面積圖時發生錯誤:', error);
    
    if (window.showNotification) {
      window.showNotification(`面積圖渲染失敗: ${error.message}`, 'error');
    }
    
    // 顯示錯誤在圖表容器中
    chartContainer.innerHTML = `
      <div class="flex flex-col items-center justify-center h-full">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-error mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <p class="text-base text-error font-medium">渲染面積圖失敗: ${error.message}</p>
        <button class="btn btn-sm btn-outline btn-error mt-4" onclick="location.reload()">重新整理頁面</button>
      </div>
    `;
  }
};

// 初始化面積圖
window.initAreaChart = function() {
  console.log('初始化面積圖函數已被調用');
  
  // 檢查圖表容器
  const chartContainer = document.getElementById('areaChart');
  if (!chartContainer) {
    console.error('找不到面積圖容器 #areaChart');
    return;
  }
  
  // 從預設路徑載入資料
  window.loadAreaData();
};

// 載入面積圖資料
window.loadAreaData = function(dataType = 'default') {
  console.log(`載入面積圖資料 (類型: ${dataType})`);
  
  let fileName;
  switch (dataType.toLowerCase()) {
    case 'webstat':
      fileName = 'apexcharts_area_webstat.json';
      break;
    case 'traffic':
      fileName = 'apexcharts_area_traffic_flow.json';
      break;
    case 'server':
      fileName = 'apexcharts_area_server_monitor.json';
      break;
    case 'default':
    default:
      fileName = 'apexcharts_area_webstat.json';
  }
  
  // 檢查是否由統一資料載入器處理
  if (window.DataLoader && typeof window.DataLoader.loadChartData === 'function') {
    window.DataLoader.loadChartData('area', fileName)
      .then(data => {
        if (data) {
          window.handleAreaChart(data);
        } else {
          console.error('載入面積圖預設資料失敗 (經由統一資料載入器)');
        }
      })
      .catch(error => {
        console.error('載入面積圖預設資料時發生錯誤:', error);
      });
  } else {
    console.warn('找不到統一資料載入器，嘗試直接載入面積圖資料');
    
    // 直接載入資料的備用方法
    fetch(`assets/examples/${fileName}`)
      .then(response => {
        if (!response.ok) throw new Error(`無法載入檔案 ${fileName} (狀態碼: ${response.status})`);
        return response.text(); // 先取得文本再解析，以便處理JSON格式問題
      })
      .then(text => {
        // 嘗試解析JSON，處理可能的格式問題
        let data;
        
        try {
          // 首先嘗試透過JSON增強工具解析
          if (window.JSONEnhancer && typeof window.JSONEnhancer.parse === 'function') {
            data = window.JSONEnhancer.parse(text);
            console.log('使用JSON增強工具成功解析面積圖資料');
          } else {
            // 若沒有增強工具，使用標準解析
            data = JSON.parse(text);
          }
        } catch (e) {
          console.warn(`解析面積圖JSON時發生錯誤，嘗試修復: ${e.message}`);
          
          try {
            // 移除註釋並嘗試再次解析
            const processedText = text.replace(/\/\/.*$/gm, '').trim();
            data = JSON.parse(processedText);
          } catch (e2) {
            console.error(`即使移除註釋也無法解析JSON: ${e2.message}`);
            throw e2;
          }
        }
        
        // 處理JSON中的函數字串
        if (data && window.processJsonFunctions) {
          data = window.processJsonFunctions(data);
        }
        
        window.handleAreaChart(data);
      })
      .catch(error => {
        console.error('直接載入面積圖資料時發生錯誤:', error);
        if (window.chartErrorHandler) {
          window.chartErrorHandler.showError('areaChart', `載入面積圖預設資料失敗: ${error.message}`);
        }
      });
  }
};

// 在頁面載入完成後執行
document.addEventListener('DOMContentLoaded', function() {
  // 檢查是否在面積圖頁面
  if (window.location.pathname.toLowerCase().includes('area.html')) {
    console.log('檢測到面積圖頁面，啟用面積圖專用處理');
    
    // 監聽組件載入完成事件
    document.addEventListener('component-loaded', function(e) {
      if (e.detail && e.detail.componentPath && e.detail.componentPath.includes('AreaChartContent.html')) {
        console.log('面積圖組件已載入，初始化面積圖專用處理');
        setTimeout(initAreaChartHandler, 500);
      }
    });
  }
});

// 初始化面積圖專用處理
function initAreaChartHandler() {
  // 獲取當前載入的範例資料元素
  const activeExample = document.querySelector('.chart-data-item.active');
  if (!activeExample) {
    console.log('找不到活躍的範例資料，嘗試載入預設面積圖範例');
    loadDefaultAreaChartExample();
    return;
  }
  
  // 獲取範例文件路徑
  const filePath = activeExample.dataset.file;
  if (!filePath) {
    console.error('範例資料缺少檔案路徑');
    loadDefaultAreaChartExample();
    return;
  }
  
  // 加載並渲染圖表
  console.log(`嘗試載入面積圖資料: ${filePath}`);
  fetch(`assets/examples/${filePath}`)
    .then(response => {
      if (!response.ok) throw new Error(`無法載入檔案 ${filePath}`);
      return response.json();
    })
    .then(data => {
      window.handleAreaChart(data);
    })
    .catch(error => {
      console.error('載入面積圖資料時發生錯誤:', error);
      loadDefaultAreaChartExample();
    });
}

// 載入預設面積圖範例
function loadDefaultAreaChartExample() {
  console.log('載入預設面積圖範例');
  fetch('assets/examples/apexcharts_area_webstat.json')
    .then(response => {
      if (!response.ok) {
        // 嘗試另一個資料檔案
        return fetch('assets/examples/apexcharts_area_traffic_flow.json');
      }
      return response.json();
    })
    .then(data => {
      window.handleAreaChart(data);
    })
    .catch(error => {
      console.error('載入預設面積圖資料時發生錯誤:', error);
      const chartContainer = document.getElementById('areaChart');
      if (chartContainer) {
        chartContainer.innerHTML = `
          <div class="flex flex-col items-center justify-center h-full">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-error mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <p class="text-base text-error font-medium">無法載入面積圖資料</p>
            <button class="btn btn-sm btn-outline btn-error mt-4" onclick="location.reload()">重新整理頁面</button>
          </div>
        `;
      }
    });
}
