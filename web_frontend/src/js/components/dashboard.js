/**
 * 儀表板組件
 * 
 * 此組件負責管理儀表板佈局和總體操作
 */
import ApexCharts from 'apexcharts';

export function initDashboard() {
  Alpine.data('dashboard', () => ({
    // 初始加載狀態
    loading: true,
    
    // 儀表板摘要數據
    summary: {
      visitors: { count: 45890, trend: -0.5 },
      revenue: { amount: 48575, trend: 3.84 },
      orders: { count: 4800, trend: 1.46 },
      events: { count: 145, trend: 0 },
      profits: { amount: 24351, trend: 1.6 }
    },
    
    // 初始化方法
    init() {
      this.initProfitExpenseChart();
      this.initVisitorMap();
      this.fetchDashboardData();
    },
    
    // 獲取儀表板數據
    async fetchDashboardData() {
      try {
        this.loading = true;
        // 使用 API 服務獲取儀表板數據
        const data = await window.apiService.getDashboardData();
        if (data) {
          // 更新摘要數據
          this.summary = data.summary;
          // 更新圖表數據
        }
      } catch (error) {
        console.error('獲取儀表板數據失敗:', error);
      } finally {
        this.loading = false;
      }
    },
    
    // 利潤/費用分析圖表
    initProfitExpenseChart() {
      const options = {
        series: [{
          name: 'Profit',
          data: [450, 480, 500, 450, 520, 580, 550, 570, 620, 750, 860, 950]
        }, {
          name: 'Expenses',
          data: [220, 380, 450, 420, 220, 250, 320, 220, 430, 220, 450, 780]
        }],
        chart: {
          type: 'bar',
          height: 350,
          toolbar: {
            show: false
          }
        },
        colors: ['#6366f1', '#4ade80'],
        plotOptions: {
          bar: {
            borderRadius: 4,
            columnWidth: '45%',
          },
        },
        xaxis: {
          categories: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        },
        // 深淺模式自適應
        theme: {
          mode: document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light'
        }
      };
      
      setTimeout(() => {
        const chart = new ApexCharts(document.querySelector("#profit-expense-chart"), options);
        chart.render();
        
        // 監聽主題變化重新渲染圖表
        const observer = new MutationObserver((mutations) => {
          mutations.forEach((mutation) => {
            if (mutation.attributeName === 'data-theme') {
              chart.updateOptions({
                theme: {
                  mode: document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light'
                }
              });
            }
          });
        });
        
        observer.observe(document.documentElement, { attributes: true });
      }, 0);
    },
    
    // 訪客地圖
    initVisitorMap() {
      // 這裡可以初始化地圖視覺化組件
      // 例如使用 ApexCharts 的地圖功能或其他地圖庫
    }
  }));
}
