import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from datetime import datetime
import sys
import os
from pandas_datareader import data as pdr
import numpy as np
import yfinance as yf

# 設定中文字型支援
plt.rcParams['font.family'] = ['Noto Sans Gothic', 'Taipei Sans TC Beta', 'AppleGothic', 'Heiti TC']
plt.rcParams['axes.unicode_minus'] = False
print("Matplotlib 已設定中文字型。")

# 設定資料夾路徑
data_dir = "../data"
images_dir = "../images"

# 確保資料夾存在
os.makedirs(data_dir, exist_ok=True)
os.makedirs(images_dir, exist_ok=True)

# 設定時間範圍
start_date = "2000-01-01"
end_date = datetime.now().strftime("%Y-%m-%d")

# 下載債券收益率數據
print(f"正在下載美國國債相關數據從 {start_date} 到 {end_date}...")

# 1. 收益率數據
bonds = {
    'DGS1MO': '1個月',
    'DGS3MO': '3個月',
    'DGS6MO': '6個月',
    'DGS1': '1年',
    'DGS2': '2年', 
    'DGS5': '5年',
    'DGS10': '10年',
    'DGS30': '30年'
}

# 2. 基準利率數據
rate_codes = ['DFF', 'DFEDTARU']  # 聯邦基金有效利率, 聯邦基金目標上限

# 3. 美債總額數據
debt_codes = ['GFDEBTN', 'FYGFD', 'FDHBPIN']  # 總債務, 財政年度債務, 公開持有債務

try:
    # 下載債券收益率
    bond_data = pdr.DataReader(list(bonds.keys()), 'fred', start_date, end_date)
    
    # 下載基準利率
    rate_data = pdr.DataReader(rate_codes, 'fred', start_date, end_date)
    
    # 下載債務總額
    debt_data = pdr.DataReader(debt_codes, 'fred', start_date, end_date)
    
    print("FRED數據下載完成!")
    
    # 4. 下載國債期貨價格 (使用yfinance)
    print("正在下載國債期貨價格...")
    futures_symbols = {
        'ZT=F': '2年期國債期貨',
        'ZF=F': '5年期國債期貨',
        'ZN=F': '10年期國債期貨',
        'ZB=F': '30年期國債期貨'
    }
    
    futures_data = {}
    any_data_downloaded = False  # 追蹤是否有任何數據被下載

    for symbol, name in futures_symbols.items():
        try:
            data = yf.download(symbol, start=start_date, end=end_date)
            if not data.empty and 'Close' in data.columns:  # 確認下載的數據非空且包含收盤價欄位
                futures_data[symbol] = data['Close']
                any_data_downloaded = True
                print(f"成功下載 {name} 價格數據")
            else:
                print(f"{name} 數據為空")
        except Exception as e:
            print(f"無法下載 {name} 數據: {e}")

    # 將期貨數據合併到DataFrame
    if any_data_downloaded:
        # 使用concat方法處理可能的索引不一致問題
        futures_list = []
        for symbol, series in futures_data.items():
            series.name = symbol
            futures_list.append(pd.DataFrame(series))
        
        if futures_list:
            futures_df = pd.concat(futures_list, axis=1)
            print("\n國債期貨價格概覽:")
            print(f"資料筆數: {len(futures_df)}")
            print(futures_df.head())
            
            # 保存數據到CSV文件
            futures_csv = os.path.join(data_dir, "US_Bond_Futures.csv")
            futures_df.to_csv(futures_csv)
        else:
            print("警告: 沒有成功下載任何期貨數據")
            futures_df = pd.DataFrame()  # 創建一個空的DataFrame
    else:
        print("警告: 沒有成功下載任何期貨數據")
        futures_df = pd.DataFrame(index=[pd.to_datetime(end_date)])  # 創建一個有索引的空DataFrame
    
except Exception as e:
    print(f"下載數據時發生錯誤: {e}")
    print("請確認網路連接並檢查pandas_datareader與yfinance套件是否安裝:")
    print("pip install pandas_datareader yfinance")
    sys.exit(1)

# 數據基本資訊顯示
print("\n國債收益率資料概覽:")
print(f"資料筆數: {len(bond_data)}")
print(bond_data.head())

print("\n基準利率資料概覽:")
print(f"資料筆數: {len(rate_data)}")
print(rate_data.head())

print("\n國債總額資料概覽:")
print(f"資料筆數: {len(debt_data)}")
print(debt_data.head())

