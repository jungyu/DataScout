#!/usr/bin/env python3
"""
DataScout 圖表診斷與修復工具

- 支援 pie、donut、treemap、polararea 圖表的診斷與自動修復
- 可選擇僅診斷（預設）或自動修復

用法：
    python chart_diagnosis_and_fix.py [--diagnose|--fix]
"""
import argparse
import json
from pathlib import Path

def diagnose_charts():
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
        html_file = public_dir / f"{chart_type}.html"
        print(f"  {'✅' if html_file.exists() else '❌'} HTML 頁面{'存在' if html_file.exists() else '不存在'}: {html_file}")
        json_files = list(examples_dir.glob(f"*{chart_type}*.json"))
        print(f"  📊 找到 {len(json_files)} 個相關 JSON 檔案:")
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"    ✅ {json_file.name} - JSON 格式正確")
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

def diagnose_data_structure():
    print("\n=== 檢查資料結構 ===")
    examples_dir = Path("/Users/aaron/Projects/DataScout/web_frontend/public/assets/examples")
    # pie/donut
    pie_donut_files = list(examples_dir.glob("*pie*.json")) + list(examples_dir.glob("*donut*.json"))
    for json_file in pie_donut_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            has_series = 'series' in data
            has_labels = 'labels' in data
            chart_type = data.get('chart', {}).get('type', '')
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
                print(f"  ⚠️  {json_file.name}: {', '.join(issues)}")
            else:
                print(f"  ✅ {json_file.name} 結構正確")
        except Exception as e:
            print(f"  ❌ {json_file.name} 結構檢查錯誤: {e}")
    # treemap
    treemap_files = list(examples_dir.glob("*treemap*.json"))
    for json_file in treemap_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            chart_type = data.get('chart', {}).get('type', '')
            has_series = 'series' in data
            if has_series:
                series = data['series']
                if isinstance(series, list) and len(series) > 0:
                    first_series = series[0]
                    has_data = 'data' in first_series
                    if has_data:
                        data_items = first_series['data']
                        if isinstance(data_items, list) and len(data_items) > 0:
                            first_item = data_items[0]
                            required_fields = ['x', 'y']
                            missing_fields = [field for field in required_fields if field not in first_item]
                            if missing_fields:
                                print(f"  ⚠️  {json_file.name} 缺少欄位: {missing_fields}")
                            else:
                                print(f"  ✅ {json_file.name} 結構正確")
                        else:
                            print(f"  ⚠️  {json_file.name} data 陣列為空或格式錯誤")
                    else:
                        print(f"  ⚠️  {json_file.name} series[0] 缺少 data 欄位")
                else:
                    print(f"  ⚠️  {json_file.name} series 格式錯誤")
            else:
                print(f"  ⚠️  {json_file.name} 缺少 series")
        except Exception as e:
            print(f"  ❌ {json_file.name} 結構檢查錯誤: {e}")

def fix_polararea_to_polar():
    print("\n=== 修復 polararea → polar ===")
    examples_dir = Path("/Users/aaron/Projects/DataScout/web_frontend/public/assets/examples")
    polararea_files = list(examples_dir.glob("*polararea*.json"))
    fixed_files = []
    for json_file in polararea_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            current_type = data.get('chart', {}).get('type', '')
            if current_type in ['polararea', 'polarArea']:
                data['chart']['type'] = 'polar'
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                fixed_files.append(json_file.name)
                print(f"  ✅ 已修復: {json_file.name} (polararea → polar)")
        except Exception as e:
            print(f"  ❌ 修復 {json_file.name} 時發生錯誤: {e}")
    return fixed_files

def fix_missing_chart_types():
    print("\n=== 修復缺少 chart.type 的 JSON 檔案 ===")
    examples_dir = Path("/Users/aaron/Projects/DataScout/web_frontend/public/assets/examples")
    fixes = [
        ("apexcharts_donut_sales.json", "donut"),
        ("apexcharts_treemap_population.json", "treemap"),
        ("apexcharts_treemap_software_modules.json", "treemap"),
        ("apexcharts_treemap_website_content.json", "treemap"),
        ("apexcharts_treemap_server_storage.json", "treemap"),
    ]
    fixed_files = []
    for filename, chart_type in fixes:
        file_path = examples_dir / filename
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if 'chart' not in data:
                    data['chart'] = {}
                data['chart']['type'] = chart_type
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                fixed_files.append(filename)
                print(f"  ✅ 已修復: {filename} -> {chart_type}")
            except Exception as e:
                print(f"  ❌ 修復 {filename} 時發生錯誤: {e}")
        else:
            print(f"  ⚠️  檔案不存在: {filename}")
    return fixed_files

def verify_fixes():
    print("\n=== 驗證修復結果 ===")
    examples_dir = Path("/Users/aaron/Projects/DataScout/web_frontend/public/assets/examples")
    chart_files = {
        "pie": list(examples_dir.glob("*pie*.json")),
        "donut": list(examples_dir.glob("*donut*.json")),
        "treemap": list(examples_dir.glob("*treemap*.json")),
        "polar": list(examples_dir.glob("*polararea*.json")),
    }
    for chart_type, files in chart_files.items():
        print(f"\n{chart_type.upper()} 圖表:")
        for json_file in files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                file_chart_type = data.get('chart', {}).get('type', 'unknown')
                status = "✅" if file_chart_type != 'unknown' else "❌"
                print(f"  {status} {json_file.name}: {file_chart_type}")
            except Exception as e:
                print(f"  ❌ {json_file.name}: 讀取錯誤 - {e}")

def main():
    parser = argparse.ArgumentParser(description="DataScout 圖表診斷與修復工具")
    parser.add_argument('--fix', action='store_true', help='執行自動修復')
    parser.add_argument('--diagnose', action='store_true', help='僅執行診斷（預設）')
    args = parser.parse_args()
    print("DataScout 圖表診斷與修復工具")
    print("=" * 60)
    diagnose_charts()
    diagnose_data_structure()
    if args.fix:
        fixed1 = fix_polararea_to_polar()
        fixed2 = fix_missing_chart_types()
        verify_fixes()
        print("\n修復完成！")
    print("\n" + "=" * 60)
    print("流程結束。")

if __name__ == "__main__":
    main()
