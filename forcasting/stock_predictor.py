# -*- coding: utf-8 -*-
"""
專業版股價預測系統 - 使用 LightGBM

這是一個完整的股價預測系統，包含數據獲取、特徵工程、模型訓練、評估和回測功能。
適用於量化交易研究和機器學習實踐。
"""

import os
import sys
import warnings
import logging
from datetime import datetime
warnings.filterwarnings('ignore')

# 添加項目路徑
sys.path.append(os.path.dirname(__file__))

# 設定中文字型支援（優先使用思源黑體字 Noto Sans TC）
try:
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from config.chart_fonts import setup_chinese_fonts
    font_manager = setup_chinese_fonts()
    print("✅ 中文字型設定完成，優先使用思源黑體字 (Noto Sans TC)")
except ImportError:
    print("⚠️  無法導入字型配置模組，使用基本字型設定")
    import matplotlib.pyplot as plt
    plt.rcParams['font.family'] = ['Noto Sans TC', 'Noto Sans CJK TC', 'PingFang TC', 'Heiti TC', 'DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False

import yfinance as yf
import pandas as pd
import numpy as np
try:
    import lightgbm as lgb
    from lightgbm import LGBMClassifier
except ImportError:
    print("Warning: LightGBM not properly installed. Please install with: pip install lightgbm")
    import sys
    sys.exit(1)
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV
from sklearn.metrics import accuracy_score
import joblib
import matplotlib.pyplot as plt

# 導入自定義模組
from config import *
from utils import FeatureEngineer, SentimentSimulator, ModelEvaluator, BacktestAnalyzer, create_target_variable, clean_data, split_time_series


class StockPredictor:
    """股價預測器主類"""
    
    def __init__(self, config=None):
        self.config = config or STOCK_CONFIG
        self.model_config = MODEL_CONFIG
        self.technical_config = TECHNICAL_INDICATORS
        self.feature_config = FEATURE_CONFIG
        
        # 初始化組件
        self.feature_engineer = FeatureEngineer(self.technical_config)
        self.sentiment_simulator = SentimentSimulator(
            weight=self.feature_config['sentiment_weight'],
            noise_std=self.feature_config['sentiment_noise_std']
        )
        self.evaluator = ModelEvaluator()
        self.backtest_analyzer = BacktestAnalyzer()
        
        # 模型和數據
        self.model = None
        self.data = None
        self.features = None
        self.target = None
        
        # 設置日誌
        self._setup_logging()
        
    def _setup_logging(self):
        """設置日誌"""
        logging.basicConfig(
            level=getattr(logging, LOGGING_CONFIG['level']),
            format=LOGGING_CONFIG['format'],
            handlers=[
                logging.FileHandler(LOGGING_CONFIG['file']),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def fetch_data(self, symbol=None, start_date=None, end_date=None):
        """獲取股票數據"""
        symbol = symbol or self.config['default_symbol']
        start_date = start_date or self.config['start_date']
        end_date = end_date or self.config['end_date']
        
        self.logger.info(f"正在獲取 {symbol} 從 {start_date} 到 {end_date} 的數據...")
        
        try:
            data = yf.download(symbol, start=start_date, end=end_date)
            if data.empty:
                raise ValueError("無法獲取股票數據")
            
            # 處理 yfinance 多層級欄位索引問題
            if isinstance(data.columns, pd.MultiIndex):
                # 展平多層級欄位索引，只保留主要欄位名稱
                data.columns = [col[0] if isinstance(col, tuple) else col for col in data.columns]
                self.logger.info("已處理多層級欄位索引")
            
            self.data = data
            self.logger.info(f"成功獲取 {len(data)} 行數據")
            return data
            
        except Exception as e:
            self.logger.error(f"數據獲取失敗: {e}")
            raise
    
    def engineer_features(self):
        """特徵工程"""
        if self.data is None:
            raise ValueError("請先獲取數據")
        
        self.logger.info("開始特徵工程...")
        df = self.data.copy()
        
        # 基礎價格特徵
        df = self.feature_engineer.create_price_features(df)
        
        # 滯後特徵
        price_columns = ['Close', 'Open', 'High', 'Low', 'Volume']
        df = self.feature_engineer.create_lag_features(
            df, price_columns, self.feature_config['lag_periods']
        )
        
        # 滾動統計特徵
        df = self.feature_engineer.create_rolling_features(
            df, ['Close', 'Volume'], self.feature_config['rolling_windows']
        )
        
        # 技術指標
        df = self.feature_engineer.create_technical_indicators(df)
        
        # 時間特徵
        df = self.feature_engineer.create_time_features(df)
        
        # 模擬情緒數據
        price_changes = df['Close'].pct_change()
        df['Sentiment'] = self.sentiment_simulator.generate_sentiment(price_changes)
        df['Sentiment_Lag1'] = df['Sentiment'].shift(1)
        df['Sentiment_MA5'] = df['Sentiment'].rolling(5).mean()
        
        # 創建目標變量
        df['Target'] = create_target_variable(df, 'Close', 1)
        
        # 清理數據
        df = clean_data(df, method='drop')
        
        self.data = df
        self.logger.info(f"特徵工程完成，剩餘 {len(df)} 行數據")
        
        return df
    
    def prepare_features(self, exclude_columns=None):
        """準備特徵和目標變量"""
        if self.data is None:
            raise ValueError("請先進行特徵工程")
        
        # 默認排除的列
        default_exclude = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume', 'Target']
        exclude_columns = exclude_columns or default_exclude
        
        # 只排除實際存在的列
        existing_exclude = [col for col in exclude_columns if col in self.data.columns]
        
        # 分離特徵和目標
        self.features = self.data.drop(columns=existing_exclude)
        self.target = self.data['Target']
        
        self.logger.info(f"準備了 {self.features.shape[1]} 個特徵")
        return self.features, self.target
    
    def split_data(self, split_date=None):
        """分割訓練和測試數據"""
        split_date = split_date or self.config['split_date']
        
        train_data, test_data = split_time_series(self.data, split_date)
        
        # 分離特徵和目標
        feature_cols = self.features.columns
        
        X_train = train_data[feature_cols]
        y_train = train_data['Target']
        X_test = test_data[feature_cols]
        y_test = test_data['Target']
        
        self.logger.info(f"訓練集: {len(X_train)} 樣本, 測試集: {len(X_test)} 樣本")
        
        return X_train, X_test, y_train, y_test
    
    def train_model(self, X_train, y_train, optimize_params=False):
        """訓練模型"""
        self.logger.info("開始訓練模型...")
        
        if optimize_params:
            # 超參數優化
            param_grid = {
                'n_estimators': [100, 200, 300],
                'learning_rate': [0.05, 0.1, 0.15],
                'max_depth': [3, 5, 7],
                'num_leaves': [31, 50, 70]
            }
            
            base_model = lgb.LGBMClassifier(**self.model_config['lightgbm_params'])
            
            # 使用時間序列交叉驗證
            tscv = TimeSeriesSplit(n_splits=3)
            
            grid_search = GridSearchCV(
                base_model, param_grid, cv=tscv, scoring='accuracy', n_jobs=-1
            )
            
            # 為了節省時間，使用部分數據進行網格搜索
            sample_size = min(2000, len(X_train))
            X_sample = X_train.sample(n=sample_size, random_state=42)
            y_sample = y_train.loc[X_sample.index]
            
            grid_search.fit(X_sample, y_sample)
            
            self.logger.info(f"最佳參數: {grid_search.best_params_}")
            self.model = grid_search.best_estimator_
            
        else:
            # 使用默認參數
            self.model = lgb.LGBMClassifier(**self.model_config['lightgbm_params'])
        
        # 使用全部訓練數據進行最終訓練
        self.model.fit(X_train, y_train)
        self.logger.info("模型訓練完成")
        
        return self.model
    
    def evaluate_model(self, X_test, y_test, save_plots=True):
        """評估模型"""
        if self.model is None:
            raise ValueError("請先訓練模型")
        
        self.logger.info("開始模型評估...")
        
        # 預測
        y_pred = self.model.predict(X_test)
        y_pred_proba = self.model.predict_proba(X_test)[:, 1]
        
        # 評估
        results = self.evaluator.evaluate_classification(y_test, y_pred, y_pred_proba)
        
        self.logger.info(f"測試集準確率: {results['accuracy']:.4f}")
        self.logger.info(f"ROC AUC: {results['roc_auc']:.4f}")
        
        # 繪圖
        if save_plots:
            # 混淆矩陣
            self.evaluator.plot_confusion_matrix(
                results['confusion_matrix'],
                save_path=DATA_DIRS['output'] / 'confusion_matrix.png'
            )
            
            # ROC曲線
            fpr, tpr, _ = results['roc_data']
            self.evaluator.plot_roc_curve(
                fpr, tpr, results['roc_auc'],
                save_path=DATA_DIRS['output'] / 'roc_curve.png'
            )
            
            # 特徵重要性
            importance_df = self.evaluator.plot_feature_importance(
                self.features.columns, self.model.feature_importances_,
                save_path=DATA_DIRS['output'] / 'feature_importance.png'
            )
            
            # 保存特徵重要性
            importance_df.to_csv(FILE_PATHS['feature_importance'], index=False)
        
        return results
    
    def run_backtest(self, split_date=None, save_results=True):
        """運行回測"""
        if self.model is None:
            raise ValueError("請先訓練模型")
        
        split_date = split_date or self.config['split_date']
        
        self.logger.info("開始回測分析...")
        
        # 獲取測試期數據
        test_data = self.data[self.data.index >= split_date].copy()
        X_test = test_data[self.features.columns]
        
        # 預測
        predictions = self.model.predict(X_test)
        pred_probabilities = self.model.predict_proba(X_test)[:, 1]
        
        # 計算收益
        daily_returns = test_data['Close'].pct_change()
        backtest_df = self.backtest_analyzer.calculate_returns(
            test_data, predictions, daily_returns
        )
        
        # 計算績效指標
        strategy_returns = backtest_df['Strategy_Return'].fillna(0)
        benchmark_returns = backtest_df['Daily_Return']
        
        metrics = self.backtest_analyzer.calculate_metrics(
            strategy_returns, benchmark_returns
        )
        
        # 添加預測概率
        backtest_df['Predicted_Proba'] = pred_probabilities
        
        # 輸出結果
        self.logger.info("回測結果:")
        self.logger.info(f"策略總收益: {metrics['total_strategy_return']:.4f}")
        self.logger.info(f"基準總收益: {metrics['total_benchmark_return']:.4f}")
        self.logger.info(f"年化夏普比率: {metrics['sharpe_ratio']:.4f}")
        self.logger.info(f"最大回撤: {metrics['max_drawdown']:.4f}")
        self.logger.info(f"勝率: {metrics['win_rate']:.4f}")
        
        # 繪製回測結果
        self.backtest_analyzer.plot_backtest_results(
            backtest_df, 
            save_path=DATA_DIRS['output'] / 'backtest_results.png'
        )
        
        # 保存結果
        if save_results:
            backtest_df.to_csv(FILE_PATHS['backtest_results'])
            
            # 保存績效指標
            metrics_df = pd.DataFrame([metrics])
            metrics_df.to_csv(DATA_DIRS['output'] / 'backtest_metrics.csv', index=False)
        
        return backtest_df, metrics
    
    def predict_future(self, periods=1):
        """預測未來趨勢"""
        if self.model is None:
            raise ValueError("請先訓練模型")
        
        # 使用最新數據進行預測
        latest_features = self.features.iloc[-periods:].copy()
        
        predictions = self.model.predict(latest_features)
        probabilities = self.model.predict_proba(latest_features)[:, 1]
        
        results = []
        for i, (pred, prob) in enumerate(zip(predictions, probabilities)):
            confidence = "高" if prob > 0.6 or prob < 0.4 else "中"
            results.append({
                'prediction': '上漲' if pred == 1 else '下跌',
                'probability': prob,
                'confidence': confidence
            })
        
        return results
    
    def save_model(self):
        """保存模型"""
        if self.model is None:
            raise ValueError("沒有訓練好的模型可保存")
        
        # 保存模型
        joblib.dump(self.model, FILE_PATHS['model'])
        
        # 保存特徵名稱
        joblib.dump(self.features.columns.tolist(), FILE_PATHS['features'])
        
        self.logger.info(f"模型已保存至 {FILE_PATHS['model']}")
        
    def load_model(self):
        """加載模型"""
        try:
            self.model = joblib.load(FILE_PATHS['model'])
            feature_names = joblib.load(FILE_PATHS['features'])
            self.logger.info(f"模型已從 {FILE_PATHS['model']} 加載")
            return feature_names
        except FileNotFoundError:
            self.logger.error("找不到保存的模型文件")
            raise
    
    def run_full_pipeline(self, symbol=None, optimize_params=False):
        """運行完整的預測流程"""
        self.logger.info("開始運行完整的股價預測流程...")
        
        try:
            # 1. 獲取數據
            self.fetch_data(symbol)
            
            # 2. 特徵工程
            self.engineer_features()
            
            # 3. 準備特徵
            self.prepare_features()
            
            # 4. 分割數據
            X_train, X_test, y_train, y_test = self.split_data()
            
            # 5. 訓練模型
            self.train_model(X_train, y_train, optimize_params)
            
            # 6. 評估模型
            results = self.evaluate_model(X_test, y_test)
            
            # 7. 回測分析
            backtest_results, metrics = self.run_backtest()
            
            # 8. 預測未來
            future_predictions = self.predict_future()
            
            # 9. 保存模型
            self.save_model()
            
            # 輸出最終結果
            self.logger.info("=== 最終結果 ===")
            self.logger.info(f"測試集準確率: {results['accuracy']:.4f}")
            self.logger.info(f"ROC AUC: {results['roc_auc']:.4f}")
            self.logger.info(f"策略年化收益: {metrics['annualized_strategy_return']:.4f}")
            self.logger.info(f"夏普比率: {metrics['sharpe_ratio']:.4f}")
            
            for i, pred in enumerate(future_predictions):
                self.logger.info(f"未來第{i+1}天預測: {pred['prediction']} (概率: {pred['probability']:.4f}, 信心度: {pred['confidence']})")
            
            self.logger.info("流程完成!")
            
            return {
                'evaluation': results,
                'backtest': metrics,
                'future_predictions': future_predictions
            }
            
        except Exception as e:
            self.logger.error(f"流程執行失敗: {e}")
            raise


def main():
    """主函數"""
    print("=== 專業股價預測系統 ===")
    print("基於 LightGBM 的時間序列預測")
    print("=" * 50)
    
    # 創建預測器
    predictor = StockPredictor()
    
    # 運行完整流程
    results = predictor.run_full_pipeline(
        symbol='AAPL',  # 可以改為其他股票代碼
        optimize_params=False  # 設為 True 進行超參數優化（需要更多時間）
    )
    
    print("\n=== 注意事項 ===")
    print("此模型僅供學習和研究用途，不構成投資建議。")
    print("實際投資需謹慎考慮風險，並諮詢專業人士。")
    print("=" * 50)


if __name__ == "__main__":
    main()
