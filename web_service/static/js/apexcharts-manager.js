/**
 * ApexCharts 管理模塊
 * 用於處理圖表載入、渲染和交互功能
 */

class ApexChartsManager {
  constructor() {
    this.activeChart = null;
    this.examples = [];
    this.chartTypes = [];
    this.currentType = 'candlestick';
    this.init();
  }

  /**
   * 初始化
   */
  async init() {
    await this.loadExamples();
    await this.loadChartTypes();
    this.setupEventListeners();
    this.setupSidebarBehavior();
    this.renderExamplesList();
    this.loadDefaultChart();
  }
  
  /**
   * 設置側邊欄行為
   * - 添加響應式布局支持
   * - 處理側邊欄與圖表類型選擇
   */
  setupSidebarBehavior() {
    // 當用戶選擇一個圖表類型時的處理邏輯
    document.querySelectorAll('.chart-type-item').forEach(item => {
      item.addEventListener('click', () => {
        // 選擇圖表時的邏輯在 selectChartType 方法中實現
      });
    });
  }

  /**
   * 載入圖表範例列表
   */
  async loadExamples() {
    try {
      const response = await fetch('/api/apexcharts/examples');
      const data = await response.json();
      this.examples = data.examples || [];
    } catch (error) {
      console.error('載入範例失敗:', error);
    }
  }

  /**
   * 載入所有圖表類型
   */
  async loadChartTypes() {
    try {
      const response = await fetch('/api/apexcharts/types');
      const data = await response.json();
      this.chartTypes = data.types || [];
      
      // 如果API沒有返回圖表類型或返回的數組為空，使用默認圖表類型列表
      if (!this.chartTypes.length) {
        this.chartTypes = this.getDefaultChartTypes();
      }
    } catch (error) {
      console.error('載入圖表類型失敗:', error);
      // API 請求失敗時使用默認圖表類型列表
      this.chartTypes = this.getDefaultChartTypes();
    }
  }
  
  /**
   * 獲取默認圖表類型列表
   * @returns {string[]} 圖表類型數組
   */
  getDefaultChartTypes() {
    return [
      // 基本圖表類型
      'line', 'area', 'bar', 'barHorizontal', 'scatter', 
      'pie', 'donut', 'radar', 'heatmap', 'treemap',
      
      // 進階圖表類型
      'candlestick', 'boxPlot', 'rangeBar', 'bubble', 
      'rangeArea', 'polarArea', 'radialBar', 'funnel',
      
      // 時間序列與監控圖表
      'timeSeries', 'timeSeriesArea', 'syncCharts', 'stepline', 'mixedTime',
      
      // 比較與分析圖表
      'groupedBar', 'stackedBar', 'percentStackedBar', 'mixedChart',
      'candlestickVolume', 'heatmapLine', 'multiYAxis', 'technicalChart',
      
      // 動態更新圖表
      'realtimeLine', 'realtimeDashboard', 'dynamicPie', 'streamingLine'
    ];
  }

  /**
   * 設置事件監聽器
   */
  setupEventListeners() {
    // 當點擊載入資料按鈕時
    document.querySelectorAll('.load-example').forEach(button => {
      button.addEventListener('click', (e) => {
        const exampleId = e.currentTarget.dataset.id;
        this.loadChartExample(exampleId);
      });
    });

    // 匯出按鈕
    document.getElementById('exportPNG')?.addEventListener('click', () => this.exportChart('png'));
    document.getElementById('exportSVG')?.addEventListener('click', () => this.exportChart('svg'));

    // 側邊欄圖表類型選擇
    document.querySelectorAll('.chart-type-item').forEach(item => {
      item.addEventListener('click', (e) => {
        e.preventDefault();
        const chartType = e.currentTarget.dataset.type;
        this.selectChartType(chartType);
      });
    });
  }

