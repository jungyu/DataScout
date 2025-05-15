#!/bin/bash

# 設置顏色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # 無顏色

# 設置基本路徑
BASE_DIR=$(dirname "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)")
cd "$BASE_DIR"

# 檢查範例檔案目錄
echo -e "${YELLOW}檢查範例檔案目錄...${NC}"
EXAMPLES_DIR="$BASE_DIR/examples"
if [ ! -d "$EXAMPLES_DIR" ]; then
    echo -e "${RED}範例檔案目錄不存在，創建中...${NC}"
    mkdir -p "$EXAMPLES_DIR"
fi

# 檢查是否有範例檔案
EXAMPLE_COUNT=$(find "$EXAMPLES_DIR" -name "example_*.json" | wc -l)
if [ "$EXAMPLE_COUNT" -eq 0 ]; then
    echo -e "${RED}沒有找到範例檔案！${NC}"
    echo -e "${YELLOW}生成一些基本範例文件...${NC}"
    
    # 生成基本範例
    python -c '
import os
import json
import random

EXAMPLES_DIR = "'"$EXAMPLES_DIR"'"
os.makedirs(EXAMPLES_DIR, exist_ok=True)

# 定義基本圖表類型
chart_types = ["bar", "line", "pie", "radar", "doughnut", "scatter", "bubble"]

# 為每個類型創建至少一個範例
for chart_type in chart_types:
    filename = f"example_{chart_type}_chart.json"
    filepath = os.path.join(EXAMPLES_DIR, filename)
    
    # 如果檔案已存在，跳過
    if os.path.exists(filepath):
        continue
    
    # 創建簡單數據
    data = {
        "type": chart_type,
        "labels": ["一月", "二月", "三月", "四月", "五月", "六月"],
        "datasets": [{
            "label": "樣本數據",
            "data": [random.randint(10, 100) for _ in range(6)],
            "backgroundColor": "rgba(75, 192, 192, 0.2)",
            "borderColor": "rgba(75, 192, 192, 1)"
        }],
        "chartTitle": f"{chart_type.capitalize()}型圖表範例"
    }
    
    # 保存檔案
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"已創建: {filename}")
'
fi

# 顯示範例檔案清單
echo -e "${GREEN}範例檔案清單:${NC}"
find "$EXAMPLES_DIR" -name "example_*.json" | sort

# 啟動開發伺服器
echo -e "${GREEN}啟動應用伺服器...${NC}"
cd "$BASE_DIR"
python -m app.main "$@"
