/**
 * 圖表快速導航工具
 * 為用戶提供在各種圖表之間快速切換的能力
 */

(function() {
  console.log('圖表快速導航工具已載入');

  // 定義所有可用的圖表類型
  const chartTypes = [
    { id: 'candlestick', name: '蠟燭圖', file: 'index.html', icon: 'trending-up' },
    { id: 'line', name: '折線圖', file: 'line.html', icon: 'activity' },
    { id: 'area', name: '面積圖', file: 'area.html', icon: 'trending-up' },
    { id: 'bar', name: '條形圖', file: 'bar.html', icon: 'bar-chart-2' },
    { id: 'column', name: '柱狀圖', file: 'column.html', icon: 'bar-chart' },
    { id: 'pie', name: '圓餅圖', file: 'pie.html', icon: 'pie-chart' },
    { id: 'donut', name: '甜甜圈圖', file: 'donut.html', icon: 'circle' },
    { id: 'radar', name: '雷達圖', file: 'radar.html', icon: 'compass' },
    { id: 'polararea', name: '極區域圖', file: 'polararea.html', icon: 'radio' },
    { id: 'heatmap', name: '熱力圖', file: 'heatmap.html', icon: 'grid' },
    { id: 'treemap', name: '樹狀圖', file: 'treemap.html', icon: 'layers' },
    { id: 'scatter', name: '散點圖', file: 'scatter.html', icon: 'scatter-plot' },
    { id: 'mixed', name: '混合圖', file: 'mixed.html', icon: 'sliders' }
  ];

  // 創建導航器UI
  function createNavigator() {
    // 檢查DOM是否可用
    if (typeof document === 'undefined') {
      return;
    }

    // 創建導航器容器
    const nav = document.createElement('div');
    nav.className = 'fixed bottom-20 right-4 bg-base-100 rounded-lg shadow-xl p-2 border border-base-300 z-40 chart-quick-nav';
    nav.id = 'chart-quick-nav';
    nav.style.maxHeight = '70vh';
    nav.style.overflow = 'auto';

    // 添加標題
    const title = document.createElement('div');
    title.className = 'p-2 font-medium text-base-content border-b border-base-200 flex justify-between items-center';
    title.innerHTML = `
      <span class="flex items-center">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
        </svg>
        圖表導航
      </span>
      <button id="chart-nav-close" class="text-base-content/70 hover:text-base-content">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    `;
    nav.appendChild(title);

    // 添加圖表類型列表
    const list = document.createElement('ul');
    list.className = 'menu menu-compact';

    // 確定當前頁面
    const currentPath = window.location.pathname;
    let currentFile = currentPath.substring(currentPath.lastIndexOf('/') + 1) || 'index.html';

    // 添加每個圖表選項
    chartTypes.forEach(chartType => {
      const li = document.createElement('li');
      
      // 標記當前頁面
      if (currentFile === chartType.file) {
        li.className = 'menu-active';
      }
      
      const iconName = chartType.icon || 'circle';
      
      li.innerHTML = `
        <a href="${chartType.file}" class="flex items-center p-2 hover:bg-base-200 rounded-md ${currentFile === chartType.file ? 'bg-base-200 font-medium' : ''}">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="${getIconPath(iconName)}" />
          </svg>
          ${chartType.name}
        </a>
      `;
      list.appendChild(li);
    });

    nav.appendChild(list);

    // 添加折疊按鈕
    const toggleButton = document.createElement('button');
    toggleButton.className = 'fixed bottom-4 right-4 bg-primary text-primary-content rounded-full w-12 h-12 flex items-center justify-center shadow-lg z-40';
    toggleButton.id = 'chart-nav-toggle';
    toggleButton.innerHTML = `
      <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
      </svg>
    `;

    // 初始隱藏導航
    nav.style.display = 'none';

    // 添加到頁面
    document.body.appendChild(nav);
    document.body.appendChild(toggleButton);

    // 添加事件處理
    toggleButton.addEventListener('click', () => {
      if (nav.style.display === 'none') {
        nav.style.display = 'block';
      } else {
        nav.style.display = 'none';
      }
    });

    document.getElementById('chart-nav-close').addEventListener('click', () => {
      nav.style.display = 'none';
    });
  }

  // 獲取圖標路徑
  function getIconPath(iconName) {
    switch(iconName) {
      case 'trending-up':
        return 'M13 7h8m0 0v8m0-8l-8 8-4-4-6 6';
      case 'activity':
        return 'M22 12h-4l-3 9L9 3l-3 9H2';
      case 'bar-chart':
        return 'M12 20V10M18 20V4M6 20v-4';
      case 'bar-chart-2':
        return 'M18 20V10M12 20V4M6 20v-6';
      case 'pie-chart':
        return 'M21.21 15.89A10 10 0 1 1 8 2.83M22 12A10 10 0 0 0 12 2v10z';
      case 'circle':
        return 'M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z M12 7v0.01 M12 17v0.01';
      case 'compass':
        return 'M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20z M16.24 7.76l-2.12 6.36-6.36 2.12 2.12-6.36 6.36-2.12z';
      case 'radio':
        return 'M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20z M12 12a2 2 0 1 0 0 4 2 2 0 0 0 0-4z';
      case 'grid':
        return 'M3 3h7v7H3z M14 3h7v7h-7z M14 14h7v7h-7z M3 14h7v7H3z';
      case 'layers':
        return 'M12 2L2 7l10 5 10-5-10-5z M2 17l10 5 10-5 M2 12l10 5 10-5';
      case 'scatter-plot':
        return 'M2 20h20M5 4v16M19 4v16M5 9h14M5 15h14M8 4v4M8 12v4M12 4v4M12 12v4M16 4v4M16 12v4';
      case 'sliders':
        return 'M4 21v-7M4 10V3M12 21v-9M12 8V3M20 21v-5M20 12V3M1 14h6M9 8h6M17 16h6';
      default:
        return 'M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z';
    }
  }

  // 在頁面載入完成後初始化
  document.addEventListener('DOMContentLoaded', function() {
    setTimeout(createNavigator, 1000);
  });
})();
