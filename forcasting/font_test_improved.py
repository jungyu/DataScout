# -*- coding: utf-8 -*-
"""
中文字體測試腳本
測試系統中可用的中文字體是否能正確顯示中文文字
"""

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import os

def test_chinese_fonts():
    """測試中文字體顯示效果"""
    
    # 可用的中文字體列表（基於系統檢查結果）
    chinese_fonts = [
        'Noto Sans CJK TC',
        'Heiti TC', 
        'STHeiti',
        'PingFang HK',
        'STFangsong',
        'Songti SC',
        'Arial Unicode MS'
    ]
    
    # 測試用的中文文字
    test_text = [
        '混淆矩陣',
        'ROC 曲線', 
        '特徵重要性',
        '累積收益',
        '預測策略',
        '買入持有策略'
    ]
    
    # 創建測試圖表
    fig, axes = plt.subplots(len(chinese_fonts), 1, figsize=(12, 2*len(chinese_fonts)))
    if len(chinese_fonts) == 1:
        axes = [axes]
    
    for i, font_name in enumerate(chinese_fonts):
        # 檢查字體是否可用
        try:
            # 設置字體
            plt.rcParams['font.family'] = [font_name]
            
            ax = axes[i]
            
            # 簡單的測試圖表
            x = np.arange(len(test_text))
            y = np.random.rand(len(test_text))
            
            bars = ax.bar(x, y, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b'])
            ax.set_xticks(x)
            ax.set_xticklabels(test_text, rotation=45, ha='right')
            ax.set_title(f'字體測試：{font_name}', fontsize=14)
            ax.set_ylabel('數值')
            
            # 在每個柱子上添加標籤
            for j, (bar, label) in enumerate(zip(bars, test_text)):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                       f'{label}\n{height:.2f}', 
                       ha='center', va='bottom', fontsize=10)
            
        except Exception as e:
            print(f"字體 {font_name} 測試失敗: {e}")
    
    plt.tight_layout()
    
    # 確保輸出目錄存在
    os.makedirs('/Users/aaron/Projects/DataScout/data/output', exist_ok=True)
    
    # 保存測試結果
    output_path = '/Users/aaron/Projects/DataScout/data/output/chinese_font_test.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"字體測試圖表已保存至: {output_path}")
    
    # 顯示圖表
    plt.show()
    
    return chinese_fonts

def find_best_chinese_font():
    """找到最佳可用的中文字體"""
    
    # 優先級順序的字體列表
    preferred_fonts = [
        'Noto Sans CJK TC',
        'PingFang HK', 
        'Heiti TC',
        'STHeiti',
        'STFangsong',
        'Songti SC',
        'Arial Unicode MS'
    ]
    
    # 獲取系統中所有可用字體
    available_fonts = [f.name for f in fm.fontManager.ttflist]
    
    print("字體可用性檢查:")
    for font in preferred_fonts:
        available = font in available_fonts
        status = "✓ 可用" if available else "✗ 不可用"
        print(f"  {font}: {status}")
        
        if available:
            print(f"\n推薦使用字體: {font}")
            return font
    
    print("\n警告: 未找到推薦的中文字體，將使用系統默認字體")
    return None

def setup_matplotlib_chinese_font():
    """設置 matplotlib 的中文字體"""
    
    best_font = find_best_chinese_font()
    
    if best_font:
        plt.rcParams['font.family'] = [best_font]
        plt.rcParams['axes.unicode_minus'] = False
        print(f"已設置 matplotlib 中文字體: {best_font}")
        return best_font
    else:
        # 使用回退字體列表
        fallback_fonts = [
            'Noto Sans CJK TC', 'PingFang HK', 'Heiti TC', 'STHeiti', 
            'STFangsong', 'Songti SC', 'Arial Unicode MS', 'SimHei', 
            'Microsoft JhengHei', 'sans-serif'
        ]
        plt.rcParams['font.family'] = fallback_fonts
        plt.rcParams['axes.unicode_minus'] = False
        print(f"已設置 matplotlib 回退字體列表: {fallback_fonts[:3]}...")
        return fallback_fonts[0]

if __name__ == "__main__":
    print("開始中文字體測試...")
    
    # 設置中文字體
    setup_matplotlib_chinese_font()
    
    # 測試字體顯示效果
    test_chinese_fonts()
    
    print("\n字體測試完成！")
