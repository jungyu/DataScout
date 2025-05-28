/**
 * 柱狀圖特殊處理函數
 * 解決柱狀圖渲染問題
 */

// 特別處理柱狀圖渲染
window.handleColumnChart = function(data) {
  console.log('開始特殊處理柱狀圖的渲染', data);
  
  // 在處理數據之前先進行深拷貝
  data = JSON.parse(JSON.stringify(data));
  
  // 立即設置圖表類型為 bar（ApexCharts 中的 column 實際上是 bar 的一種）
  if (!data.chart) data.chart = {};
  data.chart.type = 'bar';
  
  // 檢查圖表容器
  const chartContainer = document.getElementById('columnChart');
  if (!chartContainer) {
    console.error('找不到柱狀圖容器元素 #columnChart');
    console.log('document.getElementById(\'columnChart\') 返回 null');
    if (window.showNotification) {
      window.showNotification('找不到柱狀圖容器，無法載入資料', 'error');
    }
    return;
  }
  
  // 清除現有的圖表實例
  if (window.ApexCharts) {
    const existingChart = ApexCharts.getChartByID('columnChart');
    if (existingChart) {
      console.log('清除既有柱狀圖實例');
      existingChart.destroy();
    }
    
    // 也清除可能的實例緩存
    if (window.chartInstances && window.chartInstances['columnChart']) {
      delete window.chartInstances['columnChart'];
    }
  }
  
  // 確保資料結構正確，特別是 series 屬性
  if (!data || !Array.isArray(data.series)) {
    console.error('柱狀圖資料無效或 series 屬性格式不正確', data);
    if (window.showNotification) {
      window.showNotification('柱狀圖資料格式無效，無法載入', 'error');
    }
    // 嘗試清空圖表容器或顯示錯誤訊息
    if (chartContainer) {
      chartContainer.innerHTML = `
        <div class="flex flex-col items-center justify-center h-full">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-error mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <p class="text-base text-error font-medium">圖表資料格式不正確</p>
          <button class="btn btn-sm btn-outline btn-error mt-4" onclick="location.reload()">重新整理頁面</button>
        </div>
      `;
    }
    return;
  }
  
  // 進一步檢查 series 陣列中的每個數據對象
  for (let i = 0; i < data.series.length; i++) {
    const seriesItem = data.series[i];
    if (!seriesItem || !Array.isArray(seriesItem.data)) {
      console.error(`柱狀圖 series[${i}] 的 data 屬性無效或不是陣列`, seriesItem);
      if (window.showNotification) {
        window.showNotification(`柱狀圖資料中 series[${i}] 的 data 屬性格式不正確`, 'error');
      }
      // 在圖表容器中顯示更詳細的錯誤訊息
      if (chartContainer) {
        chartContainer.innerHTML = `
          <div class="flex flex-col items-center justify-center h-full">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-error mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <p class="text-base text-error font-medium">圖表資料錯誤: series[${i}] 的 data 屬性格式不正確</p>
            <button class="btn btn-sm btn-outline btn-error mt-4" onclick="location.reload()">重新整理頁面</button>
          </div>
        `;
      }
      return;
    }
  }
  
  // 確保 plotOptions 配置正確
  if (!data.plotOptions) data.plotOptions = {};
  if (!data.plotOptions.bar) data.plotOptions.bar = {};
  data.plotOptions.bar.horizontal = false;
  data.plotOptions.bar.columnWidth = '55%';
  data.plotOptions.bar.endingShape = 'rounded';
  
  // 添加額外的數據處理配置
  data.chart.animations = {
    enabled: true,
    dynamicAnimation: {
      enabled: true
    }
  };
  
  // 確保數據標籤配置完整
  if (!data.dataLabels) {
    data.dataLabels = {
      enabled: false
    };
  }
  
  // 確保 stroke 配置完整
  if (!data.stroke) {
    data.stroke = {
      show: true,
      width: 2,
      colors: ['transparent']
    };
  }
  
  // 確保 fill 配置完整
  if (!data.fill) {
    data.fill = {
      opacity: 1
    };
  }
  
  // 確保 series 數據格式正確
  if (Array.isArray(data.series)) {
    data.series = data.series.map(series => {
      if (typeof series === 'object' && series !== null) {
        return {
          name: series.name || '',
          data: Array.isArray(series.data) ? series.data : []
        };
      }
      return { name: '', data: [] };
    });
  }
  
  // 添加額外日誌和檢查關鍵配置
  console.log('傳遞給 ApexCharts 的數據:', data);
  console.log('傳遞給 ApexCharts 的完整數據 (JSON):', JSON.stringify(data, null, 2));
  if (!data.yaxis) {
    console.warn('警告: 柱狀圖數據缺少 yaxis 配置');
  }
  if (!data.plotOptions || !data.plotOptions.bar) {
     console.warn('警告: 柱狀圖數據缺少 plotOptions 或 plotOptions.bar 配置');
  }
  
  try {
    console.log('初始化柱狀圖', data);
    const chart = new ApexCharts(chartContainer, data);
    chart.render();
    console.log('柱狀圖渲染完成');
    
    // 儲存實例以便後續操作
    if (!window.chartInstances) window.chartInstances = {};
    window.chartInstances['columnChart'] = chart;
    
    if (window.showNotification) {
      window.showNotification('柱狀圖載入成功', 'success');
    }
    
    // 添加延遲日誌，檢查後續是否有其他操作
    setTimeout(() => {
      console.log('柱狀圖渲染後延遲檢查，圖表狀態:', chart);
      // 這裡可以添加更多對圖表實例狀態的檢查
    }, 1000); // 延遲1秒
    
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
    console.error('渲染柱狀圖時發生錯誤:', error);
    
    if (window.showNotification) {
      window.showNotification(`柱狀圖渲染失敗: ${error.message}`, 'error');
    }
    
    // 顯示錯誤在圖表容器中
    chartContainer.innerHTML = `
      <div class="flex flex-col items-center justify-center h-full">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-error mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <p class="text-base text-error font-medium">渲染柱狀圖失敗: ${error.message}</p>
        <button class="btn btn-sm btn-outline btn-error mt-4" onclick="location.reload()">重新整理頁面</button>
      </div>
    `;
  }
};

