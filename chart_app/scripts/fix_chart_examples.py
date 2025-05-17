#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
範例圖表檔案檢查與修復工具

此腳本檢查 chart_app 專案中的範例 JSON 檔案，
確保它們符合 Chart.js 的格式要求並修復常見的問題。
主要用於解決圖表未渲染或未出現在列表的問題。

用法:
    python fix_chart_examples.py [--dry-run] [--verbose] [--create-missing]

選項:
    --dry-run       只檢查問題，不進行修復
    --verbose       顯示詳細日誌
    --create-missing 建立缺失的範例檔案
"""

import os
import re
import sys
import json
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set


# 設定日誌記錄
def setup_logging(verbose: bool = False) -> None:
    """設定日誌層級和格式"""
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )


def get_examples_dir() -> Path:
    """獲取範例目錄路徑"""
    # 嘗試從當前目錄往上找專案根目錄
    current_dir = Path.cwd()
    
    # 嘗試從腳本位置往上找專案根目錄
    script_dir = Path(__file__).resolve().parent
    
    # 優先檢查腳本相對位置
    if (script_dir.parent / "static" / "examples").exists():
        return script_dir.parent / "static" / "examples"
    
    # 其次檢查當前工作目錄相對位置
    if (current_dir / "static" / "examples").exists():
        return current_dir / "static" / "examples"
    
    if (current_dir.parent / "static" / "examples").exists():
        return current_dir.parent / "static" / "examples"
    
    # 硬編碼的路徑作為最後選擇
    hardcoded_path = Path("/Users/aaron/Projects/DataScout/chart_app/static/examples")
    if hardcoded_path.exists():
        return hardcoded_path
    
    # 如果都找不到，預設在當前目錄下建立
    logging.warning("找不到範例目錄，將在當前目錄建立 'examples' 資料夾")
    examples_dir = Path("examples")
    examples_dir.mkdir(exist_ok=True)
    return examples_dir


def validate_chart_json(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    驗證圖表 JSON 是否符合 Chart.js 格式
    
    Args:
        data: JSON 內容
        
    Returns:
        是否有效, 錯誤列表
    """
    errors = []
    
    # 檢查類型是否存在且有效
    valid_types = ['line', 'bar', 'pie', 'radar', 'doughnut', 'polarArea', 
                   'bubble', 'scatter', 'candlestick', 'ohlc', 'sankey']
    
    if 'type' not in data:
        errors.append("缺少 'type' 欄位")
    elif data['type'] not in valid_types:
        errors.append(f"無效的圖表類型: {data['type']}，有效類型: {', '.join(valid_types)}")
    
    # 檢查 labels 是否存在且是列表
    if 'labels' not in data:
        errors.append("缺少 'labels' 欄位")
    elif not isinstance(data['labels'], list):
        errors.append("'labels' 必須是陣列")
    
    # 檢查 datasets 是否存在且格式正確
    if 'datasets' not in data:
        errors.append("缺少 'datasets' 欄位")
    elif not isinstance(data['datasets'], list) or len(data['datasets']) == 0:
        errors.append("'datasets' 必須是非空陣列")
    else:
        # 檢查每個數據集
        for i, dataset in enumerate(data['datasets']):
            if 'data' not in dataset:
                errors.append(f"數據集 #{i+1} 缺少 'data' 欄位")
            elif not isinstance(dataset['data'], list):
                errors.append(f"數據集 #{i+1} 的 'data' 必須是陣列")
            
            # 檢查標籤
            if 'label' not in dataset:
                logging.warning(f"數據集 #{i+1} 缺少 'label' 欄位")
    
    # 檢查 chartTitle 是否存在
    if 'chartTitle' not in data:
        logging.warning("缺少 'chartTitle' 欄位")
    
    return len(errors) == 0, errors


