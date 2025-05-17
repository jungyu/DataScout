/**
 * 圖表容器初始化器
 * 確保圖表畫布正確初始化
 */
(function() {
    console.log('圖表容器初始化器已載入');
    
    document.addEventListener('DOMContentLoaded', function() {
        console.log('初始化圖表容器...');
        initChartContainer();
        
        // 監聽視窗大小變化
        window.addEventListener('resize', debounce(function() {
            console.log('視窗大小變化，重新調整圖表尺寸');
            initChartContainer();
        }, 200));
    });
    
    /**
     * 初始化圖表容器
     */
    function initChartContainer() {
        // 獲取圖表容器元素
        const chartContainer = document.getElementById('chartContainer');
        if (!chartContainer) {
            console.error('找不到圖表容器元素');
            return false;
        }
        
        // 獲取或創建圖表畫布
        let canvas = document.getElementById('chartCanvas');
        if (!canvas) {
            console.log('找不到圖表畫布，將創建新畫布');
            canvas = document.createElement('canvas');
            canvas.id = 'chartCanvas';
            canvas.classList.add('w-full', 'h-full');
            chartContainer.appendChild(canvas);
        }
        
        // 確保畫布尺寸正確
        const containerWidth = chartContainer.clientWidth;
        const containerHeight = chartContainer.clientHeight;
        
        // 設置畫布尺寸
        canvas.width = containerWidth * 2;  // 高解析度 (2x)
        canvas.height = containerHeight * 2;
        canvas.style.width = `${containerWidth}px`;
        canvas.style.height = `${containerHeight}px`;
        
        // 確保畫布背景是透明的
        const ctx = canvas.getContext('2d');
        if (ctx) {
            ctx.fillStyle = 'rgba(255, 255, 255, 0)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
        }
        
        console.log(`圖表容器初始化完成，尺寸: ${containerWidth}x${containerHeight}`);
        return true;
    }
    
    /**
     * 防抖函數
     */
    function debounce(func, wait) {
        let timeout;
        return function() {
            const context = this, args = arguments;
            clearTimeout(timeout);
            timeout = setTimeout(function() {
                func.apply(context, args);
            }, wait);
        };
    }
    
    // 將初始化函數暴露為全局方法
    window.initChartContainer = initChartContainer;
})();
