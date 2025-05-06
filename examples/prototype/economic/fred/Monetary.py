import pandas as pd
import pandas_datareader.data as web
import datetime
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import os
import traceback
import time

# 設定中文字型支援
plt.rcParams['font.family'] = ['Noto Sans Gothic', 'Taipei Sans TC Beta', 'AppleGothic', 'Heiti TC', 'Arial Unicode MS']

# 定義要取的 FRED 指標 ID (積極貨幣寬鬆相關指標)
# 提供主要指標和備用指標
primary_fred_ids = ["DFF", "DFEDTAR", "WALCL"] 
secondary_fred_ids = ["BOGMBASE", "TOTRESNS"] # 備用指標，替代 RESBAL 用的貨幣基礎和總準備金指標
fred_ids = primary_fred_ids + secondary_fred_ids

print("將嘗試獲取以下指標:")
print(f"主要指標: {', '.join(primary_fred_ids)}")
print(f"備用指標: {', '.join(secondary_fred_ids)}")

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
    # 添加重試和分段獲取的邏輯
    max_retries = 3
    retry_count = 0
    fred_data = pd.DataFrame()
    
    print("正在從 FRED 獲取數據...")
    
    # 建立用來記錄成功獲取的指標
    successful_ids = []
    
    # 嘗試分批獲取數據
    while retry_count < max_retries and len(successful_ids) < len(fred_ids):
        try:
            # 嘗試獲取尚未成功的指標
            remaining_ids = [id for id in fred_ids if id not in successful_ids]
            print(f"嘗試獲取以下指標: {', '.join(remaining_ids)}")
            
            batch_data = web.DataReader(remaining_ids, 'fred', start_date, end_date)
            
            if fred_data.empty:
                fred_data = batch_data
            else:
                fred_data = fred_data.join(batch_data, how='outer')
                
            successful_ids.extend(remaining_ids)
            print(f"成功獲取 {len(remaining_ids)} 個指標")
            break
            
        except Exception as e:
            retry_count += 1
            print(f"批量獲取數據失敗 (嘗試 {retry_count}/{max_retries}): {e}")
            
            if retry_count == max_retries:
                # 最後嘗試逐個獲取指標
                print("嘗試單獨獲取每個指標...")
                
                for indicator_id in [id for id in fred_ids if id not in successful_ids]:
                    try:
                        print(f"獲取 {indicator_id}...")
                        indicator_data = web.DataReader(indicator_id, 'fred', start_date, end_date)
                        if fred_data.empty:
                            fred_data = indicator_data
                        else:
                            fred_data = fred_data.join(indicator_data, how='outer')
                        successful_ids.append(indicator_id)
                        print(f"成功獲取 {indicator_id}")
                    except Exception as indiv_error:
                        print(f"無法獲取 {indicator_id}: {indiv_error}")
                
                if successful_ids:
                    print(f"成功獲取的指標: {', '.join(successful_ids)}")
                else:
                    raise Exception("所有指標獲取均失敗")
            else:
                # 短暫暫停後重試
                print("等待 3 秒後重試...")
                time.sleep(3)
    
    if fred_data.empty:
        raise Exception("無法獲取任何數據")

    print("從 FRED 獲取的數據：")
    print(fred_data.head())

    print("\n數據基本資訊：")
    print(f"獲取到的指標數量: {len(fred_data.columns)}")
    fred_data.info()
    
    # 決定使用哪個準備金指標
    reserve_indicator = None
    if 'RESBAL' in fred_data.columns:
        reserve_indicator = 'RESBAL'
        print("使用 RESBAL 作為準備金指標")
    elif 'TOTRESNS' in fred_data.columns:
        reserve_indicator = 'TOTRESNS'
        print("使用 TOTRESNS 作為準備金指標 (RESBAL 的替代)")
    elif 'BOGMBASE' in fred_data.columns:
        reserve_indicator = 'BOGMBASE'
        print("使用 BOGMBASE 作為準備金指標 (貨幣基礎作為替代)")
    else:
        print("警告: 沒有可用的準備金相關指標")
    
    # 保存完整數據集到 CSV 檔案
    csv_filename = f"monetary_easing_indicators_{today_str}.csv"
    csv_path = data_dir / csv_filename
    fred_data.to_csv(csv_path)
    print(f"\n已將完整數據保存至: {csv_path}")
    
    # 為每個指標創建單獨的圖表
    for indicator in fred_data.columns:  # 只處理成功獲取的指標
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
    
    # 3. 準備金餘額指標分析 (使用可用的替代指標)
    if reserve_indicator:
        reserve_data = fred_data[reserve_indicator].dropna()
        if not reserve_data.empty:
            analysis_df[reserve_indicator] = reserve_data
            
            # 計算變化率 (%)
            analysis_df[f'{reserve_indicator}_pct_change_3m'] = reserve_data.pct_change(60) * 100  # 約3個月
            analysis_df[f'{reserve_indicator}_pct_change_6m'] = reserve_data.pct_change(120) * 100  # 約6個月
            
            # 定義快速上升標準 (3個月內上升10%或更多)
            analysis_df[f'{reserve_indicator}_expansion_3m'] = analysis_df[f'{reserve_indicator}_pct_change_3m'] >= 10
            analysis_df[f'{reserve_indicator}_expansion_6m'] = analysis_df[f'{reserve_indicator}_pct_change_6m'] >= 20
    
    # 綜合判斷積極貨幣寬鬆條件
    # 動態決定使用哪些指標組合
    available_indicators = []
    
    if 'DFF_easing_3m' in analysis_df.columns:
        available_indicators.append('DFF_easing_3m')
        
    if 'WALCL_expansion_3m' in analysis_df.columns:
        available_indicators.append('WALCL_expansion_3m')
        
    if reserve_indicator and f'{reserve_indicator}_expansion_3m' in analysis_df.columns:
        available_indicators.append(f'{reserve_indicator}_expansion_3m')
    
    if len(available_indicators) >= 2:
        print(f"\n使用以下指標進行綜合分析: {', '.join(available_indicators)}")
        
        # 創建綜合指標表達式
        if len(available_indicators) == 3:
            # 如果有三個指標，使用原先的公式
            analysis_df['aggressive_easing'] = (analysis_df[available_indicators[0]] & 
                                              (analysis_df[available_indicators[1]] | 
                                               analysis_df[available_indicators[2]]))
        elif len(available_indicators) == 2:
            # 如果有兩個指標，兩者都滿足時視為寬鬆
            analysis_df['aggressive_easing'] = (analysis_df[available_indicators[0]] & 
                                               analysis_df[available_indicators[1]])
        
        print("已計算綜合貨幣寬鬆指標")
    else:
        print("\n警告：可用的指標不足，無法計算綜合寬鬆指標")
    
    # 保存分析結果
    analysis_path = data_dir / f"monetary_easing_analysis_{today_str}.csv"
    analysis_df.to_csv(analysis_path)
    print(f"\n已將分析結果保存至: {analysis_path}")
    
    # 繪製綜合分析圖表
    # 根據可用的指標動態確定子圖數量
    available_main_indicators = [x for x in ['DFF', 'WALCL', reserve_indicator] if x and x in fred_data.columns]
    num_subplots = len(available_main_indicators) + ('aggressive_easing' in analysis_df.columns)
    
    if num_subplots == 0:
        print("沒有足夠數據繪製分析圖表")
    else:
        fig, axes = plt.subplots(num_subplots, 1, figsize=(12, 5*num_subplots), sharex=True)
        
        # 如果只有一個子圖，確保axes是一個列表
        if num_subplots == 1:
            axes = [axes]
        
        current_ax = 0
        
        # 1. DFF圖表
        if 'DFF' in fred_data.columns:
            dff_data = fred_data['DFF'].dropna()
            dff_data.plot(ax=axes[current_ax], color='blue')
            axes[current_ax].set_title('聯邦基金有效利率 (DFF)')
            axes[current_ax].grid(True)
            axes[current_ax].set_ylabel('%')
            
            # 標註大幅下降期間
            if 'DFF_easing_6m' in analysis_df.columns:
                easing_periods = analysis_df[analysis_df['DFF_easing_6m'] == True].index
                if len(easing_periods) > 0:
                    for date in easing_periods:
                        axes[current_ax].axvline(x=date, color='red', alpha=0.3, linestyle='--')
            
            current_ax += 1
        
        # 2. WALCL圖表
        if 'WALCL' in fred_data.columns:
            walcl_data = fred_data['WALCL'].dropna() / 1e6  # 轉換為兆美元
            walcl_data.plot(ax=axes[current_ax], color='green')
            axes[current_ax].set_title('聯準會總資產 (WALCL)')
            axes[current_ax].grid(True)
            axes[current_ax].set_ylabel('兆美元')
            
            # 標註快速上升期間
            if 'WALCL_expansion_3m' in analysis_df.columns:
                expansion_periods = analysis_df[analysis_df['WALCL_expansion_3m'] == True].index
                if len(expansion_periods) > 0:
                    for date in expansion_periods:
                        axes[current_ax].axvline(x=date, color='red', alpha=0.3, linestyle='--')
            
            current_ax += 1
        
        # 3. 準備金指標圖表
        if reserve_indicator and reserve_indicator in fred_data.columns:
            reserve_data = fred_data[reserve_indicator].dropna() / 1e9  # 轉換為十億美元
            reserve_data.plot(ax=axes[current_ax], color='purple')
            axes[current_ax].set_title(f'{reserve_indicator} (準備金相關指標)')
            axes[current_ax].grid(True)
            axes[current_ax].set_ylabel('十億美元')
            
            # 標註快速增加期間
            expansion_col = f'{reserve_indicator}_expansion_3m'
            if expansion_col in analysis_df.columns:
                expansion_periods = analysis_df[analysis_df[expansion_col] == True].index
                if len(expansion_periods) > 0:
                    for date in expansion_periods:
                        axes[current_ax].axvline(x=date, color='red', alpha=0.3, linestyle='--')
            
            current_ax += 1
        
        # 4. 綜合積極貨幣寬鬆指標
        if 'aggressive_easing' in analysis_df.columns:
            easing_indicator = analysis_df['aggressive_easing'].astype(int)
            easing_indicator.plot(ax=axes[current_ax], color='red', linewidth=2)
            axes[current_ax].set_title('積極貨幣寬鬆指標')
            axes[current_ax].grid(True)
            axes[current_ax].set_ylabel('指標值 (1=是, 0=否)')
            axes[current_ax].set_ylim(-0.1, 1.1)
        
        plt.tight_layout()
        plt.subplots_adjust(hspace=0.3)
        
        # 保存綜合分析圖
        analysis_img_path = images_dir / f"monetary_easing_analysis_{today_str}.png"
        plt.savefig(analysis_img_path, dpi=300)
        print(f"已將綜合分析圖保存至: {analysis_img_path}")
    
    # 顯示貨幣寬鬆期間
    if 'aggressive_easing' in analysis_df.columns:
        # 獲取寬鬆期間數據
        easing_periods_indices = analysis_df[analysis_df['aggressive_easing'] == True].index
        if len(easing_periods_indices) > 0:
            print("\n識別出的積極貨幣寬鬆期間:")
            
            # 建立一個新的DataFrame而不是修改視圖
            easing_periods = pd.DataFrame(index=easing_periods_indices)
            
            # 安全地添加數據
            easing_periods.loc[:, 'date'] = easing_periods_indices
            easing_periods.loc[:, 'group'] = (easing_periods['date'].diff() > pd.Timedelta(days=30)).cumsum()
            
            # 將原數據複製到新DataFrame
            for col in ['DFF', 'WALCL'] + ([reserve_indicator] if reserve_indicator else []):
                if col in analysis_df.columns:
                    easing_periods.loc[:, col] = analysis_df.loc[easing_periods_indices, col]
            
            for group, data in easing_periods.groupby('group'):
                start_date = data.index.min().strftime('%Y-%m-%d')
                end_date = data.index.max().strftime('%Y-%m-%d')
                print(f"  • {start_date} 至 {end_date}")
                
                # 計算期間內的指標變化
                indicators_to_check = {
                    'DFF': 'DFF變化 (百分點)',
                    'WALCL': 'WALCL變化 (%)'
                }
                
                # 添加可用的準備金指標
                if reserve_indicator:
                    indicators_to_check[reserve_indicator] = f'{reserve_indicator}變化 (%)'
                
                for indicator, label in indicators_to_check.items():
                    if indicator in data.columns and not data[indicator].empty and len(data[indicator]) > 1:
                        if indicator == 'DFF':
                            change = data[indicator].iloc[-1] - data[indicator].iloc[0]
                            print(f"    - {label}: {change:.2f}")
                        else:
                            change_pct = ((data[indicator].iloc[-1] / data[indicator].iloc[0]) - 1) * 100
                            print(f"    - {label}: {change_pct:.2f}%")
        else:
            print("\n未識別出明確的積極貨幣寬鬆期間")
    
    # 分析最近期間的貨幣政策傾向
    recent_period = 60  # 約3個月
    if len(analysis_df) > recent_period:
        recent_data = analysis_df.iloc[-recent_period:]
        print("\n最近期間的貨幣政策傾向分析:")
        
        # 動態決定要檢查的指標
        indicators_to_check = [
            ('DFF', 'DFF近期變化', False),
            ('WALCL', 'WALCL近期變化', True)
        ]
        
        # 添加可用的準備金指標
        if reserve_indicator:
            indicators_to_check.append((reserve_indicator, f'{reserve_indicator}近期變化', True))
        
        for indicator, label, is_percent in indicators_to_check:
            if indicator in recent_data.columns and not recent_data[indicator].empty and len(recent_data[indicator]) > 1:
                if is_percent:
                    recent_change_pct = ((recent_data[indicator].iloc[-1] / recent_data[indicator].iloc[0]) - 1) * 100
                    print(f"  • {label}: {recent_change_pct:.2f}%")
                else:
                    recent_change = recent_data[indicator].iloc[-1] - recent_data[indicator].iloc[0]
                    print(f"  • {label}: {recent_change:.2f}個百分點")
        
        # 判斷近期是否有寬鬆傾向
        recent_easing_count = 0
        easing_indicators = ['DFF_easing_3m', 'WALCL_expansion_3m']
        
        # 添加可用的準備金指標
        if reserve_indicator:
            easing_indicators.append(f'{reserve_indicator}_expansion_3m')
        
        for indicator in easing_indicators:
            if indicator in recent_data.columns:
                indicator_count = recent_data[indicator].sum()
                recent_easing_count += indicator_count
                print(f"  • {indicator} 指標觸發次數: {indicator_count}")
        
        if recent_easing_count > 0:
            print(f"  • 近期總計出現 {recent_easing_count} 個寬鬆指標觸發點")
            
            # 判斷趨勢
            if 'DFF' in recent_data.columns and len(recent_data['DFF'].dropna()) > 10:
                dff_values = recent_data['DFF'].dropna()
                dff_trend = np.polyfit(range(len(dff_values)), dff_values, 1)[0]
                if dff_trend < 0:
                    print("  • DFF呈下降趨勢，顯示利率正在下調")
                else:
                    print("  • DFF呈上升趨勢，顯示利率正在上調")
                    
            # 檢查資產負債表趨勢
            if 'WALCL' in recent_data.columns and len(recent_data['WALCL'].dropna()) > 10:
                walcl_values = recent_data['WALCL'].dropna()
                walcl_trend = np.polyfit(range(len(walcl_values)), walcl_values, 1)[0]
                if walcl_trend > 0:
                    print("  • WALCL呈上升趨勢，顯示資產負債表正在擴張")
                else:
                    print("  • WALCL呈下降趨勢，顯示資產負債表正在收縮")
        else:
            print("  • 近期未出現明確的貨幣寬鬆跡象")
    else:
        print("\n沒有足夠的數據分析最近期間的貨幣政策傾向")

except Exception as e:
    print(f"獲取或處理 FRED 數據時發生錯誤: {e}")
    print("請確認指標 ID 是否正確，以及網路連線是否正常。")
    print(traceback.format_exc())  # 顯示詳細的錯誤信息

finally:
    print("\n分析完成")
    plt.close('all')  # 關閉所有圖表