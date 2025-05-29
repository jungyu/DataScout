# -*- coding: utf-8 -*-
"""
股價預測系統測試模組

包含單元測試和集成測試，確保系統的可靠性和準確性
"""

import unittest
import sys
import os
import tempfile
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

# 添加項目路徑
sys.path.append(os.path.dirname(__file__))

from stock_predictor import StockPredictor
from utils import FeatureEngineer, SentimentSimulator, ModelEvaluator, BacktestAnalyzer
from config import STOCK_CONFIG, MODEL_CONFIG, TECHNICAL_INDICATORS


class TestFeatureEngineer(unittest.TestCase):
    """測試特徵工程模組"""
    
    def setUp(self):
        self.feature_engineer = FeatureEngineer(TECHNICAL_INDICATORS)
        
        # 創建測試數據
        dates = pd.date_range('2020-01-01', '2023-12-31', freq='D')
        np.random.seed(42)
        
        self.test_data = pd.DataFrame({
            'Open': np.random.randn(len(dates)).cumsum() + 100,
            'High': np.random.randn(len(dates)).cumsum() + 105,
            'Low': np.random.randn(len(dates)).cumsum() + 95,
            'Close': np.random.randn(len(dates)).cumsum() + 100,
            'Volume': np.random.randint(1000000, 10000000, len(dates))
        }, index=dates)
        
        # 確保 High >= Low
        self.test_data['High'] = np.maximum(self.test_data['High'], self.test_data['Low'] + 1)
    
    def test_create_lag_features(self):
        """測試滯後特徵創建"""
        df = self.test_data.copy()
        columns = ['Close', 'Volume']
        lag_periods = [1, 2, 3]
        
        result = self.feature_engineer.create_lag_features(df, columns, lag_periods)
        
        # 檢查新欄位是否被創建
        expected_columns = ['Close_Lag1', 'Close_Lag2', 'Close_Lag3', 
                          'Volume_Lag1', 'Volume_Lag2', 'Volume_Lag3']
        for col in expected_columns:
            self.assertIn(col, result.columns)
        
        # 檢查滯後值是否正確
        self.assertTrue(pd.isna(result['Close_Lag1'].iloc[0]))  # 第一行應該是 NaN
        self.assertEqual(result['Close_Lag1'].iloc[1], result['Close'].iloc[0])
    
    def test_create_rolling_features(self):
        """測試滾動統計特徵創建"""
        df = self.test_data.copy()
        columns = ['Close']
        windows = [5, 10]
        
        result = self.feature_engineer.create_rolling_features(df, columns, windows)
        
        # 檢查新欄位是否被創建
        expected_columns = ['Close_MA5', 'Close_STD5', 'Close_MA10', 'Close_STD10']
        for col in expected_columns:
            self.assertIn(col, result.columns)
        
        # 檢查移動平均計算是否正確
        manual_ma5 = result['Close'].rolling(5).mean()
        pd.testing.assert_series_equal(result['Close_MA5'], manual_ma5, check_names=False)
    
    def test_create_price_features(self):
        """測試價格特徵創建"""
        df = self.test_data.copy()
        result = self.feature_engineer.create_price_features(df)
        
        expected_columns = ['Price_Change', 'High_Low_Ratio', 'Open_Close_Ratio', 
                          'Daily_Range', 'Daily_Range_Pct']
        for col in expected_columns:
            self.assertIn(col, result.columns)
        
        # 檢查計算邏輯
        self.assertTrue((result['High_Low_Ratio'] >= 1).all())  # High 應該 >= Low
        self.assertTrue((result['Daily_Range'] >= 0).all())     # 範圍應該 >= 0
    
    def test_create_time_features(self):
        """測試時間特徵創建"""
        df = self.test_data.copy()
        result = self.feature_engineer.create_time_features(df)
        
        expected_columns = ['DayOfWeek', 'Month', 'Quarter', 'IsMonthEnd', 'IsQuarterEnd']
        for col in expected_columns:
            self.assertIn(col, result.columns)
        
        # 檢查值的範圍
        self.assertTrue((result['DayOfWeek'] >= 0).all() and (result['DayOfWeek'] <= 6).all())
        self.assertTrue((result['Month'] >= 1).all() and (result['Month'] <= 12).all())
        self.assertTrue((result['Quarter'] >= 1).all() and (result['Quarter'] <= 4).all())


