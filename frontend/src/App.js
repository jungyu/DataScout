   // DataScout 主應用程式
import Alpine from 'alpinejs';
import './styles/main.css';
import { ChartExamples } from './pages/ChartExamples';
import { DataSelector } from './pages/DataSelector';

// 全局數據存儲
window.appData = {
  theme: localStorage.getItem('theme') || 'fantasy',
  sidebarOpen: true,
  currentPage: 'chart-examples',
  toggleTheme() {
    // 由於現在只使用fantasy主題，暫時禁用切換功能
    this.theme = 'fantasy';
    document.documentElement.setAttribute('data-theme', this.theme);
    localStorage.setItem('theme', this.theme);
  },
  toggleSidebar() {
    this.sidebarOpen = !this.sidebarOpen;
  },
  setCurrentPage(page) {
    this.currentPage = page;
    // 這裡可以加入頁面切換邏輯
  }
};

// 初始化應用
function initApp() {
  // 初始化Alpine元件
  Alpine.data('DataSelector', DataSelector);
  
  // 設置初始主題
  document.documentElement.setAttribute(
    'data-theme', 
    window.appData.theme
  );
  
  // 載入對應頁面
  loadCurrentPage();
}

// 載入當前頁面
function loadCurrentPage() {
  const pageMap = {
    'chart-examples': () => {
      const chartExamples = new ChartExamples();
      chartExamples.init();
    },
    'dashboard': () => {
      console.log('Dashboard page loaded');
      // 實現儀表板頁面邏輯
    },
    'api-docs': () => {
      console.log('API docs page loaded');
      // 實現 API 文檔頁面邏輯
    }
  };
  
  const currentPage = window.appData.currentPage;
  if (pageMap[currentPage]) {
    pageMap[currentPage]();
  }
}

// 當 DOM 加載完成後初始化應用
document.addEventListener('DOMContentLoaded', () => {
  // 啟動 Alpine.js
  window.Alpine = Alpine;
  Alpine.start();
  
  // 初始化應用
  initApp();
});

// 導出應用初始化函數
export { initApp, loadCurrentPage };