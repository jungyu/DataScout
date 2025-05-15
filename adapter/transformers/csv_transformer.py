#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CSV 到 JSON 轉換器
提供將 CSV 檔案轉換為 Chart.js 格式 JSON 的功能
"""

import os
import json
import pandas as pd
import glob
import random
import logging
import re
import traceback
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

from ..core.base import BaseTransformer
from ..core.exceptions import TransformationError
from ..core.logger import Logger


class CSVTransformer(BaseTransformer):
    """CSV 到 JSON 檔案轉換器基礎類別"""
    
    # 顏色配置
    COLORS = [
        {"backgroundColor": "rgba(75, 192, 192, 0.2)", "borderColor": "rgba(75, 192, 192, 1)"},
        {"backgroundColor": "rgba(153, 102, 255, 0.2)", "borderColor": "rgba(153, 102, 255, 1)"},
        {"backgroundColor": "rgba(255, 159, 64, 0.2)", "borderColor": "rgba(255, 159, 64, 1)"},
        {"backgroundColor": "rgba(54, 162, 235, 0.2)", "borderColor": "rgba(54, 162, 235, 1)"},
        {"backgroundColor": "rgba(255, 99, 132, 0.2)", "borderColor": "rgba(255, 99, 132, 1)"},
        {"backgroundColor": "rgba(255, 206, 86, 0.2)", "borderColor": "rgba(255, 206, 86, 1)"},
        {"backgroundColor": "rgba(153, 0, 0, 0.2)", "borderColor": "rgba(153, 0, 0, 1)"},
        {"backgroundColor": "rgba(0, 153, 76, 0.2)", "borderColor": "rgba(0, 153, 76, 1)"},
        {"backgroundColor": "rgba(0, 76, 153, 0.2)", "borderColor": "rgba(0, 76, 153, 1)"}
    ]
    
    # 股票圓餅圖顏色
    PIE_COLORS = [
        'rgba(255, 99, 132, 0.8)',
        'rgba(54, 162, 235, 0.8)',
        'rgba(255, 206, 86, 0.8)',
        'rgba(75, 192, 192, 0.8)',
        'rgba(153, 102, 255, 0.8)',
        'rgba(255, 159, 64, 0.8)',
        'rgba(199, 199, 199, 0.8)',
        'rgba(83, 102, 255, 0.8)',
        'rgba(40, 159, 64, 0.8)',
        'rgba(210, 199, 199, 0.8)'
    ]
    
    def __init__(self, config: Dict[str, Any], logger: Optional[Logger] = None):
        """
        初始化轉換器
        
        Args:
            config: 轉換配置，可包含以下選項：
                - input_dir: CSV 檔案目錄
                - output_dir: 輸出 JSON 檔案目錄
                - limit: 限制處理檔案數量
                - pattern: 檔案名稱匹配模式
            logger: 日誌對象
        """
        super().__init__(config, logger)
        
        # 設置默認值
        self.input_dir = Path(self.config.get('input_dir', ''))
        self.output_dir = Path(self.config.get('output_dir', ''))
        self.limit = self.config.get('limit', None)
        self.pattern = self.config.get('pattern', None)
        
        # 確保輸出目錄存在
        os.makedirs(self.output_dir, exist_ok=True)
        
    async def transform(self, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        批次轉換 CSV 檔案為 JSON 格式
        
        Args:
            data: 可選，包含轉換參數的字典
            
        Returns:
            Dict[str, Any]: 轉換結果統計
        """
        if data:
            # 可以從傳入的數據更新配置
            if 'input_dir' in data:
                self.input_dir = Path(data['input_dir'])
            if 'output_dir' in data:
                self.output_dir = Path(data['output_dir'])
                os.makedirs(self.output_dir, exist_ok=True)
            if 'limit' in data:
                self.limit = data['limit']
            if 'pattern' in data:
                self.pattern = data['pattern']
        
        # 尋找所有 CSV 檔案
        csv_files = glob.glob(str(self.input_dir / "*.csv"))
        
        if not csv_files:
            self.logger.warning(f"在 {self.input_dir} 中未找到 CSV 檔案")
            return {"success": False, "message": f"在 {self.input_dir} 中未找到 CSV 檔案", "files_processed": 0}
        
        # 如果有指定匹配模式，進行篩選
        if self.pattern:
            try:
                pattern = re.compile(self.pattern, re.IGNORECASE)
                csv_files = [f for f in csv_files if pattern.search(os.path.basename(f))]
            except re.error as e:
                self.logger.error(f"無效的正則表達式模式: {str(e)}")
                return {"success": False, "message": f"無效的正則表達式模式: {str(e)}", "files_processed": 0}
        
        self.logger.info(f"找到 {len(csv_files)} 個 CSV 檔案")
        
        # 如果有指定限制數量，則隨機選擇檔案
        if self.limit and self.limit < len(csv_files):
            csv_files = random.sample(csv_files, self.limit)
            self.logger.info(f"將處理 {self.limit} 個隨機選擇的檔案")
        
        # 轉換每個檔案
        results = {
            "total": len(csv_files),
            "successful": 0,
            "failed": 0,
            "files": []
        }
        
        for csv_file in csv_files:
            try:
                output_file = await self._transform_file(csv_file)
                if output_file:
                    results["successful"] += 1
                    results["files"].append({
                        "input": csv_file,
                        "output": output_file,
                        "status": "success"
                    })
                else:
                    results["failed"] += 1
                    results["files"].append({
                        "input": csv_file,
                        "status": "failed"
                    })
            except Exception as e:
                self.logger.error(f"處理檔案 {csv_file} 時發生錯誤: {str(e)}")
                results["failed"] += 1
                results["files"].append({
                    "input": csv_file,
                    "status": "failed",
                    "error": str(e)
                })
                
        results["success"] = results["failed"] == 0
        
        self.logger.info(f"已成功轉換 {results['successful']}/{results['total']} 個檔案到 {self.output_dir}")
        
        return results
        
    async def _transform_file(self, csv_path: str) -> Optional[str]:
        """
        將單個 CSV 檔案轉換為 Chart.js 格式的 JSON 檔案
        
        Args:
            csv_path: CSV 檔案路徑
            
        Returns:
            Optional[str]: 輸出的 JSON 檔案路徑，如果轉換失敗則返回 None
        """
        # 此方法將在子類中實作
        raise NotImplementedError("必須在子類中實作 _transform_file 方法")

    def detect_chart_type(self, csv_path: str, df: pd.DataFrame) -> str:
        """
        偵測適合的圖表類型
        
        Args:
            csv_path (str): CSV 檔案路徑
            df (DataFrame): pandas DataFrame
            
        Returns:
            str: 圖表類型
        """
        file_name = os.path.basename(csv_path).lower()
        
        # 檢查是否包含 OHLC 資料 (股票、金融資料)
        if all(col in [c.upper() for c in df.columns] for col in ['OPEN', 'HIGH', 'LOW', 'CLOSE']):
            return "candlestick"  # 蠟燭圖
        
        if all(col.upper() in [c.upper() for c in df.columns] for col in ['Open', 'High', 'Low', 'Close']):
            return "candlestick"  # 蠟燭圖
        
        # 檢查新聞日誌資料 - 使用長條圖或圓餅圖
        if 'news_' in file_name and 'logs' in file_name and 'keyword' in ' '.join(df.columns).lower():
            return "pie"  # 圓餅圖適合關鍵字分布
        
        # 財政/貨幣政策指標分析 - 混合圖表
        if 'stimulus' in file_name or 'easing' in file_name or 'protectionism' in file_name:
            return "bar"  # 長條圖
            
        # 經濟指標 (通常是時間序列資料) - 折線圖
        if 'fred_' in file_name:
            # GDP 或相關資料通常適合長條圖
            if 'gdp' in file_name.lower() or 'debt' in file_name.lower():
                return "bar"
            # 通膨、失業率等適合折線圖
            return "line"
        
        # 匯率資料 - 折線圖
        if 'exchange' in file_name or 'usdtwd' in file_name.lower():
            return "line"
        
        # 價格資料 - 折線圖
        if 'price' in file_name:
            return "line"
            
        # VIX 指數 - 折線圖
        if 'vix' in file_name:
            return "line"
        
        # 債券相關 - 折線圖
        if 'bond' in file_name or 'yield' in file_name:
            return "line"
        
        # 其他資料默認為折線圖
        return "line"

    def find_date_column(self, df: pd.DataFrame) -> Optional[str]:
        """
        查找資料集中的日期欄位
        
        Args:
            df: pandas DataFrame
            
        Returns:
            Optional[str]: 日期欄位名稱，如果未找到則為 None
        """
        possible_date_columns = ['Date', 'DATE', 'date', 'datetime', 'time', 'timestamp', 'Time', 'Timestamp']
        
        for col in possible_date_columns:
            if col in df.columns:
                return col
        
        return None
        
    def convert_ohlc_data(self, df: pd.DataFrame, date_column: str) -> Tuple[List[Dict[str, Any]], List[str]]:
        """
        將 OHLC 資料轉換為 Candlestick 圖表格式
        
        Args:
            df: pandas DataFrame
            date_column: 日期欄位名稱
            
        Returns:
            Tuple[List[Dict[str, Any]], List[str]]: 
                - Chart.js candlestick 資料格式
                - 日期標籤列表
        """
        ohlc_data = []
        
        # 查找 OHLC 欄位
        o_col = h_col = l_col = c_col = None
        
        for col in df.columns:
            if 'open' in col.lower() or col.lower() == 'o':
                o_col = col
            elif 'high' in col.lower() or col.lower() == 'h':
                h_col = col
            elif 'low' in col.lower() or col.lower() == 'l':
                l_col = col
            elif 'close' in col.lower() or col.lower() == 'c':
                c_col = col
        
        # 確保找到所有欄位
        if not all([o_col, h_col, l_col, c_col]):
            return None, []
            
        # 轉換日期
        dates = []
        if pd.api.types.is_datetime64_any_dtype(df[date_column]):
            dates = df[date_column].dt.strftime('%Y-%m-%d').tolist()
        else:
            try:
                df[date_column] = pd.to_datetime(df[date_column])
                dates = df[date_column].dt.strftime('%Y-%m-%d').tolist()
            except:
                dates = df[date_column].astype(str).tolist()
        
        # 建立 OHLC 資料
        for i, row in df.iterrows():
            try:
                data_point = {
                    't': dates[i],
                    'o': float(row[o_col]),
                    'h': float(row[h_col]),
                    'l': float(row[l_col]),
                    'c': float(row[c_col])
                }
                ohlc_data.append(data_point)
            except (ValueError, TypeError):
                continue  # 跳過無效資料
        
        return ohlc_data, dates
