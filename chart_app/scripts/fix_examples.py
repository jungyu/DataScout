#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
修復範例檔案
確保所有範例檔案都具有一致的格式
"""

import os
import sys
import json
from pathlib import Path
import glob

# 取得基礎目錄路徑
BASE_DIR = Path(__file__).resolve().parent.parent
EXAMPLES_DIR = BASE_DIR / "examples"

def fix_example_files():
    """修復範例檔案的格式"""
    example_files = sorted(glob.glob(str(EXAMPLES_DIR / "*.json")))
    
    print(f"\n正在修復 {len(example_files)} 個範例檔案:")
    
    fixed_count = 0
    error_count = 0
    skipped_count = 0
    
    for file_path in example_files:
        file_name = os.path.basename(file_path)
        
        try:
            # 讀取檔案
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # 移除可能的註釋（JSON 不支援註釋，但有些檔案可能包含）
                if content.strip().startswith('//'):
                    lines = content.splitlines()
                    content = '\n'.join(lines[1:])
                
                data = json.loads(content)
            
            # 檢查是否需要修復
            needs_fix = False
            modifications = []
            
            # 確保有 type 欄位
            if "type" not in data:
                # 從檔案名稱猜測類型
                chart_type = file_name.split('_')[1] if len(file_name.split('_')) > 1 else "bar"
                data["type"] = chart_type
                modifications.append(f"添加 type={chart_type}")
                needs_fix = True
            
            # 檢查 datasets 欄位
            if "datasets" not in data:
                # 如果 data.datasets 存在，移到頂層
                if "data" in data and isinstance(data["data"], dict) and "datasets" in data["data"]:
                    # 將 data.datasets 移到頂層
                    data["datasets"] = data["data"]["datasets"]
                    
                    # 同時移動 labels
                    if "labels" not in data and "labels" in data["data"]:
                        data["labels"] = data["data"]["labels"]
                    
                    # 刪除原來的 data 欄位
                    del data["data"]
                    modifications.append("將 data.datasets 移至頂層")
                    needs_fix = True
                else:
                    # 創建一個空的 datasets 欄位
                    data["datasets"] = []
                    modifications.append("創建空的 datasets 欄位")
                    needs_fix = True
            
            # 檢查 chartTitle
            if "chartTitle" not in data:
                # 從檔案名生成標題
                parts = file_name.replace('.json', '').split('_')
                if len(parts) >= 3:
                    title = ' '.join(parts[2:])
                    title = title.replace('_', ' ').title()
                else:
                    chart_type = data.get("type", "Unknown")
                    title = f"{chart_type.capitalize()}型圖表"
                
                data["chartTitle"] = title
                modifications.append(f"添加標題: {title}")
                needs_fix = True
            
            # 保存修改
            if needs_fix:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                print(f"  ✓ {file_name}: 已修復 ({', '.join(modifications)})")
                fixed_count += 1
            else:
                print(f"  - {file_name}: 無需修復")
                skipped_count += 1
            
        except Exception as e:
            print(f"  ✗ {file_name}: 修復失敗: {str(e)}")
            error_count += 1
    
    print(f"\n結果: {fixed_count} 個已修復, {skipped_count} 個無需修復, {error_count} 個失敗")

if __name__ == "__main__":
    fix_example_files()
