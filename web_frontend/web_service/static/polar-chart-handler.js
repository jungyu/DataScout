/**
 * 極區圖專用處理函數
 * 解決極區圖渲染問題
 */

(function() {
  console.log('極區圖專用處理函數已啟動');
  
  // 全局保存極區圖實例
  window.polarChartInstances = {};
  
  // 在頁面載入完成後執行
  document.addEventListener('DOMContentLoaded', function() {
    console.log('檢查是否需要初始化極區圖');
    
    // 檢查頁面是否有極區圖容器
    const polarChartContainer = document.getElementById('polarChart');
    if (polarChartContainer) {
      console.log('檢測到極區圖容器，準備初始化');
      window.initPolarChart();
    }
  });
  
  // 處理極區圖渲染
  window.handlePolarChart = function(data) {
    console.log('開始處理極區圖渲染', data);
    
    // 檢查圖表容器
    const chartContainer = document.getElementById('polarChart');
    if (!chartContainer) {
      console.error('找不到極區圖容器元素 #polarChart');
      if (window.chartErrorHandler) {
        window.chartErrorHandler.showError('polarChart', '找不到極區圖容器');
      }
      return;
    }
    
    try {
        // 清理現有圖表實例
        const existingChart = ApexCharts.getChartByID('polarChart') || window.polarChartInstances['polarChart'];
        if (existingChart) {
          console.log('清理現有極區圖實例');
          existingChart.destroy();
          delete window.polarChartInstances['polarChart'];
        }
    } catch (e) {
      console.log('清理圖表實例時發生錯誤:', e);
    }
    
    // 驗證資料
    if (!data || typeof data !== 'object') {
      console.error('極區圖資料無效', data);
      if (window.chartErrorHandler) {
        window.chartErrorHandler.showError('polarChart', '極區圖資料無效');
      }
      return;
    }
    
    // 確保 chart 對象存在
    if (!data.chart) {
      data.chart = {};
    }
    
    // 設置圖表類型
    data.chart.type = 'polarArea';
    
    // 確保有預設高度
    if (!data.chart.height) {
      data.chart.height = 350;
    }
    
    // 確保有系列數據
    if (!data.series || !Array.isArray(data.series)) {
      console.warn('極區圖缺少系列數據，使用預設數據');
      data.series = [14, 23, 21, 17, 15, 10, 12, 17, 21];
    }
    
    // 確保有標籤
    if (!data.labels || !Array.isArray(data.labels)) {
      if (data.series && Array.isArray(data.series)) {
        console.warn('極區圖缺少標籤，根據數據長度生成');
        data.labels = Array(data.series.length).fill().map((_, i) => `類別${i+1}`);
      } else {
        console.warn('極區圖缺少標籤，使用預設標籤');
        data.labels = ['類別A', '類別B', '類別C', '類別D', '類別E'];
        data.series = [42, 47, 52, 58, 65];
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
      console.log('初始化極區圖', data);
      const chart = new ApexCharts(chartContainer, data);
      
      // 保存圖表實例
      window.polarChartInstances['polarChart'] = chart;
      
      // 渲染圖表
      chart.render().then(() => {
        console.log('極區圖渲染完成');
      });
      
    } catch (error) {
      console.error('極區圖渲染失敗:', error);
      if (window.chartErrorHandler) {          window.chartErrorHandler.showError('polarChart', `無法渲染極區圖: ${error.message}`);
        
        // 嘗試使用備用資料
        const alternativeFiles = [
          './assets/examples/apexcharts_polar_basic.json',
          './assets/examples/apexcharts_polar_investment.json',
          './assets/examples/apexcharts_polar_education.json'
        ];
        window.chartErrorHandler.retryLoadData('polar', alternativeFiles, 'polarChart', window.handlePolarChart);
      }
    }
  };
  
  // 保持舊函數名稱以確保向後兼容
  window.handlePolarAreaChart = function(data) {
    console.log('呼叫了舊的 handlePolarAreaChart，重新導向到新函數');
    return window.handlePolarChart(data);
  };
  
  // 初始化極區圖函數
  window.initPolarChart = function() {
    console.log('初始化極區圖');
    
    // 檢查頁面是否有極區圖
    const currentPath = window.location.pathname;
    if (!currentPath.includes('polar.html')) {
      console.log('當前頁面不是極區圖頁面，跳過初始化');
      return;
    }
    
    console.log('當前在極區圖頁面，開始載入預設資料');
    
    // 優先使用 data-loader 的初始化機制
    if (window.__chartPageInitialized) {
      console.log('圖表已由 data-loader 初始化，跳過重複初始化');
      return;
    }
    
    // 嘗試載入預設極區圖資料
    const exampleFiles = [
      './assets/examples/apexcharts_polar_basic.json',
      './assets/examples/apexcharts_polar_investment.json',
      './assets/examples/apexcharts_polar_education.json'
    ];
    
    let loadSuccess = false;
    
    const tryLoadExample = (fileIndex) => {
      if (fileIndex >= exampleFiles.length) {
        console.log('所有範例檔案載入失敗，使用硬編碼預設資料');
        const defaultData = window.getPolarChartExamples().basic;
        window.handlePolarChart(defaultData);
        return;
      }
      
      const file = exampleFiles[fileIndex];
      console.log(`嘗試載入極區圖範例: ${file}`);
      
      fetch(file)
        .then(response => {
          if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
          }
          return response.json();
        })
        .then(data => {
          console.log(`成功載入極區圖範例: ${file}`, data);
          loadSuccess = true;
          window.handlePolarChart(data);
        })
        .catch(error => {
          console.error(`載入極區圖範例失敗 ${file}:`, error);
          if (window.chartErrorHandler) {
            window.chartErrorHandler.showError('polarChart', '載入極區圖預設資料失敗');
          }
          
          // 嘗試下一個檔案
          setTimeout(() => tryLoadExample(fileIndex + 1), 100);
        });
    };
    
    // 開始嘗試載入
    tryLoadExample(0);
    
    // 如果2秒後還沒成功，使用硬編碼資料
    setTimeout(() => {
      if (!loadSuccess) {
        console.log('載入超時，使用硬編碼預設資料');
        try {
          const defaultData = window.getPolarChartExamples().basic;
          window.handlePolarChart(data);
        } catch (error) {
          console.error('使用硬編碼資料也失敗:', error);
          if (window.chartErrorHandler) {
            window.chartErrorHandler.showError('polarChart', `載入極區圖預設資料失敗: ${error.message}`);
          } else {
            window.loadPolarChartExample('apexcharts_polar_basic.json');
          }
        }
      }
    }, 2000);
  };
  
  // 保持舊函數名稱以確保向後兼容
  window.initPolarAreaChart = function() {
    console.log('呼叫了舊的 initPolarAreaChart，重新導向到新函數');
    return window.initPolarChart();
  };
  
  // 獲取極區圖範例資料
  window.getPolarChartExamples = function() {
    return {
      basic: {
        series: [14, 23, 21, 17, 15, 10, 12, 17, 21],
        chart: {
          type: 'polarArea',
          height: 350
        },
        labels: ['研發', '市場營銷', '銷售', '客服', '營運', '人力資源', '財務', '法務', '其他'],
        colors: ['#00D9FF', '#8B5CF6', '#10B981', '#F59E0B', '#EF4444', '#6B7280', '#EC4899', '#14B8A6', '#F97316'],
        fill: {
          opacity: 0.8
        },
        stroke: {
          width: 1,
          colors: undefined
        },
        yaxis: {
          show: false
        },
        legend: {
          position: 'bottom'
        },
        plotOptions: {
          polarArea: {
            rings: {
              strokeWidth: 0
            },
            spokes: {
              strokeWidth: 0
            }
          }
        },
        title: {
          text: "部門資源分配分析",
          align: 'center',
          style: {
            fontSize: '18px',
            fontWeight: 'bold',
            color: '#263238'
          }
        },
        tooltip: {
          y: {
            formatter: function(val) {
              return val + "%"
            }
          }
        }
      },
      investment: {
        series: [30, 25, 20, 15, 10],
        chart: {
          type: 'polarArea',
          height: 350
        },
        labels: ['股票', '債券', '房地產', '現金', '其他'],
        colors: ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57'],
        fill: {
          opacity: 0.9
        },
        stroke: {
          width: 2,
          colors: ['#fff']
        },
        title: {
          text: "投資組合分配",
          align: 'center'
        },
        legend: {
          position: 'bottom'
        }
      },
      education: {
        series: [35, 28, 22, 15],
        chart: {
          type: 'polarArea',
          height: 350
        },
        labels: ['線上課程', '實體課程', '自學', '培訓營'],
        colors: ['#667eea', '#764ba2', '#f093fb', '#f5576c'],
        fill: {
          opacity: 0.85
        },
        title: {
          text: "教育資源分配",
          align: 'center'
        },
        legend: {
          position: 'right'
        }
      }
    };
  };
  
  // 保持舊函數名稱以確保向後兼容
  window.getPolarAreaChartExamples = function() {
    console.log('呼叫了舊的 getPolarAreaChartExamples，重新導向到新函數');
    return window.getPolarChartExamples();
  };
  
  // 載入特定範例
  window.loadPolarChartExample = function(exampleFile) {
    console.log(`載入極區圖範例: ${exampleFile}`);
    
    // 將檔名從 polararea 轉換為 polar
    const modernFileName = exampleFile.replace(/polararea/g, 'polar');
    
    const examplePath = `./assets/examples/${modernFileName}`;
    
    fetch(examplePath)
      .then(response => {
        if (!response.ok) {
          throw new Error(`無法載入範例檔案: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        console.log(`成功載入極區圖範例: ${modernFileName}`, data);
        window.handlePolarChart(data);
      })
      .catch(error => {
        console.error(`載入極區圖範例失敗: ${error.message}`);
        
        // 嘗試使用硬編碼範例
        const examples = window.getPolarChartExamples();
        const exampleKey = exampleFile.includes('investment') ? 'investment' : 
                          exampleFile.includes('education') ? 'education' : 'basic';
        
        if (examples[exampleKey]) {
          console.log(`使用硬編碼範例: ${exampleKey}`);
          window.handlePolarChart(examples[exampleKey]);
        } else {
          console.log('使用基本範例');
          window.handlePolarChart(examples.basic);
        }
      });
  };
  
  // 保持舊函數名稱以確保向後兼容
  window.loadPolarAreaChartExample = function(exampleFile) {
    console.log('呼叫了舊的 loadPolarAreaChartExample，重新導向到新函數');
    return window.loadPolarChartExample(exampleFile);
  };
  
})();
