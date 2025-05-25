# 數據提取器

一個強大的數據提取工具包，支持多種數據源和提取方式。

## 功能特點

- 多種數據源支持（網頁、文件等）
- 異步操作支持
- 錯誤處理和重試機制
- 完整的日誌記錄
- 靈活的配置管理
- 命令行界面

## 安裝

```bash
pip install extractors
```

## 快速開始

### 命令行使用

```bash
# 從 URL 提取數據
extract https://example.com --type web

# 從文件提取數據
extract-file data.txt --type file
```

### 作為包使用

```python
from extractors import BaseExtractor, ExtractorConfig
from extractors.utils.logger import setup_logger

# 設置日誌
setup_logger()

# 創建配置
config = ExtractorConfig(
    url="https://example.com",
    extractor_type="web"
)

# 創建提取器
extractor = BaseExtractor(config)

# 執行提取
result = await extractor.extract()
```

## 開發

### 安裝開發依賴

```bash
pip install -e ".[dev]"
```

### 運行測試

```bash
pytest
```

### 代碼格式化

```bash
black .
isort .
```

## 文檔

詳細文檔請參見 [文檔目錄](docs/)。

## 許可證

MIT License 