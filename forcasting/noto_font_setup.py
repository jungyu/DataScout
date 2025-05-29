# -*- coding: utf-8 -*-
"""
DataScout 思源黑體字設定工具
修正字型名稱並確保正確顯示中文
"""

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import pandas as pd
import os

def clear_matplotlib_cache():
    """清除 matplotlib 字型快取"""
    import matplotlib
    try:
        cache_dir = matplotlib.get_cachedir()
        font_cache = os.path.join(cache_dir, 'fontlist-v*')
        import glob
        for cache_file in glob.glob(font_cache):
            try:
                os.remove(cache_file)
                print(f"已清除字型快取: {cache_file}")
            except:
                pass
    except:
        pass

def detect_noto_fonts():
    """檢測 Noto 字型的實際名稱"""
    print("檢測 Noto 思源黑體字...")
    
    # 重新載入字型管理器
    try:
        fm.fontManager.__init__()
    except:
        pass
    
    all_fonts = [f.name for f in fm.fontManager.ttflist]
    noto_fonts = []
    
    # 查找所有 Noto 相關字型
    for font_name in all_fonts:
        if any(keyword in font_name for keyword in ['Noto Sans CJK', 'NotoSansCJK']):
            noto_fonts.append(font_name)
    
    # 去重並排序
    noto_fonts = sorted(list(set(noto_fonts)))
    
    print(f"找到 {len(noto_fonts)} 個 Noto 字型:")
    for i, font in enumerate(noto_fonts, 1):
        print(f"  {i}. {font}")
    
    return noto_fonts

def setup_chinese_fonts():
    """設定中文字型，使用實際的字型名稱"""
    print("\n=== 設定思源黑體字 (Noto Sans CJK TC) ===")
    
    # 清除快取
    clear_matplotlib_cache()
    
    # 檢測字型
    noto_fonts = detect_noto_fonts()
    
    # 設定字型優先順序
    font_priority = []
    
    # 添加找到的 Noto 字型
    for font in noto_fonts:
        if 'TC' in font or 'Traditional' in font:
            font_priority.append(font)
    
    for font in noto_fonts:
        if font not in font_priority:
            font_priority.append(font)
    
    # 添加備用字型
    backup_fonts = [
        'PingFang TC',
        'Helvetica Neue',
        'Arial',
        'DejaVu Sans'
    ]
    
    font_priority.extend(backup_fonts)
    
    print(f"\n字型優先順序:")
    for i, font in enumerate(font_priority[:5], 1):
        print(f"  {i}. {font}")
    
    # 設定 matplotlib
    plt.rcParams['font.family'] = font_priority
    plt.rcParams['axes.unicode_minus'] = False
    plt.rcParams['font.size'] = 12
    
    # 測試字型
    test_font = plt.rcParams['font.family'][0]
    print(f"\n✅ 設定完成！主要字型: {test_font}")
    
    return font_priority

def create_test_chart():
    """創建測試圖表"""
    print("\n創建測試圖表...")
    
    # 創建測試數據
    dates = pd.date_range('2024-01-01', periods=20, freq='D')
    
    # 股價數據
    base_price = 100
    price_changes = np.random.randn(20) * 2
    prices = base_price + np.cumsum(price_changes)
    
    # 預測數據
    predictions = ['上漲', '下跌', '持平', '上漲', '下跌']
    probabilities = [0.75, 0.68, 0.52, 0.81, 0.63]
    
    # 創建圖表
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
    
    # 1. 股價走勢圖
    ax1.plot(dates, prices, 'b-', linewidth=2, label='股價走勢')
    ax1.set_title('AAPL 股票價格走勢圖 - 思源黑體字測試', fontsize=16, fontweight='bold')
    ax1.set_xlabel('日期', fontsize=12)
    ax1.set_ylabel('價格 (美元)', fontsize=12)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. 預測信心度
    colors = ['green' if p == '上漲' else 'red' if p == '下跌' else 'gray' for p in predictions]
    bars = ax2.bar(range(len(predictions)), probabilities, color=colors, alpha=0.7)
    ax2.set_title('AI 預測結果信心度', fontsize=16, fontweight='bold')
    ax2.set_xlabel('預測天數', fontsize=12)
    ax2.set_ylabel('信心度', fontsize=12)
    ax2.set_xticks(range(len(predictions)))
    ax2.set_xticklabels([f'第{i+1}天\n{pred}' for i, pred in enumerate(predictions)])
    ax2.set_ylim(0, 1)
    
    # 3. 技術指標
    ma5 = pd.Series(prices).rolling(5).mean()
    ma10 = pd.Series(prices).rolling(10).mean()
    
    ax3.plot(dates, prices, 'b-', alpha=0.6, label='收盤價')
    ax3.plot(dates, ma5, 'g--', label='5日移動平均', alpha=0.8)
    ax3.plot(dates, ma10, 'r--', label='10日移動平均', alpha=0.8)
    ax3.set_title('技術分析指標', fontsize=16, fontweight='bold')
    ax3.set_xlabel('日期', fontsize=12)
    ax3.set_ylabel('價格 (美元)', fontsize=12)
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. 風險提示
    ax4.text(0.5, 0.7, '⚠️ 風險提示', fontsize=24, fontweight='bold', 
             ha='center', va='center', transform=ax4.transAxes)
    ax4.text(0.5, 0.5, '此為AI模型預測結果\n僅供參考，不構成投資建議', fontsize=16, 
             ha='center', va='center', transform=ax4.transAxes)
    ax4.text(0.5, 0.3, '投資有風險，決策需謹慎 📊', fontsize=14, 
             ha='center', va='center', transform=ax4.transAxes, color='red')
    ax4.axis('off')
    
    plt.tight_layout()
    
    # 保存圖表
    output_dir = "/Users/aaron/Projects/DataScout/data/output"
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, 'noto_font_test.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    
    print(f"✅ 測試圖表已保存: {output_path}")
    
    # 顯示當前使用的字型
    current_font = plt.rcParams['font.family'][0]
    print(f"✅ 實際使用字型: {current_font}")
    
    return output_path

def main():
    """主函數"""
    print("🎨 DataScout 思源黑體字設定工具")
    print("=" * 50)
    
    try:
        # 設定字型
        font_list = setup_chinese_fonts()
        
        # 創建測試圖表
        chart_path = create_test_chart()
        
        print(f"\n🎉 設定完成！")
        print(f"📊 測試圖表: {chart_path}")
        print("\n字型設定摘要:")
        print(f"  主要字型: {font_list[0] if font_list else '未知'}")
        print(f"  備用字型: {len(font_list)-1} 個")
        
    except Exception as e:
        print(f"❌ 發生錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
