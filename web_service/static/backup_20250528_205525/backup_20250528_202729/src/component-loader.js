// component-loader.js - 動態加載組件
// 用於在不同環境中正確處理組件路徑

// 決定正確的基礎路徑前綴
function getBasePath() {
  // 檢查是否為開發環境（檢查多個可能的開發端口）
  const isDevelopment = ['5173', '5174', '5175', '5176', '5177', '3000', '8080'].includes(window.location.port);
  
  // 額外檢查：如果當前路徑已包含 /static/，則為生產環境
  const isProduction = window.location.pathname.includes('/static/') || 
                      (!isDevelopment && window.location.port === '8000');
  
  console.log(`當前環境: ${isDevelopment ? '開發環境' : '生產環境'}`);
  console.log(`當前端口: ${window.location.port}`);
  console.log(`當前路徑: ${window.location.pathname}`);
  
  // 在開發環境中，Vite 會自動處理 public 目錄下的靜態資源
  // 在生產環境中，需要 /static 前綴
  return isDevelopment ? '' : '/static';
}

// 組件載入器
export async function loadComponent(element) {
  const path = element.getAttribute('data-component');
  if (!path) return;

  const basePath = getBasePath();
  let fullPath = path;
  
  // 確保路徑處理的一致性
  if (basePath && !path.startsWith(basePath)) {
    fullPath = basePath + (path.startsWith('/') ? path : '/' + path);
  }

  console.log(`嘗試載入組件: ${fullPath}`);

  try {
    const response = await fetch(fullPath);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const html = await response.text();
    element.innerHTML = html;
    console.log(`✅ 組件載入成功: ${fullPath}`);
    return true;
  } catch (error) {
    console.error(`❌ 組件載入失敗 ${fullPath}:`, error);
    element.innerHTML = `<div class="alert alert-error">載入組件失敗: ${fullPath}</div>`;
    return false;
  }
}

// 初始化組件載入器
function initComponentLoader() {
  const components = document.querySelectorAll('[data-component]');
  console.log(`找到 ${components.length} 個組件需要載入`);
  
  if (components.length === 0) {
    console.log('⚠️ 沒有找到任何 data-component 屬性，檢查 HTML 標記');
  }
  
  components.forEach(loadComponent);
}

// DOM 載入完成後自動初始化
document.addEventListener('DOMContentLoaded', initComponentLoader);

// 導出函數供其他模組使用
export { initComponentLoader, getBasePath };