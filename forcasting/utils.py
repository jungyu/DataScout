# -*- coding: utf-8 -*-
"""
股價預測工具模組

提供特徵工程、數據處理和評估等工具函數
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_auc_score, roc_curve
from sklearn.preprocessing import StandardScaler
import pandas_ta as ta
import warnings
warnings.filterwarnings('ignore')


class FeatureEngineer:
    """特徵工程類"""
    
    def __init__(self, config):
        self.config = config
        
    def create_lag_features(self, df, columns, lag_periods):
        """創建滯後特徵"""
        for col in columns:
            for lag in lag_periods:
                df[f'{col}_Lag{lag}'] = df[col].shift(lag)
        return df
    
    def create_rolling_features(self, df, columns, windows):
        """創建滾動統計特徵"""
        for col in columns:
            for window in windows:
                df[f'{col}_MA{window}'] = df[col].rolling(window=window).mean()
                df[f'{col}_STD{window}'] = df[col].rolling(window=window).std()
                df[f'{col}_MIN{window}'] = df[col].rolling(window=window).min()
                df[f'{col}_MAX{window}'] = df[col].rolling(window=window).max()
        return df
    
    def create_technical_indicators(self, df):
        """創建技術指標"""
        # RSI
        df.ta.rsi(close='Close', length=self.config['rsi_period'], append=True)
        
        # MACD
        df.ta.macd(close='Close', 
                  fast=self.config['macd_fast'], 
                  slow=self.config['macd_slow'], 
                  signal=self.config['macd_signal'], 
                  append=True)
        
        # 布林帶
        df.ta.bbands(close='Close', 
                    length=self.config['bb_period'], 
                    std=self.config['bb_std'], 
                    append=True)
        
        # 隨機指標
        df.ta.stoch(high='High', low='Low', close='Close', 
                   k=self.config['stoch_k'], 
                   d=self.config['stoch_d'], 
                   append=True)
        
        # 威廉指標
        df.ta.willr(high='High', low='Low', close='Close', 
                   length=self.config['willr_period'], 
                   append=True)
        
        return df
    
    def create_price_features(self, df):
        """創建價格相關特徵"""
        # 價格變化率
        df['Price_Change'] = df['Close'].pct_change()
        df['High_Low_Ratio'] = df['High'] / df['Low']
        df['Open_Close_Ratio'] = df['Open'] / df['Close']
        
        # 波動性特徵
        df['Daily_Range'] = df['High'] - df['Low']
        df['Daily_Range_Pct'] = (df['High'] - df['Low']) / df['Close']
        
        # 成交量特徵
        # 確保計算結果是單一列
        volume_price_trend = df['Volume'] * df['Price_Change']
        if isinstance(volume_price_trend, pd.DataFrame):
            df['Volume_Price_Trend'] = volume_price_trend.iloc[:, 0]
        else:
            df['Volume_Price_Trend'] = volume_price_trend
        df['Volume_MA_Ratio'] = df['Volume'] / df['Volume'].rolling(20).mean()
        
        return df
    
    def create_time_features(self, df):
        """創建時間特徵"""
        df['DayOfWeek'] = df.index.dayofweek
        df['Month'] = df.index.month
        df['Quarter'] = df.index.quarter
        df['IsMonthEnd'] = df.index.is_month_end.astype(int)
        df['IsQuarterEnd'] = df.index.is_quarter_end.astype(int)
        df['DayOfYear'] = df.index.dayofyear
        
        return df


class SentimentSimulator:
    """情緒模擬器"""
    
    def __init__(self, weight=5.0, noise_std=0.5, random_state=42):
        self.weight = weight
        self.noise_std = noise_std
        self.random_state = random_state
        
    def generate_sentiment(self, price_changes):
        """生成模擬情緒數據"""
        np.random.seed(self.random_state)
        
        # 基於價格變化的基礎情緒
        sentiment_base = price_changes.shift(1).fillna(0) * self.weight
        
        # 添加隨機噪音
        sentiment_noise = np.random.randn(len(price_changes)) * self.noise_std
        
        # 合併並標準化
        sentiment = sentiment_base + sentiment_noise
        sentiment = np.tanh(sentiment)  # 縮放到 [-1, 1]
        
        return sentiment.values  # 返回 numpy array


class ModelEvaluator:
    """模型評估器"""
    
    def __init__(self, save_path=None):
        self.save_path = save_path
        
    def evaluate_classification(self, y_true, y_pred, y_pred_proba=None):
        """評估分類模型"""
        results = {}
        
        # 基本指標
        results['accuracy'] = accuracy_score(y_true, y_pred)
        results['classification_report'] = classification_report(y_true, y_pred, output_dict=True)
        results['confusion_matrix'] = confusion_matrix(y_true, y_pred)
        
        # ROC AUC
        if y_pred_proba is not None:
            results['roc_auc'] = roc_auc_score(y_true, y_pred_proba)
            results['roc_data'] = roc_curve(y_true, y_pred_proba)
        
        return results
    
    def plot_confusion_matrix(self, cm, save_path=None):
        """繪製混淆矩陣"""
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                   xticklabels=['跌', '漲'], yticklabels=['跌', '漲'])
        plt.title('混淆矩陣')
        plt.xlabel('預測值')
        plt.ylabel('實際值')
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_roc_curve(self, fpr, tpr, auc_score, save_path=None):
        """繪製ROC曲線"""
        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, label=f'ROC Curve (AUC = {auc_score:.4f})')
        plt.plot([0, 1], [0, 1], 'k--', label='Random')
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('ROC 曲線')
        plt.legend()
        plt.grid(True)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_feature_importance(self, feature_names, importances, top_n=15, save_path=None):
        """繪製特徵重要性"""
        # 創建DataFrame並排序
        importance_df = pd.DataFrame({
            'feature': feature_names,
            'importance': importances
        }).sort_values('importance', ascending=False).head(top_n)
        
        plt.figure(figsize=(12, 8))
        plt.barh(range(len(importance_df)), importance_df['importance'])
        plt.yticks(range(len(importance_df)), importance_df['feature'])
        plt.xlabel('重要性分數')
        plt.title(f'前{top_n}個最重要的特徵')
        plt.gca().invert_yaxis()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
        
        return importance_df


class BacktestAnalyzer:
    """回測分析器"""
    
    def __init__(self):
        pass
    
    def calculate_returns(self, df, predictions, actual_returns):
        """計算策略收益"""
        df = df.copy()
        df['Daily_Return'] = actual_returns
        df['Predicted'] = predictions
        df['Strategy_Return'] = df['Predicted'] * df['Daily_Return'].shift(-1)
        
        # 累積收益
        df['Cumulative_Return'] = (1 + df['Daily_Return']).cumprod()
        df['Cumulative_Strategy_Return'] = (1 + df['Strategy_Return'].fillna(0)).cumprod()
        
        return df
    
    def calculate_metrics(self, strategy_returns, benchmark_returns):
        """計算績效指標"""
        metrics = {}
        
        # 總收益
        metrics['total_strategy_return'] = (1 + strategy_returns).prod() - 1
        metrics['total_benchmark_return'] = (1 + benchmark_returns).prod() - 1
        
        # 年化收益率
        days = len(strategy_returns)
        years = days / 252
        metrics['annualized_strategy_return'] = (1 + metrics['total_strategy_return']) ** (1/years) - 1
        metrics['annualized_benchmark_return'] = (1 + metrics['total_benchmark_return']) ** (1/years) - 1
        
        # 夏普比率
        excess_returns = strategy_returns - benchmark_returns
        metrics['sharpe_ratio'] = excess_returns.mean() / excess_returns.std() * np.sqrt(252)
        
        # 最大回撤
        cumulative = (1 + strategy_returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        metrics['max_drawdown'] = drawdown.min()
        
        # 勝率
        metrics['win_rate'] = (strategy_returns > 0).sum() / len(strategy_returns)
        
        return metrics
    
    def plot_backtest_results(self, df, save_path=None):
        """繪製回測結果"""
        plt.figure(figsize=(12, 6))
        plt.plot(df.index, df['Cumulative_Return'], label='買入持有策略', linewidth=2)
        plt.plot(df.index, df['Cumulative_Strategy_Return'], label='預測策略', linewidth=2)
        plt.xlabel('日期')
        plt.ylabel('累積收益')
        plt.title('策略回測結果')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()


def create_target_variable(df, target_column='Close', periods=1):
    """創建目標變量"""
    # 未來收益率
    future_returns = df[target_column].pct_change(periods).shift(-periods)
    # 二元化：上漲為1，下跌為0
    target = (future_returns > 0).astype(int)
    return target


def clean_data(df, method='drop'):
    """清理數據中的缺失值"""
    if method == 'drop':
        return df.dropna()
    elif method == 'fill':
        return df.fillna(method='ffill').fillna(method='bfill')
    else:
        raise ValueError("method must be 'drop' or 'fill'")


def split_time_series(df, split_date):
    """按時間分割數據集"""
    train_data = df[df.index < split_date]
    test_data = df[df.index >= split_date]
    return train_data, test_data
