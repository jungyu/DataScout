# -*- coding: utf-8 -*-
"""
DataScout 圖表字型應用範例
展示如何在不同類型的圖表中正確使用中文字型
"""

import sys
import os
from pathlib import Path
import numpy as np

# 添加專案路徑
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.chart_fonts import setup_chinese_fonts


def create_matplotlib_examples():
    """創建 Matplotlib 中文字型範例"""
    try:
        import matplotlib.pyplot as plt
        
        # 設定中文字型
        font_manager = setup_chinese_fonts()
        
        # 創建多個圖表範例
        examples = [
            create_line_chart_example,
            create_bar_chart_example,
            create_pie_chart_example,
            create_scatter_plot_example,
            create_heatmap_example
        ]
        
        output_dir = Path(__file__).parent.parent / 'data' / 'temp' / 'font_examples'
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for i, example_func in enumerate(examples):
            try:
                example_func(output_dir, i+1)
                print(f"✓ 範例 {i+1} 創建成功")
            except Exception as e:
                print(f"❌ 範例 {i+1} 創建失敗: {e}")
        
        print(f"\n所有範例圖表已儲存至: {output_dir}")
        
    except ImportError:
        print("❌ Matplotlib 未安裝，無法創建範例")


def create_line_chart_example(output_dir, index):
    """創建線圖範例"""
    import matplotlib.pyplot as plt
    
    # 模擬股價數據
    days = range(1, 31)
    stock_a = 100 + np.cumsum(np.random.randn(30) * 2)
    stock_b = 95 + np.cumsum(np.random.randn(30) * 1.5)
    
    plt.figure(figsize=(12, 8))
    plt.plot(days, stock_a, label='台積電 (2330)', linewidth=2, marker='o', markersize=4)
    plt.plot(days, stock_b, label='聯發科 (2454)', linewidth=2, marker='s', markersize=4)
    
    plt.title('台股主要標的月線走勢圖', fontsize=18, fontweight='bold', pad=20)
    plt.xlabel('交易日', fontsize=14)
    plt.ylabel('股價 (新台幣)', fontsize=14)
    plt.legend(fontsize=12)
    plt.grid(True, alpha=0.3)
    
    # 添加註解
    plt.annotate('突破新高點', 
                xy=(20, stock_a[19]), xytext=(25, stock_a[19] + 5),
                arrowprops=dict(arrowstyle='->', color='red'),
                fontsize=11, color='red')
    
    plt.tight_layout()
    plt.savefig(output_dir / f'{index:02d}_line_chart.png', dpi=150, bbox_inches='tight')
    plt.close()


def create_bar_chart_example(output_dir, index):
    """創建柱狀圖範例"""
    import matplotlib.pyplot as plt
    
    # 產業數據
    industries = ['科技業', '金融業', '傳統產業', '生技醫療', '綠能環保']
    revenues = [1250, 890, 650, 420, 380]
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    
    plt.figure(figsize=(10, 8))
    bars = plt.bar(industries, revenues, color=colors, alpha=0.8, edgecolor='black', linewidth=1)
    
    plt.title('2024年各產業營收表現 (億元)', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('產業別', fontsize=14)
    plt.ylabel('營收 (億元)', fontsize=14)
    
    # 在柱子上添加數值標籤
    for bar, revenue in zip(bars, revenues):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 10,
                f'{revenue}億', ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    plt.ylim(0, max(revenues) * 1.2)
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_dir / f'{index:02d}_bar_chart.png', dpi=150, bbox_inches='tight')
    plt.close()


def create_pie_chart_example(output_dir, index):
    """創建圓餅圖範例"""
    import matplotlib.pyplot as plt
    
    # 市場份額數據
    companies = ['台積電', '聯發科', '鴻海', '台達電', '其他']
    market_share = [45, 25, 15, 10, 5]
    colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99', '#c2c2f0']
    explode = (0.1, 0, 0, 0, 0)  # 突出顯示台積電
    
    plt.figure(figsize=(10, 8))
    wedges, texts, autotexts = plt.pie(market_share, labels=companies, autopct='%1.1f%%',
                                      startangle=90, colors=colors, explode=explode,
                                      shadow=True, textprops={'fontsize': 12})
    
    plt.title('台灣科技業市場份額分布', fontsize=16, fontweight='bold', pad=20)
    
    # 美化百分比文字
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    
    plt.axis('equal')
    plt.tight_layout()
    plt.savefig(output_dir / f'{index:02d}_pie_chart.png', dpi=150, bbox_inches='tight')
    plt.close()


