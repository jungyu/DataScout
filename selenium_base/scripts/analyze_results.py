#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數據分析腳本

此模組提供爬蟲結果的數據分析功能，包括：
1. 數據載入和預處理
2. 基本統計分析
3. 數據可視化
4. 報告生成
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Union, Optional

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from loguru import logger

# 添加項目根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.config.paths import OUTPUT_DIR
from src.core.utils.logger import setup_logger

class DataAnalyzer:
    """數據分析器"""
    
    def __init__(self, data_path: Union[str, Path], output_dir: Optional[Union[str, Path]] = None):
        """初始化分析器
        
        Args:
            data_path: 數據文件路徑
            output_dir: 輸出目錄路徑
        """
        self.data_path = Path(data_path)
        self.output_dir = Path(output_dir) if output_dir else OUTPUT_DIR / "analysis"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 設置日誌
        self.logger = setup_logger("analyzer", logging.INFO)
        
        # 載入數據
        self.data = self.load_data()
    
    def load_data(self) -> pd.DataFrame:
        """載入數據"""
        try:
            if self.data_path.suffix == '.json':
                with open(self.data_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return pd.DataFrame(data)
            elif self.data_path.suffix == '.csv':
                return pd.read_csv(self.data_path)
            else:
                raise ValueError(f"不支持的文件格式: {self.data_path.suffix}")
        except Exception as e:
            self.logger.error(f"載入數據失敗: {str(e)}")
            raise
    
    def preprocess_data(self) -> None:
        """數據預處理"""
        # 處理缺失值
        self.data = self.data.fillna({
            col: self.data[col].mean() if np.issubdtype(self.data[col].dtype, np.number)
            else self.data[col].mode()[0]
            for col in self.data.columns
        })
        
        # 轉換數據類型
        for col in self.data.columns:
            if self.data[col].dtype == 'object':
                try:
                    self.data[col] = pd.to_datetime(self.data[col])
                except:
                    pass
    
    def analyze_basic_stats(self) -> Dict:
        """基本統計分析"""
        stats = {
            "總筆數": len(self.data),
            "數值型統計": self.data.select_dtypes(include=[np.number]).describe().to_dict(),
            "類別型統計": {
                col: self.data[col].value_counts().to_dict()
                for col in self.data.select_dtypes(include=['object']).columns
            }
        }
        return stats
    
    def plot_distributions(self) -> None:
        """繪製分布圖"""
        # 數值型變量分布
        numeric_cols = self.data.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            plt.figure(figsize=(10, 6))
            sns.histplot(data=self.data, x=col, kde=True)
            plt.title(f'{col} 分布圖')
            plt.savefig(self.output_dir / f'{col}_distribution.png')
            plt.close()
        
        # 類別型變量分布
        categorical_cols = self.data.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            plt.figure(figsize=(12, 6))
            sns.countplot(data=self.data, y=col)
            plt.title(f'{col} 分布圖')
            plt.tight_layout()
            plt.savefig(self.output_dir / f'{col}_distribution.png')
            plt.close()
    
    def plot_correlations(self) -> None:
        """繪製相關性圖"""
        numeric_data = self.data.select_dtypes(include=[np.number])
        if len(numeric_data.columns) > 1:
            plt.figure(figsize=(12, 8))
            sns.heatmap(numeric_data.corr(), annot=True, cmap='coolwarm')
            plt.title('數值變量相關性熱圖')
            plt.tight_layout()
            plt.savefig(self.output_dir / 'correlation_heatmap.png')
            plt.close()
    
    def generate_report(self) -> None:
        """生成分析報告"""
        # 基本統計
        stats = self.analyze_basic_stats()
        
        # 生成報告
        report = [
            "# 數據分析報告",
            f"\n## 分析時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"\n## 數據文件：{self.data_path}",
            f"\n## 總筆數：{stats['總筆數']}",
            "\n## 數值型變量統計",
        ]
        
        # 添加數值型統計
        for col, col_stats in stats['數值型統計'].items():
            report.append(f"\n### {col}")
            for stat, value in col_stats.items():
                report.append(f"- {stat}: {value:.2f}")
        
        # 添加類別型統計
        report.append("\n## 類別型變量統計")
        for col, counts in stats['類別型統計'].items():
            report.append(f"\n### {col}")
            for value, count in counts.items():
                report.append(f"- {value}: {count}")
        
        # 保存報告
        report_path = self.output_dir / 'analysis_report.md'
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report))
        
        self.logger.info(f"分析報告已保存到: {report_path}")
    
    def run_analysis(self) -> None:
        """執行完整分析流程"""
        try:
            self.logger.info("開始數據分析")
            
            # 數據預處理
            self.logger.info("數據預處理")
            self.preprocess_data()
            
            # 基本統計
            self.logger.info("計算基本統計")
            stats = self.analyze_basic_stats()
            
            # 繪製圖表
            self.logger.info("繪製分布圖")
            self.plot_distributions()
            
            self.logger.info("繪製相關性圖")
            self.plot_correlations()
            
            # 生成報告
            self.logger.info("生成分析報告")
            self.generate_report()
            
            self.logger.info("分析完成")
            
        except Exception as e:
            self.logger.error(f"分析過程出錯: {str(e)}")
            raise

def parse_args():
    """解析命令行參數"""
    parser = argparse.ArgumentParser(description="數據分析工具")
    parser.add_argument("-i", "--input", required=True, help="輸入數據文件路徑")
    parser.add_argument("-o", "--output", help="輸出目錄路徑")
    parser.add_argument("-v", "--verbose", action="store_true", help="顯示詳細日誌")
    return parser.parse_args()

def main():
    """主函數"""
    # 解析參數
    args = parse_args()
    
    try:
        # 創建分析器
        analyzer = DataAnalyzer(args.input, args.output)
        
        # 執行分析
        analyzer.run_analysis()
        
    except Exception as e:
        logger.error(f"程序執行失敗: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
