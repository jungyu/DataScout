#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
數據模型定義。
使用 Pydantic 模型定義 API 請求和響應結構。
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator


class ChartType(str, Enum):
    """圖表類型枚舉"""
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    RADAR = "radar" 
    SCATTER = "scatter"
    BUBBLE = "bubble"
    DOUGHNUT = "doughnut"
    POLAR_AREA = "polarArea"


class DataPoint(BaseModel):
    """數據點模型"""
    x: Any
    y: Any
    r: Optional[float] = None  # 用於氣泡圖
    

class Dataset(BaseModel):
    """數據集模型"""
    label: str
    data: List[Any]
    backgroundColor: Optional[Any] = None
    borderColor: Optional[Any] = None
    borderWidth: Optional[int] = 1


class ChartData(BaseModel):
    """圖表數據模型"""
    labels: List[str]
    datasets: List[Dataset]


class ChartOptions(BaseModel):
    """圖表選項模型"""
    responsive: bool = True
    maintainAspectRatio: bool = False
    plugins: Dict[str, Any] = Field(default_factory=dict)
    scales: Optional[Dict[str, Any]] = None


class ChartRequest(BaseModel):
    """圖表請求模型"""
    type: ChartType
    data: ChartData
    options: Optional[ChartOptions] = None
    

class FileInfo(BaseModel):
    """文件信息模型"""
    name: str
    type: str
    size: str
    updated: str


class UploadResponse(BaseModel):
    """文件上傳響應模型"""
    filename: str
    size: int
    description: Optional[str] = None
    status: str


class OlapOperation(BaseModel):
    """OLAP 操作模型"""
    type: str
    source: str
    filters: Optional[Dict[str, Any]] = None
    dimensions: Optional[List[str]] = None
    measures: Optional[List[str]] = None
    sort_by: Optional[List[Dict[str, str]]] = None
    
    @validator('type')
    def validate_operation_type(cls, v):
        """驗證操作類型"""
        allowed_types = ['filter', 'group', 'pivot', 'aggregate', 'sort', 'window']
        if v not in allowed_types:
            raise ValueError(f"操作類型必須是以下之一: {', '.join(allowed_types)}")
        return v
