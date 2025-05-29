#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DataScout 字型設定腳本
統一配置所有圖表模組的中文字型支援
"""

import sys
import os
import platform
from pathlib import Path

# 添加專案根目錄到路徑
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.chart_fonts import ChartFontManager, setup_chinese_fonts


def main():
    """主函數：設定和測試字型配置"""
    print("=" * 60)
    print("DataScout 圖表字型配置工具")
    print("=" * 60)
    
    # 初始化字型管理器
    try:
        print("正在初始化字型管理器...")
        font_manager = setup_chinese_fonts()
        print("✓ 字型管理器初始化成功")
        
        # 顯示系統資訊
        print(f"\n系統平台: {platform.system()}")
        print(f"Python 版本: {platform.python_version()}")
        
        # 顯示字型資訊
        print("\n" + "=" * 40)
        print("可用中文字型資訊")
        print("=" * 40)
        font_manager.print_font_info()
        
        # 測試 matplotlib 配置
        print("\n" + "=" * 40)
        print("測試 Matplotlib 字型配置")
        print("=" * 40)
        test_matplotlib_config(font_manager)
        
        # 顯示 Web 字型配置
        print("\n" + "=" * 40)
        print("Web 字型配置")
        print("=" * 40)
        web_config = font_manager.get_web_font_config()
        print(f"主要字型: {web_config['primary']}")
        print(f"備用字型: {web_config['fallback']}")
        print(f"Google Fonts URL: {web_config['google_fonts_url']}")
        
        # 顯示 ApexCharts 配置範例
        print("\n" + "=" * 40)
        print("ApexCharts 字型配置範例")
        print("=" * 40)
        apex_config = font_manager.get_apexcharts_font_config()
        print(f"圖表字型: {apex_config['chart']['fontFamily']}")
        print(f"標題字型: {apex_config['title']['style']['fontFamily']}")
        
        print("\n✓ 所有字型配置檢查完成！")
        
    except Exception as e:
        print(f"❌ 字型配置過程中發生錯誤: {e}")
        return False
    
    return True


def test_matplotlib_config(font_manager):
    """測試 matplotlib 字型配置"""
    try:
        import matplotlib.pyplot as plt
        import numpy as np
        
        # 設定字型
        font_manager.setup_matplotlib_fonts()
        
        # 創建測試圖表
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # 生成測試數據
        x = np.linspace(0, 10, 100)
        y1 = np.sin(x)
        y2 = np.cos(x)
        
        # 繪製圖表
        ax.plot(x, y1, label='正弦波', linewidth=2)
        ax.plot(x, y2, label='餘弦波', linewidth=2)
        
        # 設定中文標題和標籤
        ax.set_title('中文字型測試圖表', fontsize=16, fontweight='bold')
        ax.set_xlabel('時間軸 (秒)', fontsize=12)
        ax.set_ylabel('振幅', fontsize=12)
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)
        
        # 儲存測試圖表
        output_path = Path(__file__).parent.parent / 'data' / 'temp' / 'font_test.png'
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"✓ Matplotlib 字型測試成功")
        print(f"  測試圖表已儲存至: {output_path}")
        
    except ImportError:
        print("⚠ Matplotlib 未安裝，跳過測試")
    except Exception as e:
        print(f"❌ Matplotlib 測試失敗: {e}")


def generate_web_font_css():
    """生成 Web 字型 CSS 配置"""
    css_content = '''
/* DataScout 中文字型配置 */
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500;600;700&display=swap');

:root {
  --font-family-primary: 'Noto Sans TC', 'PingFang TC', 'Microsoft JhengHei', 'Heiti TC', sans-serif;
  --font-family-fallback: Arial, sans-serif;
  --font-family-mono: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
}

body {
  font-family: var(--font-family-primary);
}

/* ApexCharts 字型覆寫 */
.apexcharts-text {
  font-family: var(--font-family-primary) !important;
}

.apexcharts-title-text {
  font-family: var(--font-family-primary) !important;
  font-weight: 600 !important;
}

.apexcharts-legend-text {
  font-family: var(--font-family-primary) !important;
}

.apexcharts-xaxis-label,
.apexcharts-yaxis-label {
  font-family: var(--font-family-primary) !important;
}

.apexcharts-datalabels {
  font-family: var(--font-family-primary) !important;
}

/* 確保中文字符正確顯示 */
.chinese-text {
  font-family: var(--font-family-primary);
  font-feature-settings: "kern" 1;
  text-rendering: optimizeLegibility;
}
'''
    
    # 寫入 CSS 文件
    css_path = Path(__file__).parent.parent / 'web_service' / 'static' / 'css' / 'fonts.css'
    css_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(css_content)
    
    print(f"✓ Web 字型 CSS 已生成: {css_path}")


if __name__ == "__main__":
    success = main()
    
    # 生成 Web 字型 CSS
    print("\n" + "=" * 40)
    print("生成 Web 字型 CSS")
    print("=" * 40)
    generate_web_font_css()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 字型配置完成！所有圖表現在都支援中文顯示。")
        print("\n使用說明：")
        print("1. Python/Matplotlib: 導入 config.chart_fonts 並調用 setup_chinese_fonts()")
        print("2. Web/ApexCharts: 確保引入生成的 fonts.css 文件")
        print("3. 自訂配置: 可通過 ChartFontManager 類別進行調整")
    else:
        print("❌ 字型配置過程中遇到問題，請檢查錯誤訊息。")
    print("=" * 60)
