#!/usr/bin/env python3
"""
修復圖表類型問題的腳本
"""

import json
from pathlib import Path

def fix_missing_chart_types():
    """修復缺少 chart.type 的 JSON 檔案"""
    print("=== 修復缺少的圖表類型 ===")
    
    examples_dir = Path("/Users/aaron/Projects/DataScout/web_frontend/public/assets/examples")
    
    # 需要修復的檔案對應
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
                
                # 確保有 chart 物件
                if 'chart' not in data:
                    data['chart'] = {}
                
                # 設定圖表類型
                data['chart']['type'] = chart_type
                
                # 寫回檔案
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                fixed_files.append(filename)
                print(f"✅ 已修復: {filename} -> {chart_type}")
                
            except Exception as e:
                print(f"❌ 修復 {filename} 時發生錯誤: {e}")
        else:
            print(f"⚠️  檔案不存在: {filename}")
    
    return fixed_files

def fix_polararea_to_polar():
    """將 polarArea 圖表類型改為 polar"""
    print("\n=== 修復 PolarArea 圖表類型 ===")
    
    examples_dir = Path("/Users/aaron/Projects/DataScout/web_frontend/public/assets/examples")
    polararea_files = list(examples_dir.glob("*polararea*.json"))
    
    fixed_files = []
    
    for json_file in polararea_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 檢查並修復圖表類型
            current_type = data.get('chart', {}).get('type', '')
            
            if current_type == 'polarArea':
                data['chart']['type'] = 'polar'
                
                # 寫回檔案
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                fixed_files.append(json_file.name)
                print(f"✅ 已修復: {json_file.name} (polarArea -> polar)")
            else:
                print(f"✅ {json_file.name} 類型已正確: {current_type}")
                
        except Exception as e:
            print(f"❌ 修復 {json_file.name} 時發生錯誤: {e}")
    
    return fixed_files

def verify_fixes():
    """驗證修復結果"""
    print("\n=== 驗證修復結果 ===")
    
    examples_dir = Path("/Users/aaron/Projects/DataScout/web_frontend/public/assets/examples")
    
    # 檢查所有圖表檔案的類型
    chart_files = {
        "pie": list(examples_dir.glob("*pie*.json")),
        "donut": list(examples_dir.glob("*donut*.json")),
        "treemap": list(examples_dir.glob("*treemap*.json")),
        "polar": list(examples_dir.glob("*polararea*.json"))
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
    """主要修復流程"""
    print("DataScout 圖表類型修復腳本")
    print("=" * 60)
    
    # 修復缺少的圖表類型
    fixed_types = fix_missing_chart_types()
    
    # 修復 PolarArea 到 polar
    fixed_polar = fix_polararea_to_polar()
    
    # 驗證修復結果
    verify_fixes()
    
    # 總結
    print("\n" + "=" * 60)
    print("=== 修復總結 ===")
    
    print(f"✅ 修復缺少類型的檔案: {len(fixed_types)} 個")
    for filename in fixed_types:
        print(f"   - {filename}")
    
    print(f"✅ 修復 PolarArea 類型: {len(fixed_polar)} 個")
    for filename in fixed_polar:
        print(f"   - {filename}")
    
    print("\n🎯 所有圖表類型修復完成！")

if __name__ == "__main__":
    main()
