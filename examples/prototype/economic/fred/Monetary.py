import pandas as pd
import pandas_datareader.data as web
import datetime
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import os

# 定義要取的 FRED 指標 ID (積極貨幣寬鬆相關指標)
fred_ids = ["DFF", "DFEDTAR", "WALCL", "RESBAL"]

# 設定時間範圍 (從 2000 年至今)
start_date = datetime.datetime(2000, 1, 1)
end_date = datetime.datetime.now()

# 確保目標目錄存在
data_dir = Path("../data")
images_dir = Path("../images")
data_dir.mkdir(exist_ok=True)
images_dir.mkdir(exist_ok=True)

# 取得目前日期作為檔案名稱的一部分
today_str = datetime.datetime.now().strftime("%Y%m%d")

# 使用 web.DataReader 從 FRED 獲取數據
try:
    # 獲取所有指標數據
    fred_data = web.DataReader(fred_ids, 'fred', start_date, end_date)

    print("從 FRED 獲取的數據：")
    print(fred_data.head())

    print("\n數據基本資訊：")
    fred_data.info()
    
    # 保存完整數據集到 CSV 檔案
    csv_filename = f"monetary_easing_indicators_{today_str}.csv"
    csv_path = data_dir / csv_filename
    fred_data.to_csv(csv_path)
    print(f"\n已將完整數據保存至: {csv_path}")
    
    # 為每個指標創建單獨的圖表
    for indicator in fred_ids:
        if indicator in fred_data.columns:
            plt.figure(figsize=(12, 6))
            
            # 繪製指標數據
            indicator_data = fred_data[indicator].dropna()
            indicator_data.plot(title=f'FRED {indicator} 指標趨勢')
            
            plt.grid(True)
            plt.tight_layout()
            
            # 保存圖表
            img_filename = f"fred_{indicator}_trend_{today_str}.png"
            img_path = images_dir / img_filename
            plt.savefig(img_path, dpi=300)
            print(f"已將 {indicator} 趨勢圖保存至: {img_path}")
            
            # 單獨保存這個指標的數據
            indiv_csv_filename = f"fred_{indicator}_{today_str}.csv"
            indiv_csv_path = data_dir / indiv_csv_filename
            indicator_data.to_frame().to_csv(indiv_csv_path)
            print(f"已將 {indicator} 數據保存至: {indiv_csv_path}")
    
    # 分析貨幣寬鬆的指標 - 計算變化率和大幅變動
    analysis_df = pd.DataFrame(index=fred_data.index)
    
    # 1. DFF (聯邦基金有效利率) 大幅下降分析
    if 'DFF' in fred_data.columns:
        dff_data = fred_data['DFF'].dropna()
        if not dff_data.empty:
            # 計算變化率 (基點)
            analysis_df['DFF'] = dff_data
            analysis_df['DFF_change_3m'] = dff_data - dff_data.shift(60)  # 約3個月
            analysis_df['DFF_change_6m'] = dff_data - dff_data.shift(120)  # 約6個月
            
            # 定義大幅下降標準 (-0.5個百分點或更多)
            analysis_df['DFF_easing_3m'] = analysis_df['DFF_change_3m'] <= -0.5
            analysis_df['DFF_easing_6m'] = analysis_df['DFF_change_6m'] <= -0.75
    
    # 2. WALCL (聯準會總資產) 快速上升分析
    if 'WALCL' in fred_data.columns:
        walcl_data = fred_data['WALCL'].dropna()
        if not walcl_data.empty:
            analysis_df['WALCL'] = walcl_data
            
            # 計算變化率 (%)
            analysis_df['WALCL_pct_change_3m'] = walcl_data.pct_change(60) * 100  # 約3個月
            analysis_df['WALCL_pct_change_6m'] = walcl_data.pct_change(120) * 100  # 約6個月
            
            # 定義快速上升標準 (3個月內上升5%或更多)
            analysis_df['WALCL_expansion_3m'] = analysis_df['WALCL_pct_change_3m'] >= 5
            analysis_df['WALCL_expansion_6m'] = analysis_df['WALCL_pct_change_6m'] >= 10
    
    # 3. RESBAL (準備金餘額) 快速增加分析
    if 'RESBAL' in fred_data.columns:
        resbal_data = fred_data['RESBAL'].dropna()
        if not resbal_data.empty:
            analysis_df['RESBAL'] = resbal_data
            
            # 計算變化率 (%)
            analysis_df['RESBAL_pct_change_3m'] = resbal_data.pct_change(60) * 100  # 約3個月
            analysis_df['RESBAL_pct_change_6m'] = resbal_data.pct_change(120) * 100  # 約6個月
            
            # 定義快速上升標準 (3個月內上升10%或更多)
            analysis_df['RESBAL_expansion_3m'] = analysis_df['RESBAL_pct_change_3m'] >= 10
            analysis_df['RESBAL_expansion_6m'] = analysis_df['RESBAL_pct_change_6m'] >= 20
    
    # 綜合判斷積極貨幣寬鬆條件
    if all(col in analysis_df.columns for col in ['DFF_easing_3m', 'WALCL_expansion_3m', 'RESBAL_expansion_3m']):
        analysis_df['aggressive_easing'] = (analysis_df['DFF_easing_3m'] & 
                                           (analysis_df['WALCL_expansion_3m'] | 
                                            analysis_df['RESBAL_expansion_3m']))
    
    # 保存分析結果
    analysis_path = data_dir / f"monetary_easing_analysis_{today_str}.csv"
    analysis_df.to_csv(analysis_path)
    print(f"\n已將分析結果保存至: {analysis_path}")
    
    # 繪製綜合分析圖表
    fig, axes = plt.subplots(4, 1, figsize=(12, 16), sharex=True)
    
    # 1. DFF圖表
    if 'DFF' in fred_data.columns:
        dff_data = fred_data['DFF'].dropna()
        dff_data.plot(ax=axes[0], color='blue')
        axes[0].set_title('聯邦基金有效利率 (DFF)')
        axes[0].grid(True)
        axes[0].set_ylabel('%')
        
        # 標註大幅下降期間
        if 'DFF_easing_6m' in analysis_df.columns:
            easing_periods = analysis_df[analysis_df['DFF_easing_6m'] == True].index
            if len(easing_periods) > 0:
                for date in easing_periods:
                    axes[0].axvline(x=date, color='red', alpha=0.3, linestyle='--')
    
    # 2. WALCL圖表
    if 'WALCL' in fred_data.columns:
        walcl_data = fred_data['WALCL'].dropna() / 1e6  # 轉換為兆美元
        walcl_data.plot(ax=axes[1], color='green')
        axes[1].set_title('聯準會總資產 (WALCL)')
        axes[1].grid(True)
        axes[1].set_ylabel('兆美元')
        
        # 標註快速上升期間
        if 'WALCL_expansion_3m' in analysis_df.columns:
            expansion_periods = analysis_df[analysis_df['WALCL_expansion_3m'] == True].index
            if len(expansion_periods) > 0:
                for date in expansion_periods:
                    axes[1].axvline(x=date, color='red', alpha=0.3, linestyle='--')
    
    # 3. RESBAL圖表
    if 'RESBAL' in fred_data.columns:
        resbal_data = fred_data['RESBAL'].dropna() / 1e9  # 轉換為十億美元
        resbal_data.plot(ax=axes[2], color='purple')
        axes[2].set_title('準備金餘額 (RESBAL)')
        axes[2].grid(True)
        axes[2].set_ylabel('十億美元')
        
        # 標註快速增加期間
        if 'RESBAL_expansion_3m' in analysis_df.columns:
            expansion_periods = analysis_df[analysis_df['RESBAL_expansion_3m'] == True].index
            if len(expansion_periods) > 0:
                for date in expansion_periods:
                    axes[2].axvline(x=date, color='red', alpha=0.3, linestyle='--')
    
    # 4. 綜合積極貨幣寬鬆指標
    if 'aggressive_easing' in analysis_df.columns:
        easing_indicator = analysis_df['aggressive_easing'].astype(int)
        easing_indicator.plot(ax=axes[3], color='red', linewidth=2)
        axes[3].set_title('積極貨幣寬鬆指標')
        axes[3].grid(True)
        axes[3].set_ylabel('指標值 (1=是, 0=否)')
        axes[3].set_ylim(-0.1, 1.1)
    
    plt.tight_layout()
    plt.subplots_adjust(hspace=0.3)
    
    # 保存綜合分析圖
    analysis_img_path = images_dir / f"monetary_easing_analysis_{today_str}.png"
    plt.savefig(analysis_img_path, dpi=300)
    print(f"已將綜合分析圖保存至: {analysis_img_path}")
    
    # 顯示貨幣寬鬆期間
    if 'aggressive_easing' in analysis_df.columns:
        easing_periods = analysis_df[analysis_df['aggressive_easing'] == True]
        if not easing_periods.empty:
            print("\n識別出的積極貨幣寬鬆期間:")
            # 找出連續的期間
            easing_periods['date'] = easing_periods.index
            # 分組連續日期
            easing_periods['group'] = (easing_periods['date'].diff() > pd.Timedelta(days=30)).cumsum()
            
            for group, data in easing_periods.groupby('group'):
                start_date = data.index.min().strftime('%Y-%m-%d')
                end_date = data.index.max().strftime('%Y-%m-%d')
                print(f"  • {start_date} 至 {end_date}")
                
                # 計算期間內的指標變化
                if 'DFF' in data.columns and 'WALCL' in data.columns and 'RESBAL' in data.columns:
                    dff_change = data['DFF'].iloc[-1] - data['DFF'].iloc[0]
                    walcl_change_pct = ((data['WALCL'].iloc[-1] / data['WALCL'].iloc[0]) - 1) * 100
                    resbal_change_pct = ((data['RESBAL'].iloc[-1] / data['RESBAL'].iloc[0]) - 1) * 100
                    
                    print(f"    - DFF變化: {dff_change:.2f}個百分點")
                    print(f"    - WALCL變化: {walcl_change_pct:.2f}%")
                    print(f"    - RESBAL變化: {resbal_change_pct:.2f}%")
        else:
            print("\n未識別出明確的積極貨幣寬鬆期間")
    
    # 分析最近期間的貨幣政策傾向
    recent_period = 60  # 約3個月
    recent_data = analysis_df.iloc[-recent_period:] if len(analysis_df) > recent_period else analysis_df
    
    print("\n最近期間的貨幣政策傾向分析:")
    if 'DFF' in recent_data.columns:
        recent_dff_change = recent_data['DFF'].iloc[-1] - recent_data['DFF'].iloc[0]
        print(f"  • DFF近期變化: {recent_dff_change:.2f}個百分點")
    
    if 'WALCL' in recent_data.columns:
        recent_walcl_change_pct = ((recent_data['WALCL'].iloc[-1] / recent_data['WALCL'].iloc[0]) - 1) * 100
        print(f"  • WALCL近期變化: {recent_walcl_change_pct:.2f}%")
    
    if 'RESBAL' in recent_data.columns:
        recent_resbal_change_pct = ((recent_data['RESBAL'].iloc[-1] / recent_data['RESBAL'].iloc[0]) - 1) * 100
        print(f"  • RESBAL近期變化: {recent_resbal_change_pct:.2f}%")
    
    # 判斷近期是否有寬鬆傾向
    recent_easing_count = 0
    if 'DFF_easing_3m' in recent_data.columns:
        recent_easing_count += recent_data['DFF_easing_3m'].sum()
    if 'WALCL_expansion_3m' in recent_data.columns:
        recent_easing_count += recent_data['WALCL_expansion_3m'].sum()
    if 'RESBAL_expansion_3m' in recent_data.columns:
        recent_easing_count += recent_data['RESBAL_expansion_3m'].sum()
    
    if recent_easing_count > 0:
        print(f"  • 近期出現 {recent_easing_count} 個寬鬆指標觸發點")
        
        # 判斷趨勢
        if 'DFF' in recent_data.columns and len(recent_data) > 10:
            dff_trend = np.polyfit(range(len(recent_data['DFF'].dropna())), recent_data['DFF'].dropna(), 1)[0]
            if dff_trend < 0:
                print("  • DFF呈下降趨勢，顯示利率正在下調")
            else:
                print("  • DFF呈上升趨勢，顯示利率正在上調")
    else:
        print("  • 近期未出現明確的貨幣寬鬆跡象")

except Exception as e:
    print(f"獲取或處理 FRED 數據時發生錯誤: {e}")
    print("請確認指標 ID 是否正確，以及網路連線是否正常。")
    import traceback
    print(traceback.format_exc())