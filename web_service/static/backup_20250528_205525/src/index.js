// DataScout 主要應用程式
import './styles/main.css';
import './index.css';
import ApexCharts from 'apexcharts';
// 導入組件載入器
import { initComponentLoader } from './component-loader.js';

// 檢查是否需要導向到 line.html
function checkAndRedirectToLine() {
  // 只在首頁時導向，避免其他頁面被重定向
  if (window.location.pathname === '/' || window.location.pathname === '/index.html') {
    console.log('首頁訪問，自動導向 line.html');
    
    // 根據環境決定重定向目標
    const isDevelopment = ['5173', '5174', '5175', '5176', '5177', '3000', '8080'].includes(window.location.port);
    const targetUrl = isDevelopment ? '/line.html' : '/static/line.html';
    
    console.log(`重定向目標: ${targetUrl} (環境: ${isDevelopment ? '開發' : '生產'})`);
    window.location.href = targetUrl;
    return true;
  }
  return false;
}

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

// 側邊欄切換功能
function initSidebarToggle() {
  const sidebarToggle = document.getElementById('sidebar-toggle');
  const sidebar = document.getElementById('sidebar');
  
  if (sidebarToggle && sidebar) {
    sidebarToggle.addEventListener('click', () => {
      sidebar.classList.toggle('w-64');
      sidebar.classList.toggle('w-0');
    });
  }
}

// 頁面載入完成後初始化
document.addEventListener('DOMContentLoaded', () => {
  // 暫時禁用重定向，使用 Alpine.js 架構
  console.log('初始化 Alpine.js 架構 (已禁用重定向到 line.html)');
  
  // 先初始化組件載入器
  initComponentLoader();
  
  // 延遲初始化圖表和其他功能，確保組件已載入
  setTimeout(() => {
    // 初始化圖表
    initCandlestickChart();
    // 初始化側邊欄切換
    initSidebarToggle();
  }, 500);
});