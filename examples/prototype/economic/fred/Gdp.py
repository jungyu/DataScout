import pandas as pd
import pandas_datareader.data as web
import datetime
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import os

# 設定中文字型支援
plt.rcParams['font.family'] = ['Noto Sans Gothic', 'Taipei Sans TC Beta', 'AppleGothic', 'Heiti TC', 'Arial Unicode MS']

# 定義要取的 FRED 指標 ID (定向性財政刺激相關指標)
fred_ids = ["GDPC1", "GPDI", "GCE", "PAYEMS", "USCONS", "MANEMP", "UNRATE", "GFDEBTN"]

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
    csv_filename = f"fiscal_stimulus_indicators_{today_str}.csv"
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
    
    # 分析財政刺激的指標 - 計算變化率和大幅變動
    analysis_df = pd.DataFrame(index=fred_data.index)
    
    # 1. 實質GDP、GPDI和GCE增長分析
    for indicator in ["GDPC1", "GPDI", "GCE"]:
        if indicator in fred_data.columns:
            indicator_data = fred_data[indicator].dropna()
            if not indicator_data.empty:
                analysis_df[indicator] = indicator_data
                
                # 計算季度變化率 (%)
                analysis_df[f'{indicator}_qoq_pct'] = indicator_data.pct_change() * 100
                
                # 計算年度變化率 (%)
                analysis_df[f'{indicator}_yoy_pct'] = indicator_data.pct_change(4) * 100  # 假設數據是季度性的
                
                # 定義快速增長標準 (季度增長率 > 1%)
                analysis_df[f'{indicator}_growth_q'] = analysis_df[f'{indicator}_qoq_pct'] > 1
                
                # 定義持續增長標準 (年度增長率 > 3%)
                analysis_df[f'{indicator}_growth_y'] = analysis_df[f'{indicator}_yoy_pct'] > 3
    
    # 2. 就業數據分析 (PAYEMS總數、USCONS建築業、MANEMP製造業)
    for indicator in ["PAYEMS", "USCONS", "MANEMP"]:
        if indicator in fred_data.columns:
            indicator_data = fred_data[indicator].dropna()
            if not indicator_data.empty:
                analysis_df[indicator] = indicator_data
                
                # 計算月度變化 (千人)
                analysis_df[f'{indicator}_mom_change'] = indicator_data - indicator_data.shift(1)
                
                # 計算年度變化率 (%)
                analysis_df[f'{indicator}_yoy_pct'] = indicator_data.pct_change(12) * 100
                
                # 定義就業增長標準 (月度增加)
                analysis_df[f'{indicator}_growth_m'] = analysis_df[f'{indicator}_mom_change'] > 0
                
                # 定義顯著就業增長標準 (年度增長 > 2%)
                analysis_df[f'{indicator}_strong_growth'] = analysis_df[f'{indicator}_yoy_pct'] > 2
    
    # 3. UNRATE (失業率) 下降分析
    if 'UNRATE' in fred_data.columns:
        unrate_data = fred_data['UNRATE'].dropna()
        if not unrate_data.empty:
            analysis_df['UNRATE'] = unrate_data
            
            # 計算變化 (百分點)
            analysis_df['UNRATE_3m_change'] = unrate_data - unrate_data.shift(3)  # 3個月變化
            analysis_df['UNRATE_12m_change'] = unrate_data - unrate_data.shift(12)  # 12個月變化
            
            # 定義失業率下降標準 (-0.3個百分點或更多)
            analysis_df['UNRATE_decline_3m'] = analysis_df['UNRATE_3m_change'] <= -0.3
            analysis_df['UNRATE_decline_12m'] = analysis_df['UNRATE_12m_change'] <= -0.5
    
    # 4. GFDEBTN (政府總債務) 增加分析
    if 'GFDEBTN' in fred_data.columns:
        gfdebtn_data = fred_data['GFDEBTN'].dropna()
        if not gfdebtn_data.empty:
            analysis_df['GFDEBTN'] = gfdebtn_data
            
            # 計算變化率 (%)
            analysis_df['GFDEBTN_qoq_pct'] = gfdebtn_data.pct_change() * 100  # 假設數據是季度性的
            analysis_df['GFDEBTN_yoy_pct'] = gfdebtn_data.pct_change(4) * 100  # 假設數據是季度性的
            
            # 定義政府債務增加標準 (季度增長 > 2%)
            analysis_df['GFDEBTN_increase_q'] = analysis_df['GFDEBTN_qoq_pct'] > 2
            
            # 定義政府債務大幅增加標準 (年度增長 > 7%)
            analysis_df['GFDEBTN_rapid_increase'] = analysis_df['GFDEBTN_yoy_pct'] > 7
    
    # 綜合判斷定向性財政刺激條件
    stimulus_indicators = []
    
    # 檢查GDP成分增長
    for component in ['GPDI_growth_q', 'GCE_growth_q']:
        if component in analysis_df.columns:
            stimulus_indicators.append(component)
    
    # 檢查就業增長
    for emp_indicator in ['USCONS_growth_m', 'MANEMP_growth_m']:
        if emp_indicator in analysis_df.columns:
            stimulus_indicators.append(emp_indicator)
    
    # 檢查失業率下降
    if 'UNRATE_decline_3m' in analysis_df.columns:
        stimulus_indicators.append('UNRATE_decline_3m')
    
    # 檢查政府債務增加
    if 'GFDEBTN_increase_q' in analysis_df.columns:
        stimulus_indicators.append('GFDEBTN_increase_q')
    
    # 如果有足夠的指標可用，進行綜合判斷
    if len(stimulus_indicators) >= 3:
        # 至少三個指標同時滿足條件才判定為定向性財政刺激
        analysis_df['stimulus_indicators_count'] = analysis_df[stimulus_indicators].sum(axis=1)
        analysis_df['fiscal_stimulus'] = analysis_df['stimulus_indicators_count'] >= 3
    
    # 保存分析結果
    analysis_path = data_dir / f"fiscal_stimulus_analysis_{today_str}.csv"
    analysis_df.to_csv(analysis_path)
    print(f"\n已將分析結果保存至: {analysis_path}")
    
    # 繪製綜合分析圖表
    fig, axes = plt.subplots(6, 1, figsize=(12, 24), sharex=True)
    
    # 1. 實質GDP及其組成部分圖表
    for i, indicator_pair in enumerate([("GDPC1", "實質GDP"), ("GPDI", "私人國內投資"), ("GCE", "政府消費與投資")]):
        indicator, title = indicator_pair
        if indicator in fred_data.columns:
            indicator_data = fred_data[indicator].dropna()
            if i == 0:  # 實質GDP轉為萬億美元
                indicator_data = indicator_data / 1e12
                ylabel = '萬億美元'
            else:  # 其他組成部分轉為十億美元
                indicator_data = indicator_data / 1e9
                ylabel = '十億美元'
                
            indicator_data.plot(ax=axes[0], label=title)
            
    axes[0].set_title('實質GDP及其組成部分')
    axes[0].grid(True)
    axes[0].legend()
    axes[0].set_ylabel('金額')
    
    # 2. 就業數據圖表
    for i, indicator_pair in enumerate([("PAYEMS", "非農就業總數"), ("USCONS", "建築業就業"), ("MANEMP", "製造業就業")]):
        indicator, title = indicator_pair
        if indicator in fred_data.columns:
            indicator_data = fred_data[indicator].dropna() / 1e3  # 轉換為百萬人
            indicator_data.plot(ax=axes[1], label=title)
    
    axes[1].set_title('就業數據')
    axes[1].grid(True)
    axes[1].legend()
    axes[1].set_ylabel('百萬人')
    
    # 3. 失業率圖表
    if 'UNRATE' in fred_data.columns:
        unrate_data = fred_data['UNRATE'].dropna()
        unrate_data.plot(ax=axes[2], color='red')
        axes[2].set_title('失業率 (UNRATE)')
        axes[2].grid(True)
        axes[2].set_ylabel('%')
        
        # 標註明顯下降期間
        if 'UNRATE_decline_12m' in analysis_df.columns:
            decline_periods = analysis_df[analysis_df['UNRATE_decline_12m'] == True].index
            if len(decline_periods) > 0:
                for date in decline_periods:
                    axes[2].axvline(x=date, color='green', alpha=0.3, linestyle='--')
    
    # 4. 政府債務圖表
    if 'GFDEBTN' in fred_data.columns:
        gfdebtn_data = fred_data['GFDEBTN'].dropna() / 1e12  # 轉換為萬億美元
        gfdebtn_data.plot(ax=axes[3], color='purple')
        axes[3].set_title('聯邦政府總債務 (GFDEBTN)')
        axes[3].grid(True)
        axes[3].set_ylabel('萬億美元')
        
        # 標註快速增加期間
        if 'GFDEBTN_rapid_increase' in analysis_df.columns:
            increase_periods = analysis_df[analysis_df['GFDEBTN_rapid_increase'] == True].index
            if len(increase_periods) > 0:
                for date in increase_periods:
                    axes[3].axvline(x=date, color='red', alpha=0.3, linestyle='--')
    
    # 5. GDP組成部分增長率
    for component, color in [("GPDI", "blue"), ("GCE", "green")]:
        if f'{component}_yoy_pct' in analysis_df.columns:
            component_growth = analysis_df[f'{component}_yoy_pct'].dropna()
            component_growth.plot(ax=axes[4], label=f'{component} 年增長率', color=color)
    
    axes[4].set_title('GDP組成部分年度增長率')
    axes[4].grid(True)
    axes[4].legend()
    axes[4].set_ylabel('%')
    axes[4].axhline(y=0, color='black', linestyle='-', alpha=0.3)
    
    # 6. 綜合財政刺激指標
    if 'fiscal_stimulus' in analysis_df.columns:
        stimulus_indicator = analysis_df['fiscal_stimulus'].astype(int)
        stimulus_indicator.plot(ax=axes[5], color='red', linewidth=2)
        axes[5].set_title('定向性財政刺激指標')
        axes[5].grid(True)
        axes[5].set_ylabel('指標值 (1=是, 0=否)')
        axes[5].set_ylim(-0.1, 1.1)
    
    plt.tight_layout()
    plt.subplots_adjust(hspace=0.3)
    
    # 保存綜合分析圖
    analysis_img_path = images_dir / f"fiscal_stimulus_analysis_{today_str}.png"
    plt.savefig(analysis_img_path, dpi=300)
    print(f"已將綜合分析圖保存至: {analysis_img_path}")
    
    # 顯示財政刺激期間
    if 'fiscal_stimulus' in analysis_df.columns:
        stimulus_periods = analysis_df[analysis_df['fiscal_stimulus'] == True]
        if not stimulus_periods.empty:
            print("\n識別出的定向性財政刺激期間:")
            # 找出連續的期間
            stimulus_periods['date'] = stimulus_periods.index
            # 分組連續日期（當間隔超過3個月時視為不同期間）
            stimulus_periods['group'] = (stimulus_periods['date'].diff() > pd.Timedelta(days=90)).cumsum()
            
            for group, data in stimulus_periods.groupby('group'):
                start_date = data.index.min().strftime('%Y-%m-%d')
                end_date = data.index.max().strftime('%Y-%m-%d')
                print(f"  • {start_date} 至 {end_date}")
                
                # 計算期間內的指標變化
                for indicator in ['GDPC1', 'GPDI', 'GCE', 'PAYEMS', 'USCONS', 'MANEMP', 'UNRATE', 'GFDEBTN']:
                    if indicator in data.columns:
                        if indicator == 'UNRATE':  # 失業率用百分點變化
                            change = data[indicator].iloc[-1] - data[indicator].iloc[0]
                            print(f"    - {indicator}變化: {change:.2f}個百分點")
                        else:  # 其他用百分比變化
                            change_pct = ((data[indicator].iloc[-1] / data[indicator].iloc[0]) - 1) * 100
                            print(f"    - {indicator}變化: {change_pct:.2f}%")
        else:
            print("\n未識別出明確的定向性財政刺激期間")
    
    # 分析最近期間的財政政策傾向
    recent_period = 6  # 約半年
    recent_data = analysis_df.tail(recent_period) if len(analysis_df) > recent_period else analysis_df
    
    print("\n最近期間的財政政策傾向分析:")
    
    # 檢查實質GDP及其組成部分的增長
    for indicator in ['GDPC1', 'GPDI', 'GCE']:
        if f'{indicator}_qoq_pct' in recent_data.columns:
            recent_growth = recent_data[f'{indicator}_qoq_pct'].mean()
            if indicator == 'GDPC1':
                print(f"  • 實質GDP平均季度增長率: {recent_growth:.2f}%")
            elif indicator == 'GPDI':
                print(f"  • 私人國內投資平均季度增長率: {recent_growth:.2f}%")
            elif indicator == 'GCE':
                print(f"  • 政府消費與投資平均季度增長率: {recent_growth:.2f}%")
    
    # 檢查就業數據
    for indicator in ['PAYEMS', 'USCONS', 'MANEMP']:
        if f'{indicator}_mom_change' in recent_data.columns:
            recent_change = recent_data[f'{indicator}_mom_change'].mean()
            if indicator == 'PAYEMS':
                print(f"  • 非農就業平均月增長: {recent_change:.2f}千人")
            elif indicator == 'USCONS':
                print(f"  • 建築業就業平均月增長: {recent_change:.2f}千人")
            elif indicator == 'MANEMP':
                print(f"  • 製造業就業平均月增長: {recent_change:.2f}千人")
    
    # 檢查失業率變化
    if 'UNRATE_3m_change' in recent_data.columns:
        recent_unrate_change = recent_data['UNRATE_3m_change'].mean()
        print(f"  • 失業率平均3個月變化: {recent_unrate_change:.2f}個百分點")
    
    # 檢查政府債務增加情況
    if 'GFDEBTN_qoq_pct' in recent_data.columns:
        recent_debt_growth = recent_data['GFDEBTN_qoq_pct'].mean()
        print(f"  • 政府債務平均季度增長率: {recent_debt_growth:.2f}%")
    
    # 判斷近期是否有財政刺激傾向
    stimulus_count = 0
    if 'stimulus_indicators_count' in recent_data.columns:
        stimulus_count = recent_data['stimulus_indicators_count'].mean()
        
    if stimulus_count >= 2:
        print(f"  • 近期平均符合 {stimulus_count:.1f} 個財政刺激指標")
        print("  • 有定向性財政刺激的跡象")
        
        # 判斷是哪些部門受益最多
        sector_benefits = []
        
        # 檢查私人投資增長
        if 'GPDI_growth_q' in recent_data.columns and recent_data['GPDI_growth_q'].sum() > 0:
            sector_benefits.append("私人投資部門")
        
        # 檢查政府支出增長
        if 'GCE_growth_q' in recent_data.columns and recent_data['GCE_growth_q'].sum() > 0:
            sector_benefits.append("政府項目")
        
        # 檢查就業增長情況
        if 'USCONS_growth_m' in recent_data.columns and recent_data['USCONS_growth_m'].sum() > 0:
            sector_benefits.append("建築業")
        
        if 'MANEMP_growth_m' in recent_data.columns:
            if recent_data['MANEMP_growth_m'].sum() > 0:
                sector_benefits.append("製造業")
        
        if sector_benefits:
            print(f"  • 主要受益部門: {', '.join(sector_benefits)}")
        else:
            print("  • 未發現明顯受益部門")
    else:
        print("  • 近期無明顯財政刺激跡象")

except Exception as e:
    print(f"獲取或處理 FRED 數據時發生錯誤: {e}")
    print("請確認指標 ID 是否正確，以及網路連線是否正常。")
    import traceback
    print(traceback.format_exc())  # 顯示詳細的錯誤信息

finally:
    print("\n分析完成")
    plt.close('all')  # 關閉所有圖表