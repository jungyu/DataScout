# Adapter 包

## 專案概述

Adapter 包提供了一個靈活的適配器模式實現，用於數據轉換和接口適配。它支持多種數據格式的轉換，並提供了簡單的裝飾器語法來實現適配功能。

## 安裝

```bash
# 開發模式安裝
pip install -e .

# 或直接安裝
pip install adapter
```

## 使用方式

### 基本使用

```python
from adapter import adapt, BaseAdapter

# 定義適配器
class MyAdapter(BaseAdapter):
    def adapt(self, data):
        # 實現數據轉換邏輯
        return transformed_data

# 使用裝飾器
@adapt(MyAdapter)
def my_function(data):
    return process_data(data)
```

### 使用註冊表

```python
from adapter import AdapterRegistry

# 創建註冊表
registry = AdapterRegistry()

# 註冊適配器
registry.register('format_a', 'format_b', MyAdapter)

# 使用適配器
result = registry.adapt('format_a', 'format_b', data)
```

### 使用轉換器

```python
from adapter import BaseTransformer

class MyTransformer(BaseTransformer):
    def transform(self, data):
        # 實現轉換邏輯
        return transformed_data

# 使用轉換器
transformer = MyTransformer()
result = transformer.transform(data)
```

## 目錄結構

```
adapter/
├── core/           # 核心組件
├── decorators/     # 裝飾器
├── persistence/    # 持久化
├── transformers/   # 轉換器
└── adapters/       # 適配器實現
```

## 主要功能

1. 適配器模式實現
   - 基礎適配器類
   - 適配器註冊表
   - 裝飾器支持

2. 數據轉換
   - 轉換器基類
   - 自定義轉換邏輯
   - 批量轉換支持

3. 持久化
   - 數據存儲
   - 狀態管理
   - 緩存支持

## 注意事項

1. 確保在虛擬環境中安裝
2. 檢查依賴版本兼容性
3. 遵循適配器設計模式的最佳實踐
4. 注意數據轉換的性能影響

## 依賴套件

### 核心依賴
- pydantic: 數據驗證
- typing-extensions: 類型提示擴展
- loguru: 日誌管理

### 開發依賴
- pytest: 測試框架
- black: 代碼格式化
- isort: 導入排序
- mypy: 類型檢查 