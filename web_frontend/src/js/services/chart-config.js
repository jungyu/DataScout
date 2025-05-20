/**
 * 圖表配置服務
 * 
 * 提供各種圖表類型的配置選項
 */

export const chartConfig = {
  /**
   * 獲取圖表配置
   * @param {string} type - 圖表類型
   * @param {Object} data - 圖表數據
   * @param {Object} options - 附加選項
   * @returns {Object} 完整的 ApexCharts 配置
   */
  getConfig(type, data, options = {}) {
    // 基礎配置
    const baseConfig = {
      series: data.series,
      chart: {
        type: type,
        height: options.height || 350,
        width: options.width || '100%',
        toolbar: {
          show: options.showToolbar || false
        },
        fontFamily: 'Noto Sans TC, sans-serif'
      },
      colors: options.colors || ['#6366f1', '#4ade80', '#0ea5e9', '#f59e0b', '#ef4444'],
      theme: {
        mode: options.theme?.mode || 'light'
      },
      stroke: {
        curve: options.curve || 'smooth'
      },
      grid: {
        borderColor: options.theme?.mode === 'dark' ? '#334155' : '#e5e7eb',
        row: {
          colors: options.theme?.mode === 'dark' ? ['transparent', '#1e293b'] : ['transparent', '#f9fafb']
        }
      },
      dataLabels: {
        enabled: options.dataLabels || false
      }
    };
    
    // 特定圖表類型的配置
    switch (type) {
      case 'line':
      case 'area':
        return {
          ...baseConfig,
          xaxis: {
            categories: data.categories || [],
            labels: {
              style: {
                colors: options.theme?.mode === 'dark' ? '#94a3b8' : '#64748b'
              }
            }
          },
          yaxis: {
            labels: {
              style: {
                colors: options.theme?.mode === 'dark' ? '#94a3b8' : '#64748b'
              }
            }
          }
        };
        
      case 'bar':
      case 'column':
        return {
          ...baseConfig,
          plotOptions: {
            bar: {
              horizontal: type === 'bar',
              borderRadius: 4,
              columnWidth: '70%',
              ...options.plotOptions?.bar
            }
          },
          xaxis: {
            categories: data.categories || [],
            labels: {
              style: {
                colors: options.theme?.mode === 'dark' ? '#94a3b8' : '#64748b'
              }
            }
          }
        };
        
      case 'pie':
      case 'donut':
        return {
          ...baseConfig,
          labels: data.labels || [],
          legend: {
            position: 'bottom',
            ...options.legend
          }
        };
        
      case 'radar':
        return {
          ...baseConfig,
          xaxis: {
            categories: data.categories || []
          },
          yaxis: {
            show: false
          }
        };
        
      case 'bubble':
        return {
          ...baseConfig,
          xaxis: {
            type: 'numeric'
          },
          yaxis: {
            max: options.yaxisMax || undefined
          }
        };
        
      case 'scatter':
        return {
          ...baseConfig,
          xaxis: {
            type: 'numeric'
          },
          yaxis: {
            type: 'numeric'
          }
        };
        
      default:
        return baseConfig;
    }
  }
};
