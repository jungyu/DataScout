   
/**
 * 側邊欄組件 - Alpine.js 版本
 * 提供圖表類型導航和組織功能
 */
export class Sidebar {
    constructor() {
        this.componentName = 'sidebar';
    }

    /**
     * 初始化 Alpine.js 組件
     */
    init() {
        return {
            // 組件狀態
            collapsed: false,
            activeSection: 'basic',
            currentChart: 'line',
            
            // 圖表分類資料
            chartCategories: {
                basic: {
                    title: '基本圖表類型',
                    charts: [
                        { id: 'line', name: '折線圖', description: 'Line Chart', icon: '📈' },
                        { id: 'area', name: '區域圖', description: 'Area Chart', icon: '📊' },
                        { id: 'column', name: '柱狀圖', description: 'Column Chart', icon: '📊' },
                        { id: 'bar', name: '條形圖', description: 'Bar Chart', icon: '📊' },
                        { id: 'pie', name: '圓餅圖', description: 'Pie Chart', icon: '🥧' },
                        { id: 'donut', name: '環形圖', description: 'Donut Chart', icon: '🍩' },
                        { id: 'radar', name: '雷達圖', description: 'Radar Chart', icon: '🎯' },
                        { id: 'scatter', name: '散點圖', description: 'Scatter Chart', icon: '⭐' },
                        { id: 'heatmap', name: '熱力圖', description: 'Heat Map', icon: '🔥' },
                        { id: 'treemap', name: '樹狀圖', description: 'Treemap', icon: '🌳' }
                    ]
                },
                advanced: {
                    title: '進階圖表類型',
                    charts: [
                        { id: 'candlestick', name: '蠟燭圖', description: 'Candlestick', icon: '🕯️' },
                        { id: 'boxplot', name: '箱形圖', description: 'Boxplot', icon: '📦' },
                        { id: 'histogram', name: '直方圖', description: 'Histogram', icon: '📊' },
                        { id: 'bubble', name: '氣泡圖', description: 'Bubble', icon: '💭' },
                        { id: 'funnel', name: '漏斗圖', description: 'Funnel', icon: '🔽' },
                        { id: 'polar', name: '極區圖', description: 'Polar', icon: '🎯' }
                    ]
                },
                timeseries: {
                    title: '時間序列與監控',
                    charts: [
                        { id: 'timeseries', name: '時間序列', description: 'Time Series', icon: '⏰' },
                        { id: 'realtime', name: '實時圖表', description: 'Real-time', icon: '🔴' },
                        { id: 'range', name: '範圍選擇器', description: 'Range Selector', icon: '📅' },
                        { id: 'annotations', name: '標註圖表', description: 'Annotations', icon: '📝' }
                    ]
                },
                mixed: {
                    title: '混合圖表',
                    charts: [
                        { id: 'combo', name: '組合圖表', description: 'Combo Chart', icon: '🎭' },
                        { id: 'multiple-y', name: '多Y軸', description: 'Multiple Y-axis', icon: '📊' },
                        { id: 'synchronized', name: '同步圖表', description: 'Synchronized', icon: '🔄' }
                    ]
                }
            },

            /**
             * 切換側邊欄摺疊狀態
             */
            toggleCollapse() {
                this.collapsed = !this.collapsed;
                
                // 觸發自訂事件，通知其他組件
                this.$dispatch('sidebar-toggle', { collapsed: this.collapsed });
            },

            /**
             * 設定當前活動的分類
             */
            setActiveSection(sectionId) {
                this.activeSection = sectionId;
            },

            /**
             * 選擇圖表類型
             */
            selectChart(chartId, categoryId = null) {
                this.currentChart = chartId;
                
                // 觸發圖表切換事件
                this.$dispatch('chart-selected', { 
                    chartId, 
                    categoryId: categoryId || this.activeSection 
                });

                // 如果在手機版本，自動摺疊側邊欄
                if (window.innerWidth < 1024) {
                    this.collapsed = true;
                }
            },

            /**
             * 檢查圖表是否為當前選中的圖表
             */
            isCurrentChart(chartId) {
                return this.currentChart === chartId;
            },

            /**
             * 檢查分類是否為當前活動分類
             */
            isActiveSection(sectionId) {
                return this.activeSection === sectionId;
            },

            /**
             * 取得圖表的完整URL
             */
            getChartUrl(chartId) {
                // 對於 Alpine.js 架構，使用雜湊路由
                return `#/chart/${chartId}`;
            },

            /**
             * 搜尋圖表
             */
            searchCharts(query) {
                if (!query) return [];
                
                const results = [];
                query = query.toLowerCase();
                
                Object.entries(this.chartCategories).forEach(([categoryId, category]) => {
                    category.charts.forEach(chart => {
                        if (chart.name.toLowerCase().includes(query) || 
                            chart.description.toLowerCase().includes(query) ||
                            chart.id.includes(query)) {
                            results.push({ 
                                ...chart, 
                                categoryId, 
                                categoryTitle: category.title 
                            });
                        }
                    });
                });
                
                return results;
            },

            /**
             * 取得所有圖表的總數
             */
            getTotalChartCount() {
                return Object.values(this.chartCategories)
                    .reduce((total, category) => total + category.charts.length, 0);
            },

            /**
             * 處理鍵盤導航
             */
            handleKeydown(event) {
                switch(event.key) {
                    case 'ArrowUp':
                        event.preventDefault();
                        this.navigatePrevious();
                        break;
                    case 'ArrowDown':
                        event.preventDefault();
                        this.navigateNext();
                        break;
                    case 'Enter':
                        event.preventDefault();
                        this.activateCurrentChart();
                        break;
                    case 'Escape':
                        this.collapsed = true;
                        break;
                }
            },

            /**
             * 導航到上一個圖表
             */
            navigatePrevious() {
                const currentCategory = this.chartCategories[this.activeSection];
                const currentIndex = currentCategory.charts.findIndex(chart => chart.id === this.currentChart);
                
                if (currentIndex > 0) {
                    this.currentChart = currentCategory.charts[currentIndex - 1].id;
                } else if (currentIndex === 0) {
                    // 跳到上一個分類的最後一個圖表
                    const categories = Object.keys(this.chartCategories);
                    const currentCategoryIndex = categories.indexOf(this.activeSection);
                    
                    if (currentCategoryIndex > 0) {
                        const prevCategory = categories[currentCategoryIndex - 1];
                        this.activeSection = prevCategory;
                        const prevCategoryCharts = this.chartCategories[prevCategory].charts;
                        this.currentChart = prevCategoryCharts[prevCategoryCharts.length - 1].id;
                    }
                }
            },

            /**
             * 導航到下一個圖表
             */
            navigateNext() {
                const currentCategory = this.chartCategories[this.activeSection];
                const currentIndex = currentCategory.charts.findIndex(chart => chart.id === this.currentChart);
                
                if (currentIndex < currentCategory.charts.length - 1) {
                    this.currentChart = currentCategory.charts[currentIndex + 1].id;
                } else if (currentIndex === currentCategory.charts.length - 1) {
                    // 跳到下一個分類的第一個圖表
                    const categories = Object.keys(this.chartCategories);
                    const currentCategoryIndex = categories.indexOf(this.activeSection);
                    
                    if (currentCategoryIndex < categories.length - 1) {
                        const nextCategory = categories[currentCategoryIndex + 1];
                        this.activeSection = nextCategory;
                        this.currentChart = this.chartCategories[nextCategory].charts[0].id;
                    }
                }
            },

            /**
             * 啟動當前選中的圖表
             */
            activateCurrentChart() {
                this.selectChart(this.currentChart, this.activeSection);
            },

            /**
             * 初始化組件
             */
            mounted() {
                // 監聽視窗大小變化
                window.addEventListener('resize', () => {
                    if (window.innerWidth >= 1024) {
                        this.collapsed = false;
                    }
                });

                // 預設選中第一個圖表
                if (!this.currentChart) {
                    const firstCategory = Object.keys(this.chartCategories)[0];
                    this.activeSection = firstCategory;
                    this.currentChart = this.chartCategories[firstCategory].charts[0].id;
                }
            }
        };
    }

