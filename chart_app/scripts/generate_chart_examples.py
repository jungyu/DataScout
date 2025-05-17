#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Chart.js 圖表範例生成工具

此腳本用於生成各種 Chart.js 圖表類型的範例數據，
並將其保存為 JSON 檔案，可用於網頁視覺化展示。

支援的圖表類型:
- 基本圖表: line(折線圖), bar(長條圖), pie(圓餅圖), doughnut(環形圖), radar(雷達圖)
- 進階圖表: polarArea(極座標圖), bubble(氣泡圖), scatter(散點圖)
- 金融圖表: candlestick(K線圖), ohlc(開高低收圖)
- 其他圖表: sankey(桑基圖), heatmap(熱力圖), gauge(儀表板), treemap(矩形樹圖)

用法:
    python generate_chart_examples.py [--output-dir PATH] [--chart-types TYPE1,TYPE2,...] [--force]

選項:
    --output-dir     指定輸出目錄，預設為 ../static/examples
    --chart-types    指定要生成的圖表類型，用逗號分隔，預設生成所有類型
    --force          覆寫已存在的檔案
"""

import os
import json
import logging
import argparse
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple


# 設置日誌記錄
def setup_logging(verbose: bool = False) -> None:
    """設定日誌層級和格式"""
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )


def get_output_directory(output_dir: Optional[str] = None) -> Path:
    """
    獲取輸出目錄路徑
    
    Args:
        output_dir: 指定的輸出目錄路徑
        
    Returns:
        Path: 輸出目錄路徑
    """
    if output_dir:
        dir_path = Path(output_dir)
    else:
        # 嘗試從腳本位置猜測合適的輸出路徑
        script_dir = Path(__file__).resolve().parent
        
        # 預設輸出到 static/examples 目錄
        if (script_dir.parent / "static" / "examples").exists():
            dir_path = script_dir.parent / "static" / "examples"
        elif (script_dir.parent.parent / "static" / "examples").exists():
            dir_path = script_dir.parent.parent / "static" / "examples"
        else:
            # 如果找不到正確的路徑，建立一個臨時目錄
            dir_path = script_dir / "chart_examples"
            logging.warning(f"找不到標準輸出目錄，將使用臨時目錄: {dir_path}")
    
    # 確保目錄存在
    os.makedirs(dir_path, exist_ok=True)
    return dir_path


def generate_random_colors(count: int = 1, with_borders: bool = True) -> List[Dict[str, str]]:
    """
    生成隨機顏色列表

    Args:
        count: 顏色數量
        with_borders: 是否同時生成邊框顏色

    Returns:
        List: 顏色列表，每個元素包含 backgroundColor 和可選的 borderColor
    """
    colors = []
    # 預設顏色集，按色相分布較勻
    base_colors = [
        "rgba(255, 99, 132, 0.6)",   # 粉紅
        "rgba(54, 162, 235, 0.6)",   # 藍色
        "rgba(255, 206, 86, 0.6)",   # 黃色
        "rgba(75, 192, 192, 0.6)",   # 藍綠
        "rgba(153, 102, 255, 0.6)",  # 紫色
        "rgba(255, 159, 64, 0.6)",   # 橙色
        "rgba(199, 199, 199, 0.6)",  # 灰色
        "rgba(83, 102, 255, 0.6)",   # 深藍
        "rgba(255, 99, 71, 0.6)",    # 珊瑚紅
        "rgba(50, 205, 50, 0.6)"     # 萊姆綠
    ]
    
    for i in range(count):
        color_index = i % len(base_colors)
        color = base_colors[color_index]
        
        if with_borders:
            # 將透明度調整為不透明作為邊框顏色
            border_color = color.replace("0.6", "1.0")
            colors.append({
                "backgroundColor": color,
                "borderColor": border_color
            })
        else:
            colors.append({
                "backgroundColor": color
            })
    
    return colors


def create_line_chart() -> Dict[str, Any]:
    """生成折線圖範例數據"""
    months = ["一月", "二月", "三月", "四月", "五月", "六月", 
             "七月", "八月", "九月", "十月", "十一月", "十二月"]
    
    # 生成兩個數據系列
    sales_data = [random.randint(50, 200) for _ in range(12)]
    profit_data = [round(sales * random.uniform(0.1, 0.3)) for sales in sales_data]
    
    # 應用顏色
    colors = generate_random_colors(2)
    
    return {
        "type": "line",
        "labels": months,
        "datasets": [
            {
                "label": "銷售額",
                "data": sales_data,
                "fill": False,
                "tension": 0.3,
                **colors[0]
            },
            {
                "label": "利潤",
                "data": profit_data,
                "fill": False,
                "tension": 0.3,
                **colors[1]
            }
        ],
        "chartTitle": "月度銷售與利潤趨勢"
    }


def create_bar_chart() -> Dict[str, Any]:
    """生成長條圖範例數據"""
    categories = ["食品", "服裝", "電子", "家居", "美妝", "書籍"]
    
    # 模擬兩個季度的數據
    q1_data = [random.randint(50, 100) for _ in range(len(categories))]
    q2_data = [random.randint(50, 100) for _ in range(len(categories))]
    
    # 應用顏色
    colors = generate_random_colors(2)
    
    return {
        "type": "bar",
        "labels": categories,
        "datasets": [
            {
                "label": "第一季度",
                "data": q1_data,
                **colors[0]
            },
            {
                "label": "第二季度",
                "data": q2_data,
                **colors[1]
            }
        ],
        "chartTitle": "各品類季度銷售對比"
    }


def create_pie_chart() -> Dict[str, Any]:
    """生成圓餅圖範例數據"""
    browser_data = {
        "Chrome": 63.5,
        "Safari": 19.2,
        "Firefox": 3.7,
        "Edge": 3.5,
        "Opera": 1.5,
        "其他": 8.6
    }
    
    # 準備數據
    labels = list(browser_data.keys())
    values = list(browser_data.values())
    
    # 生成顏色
    colors = generate_random_colors(len(labels))
    background_colors = [color["backgroundColor"] for color in colors]
    border_colors = [color["borderColor"] for color in colors]
    
    return {
        "type": "pie",
        "labels": labels,
        "datasets": [
            {
                "label": "市場佔有率",
                "data": values,
                "backgroundColor": background_colors,
                "borderColor": border_colors,
                "borderWidth": 1
            }
        ],
        "chartTitle": "瀏覽器市場佔有率"
    }


def create_doughnut_chart() -> Dict[str, Any]:
    """生成環狀圖範例數據"""
    budget_data = {
        "住房": 35,
        "食品": 25,
        "交通": 15,
        "娛樂": 10,
        "儲蓄": 10,
        "其他": 5
    }
    
    # 準備數據
    labels = list(budget_data.keys())
    values = list(budget_data.values())
    
    # 生成顏色
    colors = generate_random_colors(len(labels))
    background_colors = [color["backgroundColor"] for color in colors]
    border_colors = [color["borderColor"] for color in colors]
    
    return {
        "type": "doughnut",
        "labels": labels,
        "datasets": [
            {
                "label": "家庭預算分配",
                "data": values,
                "backgroundColor": background_colors,
                "borderColor": border_colors,
                "borderWidth": 1
            }
        ],
        "chartTitle": "家庭月度預算分配",
        "options": {
            "cutout": "70%",  # 控制洞的大小
            "plugins": {
                "legend": {
                    "position": "right"
                }
            }
        }
    }


def create_radar_chart() -> Dict[str, Any]:
    """生成雷達圖範例數據"""
    skills = ["程式設計", "問題解決", "團隊合作", "溝通能力", "創新思維", "專案管理"]
    
    # 模擬兩個人的技能評分 (1-10分)
    person1_scores = [random.randint(6, 9) for _ in range(len(skills))]
    person2_scores = [random.randint(5, 10) for _ in range(len(skills))]
    
    return {
        "type": "radar",
        "labels": skills,
        "datasets": [
            {
                "label": "候選人A",
                "data": person1_scores,
                "backgroundColor": "rgba(255, 99, 132, 0.2)",
                "borderColor": "rgba(255, 99, 132, 1)",
                "borderWidth": 1
            },
            {
                "label": "候選人B",
                "data": person2_scores,
                "backgroundColor": "rgba(54, 162, 235, 0.2)",
                "borderColor": "rgba(54, 162, 235, 1)",
                "borderWidth": 1
            }
        ],
        "chartTitle": "候選人能力評估",
        "options": {
            "scales": {
                "r": {
                    "min": 0,
                    "max": 10,
                    "beginAtZero": true
                }
            }
        }
    }


def create_polarArea_chart() -> Dict[str, Any]:
    """生成極座標圖範例數據"""
    market_sectors = {
        "科技": 25,
        "醫療": 18,
        "金融": 15,
        "消費品": 12,
        "工業": 10,
        "能源": 8,
        "原材料": 7,
        "公用事業": 5
    }
    
    # 準備數據
    labels = list(market_sectors.keys())
    values = list(market_sectors.values())
    
    # 生成顏色
    colors = generate_random_colors(len(labels))
    background_colors = [color["backgroundColor"] for color in colors]
    border_colors = [color["borderColor"] for color in colors]
    
    return {
        "type": "polarArea",
        "labels": labels,
        "datasets": [
            {
                "label": "市值分布",
                "data": values,
                "backgroundColor": background_colors,
                "borderColor": border_colors,
                "borderWidth": 1
            }
        ],
        "chartTitle": "全球市場產業分布"
    }


def create_bubble_chart() -> Dict[str, Any]:
    """生成氣泡圖範例數據"""
    # 模擬國家數據: [x=人均GDP, y=識字率, r=人口(百萬)]
    countries = [
        {"name": "A國", "gdp": 60, "literacy": 98, "population": 50},
        {"name": "B國", "gdp": 45, "literacy": 88, "population": 120},
        {"name": "C國", "gdp": 30, "literacy": 75, "population": 200},
        {"name": "D國", "gdp": 78, "literacy": 99, "population": 25},
        {"name": "E國", "gdp": 35, "literacy": 80, "population": 80},
        {"name": "F國", "gdp": 55, "literacy": 95, "population": 35},
    ]
    
    bubble_data = []
    for country in countries:
        # 氣泡大小基於人口，但需要縮放以便視覺化
        size = country["population"] / 10  # 縮放係數
        bubble_data.append({
            "x": country["gdp"],
            "y": country["literacy"],
            "r": size
        })
    
    return {
        "type": "bubble",
        "labels": [country["name"] for country in countries],
        "datasets": [
            {
                "label": "國家發展指標",
                "data": bubble_data,
                "backgroundColor": "rgba(54, 162, 235, 0.6)",
                "borderColor": "rgba(54, 162, 235, 1)"
            }
        ],
        "chartTitle": "國家發展指標對比",
        "options": {
            "scales": {
                "x": {
                    "title": {
                        "display": True,
                        "text": "人均GDP (千美元)"
                    }
                },
                "y": {
                    "title": {
                        "display": True,
                        "text": "識字率 (%)"
                    }
                }
            }
        }
    }


def create_scatter_chart() -> Dict[str, Any]:
    """生成散點圖範例數據"""
    # 模擬教育支出與學生表現的關係
    countries = 20
    education_spending = [random.uniform(3, 10) for _ in range(countries)]
    student_performance = []
    
    for spending in education_spending:
        # 模擬趨勢: 支出越高，表現往往越好，但有隨機因素
        base_performance = spending * 8 + random.uniform(-10, 10)
        student_performance.append(min(100, max(50, base_performance)))
    
    scatter_data = []
    for i in range(countries):
        scatter_data.append({
            "x": education_spending[i],
            "y": student_performance[i]
        })
    
    return {
        "type": "scatter",
        "labels": [f"國家{i+1}" for i in range(countries)],
        "datasets": [
            {
                "label": "教育支出與學生表現",
                "data": scatter_data,
                "backgroundColor": "rgba(255, 99, 132, 0.6)",
                "pointRadius": 6
            }
        ],
        "chartTitle": "教育支出與學生表現的關係",
        "options": {
            "scales": {
                "x": {
                    "title": {
                        "display": True,
                        "text": "教育支出 (% of GDP)"
                    }
                },
                "y": {
                    "title": {
                        "display": True,
                        "text": "學生表現評分"
                    }
                }
            }
        }
    }


def create_candlestick_chart() -> Dict[str, Any]:
    """生成K線圖範例數據"""
    # 模擬30天的價格數據
    days = 30
    base_price = 100
    
    # 生成開高低收數據
    candlestick_data = []
    date = datetime.now() - timedelta(days=days)
    
    for i in range(days):
        date = date + timedelta(days=1)
        if date.weekday() >= 5:  # 跳過週末
            continue
            
        # 模擬價格變化
        open_price = base_price + random.uniform(-2, 2)
        close_price = open_price + random.uniform(-3, 3)
        high_price = max(open_price, close_price) + random.uniform(0.5, 2)
        low_price = min(open_price, close_price) - random.uniform(0.5, 2)
        
        # 更新基準價格，加入趨勢因素
        trend = random.uniform(-1, 1.2)  # 輕微上升趨勢
        base_price = close_price + trend
        
        candlestick_data.append({
            "t": date.strftime("%Y-%m-%d"),
            "o": round(open_price, 2),
            "h": round(high_price, 2),
            "l": round(low_price, 2),
            "c": round(close_price, 2)
        })
    
    return {
        "type": "candlestick",
        "labels": [data["t"] for data in candlestick_data],
        "datasets": [
            {
                "label": "股票價格",
                "data": candlestick_data
            }
        ],
        "chartTitle": "股票價格走勢 (K線圖)",
        "options": {
            "scales": {
                "x": {
                    "type": "time",
                    "time": {
                        "unit": "day"
                    }
                }
            }
        }
    }


def create_ohlc_chart() -> Dict[str, Any]:
    """生成OHLC圖範例數據"""
    # 大部分邏輯與K線圖相同，但圖表類型不同
    candlestick_data = create_candlestick_chart()
    candlestick_data["type"] = "ohlc"
    candlestick_data["chartTitle"] = "股票價格走勢 (OHLC圖)"
    
    return candlestick_data


def create_ohlc_with_indicators_chart() -> Dict[str, Any]:
    """生成帶有技術指標的OHLC圖範例數據"""
    base_chart = create_ohlc_chart()
    
    # 計算移動平均線 (MA5 和 MA10)
    ohlc_data = base_chart["datasets"][0]["data"]
    ma5_data = []
    ma10_data = []
    
    for i in range(len(ohlc_data)):
        # 計算MA5 (5日移動平均)
        if i >= 4:
            window = ohlc_data[i-4:i+1]
            avg_price = sum([item["c"] for item in window]) / 5
            ma5_data.append({
                "x": ohlc_data[i]["t"], 
                "y": round(avg_price, 2)
            })
        
        # 計算MA10 (10日移動平均)
        if i >= 9:
            window = ohlc_data[i-9:i+1]
            avg_price = sum([item["c"] for item in window]) / 10
            ma10_data.append({
                "x": ohlc_data[i]["t"], 
                "y": round(avg_price, 2)
            })
    
    # 添加技術指標數據集
    base_chart["datasets"].extend([
        {
            "type": "line",
            "label": "MA5",
            "data": ma5_data,
            "borderColor": "rgba(255, 99, 132, 1)",
            "backgroundColor": "transparent",
            "borderWidth": 1.5,
            "pointRadius": 0
        },
        {
            "type": "line",
            "label": "MA10",
            "data": ma10_data,
            "borderColor": "rgba(54, 162, 235, 1)",
            "backgroundColor": "transparent",
            "borderWidth": 1.5,
            "pointRadius": 0
        }
    ])
    
    base_chart["chartTitle"] = "股票價格與移動平均線"
    return base_chart


def create_ohlc_with_volume_chart() -> Dict[str, Any]:
    """生成帶有成交量的OHLC圖範例數據"""
    base_chart = create_ohlc_chart()
    
    # 生成成交量數據
    ohlc_data = base_chart["datasets"][0]["data"]
    volume_data = []
    
    for item in ohlc_data:
        # 價格波動越大，成交量往往越大
        price_change = abs(item["c"] - item["o"])
        base_volume = random.randint(1000, 5000)
        volume = base_volume + int(price_change * 1000)
        
        volume_data.append({
            "x": item["t"],
            "y": volume
        })
    
    # 添加成交量數據集
    base_chart["datasets"].append({
        "type": "bar",
        "label": "成交量",
        "data": volume_data,
        "backgroundColor": "rgba(75, 192, 192, 0.4)",
        "borderColor": "rgba(75, 192, 192, 1)",
        "borderWidth": 1,
        "yAxisID": "volume"
    })
    
    # 添加右側Y軸配置
    base_chart["options"] = {
        "scales": {
            "y": {
                "position": "left"
            },
            "volume": {
                "position": "right",
                "grid": {
                    "drawOnChartArea": False
                },
                "title": {
                    "display": True,
                    "text": "成交量"
                }
            }
        }
    }
    
    base_chart["chartTitle"] = "股票價格與成交量"
    return base_chart


def create_sankey_chart() -> Dict[str, Any]:
    """生成桑基圖範例數據"""
    # 模擬能源流向數據
    sankey_data = [
        {"from": "石油", "to": "運輸", "flow": 25},
        {"from": "石油", "to": "工業", "flow": 10},
        {"from": "天然氣", "to": "發電", "flow": 20},
        {"from": "天然氣", "to": "住宅", "flow": 15},
        {"from": "煤炭", "to": "發電", "flow": 25},
        {"from": "煤炭", "to": "工業", "flow": 10},
        {"from": "太陽能", "to": "發電", "flow": 7},
        {"from": "風能", "to": "發電", "flow": 8},
        {"from": "水力", "to": "發電", "flow": 5},
        {"from": "生物質", "to": "發電", "flow": 3},
        {"from": "生物質", "to": "運輸", "flow": 2},
        {"from": "核能", "to": "發電", "flow": 12},
        {"from": "發電", "to": "住宅", "flow": 30},
        {"from": "發電", "to": "商業", "flow": 35},
        {"from": "發電", "to": "工業", "flow": 15}
    ]
    
    # 收集所有唯一的節點
    nodes = set()
    for item in sankey_data:
        nodes.add(item["from"])
        nodes.add(item["to"])
    
    return {
        "type": "sankey",
        "labels": list(nodes),
        "datasets": [
            {
                "label": "能源流向",
                "data": sankey_data
            }
        ],
        "chartTitle": "能源流向圖"
    }


def create_heatmap_chart() -> Dict[str, Any]:
    """生成熱力圖範例數據"""
    weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
    hours = ["早上", "上午", "中午", "下午", "晚上"]
    
    # 生成每天每個時段的活躍度數據
    data = []
    for i, day in enumerate(weekdays):
        for j, hour in enumerate(hours):
            # 工作日工作時間通常活躍度較高
            if i < 5 and 1 <= j <= 3:
                value = random.randint(60, 100)
            # 週末白天活躍度適中
            elif i >= 5 and 1 <= j <= 3:
                value = random.randint(40, 80)
            # 其他時段活躍度較低
            else:
                value = random.randint(10, 50)
            
            data.append({
                "x": day,
                "y": hour,
                "v": value
            })
    
    return {
        "type": "heatmap",
        "labels": {
            "x": weekdays,
            "y": hours
        },
        "datasets": [
            {
                "label": "活躍度",
                "data": data
            }
        ],
        "chartTitle": "網站用戶活躍度熱力圖",
        "options": {
            "plugins": {
                "colorschemes": {
                    "scheme": "brewer.YlOrRd9"
                }
            }
        }
    }


def create_gauge_chart() -> Dict[str, Any]:
    """生成儀表板圖範例數據"""
    # 模擬服務器負載測量值
    value = random.randint(60, 85)
    
    return {
        "type": "gauge",
        "datasets": [
            {
                "label": "伺服器負載",
                "data": [value],
                "min": 0,
                "max": 100,
                "backgroundColor": [
                    "rgba(75, 192, 192, 0.6)",  # 綠色區域 (0-50)
                    "rgba(255, 206, 86, 0.6)",  # 黃色區域 (50-80)
                    "rgba(255, 99, 132, 0.6)"   # 紅色區域 (80-100)
                ],
                "borderWidth": 0,
                "segments": {
                    "count": 3,
                    "width": 0.3
                }
            }
        ],
        "chartTitle": "伺服器CPU負載 (%)",
        "options": {
            "valueLabel": {
                "display": True,
                "fontSize": 24,
                "formatter": "value%"
            }
        }
    }


def create_treemap_chart() -> Dict[str, Any]:
    """生成矩形樹圖範例數據"""
    # 模擬公司各部門預算分配
    departments = {
        "研發部": 35,
        "行銷部": 25,
        "運營部": 15,
        "人力資源部": 10,
        "財務部": 8,
        "法務部": 7
    }
    
    treemap_data = []
    for dept, value in departments.items():
        treemap_data.append({
            "label": dept,
            "value": value
        })
    
    return {
        "type": "treemap",
        "datasets": [
            {
                "label": "部門預算",
                "data": treemap_data,
                "backgroundColor": [
                    "rgba(75, 192, 192, 0.6)",
                    "rgba(54, 162, 235, 0.6)",
                    "rgba(255, 206, 86, 0.6)",
                    "rgba(255, 99, 132, 0.6)",
                    "rgba(153, 102, 255, 0.6)",
                    "rgba(255, 159, 64, 0.6)"
                ],
                "borderColor": "white",
                "borderWidth": 1
            }
        ],
        "chartTitle": "公司部門預算分配",
        "options": {
            "plugins": {
                "legend": {
                    "display": False
                },
                "tooltip": {
                    "formatter": "value%"
                }
            }
        }
    }


def create_mixed_chart() -> Dict[str, Any]:
    """生成混合圖表範例數據 (長條圖+折線圖)"""
    months = ["一月", "二月", "三月", "四月", "五月", "六月"]
    
    # 準備數據: 銷售額(長條圖) 和 利潤率(折線圖)
    sales_data = [random.randint(100, 200) for _ in range(len(months))]
    
    # 利潤率在15%-30%之間
    profit_ratio = [round(random.uniform(15, 30), 1) for _ in range(len(months))]
    
    return {
        "type": "bar",  # 主圖表類型
        "labels": months,
        "datasets": [
            {
                "type": "bar",
                "label": "銷售額",
                "data": sales_data,
                "backgroundColor": "rgba(75, 192, 192, 0.6)",
                "borderColor": "rgba(75, 192, 192, 1)",
                "borderWidth": 1,
                "yAxisID": "y"
            },
            {
                "type": "line",
                "label": "利潤率(%)",
                "data": profit_ratio,
                "backgroundColor": "transparent",
                "borderColor": "rgba(255, 99, 132, 1)",
                "borderWidth": 2,
                "yAxisID": "y1"
            }
        ],
        "chartTitle": "銷售額與利潤率對比",
        "options": {
            "scales": {
                "y": {
                    "position": "left",
                    "title": {
                        "display": True,
                        "text": "銷售額"
                    }
                },
                "y1": {
                    "position": "right",
                    "title": {
                        "display": True,
                        "text": "利潤率(%)"
                    },
                    "grid": {
                        "drawOnChartArea": False
                    },
                    "min": 0,
                    "max": 50
                }
            }
        }
    }


# 圖表生成函數映射表
CHART_GENERATORS = {
    "line": create_line_chart,
    "bar": create_bar_chart,
    "pie": create_pie_chart,
    "doughnut": create_doughnut_chart,
    "radar": create_radar_chart,
    "polarArea": create_polarArea_chart,
    "bubble": create_bubble_chart,
    "scatter": create_scatter_chart,
    "candlestick": create_candlestick_chart,
    "ohlc": create_ohlc_chart,
    "ohlc_indicators": create_ohlc_with_indicators_chart,
    "ohlc_volume": create_ohlc_with_volume_chart,
    "sankey": create_sankey_chart,
    "heatmap": create_heatmap_chart,
    "gauge": create_gauge_chart,
    "treemap": create_treemap_chart,
    "mixed": create_mixed_chart
}


def create_special_examples() -> List[Dict[str, Any]]:
    """創建特殊範例圖表數據"""
    special_examples = []
    
    # 1. 疫情數據折線圖
    covid_example = {
        "name": "example_line_covid_cases",
        "type": "line",
        "data": {
            "type": "line",
            "labels": ["一月", "二月", "三月", "四月", "五月", "六月", "七月", "八月", "九月", "十月"],
            "datasets": [
                {
                    "label": "確診病例",
                    "data": [10, 35, 280, 640, 980, 750, 320, 180, 50, 20],
                    "fill": False,
                    "backgroundColor": "rgba(255, 99, 132, 0.6)",
                    "borderColor": "rgba(255, 99, 132, 1)",
                    "borderWidth": 2,
                    "tension": 0.3
                },
                {
                    "label": "康復人數",
                    "data": [0, 5, 30, 120, 350, 600, 700, 800, 900, 950],
                    "fill": False,
                    "backgroundColor": "rgba(75, 192, 192, 0.6)",
                    "borderColor": "rgba(75, 192, 192, 1)",
                    "borderWidth": 2,
                    "tension": 0.3
                }
            ],
            "chartTitle": "疫情趨勢圖"
        }
    }
    special_examples.append(covid_example)
    
    # 2. 聯準會基準利率變化
    fed_rate_example = {
        "name": "example_line_fred_unemployment",
        "type": "line",
        "data": {
            "type": "line",
            "labels": ["2018", "2019", "2020-Q1", "2020-Q2", "2020-Q3", "2020-Q4", "2021", "2022", "2023", "2024"],
            "datasets": [
                {
                    "label": "失業率",
                    "data": [3.9, 3.7, 3.8, 13.2, 8.5, 6.8, 5.4, 3.7, 3.5, 3.6],
                    "fill": False,
                    "backgroundColor": "rgba(54, 162, 235, 0.6)",
                    "borderColor": "rgba(54, 162, 235, 1)",
                    "borderWidth": 2
                }
            ],
            "chartTitle": "美國失業率"
        }
    }
    special_examples.append(fed_rate_example)
    
    # 3. 股票指數圖表
    sp500_example = {
        "name": "example_line_Yfinance_Sp500",
        "type": "line",
        "data": {
            "type": "line",
            "labels": ["2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022", "2023", "2024"],
            "datasets": [
                {
                    "label": "S&P 500",
                    "data": [2054, 2239, 2673, 2507, 3231, 3756, 4766, 3840, 4180, 5500],
                    "fill": False,
                    "backgroundColor": "rgba(75, 192, 192, 0.6)",
                    "borderColor": "rgba(75, 192, 192, 1)",
                    "borderWidth": 2,
                    "tension": 0.2
                }
            ],
            "chartTitle": "S&P 500 指數走勢"
        }
    }
    special_examples.append(sp500_example)
    
    # 4. 新聞來源分析
    news_example = {
        "name": "example_bar_bloomberg_news_count",
        "type": "bar",
        "data": {
            "type": "bar",
            "labels": ["經濟", "政治", "科技", "健康", "娛樂", "體育", "國際"],
            "datasets": [
                {
                    "label": "彭博社",
                    "data": [120, 80, 110, 60, 30, 20, 90],
                    "backgroundColor": "rgba(54, 162, 235, 0.6)",
                    "borderColor": "rgba(54, 162, 235, 1)",
                    "borderWidth": 1
                }
            ],
            "chartTitle": "彭博社新聞分類統計"
        }
    }
    special_examples.append(news_example)
    
    # 5. 日經新聞統計
    nikkei_example = {
        "name": "example_bar_nikkei_news_count",
        "type": "bar",
        "data": {
            "type": "bar",
            "labels": ["經濟", "政治", "科技", "健康", "娛樂", "體育", "國際"],
            "datasets": [
                {
                    "label": "日經新聞",
                    "data": [100, 70, 95, 50, 25, 30, 85],
                    "backgroundColor": "rgba(255, 99, 132, 0.6)",
                    "borderColor": "rgba(255, 99, 132, 1)",
                    "borderWidth": 1
                }
            ],
            "chartTitle": "日經新聞分類統計"
        }
    }
    special_examples.append(nikkei_example)
    
    # 6. 投資風險雷達圖
    investment_risk = {
        "name": "example_radar_investment_risk",
        "type": "radar",
        "data": {
            "type": "radar",
            "labels": ["市場風險", "信用風險", "流動性風險", "操作風險", "法規風險", "匯率風險"],
            "datasets": [
                {
                    "label": "基金A",
                    "data": [7, 3, 5, 4, 3, 8],
                    "backgroundColor": "rgba(255, 99, 132, 0.2)",
                    "borderColor": "rgba(255, 99, 132, 1)",
                    "borderWidth": 1
                },
                {
                    "label": "基金B",
                    "data": [4, 7, 6, 3, 5, 4],
                    "backgroundColor": "rgba(54, 162, 235, 0.2)",
                    "borderColor": "rgba(54, 162, 235, 1)",
                    "borderWidth": 1
                }
            ],
            "chartTitle": "投資風險評估"
        }
    }
    special_examples.append(investment_risk)
    
    # 7. 比特幣/美元K線圖
    btc_example = {
        "name": "example_candlestick_bitcoin_usd",
        "type": "candlestick",
        "data": {
            "type": "candlestick",
            "labels": [f"2024-{i//2+1}-{(i%2+1)*15}" for i in range(10)],
            "datasets": [
                {
                    "label": "比特幣/美元",
                    "data": [
                        {"t": "2024-01-15", "o": 42000, "h": 43200, "l": 41500, "c": 42800},
                        {"t": "2024-01-30", "o": 42800, "h": 44500, "l": 42500, "c": 43900},
                        {"t": "2024-02-15", "o": 43900, "h": 45000, "l": 43200, "c": 44200},
                        {"t": "2024-02-29", "o": 44200, "h": 46700, "l": 44000, "c": 45800},
                        {"t": "2024-03-15", "o": 45800, "h": 47500, "l": 45300, "c": 47000},
                        {"t": "2024-03-30", "o": 47000, "h": 48800, "l": 46200, "c": 48500},
                        {"t": "2024-04-15", "o": 48500, "h": 52000, "l": 48200, "c": 51500},
                        {"t": "2024-04-30", "o": 51500, "h": 53500, "l": 51000, "c": 52800},
                        {"t": "2024-05-15", "o": 52800, "h": 54000, "l": 51500, "c": 53000},
                        {"t": "2024-05-30", "o": 53000, "h": 56000, "l": 52000, "c": 55000}
                    ]
                }
            ],
            "chartTitle": "比特幣/美元 價格走勢"
        }
    }
    special_examples.append(btc_example)
    
    return special_examples


def generate_chart_examples(output_dir: Path, chart_types: List[str] = None, force: bool = False) -> None:
    """
    生成圖表範例並保存到指定目錄
    
    Args:
        output_dir: 輸出目錄路徑
        chart_types: 要生成的圖表類型列表，None表示生成所有類型
        force: 是否覆蓋已存在的檔案
    """
    # 如果沒有指定圖表類型，則生成所有類型
    if not chart_types:
        chart_types = list(CHART_GENERATORS.keys())
    else:
        # 驗證指定的圖表類型是否有效
        invalid_types = [t for t in chart_types if t not in CHART_GENERATORS]
        if invalid_types:
            logging.warning(f"忽略無效的圖表類型: {', '.join(invalid_types)}")
            chart_types = [t for t in chart_types if t in CHART_GENERATORS]
    
    logging.info(f"準備生成 {len(chart_types)} 種圖表範例...")
    
    # 生成基本範例
    for chart_type in chart_types:
        # 建立檔案名稱
        filename = f"example_{chart_type}_chart.json"
        filepath = output_dir / filename
        
        # 檢查檔案是否已存在
        if filepath.exists() and not force:
            logging.info(f"檔案已存在，跳過: {filename}")
            continue
        
        # 生成圖表數據
        try:
            chart_data = CHART_GENERATORS[chart_type]()
            
            # 保存為JSON檔案
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(chart_data, f, ensure_ascii=False, indent=2)
                
            logging.info(f"已生成圖表範例: {filename}")
        except Exception as e:
            logging.error(f"生成 {chart_type} 圖表範例時出錯: {e}")
    
    # 生成特殊範例
    special_examples = create_special_examples()
    for example in special_examples:
        filename = f"{example['name']}.json"
        filepath = output_dir / filename
        
        # 檢查檔案是否已存在
        if filepath.exists() and not force:
            logging.info(f"檔案已存在，跳過: {filename}")
            continue
        
        # 保存為JSON檔案
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(example['data'], f, ensure_ascii=False, indent=2)
                
            logging.info(f"已生成特殊圖表範例: {filename}")
        except Exception as e:
            logging.error(f"生成特殊圖表範例 {example['name']} 時出錯: {e}")
    
    logging.info(f"圖表範例生成完成，位置: {output_dir}")


def main():
    """主程序"""
    # 解析命令列參數
    parser = argparse.ArgumentParser(description="Chart.js 圖表範例生成工具")
    parser.add_argument("--output-dir", help="輸出目錄路徑")
    parser.add_argument("--chart-types", help="要生成的圖表類型，用逗號分隔")
    parser.add_argument("--force", action="store_true", help="覆蓋已存在的檔案")
    parser.add_argument("--verbose", action="store_true", help="顯示詳細日誌")
    
    args = parser.parse_args()
    
    # 設定日誌記錄
    setup_logging(args.verbose)
    
    # 處理要生成的圖表類型
    chart_types = None
    if args.chart_types:
        chart_types = [t.strip() for t in args.chart_types.split(",")]
    
    # 獲取輸出目錄
    output_dir = get_output_directory(args.output_dir)
    
    # 生成圖表範例
    generate_chart_examples(output_dir, chart_types, args.force)


if __name__ == "__main__":
    main()
