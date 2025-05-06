import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from datetime import datetime
import sys
import os

# 設定中文字型支援
# 嘗試使用系統中存在的常見中文字型名稱列表作為優先順序
plt.rcParams['font.family'] = ['Noto Sans Gothic', 'Taipei Sans TC Beta', 'AppleGothic', 'Heiti TC']

# 解決負號顯示為方框的問題 (與中文字體問題常一起出現)
plt.rcParams['axes.unicode_minus'] = False

print("Matplotlib 已設定中文字型。")

# 設定黃金價格代碼和時間範圍
gold_symbol = "GC=F"  # 黃金期貨價格 (美元/盎司)
start_date = "2000-01-01"  # 可以調整起始日期
end_date = datetime.now().strftime("%Y-%m-%d")  # 使用當前日期作為結束日期

# 下載歷史黃金價格數據
print(f"正在下載黃金期貨價格從 {start_date} 到 {end_date} 的數據...")
gold_data = yf.download(gold_symbol, start=start_date, end=end_date)

# 檢查是否成功下載數據
if gold_data.empty:
    print(f"錯誤：無法下載 {gold_symbol} 的數據。")
    print("請嘗試以下替代黃金相關代碼之一：")
    print("- GC=F (黃金期貨)")
    print("- GLD (SPDR 黃金股票 ETF)")
    print("- IAU (iShares 黃金股票 ETF)")
    print("- GOLD (巴里克黃金公司)")
    sys.exit(1)

# 顯示數據的基本信息
print("\n資料概覽:")
print(f"資料起始日期: {gold_data.index.min().strftime('%Y-%m-%d')}")
print(f"資料結束日期: {gold_data.index.max().strftime('%Y-%m-%d')}")
print(f"總交易天數: {len(gold_data)}")
print("\n資料前5行:")
print(gold_data.head())

# 設定資料夾路徑
data_dir = "../data"
images_dir = "../images"

# 確保資料夾存在
os.makedirs(data_dir, exist_ok=True)
os.makedirs(images_dir, exist_ok=True)

# 保存到CSV檔案
csv_filename = os.path.join(data_dir, f"Gold_price_{start_date}_to_{end_date.replace('-', '_')}.csv")
gold_data.to_csv(csv_filename)
print(f"\n數據已保存至 {csv_filename}")

# 基本數據分析
print("\n基本統計數據:")
print(gold_data[['Open', 'High', 'Low', 'Close', 'Volume']].describe())

# 視覺化黃金價格走勢
plt.figure(figsize=(12, 6))

# 繪製收盤價曲線
plt.plot(gold_data.index, gold_data['Close'], 'b-', label='收盤價')
plt.title(f'黃金價格歷史走勢 ({start_date} 到 {end_date})')
plt.ylabel('價格 (USD/oz)')
plt.grid(True)
plt.legend()

plt.tight_layout()
gold_price_chart = os.path.join(images_dir, "Gold_price_chart.png")
plt.savefig(gold_price_chart)
print(f"黃金價格圖表已保存為 {gold_price_chart}")

# 如果想要顯示圖表，取消下一行的註解
# plt.show()

# 計算每日價格變化百分比
gold_data['每日漲跌幅'] = gold_data['Close'].pct_change() * 100
print("\n每日價格變化百分比統計:")
print(gold_data['每日漲跌幅'].describe())

# 找出歷史最高和最低價格
highest_price = float(gold_data['High'].max())
highest_idx = gold_data['High'].idxmax()
highest_date = highest_idx.strftime('%Y-%m-%d') if hasattr(highest_idx, 'strftime') else str(highest_idx)

lowest_price = float(gold_data['Low'].min())
lowest_idx = gold_data['Low'].idxmin()
lowest_date = lowest_idx.strftime('%Y-%m-%d') if hasattr(lowest_idx, 'strftime') else str(lowest_idx)

print(f"\n歷史最高價格: {highest_price:.2f} USD/oz (日期: {highest_date})")
print(f"歷史最低價格: {lowest_price:.2f} USD/oz (日期: {lowest_date})")

# 列印最近30天的價格數據
print("\n最近30天黃金價格數據:")
print(gold_data.tail(30)[['Open', 'High', 'Low', 'Close']])

# 計算年度平均價格
gold_data['Year'] = gold_data.index.year
yearly_avg = gold_data.groupby('Year').mean()[['Close']]
print("\n年度平均黃金價格:")
print(yearly_avg)

# 視覺化年度平均價格
plt.figure(figsize=(10, 6))
yearly_avg.plot(kind='bar', color='gold')
plt.title('年度平均黃金價格')
plt.ylabel('平均價格 (USD/oz)')
plt.xlabel('年份')
plt.grid(True, axis='y')
plt.tight_layout()
gold_yearly_prices = os.path.join(images_dir, "Gold_yearly_prices.png")
plt.savefig(gold_yearly_prices)
print(f"年度黃金價格圖表已保存為 {gold_yearly_prices}")

# 分析黃金價格的月度趨勢
gold_data['Month'] = gold_data.index.month
monthly_avg = gold_data.groupby('Month').mean()[['Close']]

plt.figure(figsize=(10, 6))
monthly_avg.plot(kind='line', marker='o', color='goldenrod')
plt.title('黃金價格的月度趨勢')
plt.xlabel('月份')
plt.ylabel('平均價格 (USD/oz)')
plt.grid(True)
plt.xticks(range(1, 13))
gold_monthly_trend = os.path.join(images_dir, "Gold_monthly_trend.png")
plt.savefig(gold_monthly_trend)
print(f"黃金價格月度趨勢圖已保存為 {gold_monthly_trend}")