import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from datetime import datetime
import sys
import os  # 新增 os 模組

# 設定中文字型支援
plt.rcParams['font.family'] = ['Noto Sans Gothic', 'Taipei Sans TC Beta', 'AppleGothic', 'Heiti TC']
plt.rcParams['axes.unicode_minus'] = False
print("Matplotlib 已設定中文字型。")

# 定義資料夾路徑
data_dir = "../data"
images_dir = "../images"

# 確保資料夾存在
os.makedirs(data_dir, exist_ok=True)
os.makedirs(images_dir, exist_ok=True)

# 定義檔案路徑
gold_file = os.path.join(data_dir, "Gold_price_2000-01-01_to_2025_05_06.csv")
exchange_file = os.path.join(data_dir, "USDTWD_exchange_rate_1985-01-01_to_2025_05_06.csv")

# 修正: 讀取資料時正確處理非標準CSV格式
print("讀取黃金價格及匯率資料...")
try:
    # 讀取前幾行以檢查檔案結構
    gold_header = pd.read_csv(gold_file, nrows=3)
    exchange_header = pd.read_csv(exchange_file, nrows=3)
    
    print("檔案頭部結構:")
    print(gold_header)
    
    # 修正讀取方式: 跳過前3行，並將第一列作為索引
    gold_data = pd.read_csv(gold_file, skiprows=3, index_col=0, parse_dates=True)
    exchange_data = pd.read_csv(exchange_file, skiprows=3, index_col=0, parse_dates=True)
    
    # 重新命名金價資料欄位
    gold_data.columns = ['Close_Gold', 'High_Gold', 'Low_Gold', 'Open_Gold', 'Volume_Gold']
    
    # 重新命名匯率資料欄位
    exchange_data.columns = ['Close_TWD', 'High_TWD', 'Low_TWD', 'Open_TWD', 'Volume_TWD']
    
    print("\n成功讀取資料")
    print(f"黃金資料筆數: {len(gold_data)}")
    print(f"匯率資料筆數: {len(exchange_data)}")
    
except FileNotFoundError:
    print("錯誤：找不到必要的資料檔案")
    sys.exit(1)
except Exception as e:
    print(f"讀取資料時發生錯誤: {e}")
    print("嘗試替代讀取方式...")
    try:
        # 第二種嘗試: 不指定欄位名稱，只指定跳過的行數
        gold_data = pd.read_csv(gold_file, skiprows=3, header=None)
        gold_data.index = pd.to_datetime(gold_data[0])
        gold_data = gold_data.drop(0, axis=1)
        gold_data.columns = ['Close_Gold', 'High_Gold', 'Low_Gold', 'Open_Gold', 'Volume_Gold']
        
        exchange_data = pd.read_csv(exchange_file, skiprows=3, header=None)
        exchange_data.index = pd.to_datetime(exchange_data[0])
        exchange_data = exchange_data.drop(0, axis=1)
        exchange_data.columns = ['Close_TWD', 'High_TWD', 'Low_TWD', 'Open_TWD', 'Volume_TWD']
        
        print("使用替代方式讀取成功")
    except Exception as e2:
        print(f"替代讀取方式也失敗: {e2}")
        sys.exit(1)

# 合併資料
print("合併資料並計算台幣黃金價格...")
merged_data = pd.merge(gold_data, exchange_data, left_index=True, right_index=True, how='inner')

# 檢查合併後的資料是否為空
if (merged_data.empty):
    print("錯誤：無法合併資料，可能沒有日期重疊。")
    sys.exit(1)

print(f"合併後資料欄位: {merged_data.columns.tolist()}")

# 計算台幣黃金價格
merged_data['Close_TWD_Gold'] = merged_data['Close_Gold'] * merged_data['Close_TWD']
merged_data['Open_TWD_Gold'] = merged_data['Open_Gold'] * merged_data['Open_TWD']
merged_data['High_TWD_Gold'] = merged_data['High_Gold'] * merged_data['High_TWD']
merged_data['Low_TWD_Gold'] = merged_data['Low_Gold'] * merged_data['Low_TWD']

# 顯示資料的基本信息
print("\n台幣黃金價格資料概覽:")
print(f"資料起始日期: {merged_data.index.min().strftime('%Y-%m-%d')}")
print(f"資料結束日期: {merged_data.index.max().strftime('%Y-%m-%d')}")
print(f"總交易天數: {len(merged_data)}")
print("\n資料前5行:")
print(merged_data[['Close_Gold', 'Close_TWD', 'Close_TWD_Gold']].head())

# 保存到CSV檔案
csv_filename = os.path.join(data_dir, f"Gold_TWD_price_{merged_data.index.min().strftime('%Y-%m-%d')}_to_{merged_data.index.max().strftime('%Y-%m-%d')}.csv")
merged_data.to_csv(csv_filename)
print(f"\n台幣黃金價格數據已保存至 {csv_filename}")

# 基本數據分析
print("\n基本統計數據 (台幣黃金價格):")
twd_gold_stats = merged_data[['Open_TWD_Gold', 'High_TWD_Gold', 'Low_TWD_Gold', 'Close_TWD_Gold']].describe()
print(twd_gold_stats)

# 視覺化台幣黃金價格走勢
plt.figure(figsize=(12, 8))

