# -*- coding: utf-8 -*-
"""
簡單的中文字體測試腳本
"""

import os
import sys
import matplotlib.pyplot as plt
import numpy as np

# 添加項目根目錄到 Python 路徑
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 導入中文字體配置模組
try:
    from config.chart_fonts import setup_chinese_fonts
    print("正在配置中文字體...")
    font_manager = setup_chinese_fonts()
    print("中文字體配置完成！")
except ImportError as e:
    print(f"警告：無法導入字體配置模組 - {e}")
    print("使用預設中文字體配置...")
    plt.rcParams['font.family'] = ['Noto Sans CJK TC', 'Heiti TC', 'PingFang HK', 'STHeiti', 'STFangsong']
    plt.rcParams['axes.unicode_minus'] = False
    print("預設中文字體配置完成！")

# 創建輸出目錄
os.makedirs('/Users/aaron/Projects/DataScout/data/output', exist_ok=True)

# 測試中文字體顯示
def test_chinese_fonts():
    print("正在測試中文字體顯示...")
    
    # 創建測試數據
    x = np.arange(1, 11)
    y = np.random.randn(10).cumsum()
    
    # 繪製測試圖表
    plt.figure(figsize=(10, 6))
    plt.plot(x, y, 'o-', linewidth=2, markersize=8)
    plt.title('中文字體測試圖表', fontsize=16)
    plt.xlabel('時間（天）', fontsize=12)
    plt.ylabel('累積收益（%）', fontsize=12)
    plt.grid(True, alpha=0.3)
    
    # 添加中文註釋
    plt.text(5, max(y), '這是中文註釋', fontsize=14, ha='center', 
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    
    # 保存圖表
    output_path = '/Users/aaron/Projects/DataScout/data/output/chinese_font_test.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"測試圖表已保存至: {output_path}")
    
    # 顯示圖表（如果在支持的環境中）
    try:
        plt.show()
    except:
        print("無法顯示圖表，但已保存至文件")
    
    plt.close()

if __name__ == "__main__":
    test_chinese_fonts()
    print("中文字體測試完成！")
