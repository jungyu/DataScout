# -*- coding: utf-8 -*-
"""
完整的 LightGBM 股價預測範例：結合技術指標與情緒數據
包含完整的中文字體支援和可視化功能

這個範例示範如何使用 OHLCV 數據和模擬的新聞情緒數據，
進行特徵工程，並使用 LightGBM 模型預測次日股價漲跌。
"""

# 匯入必要的函式庫
import os
import sys
import warnings
warnings.filterwarnings('ignore')

# 添加項目根目錄到 Python 路徑
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 導入中文字體配置模組
try:
    from config.chart_fonts import ChartFontManager
    font_manager = ChartFontManager()
    font_manager.setup_matplotlib_chinese_font()
    print("已成功配置中文字體")
except ImportError:
    print("警告：無法導入字體配置模組，使用系統默認字體")
    # 手動配置中文字體
    import matplotlib
    matplotlib.rcParams['font.sans-serif'] = ['Noto Sans CJK TC', 'Heiti TC', 'PingFang HK', 'STHeiti', 'STFangsong', 'Arial Unicode MS']
    matplotlib.rcParams['axes.unicode_minus'] = False

import yfinance as yf
import pandas as pd
import numpy as np
import pandas_ta as ta
import lightgbm as lgb
from sklearn.model_selection import train_test_split, TimeSeriesSplit, GridSearchCV
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_auc_score, roc_curve
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import joblib


