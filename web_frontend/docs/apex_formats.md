# ApexCharts JSON 格式規範

本文件說明了 ApexCharts 應用程式中使用的 JSON 資料格式標準。所有上傳或使用的 JSON 檔案應遵循此格式，以確保圖表能夠正確顯示。

## 基本結構

ApexCharts JSON 資料必須包含以下基本結構：

```json
{
  "series": [
    {
      "name": "系列名稱",
      "data": [10, 41, 35, 51, 49, 62, 69, 91, 148]
    }
  ],
  "chart": {
    "type": "圖表類型",
    "height": 350
  },
  "xaxis": {
    "categories": ["標籤1", "標籤2", "標籤3", ...]
  },
  "title": {
    "text": "圖表標題"
  },
  "annotations": {
    "xaxis": [
      {
        "x": "標籤3",
        "strokeDashArray": 0,
        "borderColor": "#775DD0",
        "label": {
          "text": "X軸標註"
        }
      }
    ],
    "yaxis": [
      {
        "y": 80,
        "y2": 100,
        "strokeDashArray": 5,
        "borderColor": "#FEB019",
        "fillColor": "#FEB019",
        "opacity": 0.1,
        "label": {
          "text": "Y軸範圍標註"
        }
      }
    ],
    "points": [
      {
        "x": "標籤4",
        "y": 62,
        "marker": {
          "size": 6,
          "fillColor": "#FF4560",
          "strokeColor": "#fff",
          "strokeWidth": 2
        },
        "label": {
          "text": "點標註"
        }
      }
    ]
  }
}
```

## 必要欄位說明

| 欄位 | 類型 | 說明 | 是否必須 |
|------|------|------|---------|
| `series` | 陣列 | 包含一個或多個資料系列的陣列 | 必填 |
| `series[].name` | 字串 | 資料系列的名稱（顯示在圖例中） | 必填 |
| `series[].data` | 數值陣列 或 物件陣列 | 資料點的值 | 必填 |
| `chart.type` | 字串 | 圖表類型，如 `"line"`, `"bar"`, `"pie"` 等 | 必填 |
| `xaxis.categories` | 字串陣列 | X 軸的標籤（線形圖、柱狀圖等適用） | 大多數圖表必填 |

## 樣式與配置欄位

| 欄位 | 類型 | 說明 | 是否必須 |
|------|------|------|---------|
| `chart.height` | 數值 | 圖表高度 | 選填，預設為 自動 |
| `stroke` | 物件 | 線條相關設定 | 選填 |
| `stroke.curve` | 字串 | 線條曲線類型，如 `"smooth"`, `"straight"` | 選填 |
| `colors` | 字串陣列 | 資料系列的顏色 | 選填 |
| `fill.type` | 字串 | 填充類型，如 `"solid"`, `"gradient"` | 選填 |
| `markers` | 物件 | 資料點標記設定 | 選填 |
| `dataLabels` | 物件 | 資料標籤設定 | 選填 |

## 圖表類型

ApexCharts 支援以下主要圖表類型：

- `line`: 折線圖
- `area`: 區域圖
- `bar`: 柱狀圖/條形圖
- `pie`: 圓餅圖
- `donut`: 環形圖
- `radar`: 雷達圖
- `polarArea`: 極座標圖
- `radialBar`: 放射狀長條圖
- `scatter`: 散點圖
- `bubble`: 氣泡圖
- `heatmap`: 熱圖
- `candlestick`: 蠟燭圖
- `boxPlot`: 箱型圖
- `treemap`: 樹狀圖

## 特殊格式

### 散點圖與氣泡圖

散點圖和氣泡圖的資料格式需要為每個點提供 X 和 Y 座標：

```json
{
  "chart": {
    "type": "scatter",
    "height": 350
  },
  "series": [
    {
      "name": "範本 A",
      "data": [
        { "x": 16.4, "y": 5.4 },
        { "x": 21.7, "y": 2 },
        { "x": 25.4, "y": 3 }
      ]
    },
    {
      "name": "範本 B",
      "data": [
        { "x": 36.4, "y": 13.4 },
        { "x": 1.7, "y": 11 },
        { "x": 5.4, "y": 8 }
      ]
    }
  ],
  "xaxis": {
    "type": "numeric"
  },
  "yaxis": {
    "type": "numeric"
  }
}
```

氣泡圖還需要提供 `z` 值來指定氣泡大小：

```json
{
  "chart": {
    "type": "bubble",
    "height": 350
  },
  "series": [
    {
      "name": "氣泡 A",
      "data": [
        { "x": 25, "y": 50, "z": 15 },
        { "x": 40, "y": 30, "z": 22 },
        { "x": 70, "y": 60, "z": 35 }
      ]
    }
  ],
  "xaxis": {
    "type": "numeric"
  },
  "yaxis": {
    "type": "numeric"
  }
}
```

### 時間序列資料

時間序列圖表的 X 軸應設定為 datetime 類型：

```json
{
  "chart": {
    "type": "line",
    "height": 350
  },
  "series": [
    {
      "name": "銷售額",
      "data": [
        { "x": 1617321600000, "y": 54 },
        { "x": 1617408000000, "y": 63 },
        { "x": 1617494400000, "y": 60 }
      ]
    }
  ],
  "xaxis": {
    "type": "datetime"
  },
  "title": {
    "text": "銷售趨勢"
  }
}
```

## 例子

### 多系列折線圖範例

```json
{
  "chart": {
    "type": "line",
    "height": 350
  },
  "series": [
    {
      "name": "網站流量",
      "data": [31, 40, 28, 51, 42, 109, 100]
    },
    {
      "name": "轉換率",
      "data": [11, 32, 45, 32, 34, 52, 41]
    }
  ],
  "xaxis": {
    "categories": ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
  },
  "title": {
    "text": "網站表現統計"
  },
  "stroke": {
    "curve": "smooth",
    "width": 2
  },
  "markers": {
    "size": 5
  }
}
```

### 圓餅圖範例

```json
{
  "chart": {
    "type": "pie",
    "height": 350
  },
  "series": [44, 55, 13, 43, 22],
  "labels": ["團隊A", "團隊B", "團隊C", "團隊D", "團隊E"],
  "title": {
    "text": "團隊績效佔比"
  },
  "responsive": [
    {
      "breakpoint": 480,
      "options": {
        "chart": {
          "width": 300
        },
        "legend": {
          "position": "bottom"
        }
      }
    }
  ]
}
```

## 注意事項

1. JSON 格式必須有效，所有字串需要用雙引號包圍，不支援單引號
2. ApexCharts 配置非常靈活，可深度自訂各種視覺元素
3. 許多配置項可以遞迴套用（例如顏色、字型、大小等）
4. 時間序列資料可使用時間戳（毫秒）或 ISO 字串格式
5. 可以使用 `responsive` 陣列定義不同螢幕尺寸下的配置
