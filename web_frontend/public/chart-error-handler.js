/**
 * 圖表通用錯誤處理與修復工具
 * 提供統一的圖表錯誤處理與響應機制
 */

(function() {
  console.log('圖表通用錯誤處理工具已載入');

  // 將功能添加到全局window對象
  window.chartErrorHandler = {
    // 顯示錯誤訊息
    showError: function(elementId, errorMsg, errorType = 'error') {
      console.error(`圖表錯誤 (${elementId}): ${errorMsg}`);
      
      const container = document.getElementById(elementId);
      if (!container) {
        console.error(`找不到圖表容器: #${elementId}`);
        return;
      }
      
      // 根據錯誤類型設置顏色
      const colorClass = errorType === 'warning' ? 'text-warning' : 'text-error';
      
      // 顯示錯誤訊息
      container.innerHTML = `
        <div class="flex flex-col items-center justify-center h-full p-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 ${colorClass} mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <p class="text-base ${colorClass} font-medium text-center mb-2">${errorMsg}</p>
          <button class="btn btn-sm btn-outline btn-primary mt-4" onclick="location.reload()">重新整理頁面</button>
        </div>
      `;
      
      // 如果存在通知功能，也發送通知
      if (window.showNotification) {
        window.showNotification(errorMsg, errorType);
      }
    },
    
    // 清理圖表實例
    cleanupChart: function(chartId) {
      try {
        // 嘗試使用ApexCharts API清除
        if (window.ApexCharts) {
          const chart = ApexCharts.getChartByID(chartId);
          if (chart) {
            console.log(`清除圖表實例: ${chartId}`);
            chart.destroy();
          }
        }
        
        // 清除可能的實例緩存
        if (window.chartInstances && window.chartInstances[chartId]) {
          delete window.chartInstances[chartId];
        }
        
        return true;
      } catch (error) {
        console.error(`清除圖表實例時發生錯誤: ${error.message}`);
        return false;
      }
    },
    
    // 重試載入圖表資料
    retryLoadData: function(chartType, alternativeFiles, elementId, handlerFunction) {
      console.log(`嘗試載入備用的${chartType}圖資料`);
      
      // 如果沒有提供備用文件，使用預設值
      if (!alternativeFiles || alternativeFiles.length === 0) {
        alternativeFiles = [`apexcharts_${chartType}_default.json`];
      }
      
      // 依序嘗試每個備用文件
      const tryNextFile = (index = 0) => {
        if (index >= alternativeFiles.length) {
          this.showError(elementId, `無法載入${chartType}圖資料，已嘗試所有備用文件`);
          return;
        }
        
        const fileName = alternativeFiles[index];
        fetch(`assets/examples/${fileName}`)
          .then(response => {
            if (!response.ok) {
              throw new Error(`無法載入檔案 ${fileName}`);
            }
            return response.json();
          })
          .then(data => {
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
              this.showError(elementId, `找不到${chartType}圖的處理函數`);
            }
          })
          .catch(error => {
            console.warn(`載入備用文件 ${fileName} 失敗: ${error.message}，嘗試下一個`);
            tryNextFile(index + 1);
          });
      };
      
      // 開始嘗試第一個備用文件
      tryNextFile();
    },
    
    // 修復JSON格式錯誤
    fixJsonFormatting: function(jsonText) {
      if (!jsonText) return this.getDefaultChartData();
      
      try {
        // 首先嘗試原始解析
        return JSON.parse(jsonText);
      } catch (error) {
        console.warn('JSON解析失敗，嘗試修復格式...', error);
        
        // 檢查是否為空文檔或不完整
        if (jsonText.trim() === '') {
          console.error('JSON文檔為空，無法修復');
          return this.getDefaultChartData();
        }
        
        // 嘗試增強修復
        let processed = jsonText;
        
        // 確保JSON有開始和結束符號
        if (!processed.trim().startsWith('{')) {
          processed = '{' + processed;
        }
        if (!processed.trim().endsWith('}')) {
          processed = processed + '}';
        }
        
        // 嘗試修復常見的JSON格式錯誤
        processed = processed.replace(/,\s*}/g, '}'); // 移除最後一個逗號
        processed = processed.replace(/,\s*\]/g, ']'); // 移除數組最後一個逗號
        
        // 使用已有的修復工具
        if (typeof handleFunctionStrings === 'function') {
          processed = handleFunctionStrings(processed);
          try {
            return JSON.parse(processed);
          } catch (innerError) {
            console.error('修復JSON後仍然無法解析', innerError);
          }
        }
        
        // 嚴重錯誤時返回默認數據
        console.error('找不到handleFunctionStrings函數或修復失敗，使用默認數據');
        return this.getDefaultChartData();
      }
    },
    
    // 獲取預設圖表數據
    getDefaultChartData: function() {
      return {
        chart: {
          type: 'line',
          height: 350,
          toolbar: {
            show: true
          }
        },
        title: {
          text: '預設圖表數據',
          align: 'center',
          style: {
            fontSize: '16px',
            color: '#263238'
          }
        },
        series: [{
          name: '範例數據',
          data: [10, 41, 35, 51, 49, 62, 69, 91, 148]
        }],
        xaxis: {
          categories: ['一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月'],
          labels: {
            style: {
              colors: '#8e8da4'
            }
          }
        },
        yaxis: {
          labels: {
            style: {
              colors: '#8e8da4'
            }
          }
        },
        colors: ['#008FFB'],
        stroke: {
          curve: 'smooth',
          width: 2
        },
        grid: {
          borderColor: '#e7e7e7'
        },
        legend: {
          labels: {
            colors: '#8e8da4'
          }
        }
      };
    }
  };

  // 將錯誤處理器添加到每個圖表處理函數
  document.addEventListener('DOMContentLoaded', function() {
    // 更新或創建通知函數
    if (!window.showNotification) {
      window.showNotification = function(message, type = 'info') {
        console.log(`通知: [${type}] ${message}`);
        
        // 檢查是否已有通知容器
        let notificationContainer = document.getElementById('notification-container');
        if (!notificationContainer) {
          // 創建通知容器
          notificationContainer = document.createElement('div');
          notificationContainer.id = 'notification-container';
          notificationContainer.className = 'fixed bottom-4 right-4 z-50 flex flex-col gap-2';
          document.body.appendChild(notificationContainer);
        }
        
        // 創建通知元素
        const notification = document.createElement('div');
        notification.className = `alert ${type === 'error' ? 'alert-error' : type === 'success' ? 'alert-success' : 'alert-info'} shadow-lg max-w-sm`;
        notification.innerHTML = `
          <div>
            <span>${message}</span>
          </div>
        `;
        
        // 添加到容器
        notificationContainer.appendChild(notification);
        
        // 自動移除
        setTimeout(() => {
          notification.style.opacity = '0';
          notification.style.transform = 'translateX(100%)';
          setTimeout(() => {
            notificationContainer.removeChild(notification);
          }, 300);
        }, 3000);
      };
    }
  });
})();