def main():
    """主函數，包含所有執行邏輯"""
    print("=== LightGBM 股價預測分析開始 ===\n")
    
    # 1. 獲取歷史股價數據
    ticker_symbol = "AAPL"
    start_date = "2015-01-01"
    end_date = "2025-01-01"

    print(f"正在獲取 {ticker_symbol} 從 {start_date} 到 {end_date} 的歷史數據...")
    try:
        stock_data = yf.download(ticker_symbol, start=start_date, end=end_date)
        if stock_data.empty:
            print("錯誤：無法獲取股票數據。請檢查股票代號和日期範圍。")
            return
        else:
            print("數據獲取成功！")
            print(f"數據形狀: {stock_data.shape}")
            print("\n數據前5行:")
            print(stock_data.head())
    except Exception as e:
        print(f"獲取數據時發生錯誤：{e}")
        return

    # 2. 模擬新聞事件情緒數據
    print("\n正在生成模擬情緒數據...")
    np.random.seed(42)
    stock_data['Price_Change'] = stock_data['Close'].diff()

    # 模擬情緒數據
    sentiment_base = stock_data['Price_Change'].shift(1).fillna(0) * 5
    sentiment_noise = np.random.randn(len(stock_data)) * 0.5
    simulated_sentiment = sentiment_base + sentiment_noise
    simulated_sentiment = np.tanh(simulated_sentiment)

    stock_data['Sentiment'] = simulated_sentiment
    stock_data['Sentiment'] = stock_data['Sentiment'].fillna(method='bfill')

    print("\n模擬情緒數據統計：")
    print(f"平均值: {stock_data['Sentiment'].mean():.4f}")
    print(f"標準差: {stock_data['Sentiment'].std():.4f}")
    print(f"最小值: {stock_data['Sentiment'].min():.4f}")
    print(f"最大值: {stock_data['Sentiment'].max():.4f}")

    # 3. 特徵工程
    print("\n進行特徵工程...")
    
    # 價格相關特徵
    stock_data['Close_Lag1'] = stock_data['Close'].shift(1)
    stock_data['Open_Lag1'] = stock_data['Open'].shift(1)
    stock_data['High_Lag1'] = stock_data['High'].shift(1)
    stock_data['Low_Lag1'] = stock_data['Low'].shift(1)

    # 移動平均
    stock_data['MA_5'] = stock_data['Close'].rolling(window=5).mean()
    stock_data['MA_10'] = stock_data['Close'].rolling(window=10).mean()
    stock_data['MA_20'] = stock_data['Close'].rolling(window=20).mean()

    # 波動性特徵
    stock_data['Close_Vol_5'] = stock_data['Close'].rolling(window=5).std()
    stock_data['Daily_Range'] = stock_data['High'] - stock_data['Low']
    stock_data['Daily_Range_Lag1'] = stock_data['Daily_Range'].shift(1)

    # 成交量特徵
    stock_data['Volume_Lag1'] = stock_data['Volume'].shift(1)
    stock_data['Volume_MA_5'] = stock_data['Volume'].rolling(window=5).mean()

    # 情緒特徵
    stock_data['Sentiment_Lag1'] = stock_data['Sentiment'].shift(1)
    stock_data['Sentiment_MA_5'] = stock_data['Sentiment'].rolling(window=5).mean()
    stock_data['Sentiment_Change_1d'] = stock_data['Sentiment'].diff(1)

    # 技術指標
    stock_data.ta.rsi(close='Close', length=14, append=True)
    stock_data.ta.macd(close='Close', fast=12, slow=26, signal=9, append=True)
    stock_data.ta.bbands(close='Close', length=20, std=2, append=True)
    stock_data.ta.stoch(high='High', low='Low', close='Close', k=14, d=3, append=True)
    stock_data.ta.willr(high='High', low='Low', close='Close', length=14, append=True)

    # 其他技術指標特徵
    bb_lower = stock_data.get('BBL_20_2.0', stock_data['Close'])
    bb_upper = stock_data.get('BBU_20_2.0', stock_data['Close'])
    stock_data['Price_Position_BB'] = (stock_data['Close'] - bb_lower) / (bb_upper - bb_lower)

    stock_data['Price_MA_Ratio_5'] = stock_data['Close'] / stock_data['MA_5']
    stock_data['Price_MA_Ratio_20'] = stock_data['Close'] / stock_data['MA_20']
    stock_data['Volume_Price_Trend'] = stock_data['Volume'] * stock_data['Close'].pct_change()

    # 時間特徵
    stock_data['DayOfWeek'] = stock_data.index.dayofweek
    stock_data['Month'] = stock_data.index.month
    stock_data['Quarter'] = stock_data.index.quarter
    stock_data['IsMonthEnd'] = stock_data.index.is_month_end.astype(int)
    stock_data['IsQuarterEnd'] = stock_data.index.is_quarter_end.astype(int)

    # 清理 NaN 值
    initial_rows = len(stock_data)
    stock_data.dropna(inplace=True)
    rows_after_dropna = len(stock_data)
    print(f"特徵工程後，刪除了 {initial_rows - rows_after_dropna} 行含有 NaN 的數據點。")
    print(f"剩餘數據點數量：{rows_after_dropna}")

    # 4. 定義預測目標
    stock_data['Target'] = (stock_data['Close'].shift(-1) > stock_data['Close']).astype(int)
    stock_data.dropna(inplace=True)

    print("\n目標變量分佈:")
    print(stock_data['Target'].value_counts(normalize=True))

    # 5. 準備數據集
    features = stock_data.drop(columns=['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume', 'Price_Change', 'Target'])
    target = stock_data['Target']

    print(f"\n特徵數量：{features.shape[1]}")
    print("前10個特徵名稱：", features.columns.tolist()[:10])

    # 數據分割
    split_date = "2023-01-01"
    X_train = features[stock_data.index < split_date]
    y_train = target[stock_data.index < split_date]
    X_test = features[stock_data.index >= split_date]
    y_test = target[stock_data.index >= split_date]

    print(f"\n訓練集數據點數量：{len(X_train)}")
    print(f"測試集數據點數量：{len(X_test)}")

    # 6. 訓練模型
    print("\n開始訓練 LightGBM 模型...")
    lgb_clf = lgb.LGBMClassifier(
        objective='binary',
        metric='binary_logloss',
        random_state=42,
        verbose=-1
    )
    lgb_clf.fit(X_train, y_train)
    print("模型訓練完成。")

    # 7. 評估模型
    print("\n正在評估模型性能...")
    y_pred = lgb_clf.predict(X_test)
    y_pred_proba = lgb_clf.predict_proba(X_test)[:, 1]

    accuracy = accuracy_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_pred_proba)

    print(f"測試集準確率: {accuracy:.4f}")
    print(f"ROC AUC 分數: {roc_auc:.4f}")
    print("\n分類報告：")
    print(classification_report(y_test, y_pred))

    # 8. 特徵重要性
    feature_importance = pd.DataFrame({
        'feature': features.columns,
        'importance': lgb_clf.feature_importances_
    }).sort_values(by='importance', ascending=False)

    print("\n前10個最重要的特徵：")
    print(feature_importance.head(10))

    # 9. 可視化結果
    print("\n正在生成可視化圖表...")
    create_visualizations(y_test, y_pred, y_pred_proba, feature_importance, stock_data, split_date)

    # 10. 超參數優化
    print("\n=== 超參數優化 ===")
    best_model = perform_hyperparameter_tuning(X_train, y_train, X_test, y_test)

    # 11. 回測分析
    print("\n=== 回測分析 ===")
    perform_backtest_analysis(stock_data, best_model, X_test, split_date)

    # 12. 模型保存
    print("\n=== 保存模型 ===")
    save_model_and_results(best_model, features.columns.tolist())

    print("\n=== 分析完成 ===")
    print("所有輸出文件已保存至 /Users/aaron/Projects/DataScout/data/output/")
    print("模型文件已保存至 /Users/aaron/Projects/DataScout/data/models/")
    print("\n注意: 此模型僅供學習和研究用途，不構成投資建議。實際投資需謹慎考慮風險。")


