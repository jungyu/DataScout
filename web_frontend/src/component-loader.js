// component-loader.js - 動態加載組件
// 用於在不同環境中正確處理組件路徑

// 決定正確的基礎路徑前綴
function getBasePath() {
  // 根據環境判斷應該使用的路徑前綴
  // 檢查是否為開發環境（使用 Vite 開發服務器，端口通常為 5173）
  const isDevelopment = window.location.port === '5173';
  
  console.log(`當前環境: ${isDevelopment ? '開發環境' : '生產環境'}`);
  // 在開發環境中，路徑是相對於 public 目錄的
  return isDevelopment ? '/public' : '/static';
}

// 組件載入器
export async function loadComponent(element) {
  const path = element.getAttribute('data-component');
  if (!path) return;

  try {
    const response = await fetch(path);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    const html = await response.text();
    element.innerHTML = html;
    return true;
  } catch (error) {
    console.error(`Error loading component ${path}:`, error);
    element.innerHTML = `<div class="alert alert-error">載入組件失敗: ${path}</div>`;
    return false;
  }
}

// 初始化組件載入器
export function initComponentLoader() {
  const components = document.querySelectorAll('[data-component]');
  components.forEach(loadComponent);
}

// DOM 載入完成後自動初始化
document.addEventListener('DOMContentLoaded', initComponentLoader);

// 導出函數供其他模組使用
export { initComponentLoader, getBasePath };