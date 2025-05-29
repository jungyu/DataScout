# -*- coding: utf-8 -*-
"""
LightGBM 股票預測範例 - 帶中文字體支援
結合股價技術指標與模擬新聞情緒預測股價趨勢
"""

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
    from config.chart_fonts import setup_chinese_fonts
    font_config_available = True
    print("✓ 字體配置模組導入成功")
except ImportError as e:
    print(f"警告：無法導入字體配置模組: {e}")
    font_config_available = False

import yfinance as yf
import pandas as pd
import numpy as np
import pandas_ta as ta
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_auc_score, roc_curve
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import joblib

# 設定中文字體支援
if font_config_available:
    print("正在配置中文字體...")
    font_manager = setup_chinese_fonts()
    print("中文字體配置完成！")
else:
    # 使用基本的中文字體配置，優先使用實際可用的字體
    print("使用預設中文字體配置...")
    plt.rcParams['font.family'] = ['Heiti TC', 'STHeiti', 'Apple LiGothic', 'Hei', 'Kai', 'Arial Unicode MS', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
    print("預設中文字體配置完成！")

def main():
    """主函數，包含所有執行邏輯"""
    
    print("=== LightGBM 股票預測分析開始 ===")
    
    # 1. 獲取歷史股價數據
    ticker_symbol = "AAPL"
    start_date = "2020-01-01"
    end_date = "2024-12-31"
    
    print(f"正在獲取 {ticker_symbol} 從 {start_date} 到 {end_date} 的歷史數據...")
    
    try:
        # 使用 yfinance 獲取數據
        stock_data = yf.download(ticker_symbol, start=start_date, end=end_date)
        
        # 檢查是否為多層索引並平坦化
        if isinstance(stock_data.columns, pd.MultiIndex):
            print("檢測到多層索引，正在平坦化...")
            stock_data.columns = stock_data.columns.droplevel(1)
        
        if stock_data.empty:
            raise ValueError("獲取的數據為空")
            
        print(f"✓ 數據獲取成功！數據點數量: {len(stock_data)}")
        print(f"數據日期範圍: {stock_data.index.min()} 到 {stock_data.index.max()}")
        
    except Exception as e:
        print(f"✗ 獲取數據時發生錯誤：{e}")
        return
    
    # 2. 數據基本信息
    print(f"\n數據基本信息:")
    print(f"- 數據形狀: {stock_data.shape}")
    print(f"- 欄位: {list(stock_data.columns)}")
    print(f"- 缺失值:")
    print(stock_data.isnull().sum())
    
    # 3. 特徵工程
    print("\n開始特徵工程...")
    
    # 基本價格特徵
    stock_data['Price_Change'] = stock_data['Close'].diff()
    stock_data['Returns'] = stock_data['Close'].pct_change()
    
    # 移動平均
    stock_data['MA_5'] = stock_data['Close'].rolling(window=5).mean()
    stock_data['MA_10'] = stock_data['Close'].rolling(window=10).mean()
    stock_data['MA_20'] = stock_data['Close'].rolling(window=20).mean()
    
    # 技術指標
    stock_data.ta.rsi(close='Close', length=14, append=True)
    stock_data.ta.macd(close='Close', fast=12, slow=26, signal=9, append=True)
    stock_data.ta.bbands(close='Close', length=20, std=2, append=True)
    
    # 波動性指標
    stock_data['Volatility_10'] = stock_data['Returns'].rolling(window=10).std()
    stock_data['ATR'] = (stock_data['High'] - stock_data['Low']).rolling(window=14).mean()
    
    # 成交量特徵
    stock_data['Volume_MA_10'] = stock_data['Volume'].rolling(window=10).mean()
    stock_data['Volume_Ratio'] = stock_data['Volume'] / stock_data['Volume_MA_10']
    
    # 模擬情緒數據（實際應用中應從新聞數據獲取）
    np.random.seed(42)
    sentiment_base = stock_data['Returns'].shift(1).fillna(0) * 2
    sentiment_noise = np.random.randn(len(stock_data)) * 0.3
    stock_data['Sentiment'] = np.tanh(sentiment_base + sentiment_noise)
    
    # 滯後特徵
    for lag in [1, 2, 3]:
        stock_data[f'Close_Lag_{lag}'] = stock_data['Close'].shift(lag)
        stock_data[f'Volume_Lag_{lag}'] = stock_data['Volume'].shift(lag)
        stock_data[f'Returns_Lag_{lag}'] = stock_data['Returns'].shift(lag)
    
    # 4. 定義預測目標（預測明日股價是否上漲）
    stock_data['Target'] = (stock_data['Close'].shift(-1) > stock_data['Close']).astype(int)
    
    # 5. 清理數據
    print("清理數據中的缺失值...")
    initial_rows = len(stock_data)
    stock_data.dropna(inplace=True)
    final_rows = len(stock_data)
    print(f"清理完成，從 {initial_rows} 行減少到 {final_rows} 行")
    
    # 6. 準備特徵和目標變數
    feature_columns = [col for col in stock_data.columns 
                      if col not in ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume', 
                                   'Price_Change', 'Returns', 'Target']]
    
    X = stock_data[feature_columns]
    y = stock_data['Target']
    
    print(f"\n特徵數量: {len(feature_columns)}")
    print(f"特徵列表: {feature_columns[:10]}{'...' if len(feature_columns) > 10 else ''}")
    
    # 7. 分割數據
    split_date = "2023-01-01"
    train_mask = stock_data.index < split_date
    test_mask = stock_data.index >= split_date
    
    X_train, y_train = X[train_mask], y[train_mask]
    X_test, y_test = X[test_mask], y[test_mask]
    
    print(f"\n數據分割:")
    print(f"- 訓練集: {len(X_train)} 樣本")
    print(f"- 測試集: {len(X_test)} 樣本")
    print(f"- 正類比例 (訓練集): {y_train.mean():.3f}")
    print(f"- 正類比例 (測試集): {y_test.mean():.3f}")
    
    # 8. 訓練模型
    print("\n開始訓練 LightGBM 模型...")
    
    lgb_model = lgb.LGBMClassifier(
        objective='binary',
        metric='binary_logloss',
        boosting_type='gbdt',
        num_leaves=31,
        learning_rate=0.05,
        feature_fraction=0.9,
        bagging_fraction=0.8,
        bagging_freq=5,
        verbose=0,
        random_state=42
    )
    
    lgb_model.fit(X_train, y_train)
    print("✓ 模型訓練完成")
    
    # 9. 模型評估
    print("\n模型評估:")
    
    # 預測
    y_pred = lgb_model.predict(X_test)
    y_pred_proba = lgb_model.predict_proba(X_test)[:, 1]
    
    # 計算評估指標
    accuracy = accuracy_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_pred_proba)
    
    print(f"- 準確率: {accuracy:.4f}")
    print(f"- ROC AUC: {roc_auc:.4f}")
    
    # 混淆矩陣
    cm = confusion_matrix(y_test, y_pred)
    print(f"- 混淆矩陣:")
    print(cm)
    
    # 10. 特徵重要性
    feature_importance = pd.DataFrame({
        'feature': feature_columns,
        'importance': lgb_model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print(f"\n前10個重要特徵:")
    print(feature_importance.head(10))
    
    # 11. 視覺化結果
    print("\n正在生成視覺化圖表...")
    
    # 創建輸出目錄
    output_dir = '/Users/aaron/Projects/DataScout/data/output'
    os.makedirs(output_dir, exist_ok=True)
    
    # 設定圖表樣式
    plt.style.use('default')
    sns.set_palette("husl")
    
    # 圖表1：混淆矩陣
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                xticklabels=['預測下跌', '預測上漲'], 
                yticklabels=['實際下跌', '實際上漲'])
    plt.title('混淆矩陣')
    plt.xlabel('預測結果')
    plt.ylabel('實際結果')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/confusion_matrix.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # 圖表2：ROC 曲線
    fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, linewidth=2, label=f'ROC 曲線 (AUC = {roc_auc:.3f})')
    plt.plot([0, 1], [0, 1], 'k--', label='隨機猜測')
    plt.xlabel('偽陽性率')
    plt.ylabel('真陽性率')
    plt.title('ROC 曲線')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/roc_curve.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # 圖表3：特徵重要性
    plt.figure(figsize=(12, 8))
    top_features = feature_importance.head(15)
    plt.barh(range(len(top_features)), top_features['importance'])
    plt.yticks(range(len(top_features)), top_features['feature'])
    plt.xlabel('重要性分數')
    plt.title('前15個最重要特徵')
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig(f'{output_dir}/feature_importance.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # 圖表4：預測概率分布
    plt.figure(figsize=(10, 6))
    plt.hist(y_pred_proba[y_test == 0], bins=30, alpha=0.7, label='實際下跌', density=True)
    plt.hist(y_pred_proba[y_test == 1], bins=30, alpha=0.7, label='實際上漲', density=True)
    plt.xlabel('預測上漲概率')
    plt.ylabel('密度')
    plt.title('預測概率分布')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f'{output_dir}/prediction_distribution.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # 12. 模型保存
    model_dir = '/Users/aaron/Projects/DataScout/data/models'
    os.makedirs(model_dir, exist_ok=True)
    
    model_path = f'{model_dir}/lightgbm_stock_predictor.pkl'
    joblib.dump(lgb_model, model_path)
    print(f"✓ 模型已保存至: {model_path}")
    
    # 保存特徵列表
    feature_path = f'{model_dir}/feature_names.pkl'
    joblib.dump(feature_columns, feature_path)
    print(f"✓ 特徵列表已保存至: {feature_path}")
    
    print(f"\n=== 分析完成 ===")
    print(f"所有輸出文件已保存至: {output_dir}")
    print(f"模型文件已保存至: {model_dir}")
    print("\n注意：此模型僅供學習和研究用途，不構成投資建議。")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n程序被用戶中斷")
    except Exception as e:
        print(f"\n程序執行時發生錯誤：{e}")
        import traceback
        traceback.print_exc()
