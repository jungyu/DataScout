#!/usr/bin/env python3
"""
圓餅圖、環形圖、樹狀圖診斷與修復腳本
"""

import json
import re
from pathlib import Path

def diagnose_specific_charts():
    """診斷圓餅圖、環形圖、樹狀圖的具體問題"""
    print("=== 診斷特定圖表問題 ===")
    
    charts_to_check = {
        "pie": "圓餅圖",
        "donut": "環形圖", 
        "treemap": "樹狀圖",
        "polararea": "極地圖"
    }
    
    public_dir = Path("/Users/aaron/Projects/DataScout/web_frontend/public")
    examples_dir = public_dir / "assets" / "examples"
    
    results = {}
    
    for chart_type, chart_name in charts_to_check.items():
        print(f"\n檢查 {chart_name} ({chart_type}):")
        
        # 檢查 HTML 頁面
        html_file = public_dir / f"{chart_type}.html"
        if html_file.exists():
            print(f"  ✅ HTML 頁面存在: {html_file}")
        else:
            print(f"  ❌ HTML 頁面不存在: {html_file}")
        
        # 檢查相關的 JSON 範例檔案
        json_files = list(examples_dir.glob(f"*{chart_type}*.json"))
        print(f"  📊 找到 {len(json_files)} 個相關 JSON 檔案:")
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"    ✅ {json_file.name} - JSON 格式正確")
                
                # 檢查圖表類型
                chart_config_type = data.get('chart', {}).get('type', 'unknown')
                print(f"      圖表類型: {chart_config_type}")
                
            except json.JSONDecodeError as e:
                print(f"    ❌ {json_file.name} - JSON 解析錯誤: {e}")
            except Exception as e:
                print(f"    ❌ {json_file.name} - 讀取錯誤: {e}")
        
        results[chart_type] = {
            "html_exists": html_file.exists(),
            "json_files": len(json_files),
            "json_files_list": [f.name for f in json_files]
        }
    
    return results

def check_polararea_chart_type():
    """檢查 PolarArea 圖表類型並修復為 polar"""
    print("\n=== 檢查 PolarArea 圖表類型 ===")
    
    examples_dir = Path("/Users/aaron/Projects/DataScout/web_frontend/public/assets/examples")
    polararea_files = list(examples_dir.glob("*polararea*.json"))
    
    fixed_files = []
    
    for json_file in polararea_files:
        print(f"\n檢查檔案: {json_file.name}")
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 檢查圖表類型
            current_type = data.get('chart', {}).get('type', '')
            print(f"  當前圖表類型: {current_type}")
            
            if current_type == 'polararea':
                print(f"  🔧 需要修復: polararea -> polar")
                
                # 修復圖表類型
                data['chart']['type'] = 'polar'
                
                # 寫回檔案
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                fixed_files.append(json_file.name)
                print(f"  ✅ 已修復: {json_file.name}")
            else:
                print(f"  ✅ 類型正確，無需修復")
                
        except Exception as e:
            print(f"  ❌ 處理檔案時發生錯誤: {e}")
    
    return fixed_files

def check_chart_data_structure():
    """檢查圓餅圖、環形圖的資料結構"""
    print("\n=== 檢查圓餅圖和環形圖資料結構 ===")
    
    examples_dir = Path("/Users/aaron/Projects/DataScout/web_frontend/public/assets/examples")
    
    pie_donut_files = list(examples_dir.glob("*pie*.json")) + list(examples_dir.glob("*donut*.json"))
    
    for json_file in pie_donut_files:
        print(f"\n檢查檔案: {json_file.name}")
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 檢查資料結構
            has_series = 'series' in data
            has_labels = 'labels' in data
            chart_type = data.get('chart', {}).get('type', '')
            
            print(f"  圖表類型: {chart_type}")
            print(f"  有 series: {has_series}")
            print(f"  有 labels: {has_labels}")
            
            if has_series:
                series = data['series']
                if isinstance(series, list):
                    print(f"  series 資料: {series[:3]}..." if len(series) > 3 else f"  series 資料: {series}")
                else:
                    print(f"  series 類型異常: {type(series)}")
            
            if has_labels:
                labels = data['labels']
                if isinstance(labels, list):
                    print(f"  labels 資料: {labels[:3]}..." if len(labels) > 3 else f"  labels 資料: {labels}")
                else:
                    print(f"  labels 類型異常: {type(labels)}")
            
            # 檢查是否有必要的屬性
            issues = []
            if chart_type in ['pie', 'donut']:
                if not has_series:
                    issues.append("缺少 series 資料")
                if not has_labels:
                    issues.append("缺少 labels 資料")
                if has_series and not isinstance(data['series'], list):
                    issues.append("series 應該是陣列")
                if has_labels and not isinstance(data['labels'], list):
                    issues.append("labels 應該是陣列")
            
            if issues:
                print(f"  ⚠️  發現問題: {', '.join(issues)}")
            else:
                print(f"  ✅ 資料結構正確")
                
        except Exception as e:
            print(f"  ❌ 檢查時發生錯誤: {e}")

