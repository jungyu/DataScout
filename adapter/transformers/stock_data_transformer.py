#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
特化版股票 CSV 到 JSON 轉換器
專為處理股票數據、匯率、商品價格等金融數據設計
"""

import os
import json
import pandas as pd
import re
import traceback
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from .csv_transformer import CSVTransformer


class StockDataTransformer(CSVTransformer):
    """特化版股票 CSV 到 JSON 轉換器"""
    
    async def transform(self, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        批次轉換股票相關 CSV 檔案為 JSON 格式
        
        Args:
            data: 可選，包含轉換參數的字典
            
        Returns:
            Dict[str, Any]: 轉換結果統計
        """
        # 設置預設的股票資料匹配模式
        if not self.pattern:
            self.pattern = r'(price|stock|exchange|rate|Gold|VIX|SP500|AAPL|Copper|USDTWD)'
            
        # 使用父類別的轉換方法
        return await super().transform(data)
    
    async def _transform_file(self, csv_path: str) -> Optional[str]:
        """
        將股票、匯率、商品價格等金融數據的 CSV 檔案轉換為 Chart.js 格式的 JSON 檔案
        
        Args:
            csv_path (str): CSV 檔案路徑
            
        Returns:
            str: 輸出的 JSON 檔案路徑，如果轉換失敗則返回 None
        """
        try:
            base_name = os.path.basename(csv_path)
            file_name = os.path.splitext(base_name)[0]
            output_path = os.path.join(self.output_dir, f"{file_name}.json")
            
            # 讀取 CSV 檔案的前幾行來分析結構
            with open(csv_path, 'r', encoding='utf-8') as f:
                first_lines = [next(f) for _ in range(5)]
                
            # 檢查結構類型
            skip_rows = 0
            if any('Ticker' in line for line in first_lines):
                # 特殊的股票資料結構 (如 AAPL_stock_data 檔案)
                skip_rows = 3
                
            # 讀取 CSV 檔案，跳過必要的行
            df = pd.read_csv(csv_path, skiprows=skip_rows)
            
            # 檢查是否有資料
            if df.empty:
                self.logger.warning(f"檔案 {csv_path} 沒有資料，已跳過")
                return None
            
            # 查找日期欄位
            date_column = self.find_date_column(df)
            
            if date_column is None:
                self.logger.warning(f"檔案 {csv_path} 中找不到日期欄位，使用第一列作為日期")
                if len(df.columns) > 0:
                    date_column = df.columns[0]
                else:
                    self.logger.error(f"檔案 {csv_path} 沒有欄位")
                    return None
                    
            # 轉換日期列
            try:
                df[date_column] = pd.to_datetime(df[date_column])
                labels = df[date_column].dt.strftime('%Y-%m-%d').tolist()
            except:
                labels = df[date_column].astype(str).tolist()
                
            # 檢查是否有 OHLC 資料 (股票類資料)
            is_ohlc = False
            ohlc_cols = {"open": None, "high": None, "low": None, "close": None}
            
            for col in df.columns:
                col_lower = col.lower()
                if "open" in col_lower and ohlc_cols["open"] is None:
                    ohlc_cols["open"] = col
                elif "high" in col_lower and ohlc_cols["high"] is None:
                    ohlc_cols["high"] = col
                elif "low" in col_lower and ohlc_cols["low"] is None:
                    ohlc_cols["low"] = col
                elif "close" in col_lower and ohlc_cols["close"] is None:
                    ohlc_cols["close"] = col
            
            # 檢查是否找到所有 OHLC 欄位
            is_ohlc = all(ohlc_cols.values())
            chart_data = None
            
            # 準備 Chart.js 資料
            if is_ohlc:
                # 準備 OHLC 資料 (蠟燭圖)
                ohlc_data = []
                
                for i, row in df.iterrows():
                    try:
                        data_point = {
                            't': labels[i],
                            'o': float(row[ohlc_cols["open"]]),
                            'h': float(row[ohlc_cols["high"]]),
                            'l': float(row[ohlc_cols["low"]]),
                            'c': float(row[ohlc_cols["close"]])
                        }
                        ohlc_data.append(data_point)
                    except (ValueError, TypeError, IndexError) as e:
                        self.logger.debug(f"跳過無效資料點 {i}: {str(e)}")
                        continue
                        
                # 建立 candlestick 圖表資料
                chart_data = {
                    "type": "candlestick",
                    "data": {
                        "datasets": [{
                            "label": file_name.replace("_", " "),
                            "data": ohlc_data,
                            "color": {
                                "up": "rgba(75, 192, 192, 1)",  # 上漲 - 綠色
                                "down": "rgba(255, 99, 132, 1)",  # 下跌 - 紅色
                                "unchanged": "rgba(110, 110, 110, 1)",  # 持平 - 灰色
                            }
                        }]
                    },
                    "options": {
                        "responsive": True,
                        "title": {
                            "display": True,
                            "text": file_name.replace("_", " ")
                        },
                        "scales": {
                            "x": {
                                "type": "time",
                                "time": {
                                    "unit": "day"
                                }
                            }
                        }
                    }
                }
                
                # 考慮額外添加一個簡化的價格線
                if "close" in ohlc_cols and ohlc_cols["close"] is not None:
                    price_line_data = []
                    for i, row in df.iterrows():
                        try:
                            price_line_data.append({
                                't': labels[i],
                                'y': float(row[ohlc_cols["close"]])
                            })
                        except (ValueError, TypeError, IndexError):
                            continue
                    
                    # 新增另一個 JSON 檔案，作為線圖呈現
                    price_output_path = os.path.join(self.output_dir, f"{file_name}_line.json")
                    price_chart_data = {
                        "type": "line",
                        "data": {
                            "datasets": [{
                                "label": f"{file_name} 價格走勢",
                                "data": price_line_data,
                                "borderColor": "rgba(75, 192, 192, 1)",
                                "backgroundColor": "rgba(75, 192, 192, 0.2)",
                                "tension": 0.1
                            }]
                        },
                        "options": {
                            "responsive": True,
                            "title": {
                                "display": True,
                                "text": f"{file_name} 價格走勢"
                            },
                            "scales": {
                                "x": {
                                    "type": "time",
                                    "time": {
                                        "unit": "day"
                                    }
                                }
                            }
                        }
                    }
                    
                    with open(price_output_path, 'w', encoding='utf-8') as f:
                        json.dump(price_chart_data, f, ensure_ascii=False, indent=2)
                    self.logger.info(f"已額外儲存價格線圖: {price_output_path}")
                
            else:
                # 使用一般折線圖顯示價格或其他數據
                numeric_cols = df.select_dtypes(include=['number']).columns
                
                # 排除日期列（如果它是數值型的）
                if date_column in numeric_cols:
                    numeric_cols = [col for col in numeric_cols if col != date_column]
                    
                if not numeric_cols.empty:
                    # 準備資料集
                    datasets = []
                    for i, col in enumerate(numeric_cols[:5]):  # 最多取5個欄位
                        color_idx = i % len(self.COLORS)
                        color = self.COLORS[color_idx]
                        
                        # 檢查是否有 NaN 值
                        data = df[col].tolist()
                        if any(pd.isna(x) for x in data):
                            # 填充 NaN 值
                            data = [None if pd.isna(x) else x for x in data]
                            
                        datasets.append({
                            "label": col,
                            "data": data,
                            "backgroundColor": color["backgroundColor"],
                            "borderColor": color["borderColor"],
                            "borderWidth": 1,
                            "tension": 0.1  # 平滑曲線
                        })
                    
                    # 建立 Chart.js JSON 格式
                    chart_data = {
                        "type": "line",  # 使用折線圖顯示價格走勢
                        "data": {
                            "labels": labels,
                            "datasets": datasets
                        },
                        "options": {
                            "responsive": True,
                            "title": {
                                "display": True,
                                "text": file_name.replace("_", " ")
                            }
                        }
                    }
                else:
                    self.logger.warning(f"檔案 {csv_path} 中沒有數值欄位，無法創建圖表")
                    return None
                    
            # 寫入 JSON 檔案
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(chart_data, f, ensure_ascii=False, indent=2)
                
            self.logger.info(f"已成功轉換並儲存: {output_path} (圖表類型: {chart_data['type']})")
            return output_path
            
        except Exception as e:
            self.logger.error(f"轉換檔案 {csv_path} 時發生錯誤: {str(e)}")
            self.logger.debug(traceback.format_exc())
            return None
