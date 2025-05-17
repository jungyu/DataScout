/**
 * 主題處理模組 - 用於管理 DaisyUI 的主題切換
 */

/**
 * 設置目前主題
 * @param {string} themeName - 主題名稱 ('light' 或 'dark')
 */
export function setTheme(themeName) {
    // 設定 HTML data-theme 屬性
    document.documentElement.setAttribute('data-theme', themeName);
    
    // 保存主題偏好到本地儲存
    localStorage.setItem('theme', themeName);
    
    // 更新切換開關狀態
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.checked = (themeName === 'dark');
    }
    
    console.log(`主題已切換為: ${themeName}`);
}

/**
 * 初始化主題處理
 */
export function initThemeHandler() {
    // 從儲存設定載入主題
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);
    
    // 設置主題切換事件
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('change', function(e) {
            const isDarkTheme = e.target.checked;
            setTheme(isDarkTheme ? 'dark' : 'light');
        });
        
        // 設置初始狀態
        themeToggle.checked = (savedTheme === 'dark');
    }
}

/**
 * 同步圖表主題與頁面主題
 * @param {Object} appState - 應用程式狀態
 * @returns {string} 適合目前頁面主題的圖表主題名稱
 */
export function syncChartThemeWithPageTheme(appState) {
    const currentTheme = localStorage.getItem('theme') || 'light';
    
    // 如果用戶選擇了特定的圖表主題，則使用用戶選擇
    if (appState.currentChartTheme !== 'auto') {
        return appState.currentChartTheme;
    }
    
    // 否則根據頁面主題自動選擇圖表主題
    return currentTheme === 'dark' ? 'dark' : 'default';
}