class TestSentimentSimulator(unittest.TestCase):
    """測試情緒模擬器"""
    
    def setUp(self):
        self.simulator = SentimentSimulator(weight=5.0, noise_std=0.5, random_state=42)
    
    def test_generate_sentiment(self):
        """測試情緒生成"""
        # 創建測試價格變化
        price_changes = pd.Series([0.01, -0.02, 0.015, -0.005, 0.02])
        
        sentiment = self.simulator.generate_sentiment(price_changes)
        
        # 檢查輸出格式
        self.assertEqual(len(sentiment), len(price_changes))
        self.assertTrue(isinstance(sentiment, np.ndarray))
        
        # 檢查值的範圍（應該在 [-1, 1] 之間）
        self.assertTrue((sentiment >= -1).all() and (sentiment <= 1).all())
    
    def test_reproducibility(self):
        """測試結果的可重現性"""
        price_changes = pd.Series([0.01, -0.02, 0.015, -0.005, 0.02])
        
        sentiment1 = self.simulator.generate_sentiment(price_changes)
        sentiment2 = self.simulator.generate_sentiment(price_changes)
        
        # 由於使用了固定的隨機種子，結果應該相同
        np.testing.assert_array_equal(sentiment1, sentiment2)


class TestModelEvaluator(unittest.TestCase):
    """測試模型評估器"""
    
    def setUp(self):
        self.evaluator = ModelEvaluator()
    
    def test_evaluate_classification(self):
        """測試分類評估"""
        # 創建測試數據
        y_true = np.array([0, 1, 1, 0, 1, 0, 1, 1, 0, 0])
        y_pred = np.array([0, 1, 0, 0, 1, 1, 1, 1, 0, 0])
        y_pred_proba = np.array([0.2, 0.8, 0.4, 0.3, 0.9, 0.6, 0.7, 0.8, 0.1, 0.2])
        
        results = self.evaluator.evaluate_classification(y_true, y_pred, y_pred_proba)
        
        # 檢查返回的指標
        self.assertIn('accuracy', results)
        self.assertIn('roc_auc', results)
        self.assertIn('confusion_matrix', results)
        self.assertIn('classification_report', results)
        
        # 檢查準確率計算
        expected_accuracy = (y_true == y_pred).sum() / len(y_true)
        self.assertEqual(results['accuracy'], expected_accuracy)


class TestBacktestAnalyzer(unittest.TestCase):
    """測試回測分析器"""
    
    def setUp(self):
        self.analyzer = BacktestAnalyzer()
    
    def test_calculate_returns(self):
        """測試收益計算"""
        # 創建測試數據
        dates = pd.date_range('2023-01-01', '2023-01-10', freq='D')
        df = pd.DataFrame({'Close': [100, 101, 99, 102, 98, 100, 103, 101, 99, 102]}, index=dates)
        
        predictions = np.array([1, 0, 1, 0, 1, 1, 0, 1, 0, 1])
        actual_returns = df['Close'].pct_change()
        
        result = self.analyzer.calculate_returns(df, predictions, actual_returns)
        
        # 檢查新欄位
        expected_columns = ['Daily_Return', 'Predicted', 'Strategy_Return', 
                          'Cumulative_Return', 'Cumulative_Strategy_Return']
        for col in expected_columns:
            self.assertIn(col, result.columns)
    
    def test_calculate_metrics(self):
        """測試績效指標計算"""
        # 創建測試收益序列
        strategy_returns = pd.Series([0.01, -0.005, 0.02, -0.01, 0.015])
        benchmark_returns = pd.Series([0.008, 0.002, 0.012, -0.003, 0.01])
        
        metrics = self.analyzer.calculate_metrics(strategy_returns, benchmark_returns)
        
        # 檢查指標
        expected_metrics = ['total_strategy_return', 'total_benchmark_return', 
                          'annualized_strategy_return', 'sharpe_ratio', 'win_rate']
        for metric in expected_metrics:
            self.assertIn(metric, metrics)
        
        # 檢查勝率計算
        expected_win_rate = (strategy_returns > 0).sum() / len(strategy_returns)
        self.assertEqual(metrics['win_rate'], expected_win_rate)


