"""
股票價格預測模組 - LightGBM 實現
只包含函數和類定義，不包含執行代碼
"""

import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import yfinance as yf
import lightgbm as lgb
from sklearn.model_selection import train_test_split, TimeSeriesSplit, RandomizedSearchCV
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, classification_report, confusion_matrix, roc_curve
import joblib
import pandas_ta
import os


def create_directories():
    """創建必要的目錄"""
    directories = [
        "/Users/aaron/Projects/DataScout/data/output",
        "/Users/aaron/Projects/DataScout/data/models",
        "/Users/aaron/Projects/DataScout/data/raw",
        "/Users/aaron/Projects/DataScout/data/processed"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)


def get_stock_data(ticker_symbol, start_date, end_date):
    """獲取股票數據"""
    print(f"正在獲取 {ticker_symbol} 從 {start_date} 到 {end_date} 的歷史數據...")
    try:
        stock_data = yf.download(ticker_symbol, start=start_date, end=end_date)
        if stock_data.empty:
            print("錯誤：無法獲取股票數據。請檢查股票代號和日期範圍。")
            return None
        else:
            # 如果有多級列，展平它們
            if isinstance(stock_data.columns, pd.MultiIndex):
                stock_data.columns = stock_data.columns.droplevel(1)
            print("數據獲取成功！")
            return stock_data
    except Exception as e:
        print(f"獲取數據時發生錯誤：{e}")
        return None


def create_sentiment_data(stock_data):
    """創建模擬情緒數據"""
    stock_data['Price_Change'] = stock_data['Close'].diff()
    
    sentiment_base = stock_data['Price_Change'].shift(1).fillna(0) * 5
    sentiment_noise = np.random.randn(len(stock_data)) * 0.5
    
    simulated_sentiment = np.tanh(sentiment_base + sentiment_noise)
    stock_data['Sentiment'] = simulated_sentiment
    stock_data['Sentiment'] = stock_data['Sentiment'].fillna(method='bfill')
    
    return stock_data


def create_features(stock_data):
    """創建所有特徵"""
    # 滯後特徵
    stock_data['Close_Lag1'] = stock_data['Close'].shift(1)
    stock_data['Open_Lag1'] = stock_data['Open'].shift(1)
    stock_data['High_Lag1'] = stock_data['High'].shift(1)
    stock_data['Low_Lag1'] = stock_data['Low'].shift(1)
    
    # 移動平均線
    stock_data['MA_5'] = stock_data['Close'].rolling(window=5).mean()
    stock_data['MA_10'] = stock_data['Close'].rolling(window=10).mean()
    stock_data['MA_20'] = stock_data['Close'].rolling(window=20).mean()
    
    # 波動性指標
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
    
    # 價格位置指標
    stock_data['Price_Position_BB'] = (stock_data['Close'] - stock_data.get('BBL_20_2.0', stock_data['Close'])) / \
                                     (stock_data.get('BBU_20_2.0', stock_data['Close']) - stock_data.get('BBL_20_2.0', stock_data['Close']))
    
    stock_data['Price_MA_Ratio_5'] = stock_data['Close'] / stock_data['MA_5']
    stock_data['Price_MA_Ratio_20'] = stock_data['Close'] / stock_data['MA_20']
    stock_data['Volume_Price_Trend'] = stock_data['Volume'] * (stock_data['Close'].pct_change())
    
    # 時間特徵
    stock_data['DayOfWeek'] = stock_data.index.dayofweek
    stock_data['Month'] = stock_data.index.month
    stock_data['Quarter'] = stock_data.index.quarter
    stock_data['IsMonthEnd'] = stock_data.index.is_month_end.astype(int)
    stock_data['IsQuarterEnd'] = stock_data.index.is_quarter_end.astype(int)
    
    return stock_data


def prepare_data_for_training(stock_data):
    """準備訓練數據"""
    # 移除缺失值
    initial_rows = len(stock_data)
    stock_data.dropna(inplace=True)
    rows_after_dropna = len(stock_data)
    print(f"移除缺失值前: {initial_rows} 行")
    print(f"移除缺失值後: {rows_after_dropna} 行")
    print(f"移除了 {initial_rows - rows_after_dropna} 行數據")
    
    # 創建目標變量
    stock_data['Target'] = (stock_data['Close'].shift(-1) > stock_data['Close']).astype(int)
    stock_data.dropna(inplace=True)
    
    return stock_data


