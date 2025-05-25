/**
 * 統一圖表錯誤恢復工具
 * 為所有圖表提供統一的錯誤恢復機制
 * 當發現圖表渲染失敗時，自動嘗試不同的恢復策略
 */

(function() {
  console.log('統一圖表錯誤恢復工具已載入');
  
  // 恢復策略對象
  const ChartRecoveryStrategies = {
    // 重新嘗試加載資料
    retryDataLoad: function(chartType, chartContainer) {
      console.log(`正在嘗試重新加載${chartType}圖表資料...`);
      
      // 重新加載對應的圖表資料
      const loadFuncName = `load${chartType.charAt(0).toUpperCase() + chartType.slice(1)}Data`;
      if (typeof window[loadFuncName] === 'function') {
        window[loadFuncName]();
        return true;
      }
      
      return false;
    },
    
    // 使用本地硬編碼資料
    useHardcodedData: function(chartType, chartContainer) {
      console.log(`正在使用預設硬編碼數據渲染${chartType}圖表...`);
      
      // 嘗試從增強錯誤處理器獲取預設資料
      if (window.chartErrorHandlerEnhanced && typeof window.chartErrorHandlerEnhanced.getDefaultChartData === 'function') {
        const defaultData = window.chartErrorHandlerEnhanced.getDefaultChartData(chartType);
        
        // 使用處理函數來渲染圖表
        const handlerFuncName = `handle${chartType.charAt(0).toUpperCase() + chartType.slice(1)}Chart`;
        if (typeof window[handlerFuncName] === 'function') {
          window[handlerFuncName](defaultData);
          return true;
        }
      }
      
      return false;
    },
    
    // 重新初始化圖表
    reinitializeChart: function(chartType, chartContainer) {
      console.log(`正在重新初始化${chartType}圖表...`);
      
      // 呼叫初始化函數
      const initFuncName = `init${chartType.charAt(0).toUpperCase() + chartType.slice(1)}Chart`;
      if (typeof window[initFuncName] === 'function') {
        window[initFuncName]();
        return true;
      }
      
      return false;
    },
    
    // 修復常見JSON格式問題
    fixJsonFormatting: function(chartType, response) {
      console.log(`嘗試修復${chartType}圖表的JSON格式...`);
      
      if (window.chartErrorHandlerEnhanced && typeof window.chartErrorHandlerEnhanced.fixJsonFormatting === 'function') {
        try {
          const fixedJson = window.chartErrorHandlerEnhanced.fixJsonFormatting(response);
          return fixedJson;
        } catch (error) {
          console.error(`修復JSON格式失敗:`, error);
        }
      }
      
      return null;
    },
    
    // 顯示友好的錯誤訊息
    showFriendlyError: function(chartType, chartContainer, error) {
      console.log(`為${chartType}圖表顯示友好的錯誤訊息...`);
      
      // 檢查是否有增強型錯誤處理程序
      if (window.chartErrorHandlerEnhanced && typeof window.chartErrorHandlerEnhanced.showError === 'function') {
        window.chartErrorHandlerEnhanced.showError(chartContainer.id, `${chartType}圖表無法渲染: ${error.message || '未知錯誤'}`);
        return true;
      } else if (window.chartErrorHandler && typeof window.chartErrorHandler.showError === 'function') {
        window.chartErrorHandler.showError(chartContainer.id, `${chartType}圖表無法渲染: ${error.message || '未知錯誤'}`);
        return true;
      } else {
        // 手動建立錯誤消息
        chartContainer.innerHTML = `
          <div class="flex flex-col items-center justify-center h-full p-6 bg-red-50 border border-red-200 rounded-lg">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-red-500 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <p class="text-base text-red-700 font-medium mb-2">無法渲染${chartType}圖表</p>
            <p class="text-sm text-red-600 mb-4">${error.message || '未知錯誤'}</p>
            <button class="btn btn-sm btn-outline btn-error" onclick="location.reload()">重新整理頁面</button>
            <p class="text-xs text-gray-500 mt-4">如果問題持續存在，請聯絡技術支持</p>
          </div>
        `;
        return true;
      }
    }
  };
  
  // 主要恢復函數
  function recoverChartRendering(chartType, chartContainer, error) {
    console.log(`開始嘗試恢復${chartType}圖表渲染...`, error);
    
    // 執行恢復策略
    const strategies = [
      ChartRecoveryStrategies.retryDataLoad,
      ChartRecoveryStrategies.useHardcodedData,
      ChartRecoveryStrategies.reinitializeChart
    ];
    
    // 逐一嘗試每個恢復策略
    for (let strategy of strategies) {
      const succeeded = strategy(chartType, chartContainer);
      if (succeeded) {
        console.log(`成功使用恢復策略修復${chartType}圖表!`);
        
        // 驗證恢復是否有效
        setTimeout(() => {
          if (window.ChartVerification && typeof window.ChartVerification.verifyChart === 'function') {
            const verified = window.ChartVerification.verifyChart(chartType, chartContainer.id);
            if (!verified) {
              console.warn(`${chartType}圖表恢復驗證失敗，嘗試下一個策略...`);
            } else {
              console.log(`${chartType}圖表恢復驗證成功!`);
              return true;
            }
          }
        }, 500);
      }
    }
    
    // 如果所有恢復策略都失敗，顯示友好的錯誤訊息
    ChartRecoveryStrategies.showFriendlyError(chartType, chartContainer, error);
    return false;
  }
  
  // 將恢復工具暴露到全局範圍
  window.ChartRecoveryTool = {
    recover: recoverChartRendering,
    fixJsonFormatting: ChartRecoveryStrategies.fixJsonFormatting
  };
  
  console.log('統一圖表錯誤恢復工具準備就緒');
})();
