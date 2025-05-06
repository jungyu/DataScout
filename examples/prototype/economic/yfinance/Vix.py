import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from datetime import datetime
import sys
import numpy as np
import os  # 新增 os 模組

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

# 設定波動率指數代碼和時間範圍
vix_symbol = "^VIX"  # 波動率指數代碼
start_date = "2000-01-01"  # 可以調整起始日期
end_date = datetime.now().strftime("%Y-%m-%d")  # 使用當前日期作為結束日期

# 下載歷史波動率指數數據
print(f"正在下載波動率指數從 {start_date} 到 {end_date} 的數據...")
vix_data = yf.download(vix_symbol, start=start_date, end=end_date)

# 檢查是否成功下載數據
if vix_data.empty:
    print(f"錯誤：無法下載 {vix_symbol} 的數據。")
    sys.exit(1)

# 顯示數據的基本信息
print("\n資料概覽:")
print(f"資料起始日期: {vix_data.index.min().strftime('%Y-%m-%d')}")
print(f"資料結束日期: {vix_data.index.max().strftime('%Y-%m-%d')}")
print(f"總交易天數: {len(vix_data)}")
print("\n資料前5行:")
print(vix_data.head())

# 保存到CSV檔案
csv_filename = os.path.join(data_dir, f"VIX_price_{start_date}_to_{end_date.replace('-', '_')}.csv")
vix_data.to_csv(csv_filename)
print(f"\n數據已保存至 {csv_filename}")

# 基本數據分析
print("\n基本統計數據:")
print(vix_data[['Open', 'High', 'Low', 'Close', 'Volume']].describe())

# 視覺化波動率指數走勢
plt.figure(figsize=(12, 6))

# 繪製收盤價曲線
plt.plot(vix_data.index, vix_data['Close'], 'b-', label='收盤價')
plt.title(f'波動率指數 (VIX) 歷史走勢 ({start_date} 到 {end_date})')
plt.ylabel('指數點數')
plt.grid(True)
plt.legend()

# 標記重要經濟事件
events = {
    '2008-09-15': '雷曼兄弟破產',
    '2020-03-16': 'COVID-19恐慌高點',
    '2022-01-03': '升息週期開始'
}

for date, event in events.items():
    try:
        event_date = pd.to_datetime(date)
        if event_date >= vix_data.index.min() and event_date <= vix_data.index.max():
            idx = vix_data.index[vix_data.index.get_indexer([event_date], method='nearest')[0]]
            price = vix_data.loc[idx, 'Close']
            plt.plot(idx, price, 'ro')
            plt.annotate(event, xy=(idx, price), xytext=(10, -20),
                         textcoords='offset points', arrowprops=dict(arrowstyle='->'))
    except:
        print(f"無法標記事件: {event} ({date})")

plt.tight_layout()
price_chart_path = os.path.join(images_dir, "VIX_price_chart.png")
plt.savefig(price_chart_path)
print(f"波動率指數圖表已保存為 {price_chart_path}")

# 計算每日價格變化百分比
vix_data['每日漲跌幅'] = vix_data['Close'].pct_change() * 100
print("\n每日價格變化百分比統計:")
print(vix_data['每日漲跌幅'].describe())

# 找出歷史最高和最低價格
highest_price = float(vix_data['High'].max())
highest_idx = vix_data['High'].idxmax()
highest_date = highest_idx.strftime('%Y-%m-%d') if hasattr(highest_idx, 'strftime') else str(highest_idx)

lowest_price = float(vix_data['Low'].min())
lowest_idx = vix_data['Low'].idxmin()
lowest_date = lowest_idx.strftime('%Y-%m-%d') if hasattr(lowest_idx, 'strftime') else str(lowest_idx)

print(f"\n歷史最高點數: {highest_price:.2f} (日期: {highest_date})")
print(f"歷史最低點數: {lowest_price:.2f} (日期: {lowest_date})")

# 列印最近30天的價格數據
print("\n最近30天波動率指數數據:")
print(vix_data.tail(30)[['Open', 'High', 'Low', 'Close']])

# 計算年度平均價格
vix_data['Year'] = vix_data.index.year
yearly_avg = vix_data.groupby('Year').mean()[['Close']]

print("\n年度平均波動率指數:")
print(yearly_avg)

# 視覺化年度平均價格
plt.figure(figsize=(12, 6))
yearly_avg.plot(kind='bar', color='steelblue')
plt.title('年度平均波動率指數 (VIX)')
plt.ylabel('指數平均點數')
plt.xlabel('年份')
plt.grid(True, axis='y')
plt.tight_layout()
yearly_avg_path = os.path.join(images_dir, "VIX_yearly_avg.png")
plt.savefig(yearly_avg_path)
print(f"年度波動率指數圖表已保存為 {yearly_avg_path}")

# 分析波動率指數的月度趨勢
vix_data['Month'] = vix_data.index.month
monthly_avg = vix_data.groupby('Month').mean()[['Close']]

plt.figure(figsize=(10, 6))
monthly_avg.plot(kind='line', marker='o', color='darkblue')
plt.title('波動率指數 (VIX) 的月度趨勢')
plt.xlabel('月份')
plt.ylabel('平均指數點數')
plt.grid(True)
plt.xticks(range(1, 13), ['一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '十二月'])
monthly_trend_path = os.path.join(images_dir, "VIX_monthly_trend.png")
plt.savefig(monthly_trend_path)
print(f"波動率指數月度趨勢圖已保存為 {monthly_trend_path}")

# 計算波動率的20日移動平均
vix_data['20日移動平均'] = vix_data['Close'].rolling(window=20).mean()

plt.figure(figsize=(12, 6))
plt.plot(vix_data.index, vix_data['Close'], label='收盤價', alpha=0.6)
plt.plot(vix_data.index, vix_data['20日移動平均'], label='20日移動平均', color='orange')
plt.title('波動率指數 (VIX) 與20日移動平均')
plt.ylabel('指數點數')
plt.grid(True)
plt.legend()
plt.tight_layout()
moving_avg_path = os.path.join(images_dir, "VIX_moving_avg.png")
plt.savefig(moving_avg_path)
print(f"波動率指數與20日移動平均圖表已保存為 {moving_avg_path}")