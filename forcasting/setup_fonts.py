# -*- coding: utf-8 -*-
"""
DataScout 股價預測系統字型設定模組
確保圖表能正確顯示中文，優先使用思源黑體字 (Noto Sans TC)
"""

import os
import sys
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 添加專案根目錄到路徑
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.append(project_root)

try:
    from config.chart_fonts import setup_chinese_fonts, font_manager
except ImportError:
    print("警告：無法導入字型配置模組，將使用基本設定")


def install_noto_fonts():
    """檢查並提示安裝思源黑體字"""
    print("檢查思源黑體字 (Noto Sans TC) 安裝狀態...")
    
    all_fonts = [f.name for f in fm.fontManager.ttflist]
    noto_fonts = [f for f in all_fonts if 'noto sans tc' in f.lower() or 'noto sans cjk tc' in f.lower()]
    
    if noto_fonts:
        print(f"✅ 找到思源黑體字: {noto_fonts}")
        return True
    else:
        print("❌ 未找到思源黑體字")
        print("\n建議安裝思源黑體字:")
        print("macOS: brew install font-noto-sans-cjk-tc")
        print("或從 Google Fonts 下載: https://fonts.google.com/noto/specimen/Noto+Sans+TC")
        print("Linux: sudo apt-get install fonts-noto-cjk")
        print("Windows: 從 Google Fonts 下載並安裝")
        return False


def setup_forecasting_fonts():
    """為股價預測系統設定字型"""
    print("=== DataScout 股價預測系統字型設定 ===")
    
    # 檢查思源黑體字
    noto_available = install_noto_fonts()
    
    # 設定 matplotlib 字型
    try:
        if 'chart_fonts' in sys.modules:
            font_manager.setup_matplotlib_fonts()
        else:
            # 基本字型設定
            print("使用基本字型設定...")
            font_list = [
                'Noto Sans TC',
                'Noto Sans CJK TC',
                'PingFang TC', 
                'Heiti TC',
                'Microsoft JhengHei',
                'SimHei',
                'DejaVu Sans'
            ]
            
            plt.rcParams['font.family'] = font_list
            plt.rcParams['axes.unicode_minus'] = False
            plt.rcParams['font.size'] = 12
            
        print("✅ Matplotlib 中文字型設定完成")
        
    except Exception as e:
        print(f"❌ 字型設定失敗: {e}")
        return False
    
    return True


def test_chinese_display():
    """測試中文顯示效果"""
    print("\n測試中文字型顯示...")
    
    import numpy as np
    import pandas as pd
    
    # 創建測試數據
    dates = pd.date_range('2024-01-01', periods=30, freq='D')
    prices = 100 + np.cumsum(np.random.randn(30) * 2)
    
    # 創建圖表
    plt.figure(figsize=(12, 8))
    
    # 主圖：股價走勢
    plt.subplot(2, 2, 1)
    plt.plot(dates, prices, 'b-', linewidth=2, label='股價走勢')
    plt.title('股票價格走勢圖', fontsize=16, fontweight='bold')
    plt.xlabel('日期', fontsize=12)
    plt.ylabel('價格 (元)', fontsize=12)
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 預測結果
    plt.subplot(2, 2, 2)
    predictions = ['上漲', '下跌', '持平', '上漲', '下跌']
    probabilities = [0.75, 0.68, 0.52, 0.81, 0.63]
    colors = ['green' if p == '上漲' else 'red' if p == '下跌' else 'gray' for p in predictions]
    
    bars = plt.bar(range(len(predictions)), probabilities, color=colors, alpha=0.7)
    plt.title('預測結果信心度', fontsize=16, fontweight='bold')
    plt.xlabel('預測天數', fontsize=12)
    plt.ylabel('信心度', fontsize=12)
    plt.xticks(range(len(predictions)), [f'第{i+1}天\n{pred}' for i, pred in enumerate(predictions)])
    plt.ylim(0, 1)
    
    # 技術指標
    plt.subplot(2, 2, 3)
    ma5 = np.convolve(prices, np.ones(5)/5, mode='valid')
    ma10 = np.convolve(prices, np.ones(10)/10, mode='valid')
    
    plt.plot(dates[-len(ma5):], ma5, 'g--', label='5日移動平均', alpha=0.8)
    plt.plot(dates[-len(ma10):], ma10, 'r--', label='10日移動平均', alpha=0.8)
    plt.plot(dates, prices, 'b-', alpha=0.6, label='收盤價')
    plt.title('技術分析指標', fontsize=16, fontweight='bold')
    plt.xlabel('日期', fontsize=12)
    plt.ylabel('價格 (元)', fontsize=12)
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 風險提示
    plt.subplot(2, 2, 4)
    plt.text(0.5, 0.7, '風險提示', fontsize=20, fontweight='bold', 
             ha='center', va='center', transform=plt.gca().transAxes)
    plt.text(0.5, 0.5, '本系統僅供學習研究\n不構成投資建議', fontsize=14, 
             ha='center', va='center', transform=plt.gca().transAxes)
    plt.text(0.5, 0.3, '投資有風險\n決策需謹慎', fontsize=12, 
             ha='center', va='center', transform=plt.gca().transAxes, color='red')
    plt.axis('off')
    
    plt.tight_layout()
    
    # 保存測試圖表
    output_path = os.path.join(project_root, 'data', 'output', 'font_test_chart.png')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    try:
        plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
        print(f"✅ 測試圖表已保存: {output_path}")
        
        # 顯示當前使用的字型
        current_font = plt.rcParams['font.family'][0]
        print(f"✅ 當前使用字型: {current_font}")
        
    except Exception as e:
        print(f"❌ 保存圖表失敗: {e}")
    
    return output_path


def main():
    """主函數"""
    print("DataScout 股價預測系統 - 中文字型設定工具")
    print("=" * 50)
    
    # 設定字型
    if setup_forecasting_fonts():
        print("\n字型設定成功！")
        
        # 測試顯示
        try:
            import pandas as pd
            test_path = test_chinese_display()
            print(f"\n圖表測試完成，請查看: {test_path}")
            
        except ImportError:
            print("需要安裝 pandas 來進行完整測試")
            print("執行: pip install pandas")
        
    else:
        print("\n字型設定失敗，請檢查錯誤訊息")
    
    print("\n=" * 50)


if __name__ == "__main__":
    main()
