/**
 * DataScout Chart App - 主入口檔案
 * 
 * 這個檔案負責初始化應用程式，導入必要的依賴和模組。
 * 使用 Alpine.js 處理 DOM 交互，ApexCharts 繪製圖表。
 */

// 引入樣式
import '../css/main.css';

// 引入 Alpine.js
import Alpine from 'alpinejs';

// 引入組件
import { initDashboard } from './components/dashboard';
import { initChartWidgets } from './components/chart-widget';
import { initDataTable } from './components/data-table';

// 引入共享組件
import { initStatCards } from './components/shared/stat-card';
import { initDataLoader } from './components/shared/data-loader';
import { initAdvancedCharts } from './components/shared/advanced-chart';

// 引入服務
import { apiService } from './services/api';
import { chartConfig } from './services/chart-config';

// 註冊全域組件
window.Alpine = Alpine;
window.apiService = apiService;
window.chartConfig = chartConfig;

// 初始化 Alpine.js 資料和組件
document.addEventListener('alpine:init', () => {
  // 註冊 dashboard 組件
  initDashboard();
  
  // 註冊圖表小組件
  initChartWidgets();
  
  // 註冊資料表格組件
  initDataTable();
  
  // 註冊共享組件
  initStatCards();
  initDataLoader();
  initAdvancedCharts();
  
  // 全域應用狀態
  Alpine.store('app', {
    darkMode: localStorage.getItem('darkMode') === 'true',
    sidebarOpen: true,
    
    // 主題切換方法
    toggleDarkMode() {
      this.darkMode = !this.darkMode;
      localStorage.setItem('darkMode', this.darkMode);
      document.documentElement.setAttribute('data-theme', this.darkMode ? 'dark' : 'light');
    },
    
    // 側邊欄切換方法
    toggleSidebar() {
      this.sidebarOpen = !this.sidebarOpen;
    }
  });
});

// 初始主題設定
document.addEventListener('DOMContentLoaded', () => {
  const darkMode = localStorage.getItem('darkMode') === 'true';
  document.documentElement.setAttribute('data-theme', darkMode ? 'dark' : 'light');
});

// 啟動 Alpine.js
Alpine.start();
