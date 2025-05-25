/**
 * 設置極區域圖範例按鈕函數
 * 從index.json中載入所有適用的極區域圖範例
 * 自動生成按鈕並添加事件監聽器
 */

function setupExampleDataButtons() {
  console.log('設置極區域圖範例按鈕');
  
  // 極區圖數據容器元素
  const container = document.getElementById('polarArea-chart-data');
  if (!container) {
    console.error('找不到極區圖數據容器 #polarArea-chart-data');
    return;
  }
  
  // 清空容器
  container.innerHTML = '';
  
  // 先顯示載入中
  container.innerHTML = '<div class="text-sm text-center py-4">載入範例數據中...</div>';
  
  // 從index.json載入所有極區域圖範例
  fetch('./assets/examples/index.json')
    .then(response => {
      if (!response.ok) throw new Error('無法載入範例索引檔');
      return response.json();
    })
    .then(indexData => {
      // 檢查是否有極區圖範例
      if (!indexData.polarArea || !Array.isArray(indexData.polarArea) || indexData.polarArea.length === 0) {
        container.innerHTML = '<div class="alert alert-warning">找不到極區圖範例數據</div>';
        return;
      }
      
      // 清空容器再添加範例按鈕
      container.innerHTML = '';
      
      // 為每個範例創建按鈕
      indexData.polarArea.forEach(example => {
        if (example && example.file && example.title && example.suitableTypes.includes('polarArea')) {
          const exampleItem = document.createElement('button');
          exampleItem.className = 'example-btn w-full btn btn-sm bg-base-200 hover:bg-accent hover:text-accent-content justify-between mb-1';
          exampleItem.setAttribute('data-example', example.file);
          
          exampleItem.innerHTML = `
            <span class="text-left truncate">${example.title}</span>
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          `;
          
          // 添加提示說明
          if (example.description) {
            exampleItem.setAttribute('title', example.description);
          }
          
          // 添加點擊事件
          exampleItem.addEventListener('click', function() {
            // 移除其他按鈕的選中狀態
            document.querySelectorAll('.example-btn').forEach(btn => {
              btn.classList.remove('bg-accent', 'text-accent-content');
              btn.classList.add('bg-base-200');
            });
            
            // 設置當前按鈕為選中狀態
            this.classList.remove('bg-base-200');
            this.classList.add('bg-accent', 'text-accent-content');
            
            // 載入範例
            window.loadPolarAreaChartExample(this.dataset.example);
          });
          
          container.appendChild(exampleItem);
        }
      });
      
      // 預設選中第一個範例
      const firstBtn = container.querySelector('.example-btn');
      if (firstBtn) {
        firstBtn.classList.remove('bg-base-200');
        firstBtn.classList.add('bg-accent', 'text-accent-content');
      }
    })
    .catch(error => {
      console.error('載入範例失敗:', error);
      container.innerHTML = `<div class="alert alert-error">載入範例出錯: ${error.message}</div>`;
    });
}