    /**
     * 產生側邊欄 HTML 模板
     */
    getTemplate() {
        return `
        <div 
            x-data="sidebar" 
            x-init="mounted()"
            @keydown.window="handleKeydown($event)"
            :class="{ 'w-16': collapsed, 'w-64': !collapsed }" 
            class="bg-primary text-primary-content overflow-y-auto transition-all duration-300 ease-in-out flex flex-col"
        >
            <!-- 標題列 -->
            <div class="p-4 flex items-center justify-between border-b border-primary-focus">
                <div x-show="!collapsed" x-transition class="text-2xl font-bold">
                    DataScout
                </div>
                <button 
                    @click="toggleCollapse()"
                    class="btn btn-ghost btn-sm text-primary-content hover:bg-primary-focus"
                    :title="collapsed ? '展開側邊欄' : '摺疊側邊欄'"
                >
                    <svg x-show="collapsed" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                    </svg>
                    <svg x-show="!collapsed" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
                    </svg>
                </button>
            </div>

            <!-- 圖表分類選單 -->
            <div x-show="!collapsed" x-transition class="flex-1 p-4">
                <div class="space-y-2">
                    <template x-for="(category, categoryId) in chartCategories" :key="categoryId">
                        <div class="collapse collapse-arrow border-b border-primary-focus">
                            <input 
                                type="radio" 
                                name="sidebar-accordion" 
                                :checked="isActiveSection(categoryId)"
                                @change="setActiveSection(categoryId)"
                            />
                            <div class="collapse-title font-medium text-sm bg-primary-focus bg-opacity-50 text-white">
                                <span x-text="category.title"></span>
                                <span class="badge badge-secondary badge-sm ml-2" x-text="category.charts.length"></span>
                            </div>
                            <div class="collapse-content p-0 bg-primary/5">
                                <ul class="menu menu-sm py-2">
                                    <template x-for="chart in category.charts" :key="chart.id">
                                        <li>
                                            <a 
                                                @click="selectChart(chart.id, categoryId)"
                                                :class="{ 
                                                    'bg-accent text-white': isCurrentChart(chart.id),
                                                    'hover:bg-accent hover:text-white active:bg-accent/80': !isCurrentChart(chart.id)
                                                }"
                                                class="text-primary-content font-medium cursor-pointer"
                                            >
                                                <span x-text="chart.icon" class="text-lg"></span>
                                                <div class="flex flex-col">
                                                    <span x-text="chart.name"></span>
                                                    <span x-text="chart.description" class="text-xs opacity-70"></span>
                                                </div>
                                            </a>
                                        </li>
                                    </template>
                                </ul>
                            </div>
                        </div>
                    </template>
                </div>
            </div>

            <!-- 摺疊狀態下的快速選單 -->
            <div x-show="collapsed" x-transition class="flex-1 p-2">
                <div class="space-y-1">
                    <template x-for="(category, categoryId) in chartCategories" :key="categoryId">
                        <div>
                            <template x-for="chart in category.charts" :key="chart.id">
                                <button
                                    @click="selectChart(chart.id, categoryId)"
                                    :class="{ 
                                        'bg-accent text-white': isCurrentChart(chart.id),
                                        'hover:bg-primary-focus': !isCurrentChart(chart.id)
                                    }"
                                    class="w-12 h-12 flex items-center justify-center rounded-lg mb-1 transition-colors"
                                    :title="chart.name + ' (' + chart.description + ')'"
                                >
                                    <span x-text="chart.icon" class="text-lg"></span>
                                </button>
                            </template>
                        </div>
                    </template>
                </div>
            </div>

            <!-- 統計資訊 -->
            <div x-show="!collapsed" x-transition class="p-4 border-t border-primary-focus">
                <div class="text-xs opacity-70">
                    <span x-text="'總計 ' + getTotalChartCount() + ' 種圖表類型'"></span>
                </div>
            </div>
        </div>
        `;
    }
}

// 匯出類別
export default Sidebar;