import pandas as pd
import pandas_datareader.data as web
import datetime
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import os
import traceback

# 設定中文字型支援
plt.rcParams['font.family'] = ['Noto Sans Gothic', 'Taipei Sans TC Beta', 'AppleGothic', 'Heiti TC', 'Arial Unicode MS']

# 定義要取的 FRED 指標 ID (貿易保護主義相關指標)
fred_ids = [
    "IMPGS",         # 商品進口 (季度數據)
    "EXPGS",         # 商品出口 (季度數據)
    "BOPGSTB",       # 貿易差額：商品 (月度數據)
    "PCEPI",         # 個人消費支出價格指數
    "CPIAUCSL",      # 消費者物價指數
    "CPILFESL",      # 核心消費者物價指數 (不包括食品和能源)
    "A939RC0Q052SBEA", # 貿易差額占GDP比例
    "IEABCSN"        # 進出口價格比率
]

# 添加更新的關稅收入相關指標
tariff_alternatives = [
    "BAAFFM",               # 聯邦預算收入
    "FGRECPT",              # 政府總收入
    "FYFR"                 # 聯邦政府總稅收
]
fred_ids.extend(tariff_alternatives)

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

# 使用 web.DataReader 從 FRED 獲取數據，添加重試機制
try:
    # 獲取所有指標數據
    # 因原始 fred_ids 可能有問題，這裡添加重試和分段獲取的邏輯
    max_retries = 3
    retry_count = 0
    fred_data = pd.DataFrame()
    
    print("正在從 FRED 獲取數據...")
    
    # 嘗試分批獲取數據
    print("將嘗試獲取指標，部分指標可能不可用...")
    successful_ids = []
    failed_ids = []

    # 先嘗試批量獲取，再嘗試單個獲取的方式
    try:
        fred_data = web.DataReader(fred_ids, 'fred', start_date, end_date)
        successful_ids = list(fred_data.columns)
        failed_ids = [id for id in fred_ids if id not in successful_ids]
        if failed_ids:
            print(f"以下指標批量獲取失敗: {', '.join(failed_ids)}")
    except Exception as e:
        print(f"批量獲取失敗，將嘗試單個獲取: {e}")
        # 如果批量獲取失敗，逐個嘗試
        for indicator_id in fred_ids:
            try:
                indicator_data = web.DataReader(indicator_id, 'fred', start_date, end_date)
                if fred_data.empty:
                    fred_data = indicator_data
                else:
                    fred_data = fred_data.join(indicator_data, how='outer')
                successful_ids.append(indicator_id)
                print(f"成功獲取 {indicator_id}")
            except Exception as indiv_error:
                failed_ids.append(indicator_id)
                print(f"無法獲取 {indicator_id}: {indiv_error}")

    if successful_ids:
        print(f"成功獲取的指標: {', '.join(successful_ids)}")
    if failed_ids:
        print(f"獲取失敗的指標: {', '.join(failed_ids)}")

    if fred_data.empty:
        raise Exception("無法獲取任何數據")

    print("從 FRED 獲取的數據：")
    print(fred_data.head())

    print("\n數據基本資訊：")
    fred_data.info()
    
    # 保存完整數據集到 CSV 檔案
    csv_filename = f"trade_protectionism_indicators_{today_str}.csv"
    csv_path = data_dir / csv_filename
    fred_data.to_csv(csv_path)
    print(f"\n已將完整數據保存至: {csv_path}")
    
    # 為每個指標創建單獨的圖表
    for indicator in fred_ids:
        if (indicator in fred_data.columns) and (indicator in successful_ids):
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
    
    # 分析貿易保護主義指標 - 計算變化率和大幅變動
    analysis_df = pd.DataFrame(index=fred_data.index)
    
    # 1. 進出口數據分析
    for indicator in ["IMPGoods", "EXPGoods"]:
        if indicator in fred_data.columns:
            indicator_data = fred_data[indicator].dropna()
            if not indicator_data.empty:
                analysis_df[indicator] = indicator_data
                
                # 計算月度變化率 (%)
                analysis_df[f'{indicator}_mom_pct'] = indicator_data.pct_change() * 100
                
                # 計算年度變化率 (%)
                analysis_df[f'{indicator}_yoy_pct'] = indicator_data.pct_change(12) * 100
                
                # 定義大幅下降標準 (月度下降 > 2%)
                analysis_df[f'{indicator}_decline_m'] = analysis_df[f'{indicator}_mom_pct'] < -2
                
                # 定義持續下降標準 (年度下降 > 5%)
                analysis_df[f'{indicator}_decline_y'] = analysis_df[f'{indicator}_yoy_pct'] < -5
    
    # 2. 進出口比率分析
    if all(x in fred_data.columns for x in ["IMPGoods", "EXPGoods"]):
        imp_data = fred_data["IMPGoods"].dropna()
        exp_data = fred_data["EXPGoods"].dropna()
        
        # 確保兩個數據集有相同的索引
        common_index = imp_data.index.intersection(exp_data.index)
        if len(common_index) > 0:
            imp_aligned = imp_data.loc[common_index]
            exp_aligned = exp_data.loc[common_index]
            
            # 計算進出口比率 (進口/出口)
            analysis_df['import_export_ratio'] = imp_aligned / exp_aligned
            
            # 計算比率的變化
            analysis_df['import_export_ratio_change'] = analysis_df['import_export_ratio'].pct_change() * 100
            
            # 定義貿易失衡加劇標準 (比率增加超過5%)
            analysis_df['trade_imbalance_worsening'] = analysis_df['import_export_ratio_change'] > 5
    
    # 3. 通貨膨脹指標分析
    for indicator in ["PCEPI", "CPIAUCSL", "CPILFESL"]:
        if indicator in fred_data.columns:
            indicator_data = fred_data[indicator].dropna()
            if not indicator_data.empty:
                analysis_df[indicator] = indicator_data
                
                # 計算月度通膨 (%)
                analysis_df[f'{indicator}_mom_pct'] = indicator_data.pct_change() * 100
                
                # 計算年度通膨 (%)
                analysis_df[f'{indicator}_yoy_pct'] = indicator_data.pct_change(12) * 100
                
                # 定義通膨上升標準 (年度通膨率增加)
                if len(indicator_data) >= 13:
                    prev_yoy = indicator_data.pct_change(12).shift(1)
                    curr_yoy = indicator_data.pct_change(12)
                    analysis_df[f'{indicator}_inflation_rising'] = (curr_yoy > prev_yoy) & (curr_yoy > 0)
                
                # 定義高通膨標準 (年度通膨率 > 3%)
                analysis_df[f'{indicator}_high_inflation'] = analysis_df[f'{indicator}_yoy_pct'] > 3
    
    # 4. 關稅收入分析
    # 首先確定可能的關稅收入指標
    customs_indicator = None
    potential_indicators = [
        "TTLCIR",            # 優先使用國際貿易收入
        "FYFR",              # 其次使用聯邦政府總稅收
        "FGRECPT",           # 再次使用政府總收入 
        "BAAFFM",            # 最後使用聯邦預算收入
        "DISCONTINUED_CUSTOMS" 
    ]

    for indicator in potential_indicators:
        if indicator in fred_data.columns:
            customs_indicator = indicator
            print(f"使用 {customs_indicator} 作為關稅收入指標替代品")
            break

    if customs_indicator:
        cust_data = fred_data[customs_indicator].dropna()
        if not cust_data.empty:
            analysis_df[customs_indicator] = cust_data
            
            # 計算月度變化率 (%)
            analysis_df[f'{customs_indicator}_mom_pct'] = cust_data.pct_change() * 100
            
            # 計算年度變化率 (%)
            analysis_df[f'{customs_indicator}_yoy_pct'] = cust_data.pct_change(12) * 100
            
            # 定義關稅收入增加標準 (年度增長率 > 10%)
            analysis_df[f'{customs_indicator}_significant_increase'] = analysis_df[f'{customs_indicator}_yoy_pct'] > 10
    else:
        print("警告: 無法獲取任何關稅收入相關指標，將生成模擬數據用於分析展示")
        # 生成模擬關稅數據用於展示
        dummy_dates = pd.date_range(start=start_date, end=end_date, freq='M')
        dummy_data = pd.Series(np.random.normal(10, 2, size=len(dummy_dates)), index=dummy_dates)
        # 添加趨勢和季節性
        trend = np.linspace(0, 5, len(dummy_dates))
        seasonality = np.sin(np.linspace(0, 12*np.pi, len(dummy_dates)))
        dummy_data = dummy_data + trend + seasonality
        
        customs_indicator = "SIMULATED_CUSTOMS"
        analysis_df[customs_indicator] = dummy_data
        analysis_df[f'{customs_indicator}_mom_pct'] = dummy_data.pct_change() * 100
        analysis_df[f'{customs_indicator}_yoy_pct'] = dummy_data.pct_change(12) * 100
        analysis_df[f'{customs_indicator}_significant_increase'] = analysis_df[f'{customs_indicator}_yoy_pct'] > 10
        print("已生成模擬關稅數據，僅供視覺化展示參考")
    
    # 5. 貿易差額占GDP比例分析
    if 'A939RC0Q052SBEA' in fred_data.columns:
        trade_gdp_ratio = fred_data['A939RC0Q052SBEA'].dropna()
        if not trade_gdp_ratio.empty:
            analysis_df['trade_gdp_ratio'] = trade_gdp_ratio
            
            # 計算變化 (百分點)
            analysis_df['trade_gdp_ratio_change'] = trade_gdp_ratio - trade_gdp_ratio.shift(1)
            
            # 定義貿易赤字惡化標準 (比率下降超過0.5個百分點)
            analysis_df['trade_deficit_worsening'] = analysis_df['trade_gdp_ratio_change'] < -0.5
    
    # 綜合判斷貿易保護主義指標
    protectionism_indicators = []

    # 進出口比率惡化
    if 'trade_imbalance_worsening' in analysis_df.columns:
        protectionism_indicators.append('trade_imbalance_worsening')

    # 關稅收入增加
    if customs_indicator and f'{customs_indicator}_significant_increase' in analysis_df.columns:
        protectionism_indicators.append(f'{customs_indicator}_significant_increase')

    # 進口下降
    if 'IMPGoods_decline_m' in analysis_df.columns:
        protectionism_indicators.append('IMPGoods_decline_m')
    elif 'IMPGS_decline_m' in analysis_df.columns:  # 使用替代指標
        protectionism_indicators.append('IMPGS_decline_m')

    # 通膨上升 (檢查PCEPI或CPI)
    for inflation_indicator in ['PCEPI_inflation_rising', 'CPIAUCSL_inflation_rising']:
        if inflation_indicator in analysis_df.columns:
            protectionism_indicators.append(inflation_indicator)
            break
    
    # 如果有足夠的指標可用，進行綜合判斷
    if len(protectionism_indicators) >= 2:
        # 至少兩個指標同時滿足條件才判定為貿易保護主義加強
        analysis_df['protectionism_indicators_count'] = analysis_df[protectionism_indicators].sum(axis=1)
        analysis_df['increased_protectionism'] = analysis_df['protectionism_indicators_count'] >= 2
    
    # 保存分析結果
    analysis_path = data_dir / f"trade_protectionism_analysis_{today_str}.csv"
    analysis_df.to_csv(analysis_path)
    print(f"\n已將分析結果保存至: {analysis_path}")
    
    # 繪製綜合分析圖表
    fig, axes = plt.subplots(5, 1, figsize=(12, 20), sharex=True)
    
    # 1. 進出口總額圖表
    if all(x in fred_data.columns for x in ["IMPGoods", "EXPGoods"]):
        imp_data = fred_data["IMPGoods"].dropna() / 1e9  # 轉換為十億美元
        exp_data = fred_data["EXPGoods"].dropna() / 1e9  # 轉換為十億美元
        
        imp_data.plot(ax=axes[0], label='商品進口總額', color='red')
        exp_data.plot(ax=axes[0], label='商品出口總額', color='blue')
        
        # 計算並繪製貿易差額
        common_index = imp_data.index.intersection(exp_data.index)
        if len(common_index) > 0:
            trade_balance = exp_data.loc[common_index] - imp_data.loc[common_index]
            trade_balance.plot(ax=axes[0], label='貿易差額', color='green', linestyle='--')
        
        axes[0].set_title('美國商品進出口總額')
        axes[0].grid(True)
        axes[0].legend()
        axes[0].set_ylabel('十億美元')
    
    # 2. 關稅收入圖表
    if customs_indicator and customs_indicator in fred_data.columns:
        cust_data = fred_data[customs_indicator].dropna() / 1e9  # 轉換為十億美元
        cust_data.plot(ax=axes[1], color='purple')
        axes[1].set_title(f'關稅收入 ({customs_indicator})')
        axes[1].grid(True)
        axes[1].set_ylabel('十億美元')
        
        # 標註大幅增加期間
        if f'{customs_indicator}_significant_increase' in analysis_df.columns:
            increase_periods = analysis_df[analysis_df[f'{customs_indicator}_significant_increase'] == True].index
            if len(increase_periods) > 0:
                for date in increase_periods:
                    axes[1].axvline(x=date, color='red', alpha=0.3, linestyle='--')
    else:
        axes[1].text(0.5, 0.5, '無法獲取關稅收入數據', 
                    horizontalalignment='center', verticalalignment='center',
                    transform=axes[1].transAxes, fontsize=14)
        axes[1].set_title('關稅收入 (數據不可用)')
        axes[1].grid(True)
    
    # 3. 通膨指標圖表
    for indicator, color, label in [("PCEPI", "red", "個人消費支出價格指數"), 
                                    ("CPIAUCSL", "blue", "消費者物價指數"), 
                                    ("CPILFESL", "green", "核心CPI")]:
        if f'{indicator}_yoy_pct' in analysis_df.columns:
            inflation_data = analysis_df[f'{indicator}_yoy_pct'].dropna()
            inflation_data.plot(ax=axes[2], label=label, color=color)
    
    axes[2].set_title('年度通膨率')
    axes[2].grid(True)
    axes[2].legend()
    axes[2].set_ylabel('%')
    axes[2].axhline(y=0, color='black', linestyle='-', alpha=0.3)
    axes[2].axhline(y=2, color='red', linestyle='--', alpha=0.3)  # 2%通膨目標
    
    # 4. 進出口比率和貿易差額占GDP比例
    if 'import_export_ratio' in analysis_df.columns:
        ratio_data = analysis_df['import_export_ratio'].dropna()
        ratio_data.plot(ax=axes[3], color='blue', label='進口/出口比率')
    
    if 'trade_gdp_ratio' in analysis_df.columns:
        trade_gdp = analysis_df['trade_gdp_ratio'].dropna()
        trade_gdp.plot(ax=axes[3], color='green', label='貿易差額占GDP比例')
    
    axes[3].set_title('貿易指標')
    axes[3].grid(True)
    axes[3].legend()
    
    # 5. 綜合貿易保護主義指標
    if 'increased_protectionism' in analysis_df.columns:
        protectionism_indicator = analysis_df['increased_protectionism'].astype(int)
        protectionism_indicator.plot(ax=axes[4], color='red', linewidth=2)
        axes[4].set_title('強硬貿易保護主義指標')
        axes[4].grid(True)
        axes[4].set_ylabel('指標值 (1=是, 0=否)')
        axes[4].set_ylim(-0.1, 1.1)
    
    plt.tight_layout()
    plt.subplots_adjust(hspace=0.3)
    
    # 保存綜合分析圖
    analysis_img_path = images_dir / f"trade_protectionism_analysis_{today_str}.png"
    plt.savefig(analysis_img_path, dpi=300)
    print(f"已將綜合分析圖保存至: {analysis_img_path}")
    
    # 顯示貿易保護主義期間
    if 'increased_protectionism' in analysis_df.columns:
        # 獲取寬鬆期間數據
        protectionism_indices = analysis_df[analysis_df['increased_protectionism'] == True].index
        if len(protectionism_indices) > 0:
            print("\n識別出的強硬貿易保護主義期間:")
            
            # 建立一個新的DataFrame而不是修改視圖
            protectionism_periods = pd.DataFrame(index=protectionism_indices)
            
            # 安全地添加數據
            protectionism_periods.loc[:, 'date'] = protectionism_indices
            protectionism_periods.loc[:, 'group'] = (protectionism_periods['date'].diff() > pd.Timedelta(days=60)).cumsum()
            
            # 將原數據複製到新DataFrame，僅包含實際獲取到的指標
            indicators_to_check = {
                'IMPGoods': '商品進口變化',
                'EXPGoods': '商品出口變化',
                'PCEPI': 'PCE物價指數變化',
                'CPIAUCSL': 'CPI變化'
            }
            
            # 添加關稅指標
            if customs_indicator:
                indicators_to_check[customs_indicator] = f'{customs_indicator}變化'
            
            # 只複製存在的指標數據
            for indicator in indicators_to_check:
                if indicator in analysis_df.columns:
                    protectionism_periods.loc[:, indicator] = analysis_df.loc[protectionism_indices, indicator]
            
            for group, data in protectionism_periods.groupby('group'):
                start_date = data.index.min().strftime('%Y-%m-%d')
                end_date = data.index.max().strftime('%Y-%m-%d')
                print(f"  • {start_date} 至 {end_date}")
                
                # 計算期間內的指標變化
                for indicator, label in indicators_to_check.items():
                    if indicator in data.columns and not data[indicator].empty and len(data[indicator]) > 1:
                        change_pct = ((data[indicator].iloc[-1] / data[indicator].iloc[0]) - 1) * 100
                        print(f"    - {label}: {change_pct:.2f}%")
                
                # 特別檢查進出口比率的變化
                if 'import_export_ratio' in data.columns and not data['import_export_ratio'].empty and len(data['import_export_ratio']) > 1:
                    ratio_change = ((data['import_export_ratio'].iloc[-1] / data['import_export_ratio'].iloc[0]) - 1) * 100
                    print(f"    - 進出口比率變化: {ratio_change:.2f}%")
        else:
            print("\n未識別出明確的強硬貿易保護主義期間")
    
    # 分析最近期間的貿易政策傾向
    recent_period = 6  # 約半年
    recent_data = analysis_df.tail(recent_period) if len(analysis_df) > recent_period else analysis_df
    
    print("\n最近期間的貿易政策傾向分析:")
    
    # 檢查進出口變化
    for indicator, label in [('IMPGoods', '商品進口'), ('EXPGoods', '商品出口')]:
        if f'{indicator}_yoy_pct' in recent_data.columns and not recent_data[f'{indicator}_yoy_pct'].empty:
            recent_change = recent_data[f'{indicator}_yoy_pct'].mean()
            print(f"  • {label}平均年度變化率: {recent_change:.2f}%")
    
    # 檢查通膨指標
    for indicator, label in [('PCEPI', 'PCE物價指數'), ('CPIAUCSL', 'CPI')]:
        if f'{indicator}_yoy_pct' in recent_data.columns and not recent_data[f'{indicator}_yoy_pct'].empty:
            recent_inflation = recent_data[f'{indicator}_yoy_pct'].mean()
            print(f"  • {label}平均年度通膨率: {recent_inflation:.2f}%")
    
    # 檢查關稅收入變化
    if customs_indicator and f'{customs_indicator}_yoy_pct' in recent_data.columns and not recent_data[f'{customs_indicator}_yoy_pct'].empty:
        recent_tariff_change = recent_data[f'{customs_indicator}_yoy_pct'].mean()
        print(f"  • {customs_indicator}平均年度變化率: {recent_tariff_change:.2f}%")
        if customs_indicator == "SIMULATED_CUSTOMS":
            print("    (注意：由於無法獲取實際關稅數據，此為模擬數據僅供參考)")
    
    # 檢查進出口比率變化
    if 'import_export_ratio' in recent_data.columns and not recent_data['import_export_ratio'].empty and len(recent_data['import_export_ratio']) > 1:
        recent_ratio_change = ((recent_data['import_export_ratio'].iloc[-1] / recent_data['import_export_ratio'].iloc[0]) - 1) * 100
        print(f"  • 進出口比率近期變化: {recent_ratio_change:.2f}%")
        if recent_ratio_change > 5:
            print("    (進口相對出口顯著增加，可能表示貿易平衡惡化)")
        elif recent_ratio_change < -5:
            print("    (出口相對進口顯著增加，可能表示貿易平衡改善)")
    
    # 判斷近期是否有貿易保護主義傾向
    protectionism_count = 0
    if 'protectionism_indicators_count' in recent_data.columns:
        protectionism_count = recent_data['protectionism_indicators_count'].mean()
        
    if protectionism_count >= 1.5:
        print(f"  • 近期平均符合 {protectionism_count:.1f} 個貿易保護主義指標")
        print("  • 有強硬貿易保護主義的跡象")
        
        # 判斷保護主義措施的主要影響
        effects = []
        
        # 檢查進口減少
        if 'IMPGoods_yoy_pct' in recent_data.columns and recent_data['IMPGoods_yoy_pct'].mean() < 0:
            effects.append("進口商品減少")
        
        # 檢查出口變化
        if 'EXPGoods_yoy_pct' in recent_data.columns:
            if recent_data['EXPGoods_yoy_pct'].mean() < 0:
                effects.append("出口商品減少")
                effects.append("可能面臨他國報復性措施")
            
        # 檢查通膨壓力
        for indicator in ['PCEPI_yoy_pct', 'CPIAUCSL_yoy_pct']:
            if indicator in recent_data.columns and recent_data[indicator].mean() > 2.5:
                effects.append("國內物價上漲壓力")
                break
        
        # 檢查關稅收入增加
        if customs_indicator and f'{customs_indicator}_yoy_pct' in recent_data.columns and recent_data[f'{customs_indicator}_yoy_pct'].mean() > 5:
            effects.append("政府關稅收入增加")
        
        if effects:
            print(f"  • 主要經濟影響: {', '.join(effects)}")
    else:
        print("  • 近期未出現明確的貿易保護主義跡象")

except Exception as e:
    print(f"獲取或處理 FRED 數據時發生錯誤: {e}")
    print("請確認指標 ID 是否正確，以及網路連線是否正常。")
    print(traceback.format_exc())  # 顯示詳細的錯誤信息

finally:
    print("\n分析完成")
    plt.close('all')  # 關閉所有圖表