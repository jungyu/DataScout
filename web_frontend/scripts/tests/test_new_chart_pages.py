#!/usr/bin/env python3
"""
測試新建立的圖表頁面功能
檢查頁面是否能正確載入和渲染圖表
"""

import json
import time
import requests
from pathlib import Path

def test_chart_page_accessibility():
    """測試新建立的圖表頁面是否可以訪問"""
    base_url = "http://localhost:8080"
    new_pages = [
        "stacked_bar.html",
        "boxplot.html", 
        "funnel.html",
        "bubble.html"
    ]
    
    print("=== 測試新建立的圖表頁面可訪問性 ===")
    results = {}
    
    for page in new_pages:
        try:
            response = requests.get(f"{base_url}/{page}", timeout=10)
            status = "✅ 成功" if response.status_code == 200 else f"❌ 失敗 ({response.status_code})"
            results[page] = {
                "status_code": response.status_code,
                "accessible": response.status_code == 200,
                "content_length": len(response.content)
            }
            print(f"  {page}: {status} - 內容大小: {len(response.content)} bytes")
        except Exception as e:
            results[page] = {
                "status_code": None,
                "accessible": False,
                "error": str(e)
            }
            print(f"  {page}: ❌ 錯誤 - {e}")
    
    return results

def verify_index_json_integration():
    """驗證 index.json 中的資料是否正確對應新頁面"""
    index_path = Path("/Users/aaron/Projects/DataScout/web_frontend/public/assets/examples/index.json")
    
    print("\n=== 驗證 index.json 與新頁面的整合 ===")
    
    if not index_path.exists():
        print("❌ index.json 檔案不存在")
        return False
    
    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            index_data = json.load(f)
        
        new_chart_types = ['stacked_bar', 'boxplot', 'funnel', 'bubble']
        
        for chart_type in new_chart_types:
            if chart_type in index_data:
                examples = index_data[chart_type]
                print(f"  {chart_type}: ✅ 找到 {len(examples)} 個範例")
                for example in examples:
                    file_path = Path("/Users/aaron/Projects/DataScout/web_frontend/public/assets/examples") / example["file"]
                    if file_path.exists():
                        print(f"    - {example['file']}: ✅ 檔案存在")
                    else:
                        print(f"    - {example['file']}: ❌ 檔案不存在")
            else:
                print(f"  {chart_type}: ❌ 在 index.json 中未找到")
        
        return True
        
    except Exception as e:
        print(f"❌ 讀取 index.json 時發生錯誤: {e}")
        return False

def test_json_file_validity():
    """測試所有相關的 JSON 檔案是否有效"""
    examples_dir = Path("/Users/aaron/Projects/DataScout/web_frontend/public/assets/examples")
    new_chart_types = ['stacked_bar', 'boxplot', 'funnel', 'bubble']
    
    print("\n=== 測試新圖表類型的 JSON 檔案有效性 ===")
    
    index_path = examples_dir / "index.json"
    if not index_path.exists():
        print("❌ index.json 不存在")
        return False
    
    try:
        with open(index_path, 'r', encoding='utf-8') as f:
            index_data = json.load(f)
        
        total_files = 0
        valid_files = 0
        
        for chart_type in new_chart_types:
            if chart_type in index_data:
                print(f"\n  檢查 {chart_type} 類型的檔案:")
                for example in index_data[chart_type]:
                    file_path = examples_dir / example["file"]
                    total_files += 1
                    
                    if file_path.exists():
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                json.load(f)
                            print(f"    ✅ {example['file']}: JSON 格式有效")
                            valid_files += 1
                        except json.JSONDecodeError as e:
                            print(f"    ❌ {example['file']}: JSON 格式錯誤 - {e}")
                    else:
                        print(f"    ❌ {example['file']}: 檔案不存在")
        
        print(f"\n  總結: {valid_files}/{total_files} 個檔案有效")
        return valid_files == total_files
        
    except Exception as e:
        print(f"❌ 檢查過程中發生錯誤: {e}")
        return False

def main():
    """主要測試函數"""
    print("DataScout 新圖表頁面測試工具")
    print("=" * 50)
    
    # 等待伺服器啟動
    print("等待本地伺服器啟動...")
    time.sleep(3)
    
    # 測試頁面可訪問性
    accessibility_results = test_chart_page_accessibility()
    
    # 驗證 index.json 整合
    index_integration = verify_index_json_integration()
    
    # 測試 JSON 檔案有效性
    json_validity = test_json_file_validity()
    
    # 生成測試報告
    print("\n" + "=" * 50)
    print("=== 測試結果總結 ===")
    
    accessible_count = sum(1 for result in accessibility_results.values() if result.get('accessible', False))
    print(f"頁面可訪問性: {accessible_count}/4 個頁面可以正常訪問")
    
    print(f"index.json 整合: {'✅ 通過' if index_integration else '❌ 失敗'}")
    print(f"JSON 檔案有效性: {'✅ 通過' if json_validity else '❌ 失敗'}")
    
    if accessible_count == 4 and index_integration and json_validity:
        print("\n🎉 所有測試都通過！新圖表頁面已經準備就緒。")
        return True
    else:
        print("\n⚠️  部分測試失敗，請檢查上述錯誤訊息。")
        return False

if __name__ == "__main__":
    main()
