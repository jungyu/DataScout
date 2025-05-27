/**
 * 組件加載工具
 * 用於動態載入HTML組件到指定位置
 */

document.addEventListener('DOMContentLoaded', function() {
  // 載入所有標記為需要載入組件的容器
  const componentContainers = document.querySelectorAll('[data-component]');
  
  // 遍歷每個容器並載入對應組件
  componentContainers.forEach(container => {
    const componentPath = container.getAttribute('data-component');
    loadComponent(container, componentPath);
  });
  
  // 初始化主題切換
  initThemeToggle();

  // 初始化頁面導航
  initPageNavigation();
  
  // 支持側邊欄激活器
  if (typeof activateSidebar === 'function') {
    setTimeout(activateSidebar, 500);
  }
});

/**
 * 載入HTML組件到指定容器
 * @param {HTMLElement} container - 目標容器元素
 * @param {string} componentPath - 組件路徑
 */
function loadComponent(container, componentPath) {
  // 設置一個加載中的指示
  container.innerHTML = '<div class="p-4 text-gray-500">Loading component...</div>';
  
  // 給容器添加一個唯一ID，如果它還沒有
  if (!container.id) {
    container.id = 'component-' + Date.now() + '-' + Math.floor(Math.random() * 1000);
  }
  
  // 給容器添加 data-component-path 屬性，以便於調試
  container.setAttribute('data-component-path', componentPath);
  
  fetch(componentPath)
    .then(response => {
      if (!response.ok) {
        throw new Error(`Failed to load component: ${componentPath}`);
      }
      return response.text();
    })
    .then(html => {
      // 清空容器
      container.innerHTML = html;
      
      // 等待DOM更新和腳本執行
      setTimeout(() => {
        // 觸發組件載入完成事件
        const event = new CustomEvent('component-loaded', { 
          detail: { 
            container: container,
            componentPath: componentPath,
            containerId: container.id
          }
        });
        document.dispatchEvent(event);
        console.log(`組件已載入: ${componentPath} 到 #${container.id}`);
      }, 50);
    })
    .catch(error => {
      console.error(`Error loading component ${componentPath}:`, error);
      container.innerHTML = `<div class="p-4 text-red-500">Failed to load component: ${componentPath}</div>`;
    });
}

/**
 * 初始化主題切換功能
 */
function initThemeToggle() {
  const themeToggleBtn = document.getElementById('theme-toggle');
  if (!themeToggleBtn) return;
  
  // 檢查localStorage中是否有保存的主題
  const savedTheme = localStorage.getItem('theme') || 'light';
  document.documentElement.setAttribute('data-theme', savedTheme);
  
  // 更新按鈕狀態
  if (savedTheme === 'dark') {
    themeToggleBtn.classList.add('swap-active');
  }
  
  // 綁定點擊事件
  themeToggleBtn.addEventListener('click', function() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    // 更新主題
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    
    // 更新按鈕狀態
    themeToggleBtn.classList.toggle('swap-active');
  });
}

/**
 * 初始化頁面導航
 * 根據當前頁面路徑高亮對應的導航項目
 */
function initPageNavigation() {
  document.addEventListener('component-loaded', function(e) {
    // 處理側邊欄導航高亮
    if (e.detail.componentPath === 'components/layout/Sidebar.html') {
      const currentPath = window.location.pathname;
      const sidebarLinks = document.querySelectorAll('#sidebar a[href]');
      
      sidebarLinks.forEach(link => {
        const linkHref = link.getAttribute('href');
        if (currentPath === linkHref || 
           (currentPath.endsWith('/index.html') && linkHref === '/') || 
           (currentPath === '/' && linkHref === '/index.html')) {
          link.classList.add('bg-accent', 'text-white');
          link.classList.remove('text-primary-content/80');
        } else {
          link.classList.remove('bg-accent', 'text-white');
          link.classList.add('text-primary-content/80');
        }
      });
    }
    
    // 處理頂部導航高亮
    if (e.detail.componentPath === 'components/layout/Topbar.html') {
      const currentPath = window.location.pathname;
      
      // 默認活躍的頂部導航
      let activeNavId = 'nav-charts';
      
      // 移除所有頂部導航的活躍狀態
      const navLinks = document.querySelectorAll('header a[id^="nav-"]');
      navLinks.forEach(link => {
        link.classList.remove('text-accent', 'font-bold', 'border-b-2', 'border-accent');
        link.classList.add('text-base-content/80', 'font-medium');
      });
      
      // 設置當前頁面的高亮狀態
      const activeLink = document.getElementById(activeNavId);
      if (activeLink) {
        activeLink.classList.remove('text-base-content/80', 'font-medium');
        activeLink.classList.add('text-accent', 'font-bold', 'border-b-2', 'border-accent');
      }
    }
    
    if (e.detail.componentPath === 'components/layout/Sidebar.html') {
      const currentPath = window.location.pathname;
      
      // 高亮當前頁面的側邊欄連結
      const sidebarLinks = document.querySelectorAll('#sidebar a[href]');
      sidebarLinks.forEach(link => {
        const linkPath = link.getAttribute('href');
        if (linkPath === currentPath) {
          link.classList.add('bg-accent', 'text-white');
        } else {
          link.classList.remove('bg-accent', 'text-white');
        }
      });
    }
  });
}

// 對外公開的API
window.ComponentLoader = {
  load: loadComponent
};
