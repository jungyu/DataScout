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
    this.renderExamplesList();
    this.loadDefaultChart();
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
    } catch (error) {
      console.error('載入圖表類型失敗:', error);
    }
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
      'line': '折線圖',
      'area': '區域圖',
      'bar': '條形圖',
      'column': '柱狀圖',
      'scatter': '散點圖',
      'pie': '圓餅圖',
      'donut': '環形圖',
      'radar': '雷達圖',
      'polararea': '極座標圖',
      'candlestick': '蠟燭圖',
      'boxplot': '箱形圖',
      'bubble': '氣泡圖',
      'heatmap': '熱力圖',
      'treemap': '樹狀圖',
      'funnel': '漏斗圖',
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
      'line': 'Line Chart',
      'area': 'Area Chart',
      'bar': 'Bar Chart',
      'column': 'Column Chart',
      'scatter': 'Scatter Chart',
      'pie': 'Pie Chart',
      'donut': 'Donut Chart',
      'radar': 'Radar Chart',
      'polararea': 'Polar Area Chart',
      'candlestick': 'Candlestick Chart',
      'boxplot': 'Box Plot Chart',
      'bubble': 'Bubble Chart',
      'heatmap': 'Heat Map',
      'treemap': 'Tree Map',
      'funnel': 'Funnel Chart',
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
    
    // 創建新的圖表
    this.activeChart = new ApexCharts(chartContainer, options);
    this.activeChart.render();
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