def run_lightgbm_prediction(ticker_symbol="AAPL", start_date="2015-01-01", end_date="2025-01-01"):
    """運行完整的 LightGBM 股票預測流程"""
    
    # 創建目錄
    create_directories()
    
    # 獲取數據
    stock_data = get_stock_data(ticker_symbol, start_date, end_date)
    if stock_data is None:
        return None
    
    print(stock_data.head())
    print(stock_data.tail())
    
    # 創建情緒數據
    stock_data = create_sentiment_data(stock_data)
    
    print("\n模擬情緒數據的一部分：")
    print(stock_data[['Close', 'Price_Change', 'Sentiment']].head())
    print(stock_data[['Close', 'Price_Change', 'Sentiment']].tail())
    
    print(f"\n情緒數據統計：")
    print(f"平均值: {stock_data['Sentiment'].mean():.4f}")
    print(f"標準差: {stock_data['Sentiment'].std():.4f}")
    print(f"最小值: {stock_data['Sentiment'].min():.4f}")
    print(f"最大值: {stock_data['Sentiment'].max():.4f}")
    
    # 創建特徵
    stock_data = create_features(stock_data)
    
    # 準備訓練數據
    stock_data = prepare_data_for_training(stock_data)
    
    print("\n最終特徵數據集 (部分欄位)：")
    print(stock_data[['Close', 'Sentiment', 'MA_5', 'RSI_14', 'MACD_12_26_9', 'Sentiment_MA_5', 'Target']].head())
    print(stock_data[['Close', 'Sentiment', 'MA_5', 'RSI_14', 'MACD_12_26_9', 'Sentiment_MA_5', 'Target']].tail())
    
    # 準備特徵和目標
    exclude_columns = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume', 'Price_Change', 'Target']
    # 只刪除實際存在的列
    existing_exclude = [col for col in exclude_columns if col in stock_data.columns]
    features = stock_data.drop(columns=existing_exclude)
    target = stock_data['Target']
    
    print(f"\n特徵維度: {features.shape}")
    print(f"目標維度: {target.shape}")
    print(f"特徵列名: {list(features.columns)}")
    
    # 時間序列分割
    split_date = pd.Timestamp('2023-01-01')
    X_train = features[stock_data.index < split_date]
    y_train = target[stock_data.index < split_date]
    X_test = features[stock_data.index >= split_date]
    y_test = target[stock_data.index >= split_date]
    
    test_data = stock_data[stock_data.index >= split_date].copy()
    
    print(f"\n訓練集大小: {X_train.shape[0]} 樣本")
    print(f"測試集大小: {X_test.shape[0]} 樣本")
    print(f"訓練集時間範圍: {X_train.index.min()} 到 {X_train.index.max()}")
    print(f"測試集時間範圍: {X_test.index.min()} 到 {X_test.index.max()}")
    
    # 目標分佈統計
    train_target_dist = y_train.value_counts()
    test_target_dist = y_test.value_counts()
    print(f"\n訓練集目標分佈: 下跌 (0): {train_target_dist.get(0, 0)}, 上漲 (1): {train_target_dist.get(1, 0)}")
    print(f"測試集目標分佈: 下跌 (0): {test_target_dist.get(0, 0)}, 上漲 (1): {test_target_dist.get(1, 0)}")
    
    # 訓練模型 - 超參數優化
    print("\n開始超參數優化...")
    
    param_distributions = {
        'n_estimators': [100, 200, 300, 500],
        'learning_rate': [0.01, 0.05, 0.1, 0.2],
        'max_depth': [3, 5, 7, 9],
        'num_leaves': [31, 50, 100, 150],
        'min_child_samples': [20, 30, 50],
        'subsample': [0.8, 0.9, 1.0],
        'colsample_bytree': [0.8, 0.9, 1.0]
    }
    
    lgb_model = lgb.LGBMClassifier(random_state=42, verbose=-1)
    
    tscv = TimeSeriesSplit(n_splits=3)
    random_search = RandomizedSearchCV(
        lgb_model, 
        param_distributions, 
        n_iter=50, 
        scoring='roc_auc', 
        cv=tscv, 
        verbose=1, 
        random_state=42, 
        n_jobs=-1
    )
    
    random_search.fit(X_train, y_train)
    
    print("最佳參數:", random_search.best_params_)
    print("最佳CV分數 (ROC-AUC):", random_search.best_score_)
    
    # 使用最佳模型進行預測
    best_model = random_search.best_estimator_
    
    # 訓練集預測
    y_train_pred = best_model.predict(X_train)
    y_train_proba = best_model.predict_proba(X_train)[:, 1]
    
    # 測試集預測
    y_test_pred = best_model.predict(X_test)
    y_test_proba = best_model.predict_proba(X_test)[:, 1]
    
    # 評估結果
    train_accuracy = accuracy_score(y_train, y_train_pred)
    test_accuracy = accuracy_score(y_test, y_test_pred)
    train_roc_auc = roc_auc_score(y_train, y_train_proba)
    test_roc_auc = roc_auc_score(y_test, y_test_proba)
    
    print(f"\n=== 模型評估結果 ===")
    print(f"訓練集準確率: {train_accuracy:.4f}")
    print(f"測試集準確率: {test_accuracy:.4f}")
    print(f"訓練集 ROC-AUC: {train_roc_auc:.4f}")
    print(f"測試集 ROC-AUC: {test_roc_auc:.4f}")
    
    # 詳細分類報告
    print(f"\n測試集詳細分類報告:")
    print(classification_report(y_test, y_test_pred))
    
    # 保存模型
    model_path = "/Users/aaron/Projects/DataScout/data/models/lightgbm_stock_model.pkl"
    joblib.dump(best_model, model_path)
    print(f"\n模型已保存至: {model_path}")
    
    # 特徵重要性
    feature_importance = best_model.feature_importances_
    feature_names = X_train.columns
    importance_df = pd.DataFrame({
        'feature': feature_names,
        'importance': feature_importance
    }).sort_values('importance', ascending=False)
    
    print(f"\n前10重要特徵:")
    print(importance_df.head(10))
    
    # 創建可視化
    plt.style.use('default')
    
    # 1. 特徵重要性圖
    plt.figure(figsize=(12, 8))
    top_features = importance_df.head(15)
    plt.barh(range(len(top_features)), top_features['importance'])
    plt.yticks(range(len(top_features)), top_features['feature'])
    plt.xlabel('重要性')
    plt.title('前15個重要特徵')
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig('/Users/aaron/Projects/DataScout/data/output/feature_importance.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. ROC曲線
    plt.figure(figsize=(10, 8))
    fpr_train, tpr_train, _ = roc_curve(y_train, y_train_proba)
    fpr_test, tpr_test, _ = roc_curve(y_test, y_test_proba)
    
    plt.plot(fpr_train, tpr_train, label=f'訓練集 (AUC = {train_roc_auc:.3f})', linewidth=2)
    plt.plot(fpr_test, tpr_test, label=f'測試集 (AUC = {test_roc_auc:.3f})', linewidth=2)
    plt.plot([0, 1], [0, 1], 'k--', label='隨機分類器')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('偽陽性率 (False Positive Rate)')
    plt.ylabel('真陽性率 (True Positive Rate)')
    plt.title('ROC 曲線')
    plt.legend(loc="lower right")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('/Users/aaron/Projects/DataScout/data/output/roc_curve.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 3. 混淆矩陣
    plt.figure(figsize=(8, 6))
    cm = confusion_matrix(y_test, y_test_pred)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['下跌', '上漲'], yticklabels=['下跌', '上漲'])
    plt.title('混淆矩陣 (測試集)')
    plt.ylabel('實際')
    plt.xlabel('預測')
    plt.tight_layout()
    plt.savefig('/Users/aaron/Projects/DataScout/data/output/confusion_matrix.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 回測分析
    print(f"\n=== 回測分析 ===")
    
    test_data['Predicted'] = y_test_pred
    test_data['Predicted_Proba'] = y_test_proba
    test_data['Actual_Return'] = test_data['Close'].pct_change()
    test_data['Strategy_Return'] = test_data['Actual_Return'] * test_data['Predicted']
    
    # 累積收益
    test_data['Cumulative_Actual'] = (1 + test_data['Actual_Return']).cumprod()
    test_data['Cumulative_Strategy'] = (1 + test_data['Strategy_Return']).cumprod()
    
    # 計算績效指標
    total_actual_return = test_data['Cumulative_Actual'].iloc[-1] - 1
    total_strategy_return = test_data['Cumulative_Strategy'].iloc[-1] - 1
    
    actual_volatility = test_data['Actual_Return'].std() * np.sqrt(252)
    strategy_volatility = test_data['Strategy_Return'].std() * np.sqrt(252)
    
    actual_sharpe = test_data['Actual_Return'].mean() / test_data['Actual_Return'].std() * np.sqrt(252)
    strategy_sharpe = test_data['Strategy_Return'].mean() / test_data['Strategy_Return'].std() * np.sqrt(252)
    
    # 最大回撤
    rolling_max_actual = test_data['Cumulative_Actual'].expanding().max()
    actual_drawdown = (test_data['Cumulative_Actual'] / rolling_max_actual - 1)
    max_actual_drawdown = actual_drawdown.min()
    
    rolling_max_strategy = test_data['Cumulative_Strategy'].expanding().max()
    strategy_drawdown = (test_data['Cumulative_Strategy'] / rolling_max_strategy - 1)
    max_strategy_drawdown = strategy_drawdown.min()
    
    print(f"買入持有策略總收益: {total_actual_return:.4f} ({total_actual_return*100:.2f}%)")
    print(f"機器學習策略總收益: {total_strategy_return:.4f} ({total_strategy_return*100:.2f}%)")
    print(f"買入持有策略年化波動率: {actual_volatility:.4f}")
    print(f"機器學習策略年化波動率: {strategy_volatility:.4f}")
    print(f"買入持有策略夏普比率: {actual_sharpe:.4f}")
    print(f"機器學習策略夏普比率: {strategy_sharpe:.4f}")
    print(f"買入持有策略最大回撤: {max_actual_drawdown:.4f} ({max_actual_drawdown*100:.2f}%)")
    print(f"機器學習策略最大回撤: {max_strategy_drawdown:.4f} ({max_strategy_drawdown*100:.2f}%)")
    
    # 4. 累積收益圖
    plt.figure(figsize=(14, 8))
    plt.plot(test_data.index, test_data['Cumulative_Actual'], label='買入持有策略', linewidth=2)
    plt.plot(test_data.index, test_data['Cumulative_Strategy'], label='機器學習策略', linewidth=2)
    plt.title('策略績效比較')
    plt.xlabel('日期')
    plt.ylabel('累積收益')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('/Users/aaron/Projects/DataScout/data/output/strategy_performance.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 未來預測
    print(f"\n=== 未來預測 ===")
    
    # 使用最後一天的數據進行預測
    last_features = features.iloc[-1:].copy()
    future_prediction = best_model.predict(last_features)[0]
    future_probability = best_model.predict_proba(last_features)[0, 1]
    
    print(f"基於最新數據預測明日趨勢:")
    print(f"預測結果: {'上漲' if future_prediction == 1 else '下跌'}")
    print(f"上漲概率: {future_probability:.4f}")
    
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
    
    return {
        'model': best_model,
        'test_accuracy': test_accuracy,
        'test_roc_auc': test_roc_auc,
        'feature_importance': importance_df,
        'backtest_results': {
            'total_actual_return': total_actual_return,
            'total_strategy_return': total_strategy_return,
            'strategy_sharpe': strategy_sharpe,
            'max_strategy_drawdown': max_strategy_drawdown
        }
    }


if __name__ == "__main__":
    # 如果直接運行此模組，執行預測
    result = run_lightgbm_prediction()