def check_treemap_structure():
    """檢查樹狀圖的資料結構"""
    print("\n=== 檢查樹狀圖資料結構 ===")
    
    examples_dir = Path("/Users/aaron/Projects/DataScout/web_frontend/public/assets/examples")
    treemap_files = list(examples_dir.glob("*treemap*.json"))
    
    for json_file in treemap_files:
        print(f"\n檢查檔案: {json_file.name}")
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            chart_type = data.get('chart', {}).get('type', '')
            print(f"  圖表類型: {chart_type}")
            
            # 檢查 treemap 特有的資料結構
            has_series = 'series' in data
            print(f"  有 series: {has_series}")
            
            if has_series:
                series = data['series']
                if isinstance(series, list) and len(series) > 0:
                    first_series = series[0]
                    has_data = 'data' in first_series
                    print(f"  series[0] 有 data: {has_data}")
                    
                    if has_data:
                        data_items = first_series['data']
                        if isinstance(data_items, list) and len(data_items) > 0:
                            first_item = data_items[0]
                            print(f"  第一個資料項目: {first_item}")
                            
                            # treemap 需要的欄位
                            required_fields = ['x', 'y']
                            missing_fields = [field for field in required_fields if field not in first_item]
                            
                            if missing_fields:
                                print(f"  ⚠️  缺少欄位: {missing_fields}")
                            else:
                                print(f"  ✅ 資料結構正確")
                        else:
                            print(f"  ⚠️  data 陣列為空或格式錯誤")
                    else:
                        print(f"  ⚠️  series[0] 缺少 data 欄位")
                else:
                    print(f"  ⚠️  series 格式錯誤")
                    
        except Exception as e:
            print(f"  ❌ 檢查時發生錯誤: {e}")

def main():
    """主要診斷流程"""
    print("DataScout 特定圖表問題診斷與修復")
    print("=" * 60)
    
    # 診斷特定圖表
    chart_results = diagnose_specific_charts()
    
    # 修復 PolarArea 圖表類型
    fixed_polar_files = check_polararea_chart_type()
    
    # 檢查圓餅圖和環形圖資料結構
    check_chart_data_structure()
    
    # 檢查樹狀圖資料結構
    check_treemap_structure()
    
    # 總結
    print("\n" + "=" * 60)
    print("=== 診斷總結 ===")
    
    for chart_type, result in chart_results.items():
        status = "✅" if result['html_exists'] and result['json_files'] > 0 else "⚠️"
        print(f"{status} {chart_type}: HTML {'存在' if result['html_exists'] else '不存在'}, "
              f"{result['json_files']} 個 JSON 檔案")
    
    if fixed_polar_files:
        print(f"🔧 已修復 {len(fixed_polar_files)} 個 PolarArea 檔案: {', '.join(fixed_polar_files)}")
    else:
        print("✅ PolarArea 圖表類型無需修復")
    
    print("\n🎯 下一步建議:")
    print("1. 檢查特定圖表的 HTML 頁面是否正確載入資料")
    print("2. 驗證圖表渲染功能")
    print("3. 測試範例切換功能")

if __name__ == "__main__":
    main()