  /**
   * 渲染範例列表
   */
  renderExamplesList() {
    const container = document.getElementById('examples-list');
    if (!container) return;

    // 過濾當前選中類型的範例
    const filteredExamples = this.examples.filter(ex => ex.type === this.currentType);
    
    container.innerHTML = '';
    
    if (filteredExamples.length === 0) {
      container.innerHTML = '<div class="alert alert-info">目前沒有此類型的範例資料</div>';
      return;
    }

    filteredExamples.forEach(example => {
      const card = document.createElement('div');
      card.className = 'card bg-base-100 shadow border mb-4';
      card.innerHTML = `
        <div class="card-body p-4">
          <h4 class="card-title text-base">${example.description} ${example.type}</h4>
          <p class="text-sm">ApexCharts ${example.type} 圖表範例</p>
          <button class="btn btn-sm btn-primary mt-2 load-example" data-id="${example.id}">載入資料</button>
        </div>
      `;
      container.appendChild(card);
    });

    // 重新綁定按鈕事件
    this.setupEventListeners();
  }

  /**
   * 選擇圖表類型
   * @param {string} type 
   */
  selectChartType(type) {
    if (!this.chartTypes.includes(type)) return;
    
    this.currentType = type;
    
    // 更新側邊欄選中狀態
    document.querySelectorAll('.chart-type-item').forEach(item => {
      const isActive = item.dataset.type === type;
      if (isActive) {
        item.classList.add('active');
        
        // 檢查該元素是否在 Alpine.js 管理的折疊區域中
        const parentSection = item.closest('[x-data]');
        if (parentSection && parentSection.__x) {
          // 確保折疊區域展開
          parentSection.__x.$data.open = true;
        }
      } else {
        item.classList.remove('active');
      }
    });
    
    // 更新頁面標題
    const chartTitle = document.getElementById('chart-type-title');
    if (chartTitle) {
      const displayName = this.getDisplayName(type);
      chartTitle.textContent = `${displayName} (${this.getEnglishName(type)})`;
    }
    
    // 重新渲染範例列表
    this.renderExamplesList();
  }

  /**
   * 獲取圖表類型的顯示名稱
   * @param {string} type 
   * @returns {string}
   */
  getDisplayName(type) {
    const nameMap = {
      // 基本圖表類型
      'line': '折線圖',
      'area': '區域圖',
      'bar': '柱狀圖',
      'barHorizontal': '條形圖',
      'scatter': '散點圖',
      'pie': '圓餅圖',
      'donut': '環形圖',
      'radar': '雷達圖',
      'heatmap': '熱圖',
      'treemap': '樹狀圖',
      
      // 進階圖表類型
      'candlestick': '蠟燭圖',
      'boxPlot': '箱形圖',
      'rangeBar': '範圍條形圖',
      'bubble': '氣泡圖',
      'rangeArea': '範圍區域圖',
      'polarArea': '極座標圖',
      'radialBar': '徑向條/圓形量規',
      'funnel': '漏斗圖',
      
      // 時間序列與監控圖表
      'timeSeries': '時間序列線圖',
      'timeSeriesArea': '時間序列區域圖',
      'syncCharts': '同步圖表',
      'stepline': '階梯圖',
      'mixedTime': '混合時間圖表',
      
      // 比較與分析圖表
      'groupedBar': '分組柱狀圖',
      'stackedBar': '堆疊柱狀圖',
      'percentStackedBar': '百分比堆疊柱狀圖',
      'mixedChart': '混合圖表',
      'candlestickVolume': '股票K線+成交量',
      'heatmapLine': '熱力圖+折線圖',
      'multiYAxis': '多重Y軸混合圖表',
      'technicalChart': '價格走勢與技術指標',
      
      // 動態更新圖表
      'realtimeLine': '實時折線圖',
      'realtimeDashboard': '實時儀表板',
      'dynamicPie': '動態餅圖',
      'streamingLine': '串流資料折線圖',
      
      // 舊版/相容性 
      'column': '柱狀圖',
      'polararea': '極座標圖',
      'mixed': '混合圖',
      'timeline': '時間軸圖',
      'grouped_bar': '分組柱狀圖',
      'stacked_bar': '堆疊柱狀圖',
      'percentage_stack': '百分比堆疊圖',
      'timeseries_line': '時間序列線圖',
      'timeseries_area': '時間序列區域圖',
      'realtime': '即時監控圖'
    };
    
    return nameMap[type] || type;
  }

