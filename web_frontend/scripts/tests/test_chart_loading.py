#!/usr/bin/env python3
"""
圖表資料載入測試腳本
驗證每個圖表頁面是否能正確從 index.json 載入對應的範例資料
"""

import json
import subprocess
import time
import sys
from pathlib import Path

def test_chart_data_loading():
    """測試圖表資料載入功能"""
    print("=== 圖表資料載入測試 ===\n")
    
    # 讀取 index.json
    examples_dir = Path("/Users/aaron/Projects/DataScout/web_frontend/public/assets/examples")
    index_file = examples_dir / "index.json"
    
    if not index_file.exists():
        print("❌ index.json 檔案不存在")
        return False
    
    with open(index_file, 'r', encoding='utf-8') as f:
        index_data = json.load(f)
    
    print(f"📚 從 index.json 載入了 {len(index_data)} 種圖表類型的資料")
    
    # 定義圖表頁面映射
    chart_pages = {
        'line': 'line.html',
        'area': 'area.html', 
        'column': 'column.html',
        'bar': 'bar.html',
        'candlestick': 'candlestick.html',
        'pie': 'pie.html',
        'donut': 'donut.html',
        'radar': 'radar.html',
        'scatter': 'scatter.html',
        'heatmap': 'heatmap.html',
        'mixed': 'mixed.html',
        'treemap': 'treemap.html',
        'polararea': 'polararea.html'
    }
    
    base_url = "http://localhost:5174"
    success_count = 0
    total_tests = 0
    
    # 測試每個圖表類型
    for chart_type, examples in index_data.items():
        if chart_type not in chart_pages:
            print(f"⚠️  {chart_type}: 沒有對應的HTML頁面")
            continue
            
        page_url = f"{base_url}/{chart_pages[chart_type]}"
        total_tests += 1
        
        print(f"\n📊 測試 {chart_type.upper()} 圖表:")
        print(f"   頁面: {chart_pages[chart_type]}")
        print(f"   範例數量: {len(examples)}")
        
        # 檢查頁面是否可訪問
        try:
            result = subprocess.run(
                ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', page_url],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0 and result.stdout.strip() == '200':
                print(f"   ✅ 頁面可訪問 (HTTP 200)")
                
                # 檢查每個範例檔案
                example_success = 0
                for example in examples:
                    filename = example['file']
                    title = example['title']
                    file_path = examples_dir / filename
                    
                    if file_path.exists():
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                json.load(f)
                            print(f"      ✅ {title}: {filename}")
                            example_success += 1
                        except Exception as e:
                            print(f"      ❌ {title}: {filename} (JSON格式錯誤)")
                    else:
                        print(f"      ❌ {title}: {filename} (檔案不存在)")
                
                if example_success == len(examples):
                    print(f"   🎉 所有 {len(examples)} 個範例檔案都正常")
                    success_count += 1
                else:
                    print(f"   ⚠️  {example_success}/{len(examples)} 個範例檔案正常")
                    
            else:
                print(f"   ❌ 頁面無法訪問 (HTTP {result.stdout.strip()})")
                
        except Exception as e:
            print(f"   ❌ 測試失敗: {e}")
    
    # 總結報告
    print(f"\n{'='*50}")
    print(f"📋 測試總結:")
    print(f"📊 測試的圖表類型: {total_tests}")
    print(f"✅ 成功的圖表類型: {success_count}")
    print(f"❌ 失敗的圖表類型: {total_tests - success_count}")
    
    if success_count == total_tests:
        print(f"\n🎉 所有圖表類型都能正確載入範例資料！")
        return True
    else:
        print(f"\n⚠️  還有 {total_tests - success_count} 個圖表類型需要檢查")
        return False

def test_missing_files():
    """檢查 index.json 中引用但不存在的檔案"""
    print("\n=== 檢查缺失檔案 ===")
    
    examples_dir = Path("/Users/aaron/Projects/DataScout/web_frontend/public/assets/examples")
    index_file = examples_dir / "index.json"
    
    with open(index_file, 'r', encoding='utf-8') as f:
        index_data = json.load(f)
    
    missing_files = []
    total_files = 0
    
    for chart_type, examples in index_data.items():
        for example in examples:
            total_files += 1
            filename = example['file']
            file_path = examples_dir / filename
            
            if not file_path.exists():
                missing_files.append((chart_type, example['title'], filename))
    
    if missing_files:
        print(f"❌ 發現 {len(missing_files)} 個缺失檔案:")
        for chart_type, title, filename in missing_files:
            print(f"   - {chart_type}/{title}: {filename}")
        return False
    else:
        print(f"✅ 所有 {total_files} 個檔案都存在")
        return True

if __name__ == "__main__":
    print("DataScout 圖表資料載入測試\n")
    
    files_ok = test_missing_files()
    loading_ok = test_chart_data_loading()
    
    if files_ok and loading_ok:
        print(f"\n🎉 所有測試通過！圖表資料載入功能正常運作。")
        sys.exit(0)
    else:
        print(f"\n❌ 測試發現問題，需要進一步檢查。")
        sys.exit(1)
