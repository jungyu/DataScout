import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os

# 設定股票代碼和時間範圍
ticker_symbol = "AAPL"
start_date = "2010-01-01"  # 可以調整起始日期
end_date = datetime.now().strftime("%Y-%m-%d")  # 使用當前日期作為結束日期

# 設定資料夾路徑
data_dir = "../data"
images_dir = "../images"

# 確保資料夾存在
os.makedirs(data_dir, exist_ok=True)
os.makedirs(images_dir, exist_ok=True)

# 下載歷史數據
print(f"正在下載 {ticker_symbol} 從 {start_date} 到 {end_date} 的數據...")
stock_data = yf.download(ticker_symbol, start=start_date, end=end_date)

# 顯示數據的基本信息
print("\n資料概覽:")
print(f"資料起始日期: {stock_data.index.min().strftime('%Y-%m-%d')}")
print(f"資料結束日期: {stock_data.index.max().strftime('%Y-%m-%d')}")
print(f"總交易天數: {len(stock_data)}")
print("\n資料前5行:")
print(stock_data.head())

# 保存到CSV檔案
csv_filename = os.path.join(data_dir, f"{ticker_symbol}_stock_data_{start_date}_to_{end_date.replace('-', '_')}.csv")
stock_data.to_csv(csv_filename)
print(f"\n數據已保存至 {csv_filename}")

# 基本數據分析
print("\n基本統計數據:")
print(stock_data.describe())

# 視覺化股價走勢
plt.figure(figsize=(12, 8))

# 繪製收盤價曲線
plt.subplot(2, 1, 1)
plt.plot(stock_data.index, stock_data['Close'], 'b-', label='收盤價')
plt.title(f'{ticker_symbol} 歷史收盤價 ({start_date} 到 {end_date})')
plt.ylabel('價格 (USD)')
plt.grid(True)
plt.legend()

# 確保 Volume 欄位中沒有 NaN 值，並轉換為浮點數型態
stock_data['Volume'] = stock_data['Volume'].fillna(0)  # 將 NaN 值填充為 0
stock_data['Volume'] = stock_data['Volume'].astype(float)  # 確保是浮點數型態

# 確保索引是 DatetimeIndex 並且唯一
if not isinstance(stock_data.index, pd.DatetimeIndex):
    stock_data.index = pd.to_datetime(stock_data.index)  # 將索引轉換為 DatetimeIndex
if not stock_data.index.is_unique:
    stock_data = stock_data[~stock_data.index.duplicated(keep='first')]  # 移除重複索引

# 繪製成交量
plt.subplot(2, 1, 2)

# 改用數值索引並設置適當的日期標籤
x = range(len(stock_data.index))
plt.bar(x, stock_data['Volume'], color='g', alpha=0.5, label='成交量')

# 設置 x 軸標籤
# 根據數據長度選擇合適的刻度間隔
step = max(1, len(stock_data)//10)  # 最多顯示約10個刻度
plt.xticks(x[::step], [date.strftime('%Y-%m') for date in stock_data.index[::step]], rotation=45)

plt.title(f'{ticker_symbol} 歷史成交量')
plt.ylabel('成交量')
plt.grid(True)
plt.legend()

# 方案三：繪製月度成交量
monthly_volume = stock_data['Volume'].resample('M').sum()
plt.subplot(2, 1, 2)
x = range(len(monthly_volume.index))
plt.bar(x, monthly_volume, color='g', alpha=0.5, label='月度成交量')
plt.xticks(x, [date.strftime('%Y-%m') for date in monthly_volume.index], rotation=45)
plt.title(f'{ticker_symbol} 月度成交量')
plt.ylabel('成交量')
plt.grid(True)
plt.legend()

plt.tight_layout()
png_filename = os.path.join(images_dir, f"{ticker_symbol}_stock_chart.png")
plt.savefig(png_filename)
print(f"股價圖表已保存為 {png_filename}")

# 如果想要顯示圖表，取消下一行的註解
# plt.show()

# 計算每日漲跌幅
stock_data['Daily_Return'] = stock_data['Close'].pct_change() * 100
print("\n每日漲跌幅統計:")
print(stock_data['Daily_Return'].describe())

# 找出歷史最高和最低價格
highest_price = stock_data['High'].max()
highest_date = stock_data['High'].idxmax().strftime('%Y-%m-%d')
lowest_price = stock_data['Low'].min()
lowest_date = stock_data['Low'].idxmin().strftime('%Y-%m-%d')

print(f"\n歷史最高價: ${highest_price:.2f} (日期: {highest_date})")
print(f"歷史最低價: ${lowest_price:.2f} (日期: {lowest_date})")

# 列印最近30天的數據
print("\n最近30天數據:")
print(stock_data.tail(30)[['Open', 'High', 'Low', 'Close', 'Volume']])