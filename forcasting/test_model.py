#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試已訓練的 LightGBM 模型
"""

import sys
import os
import pickle
import pandas as pd
import numpy as np
from datetime import datetime

# 添加項目根目錄到 Python 路徑
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 導入字體配置
try:
    from config.chart_fonts import configure_chinese_font
    print(f"成功導入字體配置模組 (項目根目錄: {project_root})")
    configure_chinese_font()
    print("中文字體配置完成！")
except ImportError as e:
    print(f"無法導入字體配置模組: {e}")
    print("將使用默認字體設置")

def load_trained_model():
    """載入已訓練的模型和特徵名稱"""
    model_path = os.path.join(project_root, "data", "models", "lightgbm_stock_predictor.pkl")
    features_path = os.path.join(project_root, "data", "models", "feature_names.pkl")
    
    if not os.path.exists(model_path):
        print(f"模型文件不存在: {model_path}")
        return None, None
    
    if not os.path.exists(features_path):
        print(f"特徵名稱文件不存在: {features_path}")
        return None, None
    
    # 載入模型
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    
    # 載入特徵名稱
    with open(features_path, 'rb') as f:
        feature_names = pickle.load(f)
    
    print(f"模型載入成功！特徵數量: {len(feature_names)}")
    print(f"特徵名稱: {feature_names[:10]}...")  # 顯示前10個特徵
    
    return model, feature_names

def test_prediction():
    """測試模型預測功能"""
    print("\n=== 測試模型預測功能 ===")
    
    # 載入模型
    model, feature_names = load_trained_model()
    if model is None or feature_names is None:
        print("無法載入模型，測試終止")
        return
    
    # 創建隨機測試數據
    np.random.seed(42)
    test_data = np.random.randn(5, len(feature_names))
    test_df = pd.DataFrame(test_data, columns=feature_names)
    
    print(f"\n測試數據形狀: {test_df.shape}")
    print("測試數據前幾行:")
    print(test_df.head())
    
    # 進行預測
    try:
        predictions = model.predict(test_df)
        probabilities = model.predict_proba(test_df)
        
        print(f"\n預測結果:")
        for i, (pred, prob) in enumerate(zip(predictions, probabilities)):
            print(f"  樣本 {i+1}: 預測類別={pred}, 概率=[{prob[0]:.4f}, {prob[1]:.4f}]")
        
        print("\n模型測試成功！")
        
    except Exception as e:
        print(f"預測過程中發生錯誤: {e}")

def check_model_info():
    """檢查模型詳細信息"""
    print("\n=== 檢查模型詳細信息 ===")
    
    model, feature_names = load_trained_model()
    if model is None:
        return
    
    print(f"模型類型: {type(model).__name__}")
    print(f"特徵數量: {model.n_features_}")
    print(f"類別數量: {model.n_classes_}")
    print(f"訓練迭代次數: {model.booster_.num_trees()}")
    
    # 獲取特徵重要性
    importance = model.feature_importances_
    feature_importance = pd.DataFrame({
        'feature': feature_names,
        'importance': importance
    }).sort_values('importance', ascending=False)
    
    print(f"\n前10個最重要特徵:")
    print(feature_importance.head(10))

if __name__ == "__main__":
    print("開始測試已訓練的 LightGBM 模型...")
    
    # 檢查模型信息
    check_model_info()
    
    # 測試預測功能
    test_prediction()
    
    print("\n模型測試完成！")
