# -*- coding: utf-8 -*-
"""
股價預測配置文件

包含模型參數、路徑設置和其他配置項
"""

import os
from pathlib import Path

# 項目根目錄
PROJECT_ROOT = Path(__file__).parent.parent

# 數據目錄配置
DATA_DIRS = {
    'output': PROJECT_ROOT / 'data' / 'output',
    'models': PROJECT_ROOT / 'data' / 'models',
    'raw': PROJECT_ROOT / 'data' / 'raw',
    'processed': PROJECT_ROOT / 'data' / 'processed'
}

# 創建必要的目錄
for dir_path in DATA_DIRS.values():
    dir_path.mkdir(parents=True, exist_ok=True)

# 股票配置
STOCK_CONFIG = {
    'default_symbol': 'AAPL',
    'start_date': '2015-01-01',
    'end_date': '2025-01-01',
    'split_date': '2023-01-01'
}

# 模型配置
MODEL_CONFIG = {
    'random_state': 42,
    'test_size': 0.2,
    'cv_folds': 5,
    'lightgbm_params': {
        'objective': 'binary',
        'metric': 'binary_logloss',
        'boosting_type': 'gbdt',
        'num_leaves': 31,
        'learning_rate': 0.1,
        'feature_fraction': 0.9,
        'bagging_fraction': 0.8,
        'bagging_freq': 5,
        'verbose': -1,
        'random_state': 42
    }
}

# 技術指標配置
TECHNICAL_INDICATORS = {
    'rsi_period': 14,
    'macd_fast': 12,
    'macd_slow': 26,
    'macd_signal': 9,
    'bb_period': 20,
    'bb_std': 2,
    'stoch_k': 14,
    'stoch_d': 3,
    'willr_period': 14,
    'ma_periods': [5, 10, 20, 50]
}

# 特徵工程配置
FEATURE_CONFIG = {
    'lag_periods': [1, 2, 3, 5],
    'rolling_windows': [5, 10, 20],
    'sentiment_weight': 5.0,
    'sentiment_noise_std': 0.5
}

# 視覺化配置
PLOT_CONFIG = {
    'figsize': (12, 8),
    'dpi': 300,
    'style': 'seaborn-v0_8',
    'color_palette': 'viridis'
}

# 文件路徑配置
FILE_PATHS = {
    'model': DATA_DIRS['models'] / 'lightgbm_stock_predictor.pkl',
    'features': DATA_DIRS['models'] / 'feature_names.pkl',
    'scaler': DATA_DIRS['models'] / 'feature_scaler.pkl',
    'backtest_results': DATA_DIRS['output'] / 'backtest_results.csv',
    'feature_importance': DATA_DIRS['output'] / 'feature_importance.csv',
    'predictions': DATA_DIRS['output'] / 'predictions.csv'
}

# 日誌配置
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': DATA_DIRS['output'] / 'stock_prediction.log'
}

# 風險管理配置
RISK_CONFIG = {
    'max_position_size': 0.1,  # 最大倉位比例
    'stop_loss': 0.05,         # 止損比例
    'take_profit': 0.10,       # 止盈比例
    'min_confidence': 0.6      # 最小信心度閾值
}