def create_scatter_plot_example(output_dir, index):
    """創建散點圖範例"""
    import matplotlib.pyplot as plt
    
    # 模擬公司數據
    np.random.seed(42)
    companies = ['台積電', '聯發科', '鴻海', '台達電', '華碩', '宏碁', '廣達', '和碩']
    revenue = np.random.normal(500, 200, len(companies))
    profit_margin = np.random.normal(15, 5, len(companies))
    market_cap = np.random.normal(1000, 500, len(companies))
    
    plt.figure(figsize=(12, 8))
    scatter = plt.scatter(revenue, profit_margin, s=market_cap/10, 
                         c=range(len(companies)), cmap='viridis', 
                         alpha=0.7, edgecolors='black', linewidth=1)
    
    plt.title('台灣科技公司營收與獲利率關係圖', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('營收 (億元)', fontsize=14)
    plt.ylabel('獲利率 (%)', fontsize=14)
    
    # 添加公司名稱標籤
    for i, company in enumerate(companies):
        plt.annotate(company, (revenue[i], profit_margin[i]), 
                    xytext=(5, 5), textcoords='offset points',
                    fontsize=10, alpha=0.8)
    
    plt.colorbar(scatter, label='公司編號')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_dir / f'{index:02d}_scatter_plot.png', dpi=150, bbox_inches='tight')
    plt.close()


def create_heatmap_example(output_dir, index):
    """創建熱力圖範例"""
    import matplotlib.pyplot as plt
    
    # 模擬股票相關係數矩陣
    stocks = ['台積電', '聯發科', '鴻海', '台達電', '華碩']
    correlation_matrix = np.random.rand(len(stocks), len(stocks))
    # 使矩陣對稱
    correlation_matrix = (correlation_matrix + correlation_matrix.T) / 2
    np.fill_diagonal(correlation_matrix, 1)
    
    plt.figure(figsize=(10, 8))
    im = plt.imshow(correlation_matrix, cmap='RdYlBu_r', aspect='auto', vmin=-1, vmax=1)
    
    plt.title('台股主要標的相關係數熱力圖', fontsize=16, fontweight='bold', pad=20)
    
    # 設定座標軸標籤
    plt.xticks(range(len(stocks)), stocks, rotation=45, ha='right')
    plt.yticks(range(len(stocks)), stocks)
    
    # 添加數值標籤
    for i in range(len(stocks)):
        for j in range(len(stocks)):
            text = plt.text(j, i, f'{correlation_matrix[i, j]:.2f}',
                           ha="center", va="center", color="black", fontweight='bold')
    
    # 添加顏色條
    cbar = plt.colorbar(im)
    cbar.set_label('相關係數', rotation=270, labelpad=20, fontsize=12)
    
    plt.tight_layout()
    plt.savefig(output_dir / f'{index:02d}_heatmap.png', dpi=150, bbox_inches='tight')
    plt.close()


