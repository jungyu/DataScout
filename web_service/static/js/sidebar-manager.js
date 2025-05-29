/**
 * DataScout 侧边栏管理器
 * 管理侧边栏的展開收合、菜单項目互動等功能
 */

class SidebarManager {
    constructor() {
        this.init();
    }
    
    init() {
        console.log('侧边栏管理器初始化中...');
        this.setupEventListeners();
        this.setupMenuInteractions();
        console.log('侧边栏管理器初始化完成');
    }
    
    setupEventListeners() {
        // 處理菜單項目點擊
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('chart-type-item')) {
                this.handleChartTypeSelection(e.target);
            }
        });
    }
    
    setupMenuInteractions() {
        // 這裡可以添加更多侧边栏互動邏輯
        console.log('侧边栏互動設定完成');
    }
    
    handleChartTypeSelection(element) {
        // 移除其他項目的活躍狀態
        document.querySelectorAll('.chart-type-item').forEach(item => {
            item.classList.remove('active');
        });
        
        // 添加活躍狀態到選中項目
        element.classList.add('active');
        
        const chartType = element.dataset.type;
        console.log(`選中圖表類型: ${chartType}`);
        
        // 觸發事件，讓其他模組可以監聽
        document.dispatchEvent(new CustomEvent('chartTypeSelected', {
            detail: { type: chartType }
        }));
    }
}

// 創建全域實例
window.sidebarManager = new SidebarManager();

console.log('侧边栏管理器腳本已載入');
