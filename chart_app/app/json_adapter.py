#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
JSON 資料轉換適配器。
提供標準化的 JSON 資料結構，以符合 Chart.js 要求的格式。
"""

import json
import logging
from typing import Dict, Any, List, Union, Optional
from pathlib import Path

# 配置日誌
logger = logging.getLogger("chart_app.json_adapter")

class ChartJSAdapter:
    """
    將標準化的 JSON 資料轉換為 Chart.js 可用格式的適配器類別。
    """
    
    VALID_CHART_TYPES = [
        'line', 'bar', 'radar', 'pie', 'doughnut', 'polarArea', 'bubble', 'scatter',
        'candlestick', 'ohlc', 'sankey', 'barLine', 'ohlcVolume', 'ohlcMaKd'
    ]
    
    def __init__(self, json_data: Union[Dict[str, Any], str, Path]):
        """
        初始化適配器。
        
        Args:
            json_data: JSON 資料，可以是字典、JSON 字符串或 JSON 文件路徑
        """
        self.original_data = self._load_json(json_data)
        self.processed_data = {}
    
    def _load_json(self, source: Union[Dict[str, Any], str, Path]) -> Dict[str, Any]:
        """
        加載 JSON 資料。
        
        Args:
            source: JSON 資料來源
            
        Returns:
            Dict: 解析後的 JSON 資料
        """
        try:
            if isinstance(source, dict):
                return source
            elif isinstance(source, (str, Path)):
                path = Path(source)
                if path.exists() and path.is_file():
                    with open(path, 'r', encoding='utf-8') as f:
                        return json.load(f)
                else:
                    # 嘗試解析字符串
                    return json.loads(source)
            else:
                raise TypeError("無效的 JSON 資料來源類型")
        except Exception as e:
            logger.error(f"JSON 資料載入失敗: {str(e)}")
            return {}
    
    def validate_chart_structure(self) -> bool:
        """
        驗證 JSON 資料是否符合 Chart.js 要求的結構。
        
        基本要求:
        - 必須有 'labels' 和 'datasets' 欄位
        - datasets 必須是一個列表，且每個元素都有 'data' 欄位
        
        Returns:
            bool: 驗證結果
        """
        data = self.original_data
        
        # 檢查基本結構
        if not isinstance(data, dict):
            logger.error("JSON 資料必須是一個字典")
            return False
        
        # 檢查 type (可選)
        if 'type' in data and data['type'] not in self.VALID_CHART_TYPES:
            logger.error(f"圖表類型 '{data['type']}' 無效，有效的類型: {', '.join(self.VALID_CHART_TYPES)}")
            return False
        
        # 檢查必要欄位
        if 'datasets' not in data:
            logger.error("JSON 資料缺少必要的 'datasets' 欄位")
            return False
        
        if not isinstance(data['datasets'], list) or len(data['datasets']) == 0:
            logger.error("'datasets' 必須是一個非空列表")
            return False
        
        # 檢查每個數據集
        for i, dataset in enumerate(data['datasets']):
            if not isinstance(dataset, dict):
                logger.error(f"datasets[{i}] 必須是一個字典")
                return False
            
            if 'data' not in dataset:
                logger.error(f"datasets[{i}] 缺少必要的 'data' 欄位")
                return False
            
            if not isinstance(dataset['data'], list):
                logger.error(f"datasets[{i}]['data'] 必須是一個列表")
                return False
        
        # 散點圖和氣泡圖使用特殊的數據格式，需要特別檢查
        chart_type = data.get('type', '')
        if chart_type in ['scatter', 'bubble']:
            for i, dataset in enumerate(data['datasets']):
                for j, point in enumerate(dataset['data']):
                    if not isinstance(point, dict) or 'x' not in point or 'y' not in point:
                        logger.error(f"datasets[{i}]['data'][{j}] 必須是包含 'x' 和 'y' 的字典")
                        return False
                    if chart_type == 'bubble' and 'r' not in point:
                        logger.error(f"氣泡圖的 datasets[{i}]['data'][{j}] 必須包含 'r' (半徑) 欄位")
                        return False
        
        return True
    
    def convert_to_chartjs(self) -> Dict[str, Any]:
        """
        確保 JSON 資料符合 Chart.js 要求的格式。
        
        Returns:
            Dict: Chart.js 格式的資料
        """
        if not self.validate_chart_structure():
            # 如果驗證失敗，返回一個基本的空結構
            return {
                "labels": [],
                "datasets": [{
                    "label": "無效資料",
                    "data": [],
                    "backgroundColor": "rgba(200, 200, 200, 0.5)",
                    "borderColor": "rgba(200, 200, 200, 1.0)",
                    "borderWidth": 1
                }],
                "chartTitle": "錯誤: 無效的 JSON 資料格式"
            }
        
        # 複製原始資料
        result = self.original_data.copy()
        
        # 確保有 labels 欄位
        if 'labels' not in result:
            # 如果沒有提供 labels，從資料中生成
            dataset_length = len(result['datasets'][0]['data'])
            result['labels'] = [f"項目 {i+1}" for i in range(dataset_length)]
        
        # 確保每個數據集都有必要的屬性
        colors = [
            "rgba(75, 192, 192, 0.6)",   # 綠松石色
            "rgba(153, 102, 255, 0.6)",  # 紫色
            "rgba(255, 159, 64, 0.6)",   # 橙色
            "rgba(54, 162, 235, 0.6)",   # 藍色
            "rgba(255, 99, 132, 0.6)",   # 粉色
            "rgba(255, 206, 86, 0.6)"    # 黃色
        ]
        
        for i, dataset in enumerate(result['datasets']):
            color_index = i % len(colors)
            color = colors[color_index]
            
            # 添加標籤（如果缺失）
            if 'label' not in dataset:
                dataset['label'] = f"數據集 {i+1}"
            
            # 添加顏色（如果缺失）
            if 'backgroundColor' not in dataset:
                dataset['backgroundColor'] = color
            if 'borderColor' not in dataset:
                dataset['borderColor'] = color.replace("0.6", "1.0")
            if 'borderWidth' not in dataset:
                dataset['borderWidth'] = 1
        
        # 添加圖表標題（如果缺失）
        if 'chartTitle' not in result:
            result['chartTitle'] = "圖表"
        
        self.processed_data = result
        return result
    
    def save_to_file(self, file_path: Union[str, Path]) -> bool:
        """
        將處理後的資料保存到 JSON 文件。
        
        Args:
            file_path: 保存路徑
            
        Returns:
            bool: 保存結果
        """
        try:
            data = self.processed_data if self.processed_data else self.convert_to_chartjs()
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"保存 JSON 文件失敗: {str(e)}")
            return False