  /**
   * 獲取圖表類型的英文名稱
   * @param {string} type 
   * @returns {string}
   */
  getEnglishName(type) {
    const nameMap = {
      // 基本圖表類型
      'line': 'Line Chart',
      'area': 'Area Chart',
      'bar': 'Column Chart',
      'barHorizontal': 'Bar Chart',
      'scatter': 'Scatter Chart',
      'pie': 'Pie Chart',
      'donut': 'Donut Chart',
      'radar': 'Radar Chart',
      'heatmap': 'Heat Map',
      'treemap': 'Tree Map',
      
      // 進階圖表類型
      'candlestick': 'Candlestick Chart',
      'boxPlot': 'Box Plot Chart',
      'rangeBar': 'Range Bar Chart',
      'bubble': 'Bubble Chart',
      'rangeArea': 'Range Area Chart',
      'polarArea': 'Polar Area Chart',
      'radialBar': 'RadialBar/Circular Gauge',
      'funnel': 'Funnel Chart',
      
      // 時間序列與監控圖表
      'timeSeries': 'Time Series Line Chart',
      'timeSeriesArea': 'Time Series Area Chart',
      'syncCharts': 'Synchronized Charts',
      'stepline': 'Stepline Chart',
      'mixedTime': 'Mixed Time Chart',
      
      // 比較與分析圖表
      'groupedBar': 'Grouped Bar Chart',
      'stackedBar': 'Stacked Bar Chart',
      'percentStackedBar': 'Percentage Stacked Bar Chart',
      'mixedChart': 'Mixed Chart',
      'candlestickVolume': 'Candlestick with Volume',
      'heatmapLine': 'Heatmap with Line',
      'multiYAxis': 'Multi Y-Axis Chart',
      'technicalChart': 'Technical Analysis Chart',
      
      // 動態更新圖表
      'realtimeLine': 'Realtime Line Chart',
      'realtimeDashboard': 'Realtime Dashboard',
      'dynamicPie': 'Dynamic Pie Chart',
      'streamingLine': 'Streaming Data Chart',
      
      // 舊版/相容性
      'column': 'Column Chart',
      'polararea': 'Polar Area Chart',
      'mixed': 'Mixed Chart',
      'timeline': 'Timeline Chart',
      'grouped_bar': 'Grouped Bar Chart',
      'stacked_bar': 'Stacked Bar Chart',
      'percentage_stack': 'Percentage Stack Chart',
      'timeseries_line': 'Time Series Line Chart',
      'timeseries_area': 'Time Series Area Chart',
      'realtime': 'Real-time Chart'
    };
    
    return nameMap[type] || type;
  }

  /**
   * 載入預設圖表
   */
  loadDefaultChart() {
    // 預設載入蠟燭圖
    const candlestickExample = this.examples.find(ex => ex.type === 'candlestick');
    if (candlestickExample) {
      this.loadChartExample(candlestickExample.id);
    } else {
      // 如果沒有蠟燭圖範例，使用預設數據
      this.renderDefaultCandlestickChart();
    }
  }

  /**
   * 載入特定的圖表範例
   * @param {string} exampleId 
   */
  async loadChartExample(exampleId) {
    try {
      const response = await fetch(`/api/apexcharts/example/${exampleId}`);
      const data = await response.json();
      
      if (!data || !data.data) {
        throw new Error('範例數據無效');
      }
      
      const chartOptions = data.data;
      this.renderChart(chartOptions);
      
      // 更新當前圖表類型
      const example = this.examples.find(ex => ex.id === exampleId);
      if (example) {
        this.currentType = example.type;
        this.selectChartType(example.type);
      }
    } catch (error) {
      console.error('載入圖表範例失敗:', error);
    }
  }