def fix_chart_json(data: Dict[str, Any], filename: str) -> Dict[str, Any]:
    """
    修復圖表 JSON 中的常見問題
    
    Args:
        data: JSON 內容
        filename: 檔案名稱（用於猜測圖表類型）
        
    Returns:
        修復後的 JSON 內容
    """
    fixed_data = data.copy()
    
    # 如果沒有 type，從檔名猜測
    if 'type' not in fixed_data:
        chart_type = guess_chart_type_from_filename(filename)
        fixed_data['type'] = chart_type
        logging.info(f"已從檔名猜測圖表類型: {chart_type}")
    
    # 確保 datasets 存在且是列表
    if 'datasets' not in fixed_data or not isinstance(fixed_data['datasets'], list):
        if 'data' in fixed_data and isinstance(fixed_data['data'], dict) and 'datasets' in fixed_data['data']:
            fixed_data['datasets'] = fixed_data['data']['datasets']
            logging.info("已從 data.datasets 移動數據集")
        else:
            fixed_data['datasets'] = [{'label': '數據', 'data': []}]
            logging.info("已創建預設數據集")
    
    # 確保每個數據集都有 label 和 data
    for i, dataset in enumerate(fixed_data['datasets']):
        if 'label' not in dataset:
            dataset['label'] = f"數據系列 {i+1}"
            logging.info(f"已為數據集 #{i+1} 添加預設標籤")
        
        if 'data' not in dataset:
            dataset['data'] = []
            logging.warning(f"已為數據集 #{i+1} 添加空數據陣列")
    
    # 確保 labels 存在
    if 'labels' not in fixed_data:
        if 'data' in fixed_data and isinstance(fixed_data['data'], dict) and 'labels' in fixed_data['data']:
            fixed_data['labels'] = fixed_data['data']['labels']
            logging.info("已從 data.labels 移動標籤")
        else:
            # 建立預設標籤，長度與第一個數據集一致
            if fixed_data['datasets'] and 'data' in fixed_data['datasets'][0]:
                data_length = len(fixed_data['datasets'][0]['data'])
                fixed_data['labels'] = [f"項目 {i+1}" for i in range(data_length)]
                logging.info(f"已建立 {data_length} 個預設標籤")
            else:
                fixed_data['labels'] = ["項目 1", "項目 2", "項目 3", "項目 4", "項目 5"]
                logging.info("已建立 5 個預設標籤")
    
    # 確保 chartTitle 存在
    if 'chartTitle' not in fixed_data:
        # 從檔名生成標題
        title = filename.replace('example_', '').replace('_', ' ').replace('.json', '')
        fixed_data['chartTitle'] = title.title()
        logging.info(f"已添加標題: {fixed_data['chartTitle']}")
    
    # 特殊圖表類型處理
    if fixed_data['type'] in ['pie', 'doughnut', 'polarArea']:
        # 確保有顏色
        for dataset in fixed_data['datasets']:
            if 'backgroundColor' not in dataset:
                dataset['backgroundColor'] = [
                    "rgba(255, 99, 132, 0.6)",
                    "rgba(54, 162, 235, 0.6)",
                    "rgba(255, 206, 86, 0.6)",
                    "rgba(75, 192, 192, 0.6)",
                    "rgba(153, 102, 255, 0.6)",
                    "rgba(255, 159, 64, 0.6)",
                    "rgba(201, 203, 207, 0.6)"
                ]
                logging.info("已添加預設背景顏色")
            
            # 確保數據長度與標籤一致
            if len(dataset['data']) != len(fixed_data['labels']):
                logging.warning(f"數據長度 ({len(dataset['data'])}) 與標籤長度 ({len(fixed_data['labels'])}) 不一致")
                
                # 如果數據比標籤少，補足數據
                if len(dataset['data']) < len(fixed_data['labels']):
                    extra_data = [0] * (len(fixed_data['labels']) - len(dataset['data']))
                    dataset['data'].extend(extra_data)
                    logging.info(f"已將數據長度從 {len(dataset['data']) - len(extra_data)} 擴充到 {len(dataset['data'])}")
                # 如果數據比標籤多，截斷數據
                elif len(dataset['data']) > len(fixed_data['labels']):
                    dataset['data'] = dataset['data'][:len(fixed_data['labels'])]
                    logging.info(f"已將數據長度從 {len(dataset['data'])} 縮減到 {len(fixed_data['labels'])}")
    
    return fixed_data


