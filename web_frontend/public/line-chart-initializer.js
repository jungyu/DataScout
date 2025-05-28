/**
 * 折線圖專用初始化和渲染函數
 * 解決折線圖無法正確載入或顯示的問題
 */

document.addEventListener('DOMContentLoaded', function() {
  console.log('折線圖專用初始化腳本已載入');

  // 監聽組件載入事件
  document.addEventListener('component-loaded', function(e) {
    if (e.detail && e.detail.componentPath && e.detail.componentPath.includes('LineChartContent.html')) {
      console.log('折線圖組件已載入，初始化專用處理');
      // 等待一下確保 DOM 完全更新
      setTimeout(initLineChartPage, 100);
    }
  });

  /**
   * 折線圖頁面初始化
   */
  function initLineChartPage() {
    console.log('初始化折線圖頁面');

    // 檢查是否已經初始化過
    if (window.__lineChartInitialized) {
      console.log('折線圖頁面已初始化，跳過');
      return;
    }

    // 標記為已初始化
    window.__lineChartInitialized = true;

    // 確保頁面上有折線圖容器
    const chartContainer = document.getElementById('lineChart');
    if (!chartContainer) {
      console.error('找不到折線圖容器 #lineChart');
      return;
    }

    // 為折線圖示例準備容器
    prepareLineChartExamples();

    // 載入預設折線圖數據
    loadDefaultLineChartData();
  }

  /**
   * 準備折線圖示例列表
   */
  function prepareLineChartExamples() {
    console.log('準備折線圖示例');

    // 獲取示例容器
    const examplesContainer = document.getElementById('line-chart-data');
    if (!examplesContainer) {
      console.error('找不到折線圖示例容器 #line-chart-data');
      return;
    }

    // 清空容器內容，準備添加示例
    examplesContainer.innerHTML = '';

    // 獲取所有折線圖示例
    fetch('assets/examples/index.json')
      .then(response => response.json())
      .then(data => {
        // 從 index.json 中獲取折線圖示例
        const lineExamples = data.line || [];
        console.log(`找到 ${lineExamples.length} 個折線圖示例`);

        if (lineExamples.length === 0) {
          examplesContainer.innerHTML = '<div class="text-center p-4">沒有找到折線圖示例</div>';
          return;
        }

        // 為每個示例創建UI元素
        lineExamples.forEach((example, index) => {
          const exampleBlock = document.createElement('div');
          exampleBlock.className = 'chart-data-item bg-base-200 p-4 mb-4 rounded-lg hover:bg-base-300 transition-colors border border-base-300';
          exampleBlock.setAttribute('data-file', example.file);
          
          const loadBtnText = index === 0 ? '自動載入' : '點擊載入';
          
          exampleBlock.innerHTML = `
            <div class="font-medium mb-1 text-base-content">${example.title}</div>
            <div class="text-sm text-base-content opacity-80 mb-2">${example.description}</div>
            <button class="text-accent hover:text-accent-focus text-sm font-medium btn-sm btn-ghost px-2 py-0.5 rounded load-data-btn">${loadBtnText}</button>
          `;
          
          examplesContainer.appendChild(exampleBlock);
          
          // 添加點擊事件
          const loadBtn = exampleBlock.querySelector('.load-data-btn');
          loadBtn.addEventListener('click', function() {
            loadLineChartData(example.file);
            
            // 更新所有按鈕狀態
            document.querySelectorAll('.chart-data-item').forEach(item => {
              const btn = item.querySelector('.load-data-btn');
              const isActive = item.getAttribute('data-file') === example.file;
              
              if (isActive) {
                btn.textContent = '已載入';
                btn.classList.remove('btn-ghost', 'text-accent');
                btn.classList.add('btn-accent', 'text-accent-content');
                item.classList.add('border-accent', 'active');
                item.classList.remove('border-base-300');
              } else {
                btn.textContent = '點擊載入';
                btn.classList.add('btn-ghost', 'text-accent');
                btn.classList.remove('btn-accent', 'text-accent-content');
                item.classList.remove('border-accent', 'active');
                item.classList.add('border-base-300');
              }
            });
          });
        });
        
        // 自動載入第一個示例
        if (lineExamples.length > 0) {
          setTimeout(() => {
            loadLineChartData(lineExamples[0].file);
            
            // 標記第一個示例為已載入
            const firstExample = examplesContainer.querySelector('.chart-data-item');
            if (firstExample) {
              const btn = firstExample.querySelector('.load-data-btn');
              btn.textContent = '已載入';
              btn.classList.remove('btn-ghost', 'text-accent');
              btn.classList.add('btn-accent', 'text-accent-content');
              firstExample.classList.add('border-accent', 'active');
              firstExample.classList.remove('border-base-300');
            }
          }, 300);
        }
      })
      .catch(error => {
        console.error('載入折線圖示例失敗:', error);
        examplesContainer.innerHTML = '<div class="text-center p-4 text-error">載入示例失敗</div>';
      });
  }

  /**
   * 載入預設折線圖數據
   */
  function loadDefaultLineChartData() {
    console.log('載入預設折線圖數據');
    loadLineChartData('apexcharts_line_sales.json');
  }

  /**
   * 載入指定折線圖數據
   */
  function loadLineChartData(filename) {
    console.log(`載入折線圖數據: ${filename}`);
    
    // 獲取圖表容器
    const chartContainer = document.getElementById('lineChart');
    if (!chartContainer) {
      console.error('找不到折線圖容器');
      return;
    }
    
    // 清除可能存在的舊圖表
    if (window.ApexCharts) {
      const existingChart = ApexCharts.getChartByID('lineChart');
      if (existingChart) {
        existingChart.destroy();
      }
    }
    
    // 標記圖表容器為載入中
    chartContainer.innerHTML = `
      <div class="flex items-center justify-center h-full">
        <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-accent"></div>
        <span class="ml-3 text-base-content">載入中...</span>
      </div>
    `;
    
    // 從檔案載入數據
    fetch(`assets/examples/${filename}`)
      .then(response => {
        if (!response.ok) {
          throw new Error(`無法載入檔案: ${filename}`);
        }
        return response.json();
      })
      .then(data => {
        renderLineChart(data);
      })
      .catch(error => {
        console.error('載入折線圖數據失敗:', error);
        
        // 顯示錯誤訊息
        chartContainer.innerHTML = `
          <div class="flex flex-col items-center justify-center h-full">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-error mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <p class="text-base text-error font-medium">載入數據失敗: ${error.message}</p>
            <button class="btn btn-sm btn-outline btn-error mt-4" onclick="location.reload()">重新整理頁面</button>
          </div>
        `;
      });
  }

  /**
   * 渲染折線圖
   */
  function renderLineChart(data) {
    console.log('渲染折線圖:', data);
    
    // 獲取圖表容器
    const chartContainer = document.getElementById('lineChart');
    if (!chartContainer) {
      console.error('找不到折線圖容器');
      return;
    }
    
    // 清空圖表容器
    chartContainer.innerHTML = '';
    
    // 確保數據格式正確
    if (!data || !data.series || !data.series.length) {
      console.error('折線圖數據格式錯誤');
      showChartError('數據格式錯誤');
      return;
    }
    
    // 確保圖表類型為line
    if (!data.chart) data.chart = {};
    data.chart.type = 'line';
    data.chart.id = 'lineChart';
    
    try {
      // 創建並渲染圖表
      const chart = new ApexCharts(chartContainer, data);
      chart.render();
      console.log('折線圖渲染成功');
      
      // 更新圖例標籤
      updateChartLegends(data);
    } catch (error) {
      console.error('渲染折線圖失敗:', error);
      showChartError(`渲染失敗: ${error.message}`);
    }
  }

  /**
   * 更新圖例標籤
   */
  function updateChartLegends(data) {
    if (!data || !data.series) return;
    
    // 獲取圖例容器
    const legendContainer = document.querySelector('.flex.space-x-4');
    if (!legendContainer) return;
    
    // 清空現有圖例
    legendContainer.innerHTML = '';
    
    // 預定義的顏色
    const colors = ['#008FFB', '#00E396', '#FEB019', '#FF4560', '#775DD0'];
    
    // 為每個數據系列創建一個圖例項
    data.series.forEach((series, index) => {
      const color = data.colors && data.colors[index] ? data.colors[index] : colors[index % colors.length];
      
      const legendItem = document.createElement('div');
      legendItem.className = 'flex items-center';
      legendItem.innerHTML = `
        <span class="w-3 h-3 rounded-full mr-2 ring-1 ring-base-content/10" style="background-color: ${color};"></span>
        <span class="text-sm font-medium text-base-content">${series.name}</span>
      `;
      
      legendContainer.appendChild(legendItem);
    });
  }

  /**
   * 顯示圖表錯誤
   */
  function showChartError(message) {
    const chartContainer = document.getElementById('lineChart');
    if (!chartContainer) return;
    
    chartContainer.innerHTML = `
      <div class="flex flex-col items-center justify-center h-full">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-error mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <p class="text-base text-error font-medium">${message}</p>
        <button class="btn btn-sm btn-outline btn-error mt-4" onclick="location.reload()">重新整理頁面</button>
      </div>
    `;
  }

  // 將主要函數暴露給全局
  window.initLineChartPage = initLineChartPage;
  window.loadLineChartData = loadLineChartData;
  window.renderLineChart = renderLineChart;
});
