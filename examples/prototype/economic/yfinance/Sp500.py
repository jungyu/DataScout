import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from datetime import datetime
import sys
import numpy as np
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

# 設定標普500指數代碼和時間範圍
sp500_symbol = "^GSPC"  # 標普500指數代碼
start_date = "2000-01-01"  # 可以調整起始日期
end_date = datetime.now().strftime("%Y-%m-%d")  # 使用當前日期作為結束日期

# 下載歷史標普500指數數據
print(f"正在下載標普500指數從 {start_date} 到 {end_date} 的數據...")
sp500_data = yf.download(sp500_symbol, start=start_date, end=end_date)

# 檢查是否成功下載數據
if (sp500_data.empty):
    print(f"錯誤：無法下載 {sp500_symbol} 的數據。")
    print("請嘗試以下替代標普500相關代碼之一：")
    print("- ^GSPC (標普500指數)")
    print("- SPY (SPDR 標普500 ETF)")
    print("- VOO (Vanguard 標普500 ETF)")
    print("- IVV (iShares Core 標普500 ETF)")
    sys.exit(1)

# 顯示數據的基本信息
print("\n資料概覽:")
print(f"資料起始日期: {sp500_data.index.min().strftime('%Y-%m-%d')}")
print(f"資料結束日期: {sp500_data.index.max().strftime('%Y-%m-%d')}")
print(f"總交易天數: {len(sp500_data)}")
print("\n資料前5行:")
print(sp500_data.head())

# 保存到CSV檔案
csv_filename = os.path.join(data_dir, f"SP500_price_{start_date}_to_{end_date.replace('-', '_')}.csv")
sp500_data.to_csv(csv_filename)
print(f"\n數據已保存至 {csv_filename}")

# 基本數據分析
print("\n基本統計數據:")
print(sp500_data[['Open', 'High', 'Low', 'Close', 'Volume']].describe())

# 視覺化標普500指數走勢
plt.figure(figsize=(12, 6))

# 繪製收盤價曲線
plt.plot(sp500_data.index, sp500_data['Close'], 'b-', label='收盤價')
plt.title(f'標普500指數歷史走勢 ({start_date} 到 {end_date})')
plt.ylabel('指數點數')
plt.grid(True)
plt.legend()

# 標記重要經濟事件
events = {
    '2001-09-11': '911事件',
    '2008-09-15': '雷曼兄弟破產',
    '2020-03-23': 'COVID-19低點',
    '2022-01-03': '升息週期開始'
}

for date, event in events.items():
    try:
        event_date = pd.to_datetime(date)
        if event_date >= sp500_data.index.min() and event_date <= sp500_data.index.max():
            idx = sp500_data.index[sp500_data.index.get_indexer([event_date], method='nearest')[0]]
            price = sp500_data.loc[idx, 'Close']
            plt.plot(idx, price, 'ro')
            plt.annotate(event, xy=(idx, price), xytext=(10, -20),
                        textcoords='offset points', arrowprops=dict(arrowstyle='->'))
    except:
        print(f"無法標記事件: {event} ({date})")

plt.tight_layout()
price_chart_path = os.path.join(images_dir, "SP500_price_chart.png")
plt.savefig(price_chart_path)
print(f"標普500指數圖表已保存為 {price_chart_path}")

# 計算每日價格變化百分比
sp500_data['每日漲跌幅'] = sp500_data['Close'].pct_change() * 100
print("\n每日價格變化百分比統計:")
print(sp500_data['每日漲跌幅'].describe())

# 找出歷史最高和最低價格
highest_price = float(sp500_data['High'].max())
highest_idx = sp500_data['High'].idxmax()
highest_date = highest_idx.strftime('%Y-%m-%d') if hasattr(highest_idx, 'strftime') else str(highest_idx)

lowest_price = float(sp500_data['Low'].min())
lowest_idx = sp500_data['Low'].idxmin()
lowest_date = lowest_idx.strftime('%Y-%m-%d') if hasattr(lowest_idx, 'strftime') else str(lowest_idx)

print(f"\n歷史最高點數: {highest_price:.2f} (日期: {highest_date})")
print(f"歷史最低點數: {lowest_price:.2f} (日期: {lowest_date})")

# 列印最近30天的價格數據
print("\n最近30天標普500指數數據:")
print(sp500_data.tail(30)[['Open', 'High', 'Low', 'Close']])

# 計算年度平均價格和年度回報率
sp500_data['Year'] = sp500_data.index.year
yearly_avg = sp500_data.groupby('Year').mean()[['Close']]

# 修正年度回報率計算方式 - 確保獲取的是純數值
# 計算每年最後一個交易日的收盤價
sp500_data['Year'] = sp500_data.index.year

# 獲取每年第一個和最後一個交易日的數據
yearly_first = sp500_data.groupby('Year').first()
yearly_last = sp500_data.groupby('Year').last()

# 正確計算年度回報率 - 使用純數值
yearly_returns = ((yearly_last['Close'] - yearly_first['Close']) / yearly_first['Close'] * 100)

print("\n年度回報率:")
print(yearly_returns)

# 視覺化年度平均價格和回報率
plt.figure(figsize=(12, 10))

