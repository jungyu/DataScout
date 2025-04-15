# DataScout Extractors

這是一個通用的數據提取器集合，用於從各種數據源中提取和處理數據。

## 功能特點

- 支持多種數據源的提取（網頁、API、文件等）
- 可擴展的提取器架構
- 內建數據清理和轉換功能
- 支持自定義提取規則

## 安裝

```bash
pip install data_scout_extractors
```

## 使用方法

### 基本用法

```python
from data_scout_extractors import BaseExtractor

# 創建提取器實例
extractor = BaseExtractor()

# 提取數據
data = extractor.extract(source_data)
```

### 使用特定提取器

```python
from data_scout_extractors.handlers import HTMLHandler, JSONHandler

# HTML 提取
html_extractor = HTMLHandler()
html_data = html_extractor.extract(html_content)

# JSON 提取
json_extractor = JSONHandler()
json_data = json_extractor.extract(json_content)
```

## 目錄結構

```
extractors/
├── core/           # 核心提取功能
├── handlers/       # 特定數據類型的處理器
└── tests/          # 測試文件
```

## 開發指南

1. 克隆倉庫
2. 安裝依賴：`pip install -r requirements.txt`
3. 運行測試：`python -m pytest tests/`

## 貢獻指南

1. Fork 倉庫
2. 創建特性分支
3. 提交更改
4. 推送到分支
5. 創建 Pull Request

## 授權

MIT License 