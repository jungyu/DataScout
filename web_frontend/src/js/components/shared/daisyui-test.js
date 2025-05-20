/**
 * DaisyUI 組件測試文件
 * 
 * 本文件包含一些基本的 DaisyUI 測試組件，用於確認 DaisyUI 是否正確加載
 * 這是一個純前端功能，不依賴後端 API
 */

// 簡單的警告組件
export function createAlert(type = 'info', message = '這是一個測試消息') {
  const alertTypes = {
    'info': 'alert-info',
    'success': 'alert-success',
    'warning': 'alert-warning',
    'error': 'alert-error'
  };
  
  const alertClass = alertTypes[type] || alertTypes['info'];
  const alertDiv = document.createElement('div');
  alertDiv.className = `alert ${alertClass} my-4`;
  alertDiv.innerHTML = `
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current shrink-0 w-6 h-6">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
    </svg>
    <span>${message}</span>
  `;
  
  return alertDiv;
}

// DaisyUI 主題測試
export function injectThemeSelector(targetSelector = 'body') {
  const themeOptions = [
    'light', 'dark', 'cupcake', 'bumblebee', 'emerald', 'corporate', 
    'synthwave', 'retro', 'cyberpunk', 'valentine', 'halloween', 'garden',
    'forest', 'aqua', 'lofi', 'pastel', 'fantasy', 'wireframe', 'black',
    'luxury', 'dracula', 'cmyk', 'autumn', 'business', 'acid', 'lemonade',
    'night', 'coffee', 'winter'
  ];
  
  const target = document.querySelector(targetSelector);
  if (!target) return;
  
  const container = document.createElement('div');
  container.className = 'fixed bottom-4 right-4 card bg-base-100 shadow-lg p-4 w-64';
  
  const title = document.createElement('h3');
  title.className = 'text-lg font-bold mb-2';
  title.textContent = 'DaisyUI 主題測試';
  
  const select = document.createElement('select');
  select.className = 'select select-bordered w-full';
  
  themeOptions.forEach(theme => {
    const option = document.createElement('option');
    option.value = theme;
    option.textContent = theme;
    if (theme === 'light') option.selected = true;
    select.appendChild(option);
  });
  
  select.addEventListener('change', (e) => {
    document.documentElement.setAttribute('data-theme', e.target.value);
    localStorage.setItem('daisy-theme', e.target.value);
  });
  
  // 從 localStorage 加載上次選擇的主題
  const savedTheme = localStorage.getItem('daisy-theme');
  if (savedTheme && themeOptions.includes(savedTheme)) {
    document.documentElement.setAttribute('data-theme', savedTheme);
    select.value = savedTheme;
  }
  
  container.appendChild(title);
  container.appendChild(select);
  target.appendChild(container);
}

// 測試 DaisyUI 共用組件
export function testDaisyUIComponents(targetSelector = '#daisyui-test') {
  const target = document.querySelector(targetSelector);
  if (!target) return;
  
  target.innerHTML = `
    <div class="p-4">
      <h2 class="text-2xl font-bold mb-4">DaisyUI 組件測試</h2>
      
      <!-- 按鈕測試 -->
      <div class="card bg-base-100 shadow-lg p-4 mb-4">
        <h3 class="text-lg font-bold mb-2">按鈕</h3>
        <div class="flex flex-wrap gap-2">
          <button class="btn">默認按鈕</button>
          <button class="btn btn-primary">主要按鈕</button>
          <button class="btn btn-secondary">次要按鈕</button>
          <button class="btn btn-accent">強調按鈕</button>
          <button class="btn btn-ghost">幽靈按鈕</button>
          <button class="btn btn-link">鏈接按鈕</button>
        </div>
      </div>
      
      <!-- 卡片測試 -->
      <div class="card bg-base-100 shadow-lg p-4 mb-4">
        <h3 class="text-lg font-bold mb-2">卡片樣式</h3>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="card bg-primary text-primary-content">
            <div class="card-body">
              <h3 class="card-title">主要卡片</h3>
              <p>這是一個測試卡片。</p>
            </div>
          </div>
          
          <div class="card bg-secondary text-secondary-content">
            <div class="card-body">
              <h3 class="card-title">次要卡片</h3>
              <p>這是一個測試卡片。</p>
            </div>
          </div>
          
          <div class="card bg-accent text-accent-content">
            <div class="card-body">
              <h3 class="card-title">強調卡片</h3>
              <p>這是一個測試卡片。</p>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 表單元素 -->
      <div class="card bg-base-100 shadow-lg p-4 mb-4">
        <h3 class="text-lg font-bold mb-2">表單元素</h3>
        <div class="form-control w-full max-w-md">
          <label class="label">
            <span class="label-text">輸入框</span>
          </label>
          <input type="text" placeholder="請輸入內容" class="input input-bordered w-full" />
          
          <label class="label mt-4">
            <span class="label-text">下拉選單</span>
          </label>
          <select class="select select-bordered w-full">
            <option disabled selected>選擇一個選項</option>
            <option>選項 1</option>
            <option>選項 2</option>
            <option>選項 3</option>
          </select>
          
          <div class="mt-4">
            <label class="cursor-pointer label justify-start gap-4">
              <input type="checkbox" class="checkbox checkbox-primary" />
              <span class="label-text">複選框</span>
            </label>
          </div>
          
          <div class="mt-4">
            <div class="form-control">
              <label class="label cursor-pointer justify-start gap-4">
                <input type="radio" name="radio-test" class="radio radio-primary" checked />
                <span class="label-text">選項 A</span>
              </label>
            </div>
            <div class="form-control">
              <label class="label cursor-pointer justify-start gap-4">
                <input type="radio" name="radio-test" class="radio radio-primary" />
                <span class="label-text">選項 B</span>
              </label>
            </div>
          </div>
          
          <div class="mt-4">
            <label class="label">
              <span class="label-text">滑塊</span>
            </label>
            <input type="range" min="0" max="100" class="range range-primary" />
          </div>
        </div>
      </div>
      
      <!-- 提示和警告 -->
      <div class="card bg-base-100 shadow-lg p-4 mb-4">
        <h3 class="text-lg font-bold mb-2">提示和警告</h3>
        <div class="space-y-4">
          <div class="alert alert-info">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current shrink-0 w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
            <span>信息提示</span>
          </div>
          
          <div class="alert alert-success">
            <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
            <span>成功提示</span>
          </div>
          
          <div class="alert alert-warning">
            <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
            <span>警告提示</span>
          </div>
          
          <div class="alert alert-error">
            <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
            <span>錯誤提示</span>
          </div>
        </div>
      </div>
    </div>
  `;
}
