#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
範例檔案測試工具

用於測試與管理範例檔案的命令行工具
"""

import os
import sys
import json
import argparse
from pathlib import Path
import glob
import random
import string

# 取得基礎目錄路徑
BASE_DIR = Path(__file__).resolve().parent.parent
EXAMPLES_DIR = BASE_DIR / "examples"

def generate_random_data(chart_type, num_points=10):
    """生成隨機圖表數據"""
    data = {
        "type": chart_type,
        "chartTitle": f"{chart_type.capitalize()} Chart Example",
        "labels": [f"Label {i+1}" for i in range(num_points)],
        "datasets": []
    }
    
    # 為不同圖表類型生成合適的數據
    if chart_type in ["line", "bar", "radar"]:
        # 添加 2 個數據集
        for i in range(2):
            dataset = {
                "label": f"Dataset {i+1}",
                "data": [round(random.random() * 100) for _ in range(num_points)],
                "backgroundColor": f"rgba({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)}, 0.2)",
                "borderColor": f"rgba({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)}, 1)"
            }
            data["datasets"].append(dataset)
    
    elif chart_type in ["pie", "doughnut"]:
        # 只添加 1 個數據集
        dataset = {
            "label": "Dataset 1",
            "data": [round(random.random() * 100) for _ in range(num_points)],
            "backgroundColor": [f"rgba({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)}, 0.6)" for _ in range(num_points)]
        }
        data["datasets"].append(dataset)
    
    elif chart_type == "scatter":
        # 添加 2 個散點數據集
        for i in range(2):
            dataset = {
                "label": f"Dataset {i+1}",
                "data": [{"x": round(random.random() * 100), "y": round(random.random() * 100)} for _ in range(num_points)],
                "backgroundColor": f"rgba({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)}, 0.6)"
            }
            data["datasets"].append(dataset)
    
    elif chart_type == "bubble":
        # 添加氣泡圖數據
        dataset = {
            "label": "Dataset 1",
            "data": [{"x": round(random.random() * 100), "y": round(random.random() * 100), "r": round(random.random() * 20) + 5} for _ in range(num_points)],
            "backgroundColor": f"rgba({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)}, 0.6)"
        }
        data["datasets"].append(dataset)
    
    return data

def list_examples():
    """列出所有範例檔案"""
    example_files = sorted(glob.glob(str(EXAMPLES_DIR / "*.json")))
    
    print(f"\n找到 {len(example_files)} 個範例檔案:")
    
    # 按類型分類
    chart_types = {}
    for file_path in example_files:
        file_name = os.path.basename(file_path)
        # 從檔案名稱中提取圖表類型
        parts = file_name.split('_')
        if len(parts) > 1:
            chart_type = parts[1]  # example_TYPE_name.json
            if chart_type not in chart_types:
                chart_types[chart_type] = []
            chart_types[chart_type].append(file_name)
    
    # 顯示分類結果
    for chart_type, files in sorted(chart_types.items()):
        print(f"\n{chart_type.upper()}型圖表 ({len(files)}):")
        for file_name in files:
            print(f"  - {file_name}")

def create_example(chart_type, name, num_points=10):
    """創建新的範例檔案"""
    # 檢查圖表類型是否有效
    valid_types = ["bar", "line", "pie", "doughnut", "radar", "scatter", "bubble", "mixed", "candlestick"]
    if chart_type not in valid_types:
        print(f"錯誤: 無效的圖表類型 '{chart_type}'")
        print(f"有效類型: {', '.join(valid_types)}")
        return
    
    # 創建檔案名稱
    if not name:
        # 生成隨機名稱
        random_suffix = ''.join(random.choice(string.ascii_lowercase) for _ in range(5))
        name = f"random_{random_suffix}"
    
    file_name = f"example_{chart_type}_{name}.json"
    file_path = EXAMPLES_DIR / file_name
    
    # 檢查檔案是否已存在
    if os.path.exists(file_path):
        print(f"錯誤: 檔案已存在: {file_name}")
        return
    
    # 生成隨機數據
    data = generate_random_data(chart_type, num_points)
    
    # 儲存檔案
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"範例檔案已創建: {file_name}")

def check_examples():
    """檢查所有範例檔案是否有效"""
    example_files = sorted(glob.glob(str(EXAMPLES_DIR / "*.json")))
    
    print(f"\n檢查 {len(example_files)} 個範例檔案:")
    
    success_count = 0
    error_count = 0
    
    for file_path in example_files:
        file_name = os.path.basename(file_path)
        try:
            # 嘗試讀取並解析 JSON
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 檢查必要的字段
            required_fields = ["type", "datasets"]
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"  ✗ {file_name}: 缺少必要字段 {', '.join(missing_fields)}")
                error_count += 1
            else:
                # 檢查數據集
                if not data["datasets"] or not isinstance(data["datasets"], list):
                    print(f"  ✗ {file_name}: 無效的 datasets 字段")
                    error_count += 1
                else:
                    print(f"  ✓ {file_name}: 有效")
                    success_count += 1
        
        except json.JSONDecodeError:
            print(f"  ✗ {file_name}: JSON 解析錯誤")
            error_count += 1
        except Exception as e:
            print(f"  ✗ {file_name}: 錯誤: {str(e)}")
            error_count += 1
    
    print(f"\n結果: {success_count} 個有效, {error_count} 個錯誤")

def main():
    parser = argparse.ArgumentParser(description='範例檔案管理工具')
    
    subparsers = parser.add_subparsers(dest='command', help='指令')
    
    # 列出範例檔案
    list_parser = subparsers.add_parser('list', help='列出所有範例檔案')
    
    # 創建範例檔案
    create_parser = subparsers.add_parser('create', help='創建新的範例檔案')
    create_parser.add_argument('chart_type', help='圖表類型 (bar, line, pie, etc)')
    create_parser.add_argument('--name', help='檔案名稱 (不含前綴和後綴)')
    create_parser.add_argument('--points', type=int, default=10, help='數據點數量')
    
    # 檢查範例檔案
    check_parser = subparsers.add_parser('check', help='檢查所有範例檔案是否有效')
    
    args = parser.parse_args()
    
    # 確保範例目錄存在
    os.makedirs(EXAMPLES_DIR, exist_ok=True)
    
    if args.command == 'list':
        list_examples()
    elif args.command == 'create':
        create_example(args.chart_type, args.name, args.points)
    elif args.command == 'check':
        check_examples()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
