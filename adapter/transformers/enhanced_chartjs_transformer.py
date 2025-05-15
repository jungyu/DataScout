#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
增強版 CSV 到 JSON 轉換器
依據檔案類型選擇適合的圖表類型，將 CSV 檔案轉換為 Chart.js 格式的 JSON 檔案
"""

import os
import json
import pandas as pd
import re
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from .csv_transformer import CSVTransformer


class EnhancedChartJSTransformer(CSVTransformer):
    """增強版 CSV 到 Chart.js JSON 轉換器"""
    
    async def _transform_file(self, csv_path: str) -> Optional[str]:
        """
        將 CSV 檔案轉換為 Chart.js 格式的 JSON 檔案，具有增強的圖表類型檢測
        
        Args:
            csv_path (str): CSV 檔案路徑
            
        Returns:
            str: 輸出的 JSON 檔案路徑，如果轉換失敗則返回 None
        """
        chart_data = None  # 初始化圖表資料變數
        
        try:
            # 讀取 CSV 檔案
            df = pd.read_csv(csv_path)
            
            # 檢查是否有資料
            if df.empty:
                self.logger.warning(f"檔案 {csv_path} 沒有資料，已跳過")
                return None
                
            # 取得檔案基本名稱
            base_name = os.path.basename(csv_path)
            file_name = os.path.splitext(base_name)[0]
            output_path = os.path.join(self.output_dir, f"{file_name}.json")
            
            # 檢測日期欄位
            date_column = self.find_date_column(df)
                
            # 偵測圖表類型
            chart_type = self.detect_chart_type(csv_path, df)
            
            # 設置標籤資料
            labels = []
            if date_column is None and len(df.columns) > 0:
                labels = df.iloc[:, 0].astype(str).tolist()
            elif date_column is not None:
                # 如果有日期欄位，將其轉換為字串格式
                if pd.api.types.is_datetime64_any_dtype(df[date_column]):
                    labels = df[date_column].dt.strftime('%Y-%m-%d').tolist()
                else:
                    try:
                        df[date_column] = pd.to_datetime(df[date_column])
                        labels = df[date_column].dt.strftime('%Y-%m-%d').tolist()
                    except:
                        labels = df[date_column].astype(str).tolist()
            else:
                # 如果沒有適合的欄位，使用索引作為標籤
                labels = [str(i+1) for i in range(len(df))]
                
            # 根據圖表類型處理資料
            if chart_type == "candlestick" and date_column is not None:
                ohlc_data, dates = self.convert_ohlc_data(df, date_column)
                
                if ohlc_data:
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
                else:
                    chart_type = "line"  # 備用選項，如果無法處理蠟燭圖
            
            # 如果是圓餅圖類型
            elif chart_type == "pie":
                # 查找適合作為類別和數值的欄位
                category_col = None
                value_col = None
                
                # 嘗試找到類別欄位（通常是字符串類型）
                string_cols = df.select_dtypes(include=['object']).columns
                if len(string_cols) > 0 and date_column not in string_cols:
                    for col in string_cols:
                        if col.lower() in ['keyword', 'category', 'name', 'type', 'item']:
                            category_col = col
                            break
                    if category_col is None and len(string_cols) > 0:
                        category_col = string_cols[0]
                
                # 嘗試找到數值欄位
                numeric_cols = df.select_dtypes(include=['number']).columns
                if len(numeric_cols) > 0:
                    for col in numeric_cols:
                        if col.lower() in ['count', 'value', 'amount', 'total']:
                            value_col = col
                            break
                    if value_col is None and len(numeric_cols) > 0:
                        value_col = numeric_cols[0]
                
                if category_col and value_col:
                    # 準備圓餅圖資料
                    categories = df[category_col].tolist()
                    values = df[value_col].tolist()
                    
                    # 確保顏色足夠
                    pie_colors = self.PIE_COLORS
                    while len(pie_colors) < len(categories):
                        pie_colors = pie_colors + self.PIE_COLORS
                    
                    chart_data = {
                        "type": "pie",
                        "data": {
                            "labels": categories,
                            "datasets": [{
                                "data": values,
                                "backgroundColor": pie_colors[:len(categories)],
                                "hoverOffset": 4
                            }]
                        },
                        "options": {
                            "responsive": True,
                            "plugins": {
                                "title": {
                                    "display": True,
                                    "text": file_name.replace("_", " ")
                                },
                                "legend": {
                                    "position": "right"
                                }
                            }
                        }
                    }
                else:
                    chart_type = "bar"  # 備用選項，如果無法處理圓餅圖
            
            # 如果沒有特殊處理或處理失敗，使用標準圖表格式（線圖或長條圖）
            if chart_data is None:
                # 準備資料集
                datasets = []
                numeric_cols = df.select_dtypes(include=['number']).columns
                
                # 排除日期列（如果它是數值型的）
                if date_column and date_column in numeric_cols:
                    numeric_cols = [col for col in numeric_cols if col != date_column]
                    
                # 為每個數值欄位建立資料集
                for i, col in enumerate(numeric_cols[:8]):  # 最多取8個欄位
                    color_idx = i % len(self.COLORS)
                    color = self.COLORS[color_idx]
                    
                    # 檢查是否有 NaN 值
                    data = df[col].tolist()
                    if any(pd.isna(x) for x in data):
                        # 填充 NaN 值
                        data = [None if pd.isna(x) else x for x in data]
                    
                    dataset = {
                        "label": col,
                        "data": data,
                        "backgroundColor": color["backgroundColor"],
                        "borderColor": color["borderColor"],
                        "borderWidth": 1
                    }
                    
                    # 為長條圖添加一些特殊配置
                    if chart_type == "bar":
                        dataset["barPercentage"] = 0.8
                        dataset["categoryPercentage"] = 0.9
                        
                    datasets.append(dataset)
                
                # 建立 Chart.js JSON 格式
                chart_data = {
                    "type": chart_type,
                    "data": {
                        "labels": labels,
                        "datasets": datasets
                    },
                    "options": {
                        "responsive": True,
                        "plugins": {
                            "title": {
                                "display": True,
                                "text": file_name.replace("_", " ")
                            },
                            "legend": {
                                "position": "top"
                            },
                            "tooltip": {
                                "mode": "index",
                                "intersect": False
                            }
                        }
                    }
                }
            
            # 寫入 JSON 檔案
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(chart_data, f, ensure_ascii=False, indent=2)
                
            self.logger.info(f"已成功轉換並儲存: {output_path} (圖表類型: {chart_data['type']})")
            return output_path
            
        except Exception as e:
            self.logger.error(f"轉換檔案 {csv_path} 時發生錯誤: {str(e)}")
            self.logger.debug(traceback.format_exc())
            return None
