/**
 * 圖表類型和資料格式一致性驗證工具
 * 用於檢查範例資料 JSON 的類型與 index.json 中的 suitableTypes 是否一致
 */

(function() {
  console.log('圖表類型驗證工具已啟動');

  // 保存已檢查的文件和結果
  window.chartTypeValidation = {
    validatedFiles: {},
    inconsistencies: [],
    formatterIssues: []
  };
  
  // 主驗證函數
  window.validateChartTypes = async function() {
    console.log('開始驗證圖表類型一致性');
    
    try {
      // 載入索引文件
      const indexResp = await fetch('assets/examples/index.json');
      if (!indexResp.ok) throw new Error('無法載入 index.json');
      
      const indexData = await indexResp.json();
      console.log('已載入圖表索引文件');
      
      // 建立待驗證的文件列表
      const filesToValidate = [];
      let totalExamples = 0;
      
      // 收集所有範例資料文件
      Object.keys(indexData).forEach(chartType => {
        if (Array.isArray(indexData[chartType])) {
          indexData[chartType].forEach(example => {
            if (example.file && example.suitableTypes) {
              filesToValidate.push({
                file: example.file,
                expectedTypes: example.suitableTypes,
                category: chartType
              });
              totalExamples++;
            }
          });
        }
      });
      
      console.log(`共發現 ${totalExamples} 個範例需要驗證`);
      
      // 開始逐一驗證
      for (const item of filesToValidate) {
        await validateFile(item);
      }
      
      // 輸出結果
      console.log('圖表類型驗證完成，結果：');
      console.log(`- 已檢查文件：${Object.keys(window.chartTypeValidation.validatedFiles).length}`);
      console.log(`- 發現不一致：${window.chartTypeValidation.inconsistencies.length}`);
      console.log(`- Formatter 問題：${window.chartTypeValidation.formatterIssues.length}`);
      
      return {
        validated: Object.keys(window.chartTypeValidation.validatedFiles).length,
        inconsistencies: window.chartTypeValidation.inconsistencies,
        formatterIssues: window.chartTypeValidation.formatterIssues
      };
    } catch (error) {
      console.error('圖表類型驗證失敗：', error);
      return {
        error: error.message,
        validated: Object.keys(window.chartTypeValidation.validatedFiles).length,
        inconsistencies: window.chartTypeValidation.inconsistencies,
        formatterIssues: window.chartTypeValidation.formatterIssues
      };
    }
  };
  
  // 檢查單個文件
  async function validateFile(item) {
    const { file, expectedTypes, category } = item;
    const filePath = `assets/examples/${file}`;
    
    try {
      // 載入檔案
      const resp = await fetch(filePath);
      if (!resp.ok) throw new Error(`無法載入文件 ${file}`);
      
      const chartData = await resp.json();
      
      // 檢查 chart.type
      let actualType = null;
      if (chartData.chart && chartData.chart.type) {
        actualType = chartData.chart.type.toLowerCase();
      }
      
      // 特殊處理 polarArea/polararea 大小寫
      if (actualType === 'polararea') actualType = 'polarArea';
      
      // 記錄驗證結果
      const result = {
        file,
        expectedTypes,
        actualType,
        category,
        isConsistent: false
      };
      
      // 檢查一致性
      if (actualType) {
        result.isConsistent = expectedTypes.some(type => 
          type.toLowerCase() === actualType.toLowerCase()
        );
      }
      
      // 檢查 formatter 函數
      const formatterIssues = checkFormatters(chartData, file);
      
      // 保存結果
      window.chartTypeValidation.validatedFiles[file] = result;
      
      if (!result.isConsistent) {
        window.chartTypeValidation.inconsistencies.push({
          file,
          expectedTypes,
          actualType,
          category
        });
        console.warn(`類型不一致：${file} - 預期：${expectedTypes.join(', ')}，實際：${actualType || '未指定'}`);
      }
      
      if (formatterIssues.length > 0) {
        window.chartTypeValidation.formatterIssues.push({
          file,
          issues: formatterIssues
        });
      }
      
      return result;
    } catch (error) {
      console.error(`驗證文件 ${file} 失敗：`, error);
      return {
        file,
        error: error.message,
        isConsistent: false
      };
    }
  }
  
  // 檢查是否還有未解決的 formatter 函數問題
  function checkFormatters(data, file) {
    const issues = [];
    
    // 檢查各種常見的 formatter 位置
    if (data.yaxis) {
      // 單一 y 軸
      if (data.yaxis.labels && data.yaxis.labels.formatter && 
          data.yaxis.labels.formatter !== null &&
          typeof data.yaxis.labels.formatter === 'string') {
        issues.push('yaxis.labels.formatter');
      }
      
      // 多個 y 軸
      if (Array.isArray(data.yaxis)) {
        data.yaxis.forEach((axis, index) => {
          if (axis.labels && axis.labels.formatter && 
              axis.labels.formatter !== null &&
              typeof axis.labels.formatter === 'string') {
            issues.push(`yaxis[${index}].labels.formatter`);
          }
        });
      }
    }
    
    // 檢查 tooltip
    if (data.tooltip) {
      if (data.tooltip.y && data.tooltip.y.formatter && 
          data.tooltip.y.formatter !== null &&
          typeof data.tooltip.y.formatter === 'string') {
        issues.push('tooltip.y.formatter');
      }
      
      if (data.tooltip.x && data.tooltip.x.formatter &&
          data.tooltip.x.formatter !== null &&
          typeof data.tooltip.x.formatter === 'string') {
        issues.push('tooltip.x.formatter');
      }
    }
    
    // 檢查 dataLabels
    if (data.dataLabels && data.dataLabels.formatter && 
        data.dataLabels.formatter !== null &&
        typeof data.dataLabels.formatter === 'string') {
      issues.push('dataLabels.formatter');
    }
    
    // 檢查 legend
    if (data.legend && data.legend.formatter && 
        data.legend.formatter !== null &&
        typeof data.legend.formatter === 'string') {
      issues.push('legend.formatter');
    }
    
    if (issues.length > 0) {
      console.warn(`文件 ${file} 中發現 formatter 問題：${issues.join(', ')}`);
    }
    
    return issues;
  }
  
  // 呈現驗證結果的 UI
  window.showChartValidationResults = function() {
    // 檢查是否已存在結果面板
    let resultPanel = document.getElementById('chart-validation-results');
    if (resultPanel) {
      resultPanel.remove();
    }
    
    // 建立結果面板
    resultPanel = document.createElement('div');
    resultPanel.id = 'chart-validation-results';
    resultPanel.className = 'fixed top-4 right-4 w-96 max-h-[80vh] overflow-auto bg-base-100 p-4 rounded-lg shadow-xl z-50 border border-base-300';
    
    // 添加標題和關閉按鈕
    resultPanel.innerHTML = `
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-lg font-bold">圖表類型驗證結果</h3>
        <button id="close-validation-panel" class="btn btn-sm btn-ghost">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      <div id="validation-content" class="space-y-4">
        <p>正在加載驗證結果...</p>
      </div>
    `;
    
    document.body.appendChild(resultPanel);
    
    // 綁定關閉按鈕事件
    document.getElementById('close-validation-panel').addEventListener('click', function() {
      resultPanel.remove();
    });
    
    // 執行驗證並顯示結果
    window.validateChartTypes().then(results => {
      const contentDiv = document.getElementById('validation-content');
      
      // 生成結果摘要
      let html = `
        <div class="stats shadow w-full">
          <div class="stat">
            <div class="stat-title">已驗證文件</div>
            <div class="stat-value">${results.validated}</div>
          </div>
          <div class="stat">
            <div class="stat-title">類型不一致</div>
            <div class="stat-value ${results.inconsistencies.length > 0 ? 'text-error' : 'text-success'}">${results.inconsistencies.length}</div>
          </div>
          <div class="stat">
            <div class="stat-title">Formatter 問題</div>
            <div class="stat-value ${results.formatterIssues.length > 0 ? 'text-warning' : 'text-success'}">${results.formatterIssues.length}</div>
          </div>
        </div>
      `;
      
      // 若有不一致問題，顯示詳細資訊
      if (results.inconsistencies.length > 0) {
        html += `
          <div class="mt-4">
            <h4 class="font-bold text-error mb-2">類型不一致問題：</h4>
            <div class="overflow-x-auto">
              <table class="table table-xs table-zebra w-full">
                <thead>
                  <tr>
                    <th>檔案</th>
                    <th>預期類型</th>
                    <th>實際類型</th>
                  </tr>
                </thead>
                <tbody>
        `;
        
        results.inconsistencies.forEach(issue => {
          html += `
            <tr>
              <td class="text-xs">${issue.file}</td>
              <td class="text-xs">${issue.expectedTypes.join(', ')}</td>
              <td class="text-xs ${issue.actualType ? '' : 'text-error'}">${issue.actualType || '未指定'}</td>
            </tr>
          `;
        });
        
        html += `
                </tbody>
              </table>
            </div>
          </div>
        `;
      }
      
      // 若有 formatter 問題，顯示詳細資訊
      if (results.formatterIssues.length > 0) {
        html += `
          <div class="mt-4">
            <h4 class="font-bold text-warning mb-2">Formatter 問題：</h4>
            <div class="overflow-x-auto">
              <table class="table table-xs table-zebra w-full">
                <thead>
                  <tr>
                    <th>檔案</th>
                    <th>問題位置</th>
                  </tr>
                </thead>
                <tbody>
        `;
        
        results.formatterIssues.forEach(issue => {
          html += `
            <tr>
              <td class="text-xs">${issue.file}</td>
              <td class="text-xs">${issue.issues.join('<br>')}</td>
            </tr>
          `;
        });
        
        html += `
                </tbody>
              </table>
            </div>
          </div>
        `;
      }
      
      contentDiv.innerHTML = html;
    });
  };
  
  // 添加到主視窗
  if (typeof window.installChartDebugTools === 'function') {
    window.installChartDebugTools('chart-type-validator', {
      name: '驗證圖表類型',
      action: window.showChartValidationResults
    });
  }
  
  console.log('圖表類型驗證工具初始化完成');
})();
