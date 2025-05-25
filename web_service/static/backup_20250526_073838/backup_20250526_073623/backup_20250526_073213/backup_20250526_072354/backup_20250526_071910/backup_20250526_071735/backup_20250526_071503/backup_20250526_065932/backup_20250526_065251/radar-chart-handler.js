/**
 * 雷達圖專用處理函數
 * 解決雷達圖渲染問題
 */

(function() {
  console.log('雷達圖專用處理函數已啟動');
  
  // 全局保存雷達圖實例
  window.radarChartInstances = {};
  
  // 在頁面載入完成後執行
  document.addEventListener('DOMContentLoaded', function() {
    console.log('檢查是否需要初始化雷達圖');
    
    // 檢查頁面是否有雷達圖容器
    const radarChartContainer = document.getElementById('radarChart');
    if (radarChartContainer) {
      console.log('檢測到雷達圖容器，準備初始化');
      window.initRadarChart();
    }
  });
  
  // 處理雷達圖渲染
  window.handleRadarChart = function(data) {
    console.log('開始處理雷達圖渲染', data);
    
    // 檢查圖表容器
    const chartContainer = document.getElementById('radarChart');
    if (!chartContainer) {
      console.error('找不到雷達圖容器元素 #radarChart');
      if (window.chartErrorHandler) {
        window.chartErrorHandler.showError('radarChart', '找不到雷達圖容器');
      }
      return false;
    }
    
    // 清除現有的圖表實例
    if (window.ApexCharts) {
      try {
        const existingChart = ApexCharts.getChartByID('radarChart') || window.radarChartInstances['radarChart'];
        if (existingChart && typeof existingChart.destroy === 'function') {
          console.log('清除既有雷達圖實例');
          existingChart.destroy();
        }
      } catch (e) {
        console.warn('清除雷達圖時發生錯誤:', e);
      }
    }
    
    // 確保資料結構正確
    if (!data) {
      console.error('雷達圖資料無效');
      if (window.chartErrorHandler) {
        window.chartErrorHandler.showError('radarChart', '雷達圖資料無效');
      }
      return false;
    }
    
    // 確保圖表類型設置為radar
    if (!data.chart) data.chart = {};
    data.chart.type = 'radar';
    
    // 確保基本設定
    if (!data.xaxis || !data.xaxis.categories) {
      console.warn('雷達圖缺少類別資料，設置預設值');
      if (!data.xaxis) data.xaxis = {};
      data.xaxis.categories = ['January', 'February', 'March', 'April', 'May', 'June'];
    }
    
    // 確保系列資料
    if (!data.series || !Array.isArray(data.series) || data.series.length === 0) {
      console.warn('雷達圖缺少系列資料，設置預設值');
      data.series = [{
        name: '預設系列',
        data: [80, 50, 30, 40, 100, 20]
      }];
    }
    
    // 格式轉換處理
    if (data.plotOptions && data.plotOptions.radar && typeof data.plotOptions.radar.polygons === 'string') {
      try {
        const polygonsStr = data.plotOptions.radar.polygons;
        data.plotOptions.radar.polygons = JSON.parse(polygonsStr);
        console.log('成功將雷達圖 polygons 字串轉換為物件');
      } catch (e) {
        console.error('轉換雷達圖 polygons 字串為物件失敗:', e);
        delete data.plotOptions.radar.polygons;
      }
    }
    
    try {
      console.log('初始化雷達圖', data);
      const chart = new ApexCharts(chartContainer, data);
      window.radarChartInstances['radarChart'] = chart;
      chart.render();
      console.log('雷達圖渲染完成');
      return true;
    } catch (error) {
      console.error('渲染雷達圖時發生錯誤:', error);
      
      if (window.chartErrorHandler) {
        window.chartErrorHandler.showError('radarChart', `無法渲染雷達圖: ${error.message}`);
        
        // 嘗試使用替代數據源
        const alternativeFiles = [
          'apexcharts_radar_tech_industry.json',
          'apexcharts_radar_character.json',
          'apexcharts_radar_business_performance.json'
        ];
        
        window.chartErrorHandler.retryLoadData('radar', alternativeFiles, 'radarChart', window.handleRadarChart);
      } else {
        chartContainer.innerHTML = `
          <div class="flex flex-col items-center justify-center h-full">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-error mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <p class="text-base text-error font-medium">渲染雷達圖失敗: ${error.message}</p>
            <button class="btn btn-sm btn-outline btn-error mt-4" onclick="location.reload()">重新整理頁面</button>
          </div>
        `;
      }
      return false;
    }
  };
  
  // 初始化雷達圖
  window.initRadarChart = function() {
    console.log('初始化雷達圖...');
    
    // 如果有預設配置則載入
    window.loadRadarData();
  };
  
  // 載入雷達圖資料
  window.loadRadarData = function(dataType = 'default') {
    console.log(`載入雷達圖資料 (類型: ${dataType})`);
    
    let fileName;
    switch (dataType.toLowerCase()) {
      case 'business':
        fileName = 'apexcharts_radar_business_performance.json';
        break;
      case 'character':
        fileName = 'apexcharts_radar_character.json';
        break;
      case 'default':
      default:
        fileName = 'apexcharts_radar_tech_industry.json';
    }
    
    // 檢查是否由統一資料載入器處理
    if (window.DataLoader && typeof window.DataLoader.loadChartData === 'function') {
      window.DataLoader.loadChartData('radar', fileName)
        .then(data => {
          if (data) {
            window.handleRadarChart(data);
          } else {
            console.error('載入雷達圖預設資料失敗 (經由統一資料載入器)');
            if (window.chartErrorHandler) {
              window.chartErrorHandler.showError('radarChart', '載入雷達圖預設資料失敗');
            }
          }
        })
        .catch(error => {
          console.error('載入雷達圖預設資料時發生錯誤:', error);
          if (window.chartErrorHandler) {
            window.chartErrorHandler.showError('radarChart', `載入雷達圖預設資料失敗: ${error.message}`);
          }
        });
    } else {
      console.warn('找不到統一資料載入器，嘗試直接載入雷達圖資料');
      
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
              console.log('使用JSON增強工具成功解析雷達圖資料');
            } else {
              // 若沒有增強工具，使用標準解析
              data = JSON.parse(text);
            }
          } catch (e) {
            console.warn(`解析雷達圖JSON時發生錯誤，嘗試修復: ${e.message}`);
            
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
          
          window.handleRadarChart(data);
        })
        .catch(error => {
          console.error('直接載入雷達圖資料時發生錯誤:', error);
          if (window.chartErrorHandler) {
            window.chartErrorHandler.showError('radarChart', `載入雷達圖預設資料失敗: ${error.message}`);
          }
        });
    }
  };
  
  // 提供雷達圖範例資料
  window.getRadarChartExamples = function() {
    return {
      basic: {
        chart: {
          type: 'radar',
          height: 350,
          dropShadow: {
            enabled: true,
            blur: 1,
            left: 1,
            top: 1
          }
        },
        series: [{
          name: '系列 1',
          data: [80, 50, 30, 40, 100, 20]
        }],
        title: {
          text: '基本雷達圖'
        },
        xaxis: {
          categories: ['January', 'February', 'March', 'April', 'May', 'June']
        },
        colors: ['#3B82F6']
      },
      multiSeries: {
        chart: {
          type: 'radar',
          height: 350,
          toolbar: {
            show: false
          }
        },
        series: [{
          name: '系列 1',
          data: [80, 50, 30, 40, 100, 20]
        }, {
          name: '系列 2',
          data: [20, 30, 40, 80, 20, 80]
        }, {
          name: '系列 3',
          data: [44, 76, 78, 13, 43, 10]
        }],
        title: {
          text: '多系列雷達圖'
        },
        xaxis: {
          categories: ['January', 'February', 'March', 'April', 'May', 'June']
        },
        colors: ['#3B82F6', '#10B981', '#F97316'],
        stroke: {
          width: 2
        },
        fill: {
          opacity: 0.1
        },
        markers: {
          size: 3
        }
      }
    };
  };
})();