  /**
   * 渲染預設蠟燭圖
   */
  renderDefaultCandlestickChart() {
    const defaultOptions = {
      series: [{
        data: [
          { x: new Date('2024-05-01').getTime(), y: [6560, 6650, 6550, 6600] },
          { x: new Date('2024-05-02').getTime(), y: [6600, 6700, 6580, 6640] },
          { x: new Date('2024-05-03').getTime(), y: [6640, 6680, 6620, 6630] },
          { x: new Date('2024-05-06').getTime(), y: [6630, 6780, 6630, 6750] },
          { x: new Date('2024-05-07').getTime(), y: [6750, 6780, 6700, 6740] },
          { x: new Date('2024-05-08').getTime(), y: [6740, 6750, 6620, 6650] },
          { x: new Date('2024-05-09').getTime(), y: [6650, 6700, 6590, 6600] },
          { x: new Date('2024-05-10').getTime(), y: [6600, 6600, 6550, 6580] },
          { x: new Date('2024-05-11').getTime(), y: [6580, 6600, 6550, 6560] },
          { x: new Date('2024-05-12').getTime(), y: [6560, 6620, 6560, 6610] }
        ]
      }],
      chart: {
        type: 'candlestick',
        height: 380,
        toolbar: {
          show: true
        }
      },
      annotations: {
        xaxis: [
          {
            x: new Date('2024-05-06').getTime(),
            borderColor: '#775DD0',
            label: {
              text: '關鍵日期'
            }
          }
        ]
      },
      xaxis: {
        type: 'datetime',
        labels: {
          formatter: function(val) {
            return new Date(val).toLocaleDateString('zh-TW', {month: 'short', day: 'numeric'});
          }
        }
      },
      yaxis: {
        tooltip: {
          enabled: true
        }
      },
      plotOptions: {
        candlestick: {
          colors: {
            upward: '#26a69a',
            downward: '#ef5350'
          }
        }
      }
    };
    
    this.renderChart(defaultOptions);
  }

  /**
   * 渲染圖表
   * @param {Object} options ApexCharts 選項
   */
  renderChart(options) {
    const chartContainer = document.getElementById('chart-container');
    if (!chartContainer) return;
    
    // 清空容器
    chartContainer.innerHTML = '';
    
    // 銷毀現有圖表
    if (this.activeChart) {
      this.activeChart.destroy();
      this.activeChart = null;
    }
    
    // 應用可能的圖表類型特定增強
    const enhancedOptions = this.enhanceChartOptions(options);
    
    // 創建新的圖表
    this.activeChart = new ApexCharts(chartContainer, enhancedOptions);
    this.activeChart.render();
  }
  
  /**
   * 根據圖表類型增強/調整選項
   * @param {Object} options 原始選項
   * @returns {Object} 增強後的選項
   */
  enhanceChartOptions(options) {
    // 複製選項以避免修改原始對象
    const enhancedOptions = JSON.parse(JSON.stringify(options));
    const chartType = enhancedOptions.chart?.type || 'line';
    
    // 根據圖表類型應用特定增強
    switch (chartType) {
      case 'rangeBar':
        // 確保範圍條形圖有正確的水平設置
        if (!enhancedOptions.plotOptions) enhancedOptions.plotOptions = {};
        if (!enhancedOptions.plotOptions.bar) enhancedOptions.plotOptions.bar = {};
        enhancedOptions.plotOptions.bar.horizontal = true;
        break;
        
      case 'rangeArea':
        // 確保範圍區域圖有正確的填充設置
        if (!enhancedOptions.fill) enhancedOptions.fill = {};
        enhancedOptions.fill.type = 'solid';
        break;
        
      case 'stepline':
        // 確保階梯圖有正確的曲線類型
        if (!enhancedOptions.stroke) enhancedOptions.stroke = {};
        enhancedOptions.stroke.curve = 'stepline';
        break;
        
      case 'syncCharts':
        // 同步圖表需要特殊處理，目前我們僅顯示警告
        console.warn('同步圖表需要多個圖表實例，請參考文檔實現。');
        break;
        
      case 'mixedChart':
      case 'mixedTime':
        // 確保對於混合圖表，每個數據系列都有正確的類型
        if (enhancedOptions.series && Array.isArray(enhancedOptions.series)) {
          enhancedOptions.series.forEach(s => {
            if (!s.type) s.type = 'line'; // 默認類型
          });
        }
        break;
    }
    
    return enhancedOptions;
  }

  /**
   * 匯出圖表
   * @param {string} format 'png' 或 'svg'
   */
  exportChart(format) {
    if (!this.activeChart) return;
    
    if (format === 'png') {
      this.activeChart.exportToImage('png').then(function(dataUrl) {
        const link = document.createElement('a');
        link.href = dataUrl;
        link.download = `ApexCharts_${new Date().getTime()}.png`;
        link.click();
      });
    } else {
      this.activeChart.exportToSVG().then(function(dataUrl) {
        const link = document.createElement('a');
        link.href = dataUrl;
        link.download = `ApexCharts_${new Date().getTime()}.svg`;
        link.click();
      });
    }
  }
}

// 當頁面加載完成時初始化
document.addEventListener('DOMContentLoaded', () => {
  window.apexChartsManager = new ApexChartsManager();
});