def guess_chart_type_from_filename(filename: str) -> str:
    """從檔名猜測圖表類型"""
    filename = filename.lower()
    
    if 'line' in filename:
        return 'line'
    elif 'bar' in filename:
        return 'bar'
    elif 'pie' in filename:
        return 'pie'
    elif 'doughnut' in filename:
        return 'doughnut'
    elif 'radar' in filename:
        return 'radar'
    elif 'polar' in filename:
        return 'polarArea'
    elif 'bubble' in filename:
        return 'bubble'
    elif 'scatter' in filename:
        return 'scatter'
    elif 'candlestick' in filename:
        return 'candlestick'
    elif 'ohlc' in filename:
        return 'ohlc'
    elif 'sankey' in filename:
        return 'sankey'
    else:
        return 'line'  # 預設為折線圖


def create_chart_templates() -> Dict[str, Dict[str, Any]]:
    """建立各種圖表類型的範例模板"""
    templates = {}
    
    # 折線圖模板
    templates['line'] = {
        "type": "line",
        "labels": ["一月", "二月", "三月", "四月", "五月", "六月"],
        "datasets": [
            {
                "label": "銷售額",
                "data": [12, 19, 3, 5, 2, 3],
                "fill": False,
                "backgroundColor": "rgba(75, 192, 192, 0.6)",
                "borderColor": "rgba(75, 192, 192, 1)",
                "borderWidth": 1,
                "tension": 0.1
            }
        ],
        "chartTitle": "月度銷售趨勢"
    }
    
    # 長條圖模板
    templates['bar'] = {
        "type": "bar",
        "labels": ["一月", "二月", "三月", "四月", "五月", "六月"],
        "datasets": [
            {
                "label": "收入",
                "data": [65, 59, 80, 81, 56, 55],
                "backgroundColor": [
                    "rgba(255, 99, 132, 0.6)",
                    "rgba(54, 162, 235, 0.6)",
                    "rgba(255, 206, 86, 0.6)",
                    "rgba(75, 192, 192, 0.6)",
                    "rgba(153, 102, 255, 0.6)",
                    "rgba(255, 159, 64, 0.6)"
                ],
                "borderColor": [
                    "rgba(255, 99, 132, 1)",
                    "rgba(54, 162, 235, 1)",
                    "rgba(255, 206, 86, 1)",
                    "rgba(75, 192, 192, 1)",
                    "rgba(153, 102, 255, 1)",
                    "rgba(255, 159, 64, 1)"
                ],
                "borderWidth": 1
            }
        ],
        "chartTitle": "收入統計"
    }
    
    # 圓餅圖模板
    templates['pie'] = {
        "type": "pie",
        "labels": ["台北", "台中", "高雄", "台南", "新竹"],
        "datasets": [
            {
                "label": "銷售分布",
                "data": [35, 25, 20, 15, 5],
                "backgroundColor": [
                    "rgba(255, 99, 132, 0.6)",
                    "rgba(54, 162, 235, 0.6)",
                    "rgba(255, 206, 86, 0.6)",
                    "rgba(75, 192, 192, 0.6)",
                    "rgba(153, 102, 255, 0.6)"
                ],
                "borderColor": [
                    "rgba(255, 99, 132, 1.0)",
                    "rgba(54, 162, 235, 1.0)",
                    "rgba(255, 206, 86, 1.0)",
                    "rgba(75, 192, 192, 1.0)",
                    "rgba(153, 102, 255, 1.0)"
                ],
                "borderWidth": 1
            }
        ],
        "chartTitle": "各地區銷售佔比"
    }
    
    # 環狀圖模板
    templates['doughnut'] = {
        "type": "doughnut",
        "labels": ["人事", "行銷", "研發", "生產", "行政"],
        "datasets": [
            {
                "label": "預算分配",
                "data": [40, 20, 15, 15, 10],
                "backgroundColor": [
                    "rgba(255, 99, 132, 0.6)",
                    "rgba(54, 162, 235, 0.6)",
                    "rgba(255, 206, 86, 0.6)",
                    "rgba(75, 192, 192, 0.6)",
                    "rgba(153, 102, 255, 0.6)"
                ],
                "borderColor": [
                    "rgba(255, 99, 132, 1.0)",
                    "rgba(54, 162, 235, 1.0)",
                    "rgba(255, 206, 86, 1.0)",
                    "rgba(75, 192, 192, 1.0)",
                    "rgba(153, 102, 255, 1.0)"
                ],
                "borderWidth": 1
            }
        ],
        "chartTitle": "部門預算分配比例"
    }
    
    # 雷達圖模板
    templates['radar'] = {
        "type": "radar",
        "labels": ["攻擊", "防禦", "速度", "能力", "體力", "智力"],
        "datasets": [
            {
                "label": "玩家A",
                "data": [80, 60, 75, 90, 65, 85],
                "backgroundColor": "rgba(255, 99, 132, 0.2)",
                "borderColor": "rgba(255, 99, 132, 1)",
                "borderWidth": 1
            },
            {
                "label": "玩家B",
                "data": [65, 85, 70, 60, 90, 70],
                "backgroundColor": "rgba(54, 162, 235, 0.2)",
                "borderColor": "rgba(54, 162, 235, 1)",
                "borderWidth": 1
            }
        ],
        "chartTitle": "玩家能力對比"
    }
    
    # 極座標模板
    templates['polarArea'] = {
        "type": "polarArea",
        "labels": ["研發", "行銷", "銷售", "客服", "管理"],
        "datasets": [
            {
                "label": "部門預算分配",
                "data": [40, 25, 20, 10, 5],
                "backgroundColor": [
                    "rgba(255, 99, 132, 0.6)",
                    "rgba(54, 162, 235, 0.6)",
                    "rgba(255, 206, 86, 0.6)",
                    "rgba(75, 192, 192, 0.6)",
                    "rgba(153, 102, 255, 0.6)"
                ],
                "borderColor": [
                    "rgba(255, 99, 132, 1.0)",
                    "rgba(54, 162, 235, 1.0)",
                    "rgba(255, 206, 86, 1.0)",
                    "rgba(75, 192, 192, 1.0)",
                    "rgba(153, 102, 255, 1.0)"
                ],
                "borderWidth": 1
            }
        ],
        "chartTitle": "公司資源分配"
    }
    
    # 散點圖模板
    templates['scatter'] = {
        "type": "scatter",
        "labels": [],  # 散點圖不使用 labels
        "datasets": [
            {
                "label": "人口與GDP關係",
                "data": [
                    {"x": 10, "y": 20},
                    {"x": 15, "y": 25},
                    {"x": 20, "y": 40},
                    {"x": 25, "y": 30},
                    {"x": 30, "y": 50},
                    {"x": 35, "y": 45},
                    {"x": 40, "y": 60}
                ],
                "backgroundColor": "rgba(75, 192, 192, 0.6)"
            }
        ],
        "chartTitle": "散點圖示例"
    }
    
    # 氣泡圖模板
    templates['bubble'] = {
        "type": "bubble",
        "labels": [],  # 氣泡圖不使用 labels
        "datasets": [
            {
                "label": "城市發展指標",
                "data": [
                    {"x": 20, "y": 30, "r": 15},
                    {"x": 40, "y": 10, "r": 10},
                    {"x": 15, "y": 15, "r": 20},
                    {"x": 30, "y": 50, "r": 30},
                    {"x": 50, "y": 40, "r": 12},
                    {"x": 60, "y": 80, "r": 25}
                ],
                "backgroundColor": "rgba(255, 99, 132, 0.6)",
                "borderColor": "rgba(255, 99, 132, 1)"
            }
        ],
        "chartTitle": "城市發展分析"
    }
    
    # K線圖模板
    templates['candlestick'] = {
        "type": "candlestick",
        "labels": ["1/1", "1/2", "1/3", "1/4", "1/5", "1/6", "1/7", "1/8", "1/9", "1/10"],
        "datasets": [
            {
                "label": "股價",
                "data": [
                    {"t": "2023-01-01", "o": 150, "h": 160, "l": 145, "c": 155},
                    {"t": "2023-01-02", "o": 155, "h": 165, "l": 150, "c": 160},
                    {"t": "2023-01-03", "o": 160, "h": 168, "l": 155, "c": 163},
                    {"t": "2023-01-04", "o": 163, "h": 170, "l": 160, "c": 167},
                    {"t": "2023-01-05", "o": 167, "h": 175, "l": 165, "c": 172},
                    {"t": "2023-01-06", "o": 172, "h": 178, "l": 170, "c": 175},
                    {"t": "2023-01-07", "o": 175, "h": 180, "l": 170, "c": 172},
                    {"t": "2023-01-08", "o": 172, "h": 175, "l": 165, "c": 168},
                    {"t": "2023-01-09", "o": 168, "h": 175, "l": 165, "c": 170},
                    {"t": "2023-01-10", "o": 170, "h": 180, "l": 170, "c": 178}
                ]
            }
        ],
        "chartTitle": "股價走勢"
    }
    
    # OHLC圖模板
    templates['ohlc'] = {
        "type": "ohlc",
        "labels": ["1/1", "1/2", "1/3", "1/4", "1/5", "1/6", "1/7", "1/8", "1/9", "1/10"],
        "datasets": [
            {
                "label": "股價",
                "data": [
                    {"t": "2023-01-01", "o": 150, "h": 160, "l": 145, "c": 155},
                    {"t": "2023-01-02", "o": 155, "h": 165, "l": 150, "c": 160},
                    {"t": "2023-01-03", "o": 160, "h": 168, "l": 155, "c": 163},
                    {"t": "2023-01-04", "o": 163, "h": 170, "l": 160, "c": 167},
                    {"t": "2023-01-05", "o": 167, "h": 175, "l": 165, "c": 172},
                    {"t": "2023-01-06", "o": 172, "h": 178, "l": 170, "c": 175},
                    {"t": "2023-01-07", "o": 175, "h": 180, "l": 170, "c": 172},
                    {"t": "2023-01-08", "o": 172, "h": 175, "l": 165, "c": 168},
                    {"t": "2023-01-09", "o": 168, "h": 175, "l": 165, "c": 170},
                    {"t": "2023-01-10", "o": 170, "h": 180, "l": 170, "c": 178}
                ]
            }
        ],
        "chartTitle": "OHLC 股價走勢"
    }
    
    # 桑基圖模板
    templates['sankey'] = {
        "type": "sankey",
        "labels": ["A", "B", "C", "D", "E", "F"],
        "datasets": [
            {
                "label": "資源流向",
                "data": [
                    {"from": "A", "to": "B", "flow": 10},
                    {"from": "A", "to": "C", "flow": 5},
                    {"from": "B", "to": "D", "flow": 7},
                    {"from": "B", "to": "E", "flow": 3},
                    {"from": "C", "to": "E", "flow": 2},
                    {"from": "C", "to": "F", "flow": 3}
                ]
            }
        ],
        "chartTitle": "資源流向圖"
    }
    
    return templates


