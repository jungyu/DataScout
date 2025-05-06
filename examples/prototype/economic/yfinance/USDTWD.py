import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from datetime import datetime
import os  # 新增 os 模組

# 設定中文字型支援
# 嘗試使用系統中存在的常見中文字型名稱列表作為優先順序
plt.rcParams['font.family'] = ['Noto Sans Gothic', 'Taipei Sans TC Beta', 'AppleGothic', 'Heiti TC']

# 解決負號顯示為方框的問題 (與中文字體問題常一起出現)
plt.rcParams['axes.unicode_minus'] = False

print("Matplotlib 已設定中文字型。")

# 設定資料夾路徑
data_dir = "../data"
images_dir = "../images"

# 確保資料夾存在
os.makedirs(data_dir, exist_ok=True)
os.makedirs(images_dir, exist_ok=True)

# 設定匯率代碼和時間範圍
currency_pair = "USDTWD=X"
start_date = "1985-01-01"  # 可以調整起始日期
end_date = datetime.now().strftime("%Y-%m-%d")  # 使用當前日期作為結束日期

# 下載歷史匯率數據
print(f"正在下載美金對台幣匯率從 {start_date} 到 {end_date} 的數據...")
exchange_rate_data = yf.download(currency_pair, start=start_date, end=end_date)

# 顯示數據的基本信息
print("\n資料概覽:")
print(f"資料起始日期: {exchange_rate_data.index.min().strftime('%Y-%m-%d')}")
print(f"資料結束日期: {exchange_rate_data.index.max().strftime('%Y-%m-%d')}")
print(f"總交易天數: {len(exchange_rate_data)}")
print("\n資料前5行:")
print(exchange_rate_data.head())

# 保存到CSV檔案
csv_filename = os.path.join(data_dir, f"USDTWD_exchange_rate_{start_date}_to_{end_date.replace('-', '_')}.csv")
exchange_rate_data.to_csv(csv_filename)
print(f"\n數據已保存至 {csv_filename}")

# 基本數據分析
print("\n基本統計數據:")
print(exchange_rate_data.describe())

# 視覺化匯率走勢
plt.figure(figsize=(12, 6))

# 繪製收盤價曲線
plt.plot(exchange_rate_data.index, exchange_rate_data['Close'], 'b-', label='收盤價')
plt.title(f'美金對台幣匯率歷史走勢 ({start_date} 到 {end_date})')
plt.ylabel('匯率 (1 USD = ? TWD)')
plt.grid(True)
plt.legend()

plt.tight_layout()
chart_filename = os.path.join(images_dir, "USDTWD_exchange_rate_chart.png")
plt.savefig(chart_filename)
print(f"匯率圖表已保存為 {chart_filename}")

# 如果想要顯示圖表，取消下一行的註解
# plt.show()

# 計算每日匯率變化百分比
exchange_rate_data['Daily_Change'] = exchange_rate_data['Close'].pct_change() * 100
print("\n每日匯率變化百分比統計:")
print(exchange_rate_data['Daily_Change'].describe())

# 找出歷史最高和最低匯率
highest_rate = float(exchange_rate_data['High'].max())
highest_idx = exchange_rate_data['High'].idxmax()
highest_date = highest_idx.strftime('%Y-%m-%d') if hasattr(highest_idx, 'strftime') else str(highest_idx)

lowest_rate = float(exchange_rate_data['Low'].min())
lowest_idx = exchange_rate_data['Low'].idxmin()
lowest_date = lowest_idx.strftime('%Y-%m-%d') if hasattr(lowest_idx, 'strftime') else str(lowest_idx)

print(f"\n歷史最高匯率: {highest_rate:.2f} TWD/USD (日期: {highest_date})")
print(f"歷史最低匯率: {lowest_rate:.2f} TWD/USD (日期: {lowest_date})")

# 列印最近30天的數據
print("\n最近30天匯率數據:")
print(exchange_rate_data.tail(30)[['Open', 'High', 'Low', 'Close']])

# 計算年度平均匯率
exchange_rate_data['Year'] = exchange_rate_data.index.year
yearly_avg = exchange_rate_data.groupby('Year')['Close'].mean()
print("\n年度平均匯率:")
print(yearly_avg)

# 視覺化年度平均匯率
plt.figure(figsize=(10, 6))
yearly_avg.plot(kind='bar', color='teal')
plt.title('美金對台幣年度平均匯率')
plt.ylabel('平均匯率 (TWD/USD)')
plt.xlabel('年份')
plt.grid(True, axis='y')
plt.tight_layout()
yearly_avg_filename = os.path.join(images_dir, "USDTWD_yearly_average.png")
plt.savefig(yearly_avg_filename)
print(f"年度平均匯率圖表已保存為 {yearly_avg_filename}")