# 繪製台幣黃金收盤價曲線
plt.subplot(2, 1, 1)
plt.plot(merged_data.index, merged_data['Close_TWD_Gold'], 'b-', label='台幣黃金收盤價')
plt.title(f'台幣黃金價格歷史走勢 ({merged_data.index.min().strftime("%Y-%m-%d")} 到 {merged_data.index.max().strftime("%Y-%m-%d")})')
plt.ylabel('價格 (TWD/oz)')
plt.grid(True)
plt.legend()

# 繪製匯率走勢
plt.subplot(2, 1, 2)
plt.plot(merged_data.index, merged_data['Close_TWD'], 'g-', label='USD/TWD 匯率')
plt.title('美元兌台幣匯率走勢')
plt.ylabel('匯率 (TWD/USD)')
plt.grid(True)
plt.legend()

plt.tight_layout()
chart_filename = os.path.join(images_dir, "Gold_TWD_price_chart.png")
plt.savefig(chart_filename)
print(f"台幣黃金價格圖表已保存為 {chart_filename}")

# 計算每日價格變化百分比
merged_data['每日漲跌幅_台幣黃金'] = merged_data['Close_TWD_Gold'].pct_change() * 100
merged_data['每日漲跌幅_美元黃金'] = merged_data['Close_Gold'].pct_change() * 100
merged_data['每日漲跌幅_匯率'] = merged_data['Close_TWD'].pct_change() * 100

print("\n每日價格變化百分比統計 (台幣黃金):")
print(merged_data['每日漲跌幅_台幣黃金'].describe())

# 找出歷史最高和最低台幣黃金價格
highest_price = float(merged_data['High_TWD_Gold'].max())
highest_idx = merged_data['High_TWD_Gold'].idxmax()
highest_date = highest_idx.strftime('%Y-%m-%d') if hasattr(highest_idx, 'strftime') else str(highest_idx)

lowest_price = float(merged_data['Low_TWD_Gold'].min())
lowest_idx = merged_data['Low_TWD_Gold'].idxmin()
lowest_date = lowest_idx.strftime('%Y-%m-%d') if hasattr(lowest_idx, 'strftime') else str(lowest_idx)

print(f"\n歷史最高台幣黃金價格: {highest_price:.2f} TWD/oz (日期: {highest_date})")
print(f"歷史最低台幣黃金價格: {lowest_price:.2f} TWD/oz (日期: {lowest_date})")

# 列印最近30天的價格數據
print("\n最近30天台幣黃金價格數據:")
recent_data = merged_data.tail(30)[['Open_TWD_Gold', 'High_TWD_Gold', 'Low_TWD_Gold', 'Close_TWD_Gold', 'Close_Gold', 'Close_TWD']]
recent_data.columns = ['開盤價(台幣)', '最高價(台幣)', '最低價(台幣)', '收盤價(台幣)', '收盤價(美元)', '匯率(USD/TWD)']
print(recent_data)

# 計算年度平均價格
merged_data['Year'] = merged_data.index.year
yearly_avg = merged_data.groupby('Year').mean()[['Close_TWD_Gold', 'Close_Gold', 'Close_TWD']]
yearly_avg.columns = ['台幣黃金均價', '美元黃金均價', '年均匯率']
print("\n年度平均台幣黃金價格:")
print(yearly_avg)

# 視覺化年度平均價格
plt.figure(figsize=(12, 10))

# 台幣黃金年度均價
plt.subplot(3, 1, 1)
yearly_avg['台幣黃金均價'].plot(kind='bar', color='red')
plt.title('年度平均台幣黃金價格')
plt.ylabel('價格 (TWD/oz)')
plt.grid(True, axis='y')

# 美元黃金年度均價
plt.subplot(3, 1, 2)
yearly_avg['美元黃金均價'].plot(kind='bar', color='gold')
plt.title('年度平均美元黃金價格')
plt.ylabel('價格 (USD/oz)')
plt.grid(True, axis='y')

# 年度平均匯率
plt.subplot(3, 1, 3)
yearly_avg['年均匯率'].plot(kind='bar', color='green')
plt.title('年度平均美元兌台幣匯率')
plt.ylabel('匯率 (TWD/USD)')
plt.xlabel('年份')
plt.grid(True, axis='y')

plt.tight_layout()
yearly_chart_filename = os.path.join(images_dir, "Gold_TWD_yearly_prices.png")
plt.savefig(yearly_chart_filename)
print(f"年度台幣黃金價格圖表已保存為 {yearly_chart_filename}")

# 比較投資分析：計算年度投資報酬率
yearly_returns = pd.DataFrame(index=yearly_avg.index)
yearly_returns['台幣黃金報酬率(%)'] = yearly_avg['台幣黃金均價'].pct_change() * 100
yearly_returns['美元黃金報酬率(%)'] = yearly_avg['美元黃金均價'].pct_change() * 100
yearly_returns['匯率變化率(%)'] = yearly_avg['年均匯率'].pct_change() * 100

print("\n年度投資報酬率比較 (台幣黃金 vs 美元黃金):")
print(yearly_returns)

# 視覺化年度報酬率比較
plt.figure(figsize=(12, 6))
yearly_returns[['台幣黃金報酬率(%)', '美元黃金報酬率(%)']].plot(kind='bar')
plt.title('年度黃金投資報酬率比較: 台幣計價 vs 美元計價')
plt.ylabel('年度報酬率 (%)')
plt.grid(True, axis='y')
plt.tight_layout()
returns_chart_filename = os.path.join(images_dir, "Gold_TWD_vs_USD_returns.png")
plt.savefig(returns_chart_filename)
print(f"年度報酬率比較圖表已保存為 {returns_chart_filename}")