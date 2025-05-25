/**
 * 圖表全面性測試工具
 * 用於測試所有圖表的渲染狀態
 */

(function() {
  console.log('圖表全面性測試工具已載入');
  
  // 所有圖表類型及其對應的頁面文件
  const chartTypesMap = {
    'line': 'line.html',
    'area': 'area.html',
    'bar': 'bar.html',
    'column': 'column.html',
    'pie': 'pie.html',
    'donut': 'donut.html',
    'radar': 'radar.html',
    'polararea': 'polararea.html',
    'heatmap': 'heatmap.html',
    'treemap': 'treemap.html',
    'scatter': 'scatter.html',
    'mixed': 'mixed.html',
    'candlestick': 'index.html'
  };
  
  // 檢測當前頁面
  function detectCurrentChartPage() {
    const path = window.location.pathname;
    
    // 遍歷圖表類型映射表
    for (const [chartType, htmlFile] of Object.entries(chartTypesMap)) {
      if (path.includes(htmlFile)) {
        return chartType;
      }
    }
    
    // 特殊情況：首頁通常是蠟燭圖
    if (path === '/' || path.endsWith('/') || path.includes('index.html')) {
      return 'candlestick';
    }
    
    return null;
  }
  
  // 測試單個圖表
  function testSingleChart(chartType) {
    console.log(`測試 ${chartType} 圖表...`);
    
    // 使用驗證工具檢查圖表
    if (window.ChartVerification && typeof window.ChartVerification.runVerification === 'function') {
      const result = window.ChartVerification.runVerification(chartType);
      return {
        type: chartType,
        status: result ? '成功' : '失敗',
        timestamp: new Date().toISOString()
      };
    }
    
    return {
      type: chartType,
      status: '未測試 - 無法訪問驗證工具',
      timestamp: new Date().toISOString()
    };
  }
  
  // 在控制台中顯示測試結果
  function displayTestResults(results) {
    console.log('===== 圖表測試結果 =====');
    console.table(results);
    
    // 計算統計資料
    const total = results.length;
    const successful = results.filter(r => r.status === '成功').length;
    const failed = results.filter(r => r.status === '失敗').length;
    
    console.log(`總共測試: ${total} | 成功: ${successful} | 失敗: ${failed}`);
    
    return {
      total,
      successful,
      failed,
      successRate: `${Math.round(successful / total * 100)}%`
    };
  }
  
  // 創建測試報告UI
  function createTestReportUI(results, stats) {
    // 檢查是否有DOM環境
    if (typeof document === 'undefined') {
      return;
    }
    
    // 創建報告容器
    const reportContainer = document.createElement('div');
    reportContainer.className = 'fixed bottom-4 right-4 w-72 bg-white shadow-xl rounded-lg p-4 border border-gray-200 z-50';
    reportContainer.id = 'chart-test-report';
    
    // 添加標題
    const title = document.createElement('div');
    title.className = 'font-medium text-lg mb-2 flex justify-between items-center';
    title.innerHTML = `
      <span>圖表測試報告</span>
      <button class="text-sm text-gray-400 hover:text-gray-600" id="close-report">✕</button>
    `;
    reportContainer.appendChild(title);
    
    // 添加統計資料
    const statsEl = document.createElement('div');
    statsEl.className = 'mb-2 text-sm';
    statsEl.innerHTML = `
      <div class="grid grid-cols-2 gap-2 mb-2">
        <div class="bg-gray-100 rounded p-1">總計: ${stats.total}</div>
        <div class="bg-green-100 rounded p-1">成功: ${stats.successful}</div>
        <div class="bg-red-100 rounded p-1">失敗: ${stats.failed}</div>
        <div class="bg-blue-100 rounded p-1">成功率: ${stats.successRate}</div>
      </div>
    `;
    reportContainer.appendChild(statsEl);
    
    // 添加結果表格
    const table = document.createElement('table');
    table.className = 'w-full text-xs';
    
    // 表頭
    const thead = document.createElement('thead');
    thead.innerHTML = `
      <tr class="bg-gray-100">
        <th class="text-left p-1">圖表類型</th>
        <th class="text-left p-1">狀態</th>
        <th class="text-left p-1">操作</th>
      </tr>
    `;
    table.appendChild(thead);
    
    // 表格內容
    const tbody = document.createElement('tbody');
    results.forEach(result => {
      const tr = document.createElement('tr');
      tr.className = 'border-t border-gray-200';
      
      const statusClass = result.status === '成功' ? 'text-green-600' : 'text-red-600';
      
      tr.innerHTML = `
        <td class="p-1">${result.type}</td>
        <td class="p-1 ${statusClass}">${result.status}</td>
        <td class="p-1">
          <a href="${chartTypesMap[result.type]}" class="text-blue-500 hover:underline">查看</a>
        </td>
      `;
      tbody.appendChild(tr);
    });
    table.appendChild(tbody);
    reportContainer.appendChild(table);
    
    // 添加動作按鈕
    const actions = document.createElement('div');
    actions.className = 'mt-3 flex justify-end space-x-2';
    actions.innerHTML = `
      <button id="rerun-tests" class="px-2 py-1 bg-primary text-white text-xs rounded hover:bg-primary-focus">重新測試</button>
    `;
    reportContainer.appendChild(actions);
    
    // 添加到頁面
    document.body.appendChild(reportContainer);
    
    // 添加事件監聽
    document.getElementById('close-report').addEventListener('click', () => {
      reportContainer.remove();
    });
    
    document.getElementById('rerun-tests').addEventListener('click', () => {
      runAllTests();
    });
  }
  
  // 運行當前頁面的圖表測試
  function runCurrentPageTest() {
    const currentChartType = detectCurrentChartPage();
    if (!currentChartType) {
      console.warn('無法檢測當前頁面的圖表類型');
      return null;
    }
    
    return testSingleChart(currentChartType);
  }
  
  // 運行所有圖表測試
  function runAllTests() {
    // 在實際環境中，這需要通過iframe或導航來完成
    // 這裡我們只是模擬測試每個圖表
    const results = [];
    
    Object.keys(chartTypesMap).forEach(chartType => {
      results.push(testSingleChart(chartType));
    });
    
    const stats = displayTestResults(results);
    createTestReportUI(results, stats);
    
    return { results, stats };
  }
  
  // 在頁面載入完成後執行
  document.addEventListener('DOMContentLoaded', function() {
    // 等待組件載入完成
    document.addEventListener('component-loaded', function() {
      // 等待頁面穩定
      setTimeout(function() {
        // 只在主頁面上添加測試面板
        const path = window.location.pathname;
        if (path === '/' || path.endsWith('/') || path.includes('index.html')) {
          console.log('在主頁面上添加圖表測試面板');
          
          // 創建測試按鈕
          const testButton = document.createElement('button');
          testButton.className = 'fixed bottom-4 left-4 bg-accent text-white px-3 py-2 rounded shadow hover:bg-accent-focus z-40';
          testButton.textContent = '測試所有圖表';
          testButton.id = 'test-all-charts';
          document.body.appendChild(testButton);
          
          // 添加事件監聽
          testButton.addEventListener('click', runAllTests);
        } else {
          // 在其他頁面上自動運行測試
          runCurrentPageTest();
        }
      }, 1500);
    });
  });
  
  // 將測試工具暴露到全局範圍
  window.ChartTestingTool = {
    runAllTests,
    testSingleChart,
    runCurrentPageTest,
    chartTypes: Object.keys(chartTypesMap)
  };
})();
