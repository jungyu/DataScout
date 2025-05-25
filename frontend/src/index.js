   // DataScout 主要應用程式

import './styles/main.css';
import './index.css';
import Alpine from 'alpinejs';
import ApexCharts from 'apexcharts';
import { DataSelector } from './pages/DataSelector';

// 創建全局變數
window.appData = { currentDataset: null };

// 全局註冊 Alpine
window.Alpine = Alpine;

// 註冊 Alpine 元件
Alpine.data('DataSelector', DataSelector);

// 調試開關
console.log('註冊 DataSelector 元件');

// 啟動 Alpine
Alpine.start();

// 添加調試日誌
console.log('Alpine.js 已啟動');

// DOM 載入完成後，載入資料選擇器元件
document.addEventListener('DOMContentLoaded', function() {
  // 載入資料選擇器元件內容
  fetch('./components/ui/DataSelector.html')
    .then(response => {
      if (!response.ok) {
        throw new Error(`無法載入資料選擇器元件: ${response.status} ${response.statusText}`);
      }
      return response.text();
    })
    .then(html => {
      const selectorEl = document.getElementById('data-selector');
      if (selectorEl) {
        selectorEl.innerHTML = html;
        console.log('資料選擇器元件已載入成功');
        
        // 初始化全局數據對象，如果尚未定義
        if (!window.appData) {
          window.appData = { currentDataset: null };
        }
      } else {
        console.error('找不到 data-selector 元素');
      }
    })
    .catch(err => console.error('無法載入資料選擇器元件:', err));
});

// 圖表初始化函數
function initCandlestickChart() {
  const options = {
    series: [{
      data: [
        {x: new Date(1677630000000), y: [6660.00, 6680.00, 6640.00, 6660.00]},
        {x: new Date(1677633600000), y: [6660.00, 6625.00, 6610.00, 6620.00]},
        {x: new Date(1677637200000), y: [6618.00, 6630.00, 6615.00, 6621.00]},
        {x: new Date(1677640800000), y: [6621.00, 6640.00, 6620.00, 6635.00]},
        {x: new Date(1677644400000), y: [6635.00, 6645.00, 6630.00, 6640.00]},
        {x: new Date(1677648000000), y: [6645.00, 6660.00, 6635.00, 6648.00]},
        {x: new Date(1677651600000), y: [6650.00, 6600.00, 6580.00, 6590.00]},
        {x: new Date(1677655200000), y: [6590.00, 6605.00, 6580.00, 6600.00]},
        {x: new Date(1677658800000), y: [6600.00, 6650.00, 6585.00, 6590.00]},
        {x: new Date(1677662400000), y: [6590.00, 6650.00, 6580.00, 6590.00]}
      ]
    }],
    chart: {
      height: 350,
      type: 'candlestick',
    },
    title: {
      text: 'BTC/USD 小時K線圖',
      align: 'left'
    },
    annotations: {
      xaxis: [
        {
          x: new Date(1677648000000).getTime(),
          borderColor: '#999',
          label: {
            borderColor: '#999',
            style: {
              color: '#fff',
              background: '#999',
            },
            text: '下跌點',
          }
        }
      ]
    },
    tooltip: {
      enabled: true,
    },
    xaxis: {
      type: 'datetime',
      labels: {
        formatter: function(val) {
          return new Date(val).toLocaleTimeString('zh-TW', {hour: '2-digit', minute:'2-digit'});
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

  const chart = new ApexCharts(document.querySelector("#candlestickChart"), options);
  chart.render();
}

// 頁面載入完成後初始化
document.addEventListener('DOMContentLoaded', () => {
  // 初始化圖表
  initCandlestickChart();
});

// 導出函數供其他模組使用
export { initCandlestickChart };