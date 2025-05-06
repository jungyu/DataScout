import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from datetime import datetime
import os
import sys

# 設定中文字型支援
# 嘗試使用系統中存在的常見中文字型名稱列表作為優先順序
plt.rcParams['font.family'] = ['Noto Sans Gothic', 'Taipei Sans TC Beta', 'AppleGothic', 'Heiti TC']

# 解決負號顯示為方框的問題 (與中文字體問題常一起出現)
plt.rcParams['axes.unicode_minus'] = False

print("Matplotlib 已設定中文字型。")

# 設定銅價代碼和時間範圍
copper_symbol = "HG=F"  # 銅期貨價格 (美元/磅)
start_date = "2000-01-01"  # 可以調整起始日期
end_date = datetime.now().strftime("%Y-%m-%d")  # 使用當前日期作為結束日期

# 設定資料夾路徑
data_dir = "../data"
images_dir = "../images"

# 確保資料夾存在
os.makedirs(data_dir, exist_ok=True)
os.makedirs(images_dir, exist_ok=True)

# 下載歷史銅價數據
print(f"正在下載銅期貨價格從 {start_date} 到 {end_date} 的數據...")
copper_data = yf.download(copper_symbol, start=start_date, end=end_date)

# 檢查是否成功下載數據
if copper_data.empty:
    print(f"錯誤：無法下載 {copper_symbol} 的數據。")
    print("請嘗試以下替代銅相關代碼之一：")
    print("- HG=F (銅期貨)")
    print("- CPER (United States Copper Index Fund)")
    print("- JJCTF (iPath Bloomberg Copper Subindex)")
    print("- COPX (Global X Copper Miners ETF)")
    sys.exit(1)

# 顯示數據的基本信息
print("\n資料概覽:")
print(f"資料起始日期: {copper_data.index.min().strftime('%Y-%m-%d')}")
print(f"資料結束日期: {copper_data.index.max().strftime('%Y-%m-%d')}")
print(f"總交易天數: {len(copper_data)}")
print("\n資料前5行:")
print(copper_data.head())

# 保存到CSV檔案
csv_filename = os.path.join(data_dir, f"Copper_price_{start_date}_to_{end_date.replace('-', '_')}.csv")
copper_data.to_csv(csv_filename)
print(f"\n數據已保存至 {csv_filename}")

# 基本數據分析
print("\n基本統計數據:")
print(copper_data[['Open', 'High', 'Low', 'Close', 'Volume']].describe())

# 視覺化銅價走勢
plt.figure(figsize=(12, 6))

# 繪製收盤價曲線
plt.plot(copper_data.index, copper_data['Close'], 'r-', label='收盤價')
plt.title(f'銅價歷史走勢 ({start_date} 到 {end_date})')
plt.ylabel('價格 (USD/lb)')
plt.grid(True)
plt.legend()

plt.tight_layout()
price_chart_filename = os.path.join(images_dir, "Copper_price_chart.png")
plt.savefig(price_chart_filename)
print(f"銅價圖表已保存為 {price_chart_filename}")

# 如果想要顯示圖表，取消下一行的註解
# plt.show()

# 計算每日價格變化百分比
copper_data['每日漲跌幅'] = copper_data['Close'].pct_change() * 100
print("\n每日價格變化百分比統計:")
print(copper_data['每日漲跌幅'].describe())

# 找出歷史最高和最低價格
highest_price = float(copper_data['High'].max())
highest_idx = copper_data['High'].idxmax()
highest_date = highest_idx.strftime('%Y-%m-%d') if hasattr(highest_idx, 'strftime') else str(highest_idx)

lowest_price = float(copper_data['Low'].min())
lowest_idx = copper_data['Low'].idxmin()
lowest_date = lowest_idx.strftime('%Y-%m-%d') if hasattr(lowest_idx, 'strftime') else str(lowest_idx)

print(f"\n歷史最高價格: {highest_price:.2f} USD/lb (日期: {highest_date})")
print(f"歷史最低價格: {lowest_price:.2f} USD/lb (日期: {lowest_date})")

# 列印最近30天的價格數據
print("\n最近30天銅價數據:")
print(copper_data.tail(30)[['Open', 'High', 'Low', 'Close']])

# 計算年度平均價格
copper_data['Year'] = copper_data.index.year
yearly_avg = copper_data.groupby('Year').mean()[['Close']]
print("\n年度平均銅價:")
print(yearly_avg)

# 視覺化年度平均價格
plt.figure(figsize=(10, 6))
# 使用有效的銅色系顏色代替 'copper'
yearly_avg.plot(kind='bar', color='#B87333')  # 使用銅的 HEX 色碼
plt.title('年度平均銅價')
plt.ylabel('平均價格 (USD/lb)')
plt.xlabel('年份')
plt.grid(True, axis='y')
plt.tight_layout()
yearly_prices_filename = os.path.join(images_dir, "Copper_yearly_prices.png")
plt.savefig(yearly_prices_filename)
print(f"年度銅價圖表已保存為 {yearly_prices_filename}")

# 分析銅價的月度趨勢
copper_data['Month'] = copper_data.index.month
monthly_avg = copper_data.groupby('Month').mean()[['Close']]

plt.figure(figsize=(10, 6))
monthly_avg.plot(kind='line', marker='o', color='#B87333')  # 使用相同的銅色 HEX 碼
plt.title('銅價的月度趨勢')
plt.xlabel('月份')
plt.ylabel('平均價格 (USD/lb)')
plt.grid(True)
plt.xticks(range(1, 13))
monthly_trend_filename = os.path.join(images_dir, "Copper_monthly_trend.png")
plt.savefig(monthly_trend_filename)
print(f"銅價月度趨勢圖已保存為 {monthly_trend_filename}")

# 增加銅價與製造業關係分析
print("\n銅價波動特性分析:")
print("銅被稱為「博士」，其價格走勢常被視為全球製造業和經濟健康的重要指標")

# 修正: 將 Series 轉換為 float - 使用 .item() 而不是 float()
mean_series = copper_data.loc[copper_data.index >= copper_data.index.max() - pd.DateOffset(years=5), 'Close'].mean()
mean_price = mean_series.item() if hasattr(mean_series, 'item') else float(mean_series)
print(f"過去5年平均價格: {mean_price:.2f} USD/lb")

# 計算1年、5年和10年回報率
periods = {
    "1年": 1,
    "5年": 5,
    "10年": 10
}

print("\n銅價長期投資表現:")
for period_name, years in periods.items():
    try:
        start_idx = copper_data.index.max() - pd.DateOffset(years=years)
        if start_idx < copper_data.index.min():
            print(f"{period_name}投資回報率: 資料不足")
            continue
        
        # 修正: 使用 .item() 方法從 Series 取出單一數值
        temp_series = copper_data.loc[copper_data.index >= start_idx, 'Close']
        if not temp_series.empty:
            start_price = temp_series.iloc[0].item()  # 修正警告
            end_price = copper_data['Close'].iloc[-1].item()  # 修正警告
            return_pct = (end_price - start_price) / start_price * 100
            print(f"{period_name}投資回報率: {return_pct:.2f}%")
        else:
            print(f"{period_name}投資回報率: 資料不足")
    except Exception as e:
        print(f"{period_name}投資回報率計算錯誤: {e}")