print("\n國債期貨價格概覽:")
print(f"資料筆數: {len(futures_df)}")
print(futures_df.head())

# 保存數據到CSV文件
bond_csv = os.path.join(data_dir, "US_Bond_Yields.csv")
rate_csv = os.path.join(data_dir, "US_Benchmark_Rates.csv")
debt_csv = os.path.join(data_dir, "US_Debt_Total.csv")
futures_csv = os.path.join(data_dir, "US_Bond_Futures.csv")

bond_data.to_csv(bond_csv)
rate_data.to_csv(rate_csv)
debt_data.to_csv(debt_csv)
futures_df.to_csv(futures_csv)
print(f"數據已保存到 {data_dir} 資料夾中。")

# ====================
# 視覺化分析部分
# ====================

# 1. 顯示基準利率與10年期國債收益率比較
plt.figure(figsize=(14, 7))
if 'DFF' in rate_data.columns and 'DGS10' in bond_data.columns:
    plt.plot(rate_data.index, rate_data['DFF'], 'r-', label='聯邦基金有效利率')
    plt.plot(bond_data.index, bond_data['DGS10'], 'b-', label='10年期國債收益率')
    plt.title('美國基準利率與10年期國債收益率比較')
    plt.ylabel('利率 (%)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    benchmark_rate_img = os.path.join(images_dir, "US_Benchmark_Rate_vs_10Y_Yield.png")
    plt.savefig(benchmark_rate_img)
    print(f"基準利率與國債收益率比較圖已保存至 {benchmark_rate_img}")

# 2. 美國國債總額
plt.figure(figsize=(14, 7))
if 'GFDEBTN' in debt_data.columns:
    # 轉換為萬億美元單位便於顯示
    debt_data['GFDEBTN_Trillion'] = debt_data['GFDEBTN'] / 1000000
    plt.plot(debt_data.index, debt_data['GFDEBTN_Trillion'], 'g-', linewidth=2)
    plt.title('美國聯邦政府債務總額')
    plt.ylabel('債務總額 (萬億美元)')
    plt.grid(True)
    
    # 標記重要時期
    important_years = [2001, 2008, 2020]  # 9/11, 金融危機, COVID-19
    for year in important_years:
        try:
            date_str = f"{year}-01-01"
            plt.axvline(x=pd.to_datetime(date_str), color='r', linestyle='--', alpha=0.7)
        except:
            pass
    
    plt.tight_layout()
    debt_total_img = os.path.join(images_dir, "US_Debt_Total.png")
    plt.savefig(debt_total_img)
    print(f"美國國債總額圖已保存至 {debt_total_img}")

# 3. 債務總額增長率
plt.figure(figsize=(14, 7))
if 'GFDEBTN' in debt_data.columns:
    # 計算年度增長率
    debt_data['YoY_Growth'] = debt_data['GFDEBTN'].pct_change(periods=12) * 100
    plt.plot(debt_data.index, debt_data['YoY_Growth'], 'purple', linewidth=2)
    plt.title('美國國債年度增長率')
    plt.ylabel('增長率 (%)')
    plt.axhline(y=0, color='black', linestyle='-')
    plt.grid(True)
    plt.tight_layout()
    debt_growth_img = os.path.join(images_dir, "US_Debt_Growth_Rate.png")
    plt.savefig(debt_growth_img)
    print(f"美國國債增長率圖已保存至 {debt_growth_img}")

# 4. 國債期貨價格走勢
plt.figure(figsize=(14, 7))
for symbol, name in futures_symbols.items():
    if symbol in futures_df.columns:
        plt.plot(futures_df.index, futures_df[symbol], label=name)

plt.title('美國國債期貨價格走勢')
plt.ylabel('價格')
plt.grid(True)
plt.legend()
plt.tight_layout()
futures_price_img = os.path.join(images_dir, "US_Bond_Futures_Price.png")
plt.savefig(futures_price_img)
print(f"國債期貨價格圖已保存至 {futures_price_img}")

# 5. 債務與GDP比率
try:
    gdp_data = pdr.DataReader(['GDP'], 'fred', start_date, end_date)
    merged = pd.merge(debt_data, gdp_data, left_index=True, right_index=True, how='inner')
    merged['Debt_to_GDP'] = merged['GFDEBTN'] / merged['GDP'] * 100
    
    plt.figure(figsize=(14, 7))
    plt.plot(merged.index, merged['Debt_to_GDP'], 'darkred', linewidth=2)
    plt.title('美國債務與GDP比率')
    plt.ylabel('債務佔GDP百分比 (%)')
    plt.grid(True)
    plt.tight_layout()
    debt_gdp_img = os.path.join(images_dir, "US_Debt_to_GDP_Ratio.png")
    plt.savefig(debt_gdp_img)
    print(f"債務與GDP比率圖已保存至 {debt_gdp_img}")
except Exception as e:
    print(f"計算債務與GDP比率時出錯: {e}")

# ====================
# 數據分析部分
# ====================

# 1. 當前各項數據最新值
print("\n=== 最新數據概覽 ===")

# 最新基準利率
if 'DFF' in rate_data.columns:
    latest_rate = rate_data['DFF'].iloc[-1]
    print(f"當前聯邦基金有效利率: {latest_rate:.2f}%")

# 最新10年期收益率
if 'DGS10' in bond_data.columns:
    latest_10y_yield = bond_data['DGS10'].iloc[-1]
    print(f"當前10年期國債收益率: {latest_10y_yield:.2f}%")

# 最新國債總額
if 'GFDEBTN' in debt_data.columns:
    latest_debt = debt_data['GFDEBTN'].iloc[-1]
    print(f"當前美國國債總額: {latest_debt/1000000:.2f} 萬億美元")

# 最新期貨價格
for symbol, name in futures_symbols.items():
    if symbol in futures_df.columns:
        latest_price = futures_df[symbol].iloc[-1]
        print(f"當前{name}價格: {latest_price:.2f}")

# 2. 債券相關重要指標分析
print("\n=== 債券市場指標分析 ===")

# 實質收益率 (10年期債券收益率減去通膨率)
try:
    inflation_data = pdr.DataReader(['CPIAUCSL'], 'fred', start_date, end_date)
    inflation_data['YoY_Inflation'] = inflation_data['CPIAUCSL'].pct_change(periods=12) * 100
    recent_inflation = inflation_data['YoY_Inflation'].iloc[-1]
    real_yield = latest_10y_yield - recent_inflation
    print(f"當前通膨率: {recent_inflation:.2f}%")
    print(f"10年期國債實質收益率: {real_yield:.2f}%")
    
    if real_yield < 0:
        print("警告: 實質收益率為負值，代表以長期國債對抗通膨的效果受限")
    elif real_yield < 1:
        print("注意: 實質收益率偏低，距離歷史平均水準有落差")
    else:
        print("國債實質收益率處於合理區間")
        
except Exception as e:
    print(f"計算實質收益率時出錯: {e}")

# 國債期貨與實際收益率相關性
try:
    if 'ZN=F' in futures_df.columns and 'DGS10' in bond_data.columns:
        common_dates = futures_df.index.intersection(bond_data.index)
        correlation = futures_df.loc[common_dates, 'ZN=F'].corr(bond_data.loc[common_dates, 'DGS10'])
        print(f"10年期國債期貨與收益率相關性: {correlation:.4f}")
        print("負相關性表示期貨價格與收益率呈反向關係 (收益率上升時，債券價格下跌)")
except Exception as e:
    print(f"計算相關性時出錯: {e}")

# 3. 國債償債壓力分析
print("\n=== 國債償債壓力分析 ===")
try:
    # 獲取利息支出數據
    interest_data = pdr.DataReader(['A091RC1Q027SBEA'], 'fred', start_date, end_date)
    interest_data.columns = ['Interest_Payment']
    
    # 最近一季利息支出
    recent_interest = interest_data['Interest_Payment'].iloc[-1]
    
    # 政府收入
    revenue_data = pdr.DataReader(['W006RC1Q027SBEA'], 'fred', start_date, end_date)
    revenue_data.columns = ['Government_Revenue']
    recent_revenue = revenue_data['Government_Revenue'].iloc[-1]
    
    # 利息占政府收入比例
    interest_to_revenue = recent_interest / recent_revenue * 100
    
    print(f"當前季度政府利息支出: {recent_interest:.2f} 十億美元")
    print(f"當前季度政府總收入: {recent_revenue:.2f} 十億美元")
    print(f"利息支出佔政府收入比例: {interest_to_revenue:.2f}%")
    
    if interest_to_revenue > 15:
        print("警告: 利息支出佔比較高，可能面臨償債壓力")
    elif interest_to_revenue > 10:
        print("注意: 利息支出佔比處於中等水平")
    else:
        print("利息支出佔比處於可控範圍內")
        
except Exception as e:
    print(f"計算償債壓力指標時出錯: {e}")