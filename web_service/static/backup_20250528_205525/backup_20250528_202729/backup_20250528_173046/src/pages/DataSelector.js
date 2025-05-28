// DataScout 資料選擇頁面
import { FileUploader } from '../components/ui/FileUploader';
import { appleStockData, tsmcStockData } from '../data/stockData';
import { bitcoinData } from '../data/cryptoData';

export const DataSelector = () => {
  return {
    ...FileUploader(),
    
    // 初始化時確保 Toggle 按鈕設置為開啟
    init() {
      this.showExamples = true;
      this.isLoading = false;
      console.log('DataSelector initialized with showExamples:', this.showExamples);
      
      // 設置資料載入完成後的事件監聽
      window.addEventListener('data-loaded', (event) => {
        this.handleDataLoaded(event.detail);
      });
      
      // 同步 Toggle 按鈕狀態
      const toggleBtn = document.getElementById('example-data-toggle');
      if (toggleBtn) {
        toggleBtn.checked = this.showExamples;
        
        // 確保 DOM 顯示正確狀態
        const exampleSection = document.getElementById('example-data-section');
        const uploadSection = document.getElementById('file-upload-section');
        
        if (exampleSection && uploadSection) {
          if (this.showExamples) {
            exampleSection.style.display = 'block';
            uploadSection.style.display = 'none';
          } else {
            exampleSection.style.display = 'none';
            uploadSection.style.display = 'block';
          }
        }
      }
      
      // 處理重複的數據項目
      setTimeout(() => {
        this.removeExtraDuplicates();
      }, 100);
    },
    
    // 移除頁面上重複的範例數據項目
    removeExtraDuplicates() {
      const mainContainer = document.querySelector('.col-span-1 .bg-base-100');
      if (mainContainer) {
        // 找出所有範例數據項目
        const allItems = mainContainer.querySelectorAll('.bg-base-200');
        const processedIds = new Set();
        
        if (allItems.length > 0) {
          allItems.forEach((item, index) => {
            const id = item.id;
            if ((id && processedIds.has(id)) || (index >= 3 && !item.closest('#file-upload-section'))) {
              // 如果ID已經處理過或超過前3個項目，且不在檔案上傳區塊內，則移除
              item.remove();
              console.log('移除重複項目:', id || index);
            } else if (id) {
              processedIds.add(id);
            }
          });
        }
      }
    },
    
    // 處理資料載入完成後的操作
    handleDataLoaded(detail) {
      console.log('資料載入完成:', detail);
      
      // 顯示資料載入成功訊息
      const symbol = detail.symbol || '自定義資料';
      this.showDataLoadedToast(symbol);
      
      // 更新圖表 (如果存在)
      this.updateChart();
    },
    
    // 顯示資料載入成功的通知
    showDataLoadedToast(symbol) {
      const toast = document.createElement('div');
      toast.className = 'fixed bottom-4 right-4 bg-success text-white px-4 py-2 rounded shadow-lg z-50';
      toast.innerHTML = `
        <div class="flex items-center">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
          <span>${symbol} 資料已成功載入</span>
        </div>
      `;
      document.body.appendChild(toast);
      
      // 3秒後自動移除
      setTimeout(() => {
        toast.classList.add('fade-out');
        setTimeout(() => {
          document.body.removeChild(toast);
        }, 500);
      }, 3000);
    },
    
    // 更新圖表
    updateChart() {
      // 檢查當前載入的數據
      if (!window.appData || !window.appData.currentDataset) {
        console.error('沒有可用的數據集');
        return;
      }
      
      const dataset = window.appData.currentDataset;
      
      // 檢查是否有K線圖元素
      const candlestickChartEl = document.querySelector('#candlestickChart');
      if (!candlestickChartEl) {
        console.warn('找不到K線圖元素');
        return;
      }
      
      // 清空現有圖表
      candlestickChartEl.innerHTML = '';
      
      // 準備圖表數據
      let chartData = [];
      let chartTitle = '';
      
      if (dataset.type === 'stock' || dataset.type === 'crypto') {
        // 股票或加密貨幣數據通常有 OHLC 格式
        chartData = dataset.data.map(item => ({
          x: new Date(item.date).getTime(),
          y: [item.open, item.high, item.low, item.close]
        }));
        chartTitle = `${dataset.name} ${dataset.type === 'stock' ? '股票' : '加密貨幣'} K線圖`;
      } else if (dataset.type === 'custom') {
        // 自定義數據需要檢查格式並適配
        if (Array.isArray(dataset.data) && dataset.data.length > 0) {
          const firstItem = dataset.data[0];
          
          if ('open' in firstItem && 'high' in firstItem && 'low' in firstItem && 'close' in firstItem) {
            // 假設是 OHLC 格式
            chartData = dataset.data.map(item => ({
              x: new Date(item.date || item.timestamp || Date.now()).getTime(),
              y: [+item.open, +item.high, +item.low, +item.close]
            }));
            chartTitle = `${dataset.name} 資料視覺化`;
          } else if ('value' in firstItem || 'price' in firstItem) {
            // 假設是單一數值的時間序列
            chartData = dataset.data.map(item => ({
              x: new Date(item.date || item.timestamp || Date.now()).getTime(),
              y: [item.value || item.price, item.value || item.price, item.value || item.price, item.value || item.price]
            }));
            chartTitle = `${dataset.name} 資料視覺化`;
          } else {
            console.error('無法識別的數據格式');
            return;
          }
        } else {
          console.error('無效的數據格式或空數據');
          return;
        }
      }
      
      // 建立新圖表
      const options = {
        series: [{
          data: chartData
        }],
        chart: {
          height: 350,
          type: 'candlestick',
        },
        title: {
          text: chartTitle,
          align: 'left'
        },
        xaxis: {
          type: 'datetime',
          labels: {
            formatter: function(val) {
              return new Date(val).toLocaleDateString('zh-TW');
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
              upward: '#22c55e',
              downward: '#ef4444'
            }
          }
        }
      };

      const chart = new ApexCharts(candlestickChartEl, options);
      chart.render();
      
      console.log('圖表已更新:', chartTitle);
    },
    
    // 載入範例資料的方法
    loadAppleData() {
      console.log('Loading Apple stock data');
      window.appData.currentDataset = {
        type: 'stock',
        symbol: 'AAPL',
        name: '蘋果公司',
        data: appleStockData
      };
      // 觸發資料載入事件
      window.dispatchEvent(new CustomEvent('data-loaded', { 
        detail: { datasetType: 'stock', symbol: 'AAPL' } 
      }));
    },
    
    loadTSMCData() {
      console.log('Loading TSMC stock data');
      window.appData.currentDataset = {
        type: 'stock',
        symbol: 'TSM',
        name: '台積電',
        data: tsmcStockData
      };
      // 觸發資料載入事件
      window.dispatchEvent(new CustomEvent('data-loaded', { 
        detail: { datasetType: 'stock', symbol: 'TSM' } 
      }));
    },
    
    loadBitcoinData() {
      console.log('Loading Bitcoin data');
      window.appData.currentDataset = {
        type: 'crypto',
        symbol: 'BTC/USD',
        name: '比特幣/美元',
        data: bitcoinData
      };
      // 觸發資料載入事件
      window.dispatchEvent(new CustomEvent('data-loaded', { 
        detail: { datasetType: 'crypto', symbol: 'BTC/USD' } 
      }));
    }
  };
};