def generate_apexcharts_config():
    """生成 ApexCharts 中文字型配置 JavaScript"""
    
    js_content = '''
/**
 * DataScout ApexCharts 中文字型配置
 * 統一配置所有 ApexCharts 圖表的字型設定
 */

// 全域字型配置
window.DataScoutChartConfig = {
    // 基礎字型設定
    fonts: {
        primary: "'Noto Sans TC', 'PingFang TC', 'Microsoft JhengHei', 'Heiti TC', sans-serif",
        fallback: "Arial, sans-serif",
        mono: "'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace"
    },
    
    // 預設 ApexCharts 配置
    getDefaultConfig: function() {
        return {
            chart: {
                fontFamily: this.fonts.primary,
                toolbar: {
                    show: true
                }
            },
            title: {
                style: {
                    fontFamily: this.fonts.primary,
                    fontSize: '16px',
                    fontWeight: '600',
                    color: '#263238'
                }
            },
            subtitle: {
                style: {
                    fontFamily: this.fonts.primary,
                    fontSize: '14px',
                    color: '#607d8b'
                }
            },
            legend: {
                fontFamily: this.fonts.primary,
                fontSize: '12px'
            },
            dataLabels: {
                style: {
                    fontFamily: this.fonts.primary,
                    fontSize: '11px'
                }
            },
            xaxis: {
                labels: {
                    style: {
                        fontFamily: this.fonts.primary,
                        fontSize: '12px',
                        colors: '#607d8b'
                    }
                },
                title: {
                    style: {
                        fontFamily: this.fonts.primary,
                        fontSize: '13px',
                        color: '#607d8b'
                    }
                }
            },
            yaxis: {
                labels: {
                    style: {
                        fontFamily: this.fonts.primary,
                        fontSize: '12px',
                        colors: '#607d8b'
                    }
                },
                title: {
                    style: {
                        fontFamily: this.fonts.primary,
                        fontSize: '13px',
                        color: '#607d8b'
                    }
                }
            },
            tooltip: {
                style: {
                    fontFamily: this.fonts.primary,
                    fontSize: '12px'
                }
            }
        };
    },
    
    // 合併自訂配置與預設配置
    mergeConfig: function(customConfig) {
        const defaultConfig = this.getDefaultConfig();
        return this.deepMerge(defaultConfig, customConfig);
    },
    
    // 深度合併物件
    deepMerge: function(target, source) {
        for (const key in source) {
            if (source[key] && typeof source[key] === 'object' && !Array.isArray(source[key])) {
                if (!target[key]) target[key] = {};
                this.deepMerge(target[key], source[key]);
            } else {
                target[key] = source[key];
            }
        }
        return target;
    },
    
    // 常用顏色配置
    colors: {
        primary: ['#1976d2', '#388e3c', '#f57c00', '#d32f2f', '#7b1fa2'],
        success: ['#4caf50', '#66bb6a', '#81c784', '#a5d6a7', '#c8e6c9'],
        warning: ['#ff9800', '#ffb74d', '#ffcc02', '#ffd54f', '#ffe082'],
        error: ['#f44336', '#ef5350', '#e57373', '#ef9a9a', '#ffcdd2'],
        info: ['#2196f3', '#42a5f5', '#64b5f6', '#90caf9', '#bbdefb'],
        neutral: ['#607d8b', '#78909c', '#90a4ae', '#b0bec5', '#cfd8dc']
    }
};

// 初始化函數
window.initDataScoutCharts = function() {
    console.log('DataScout 圖表字型配置已載入');
    
    // 檢查是否有 ApexCharts
    if (typeof ApexCharts !== 'undefined') {
        console.log('ApexCharts 已就緒，字型配置生效');
    } else {
        console.warn('ApexCharts 未載入，請確保已引入 ApexCharts 庫');
    }
};

// 頁面載入完成後自動初始化
document.addEventListener('DOMContentLoaded', function() {
    window.initDataScoutCharts();
});

// 範例使用方法
window.createExampleChart = function(elementId) {
    const config = window.DataScoutChartConfig.mergeConfig({
        series: [{
            name: '銷售額',
            data: [30, 40, 35, 50, 49, 60, 70, 91, 125]
        }],
        chart: {
            type: 'line',
            height: 350
        },
        title: {
            text: '月度銷售趨勢圖'
        },
        xaxis: {
            categories: ['一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月']
        }
    });
    
    const chart = new ApexCharts(document.querySelector(elementId), config);
    chart.render();
    
    return chart;
};
'''
    
    # 寫入 JavaScript 文件
    js_path = Path(__file__).parent.parent / 'web_service' / 'static' / 'js' / 'chart-font-config.js'
    js_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(js_content)
    
    print(f"✓ ApexCharts 字型配置 JavaScript 已生成: {js_path}")


def main():
    """主函數"""
    print("=" * 60)
    print("DataScout 圖表字型應用範例")
    print("=" * 60)
    
    # 創建 Matplotlib 範例
    print("正在創建 Matplotlib 中文字型範例...")
    create_matplotlib_examples()
    
    # 生成 ApexCharts 配置
    print("\n正在生成 ApexCharts 字型配置...")
    generate_apexcharts_config()
    
    print("\n" + "=" * 60)
    print("🎉 所有字型範例和配置文件已生成完成！")
    print("\n使用說明：")
    print("1. Matplotlib 範例圖片位於: data/temp/font_examples/")
    print("2. Web 字型 CSS: web_service/static/css/fonts.css")
    print("3. ApexCharts JS 配置: web_service/static/js/chart-font-config.js")
    print("\n在 HTML 中引入這些文件即可使用中文字型。")
    print("=" * 60)


if __name__ == "__main__":
    main()
