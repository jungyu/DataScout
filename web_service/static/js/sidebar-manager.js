/**
 * ApexCharts 側邊欄管理模塊
 * 處理側邊欄樣式、交互和狀態管理
 */

class SidebarManager {
  constructor() {
    this.sidebarOpen = true; // 預設為開啟狀態
    this.currentCategory = null;
    this.init();
  }

  /**
   * 初始化側邊欄功能
   */
  init() {
    this.setupSidebarToggle();
    this.setupCategoryToggle();
    this.setupChartTypeSelection();
    this.setupMobileResponsive();
    this.syncStateFromURL();
  }

  /**
   * 設置側邊欄收合切換
   */
  setupSidebarToggle() {
    const toggleBtns = document.querySelectorAll('[data-toggle="sidebar"]');
    if (toggleBtns.length === 0) return;
    
    toggleBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        this.toggleSidebar();
      });
    });
    
    // 檢查本地存儲中的側邊欄狀態
    const savedState = localStorage.getItem('sidebarState');
    if (savedState !== null) {
      this.sidebarOpen = savedState === 'open';
      this.updateSidebarVisibility();
    }
  }

  /**
   * 切換側邊欄開關狀態
   */
  toggleSidebar() {
    this.sidebarOpen = !this.sidebarOpen;
    this.updateSidebarVisibility();
    
    // 保存到本地存儲
    localStorage.setItem('sidebarState', this.sidebarOpen ? 'open' : 'closed');
  }

  /**
   * 更新側邊欄可見性
   */
  updateSidebarVisibility() {
    const sidebar = document.querySelector('.sidebar');
    const contentWrapper = document.querySelector('.flex-1');
    
    if (!sidebar) return;
    
    if (this.sidebarOpen) {
      sidebar.classList.remove('hidden');
      if (contentWrapper) {
        contentWrapper.classList.remove('lg:ml-0');
      }
    } else {
      sidebar.classList.add('hidden');
      if (contentWrapper) {
        contentWrapper.classList.add('lg:ml-0');
      }
    }
    
    // 觸發調整事件以便其他元素響應
    window.dispatchEvent(new Event('resize'));
  }

  /**
   * 設置類別折疊切換
   */
  setupCategoryToggle() {
    // Alpine.js 已經在處理這部分功能
    // 這裡可以添加額外的類別相關邏輯
    
    // 儲存類別的開關狀態
    document.querySelectorAll('.menu-title').forEach(title => {
      title.addEventListener('click', (e) => {
        const categoryName = title.querySelector('span:not(.menu-arrow)').textContent.trim();
        const isOpen = title.getAttribute('aria-expanded') === 'true';
        
        // 保存狀態到本地存儲
        const categoryStates = JSON.parse(localStorage.getItem('categorySates') || '{}');
        categoryStates[categoryName] = !isOpen; // 點擊後狀態會變更
        localStorage.setItem('categorySates', JSON.stringify(categoryStates));
      });
    });
  }

  /**
   * 設置圖表類型選擇
   */
  setupChartTypeSelection() {
    document.querySelectorAll('.chart-type-item').forEach(item => {
      item.addEventListener('click', () => {
        // 移除其他項目的活動狀態
        document.querySelectorAll('.chart-type-item').forEach(i => {
          i.classList.remove('active');
        });
        
        // 設置當前項為活動狀態
        item.classList.add('active');
        
        // 獲取圖表類型
        const chartType = item.getAttribute('data-type');
        
        // 更新 URL 參數
        this.updateURLParameter('type', chartType);
        
        // 在移動設備上點擊後收起側邊欄
        if (window.innerWidth < 1024) {
          this.sidebarOpen = false;
          this.updateSidebarVisibility();
        }
      });
    });
  }

  /**
   * 設置移動設備響應
   */
  setupMobileResponsive() {
    // 監聽視窗大小變化
    window.addEventListener('resize', () => {
      if (window.innerWidth < 768) {
        // 在小屏幕上預設隱藏側邊欄
        this.sidebarOpen = false;
        this.updateSidebarVisibility();
      } else if (window.innerWidth > 1200) {
        // 在大屏幕上預設顯示側邊欄
        this.sidebarOpen = true;
        this.updateSidebarVisibility();
      }
    });
    
    // 初始檢查
    if (window.innerWidth < 768) {
      this.sidebarOpen = false;
      this.updateSidebarVisibility();
    }
  }

  /**
   * 從 URL 同步側邊欄狀態
   */
  syncStateFromURL() {
    const urlParams = new URLSearchParams(window.location.search);
    const chartType = urlParams.get('type');
    
    if (chartType) {
      const targetItem = document.querySelector(`.chart-type-item[data-type="${chartType}"]`);
      if (targetItem) {
        // 更新所有菜單項的狀態
        document.querySelectorAll('.chart-type-item').forEach(item => {
          item.classList.remove('active');
        });
        
        // 設置目標項為活動狀態
        targetItem.classList.add('active');
        
        // 打開包含該項的折疊區域
        const parentSection = targetItem.closest('[x-data]');
        if (parentSection && parentSection.__x) {
          parentSection.__x.$data.open = true;
        }
      }
    }
  }

  /**
   * 更新 URL 參數
   * @param {string} key 參數名
   * @param {string} value 參數值
   */
  updateURLParameter(key, value) {
    const url = new URL(window.location.href);
    url.searchParams.set(key, value);
    window.history.replaceState({}, '', url.toString());
  }
}

// 當文檔載入完成時初始化
document.addEventListener('DOMContentLoaded', function() {
  // 創建側邊欄管理器實例
  window.sidebarManager = new SidebarManager();
});
