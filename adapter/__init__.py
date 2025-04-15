#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
資料轉換適配器模組 (Data Adapter Module)

提供靈活的資料轉換功能，將爬蟲或 API 獲取的資料轉換為適合各種資料庫存儲的格式。

主要功能：
- 資料欄位映射：將來源資料欄位映射到目標資料庫欄位
- 資料類型轉換：自動轉換資料類型以符合目標資料庫要求
- 資料驗證：確保資料符合目標資料庫的約束條件
- 資料清洗：去除無效資料、處理缺失值等
- 資料轉換規則：支援自定義轉換規則
- 批量處理：高效處理大量資料

擴展性：
- 支援自定義轉換規則
- 支援自定義驗證規則
- 支援與各種資料庫的整合
- 支援與爬蟲和 API 客戶端的整合

使用方式：
```python
from adapter import DataAdapter
from adapter.transformers import FieldMapper, TypeConverter

# 創建適配器
adapter = DataAdapter(
    transformers=[
        FieldMapper({
            'source_field': 'target_field',
            'old_name': 'new_name'
        }),
        TypeConverter({
            'field_name': 'int',
            'date_field': 'datetime'
        })
    ]
)

# 轉換資料
transformed_data = adapter.transform(source_data)
```
"""

from adapter.core.adapter import DataAdapter
from adapter.core.transformer import Transformer
from adapter.transformers.field_mapper import FieldMapper
from adapter.transformers.type_converter import TypeConverter
from adapter.transformers.value_formatter import ValueFormatter
from adapter.transformers.data_validator import DataValidator
from adapter.transformers.data_cleaner import DataCleaner
from adapter.core.exceptions import (
    AdapterError,
    TransformationError,
    ValidationError,
    ConfigurationError
)

__version__ = '1.0.0'
__author__ = 'Aaron Yu (https://github.com/jungyu), Claude AI, Cursor AI'
__license__ = 'MIT'

__all__ = [
    # 核心類
    'DataAdapter',
    'Transformer',
    
    # 轉換器
    'FieldMapper',
    'TypeConverter',
    'ValueFormatter',
    'DataValidator',
    'DataCleaner',
    
    # 異常類
    'AdapterError',
    'TransformationError',
    'ValidationError',
    'ConfigurationError'
] 