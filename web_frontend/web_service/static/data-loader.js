/**
 * 圖表資料動態載入腳本
 * 從 /public/assets/examples 資料夾中載入範例資料
 * 檔名格式: [函式庫]_[圖表類型]_[資料說明].json
 */

(function() {
  console.log('資料動態載入腳本已啟動');

  // 定義圖表類型枚舉
  const ChartType = {
    AREA: 'area',
    LINE: 'line',
    COLUMN: 'column',
    BAR: 'bar',
    PIE: 'pie', 
    DONUT: 'donut',
    RADAR: 'radar',
    POLAR: 'polar', // 極區圖，避免命名首字大小寫問題
    HEATMAP: 'heatmap',
    TREEMAP: 'treemap',
    SCATTER: 'scatter',
    MIXED: 'mixed',
    STACKED_BAR: 'stacked_bar',
    BOXPLOT: 'boxplot',
    FUNNEL: 'funnel',
    BUBBLE: 'bubble',
    CANDLESTICK: 'candlestick',
    
    // 獲取所有圖表類型
    getAll() {
      return Object.values(this).filter(value => typeof value === 'string');
    },
    
    // 檢查是否為有效的圖表類型
    isValid(type) {
      if (!type) return false;
      const lowerType = type.toLowerCase();
      return this.getAll().some(validType => validType.toLowerCase() === lowerType);
    }
  };

  // 圖表類型與頁面元素ID的對應 (擴充)
  const ChartElementMap = {
    [ChartType.AREA]: 'areaChart',      // 區域圖
    [ChartType.LINE]: 'lineChart',
    [ChartType.COLUMN]: 'columnChart',
    [ChartType.BAR]: 'barChart',
    [ChartType.PIE]: 'pieChart',
    [ChartType.DONUT]: 'donutChart',
    [ChartType.RADAR]: 'radarChart',
    [ChartType.POLAR]: 'polarChart', // 極區圖，使用更簡潔的命名
    [ChartType.HEATMAP]: 'heatmapChart',
    [ChartType.TREEMAP]: 'treemapChart',
    [ChartType.SCATTER]: 'scatterChart',
    [ChartType.MIXED]: 'mixedChart',
    [ChartType.STACKED_BAR]: 'stackedBarChart',
    [ChartType.BOXPLOT]: 'boxplotChart',
    [ChartType.FUNNEL]: 'funnelChart',
    [ChartType.BUBBLE]: 'bubbleChart',
    [ChartType.CANDLESTICK]: 'candlestickChart', 
    // 其他圖表類型可在此擴充...
  };

  // 圖表類型與頁面標題關鍵字的對應 (擴充)
  const ChartTitleMap = {
    [ChartType.AREA]: ['區域圖', 'area chart'],           // 區域圖
    [ChartType.LINE]: ['折線圖', 'line chart'],
    [ChartType.COLUMN]: ['柱狀圖', 'column chart'],
    [ChartType.BAR]: ['長條圖', 'bar chart'],
    [ChartType.PIE]: ['圓餅圖', 'pie chart'],
    [ChartType.DONUT]: ['甜甜圈圖', 'donut chart'],
    [ChartType.RADAR]: ['雷達圖', 'radar chart'],
    [ChartType.POLAR]: ['極區圖', 'polar chart'], // 更改為更簡潔的中文名稱
    [ChartType.HEATMAP]: ['熱力圖', 'heatmap chart'],
    [ChartType.TREEMAP]: ['樹狀圖', 'treemap chart'],
    [ChartType.SCATTER]: ['散佈圖', 'scatter chart'],
    [ChartType.MIXED]: ['混合圖', 'mixed chart'],
    [ChartType.CANDLESTICK]: ['K線圖', 'candlestick chart'],
    // 其他圖表類型可在此擴充...
  };

  // 存儲不同圖表類型的資料
  const chartDataCache = {};
  
  // 圖表類型檢測映射表
  const chartTypeMapping = {
    'area.html': ChartType.AREA,
    'polar.html': ChartType.POLAR
  };
  
  // 初始化資料選擇器
  function initDataSelector() {
    const dataSelectors = document.querySelectorAll('.chart-data-selector, #chart-data-selector-component');
    if (!dataSelectors.length) {
      console.log('找不到資料選擇器，將在300ms後重試');
      setTimeout(initDataSelector, 300);
      return;
    }
    
    console.log(`找到 ${dataSelectors.length} 個資料選擇器`);
    
    // 偵測當前頁面的圖表類型
    const chartType = detectChartType();
    if (!chartType) {
      console.warn('無法確定當前頁面圖表類型');
      return;
    }
    
    console.log(`檢測到當前圖表類型: ${chartType}`);
    
    // 檢查頁面是否已經初始化過
    const pageInitialized = window.__chartPageInitialized === true;
    
    // 如果頁面已初始化且與當前圖表類型不同，則清除所有圖表實例
    if (pageInitialized && window.__currentChartType !== chartType) {
      console.log(`圖表類型從 ${window.__currentChartType} 切換到 ${chartType}，清除舊圖表`);
      
      // 清除先前的圖表
      for (const type of ChartType.getAll()) {
        window.cleanupChartInstances(`${type}Chart`);
      }
    }
    
    // 記錄當前圖表類型和初始化狀態
    window.__currentChartType = chartType;
    window.__chartPageInitialized = true;
    
    // 遍歷所有資料選擇器
    dataSelectors.forEach(selector => {
      // 載入該圖表類型的所有範例資料
      loadExamplesList(chartType, selector);
    });
  }
  
  // 偵測當前頁面的圖表類型
  function detectChartType() {
    // 方法 1: 通過 URL 路徑判斷
    const pathname = window.location.pathname.toLowerCase();
    
    if (pathname.includes('area.html')) return ChartType.AREA;
    if (pathname.includes('line.html')) return ChartType.LINE;
    if (pathname.includes('column.html')) return ChartType.COLUMN;
    if (pathname.includes('bar.html')) return ChartType.BAR;
    if (pathname.includes('pie.html')) return ChartType.PIE;
    if (pathname.includes('donut.html')) return ChartType.DONUT;
    if (pathname.includes('radar.html')) return ChartType.RADAR;
    if (pathname.includes('polar.html')) return ChartType.POLAR;
    if (pathname.includes('heatmap.html')) return ChartType.HEATMAP;
    if (pathname.includes('treemap.html')) return ChartType.TREEMAP;
    if (pathname.includes('scatter.html')) return ChartType.SCATTER;
    if (pathname.includes('mixed.html')) return ChartType.MIXED;
    if (pathname.includes('candlestick.html')) return ChartType.CANDLESTICK;
    // 預設/首頁通常是 line
    if (pathname.includes('index.html') || pathname.endsWith('/') || pathname === '') return ChartType.CANDLESTICK;
    
    // 方法 2: 通過頁面 body 的 data-chart-type 屬性判斷 (新增)
    const bodyChartType = document.body.dataset.chartType;
    if (bodyChartType && ChartType.isValid(bodyChartType)) {
      console.log(`detectChartType: Found chart type from body data attribute: ${bodyChartType}`);
      return bodyChartType.toUpperCase(); // Ensure it matches ChartType enum keys
    }

    // 方法 3: 通過圖表容器 ID 判斷
    for (const type of ChartType.getAll()) {
        // Generate potential chart ID, e.g., 'areaChart', 'pieChart'
        const chartId = `${type.toLowerCase()}Chart`; 
        if (document.getElementById(chartId)) {
            console.log(`detectChartType: Found chart type by element ID: ${chartId}`);
            return type; // type is already in uppercase as per ChartType enum keys
        }
    }
    
    // 方法 4: 通過圖表標題文字判斷
    const chartTitles = document.querySelectorAll('.text-lg.font-bold');
    for (const title of chartTitles) {
      const titleText = title.textContent.toLowerCase();
      
      for (const [type, keywords] of Object.entries(ChartTitleMap)) {
        if (keywords.some(keyword => titleText.includes(keyword))) {
          return type;
        }
      }
    }
    
    // 無法判斷
    console.warn('detectChartType: Unable to determine chart type from URL, body attribute, element ID, or title.');
    return null;
  }
  
  // 載入指定圖表類型的範例資料清單
  function loadExamplesList(chartType, selector) {
    // 避免重複載入同一類型的範例
    if (selector.dataset.loadedChartType === chartType) {
      console.log(`已經載入過 ${chartType} 圖表的範例資料清單，跳過重複載入`);
      return;
    }
    
    // 標記當前載入的圖表類型
    selector.dataset.loadedChartType = chartType;
    
    console.log(`開始載入 ${chartType} 圖表的範例資料清單...`);
    
    // 清除可能存在的之前圖表實例
    for (const type of ChartType.getAll()) {
      const chartElementId = `${type}Chart`;
      window.cleanupChartInstances(chartElementId);
    }
    
    fetch(`/assets/examples/index.json`)
      .then(response => {
        if (!response.ok) throw new Error('範例索引檔案不存在');
        return response.json();
      })
      .then(indexData => {
        // 根據 suitableTypes 過濾出適用於當前圖表類型的範例
        const typeExamples = [];
        // indexData 現在是一個對象，需要遍歷其屬性（圖表類型）
        for (const type in indexData) {
            if (indexData.hasOwnProperty(type) && Array.isArray(indexData[type])) {
                indexData[type].forEach(example => {
                    // 檢查 example.suitableTypes 是否包含當前 chartType
                    if (example.suitableTypes && Array.isArray(example.suitableTypes) && example.suitableTypes.includes(chartType)) {
                        typeExamples.push(example);
                    }
                });
            }
        }
        
        console.log(`載入了 ${typeExamples.length} 個適用於 ${chartType} 的範例`);
        
        // 生成範例資料區塊
        generateExampleBlocks(typeExamples, selector, chartType);
      })
      .catch(error => {
        console.error('載入範例索引時發生錯誤:', error);
        // 如果無法載入索引，嘗試直接掃描資料夾
        fallbackDirectoryScanning(chartType, selector);
      });
  }
  
  // 生成範例資料區塊
  function generateExampleBlocks(examples, selector, chartType) {
    console.log(`為 ${chartType} 圖表生成範例區塊`, examples);
    // 找到對應的圖表類型數據塊
    const dataBlockId = `${chartType}-chart-data`;
    const dataContainer = selector.querySelector(`#${dataBlockId}`) || selector;
    
    if (!dataContainer) {
      console.error(`找不到 ${chartType} 圖表數據塊 (#${dataBlockId})`);
      return;
    }
    
    // 清空現有的資料區塊，但保留類別標籤
    dataContainer.innerHTML = '';
    
    // 檢查是否有範例
    if (!examples || examples.length === 0) {
      console.warn(`圖表類型 ${chartType} 沒有可用的範例資料`);
      dataContainer.innerHTML = `
        <div class="text-center p-4 text-base-content/50">
          沒有可用的範例資料
        </div>
      `;
      return;
    }
    
    // 追蹤是否已自動載入了第一個範例
    let firstExampleLoaded = false;
    
    // 為每個範例創建一個資料區塊
    examples.forEach((example, index) => {
      const block = document.createElement('div');
      block.className = 'bg-base-200 p-4 mb-4 rounded-lg hover:bg-base-300 transition-colors border border-base-300';
      block.dataset.file = example.file;
      block.dataset.chartType = chartType;
      
      // 動態設置按鈕文字，第一個範例標記為「自動載入」
      const buttonText = index === 0 ? '自動載入' : '點擊載入';
      
      block.innerHTML = `
        <div class="font-medium mb-1 text-base-content">${example.title}</div>
        <div class="text-sm text-base-content opacity-80 mb-2">${example.description}</div>
        <button class="text-accent hover:text-accent-focus text-sm font-medium btn-sm btn-ghost px-2 py-0.5 rounded load-data-btn">${buttonText}</button>
      `;
      
      // 添加點擊載入事件
      const loadBtn = block.querySelector('.load-data-btn');
      loadBtn.addEventListener('click', function() {
        loadChartData(example.file, chartType);
        // 更新所有按鈕狀態
        updateButtonStates(dataContainer, example.file);
      });
      
      dataContainer.appendChild(block);
      
      // 自動載入第一個範例
      if (index === 0 && !firstExampleLoaded) {
        // 設置一個短暫延遲，確保UI先渲染
        setTimeout(() => {
          loadChartData(example.file, chartType);
          updateButtonStates(dataContainer, example.file);
          firstExampleLoaded = true;
        }, 100);
      }
    });
    
    // 確保當前圖表類型數據塊可見
    if (selector.querySelectorAll('.chart-data-block').length > 0) {
      const allBlocks = selector.querySelectorAll('.chart-data-block');
      allBlocks.forEach(block => {
        block.style.display = 'none';
      });
      dataContainer.style.display = 'block';
    }
  }
  
  // 更新按鈕狀態
  function updateButtonStates(container, currentFile) {
    // 找到所有按鈕
    const allButtons = container.querySelectorAll('.load-data-btn');
    
    // 重置所有按鈕
    allButtons.forEach(btn => {
      const parentBlock = btn.closest('div');
      const isCurrent = parentBlock.dataset.file === currentFile;
      
      // 更新按鈕文字和樣式
      if (isCurrent) {
        btn.textContent = '已載入';
        btn.classList.remove('btn-ghost', 'text-accent', 'hover:text-accent-focus');
        btn.classList.add('btn-accent', 'text-accent-content');
        
        // 標記當前選中的範例區塊
        parentBlock.classList.add('border-accent');
        parentBlock.classList.remove('border-base-300');
      } else {
        btn.textContent = '點擊載入';
        btn.classList.add('btn-ghost', 'text-accent', 'hover:text-accent-focus');
        btn.classList.remove('btn-accent', 'text-accent-content');
        
        // 恢復未選中範例區塊的樣式
        parentBlock.classList.remove('border-accent');
        parentBlock.classList.add('border-base-300');
      }
    });
  }
  
  // 如果無法載入索引，嘗試直接掃描資料夾中的檔案
  function fallbackDirectoryScanning(chartType, selector) {
    console.log(`使用備用方法掃描 ${chartType} 圖表的範例資料檔案`);
    
    // 確保圖表類型是有效的
    if (!ChartType.isValid(chartType)) {
      console.error(`無效的圖表類型: ${chartType}`);
      return;
    }
    
    // 根據圖表類型選擇適當的預設範例
    const fallbackExamples = getFallbackExamplesForType(chartType);
    
    // 生成範例區塊
    generateExampleBlocks(fallbackExamples, selector, chartType);
  }
  
  // 根據圖表類型獲取預設的範例資料
  function getFallbackExamplesForType(chartType) {
    // 所有圖表類型都可以使用的通用範例
    const commonExamples = [
      { 
        title: '銷售數據',
        description: '月度銷售和訪客趨勢',
        file: `apexcharts_${chartType}_sales.json`
      },
      {
        title: '收入數據',
        description: '季度收入趨勢',
        file: `apexcharts_${chartType}_revenue.json`
      }
    ];
    
    // 特定圖表類型的專用範例
    const typeSpecificExamples = {
      [ChartType.AREA]: [
        {
          title: '網站統計資料',
          description: '每月訪問量與轉換率',
          file: 'apexcharts_area_webstat.json'
        }
      ],
      [ChartType.LINE]: [
        {
          title: '財務時間序列',
          description: '季度收入趨勢',
          file: 'apexcharts_timeseries_line_unemployment.json'
        }
      ],
      [ChartType.COLUMN]: [
        {
          title: '財務資料',
          description: '季度營收與成本分析',
          file: 'apexcharts_column_finance.json'
        }
      ],
      [ChartType.CANDLESTICK]: [
        {
          title: '股票走勢',
          description: 'AAPL 股票資料',
          file: 'apexcharts_candlestick_stock.json'
        }
      ],
      [ChartType.BOXPLOT]: [
        {
          title: '數據分佈情況',
          description: '類別資料統計分析',
          file: 'apexcharts_boxplot_distribution.json'
        }
      ]
    };
    
    // 如果有特定類型的範例，返回通用範例和特定範例的組合
    if (typeSpecificExamples[chartType]) {
      return [...typeSpecificExamples[chartType], ...commonExamples];
    }
    
    // 否則只返回通用範例
    return commonExamples;
  }
  
  // 載入並應用圖表資料
  function loadChartData(filename, chartType) {
    // 避免重複載入
    if (window.currentLoadedFile === filename) {
      console.log(`檔案 ${filename} 已經載入，跳過重複載入`);
      return;
    }
    
    // 清除舊的圖表
    clearAllChartsForType(chartType);
    
    // 記錄當前載入的檔案
    window.currentLoadedFile = filename;
    
    // 為折線圖添加特殊處理
    const isLineChart = chartType === 'line';
    if (isLineChart) {
      console.log(`折線圖特殊處理: ${filename}`);
    }
    
    // 如果已經載入過此資料，使用緩存
    if (chartDataCache[filename]) {
      applyChartData(chartDataCache[filename], chartType);
      return;
    }
    
    // 從檔案載入資料
    console.log(`開始載入檔案: ${filename}`);
    fetch(`./assets/examples/${filename}`)
      .then(response => {
        if (!response.ok) throw new Error(`檔案 ${filename} 不存在`);
        return response.text(); // 先以文本形式獲取
      })
      .then(text => {
        // 嘗試使用增強版JSON解析
        let data;
        
        try {
          // 先嘗試標準解析
          data = JSON.parse(text);
        } catch (parseError) {
          console.warn(`解析 ${filename} 時發生錯誤，嘗試修復:`, parseError);
          
          // 嘗試使用修復工具處理
          if (window.chartErrorHandler) {
            data = window.chartErrorHandler.fixJsonFormatting(text);
          } else if (typeof handleFunctionStrings === 'function') {
            const processed = handleFunctionStrings(text);
            data = JSON.parse(processed);
          } else {
            throw new Error(`JSON解析失敗: ${parseError.message}`);
          }
        }
        
        if (!data) {
          throw new Error('無法解析JSON資料');
        }
        
        // 緩存資料
        chartDataCache[filename] = data;
        // 應用到圖表
        applyChartData(data, chartType);
      })
      .catch(error => {
        console.error(`載入資料 ${filename} 時發生錯誤:`, error);
        showNotification(`無法載入資料: ${error.message}`, 'error');
      });
  }
  
  // 應用資料到當前圖表
  function applyChartData(data, chartType) {
    console.log(`應用${chartType}圖表資料`, typeof data);
    
    // 檢查是否為有效的圖表類型
    if (!ChartType.isValid(chartType)) {
      console.warn(`未知的圖表類型: ${chartType}`);
      showNotification(`無法套用未知的圖表類型: ${chartType}`, 'error');
      return;
    }
    
    // 使用統一圖表處理器 (如果可用)
    if (typeof window.handleChart === 'function') {
      console.log(`使用統一圖表處理器處理 ${chartType} 圖表`);
      window.handleChart(data, chartType);
      return;
    }
    
    // 退回到原先的特殊處理邏輯
    
    // 特殊處理折線圖類型
    if (chartType === 'line') {
      console.log('偵測到折線圖類型，使用特殊處理邏輯');
      handleLineChart(data);
      return;
    }
    
    // 特殊處理蠟燭圖類型
    if (chartType === 'candlestick' && typeof window.handleCandlestickChart === 'function') {
      console.log('偵測到蠟燭圖類型，使用特殊處理邏輯');
      window.handleCandlestickChart(data);
      return;
    }
    
    // 特殊處理面積圖類型
    if (chartType === 'area' && typeof window.handleAreaChart === 'function') {
      console.log('偵測到面積圖類型，使用特殊處理邏輯');
      window.handleAreaChart(data);
      return;
    }
    
    // 特殊處理柱狀圖類型
    if (chartType === 'column' && typeof window.handleColumnChart === 'function') {
      console.log('偵測到柱狀圖類型，使用特殊處理邏輯');
      window.handleColumnChart(data);
      return;
    }
    
    // 特殊處理極區圖類型 - 統一使用 polar
    const polarTypes = ['polar', 'polarArea', 'polararea', 'polar_area'];
    
    if (polarTypes.includes(chartType.toLowerCase()) && typeof window.handlePolarChart === 'function') {
      console.log('偵測到極區圖類型（polar），使用特殊處理邏輯');
      window.handlePolarChart(data);
      return;
    }
    
    // 向後相容性：支援舊的 handlePolarAreaChart 函數
    if (polarTypes.includes(chartType.toLowerCase()) && typeof window.handlePolarAreaChart === 'function') {
      console.log('偵測到極區圖類型（polararea），使用向後相容處理邏輯');
      window.handlePolarAreaChart(data);
      return;
    }
    
    // 特殊處理餅圖類型
    if (chartType === 'pie' && typeof window.handlePieChart === 'function') {
      console.log('偵測到餅圖類型，使用特殊處理邏輯');
      window.handlePieChart(data);
      return;
    }
    
    // 特殊處理甜甜圈圖類型
    if (chartType === 'donut' && typeof window.handleDonutChart === 'function') {
      console.log('偵測到甜甜圈圖類型，使用特殊處理邏輯');
      window.handleDonutChart(data);
      return;
    }
    
    // 特殊處理雷達圖類型
    if (chartType === 'radar' && typeof window.handleRadarChart === 'function') {
      console.log('偵測到雷達圖類型，使用特殊處理邏輯');
      window.handleRadarChart(data);
      return;
    }
    
    // 創建函數名稱，格式為 update{ChartType}Chart 或 init{ChartType}Chart
    const chartTypeCap = chartType.charAt(0).toUpperCase() + chartType.slice(1);
    const updateFunctionName = `update${chartTypeCap}Chart`;
    const initFunctionName = `init${chartTypeCap}Chart`;
    const cleanupFunctionName = `cleanup${chartTypeCap}Chart`;
    
    // 先徹底清除現有圖表
    clearAllChartsForType(chartType);
    
    // 確保只有一個圖表容器存在於頁面上
    const chartElement = document.getElementById(`${chartType}Chart`);
    if (!chartElement) {
      console.error(`找不到圖表容器 #${chartType}Chart`);
      showNotification('找不到圖表容器，無法載入資料', 'error');
      return;
    }
    
    // 確保容器是空的
    chartElement.innerHTML = '';
    
    console.log(`調用 ${initFunctionName} 或 ${updateFunctionName}...`);
    
    // 嘗試調用相應的更新或初始化函數
    let chartRendered = false;
    
    if (typeof window[updateFunctionName] === 'function') {
      try {
        window[updateFunctionName](data);
        chartRendered = true;
      } catch (err) {
        console.error(`調用 ${updateFunctionName} 時出錯:`, err);
      }
    }
    
    if (!chartRendered && typeof window[initFunctionName] === 'function') {
      try {
        window[initFunctionName](data);
        chartRendered = true;
      } catch (err) {
        console.error(`調用 ${initFunctionName} 時出錯:`, err);
      }
    }
    
    if (!chartRendered) {
      // 如果無法通過函數渲染，嘗試直接使用 ApexCharts 渲染
      try {
        if (typeof ApexCharts !== 'undefined' && data && data.series) {
          console.log('直接使用 ApexCharts 渲染圖表');
          const chart = new ApexCharts(chartElement, data);
          chart.render();
          
          if (window.registerChartInstance) {
            window.registerChartInstance(`${chartType}Chart`, chart);
          }
          
          chartRendered = true;
        }
      } catch (err) {
        console.error('嘗試直接渲染圖表時出錯:', err);
      }
    }
    
    if (!chartRendered) {
      console.warn(`找不到圖表更新函數: ${updateFunctionName} 或 ${initFunctionName}`);
      showNotification(`無法更新圖表: 找不到更新函數`, 'error');
      return;
    }
    
    // 標記當前載入的資料
    window.currentLoadedChartData = {
      type: chartType,
      data: data
    };
    
    showNotification('資料已成功載入!', 'success');
  }
  
  // 顯示通知
  function showNotification(message, type = 'info') {
    // 檢查是否存在通知容器，如果不存在則創建
    let container = document.querySelector('.notification-container');
    if (!container) {
      container = document.createElement('div');
      container.className = 'notification-container fixed top-4 right-4 z-50';
      document.body.appendChild(container);
    }
    
    // 創建通知元素
    const notification = document.createElement('div');
    notification.className = `notification p-3 mb-2 rounded-lg shadow-md transition-all transform translate-x-0 max-w-sm`;
    
    // 設置不同類型的樣式
    if (type === 'success') {
      notification.classList.add('bg-green-100', 'text-green-800');
    } else if (type === 'error') {
      notification.classList.add('bg-red-100', 'text-red-800');
    } else {
      notification.classList.add('bg-blue-100', 'text-blue-800');
    }
    
    // 設置通知內容
    notification.textContent = message;
    
    // 添加到容器中
    container.appendChild(notification);
    
    // 顯示後淡出
    setTimeout(() => {
      notification.classList.add('opacity-0');
      setTimeout(() => {
        notification.remove();
      }, 300);
    }, 3000);
  }
  
  // 頁面載入時執行
  document.addEventListener('DOMContentLoaded', function() {
    console.log('資料載入器: 頁面載入完成');
    setTimeout(initDataSelector, 500);
  });
  
  // 組件載入後執行
  document.addEventListener('component-loaded', function(e) {
    console.log(`組件載入完成: ${e.detail.componentPath}`);
    
    if (e.detail.componentPath?.includes('ChartContent.html')) {
      setTimeout(initDataSelector, 300);
    }
  });
  
  // 每秒檢查一次，確保資料選擇器存在並已正確初始化
  let checkCounter = 0;
  const intervalId = setInterval(() => {
    const selectors = document.querySelectorAll('.chart-data-selector, #chart-data-selector-component');
    if (selectors.length > 0 || checkCounter > 10) {
      clearInterval(intervalId);
      if (selectors.length > 0) {
        console.log('檢測到資料選擇器，開始初始化');
        initDataSelector();
      }
    }
    checkCounter++;
  }, 1000);
  
  // 註冊新的圖表類型 (提供給外部使用)
  window.registerChartType = function(type, options = {}) {
    if (typeof type !== 'string' || type.trim() === '') {
      console.error('圖表類型必須是有效的字串');
      return false;
    }
    
    // 將圖表類型統一為小寫
    const normalizedType = type.toLowerCase();
    
    // 檢查是否已存在相同的圖表類型
    if (ChartType.isValid(normalizedType)) {
      console.warn(`圖表類型 ${normalizedType} 已經註冊過`);
      return false;
    }
    
    // 註冊新的圖表類型
    ChartType[type.toUpperCase()] = normalizedType;
    
    // 如果提供了元素 ID，則註冊元素映射
    if (options.elementId) {
      ChartElementMap[normalizedType] = options.elementId;
    }
    
    // 如果提供了標題關鍵字，則註冊標題映射
    if (options.titleKeywords && Array.isArray(options.titleKeywords)) {
      ChartTitleMap[normalizedType] = options.titleKeywords;
    }
    
    console.log(`成功註冊新的圖表類型: ${normalizedType}`);
    return true;
  };
  
  // 提供圖表類型枚舉給外部使用
  window.ChartTypes = Object.freeze({...ChartType});
  
  // 記錄所有可用的圖表類型
  console.log('可用圖表類型:', ChartType.getAll());
  
  // 輔助函數：註冊圖表實例，以便後續清理
  window.registerChartInstance = function(elementId, chartInstance) {
    if (!elementId || !chartInstance) return;
    
    const element = document.getElementById(elementId);
    if (!element) return;
    
    // 初始化圖表實例數組
    if (!element.__chartInstances) {
      element.__chartInstances = [];
    }
    
    // 添加新的實例
    element.__chartInstances.push(chartInstance);
    console.log(`已註冊圖表實例到元素 #${elementId}`);
  };
  
  // 輔助函數：清理特定元素的所有圖表實例
  window.cleanupChartInstances = function(elementId) {
    if (!elementId) return;
    
    const element = document.getElementById(elementId);
    if (!element) return;
    
    // 檢查是否有 ApexCharts 實例
    if (element.__chartInstances) {
      // 清理所有實例
      element.__chartInstances.forEach(chart => {
        if (chart && typeof chart.destroy === 'function') {
          try {
            chart.destroy();
            console.log(`已清理圖表實例 (元素: #${elementId})`);
          } catch (err) {
            console.error(`清理圖表實例時出錯: ${err.message}`);
          }
        }
      });
      
      // 重置實例數組
      element.__chartInstances = [];
    }
    
    // 嘗試徹底清除容器內容
    element.innerHTML = '';
  };
  
  // 清除特定類型的所有圖表
  function clearAllChartsForType(chartType) {
    if (!chartType) return;
    
    console.log(`清除所有 ${chartType} 類型的圖表...`);
    
    // 清除主要圖表容器
    const mainChartId = `${chartType}Chart`;
    window.cleanupChartInstances(mainChartId);
    
    // 尋找頁面上可能的其他同類型圖表容器
    const allChartElements = document.querySelectorAll(`[id$="Chart"]`);
    allChartElements.forEach(el => {
      if (el.id !== mainChartId && el.id.toLowerCase().includes(chartType.toLowerCase())) {
        window.cleanupChartInstances(el.id);
      }
    });
    
    // 清除所有相關上下文
    delete window.currentChartData;
    
    console.log(`${chartType} 圖表清除完成`);
  }
})();
