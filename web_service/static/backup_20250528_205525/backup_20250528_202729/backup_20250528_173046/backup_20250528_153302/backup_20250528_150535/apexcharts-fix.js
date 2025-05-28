/**
 * ApexCharts 修復腳本
 * 解決 "TypeError: C is not a function" 錯誤
 */

(function() {
  console.log('ApexCharts 修復腳本已加載');

  // 等待 ApexCharts 庫完全加載
  function waitForApexCharts() {
    return new Promise((resolve, reject) => {
      let attempts = 0;
      const maxAttempts = 50;
      
      const checkApexCharts = () => {
        attempts++;
        
        if (window.ApexCharts && typeof window.ApexCharts === 'function') {
          console.log('ApexCharts 庫已成功加載');
          resolve(window.ApexCharts);
        } else if (attempts >= maxAttempts) {
          console.error('ApexCharts 庫加載失敗，已達到最大嘗試次數');
          reject(new Error('ApexCharts 庫加載超時'));
        } else {
          console.log(`正在等待 ApexCharts 庫加載... (嘗試 ${attempts}/${maxAttempts})`);
          setTimeout(checkApexCharts, 100);
        }
      };
      
      checkApexCharts();
    });
  }

  // 安全的圖表初始化函數
  function safeInitChart(container, options) {
    return waitForApexCharts().then((ApexCharts) => {
      try {
        console.log('使用安全方法初始化圖表', { container, options });
        
        // 確保容器存在
        if (!container) {
          throw new Error('圖表容器不存在');
        }
        
        // 驗證 ApexCharts 構造函數
        if (typeof ApexCharts !== 'function') {
          throw new Error('ApexCharts 不是有效的構造函數');
        }
        
        // 清理選項中可能導致問題的屬性
        const cleanOptions = JSON.parse(JSON.stringify(options));
        
        // 處理字串形式的formatter函數
        function processFormatters(obj) {
          if (typeof obj !== 'object' || obj === null) return;
          
          for (const key in obj) {
            if (obj.hasOwnProperty(key)) {
              if (key === 'formatter' && typeof obj[key] === 'string') {
                // 使用簡單的預設formatter替代字串形式的函數
                if (obj[key].includes('%')) {
                  obj[key] = function(val) { return val + '%'; };
                } else {
                  delete obj[key]; // 移除可能有問題的formatter
                }
              } else if (typeof obj[key] === 'object') {
                processFormatters(obj[key]);
              }
            }
          }
        }
        
        processFormatters(cleanOptions);
        
        // 確保基本的圖表配置
        if (!cleanOptions.chart) {
          cleanOptions.chart = {};
        }
        
        if (!cleanOptions.chart.type) {
          cleanOptions.chart.type = 'pie';
        }
        
        // 創建圖表實例
        const chart = new ApexCharts(container, cleanOptions);
        
        console.log('圖表實例創建成功');
        return chart;
        
      } catch (error) {
        console.error('創建圖表時發生錯誤:', error);
        throw error;
      }
    });
  }

  // 修復後的 handlePieChart 函數
  window.handlePieChartFixed = function(data) {
    console.log('使用修復版本處理餅圖渲染', data);
    
    const chartContainerId = 'pieChart';
    const chartContainer = document.getElementById(chartContainerId);
    
    if (!chartContainer) {
      console.error(`找不到餅圖容器元素 #${chartContainerId}`);
      if (window.showNotification) {
        window.showNotification('找不到餅圖容器，無法載入資料', 'error');
      }
      return false;
    }
    
    // 清除現有圖表
    if (window.chartInstances && window.chartInstances[chartContainerId]) {
      try {
        window.chartInstances[chartContainerId].destroy();
        delete window.chartInstances[chartContainerId];
        console.log('已清除現有餅圖實例');
      } catch (error) {
        console.warn('清除現有圖表時出現警告:', error);
      }
    }
    
    // 清空容器
    chartContainer.innerHTML = '';
    
    // 確保數據格式正確
    if (!data || typeof data !== 'object') {
      console.error('餅圖數據無效');
      return false;
    }
    
    // 設置預設值
    if (!data.chart) data.chart = {};
    data.chart.type = 'pie';
    
    if (!data.chart.height) {
      data.chart.height = 350;
    }
    
    // 確保 series 和 labels 存在
    if (!Array.isArray(data.series)) {
      console.warn('餅圖 series 數據無效，使用預設值');
      data.series = [44, 55, 13, 43, 22];
    }
    
    if (!Array.isArray(data.labels)) {
      console.warn('餅圖 labels 數據無效，使用預設值');
      data.labels = ['產品A', '產品B', '產品C', '產品D', '產品E'];
    }
    
    // 使用安全的初始化方法
    safeInitChart(chartContainer, data)
      .then(chart => {
        return chart.render();
      })
      .then(chart => {
        console.log('餅圖渲染成功');
        
        // 保存圖表實例
        if (!window.chartInstances) {
          window.chartInstances = {};
        }
        window.chartInstances[chartContainerId] = chart;
        
        if (window.showNotification) {
          window.showNotification('餅圖載入成功', 'success');
        }
      })
      .catch(error => {
        console.error('餅圖渲染失敗:', error);
        
        if (window.showNotification) {
          window.showNotification(`餅圖載入失敗: ${error.message}`, 'error');
        }
        
        // 顯示錯誤信息
        chartContainer.innerHTML = `
          <div class="flex items-center justify-center h-64 bg-gray-100 rounded-lg">
            <div class="text-center">
              <div class="text-red-500 text-xl mb-2">⚠️</div>
              <div class="text-gray-600">圖表載入失敗</div>
              <div class="text-sm text-gray-500 mt-1">${error.message}</div>
            </div>
          </div>
        `;
      });
  };

  // 替換原有的 handlePieChart 函數
  if (window.handlePieChart) {
    console.log('替換原有的 handlePieChart 函數');
    window.handlePieChart = window.handlePieChartFixed;
  }

  // 在 DOM 加載完成後設置函數
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
      window.handlePieChart = window.handlePieChartFixed;
    });
  } else {
    window.handlePieChart = window.handlePieChartFixed;
  }

  console.log('ApexCharts 修復腳本初始化完成');
})();
