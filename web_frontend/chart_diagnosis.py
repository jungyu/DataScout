#!/usr/bin/env python3
"""
檢查圓餅圖、環形圖、樹狀圖和極狀圖的問題
"""

import json
import requests
from pathlib import Path

def check_chart_pages():
    """檢查有問題的圖表頁面"""
    base_url = "http://localhost:8080"
    problem_charts = [
        ("pie.html", "圓餅圖"),
        ("donut.html", "環形圖"),
        ("treemap.html", "樹狀圖"),
        ("polararea.html", "極狀圖")
    ]
    
    print("=== 檢查有問題的圖表頁面 ===")
    
    for page, chart_name in problem_charts:
        try:
            response = requests.get(f"{base_url}/{page}", timeout=10)
            status = "✅ 可訪問" if response.status_code == 200 else f"❌ HTTP {response.status_code}"
            print(f"  {chart_name} ({page}): {status}")
        except Exception as e:
            print(f"  {chart_name} ({page}): ❌ 錯誤 - {e}")

def check_index_json_chart_types():
    """檢查 index.json 中的圖表類型"""
    index_path = Path("/Users/aaron/Projects/DataScout/web_frontend/public/assets/examples/index.json")
    
    print("\n=== 檢查 index.json 中的圖表類型 ===")
    
    if not index_path.exists():
        print("❌ index.json 檔案不存在")
        return
    
    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            index_data = json.load(f)
        
        problem_types = ["pie", "donut", "treemap", "polararea", "polar"]
        
        for chart_type in problem_types:
            if chart_type in index_data:
                examples = index_data[chart_type]
                print(f"  {chart_type}: ✅ 找到 {len(examples)} 個範例")
            else:
                print(f"  {chart_type}: ❌ 未找到")
                
    except Exception as e:
        print(f"❌ 讀取 index.json 時發生錯誤: {e}")

def check_data_loader_chart_types():
    """檢查 data-loader.js 中的圖表類型定義"""
    data_loader_path = Path("/Users/aaron/Projects/DataScout/web_frontend/public/data-loader.js")
    
    print("\n=== 檢查 data-loader.js 中的圖表類型定義 ===")
    
    if not data_loader_path.exists():
        print("❌ data-loader.js 檔案不存在")
        return
    
    try:
        with open(data_loader_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 檢查 ChartType 定義
        problem_types = ["pie", "donut", "treemap", "polararea", "polar"]
        
        for chart_type in problem_types:
            if f"'{chart_type}'" in content or f'"{chart_type}"' in content:
                print(f"  {chart_type}: ✅ 已定義")
            else:
                print(f"  {chart_type}: ❌ 未定義")
                
    except Exception as e:
        print(f"❌ 讀取 data-loader.js 時發生錯誤: {e}")

def main():
    """主要檢查流程"""
    print("DataScout 圖表問題診斷工具")
    print("=" * 50)
    
    # 先檢查本地伺服器是否運行
    try:
        response = requests.get("http://localhost:8080", timeout=5)
        print("✅ 本地伺服器運行正常\n")
    except:
        print("⚠️  本地伺服器未啟動，跳過頁面訪問測試\n")
    
    check_index_json_chart_types()
    check_data_loader_chart_types()
    
    # 如果伺服器運行，檢查頁面
    try:
        requests.get("http://localhost:8080", timeout=2)
        check_chart_pages()
    except:
        pass
    
    print("\n" + "=" * 50)
    print("檢查完成")

if __name__ == "__main__":
    main()
