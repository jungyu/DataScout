#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
提取器類型定義模組

提供提取器相關的類型定義，包括：
1. 配置類型
2. 狀態類型
3. 結果類型
"""

from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, asdict

@dataclass
class ExtractorConfig:
    """提取器配置基類"""
    name: str
    description: str
    version: str = "1.0.0"
    enabled: bool = True
    timeout: Optional[float] = None
    retry_count: int = 3
    retry_delay: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典
        
        Returns:
            Dict[str, Any]: 字典表示
        """
        return asdict(self)
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExtractorConfig":
        """從字典創建
        
        Args:
            data: 字典數據
            
        Returns:
            ExtractorConfig: 配置對象
        """
        return cls(**data)

@dataclass
class ExtractorState:
    """提取器狀態基類"""
    is_initialized: bool = False
    is_running: bool = False
    error_count: int = 0
    last_error: Optional[str] = None
    last_success: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典
        
        Returns:
            Dict[str, Any]: 字典表示
        """
        return asdict(this)
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExtractorState":
        """從字典創建
        
        Args:
            data: 字典數據
            
        Returns:
            ExtractorState: 狀態對象
        """
        return cls(**data)

@dataclass
class ExtractorResult:
    """提取器結果基類"""
    success: bool
    data: Any
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典
        
        Returns:
            Dict[str, Any]: 字典表示
        """
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "metadata": self.metadata
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExtractorResult":
        """從字典創建
        
        Args:
            data: 字典數據
            
        Returns:
            ExtractorResult: 結果對象
        """
        return cls(**data) 