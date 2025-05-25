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
  error: null,
  
  toggleTheme() {
    try {
      this.theme = 'fantasy';
      document.documentElement.setAttribute('data-theme', this.theme);
      localStorage.setItem('theme', this.theme);
    } catch (error) {
      console.error('主題切換失敗:', error);
      this.error = '主題切換失敗';
    }
  },
  
  toggleSidebar() {
    this.sidebarOpen = !this.sidebarOpen;
  },
  
  setCurrentPage(page) {
    try {
      if (!page) throw new Error('頁面名稱不能為空');
      this.currentPage = page;
      loadCurrentPage();
    } catch (error) {
      console.error('頁面切換失敗:', error);
      this.error = '頁面切換失敗';
    }
  },
  
  clearError() {
    this.error = null;
  }
};

// 初始化應用
function initApp() {
  try {
    // 初始化Alpine元件
    Alpine.data('DataSelector', DataSelector);
    
    // 設置初始主題
    document.documentElement.setAttribute(
      'data-theme', 
      window.appData.theme
    );
    
    // 載入對應頁面
    loadCurrentPage();
  } catch (error) {
    console.error('應用初始化失敗:', error);
    window.appData.error = '應用初始化失敗';
  }
}

// 載入當前頁面
function loadCurrentPage() {
  const pageMap = {
    'chart-examples': () => {
      try {
        const chartExamples = new ChartExamples();
        chartExamples.init();
      } catch (error) {
        console.error('圖表頁面載入失敗:', error);
        window.appData.error = '圖表頁面載入失敗';
      }
    },
    'dashboard': () => {
      try {
        console.log('Dashboard page loaded');
        // 實現儀表板頁面邏輯
      } catch (error) {
        console.error('儀表板頁面載入失敗:', error);
        window.appData.error = '儀表板頁面載入失敗';
      }
    },
    'api-docs': () => {
      try {
        console.log('API docs page loaded');
        // 實現 API 文檔頁面邏輯
      } catch (error) {
        console.error('API文檔頁面載入失敗:', error);
        window.appData.error = 'API文檔頁面載入失敗';
      }
    }
  };
  
  const currentPage = window.appData.currentPage;
  if (pageMap[currentPage]) {
    pageMap[currentPage]();
  } else {
    console.error('未知頁面:', currentPage);
    window.appData.error = '未知頁面';
  }
}

// 當 DOM 加載完成後初始化應用
document.addEventListener('DOMContentLoaded', () => {
  try {
    // 啟動 Alpine.js
    window.Alpine = Alpine;
    Alpine.start();
    
    // 初始化應用
    initApp();
  } catch (error) {
    console.error('應用啟動失敗:', error);
    window.appData.error = '應用啟動失敗';
  }
});

// 導出應用初始化函數
export { initApp, loadCurrentPage };