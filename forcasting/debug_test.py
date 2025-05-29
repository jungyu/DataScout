#!/usr/bin/env python3
"""
調試測試腳本 - 找出 Volume_Price_Trend 錯誤的原因
"""

import warnings
warnings.filterwarnings('ignore')

import pandas as pd
import yfinance as yf
from utils import FeatureEngineer
import traceback

def debug_feature_engineering():
    """調試特徵工程過程"""
    print("=== 調試特徵工程過程 ===")
    
    # 獲取測試數據
    print("1. 獲取測試數據...")
    data = yf.download("AAPL", start="2023-01-01", end="2024-01-01")
    print(f"原始數據形狀: {data.shape}")
    print(f"原始數據列: {list(data.columns)}")
    
    # 檢查並處理多級列索引
    if isinstance(data.columns, pd.MultiIndex):
        print("檢測到多級列索引，正在展平...")
        data.columns = data.columns.droplevel(1)  # 移除股票代碼層級
        print(f"展平後列名: {list(data.columns)}")
    
    # 初始化特徵工程器
    config = {
        'rsi_period': 14,
        'macd_fast': 12,
        'macd_slow': 26,
        'macd_signal': 9,
        'bb_period': 20,
        'bb_std': 2,
        'stoch_k': 14,
        'stoch_d': 3,
        'willr_period': 14,
        'sma_periods': [5, 10, 20, 50],
        'ema_periods': [5, 10, 20, 50]
    }
    
    engineer = FeatureEngineer(config)
    
    try:
        # 測試技術指標
        print("\n2. 創建技術指標...")
        data = engineer.create_technical_indicators(data)
        print(f"技術指標後數據形狀: {data.shape}")
        print(f"技術指標後列: {list(data.columns)}")
        
        # 測試價格特徵 - 這裡可能出現問題
        print("\n3. 創建價格特徵...")
        print(f"Price_Change 創建前數據形狀: {data.shape}")
        
        # 手動測試 Price_Change 計算
        price_change = data['Close'].pct_change()
        print(f"Price_Change 類型: {type(price_change)}")
        print(f"Price_Change 形狀: {price_change.shape if hasattr(price_change, 'shape') else 'N/A'}")
        
        # 手動測試 Volume_Price_Trend 計算
        volume_price_trend = data['Volume'] * price_change
        print(f"Volume_Price_Trend 類型: {type(volume_price_trend)}")
        print(f"Volume_Price_Trend 形狀: {volume_price_trend.shape if hasattr(volume_price_trend, 'shape') else 'N/A'}")
        
        data = engineer.create_price_features(data)
        print(f"價格特徵後數據形狀: {data.shape}")
        
        print("\n✅ 特徵工程成功完成!")
        
    except Exception as e:
        print(f"\n❌ 錯誤發生: {e}")
        print("\n完整錯誤訊息:")
        traceback.print_exc()

if __name__ == "__main__":
    debug_feature_engineering()
