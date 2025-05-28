   import { CandlestickChart } from '../components/charts/CandlestickChart';
import { 
  appleStockData, 
  tsmcStockData, 
  btcUsdData, 
  formatDataForCandlestick 
} from '../data/stockData';
import { formatCryptoCandlestickData } from '../data/cryptoData';
import { formatTime, convertToOHLC } from '../utils/chartHelpers';

// 圖表範例頁面類
export class ChartExamples {
  constructor() {
    this.charts = {};
    this.activeDataSource = 'btc';
    this.dataMap = {
      aapl: {
        title: 'AAPL 蘋果公司股票',
        data: appleStockData,
        format: (data) => {
          return convertToOHLC(data, 'date', 'open', 'high', 'low', 'close');
        }
      },
      tsmc: {
        title: 'TSMC 台積電股票',
        data: tsmcStockData,
        format: (data) => {
          return convertToOHLC(data, 'date', 'open', 'high', 'low', 'close');
        }
      },
      btc: {
        title: 'BTC/USD 比特幣對美元',
        data: btcUsdData,
        format: (data) => {
          return convertToOHLC(data, 'date', 'open', 'high', 'low', 'close');
        }
      }
    };
    
    // Alpine.js 數據綁定
    window.chartExamplesData = {
      activeData: this.activeDataSource,
      changeDataSource: (source) => this.changeDataSource(source)
    };
  }

  // 初始化頁面
  init() {
    this.initCandlestickChart();
    this.setupEventListeners();
  }
  
  // 初始化蠟燭圖
  initCandlestickChart() {
    const dataSource = this.dataMap[this.activeDataSource];
    const chartData = dataSource.format(dataSource.data);
    
    this.charts.candlestick = new CandlestickChart('candlestickChart', chartData, {
      title: dataSource.title,
      seriesName: '價格'
    });
    this.charts.candlestick.init();
  }
  
  // 切換數據源
  changeDataSource(source) {
    if (!this.dataMap[source]) return;
    
    this.activeDataSource = source;
    const dataSource = this.dataMap[source];
    const chartData = dataSource.format(dataSource.data);
    
    if (this.charts.candlestick) {
      this.charts.candlestick.updateData(chartData);
      // 更新標題
      document.querySelector('#chartTitle').textContent = dataSource.title;
    }
  }
  
  // 設置事件監聽器
  setupEventListeners() {
    // AAPL 數據載入按鈕
    document.querySelector('#loadApple').addEventListener('click', () => {
      this.changeDataSource('aapl');
    });
    
    // TSMC 數據載入按鈕
    document.querySelector('#loadTSMC').addEventListener('click', () => {
      this.changeDataSource('tsmc');
    });
    
    // BTC/USD 數據載入按鈕
    document.querySelector('#loadBTC').addEventListener('click', () => {
      this.changeDataSource('btc');
    });
    
    // 導出 PNG 按鈕
    document.querySelector('#exportPNG').addEventListener('click', () => {
      if (this.charts.candlestick) {
        this.charts.candlestick.exportToPNG();
      }
    });
    
    // 導出 SVG 按鈕
    document.querySelector('#exportSVG').addEventListener('click', () => {
      if (this.charts.candlestick) {
        this.charts.candlestick.exportToSVG();
      }
    });
  }
}

// 頁面載入時初始化
document.addEventListener('DOMContentLoaded', () => {
  const chartExamples = new ChartExamples();
  chartExamples.init();
});