def create_missing_examples(examples_dir: Path, missing_examples: List[str], templates: Dict[str, Dict[str, Any]]) -> None:
    """
    建立缺失的範例檔案
    
    Args:
        examples_dir: 範例目錄路徑
        missing_examples: 缺失的範例檔案名稱列表
        templates: 圖表模板
    """
    for filename in missing_examples:
        # 確保文件名有 .json 副檔名
        if not filename.endswith('.json'):
            filename += '.json'
        
        file_path = examples_dir / filename
        
        # 檢查文件是否已存在
        if file_path.exists():
            logging.info(f"檔案已存在，跳過: {filename}")
            continue
        
        # 從檔名猜測圖表類型
        chart_type = guess_chart_type_from_filename(filename)
        
        # 獲取對應類型的模板
        if chart_type in templates:
            template = templates[chart_type].copy()
        else:
            template = templates['line'].copy()  # 預設使用折線圖模板
            template['type'] = chart_type  # 但將類型改為猜測的類型
        
        # 從檔名生成標題
        title = filename.replace('example_', '').replace('_', ' ').replace('.json', '')
        template['chartTitle'] = title.title()
        
        # 根據文件名稱進行特殊處理
        if 'polar_area_market_sectors' in filename:
            template = templates['polarArea'].copy()
            template['labels'] = ["科技", "健康醫療", "金融", "能源", "消費性產品", "工業", "原材料"]
            template['datasets'][0]['data'] = [25, 20, 15, 15, 10, 10, 5]
            template['chartTitle'] = "市場類股分布"
        
        elif 'polar_area_skill_assessment' in filename:
            template = templates['polarArea'].copy()
            template['labels'] = ["領導力", "溝通能力", "技術知識", "團隊合作", "解決問題", "適應能力", "創新思維"]
            template['datasets'][0]['data'] = [8, 7, 9, 8, 7, 6, 8]
            template['chartTitle'] = "技能評估"
            
        elif 'sankey_budget_allocation' in filename:
            template = templates['sankey'].copy()
            template['labels'] = ["收入", "稅收", "薪資", "採購", "營銷", "研發", "行政", "公共服務", "基礎設施", "教育", "醫療"]
            template['datasets'][0]['data'] = [
                {"from": "收入", "to": "稅收", "flow": 30},
                {"from": "收入", "to": "薪資", "flow": 40},
                {"from": "收入", "to": "採購", "flow": 30},
                {"from": "稅收", "to": "公共服務", "flow": 10},
                {"from": "稅收", "to": "基礎設施", "flow": 10},
                {"from": "稅收", "to": "教育", "flow": 5},
                {"from": "稅收", "to": "醫療", "flow": 5}
            ]
            template['chartTitle'] = "預算分配流向"
            
        elif 'sankey_energy_flow' in filename:
            template = templates['sankey'].copy()
            template['labels'] = ["石油", "天然氣", "煤炭", "核能", "再生能源", "運輸", "工業", "住宅", "商業", "電力生產"]
            template['datasets'][0]['data'] = [
                {"from": "石油", "to": "運輸", "flow": 25},
                {"from": "天然氣", "to": "工業", "flow": 15},
                {"from": "天然氣", "to": "住宅", "flow": 10},
                {"from": "煤炭", "to": "電力生產", "flow": 20},
                {"from": "核能", "to": "電力生產", "flow": 15},
                {"from": "再生能源", "to": "電力生產", "flow": 10},
                {"from": "電力生產", "to": "商業", "flow": 15},
                {"from": "電力生產", "to": "住宅", "flow": 20},
                {"from": "電力生產", "to": "工業", "flow": 10}
            ]
            template['chartTitle'] = "能源流向"
            
        elif 'ohlc_hsi' in filename:
            template = templates['ohlc'].copy()
            template['labels'] = [f"5/{i}" for i in range(1, 11)]
            template['datasets'][0]['label'] = "恆生指數"
            template['datasets'][0]['data'] = [
                {"t": f"2023-05-0{i}" if i < 10 else f"2023-05-{i}", 
                 "o": 19500 + i*50, 
                 "h": 19600 + i*60, 
                 "l": 19450 + i*40, 
                 "c": 19550 + i*45} for i in range(1, 11)
            ]
            template['chartTitle'] = "恆生指數走勢"
            
        elif 'ohlc_ma_kd' in filename:
            template = templates['ohlc'].copy()
            template['chartTitle'] = "股價與技術指標"
            if 'aapl' in filename:
                template['datasets'][0]['label'] = "AAPL"
                base_price = 150
            elif 'taiex' in filename:
                template['datasets'][0]['label'] = "台股指數"
                base_price = 16000
            else:
                base_price = 100
                
            # 生成基本 OHLC 數據
            template['datasets'][0]['data'] = [
                {"t": f"2023-05-{i:02d}", 
                "o": base_price + (i-1)*5, 
                "h": base_price + (i-1)*5 + 8, 
                "l": base_price + (i-1)*5 - 5, 
                "c": base_price + i*5} for i in range(1, 21)
            ]
            
            # 添加 MA 和 KD 數據
            template['datasets'].append({
                "label": "MA5",
                "type": "line",
                "data": [base_price + i*5 for i in range(1, 21)],
                "borderColor": "rgba(255, 99, 132, 1)",
                "borderWidth": 1,
                "fill": False
            })
            
            template['datasets'].append({
                "label": "MA10",
                "type": "line",
                "data": [base_price + i*4 for i in range(1, 21)],
                "borderColor": "rgba(54, 162, 235, 1)",
                "borderWidth": 1,
                "fill": False
            })
            
            template['labels'] = [f"5/{i}" for i in range(1, 21)]
            
        elif 'ohlc_tai_volume' in filename:
            template = templates['ohlc'].copy()
            template['chartTitle'] = "股價與成交量"
            
            if 'msft' in filename:
                template['datasets'][0]['label'] = "MSFT"
                base_price = 280
            elif 'tsmc' in filename:
                template['datasets'][0]['label'] = "台積電"
                base_price = 550
            else:
                base_price = 100
            
            # 生成基本 OHLC 數據
            template['datasets'][0]['data'] = [
                {"t": f"2023-05-{i:02d}", 
                "o": base_price + (i-1)*2, 
                "h": base_price + (i-1)*2 + 5, 
                "l": base_price + (i-1)*2 - 3, 
                "c": base_price + i*2} for i in range(1, 21)
            ]
            
            # 添加成交量數據
            template['datasets'].append({
                "label": "成交量",
                "type": "bar",
                "data": [i*1000 for i in range(1, 21)],
                "backgroundColor": "rgba(75, 192, 192, 0.6)",
                "borderColor": "rgba(75, 192, 192, 1)",
                "borderWidth": 1
            })
            
            template['labels'] = [f"5/{i}" for i in range(1, 21)]
            
        # 保存文件
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(template, f, ensure_ascii=False, indent=4)
            
        logging.info(f"已創建範例檔案: {filename}")