class TestStockPredictor(unittest.TestCase):
    """測試股價預測器主類"""
    
    def setUp(self):
        self.predictor = StockPredictor()
    
    @patch('yfinance.download')
    def test_fetch_data(self, mock_download):
        """測試數據獲取（使用模擬）"""
        # 模擬 yfinance 返回數據
        dates = pd.date_range('2023-01-01', '2023-01-10', freq='D')
        mock_data = pd.DataFrame({
            'Open': [100, 101, 99, 102, 98, 100, 103, 101, 99, 102],
            'High': [102, 103, 101, 104, 100, 102, 105, 103, 101, 104],
            'Low': [99, 100, 98, 101, 97, 99, 102, 100, 98, 101],
            'Close': [101, 100, 102, 99, 101, 103, 102, 100, 101, 103],
            'Volume': [1000000] * 10
        }, index=dates)
        
        mock_download.return_value = mock_data
        
        result = self.predictor.fetch_data('AAPL')
        
        # 檢查數據是否正確設置
        self.assertIsNotNone(self.predictor.data)
        self.assertEqual(len(self.predictor.data), 10)
        mock_download.assert_called_once()
    
    def test_prepare_features(self):
        """測試特徵準備"""
        # 創建測試數據
        dates = pd.date_range('2023-01-01', '2023-01-20', freq='D')
        test_data = pd.DataFrame({
            'Open': np.random.randn(len(dates)).cumsum() + 100,
            'High': np.random.randn(len(dates)).cumsum() + 105,
            'Low': np.random.randn(len(dates)).cumsum() + 95,
            'Close': np.random.randn(len(dates)).cumsum() + 100,
            'Volume': np.random.randint(1000000, 10000000, len(dates)),
            'Feature1': np.random.randn(len(dates)),
            'Feature2': np.random.randn(len(dates)),
            'Target': np.random.randint(0, 2, len(dates))
        }, index=dates)
        
        self.predictor.data = test_data
        
        features, target = self.predictor.prepare_features()
        
        # 檢查特徵和目標是否正確分離
        self.assertNotIn('Target', features.columns)
        self.assertIn('Feature1', features.columns)
        self.assertIn('Feature2', features.columns)
        self.assertEqual(len(target), len(test_data))


class TestIntegration(unittest.TestCase):
    """集成測試"""
    
    def setUp(self):
        self.predictor = StockPredictor()
    
    @patch('yfinance.download')
    def test_mini_pipeline(self, mock_download):
        """測試小型完整流程"""
        # 創建較大的測試數據集
        dates = pd.date_range('2020-01-01', '2023-12-31', freq='D')
        np.random.seed(42)
        
        # 生成更真實的股價數據
        price = 100
        prices = [price]
        for _ in range(len(dates) - 1):
            change = np.random.normal(0, 0.02)  # 2% 日波動率
            price *= (1 + change)
            prices.append(price)
        
        mock_data = pd.DataFrame({
            'Open': prices,
            'High': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
            'Low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
            'Close': prices,
            'Volume': np.random.randint(1000000, 10000000, len(dates))
        }, index=dates)
        
        mock_download.return_value = mock_data
        
        try:
            # 運行簡化的流程
            self.predictor.fetch_data('TEST')
            self.predictor.engineer_features()
            self.predictor.prepare_features()
            X_train, X_test, y_train, y_test = self.predictor.split_data('2023-01-01')
            
            # 檢查數據分割
            self.assertGreater(len(X_train), 0)
            self.assertGreater(len(X_test), 0)
            self.assertEqual(len(X_train), len(y_train))
            self.assertEqual(len(X_test), len(y_test))
            
            # 訓練簡單模型
            model = self.predictor.train_model(X_train, y_train, optimize_params=False)
            self.assertIsNotNone(model)
            
            # 進行預測
            results = self.predictor.evaluate_model(X_test, y_test, save_plots=False)
            self.assertIn('accuracy', results)
            self.assertIsInstance(results['accuracy'], float)
            self.assertTrue(0 <= results['accuracy'] <= 1)
            
        except Exception as e:
            self.fail(f"Mini pipeline failed: {e}")