# 年度平均指數
plt.subplot(2, 1, 1)
yearly_avg.plot(kind='bar', color='steelblue')
plt.title('年度平均標普500指數')
plt.ylabel('指數平均點數')
plt.grid(True, axis='y')

# 年度回報率（修正顏色設置方式）
plt.subplot(2, 1, 2)
# 確保 yearly_returns 是數值型，然後創建顏色列表
colors = ['green' if x >= 0 else 'red' for x in yearly_returns.values]
yearly_returns.plot(kind='bar', color=colors)
plt.title('標普500年度回報率')
plt.ylabel('回報率 (%)')
plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
plt.grid(True, axis='y')

plt.tight_layout()
yearly_analysis_path = os.path.join(images_dir, "SP500_yearly_analysis.png")
plt.savefig(yearly_analysis_path)
print(f"標普500年度分析圖表已保存為 {yearly_analysis_path}")

# 分析標普500指數的月度趨勢
sp500_data['Month'] = sp500_data.index.month
monthly_avg = sp500_data.groupby('Month').mean()[['Close']]

plt.figure(figsize=(10, 6))
monthly_avg.plot(kind='line', marker='o', color='darkblue')
plt.title('標普500指數的月度趨勢')
plt.xlabel('月份')
plt.ylabel('平均指數點數')
plt.grid(True)
plt.xticks(range(1, 13), ['一月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '十二月'])
monthly_trend_path = os.path.join(images_dir, "SP500_monthly_trend.png")
plt.savefig(monthly_trend_path)
print(f"標普500指數月度趨勢圖已保存為 {monthly_trend_path}")

# 計算波動度 (20日標準差年化)
sp500_data['volatility'] = sp500_data['每日漲跌幅'].rolling(window=20).std() * np.sqrt(252)

plt.figure(figsize=(12, 6))
plt.plot(sp500_data.index, sp500_data['volatility'], 'r-')
plt.title('標普500指數波動率 (20交易日移動窗口)')
plt.ylabel('年化波動率 (%)')
plt.grid(True)
plt.tight_layout()
volatility_path = os.path.join(images_dir, "SP500_volatility.png")
plt.savefig(volatility_path)
print(f"標普500波動率圖表已保存為 {volatility_path}")

# 熊市和牛市分析
# 定義熊市為從高點下跌20%或以上，牛市為從低點上漲20%或以上
# 修正熊市和牛市分析函數
def detect_bear_bull_markets(data, threshold=0.2):
    close = data['Close'].values
    dates = data.index
    
    bull_starts = []
    bear_starts = []
    current_max = close[0]
    current_min = close[0]
    
    # 尋找熊市開始點 (從高點下跌20%)
    for i in range(1, len(close)):
        if close[i] > current_max:
            current_max = close[i]
        elif close[i] < current_max * (1 - threshold) and len(bear_starts) == 0:
            bear_starts.append((dates[i], float(close[i])))  # 使用 float() 確保是標量
        elif close[i] < current_max * (1 - threshold) and dates[i] > bear_starts[-1][0] + pd.DateOffset(months=6):
            bear_starts.append((dates[i], float(close[i])))  # 使用 float() 確保是標量
            current_max = close[i]  # 重設最高點
    
    # 尋找牛市開始點 (從低點上漲20%)
    current_min = close[0]
    for i in range(1, len(close)):
        if close[i] < current_min:
            current_min = close[i]
        elif close[i] > current_min * (1 + threshold) and len(bull_starts) == 0:
            bull_starts.append((dates[i], float(close[i])))  # 使用 float() 確保是標量
        elif close[i] > current_min * (1 + threshold) and dates[i] > bull_starts[-1][0] + pd.DateOffset(months=6):
            bull_starts.append((dates[i], float(close[i])))  # 使用 float() 確保是標量
            current_min = close[i]  # 重設最低點
    
    return bear_starts, bull_starts

bear_markets, bull_markets = detect_bear_bull_markets(sp500_data)

print("\n檢測到的熊市起點:")
for date, price in bear_markets:
    print(f"日期: {date.strftime('%Y-%m-%d')}, 指數: {price:.2f}")

print("\n檢測到的牛市起點:")
for date, price in bull_markets:
    print(f"日期: {date.strftime('%Y-%m-%d')}, 指數: {price:.2f}")

# 長期投資回報分析
long_term_periods = {
    "5年": 5,
    "10年": 10,
    "15年": 15,
    "20年": 20
}

print("\n長期投資回報分析 (假設在起始日期投資100單位):")
for period_name, years in long_term_periods.items():
    try:
        start_idx = sp500_data.index.max() - pd.DateOffset(years=years)
        if start_idx < sp500_data.index.min():
            print(f"{period_name}投資回報: 資料不足")
            continue
            
        start_price = sp500_data.loc[sp500_data.index >= start_idx, 'Close'].iloc[0].item()
        end_price = sp500_data['Close'].iloc[-1].item()
        
        total_return = (end_price / start_price - 1) * 100
        annualized_return = ((end_price / start_price) ** (1 / years) - 1) * 100
        
        print(f"{period_name}總回報率: {total_return:.2f}%, 年化: {annualized_return:.2f}%")
    except Exception as e:
        print(f"{period_name}回報率計算錯誤: {e}")

print("\n分析完成！")