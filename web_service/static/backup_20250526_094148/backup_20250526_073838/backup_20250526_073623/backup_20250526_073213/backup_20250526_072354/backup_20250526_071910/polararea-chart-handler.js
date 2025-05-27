/**
 * 極區域圖專用處理函數
 * 解決極區域圖渲染問題
 */

(function() {
  console.log('極區域圖專用處理函數已啟動');
  
  // 全局保存極區域圖實例
  window.polarAreaChartInstances = {};
  
  // 在頁面載入完成後執行
  document.addEventListener('DOMContentLoaded', function() {
    console.log('檢查是否需要初始化極區域圖');
    
    // 檢查頁面是否有極區圖容器
    const polarAreaChartContainer = document.getElementById('polarAreaChart');
    if (polarAreaChartContainer) {
      console.log('檢測到極區圖容器，準備初始化');
      window.initPolarAreaChart();
    }
  });
  
  // 處理極區圖渲染
  window.handlePolarAreaChart = function(data) {
    console.log('開始處理極區圖渲染', data);
    
    // 檢查圖表容器
    const chartContainer = document.getElementById('polarAreaChart');
    if (!chartContainer) {
      console.error('找不到極區域圖容器元素 #polarAreaChart');
      if (window.chartErrorHandler) {
        window.chartErrorHandler.showError('polarAreaChart', '找不到極區域圖容器');
      }
      return false;
    }
    
    // 清除現有的圖表實例
    if (window.ApexCharts) {
      try {
        const existingChart = ApexCharts.getChartByID('polarAreaChart') || window.polarAreaChartInstances['polarAreaChart'];
        if (existingChart && typeof existingChart.destroy === 'function') {
          console.log('清除既有極區域圖實例');
          existingChart.destroy();
        }
      } catch (e) {
        console.warn('清除極區域圖時發生錯誤:', e);
      }
    }
    
    // 確保資料結構正確
    if (!data) {
      console.error('極區域圖資料無效');
      if (window.chartErrorHandler) {
        window.chartErrorHandler.showError('polarAreaChart', '極區域圖資料無效');
      }
      return false;
    }
    
    // 確保圖表類型設置為polarArea
    if (!data.chart) data.chart = {};
    data.chart.type = 'polarArea';
    
    // 確保填充設定
    if (!data.fill) {
      data.fill = {
        opacity: 0.8
      };
    }
    
    // 確保標籤
    if (!data.labels || !Array.isArray(data.labels) || data.labels.length === 0) {
      if (!data.series || !Array.isArray(data.series)) {
        console.warn('極區域圖缺少標籤和數據，設置預設值');
        data.labels = ['類別A', '類別B', '類別C', '類別D', '類別E'];
        data.series = [42, 47, 52, 58, 65];
      } else {
        console.warn('極區域圖缺少標籤，根據數據長度生成');
        data.labels = Array(data.series.length).fill().map((_, i) => `類別${i+1}`);
      }
    }
    
    // 確保stroke設定
    if (!data.stroke) {
      data.stroke = {
        width: 1,
        colors: ['#fff']
      };
    }
    
    try {
      console.log('初始化極區域圖', data);
      const chart = new ApexCharts(chartContainer, data);
      window.polarAreaChartInstances['polarAreaChart'] = chart;
      chart.render();
      console.log('極區域圖渲染完成');
      return true;
    } catch (error) {
      console.error('渲染極區域圖時發生錯誤:', error);
      
      if (window.chartErrorHandler) {          window.chartErrorHandler.showError('polarAreaChart', `無法渲染極區域圖: ${error.message}`);
        
        // 嘗試使用替代數據源
        const alternativeFiles = [
          'apexcharts_polararea_basic.json',
          'apexcharts_polararea_resource.json',
          'apexcharts_polararea_investment.json'
        ];
        
        window.chartErrorHandler.retryLoadData('polarArea', alternativeFiles, 'polarAreaChart', window.handlePolarAreaChart);
      } else {
        chartContainer.innerHTML = `
          <div class="flex flex-col items-center justify-center h-full">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-error mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <p class="text-base text-error font-medium">渲染極區域圖失敗: ${error.message}</p>
            <button class="btn btn-sm btn-outline btn-error mt-4" onclick="location.reload()">重新整理頁面</button>
          </div>
        `;
      }
      return false;
    }
  };
  
  // 初始化極區域圖
  window.initPolarAreaChart = function() {
    console.log('初始化極區域圖...');
    
    // 如果有預設配置則載入
    window.loadPolarAreaData();
  };
  
  // 載入極區域圖資料
  window.loadPolarAreaData = function(dataType = 'default') {
    console.log(`載入極區域圖資料 (類型: ${dataType})`);
    
    let fileName;
    switch (dataType.toLowerCase()) {
      case 'resource':
        fileName = 'apexcharts_polararea_resource.json';
        break;
      case 'investment':
        fileName = 'apexcharts_polararea_investment.json';
        break;
      case 'education':
        fileName = 'apexcharts_polararea_education.json';
        break;
      case 'default':
      default:
        fileName = 'apexcharts_polararea_basic.json';
    }
    
    // 檢查是否由統一資料載入器處理
    if (window.DataLoader && typeof window.DataLoader.loadChartData === 'function') {
      window.DataLoader.loadChartData('polarArea', fileName)
        .then(data => {
          if (data) {
            window.handlePolarAreaChart(data);
          } else {
            console.error('載入極區域圖預設資料失敗 (經由統一資料載入器)');
            if (window.chartErrorHandler) {
              window.chartErrorHandler.showError('polarAreaChart', '載入極區域圖預設資料失敗');
            }
          }
        })
        .catch(error => {
          console.error('載入極區域圖預設資料時發生錯誤:', error);
          if (window.chartErrorHandler) {
            window.chartErrorHandler.showError('polarareaChart', `載入極區域圖預設資料失敗: ${error.message}`);
          }
        });
    } else {
      console.warn('找不到統一資料載入器，嘗試直接載入極區域圖資料');
      
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
              console.log('使用JSON增強工具成功解析');
            } else {
              // 若沒有增強工具，使用標準解析
              data = JSON.parse(text);
            }
          } catch (e) {
            console.warn(`解析JSON時發生錯誤，嘗試修復: ${e.message}`);
            
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
          if (data) {
            data = processJsonFunctions(data);
          }
          
          window.handlePolarAreaChart(data);
        })
        .catch(error => {
          console.error('直接載入極區域圖資料時發生錯誤:', error);
          if (window.chartErrorHandler) {
            window.chartErrorHandler.showError('polarareaChart', `載入極區域圖預設資料失敗: ${error.message}`);
            // 嘗試加載替代數據
            window.loadPolarAreaChartExample('apexcharts_polararea_basic.json');
          }
        });
    }
  };
  
  // 提供極區域圖範例資料
  window.getPolarAreaChartExamples = function() {
    return {
      basic: {
        chart: {
          type: 'polarArea',
          height: 350
        },
        series: [14, 23, 21, 17, 15, 10, 12, 17, 21],
        labels: ['類別A', '類別B', '類別C', '類別D', '類別E', '類別F', '類別G', '類別H', '類別I'],
        stroke: {
          colors: ['#fff']
        },
        fill: {
          opacity: 0.8
        },
        responsive: [{
          breakpoint: 480,
          options: {
            chart: {
              width: 280
            },
            legend: {
              position: 'bottom'
            }
          }
        }]
      },
      resource: {
        chart: {
          type: 'polarArea',
          height: 350
        },
        series: [14, 23, 21, 17, 15, 10],
        labels: ['類別A', '類別B', '類別C', '類別D', '類別E', '類別F'],
        stroke: {
          colors: ['#fff']
        },
        fill: {
          opacity: 0.8
        },
        colors: ["#00E396", "#FF4560", "#775DD0", "#008FFB", "#FEB019", "#A300D6"],
        title: {
          text: "資源分配比例"
        },
        responsive: [{
          breakpoint: 480,
          options: {
            chart: {
              width: 280
            },
            legend: {
              position: 'bottom'
            }
          }
        }]
      },
      investment: {
        chart: {
          type: 'polarArea',
          height: 350
        },
        series: [14, 23, 21, 17, 15, 10],
        labels: ['醫療保健', '金融服務', '能源', '科技', '消費品', '工業'],
        stroke: {
          width: 2
        },
        fill: {
          opacity: 0.8
        },
        colors: ["#00D8B6", "#008FFB", "#FEB019", "#FF4560", "#775DD0", "#546E7A"],
        title: {
          text: "投資組合產業分布",
          align: "left"
        },
        responsive: [{
          breakpoint: 480,
          options: {
            chart: {
              width: 280
            },
            legend: {
              position: 'bottom'
            }
          }
        }]
      }
    };
  };
  
  // 使用全域的processJsonFunctions函數
  
  // 載入特定極區域圖範例
  window.loadPolarAreaChartExample = function(exampleFile) {
    console.log(`載入極區域圖範例: ${exampleFile}`);
    
    fetch(`./assets/examples/${exampleFile}`)
      .then(response => {
        if (!response.ok) throw new Error(`範例檔案 ${exampleFile} 不存在`);
        return response.text(); // 先取得文本再解析，以便處理JSON格式問題
      })
      .then(text => {
        // 嘗試解析JSON，處理可能的格式問題
        let data;
        
        try {
          // 首先嘗試透過JSON增強工具解析
          if (window.JSONEnhancer && typeof window.JSONEnhancer.parse === 'function') {
            data = window.JSONEnhancer.parse(text);
            console.log('使用JSON增強工具成功解析');
          } else {
            // 若沒有增強工具，使用標準解析
            data = JSON.parse(text);
          }
        } catch (e) {
          console.warn(`解析JSON時發生錯誤，嘗試修復: ${e.message}`);
          
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
        
        // 確保數據適用於極區域圖
        if (data.chart) {
          data.chart.type = 'polarArea';
        } else {
          data.chart = { type: 'polarArea' };
        }
        
        window.handlePolarAreaChart(data);
      })
      .catch(error => {
        console.error(`載入極區域圖範例失敗: ${exampleFile}`, error);
        if (window.chartErrorHandler) {
          window.chartErrorHandler.showError('polarAreaChart', `載入範例失敗: ${error.message}`);
          
          // 如果外部範例加載失敗，使用內建範例
          const examples = window.getPolarAreaChartExamples();
          window.handlePolarAreaChart(examples.basic);
        }
      });
  };
})();
