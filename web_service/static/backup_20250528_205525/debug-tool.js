// debug-tool.js - 用於調試前端加載問題
// 此工具將檢查頁面上的組件載入情況，並提供詳細的診斷信息

(function() {
    // 檢查環境 - 支援多個開發端口
    const isDevelopment = ['5173', '5174', '5175', '3000', '8080'].includes(window.location.port);
    const environment = isDevelopment ? '開發環境' : '生產環境';
    
    // 檢查組件路徑處理
    function analyzePaths() {
        const componentsContainers = document.querySelectorAll('[data-component]');
        const paths = Array.from(componentsContainers).map(el => el.getAttribute('data-component'));
        
        console.log('組件路徑分析:');
        paths.forEach(path => {
            console.log(`- 原始路徑: ${path}`);
            // 在這裡模擬路徑處理邏輯，與組件加載器相同
            let processedPath = path;
            if (isDevelopment) {
                if (path.startsWith('/')) {
                    processedPath = path.substring(1);
                }
                console.log(`  處理後的開發環境路徑: ${processedPath}`);
            } else {
                if (!path.startsWith('/')) {
                    processedPath = '/' + path;
                }
                if (!path.startsWith('/static')) {
                    processedPath = '/static' + processedPath;
                }
                console.log(`  處理後的生產環境路徑: ${processedPath}`);
            }
        });
    }
    
    // 在頁面加載後執行檢查
    window.addEventListener('DOMContentLoaded', function() {
        console.log(`%c DataScout 前端調試工具 %c ${environment} `, 
            'background:#4CAF50; color:white; padding:4px;', 
            'background:#2196F3; color:white; padding:4px;');
        
        // 分析組件路徑
        analyzePaths();
        
        // 延遲執行，確保組件有時間載入
        setTimeout(checkComponents, 1000);
    });
    
    // 檢查組件加載情況
    function checkComponents() {
        console.log('正在檢查組件加載情況...');
        
        // 獲取所有組件容器
        const components = document.querySelectorAll('[data-component]');
        console.log(`找到 ${components.length} 個組件容器`);
        
        // 檢查每個組件
        components.forEach((component, index) => {
            const path = component.getAttribute('data-component');
            const id = component.id || `未命名組件-${index}`;
            const isEmpty = component.innerHTML.trim() === '';
            
            if (isEmpty) {
                console.error(`❌ 組件 "${id}" (${path}) 未載入內容`);
            } else {
                console.log(`✅ 組件 "${id}" (${path}) 已成功載入`);
            }
        });
        
        // 檢查腳本加載情況
        const scripts = Array.from(document.scripts).map(s => s.src).filter(src => src);
        console.log('已載入的腳本:', scripts);
        
        // 創建可視化調試面板
        createDebugPanel(components);
    }
    
    // 創建可視化調試面板
    function createDebugPanel(components) {
        // 創建調試面板容器
        const panel = document.createElement('div');
        panel.style.position = 'fixed';
        panel.style.bottom = '10px';
        panel.style.right = '10px';
        panel.style.width = '300px';
        panel.style.background = 'rgba(0,0,0,0.8)';
        panel.style.color = 'white';
        panel.style.padding = '10px';
        panel.style.borderRadius = '5px';
        panel.style.zIndex = '9999';
        panel.style.fontFamily = 'monospace';
        panel.style.fontSize = '12px';
        
        // 添加標題
        const title = document.createElement('div');
        title.textContent = `DataScout 調試面板 (${environment})`;
        title.style.fontWeight = 'bold';
        title.style.marginBottom = '5px';
        title.style.borderBottom = '1px solid #555';
        title.style.paddingBottom = '5px';
        panel.appendChild(title);
        
        // 添加組件列表
        const list = document.createElement('ul');
        list.style.listStyle = 'none';
        list.style.padding = '0';
        list.style.margin = '0';
        
        components.forEach((component, index) => {
            const path = component.getAttribute('data-component');
            const id = component.id || `未命名組件-${index}`;
            const isEmpty = component.innerHTML.trim() === '';
            
            const item = document.createElement('li');
            item.style.padding = '3px 0';
            item.style.borderBottom = '1px solid #333';
            item.style.color = isEmpty ? '#ff5252' : '#4caf50';
            item.textContent = `${isEmpty ? '❌' : '✅'} ${id}`;
            
            // 添加懸停提示
            item.title = path;
            
            list.appendChild(item);
        });
        
        panel.appendChild(list);
        
        // 添加關閉按鈕
        const closeBtn = document.createElement('div');
        closeBtn.textContent = '關閉';
        closeBtn.style.padding = '5px';
        closeBtn.style.textAlign = 'center';
        closeBtn.style.marginTop = '10px';
        closeBtn.style.background = '#555';
        closeBtn.style.cursor = 'pointer';
        closeBtn.style.borderRadius = '3px';
        closeBtn.onclick = () => panel.remove();
        
        panel.appendChild(closeBtn);
        
        // 將面板添加到頁面
        document.body.appendChild(panel);
    }
})();