// 在頁面載入完成後執行
document.addEventListener('DOMContentLoaded', function() {
  // 檢查是否在柱狀圖頁面
  if (window.location.pathname.toLowerCase().includes('column.html')) {
    console.log('檢測到柱狀圖頁面，啟用柱狀圖專用處理');
    
    // 監聽組件載入完成事件
    document.addEventListener('component-loaded', function(e) {
      if (e.detail && e.detail.componentPath && e.detail.componentPath.includes('ColumnChartContent.html')) {
        console.log('柱狀圖組件已載入，初始化柱狀圖專用處理');
        setTimeout(initColumnChartHandler, 500);
      }
    });
  }
});

// 初始化柱狀圖專用處理
function initColumnChartHandler() {
  console.log('初始化柱狀圖專用處理');
  
  // 檢查圖表容器是否已經有內容，避免重複初始化
  const chartContainer = document.getElementById('columnChart');
  if (chartContainer && chartContainer.innerHTML.trim() !== '') {
    console.log('圖表容器已有內容，跳過初始化');
    return;
  }
  
  // 獲取當前載入的範例資料元素
  const activeExample = document.querySelector('.chart-data-item.active');
  if (!activeExample) {
    console.log('找不到活躍的範例資料，嘗試載入預設柱狀圖範例');
    loadDefaultColumnExample();
    return;
  }
  
  // 獲取範例文件路徑
  const filePath = activeExample.dataset.file;
  if (!filePath) {
    console.error('範例資料缺少檔案路徑');
    loadDefaultColumnExample();
    return;
  }
  
  // 加載並渲染圖表
  console.log(`嘗試載入柱狀圖資料: ${filePath}`);
  fetch(`assets/examples/${filePath}`)
    .then(response => {
      if (!response.ok) throw new Error(`無法載入檔案 ${filePath}`);
      return response.json();
    })
    .then(data => {
      window.handleColumnChart(data);
    })
    .catch(error => {
      console.error('載入柱狀圖資料時發生錯誤:', error);
      loadDefaultColumnExample();
    });
}

// 載入預設柱狀圖範例
function loadDefaultColumnExample() {
  console.log('載入預設柱狀圖範例');
  fetch('assets/examples/apexcharts_column_finance.json')
    .then(response => {
      if (!response.ok) {
        // 嘗試另一個資料檔案
        return fetch('assets/examples/apexcharts_bar_budget.json');
      }
      return response.json();
    })
    .then(data => {
      // 強制類型為column
      if (data && data.chart) {
        data.chart.type = 'column';
      } else if (data) {
        data.chart = { type: 'column' };
      }
      
      window.handleColumnChart(data);
    })
    .catch(error => {
      console.error('載入預設柱狀圖資料時發生錯誤:', error);
      const chartContainer = document.getElementById('columnChart');
      if (chartContainer) {
        chartContainer.innerHTML = `
          <div class="flex flex-col items-center justify-center h-full">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-error mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <p class="text-base text-error font-medium">無法載入柱狀圖資料</p>
            <button class="btn btn-sm btn-outline btn-error mt-4" onclick="location.reload()">重新整理頁面</button>
          </div>
        `;
      }
    });
}