def create_visualizations(y_test, y_pred, y_pred_proba, feature_importance, stock_data, split_date):
    """創建所有可視化圖表"""
    # 確保輸出目錄存在
    os.makedirs('/Users/aaron/Projects/DataScout/data/output', exist_ok=True)
    
    # 1. 混淆矩陣
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['跌', '漲'], yticklabels=['跌', '漲'])
    plt.title('混淆矩陣', fontsize=16, fontweight='bold')
    plt.xlabel('預測值', fontsize=14)
    plt.ylabel('實際值', fontsize=14)
    plt.tight_layout()
    plt.savefig('/Users/aaron/Projects/DataScout/data/output/confusion_matrix.png', 
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.show()

    # 2. ROC 曲線
    from sklearn.metrics import roc_curve
    fpr, tpr, thresholds = roc_curve(y_test, y_pred_proba)
    roc_auc = roc_auc_score(y_test, y_pred_proba)
    
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, linewidth=2, label=f'ROC 曲線 (AUC = {roc_auc:.4f})')
    plt.plot([0, 1], [0, 1], 'k--', alpha=0.6, label='隨機預測')
    plt.xlabel('偽陽性率 (False Positive Rate)', fontsize=12)
    plt.ylabel('真陽性率 (True Positive Rate)', fontsize=12)
    plt.title('ROC 曲線', fontsize=16, fontweight='bold')
    plt.legend(fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('/Users/aaron/Projects/DataScout/data/output/roc_curve.png', 
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.show()

    # 3. 特徵重要性圖
    plt.figure(figsize=(12, 8))
    top_features = feature_importance.head(15)
    bars = plt.barh(range(len(top_features)), top_features['importance'])
    plt.yticks(range(len(top_features)), top_features['feature'])
    plt.xlabel('重要性分數', fontsize=14)
    plt.title('前15個最重要的特徵', fontsize=16, fontweight='bold')
    plt.gca().invert_yaxis()
    
    # 添加數值標籤
    for i, bar in enumerate(bars):
        width = bar.get_width()
        plt.text(width, bar.get_y() + bar.get_height()/2, 
                f'{width:.3f}', ha='left', va='center', fontsize=10)
    
    plt.tight_layout()
    plt.savefig('/Users/aaron/Projects/DataScout/data/output/feature_importance.png', 
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.show()


def perform_hyperparameter_tuning(X_train, y_train, X_test, y_test):
    """執行超參數優化"""
    param_grid = {
        'n_estimators': [100, 200, 300],
        'learning_rate': [0.05, 0.1, 0.15],
        'max_depth': [3, 5, 7],
        'num_leaves': [31, 50, 70]
    }

    # 使用較小的樣本進行網格搜索
    sample_size = min(1000, len(X_train))
    X_sample = X_train.sample(n=sample_size, random_state=42)
    y_sample = y_train.loc[X_sample.index]

    grid_search = GridSearchCV(
        lgb.LGBMClassifier(objective='binary', random_state=42, verbose=-1),
        param_grid,
        cv=3,
        scoring='accuracy',
        n_jobs=-1,
        verbose=0
    )

    print("開始超參數優化...")
    grid_search.fit(X_sample, y_sample)

    print(f"最佳參數: {grid_search.best_params_}")
    print(f"最佳交叉驗證分數: {grid_search.best_score_:.4f}")

    # 使用最佳參數重新訓練
    best_model = grid_search.best_estimator_
    best_model.fit(X_train, y_train)

    # 評估優化後的模型
    best_y_pred = best_model.predict(X_test)
    best_accuracy = accuracy_score(y_test, best_y_pred)
    print(f"優化後模型測試集準確率: {best_accuracy:.4f}")

    return best_model


def perform_backtest_analysis(stock_data, best_model, X_test, split_date):
    """執行回測分析"""
    test_data = stock_data[stock_data.index >= split_date].copy()
    test_data['Predicted'] = best_model.predict(X_test)
    test_data['Predicted_Proba'] = best_model.predict_proba(X_test)[:, 1]

    # 計算策略收益
    test_data['Daily_Return'] = test_data['Close'].pct_change()
    test_data['Strategy_Return'] = test_data['Predicted'] * test_data['Daily_Return'].shift(-1)
    test_data['Cumulative_Return'] = (1 + test_data['Daily_Return']).cumprod()
    test_data['Cumulative_Strategy_Return'] = (1 + test_data['Strategy_Return'].fillna(0)).cumprod()

    # 計算績效指標
    total_return = test_data['Cumulative_Return'].iloc[-1] - 1
    strategy_return = test_data['Cumulative_Strategy_Return'].iloc[-1] - 1
    
    strategy_returns = test_data['Strategy_Return'].fillna(0)
    if strategy_returns.std() > 0:
        sharpe_ratio = strategy_returns.mean() / strategy_returns.std() * np.sqrt(252)
    else:
        sharpe_ratio = 0

    print(f"\n回測結果 ({split_date} 至今):")
    print(f"買入持有策略總收益: {total_return:.4f} ({total_return*100:.2f}%)")
    print(f"預測策略總收益: {strategy_return:.4f} ({strategy_return*100:.2f}%)")
    print(f"策略年化夏普比率: {sharpe_ratio:.4f}")

    # 繪製累積收益曲線
    plt.figure(figsize=(12, 6))
    plt.plot(test_data.index, test_data['Cumulative_Return'], 
             label='買入持有策略', linewidth=2, color='blue')
    plt.plot(test_data.index, test_data['Cumulative_Strategy_Return'], 
             label='預測策略', linewidth=2, color='red')
    plt.xlabel('日期', fontsize=14)
    plt.ylabel('累積收益', fontsize=14)
    plt.title('策略回測結果', fontsize=16, fontweight='bold')
    plt.legend(fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('/Users/aaron/Projects/DataScout/data/output/backtest_results.png', 
                dpi=300, bbox_inches='tight', facecolor='white')
    plt.show()

    # 保存回測結果
    backtest_path = '/Users/aaron/Projects/DataScout/data/output/backtest_results.csv'
    test_data[['Close', 'Predicted', 'Predicted_Proba', 'Daily_Return', 'Strategy_Return', 
              'Cumulative_Return', 'Cumulative_Strategy_Return']].to_csv(backtest_path)
    print(f"回測結果已保存至: {backtest_path}")


def save_model_and_results(best_model, feature_names):
    """保存模型和相關文件"""
    # 創建模型目錄
    os.makedirs('/Users/aaron/Projects/DataScout/data/models', exist_ok=True)

    # 保存模型
    model_path = '/Users/aaron/Projects/DataScout/data/models/lightgbm_stock_predictor.pkl'
    joblib.dump(best_model, model_path)
    print(f"模型已保存至: {model_path}")

    # 保存特徵列表
    feature_path = '/Users/aaron/Projects/DataScout/data/models/feature_names.pkl'
    joblib.dump(feature_names, feature_path)
    print(f"特徵列表已保存至: {feature_path}")


if __name__ == "__main__":
    main()

# 計算隨機指標 (Stochastic Oscillator)
stock_data.ta.stoch(high='High', low='Low', close='Close', k=14, d=3, append=True) # 會新增 'STOCHk_14_3_3', 'STOCHd_14_3_3'

# 計算威廉指標 (Williams %R)
stock_data.ta.willr(high='High', low='Low', close='Close', length=14, append=True) # 會新增 'WILLR_14'

# 價格相對位置特徵
stock_data['Price_Position_BB'] = (stock_data['Close'] - stock_data.get('BBL_20_2.0', stock_data['Close'])) / \
                                 (stock_data.get('BBU_20_2.0', stock_data['Close']) - stock_data.get('BBL_20_2.0', stock_data['Close']))

# 其他技術指標特徵
stock_data['Price_MA_Ratio_5'] = stock_data['Close'] / stock_data['MA_5']  # 價格與5日均線比值
stock_data['Price_MA_Ratio_20'] = stock_data['Close'] / stock_data['MA_20']  # 價格與20日均線比值
stock_data['Volume_Price_Trend'] = stock_data['Volume'] * (stock_data['Close'].pct_change())  # 成交量價格趨勢

# 時間特徵
stock_data['DayOfWeek'] = stock_data.index.dayofweek  # 星期幾 (0=Monday, 6=Sunday)
stock_data['Month'] = stock_data.index.month  # 月份
stock_data['Quarter'] = stock_data.index.quarter  # 季度
stock_data['IsMonthEnd'] = stock_data.index.is_month_end.astype(int)  # 是否月末
stock_data['IsQuarterEnd'] = stock_data.index.is_quarter_end.astype(int)  # 是否季末

# 清理因計算特徵而產生的 NaN 值
# 簡單起見，這裡直接刪除包含 NaN 的行。這會移除開頭的數據點 (取決於最長的 rolling window 或 lag)。
initial_rows = len(stock_data)
stock_data.dropna(inplace=True)
rows_after_dropna = len(stock_data)
print(f"\n特徵工程後，刪除了 {initial_rows - rows_after_dropna} 行含有 NaN 的數據點。")
print(f"剩餘數據點數量：{rows_after_dropna}")


# 5. 定義預測目標
# 預測明日的股價趨勢 (漲或跌)
# 如果明日收盤價 > 今日收盤價，目標為 1 (漲)
# 否則目標為 0 (跌)
# 使用 shift(-1) 來獲取下一日的收盤價
stock_data['Target'] = (stock_data['Close'].shift(-1) > stock_data['Close']).astype(int)

# 再次清理因 Target 欄位 shift(-1) 產生的最後一行的 NaN
stock_data.dropna(inplace=True)

print("\n數據集包含特徵和目標：")
print(stock_data[['Close', 'Sentiment', 'MA_5', 'RSI_14', 'MACD_12_26_9', 'Sentiment_MA_5', 'Target']].head())
print(stock_data[['Close', 'Sentiment', 'MA_5', 'RSI_14', 'MACD_12_26_9', 'Sentiment_MA_5', 'Target']].tail())


# 6. 準備數據集用於模型訓練
# 特徵 (X) 和目標 (y)
# 排除原始價格、Volume、Price_Change 和 Target 本身作為特徵
features = stock_data.drop(columns=['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume', 'Price_Change', 'Target'])
target = stock_data['Target']

print(f"\n特徵數量：{features.shape[1]}")
print("特徵名稱：", features.columns.tolist())

# 將數據集按時間順序分成訓練集和測試集
# 常用方法是設定一個分割日期
split_date = "2023-01-01" # 例如，用 2023 年之前的數據訓練，之後的數據測試

X_train = features[stock_data.index < split_date]
y_train = target[stock_data.index < split_date]
X_test = features[stock_data.index >= split_date]
y_test = target[stock_data.index >= split_date]

print(f"\n訓練集數據點數量：{len(X_train)}")
print(f"測試集數據點數量：{len(X_test)}")
print(f"訓練集漲跌比例 (1:漲, 0:跌):\n{y_train.value_counts(normalize=True)}")


# 7. 訓練 LightGBM 模型
# 使用 LightGBM 分類器預測漲跌 (二元分類)
lgb_clf = lgb.LGBMClassifier(objective='binary', metric='binary_logloss', random_state=42)

print("\n開始訓練 LightGBM 模型...")
lgb_clf.fit(X_train, y_train)
print("模型訓練完成。")

# 8. 評估模型性能
print("\n正在測試集上評估模型性能...")
y_pred = lgb_clf.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
print(f"測試集準確率 (Accuracy): {accuracy:.4f}")

# 查看更詳細的分類報告
print("\n分類報告：")
print(classification_report(y_test, y_pred))

# 9. 查看特徵重要性 (模型可解釋性的一部分)
print("\n特徵重要性 (Feature Importance):")
# LightGBM 提供了兩種特徵重要性：split (按特徵被用於分裂的次數) 和 gain (按特徵分裂帶來的平均增益)
# 這裡使用 'gain'，通常更能反映特徵的預測能力
feature_importance = pd.DataFrame({
    'feature': features.columns,
    'importance': lgb_clf.feature_importances_
}).sort_values(by='importance', ascending=False)

print(feature_importance)

# 可以將特徵重要性繪製出來
# plt.figure(figsize=(10, 6))
# lgb.plot_importance(lgb_clf, importance_type='gain', max_num_features=20, figsize=(10, 6), title='LightGBM Feature Importance (Gain)')
# plt.show()


# 10. 範例預測 (使用測試集中的幾行數據來示範預測結果)
print("\n使用測試集中的前 5 行數據進行預測示範：")
sample_for_prediction = X_test.head(5)
sample_true_target = y_test.head(5).tolist()
sample_predictions = lgb_clf.predict(sample_for_prediction)
sample_probabilities = lgb_clf.predict_proba(sample_for_prediction)[:, 1] # 預測為 1 (漲) 的概率

for i in range(len(sample_for_prediction)):
    date = sample_for_prediction.index[i].strftime('%Y-%m-%d')
    print(f"日期: {date}, 實際次日趨勢 (1=漲, 0=跌): {sample_true_target[i]}, 模型預測趨勢: {sample_predictions[i]}, 預測漲的概率: {sample_probabilities[i]:.4f}")


# 11. 進階模型評估與視覺化
print("\n=== 進階模型評估 ===")

# 混淆矩陣
cm = confusion_matrix(y_test, y_pred)
print(f"\n混淆矩陣:")
print(cm)

# 計算 ROC AUC 分數
y_pred_proba = lgb_clf.predict_proba(X_test)[:, 1]
roc_auc = roc_auc_score(y_test, y_pred_proba)
print(f"\nROC AUC 分數: {roc_auc:.4f}")

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


# 12. 時間序列交叉驗證
print("\n=== 時間序列交叉驗證 ===")

# 使用時間序列分割進行交叉驗證
tscv = TimeSeriesSplit(n_splits=5)
cv_scores = []

for train_idx, val_idx in tscv.split(X_train):
    X_cv_train, X_cv_val = X_train.iloc[train_idx], X_train.iloc[val_idx]
    y_cv_train, y_cv_val = y_train.iloc[train_idx], y_train.iloc[val_idx]
    
    # 訓練模型
    cv_model = lgb.LGBMClassifier(objective='binary', metric='binary_logloss', random_state=42, verbose=-1)
    cv_model.fit(X_cv_train, y_cv_train)
    
    # 預測並計算準確率
    cv_pred = cv_model.predict(X_cv_val)
    cv_score = accuracy_score(y_cv_val, cv_pred)
    cv_scores.append(cv_score)

print(f"交叉驗證準確率: {cv_scores}")
print(f"平均交叉驗證準確率: {np.mean(cv_scores):.4f} (+/- {np.std(cv_scores) * 2:.4f})")


# 13. 超參數優化
print("\n=== 超參數優化 ===")

# 簡單的網格搜索
from sklearn.model_selection import GridSearchCV

param_grid = {
    'n_estimators': [100, 200, 300],
    'learning_rate': [0.05, 0.1, 0.15],
    'max_depth': [3, 5, 7],
    'num_leaves': [31, 50, 70]
}

# 由於計算量較大，我們使用較小的數據集進行網格搜索
sample_size = min(1000, len(X_train))
X_sample = X_train.sample(n=sample_size, random_state=42)
y_sample = y_train.loc[X_sample.index]

grid_search = GridSearchCV(
    lgb.LGBMClassifier(objective='binary', random_state=42, verbose=-1),
    param_grid,
    cv=3,
    scoring='accuracy',
    n_jobs=-1,
    verbose=1
)

print("開始超參數優化...")
grid_search.fit(X_sample, y_sample)

print(f"最佳參數: {grid_search.best_params_}")
print(f"最佳交叉驗證分數: {grid_search.best_score_:.4f}")

# 使用最佳參數重新訓練模型
best_model = grid_search.best_estimator_
best_model.fit(X_train, y_train)

# 評估優化後的模型
best_y_pred = best_model.predict(X_test)
best_accuracy = accuracy_score(y_test, best_y_pred)
print(f"優化後模型測試集準確率: {best_accuracy:.4f}")


# 14. 模型保存與回測分析
print("\n=== 模型保存與回測分析 ===")

# 創建輸出目錄
os.makedirs('/Users/aaron/Projects/DataScout/data/output', exist_ok=True)
os.makedirs('/Users/aaron/Projects/DataScout/data/models', exist_ok=True)

# 保存最佳模型
model_path = '/Users/aaron/Projects/DataScout/data/models/lightgbm_stock_predictor.pkl'
joblib.dump(best_model, model_path)
print(f"模型已保存至: {model_path}")

# 保存特徵列表
feature_path = '/Users/aaron/Projects/DataScout/data/models/feature_names.pkl'
joblib.dump(features.columns.tolist(), feature_path)
print(f"特徵列表已保存至: {feature_path}")

# 回測分析
print("\n進行回測分析...")
test_data = stock_data[stock_data.index >= split_date].copy()
test_data['Predicted'] = best_model.predict(X_test)
test_data['Predicted_Proba'] = best_model.predict_proba(X_test)[:, 1]

# 計算策略收益
test_data['Daily_Return'] = test_data['Close'].pct_change()
test_data['Strategy_Return'] = test_data['Predicted'] * test_data['Daily_Return'].shift(-1)
test_data['Cumulative_Return'] = (1 + test_data['Daily_Return']).cumprod()
test_data['Cumulative_Strategy_Return'] = (1 + test_data['Strategy_Return'].fillna(0)).cumprod()

# 計算績效指標
total_return = test_data['Cumulative_Return'].iloc[-1] - 1
strategy_return = test_data['Cumulative_Strategy_Return'].iloc[-1] - 1
sharpe_ratio = test_data['Strategy_Return'].mean() / test_data['Strategy_Return'].std() * np.sqrt(252)

print(f"\n回測結果 ({split_date} 至今):")
print(f"買入持有策略總收益: {total_return:.4f} ({total_return*100:.2f}%)")
print(f"預測策略總收益: {strategy_return:.4f} ({strategy_return*100:.2f}%)")
print(f"策略年化夏普比率: {sharpe_ratio:.4f}")

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


# 15. 預測未來趨勢
print("\n=== 預測未來趨勢 ===")

# 使用最新數據預測未來趨勢
latest_features = features.iloc[-1:].copy()
future_prediction = best_model.predict(latest_features)[0]
future_probability = best_model.predict_proba(latest_features)[0, 1]

print(f"基於最新數據的預測:")
print(f"預測明日趨勢: {'上漲' if future_prediction == 1 else '下跌'}")
print(f"上漲概率: {future_probability:.4f}")
print(f"下跌概率: {1-future_probability:.4f}")

# 信心區間分析
if future_probability > 0.6:
    confidence = "高"
elif future_probability > 0.4:
    confidence = "中"
else:
    confidence = "低"

print(f"預測信心度: {confidence}")

print("\n=== 分析完成 ===")
print(f"所有輸出文件已保存至 /Users/aaron/Projects/DataScout/data/output/")
print(f"模型文件已保存至 /Users/aaron/Projects/DataScout/data/models/")
print("\n注意: 此模型僅供學習和研究用途，不構成投資建議。實際投資需謹慎考慮風險。")


if __name__ == "__main__":
    # 當直接運行此腳本時才執行
    main()