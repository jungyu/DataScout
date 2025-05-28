// 基礎圖表組件類別 - 所有圖表組件的基礎
import ApexCharts from 'apexcharts';

/**
 * 基礎圖表組件
 * 提供所有圖表組件的共用功能
 */
export class BaseChart {
  constructor(containerId, data, options = {}) {
    this.containerId = containerId;
    this.data = data;
    this.options = options;
    this.chart = null;
    this.isInitialized = false;
  }

  /**
   * 獲取預設圖表配置
   * 子類別應該覆寫此方法以提供特定的圖表設定
   */
  getDefaultOptions() {
    return {
      chart: {
        height: 350,
        toolbar: {
          show: true,
          tools: {
            download: true,
            selection: true,
            zoom: true,
            zoomin: true,
            zoomout: true,
            pan: true,
            reset: true
          }
        },
        background: 'transparent',
        animations: {
          enabled: true,
          easing: 'easeinout',
          speed: 800
        }
      },
      theme: {
        mode: 'light',
        palette: 'palette1'
      },
      responsive: [{
        breakpoint: 480,
        options: {
          chart: {
            height: 300
          },
          legend: {
            position: 'bottom'
          }
        }
      }]
    };
  }

  /**
   * 合併配置選項
   */
  mergeOptions(defaultOptions, userOptions) {
    return {
      ...defaultOptions,
      ...userOptions,
      chart: {
        ...defaultOptions.chart,
        ...userOptions.chart
      }
    };
  }

  /**
   * 初始化圖表
   */
  init() {
    try {
      if (this.isInitialized) {
        console.warn(`圖表 ${this.containerId} 已經初始化`);
        return;
      }

      const container = document.querySelector(`#${this.containerId}`);
      if (!container) {
        throw new Error(`找不到圖表容器元素 #${this.containerId}`);
      }

      // 清除現有圖表實例
      this.destroy();

      // 獲取圖表配置
      const defaultOptions = this.getDefaultOptions();
      const chartOptions = this.mergeOptions(defaultOptions, this.options);
      
      // 設定資料
      if (this.data) {
        chartOptions.series = this.formatData(this.data);
      }

      // 建立新的圖表實例
      this.chart = new ApexCharts(container, chartOptions);
      this.chart.render();
      this.isInitialized = true;

      // 記錄實例以便後續清理
      if (!window.chartInstances) {
        window.chartInstances = {};
      }
      window.chartInstances[this.containerId] = this.chart;

      // 發送成功通知
      this.showNotification('圖表載入成功', 'success');
      
      console.log(`${this.constructor.name} 初始化完成:`, this.containerId);

    } catch (error) {
      this.handleError(error);
    }
  }

  /**
   * 格式化資料 - 子類別應該覆寫此方法
   */
  formatData(data) {
    return Array.isArray(data) ? data : [{ name: '資料', data: data }];
  }

  /**
   * 更新圖表資料
   */
  updateData(newData) {
    try {
      if (!this.chart) {
        throw new Error('圖表尚未初始化');
      }

      this.data = newData;
      const formattedData = this.formatData(newData);
      this.chart.updateSeries(formattedData);
      
      console.log(`${this.constructor.name} 資料更新完成`);
    } catch (error) {
      this.handleError(error);
    }
  }

  /**
   * 更新圖表選項
   */
  updateOptions(newOptions) {
    try {
      if (!this.chart) {
        throw new Error('圖表尚未初始化');
      }

      this.options = { ...this.options, ...newOptions };
      this.chart.updateOptions(newOptions);
      
      console.log(`${this.constructor.name} 選項更新完成`);
    } catch (error) {
      this.handleError(error);
    }
  }

  /**
   * 重新渲染圖表
   */
  rerender(newData = null, newOptions = null) {
    if (newData) this.data = newData;
    if (newOptions) this.options = { ...this.options, ...newOptions };
    
    this.destroy();
    this.isInitialized = false;
    this.init();
  }

  /**
   * 銷毀圖表
   */
  destroy() {
    if (this.chart) {
      this.chart.destroy();
      this.chart = null;
    }
    
    // 清理全域記錄
    if (window.chartInstances && window.chartInstances[this.containerId]) {
      delete window.chartInstances[this.containerId];
    }
    
    this.isInitialized = false;
  }

  /**
   * 匯出圖表為 PNG
   */
  exportToPNG(filename = null) {
    if (!this.chart) {
      this.showNotification('圖表尚未初始化，無法匯出', 'error');
      return;
    }

    const fileName = filename || `${this.containerId}-chart.png`;
    
    this.chart.dataURI().then(({ imgURI }) => {
      const link = document.createElement('a');
      link.href = imgURI;
      link.download = fileName;
      link.click();
      this.showNotification('PNG 檔案已下載', 'success');
    }).catch(error => {
      this.handleError(error, 'PNG 匯出失敗');
    });
  }

  /**
   * 匯出圖表為 SVG
   */
  exportToSVG(filename = null) {
    if (!this.chart) {
      this.showNotification('圖表尚未初始化，無法匯出', 'error');
      return;
    }

    const fileName = filename || `${this.containerId}-chart.svg`;
    
    this.chart.dataURI('svg').then(({ imgURI }) => {
      const link = document.createElement('a');
      link.href = imgURI;
      link.download = fileName;
      link.click();
      this.showNotification('SVG 檔案已下載', 'success');
    }).catch(error => {
      this.handleError(error, 'SVG 匯出失敗');
    });
  }

  /**
   * 錯誤處理
   */
  handleError(error, context = '圖表操作') {
    console.error(`${this.constructor.name} 錯誤:`, error);
    
    const errorMessage = `${context}失敗: ${error.message}`;
    this.showNotification(errorMessage, 'error');
    
    // 在圖表容器中顯示錯誤
    const container = document.querySelector(`#${this.containerId}`);
    if (container) {
      container.innerHTML = `
        <div class="flex flex-col items-center justify-center h-full p-8">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 text-error mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <p class="text-base text-error font-medium text-center">${errorMessage}</p>
          <button class="btn btn-sm btn-outline btn-error mt-4" onclick="location.reload()">
            重新整理頁面
          </button>
        </div>
      `;
    }
  }

  /**
   * 顯示通知 (如果有通知系統可用)
   */
  showNotification(message, type = 'info') {
    if (window.showNotification && typeof window.showNotification === 'function') {
      window.showNotification(message, type);
    } else {
      console.log(`[${type.toUpperCase()}] ${message}`);
    }
  }

  /**
   * 重設大小 (響應式處理)
   */
  resize() {
    if (this.chart) {
      this.chart.resize();
    }
  }

  /**
   * 取得圖表實例 (用於進階操作)
   */
  getChartInstance() {
    return this.chart;
  }

  /**
   * 檢查圖表是否已初始化
   */
  isReady() {
    return this.isInitialized && this.chart !== null;
  }
}