class TestDataValidation(unittest.TestCase):
    """數據驗證測試"""
    
    def test_data_quality_checks(self):
        """測試數據質量檢查"""
        # 創建包含問題的數據
        dates = pd.date_range('2023-01-01', '2023-01-10', freq='D')
        problematic_data = pd.DataFrame({
            'Open': [100, np.nan, 99, 102, 98, 100, 103, 101, 99, 102],
            'High': [102, 103, 101, 104, 100, 102, 105, 103, 101, 104],
            'Low': [99, 100, 98, 101, 97, 99, 102, 100, 98, 101],
            'Close': [101, 100, 102, 99, 101, 103, 102, 100, 101, 103],
            'Volume': [1000000, -500000, 0, 2000000, 1500000, 1000000, 0, 800000, 1200000, 900000]
        }, index=dates)
        
        # 檢查缺失值
        missing_count = problematic_data.isnull().sum().sum()
        self.assertGreater(missing_count, 0)
        
        # 檢查異常值
        negative_volume = (problematic_data['Volume'] < 0).sum()
        self.assertGreater(negative_volume, 0)


def run_performance_test():
    """運行性能測試"""
    import time
    
    print("運行性能測試...")
    
    # 測試大數據集處理速度
    dates = pd.date_range('2015-01-01', '2024-12-31', freq='D')
    large_data = pd.DataFrame({
        'Open': np.random.randn(len(dates)).cumsum() + 100,
        'High': np.random.randn(len(dates)).cumsum() + 105,
        'Low': np.random.randn(len(dates)).cumsum() + 95,
        'Close': np.random.randn(len(dates)).cumsum() + 100,
        'Volume': np.random.randint(1000000, 10000000, len(dates))
    }, index=dates)
    
    feature_engineer = FeatureEngineer(TECHNICAL_INDICATORS)
    
    start_time = time.time()
    
    # 特徵工程性能測試
    result = feature_engineer.create_price_features(large_data.copy())
    result = feature_engineer.create_lag_features(result, ['Close'], [1, 2, 3])
    result = feature_engineer.create_rolling_features(result, ['Close'], [5, 10, 20])
    result = feature_engineer.create_time_features(result)
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    print(f"處理 {len(dates)} 行數據的時間: {processing_time:.2f} 秒")
    print(f"生成特徵數量: {result.shape[1]}")
    print(f"處理速度: {len(dates)/processing_time:.0f} 行/秒")
    
    return processing_time < 30  # 應該在30秒內完成


def main():
    """運行所有測試"""
    print("🧪 開始運行股價預測系統測試")
    print("=" * 50)
    
    # 運行單元測試
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加測試類
    test_classes = [
        TestFeatureEngineer,
        TestSentimentSimulator,
        TestModelEvaluator,
        TestBacktestAnalyzer,
        TestStockPredictor,
        TestIntegration,
        TestDataValidation
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # 運行測試
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 運行性能測試
    print("\n" + "=" * 50)
    performance_result = run_performance_test()
    
    # 輸出結果摘要
    print("\n" + "=" * 50)
    print("測試結果摘要:")
    print(f"運行測試數量: {result.testsRun}")
    print(f"失敗測試數量: {len(result.failures)}")
    print(f"錯誤測試數量: {len(result.errors)}")
    print(f"性能測試: {'通過' if performance_result else '失敗'}")
    
    if result.failures:
        print("\n失敗的測試:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\n錯誤的測試:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    # 返回是否所有測試都通過
    success = len(result.failures) == 0 and len(result.errors) == 0 and performance_result
    
    print(f"\n總體結果: {'✅ 所有測試通過' if success else '❌ 存在測試失敗'}")
    
    return success


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
