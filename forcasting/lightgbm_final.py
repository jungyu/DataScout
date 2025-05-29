# -*- coding: utf-8 -*-
"""
Google Colab 範例：結合股價技術指標與模擬新聞情緒預測股價趨勢 (LightGBM)

這個範例示範如何在 Google Colab 環境中，使用有限的 OHLCV 數據和模擬的新聞情緒數據，
進行適度的特徵工程，並使用 LightGBM 模型預測次日股價漲跌，同時查看特徵重要性。
"""

# 1. 安裝所需函式庫
# 在 Colab 環境中執行此命令
# !pip install yfinance pandas_ta lightgbm numpy pandas scikit-learn

# 匯入所需函式庫
import os
import sys
import warnings
warnings.filterwarnings('ignore')  # 忽略警告信息

# 添加項目根目錄到 Python 路徑
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 確保當前工作目錄是項目根目錄
os.chdir(project_root)

# 導入中文字體配置模組
try:
    from config.chart_fonts import setup_chinese_fonts
    font_config_available = True
    print(f"成功導入字體配置模組 (項目根目錄: {project_root})")
except ImportError as e:
    print(f"警告：無法導入字體配置模組 (錯誤: {e})，將使用預設字體設定")
    font_config_available = False

import yfinance as yf
import pandas as pd
import numpy as np
import pandas_ta as ta  # 用於技術指標計算
import lightgbm as lgb
from sklearn.model_selection import train_test_split, TimeSeriesSplit, GridSearchCV
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_auc_score, roc_curve
import matplotlib.pyplot as plt  # 用於繪圖，支援中文字體
import seaborn as sns
from datetime import datetime, timedelta
import joblib  # 用於模型保存和加載

# 設定中文字體支援
if font_config_available:
    print("正在配置中文字體...")
    font_manager = setup_chinese_fonts()
    print("中文字體配置完成！")
else:
    # 使用基本的中文字體配置
    print("使用預設中文字體配置...")
    plt.rcParams['font.family'] = ['Heiti TC', 'STHeiti', 'Apple LiGothic', 'Hei', 'Kai']
    plt.rcParams['axes.unicode_minus'] = False
    print("預設中文字體配置完成！")