def process_chart_files(examples_dir: Path, dry_run: bool = False, create_missing: bool = False) -> None:
    """
    處理圖表檔案目錄中的所有 JSON 檔案
    
    Args:
        examples_dir: 範例檔案目錄
        dry_run: 是否只檢查不修改
        create_missing: 是否創建缺失的範例檔案
    """
    if not examples_dir.exists():
        logging.error(f"目錄不存在: {examples_dir}")
        return
    
    # 檢查所有 JSON 檔案
    json_files = list(examples_dir.glob('*.json'))
    logging.info(f"找到 {len(json_files)} 個 JSON 檔案")
    
    issues_found = False
    issues_fixed = 0
    
    # 提到的問題檔案列表
    mentioned_files = [
        "example_line_fred_unemployment",
        "example_line_Yfinance_Sp500",
        "example_line_chart",
        "example_line_chart_2",
        "example_bar_nikkei_news_count",
        "example_bar_bloomberg_news_count",
        "radar_investment_risk",
        "pie_chart_2",
        "Doughnut_chart",
        "Bubble_Market_analysis",
        "scatter_economic_indicators",
        "candlestick_gold_twd",
        "candlestick_bitcoin_usd"
    ]
    
    # 沒有顯示的檔案列表
    missing_files = [
        "example_polar_area_market_sectors",
        "example_polar_area_skill_assessment",
        "example_sankey_budget_allocation",
        "example_sankey_energy_flow",
        "example_ohlc_hsi",
        "example_ohlc_ma_kd_aapl",
        "example_ohlc_ma_kd_taiex",
        "example_ohlc_tai_volume_msft",
        "example_ohlc_tai_volume_tsmc"
    ]
    
    # 建立一個集合，存儲所有檔名(不含副檔名)
    existing_files = {os.path.splitext(file.name)[0] for file in json_files}
    
    # 檢查是否有提到但不存在的檔案
    not_found_files = [file for file in mentioned_files if file not in existing_files]
    for file in not_found_files:
        logging.warning(f"提到的檔案不存在: {file}.json")
    
    # 檢查是否有應該顯示但沒顯示的檔案
    not_shown_files = [file for file in missing_files if file in existing_files]
    for file in not_shown_files:
        logging.warning(f"檔案存在但未顯示在列表中: {file}.json")
    
    # 待建立的缺失檔案
    to_create_files = [file for file in missing_files if file not in existing_files]
    if to_create_files and create_missing:
        logging.info(f"將創建 {len(to_create_files)} 個缺失的範例檔案")
        templates = create_chart_templates()
        create_missing_examples(examples_dir, to_create_files, templates)
    elif to_create_files:
        logging.info(f"檢測到 {len(to_create_files)} 個缺失的範例檔案，使用 --create-missing 選項可以建立它們")
    
    # 檢查現有檔案的格式問題
    for json_path in json_files:
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            is_valid, errors = validate_chart_json(data)
            
            if not is_valid:
                issues_found = True
                logging.warning(f"{json_path.name} 有問題: {', '.join(errors)}")
                
                # 修復檔案
                if not dry_run:
                    fixed_data = fix_chart_json(data, json_path.name)
                    
                    # 保存修復後的檔案
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(fixed_data, f, ensure_ascii=False, indent=4)
                    
                    logging.info(f"已修復 {json_path.name}")
                    issues_fixed += 1
        except Exception as e:
            logging.error(f"處理 {json_path.name} 時出錯: {e}")
    
    if dry_run and issues_found:
        logging.info(f"發現 {len([e for e in errors if e])} 個問題，但由於 --dry-run 選項，未進行修復")
    elif not issues_found:
        logging.info("所有現有檔案格式正確")
    else:
        logging.info(f"修復了 {issues_fixed} 個檔案")


def main():
    """主程序"""
    # 解析命令列參數
    parser = argparse.ArgumentParser(description="檢查並修復範例圖表 JSON 檔案")
    parser.add_argument("--dry-run", action="store_true", help="只檢查問題，不進行修復")
    parser.add_argument("--verbose", action="store_true", help="顯示詳細日誌")
    parser.add_argument("--create-missing", action="store_true", help="建立缺失的範例檔案")
    
    args = parser.parse_args()
    
    # 設定日誌記錄
    setup_logging(args.verbose)
    
    # 獲取範例目錄路徑
    examples_dir = get_examples_dir()
    
    logging.info(f"開始檢查範例圖表檔案，目錄: {examples_dir}")
    process_chart_files(examples_dir, args.dry_run, args.create_missing)


if __name__ == "__main__":
    main()