def main():
    """主函數，包含所有執行邏輯"""
    
    # 2. 獲取歷史股價數據 (AAPL)
    # 獲取最近約 10 年的 AAPL 每日數據
    # 您可以調整 start 和 end 日期
    ticker_symbol = "AAPL"
    start_date = "2015-01-01"
    end_date = "2025-01-01"  # 或 pd.Timestamp.today().strftime('%Y-%m-%d') 獲取最新數據
    
    print(f"正在獲取 {ticker_symbol} 從 {start_date} 到 {end_date} 的歷史數據...")
    try:
        stock_data_raw = yf.download(ticker_symbol, start=start_date, end=end_date)
        if stock_data_raw.empty:
            print("錯誤：無法獲取股票數據。請檢查股票代號和日期範圍。")
        else:
            print("數據獲取成功！")
            
            # 處理多級索引，將其扁平化
            if isinstance(stock_data_raw.columns, pd.MultiIndex):
                # 如果是多級索引，取第一級（價格類型）
                stock_data = pd.DataFrame()
                for price_type in ['Open', 'High', 'Low', 'Close', 'Volume']:
                    if (price_type, ticker_symbol) in stock_data_raw.columns:
                        stock_data[price_type] = stock_data_raw[(price_type, ticker_symbol)]
                print("多級索引數據已扁平化")
            else:
                stock_data = stock_data_raw.copy()
            
            print("處理後的數據樣本：")
            print(stock_data.head())
            print(stock_data.tail())
            
    except Exception as e:
        print(f"獲取數據時發生錯誤：{e}")
        stock_data = pd.DataFrame()  # 創建空DataFrame防止後續錯誤

    if stock_data.empty:
        # 如果數據獲取失敗，停止執行
        raise SystemExit("因無法獲取數據，範例終止。")

    # 3. 模擬新聞事件情緒數據
    # 這是為了示範如何包含外部情緒數據。
    # 實際應用中，這部分需要通過爬蟲、自然語言處理(NLP)等方法從新聞中提取並量化情緒。
    # 簡單模擬：讓情緒與前一日的價格漲跌有點關聯，並加入隨機噪音
    np.random.seed(42)  # 設定隨機種子以確保結果可重現
    stock_data['Price_Change'] = stock_data['Close'].diff()
    
    # 模擬一個在 -1 到 1 之間的情緒分數
    # 情緒與前一日漲跌正相關，並疊加噪音
    sentiment_base = stock_data['Price_Change'].shift(1).fillna(0) * 5  # 放大一點影響
    sentiment_noise = np.random.randn(len(stock_data)) * 0.5  # 加入噪音
    simulated_sentiment = sentiment_base + sentiment_noise
    
    # 將模擬情緒縮放到 -1 到 1 的範圍
    simulated_sentiment = np.tanh(simulated_sentiment)  # 使用 tanh 函數縮放
    stock_data['Sentiment'] = simulated_sentiment
    stock_data['Sentiment'] = stock_data['Sentiment'].fillna(method='bfill')  # 填充最前面的 NaN
    
    print("\n模擬情緒數據的一部分：")
    print(stock_data[['Close', 'Price_Change', 'Sentiment']].head())
    print(stock_data[['Close', 'Price_Change', 'Sentiment']].tail())
    
    # 檢查情緒數據分佈
    print(f"\n情緒數據統計：")
    print(f"平均值: {stock_data['Sentiment'].mean():.4f}")
    print(f"標準差: {stock_data['Sentiment'].std():.4f}")
    print(f"最小值: {stock_data['Sentiment'].min():.4f}")
    print(f"最大值: {stock_data['Sentiment'].max():.4f}")

    # 4. 進行適度的特徵工程
    # 從 OHLCV、Volume 和 Sentiment 創建預測所需的特徵
    # 這裡創建一些常用的時序和技術指標特徵
    
    # 價格相關特徵 (滯後值, 移動平均)
    stock_data['Close_Lag1'] = stock_data['Close'].shift(1)
    stock_data['Open_Lag1'] = stock_data['Open'].shift(1)
    stock_data['High_Lag1'] = stock_data['High'].shift(1)
    stock_data['Low_Lag1'] = stock_data['Low'].shift(1)
    stock_data['MA_5'] = stock_data['Close'].rolling(window=5).mean()  # 5日移動平均
    stock_data['MA_10'] = stock_data['Close'].rolling(window=10).mean()  # 10日移動平均
    stock_data['MA_20'] = stock_data['Close'].rolling(window=20).mean()  # 20日移動平均
    
    # 波動性特徵
    stock_data['Close_Vol_5'] = stock_data['Close'].rolling(window=5).std()  # 5日收盤價標準差
    stock_data['Daily_Range'] = stock_data['High'] - stock_data['Low']  # 每日幅度
    stock_data['Daily_Range_Lag1'] = stock_data['Daily_Range'].shift(1)
    
    # 成交量相關特徵
    stock_data['Volume_Lag1'] = stock_data['Volume'].shift(1)
    stock_data['Volume_MA_5'] = stock_data['Volume'].rolling(window=5).mean()  # 5日成交量移動平均
    
    # 情緒相關特徵
    stock_data['Sentiment_Lag1'] = stock_data['Sentiment'].shift(1)
    stock_data['Sentiment_MA_5'] = stock_data['Sentiment'].rolling(window=5).mean()  # 5日情緒移動平均
    stock_data['Sentiment_Change_1d'] = stock_data['Sentiment'].diff(1)  # 每日情緒變化
    
    # 技術指標 (使用 pandas_ta 函式庫)
    # 為了避免複雜性，這裡手動計算一些基本技術指標
    
    # 計算 RSI (相對強弱指數) - 手動實現
    def calculate_rsi(close_prices, window=14):
        delta = close_prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    stock_data['RSI_14'] = calculate_rsi(stock_data['Close'])
    
    # 計算 MACD (移動平均聚散異同)
    exp1 = stock_data['Close'].ewm(span=12).mean()
    exp2 = stock_data['Close'].ewm(span=26).mean()
    stock_data['MACD_12_26_9'] = exp1 - exp2
    stock_data['MACD_Signal'] = stock_data['MACD_12_26_9'].ewm(span=9).mean()
    stock_data['MACD_Histogram'] = stock_data['MACD_12_26_9'] - stock_data['MACD_Signal']
    
    # 計算布林帶 (Bollinger Bands)
    stock_data['BB_Middle'] = stock_data['Close'].rolling(window=20).mean()
    bb_std = stock_data['Close'].rolling(window=20).std()
    stock_data['BB_Upper'] = stock_data['BB_Middle'] + (bb_std * 2)
    stock_data['BB_Lower'] = stock_data['BB_Middle'] - (bb_std * 2)
    
    # 價格相對位置特徵
    stock_data['Price_Position_BB'] = (stock_data['Close'] - stock_data['BB_Lower']) / (stock_data['BB_Upper'] - stock_data['BB_Lower'])
    
    # 其他技術指標特徵
    stock_data['Price_MA_Ratio_5'] = stock_data['Close'] / stock_data['MA_5']  # 價格與5日均線比值
    stock_data['Price_MA_Ratio_20'] = stock_data['Close'] / stock_data['MA_20']  # 價格與20日均線比值
    stock_data['Volume_Price_Trend'] = stock_data['Volume'] * stock_data['Close'].pct_change()  # 成交量價格趨勢
    
    # 時間特徵
    stock_data['DayOfWeek'] = stock_data.index.dayofweek  # 星期幾 (0=Monday, 6=Sunday)
    stock_data['Month'] = stock_data.index.month  # 月份
    stock_data['Quarter'] = stock_data.index.quarter  # 季度
    stock_data['IsMonthEnd'] = stock_data.index.is_month_end.astype(int)  # 是否月末
    stock_data['IsQuarterEnd'] = stock_data.index.is_quarter_end.astype(int)  # 是否季末
    
    # 清理因計算特徵而產生的 NaN 值
    initial_rows = len(stock_data)
    stock_data.dropna(inplace=True)
    rows_after_dropna = len(stock_data)
    print(f"\n特徵工程後，刪除了 {initial_rows - rows_after_dropna} 行含有 NaN 的數據點。")
    print(f"剩餘數據點數量：{rows_after_dropna}")

    # 5. 定義預測目標
    stock_data['Target'] = (stock_data['Close'].shift(-1) > stock_data['Close']).astype(int)
    stock_data.dropna(inplace=True)
    
    print("\n數據集包含特徵和目標：")
    print(stock_data[['Close', 'Sentiment', 'MA_5', 'RSI_14', 'MACD_12_26_9', 'Sentiment_MA_5', 'Target']].head())

    # 6. 準備數據集用於模型訓練
    feature_columns = [col for col in stock_data.columns if col not in ['Open', 'High', 'Low', 'Close', 'Volume', 'Price_Change', 'Target']]
    features = stock_data[feature_columns]
    target = stock_data['Target']
    
    print(f"\n特徵數量：{features.shape[1]}")
    print(f"特徵列表：{list(features.columns)}")
    
    # 將數據集按時間順序分成訓練集和測試集
    split_date = "2023-01-01"
    X_train = features[stock_data.index < split_date]
    y_train = target[stock_data.index < split_date]
    X_test = features[stock_data.index >= split_date]
    y_test = target[stock_data.index >= split_date]
    
    print(f"\n訓練集數據點數量：{len(X_train)}")
    print(f"測試集數據點數量：{len(X_test)}")

    if len(X_test) == 0:
        print("警告：測試集為空，調整分割日期...")
        split_date = "2022-01-01"
        X_train = features[stock_data.index < split_date]
        y_train = target[stock_data.index < split_date]
        X_test = features[stock_data.index >= split_date]
        y_test = target[stock_data.index >= split_date]
        print(f"調整後 - 訓練集數據點數量：{len(X_train)}")
        print(f"調整後 - 測試集數據點數量：{len(X_test)}")

    # 7. 訓練 LightGBM 模型
    lgb_clf = lgb.LGBMClassifier(objective='binary', metric='binary_logloss', random_state=42, verbose=-1)
    print("\n開始訓練 LightGBM 模型...")
    lgb_clf.fit(X_train, y_train)
    print("模型訓練完成。")

    # 8. 評估模型性能
    print("\n正在測試集上評估模型性能...")
    y_pred = lgb_clf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"測試集準確率 (Accuracy): {accuracy:.4f}")

    # 9. 查看特徵重要性
    print("\n特徵重要性 (Feature Importance):")
    feature_importance = pd.DataFrame({
        'feature': features.columns,
        'importance': lgb_clf.feature_importances_
    }).sort_values(by='importance', ascending=False)
    print(feature_importance.head(10))

    # 10. 進階模型評估與視覺化
    print("\n=== 進階模型評估 ===")
    
    # 混淆矩陣
    cm = confusion_matrix(y_test, y_pred)
    print(f"\n混淆矩陣:")
    print(cm)
    
    # 計算 ROC AUC 分數
    y_pred_proba = lgb_clf.predict_proba(X_test)[:, 1]
    roc_auc = roc_auc_score(y_test, y_pred_proba)
    print(f"\nROC AUC 分數: {roc_auc:.4f}")
    
    # 創建輸出目錄
    os.makedirs('/Users/aaron/Projects/DataScout/data/output', exist_ok=True)
    
    # 繪製混淆矩陣熱圖
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=['跌', '漲'], yticklabels=['跌', '漲'])
    plt.title('混淆矩陣')
    plt.xlabel('預測值')
    plt.ylabel('實際值')
    plt.tight_layout()
    plt.savefig('/Users/aaron/Projects/DataScout/data/output/confusion_matrix.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # 繪製 ROC 曲線
    fpr, tpr, thresholds = roc_curve(y_test, y_pred_proba)
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, label=f'ROC Curve (AUC = {roc_auc:.4f})')
    plt.plot([0, 1], [0, 1], 'k--', label='Random')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC 曲線')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('/Users/aaron/Projects/DataScout/data/output/roc_curve.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # 繪製特徵重要性圖
    plt.figure(figsize=(12, 8))
    top_features = feature_importance.head(15)  # 顯示前15個重要特徵
    plt.barh(range(len(top_features)), top_features['importance'])
    plt.yticks(range(len(top_features)), top_features['feature'])
    plt.xlabel('重要性分數')
    plt.title('前15個最重要的特徵')
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig('/Users/aaron/Projects/DataScout/data/output/feature_importance.png', dpi=300, bbox_inches='tight')
    plt.show()

    # 11. 模型保存與回測分析
    print("\n=== 模型保存與回測分析 ===")
    
    # 創建模型目錄
    os.makedirs('/Users/aaron/Projects/DataScout/data/models', exist_ok=True)
    
    # 保存模型
    model_path = '/Users/aaron/Projects/DataScout/data/models/lightgbm_stock_predictor.pkl'
    joblib.dump(lgb_clf, model_path)
    print(f"模型已保存至: {model_path}")
    
    # 保存特徵列表
    feature_path = '/Users/aaron/Projects/DataScout/data/models/feature_names.pkl'
    joblib.dump(features.columns.tolist(), feature_path)
    print(f"特徵列表已保存至: {feature_path}")
    
    # 回測分析
    print("\n進行回測分析...")
    test_data = stock_data[stock_data.index >= split_date].copy()
    test_data['Predicted'] = lgb_clf.predict(X_test)
    test_data['Predicted_Proba'] = lgb_clf.predict_proba(X_test)[:, 1]
    
    # 計算策略收益
    test_data['Daily_Return'] = test_data['Close'].pct_change()
    test_data['Strategy_Return'] = test_data['Predicted'] * test_data['Daily_Return'].shift(-1)
    test_data['Cumulative_Return'] = (1 + test_data['Daily_Return']).cumprod()
    test_data['Cumulative_Strategy_Return'] = (1 + test_data['Strategy_Return'].fillna(0)).cumprod()
    
    # 計算績效指標
    total_return = test_data['Cumulative_Return'].iloc[-1] - 1
    strategy_return = test_data['Cumulative_Strategy_Return'].iloc[-1] - 1
    
    print(f"\n回測結果 ({split_date} 至今):")
    print(f"買入持有策略總收益: {total_return:.4f} ({total_return*100:.2f}%)")
    print(f"預測策略總收益: {strategy_return:.4f} ({strategy_return*100:.2f}%)")
    
    # 繪製累積收益曲線
    plt.figure(figsize=(12, 6))
    plt.plot(test_data.index, test_data['Cumulative_Return'], label='買入持有策略', linewidth=2)
    plt.plot(test_data.index, test_data['Cumulative_Strategy_Return'], label='預測策略', linewidth=2)
    plt.xlabel('日期')
    plt.ylabel('累積收益')
    plt.title('策略回測結果')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('/Users/aaron/Projects/DataScout/data/output/backtest_results.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # 保存回測結果
    backtest_path = '/Users/aaron/Projects/DataScout/data/output/backtest_results.csv'
    test_data[['Close', 'Predicted', 'Predicted_Proba', 'Daily_Return', 'Strategy_Return',
               'Cumulative_Return', 'Cumulative_Strategy_Return']].to_csv(backtest_path)
    print(f"回測結果已保存至: {backtest_path}")
    
    print("\n=== 分析完成 ===")
    print(f"所有輸出文件已保存至 /Users/aaron/Projects/DataScout/data/output/")
    print(f"模型文件已保存至 /Users/aaron/Projects/DataScout/data/models/")
    print("\n注意: 此模型僅供學習和研究用途，不構成投資建議。實際投資需謹慎考慮風險。")


if __name__ == "__main__":
    # 當直接運行此腳本時才執行
    main()
