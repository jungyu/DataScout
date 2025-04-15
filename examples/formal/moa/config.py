#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
農產品交易行情 API 配置
"""

from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class MOAConfig:
    """農產品交易行情 API 配置"""
    
    base_url: str = "https://data.moa.gov.tw/api/v1"
    timeout: int = 30
    response_type: str = "json"
    api_key: str = None
    
    def validate(self) -> None:
        """驗證配置"""
        if not self.base_url:
            raise ValueError("base_url 不能為空")
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式
        
        Returns:
            Dict[str, Any]: 配置字典
        """
        headers = {
            "Accept": "application/json"
        }
        
        # 如果有 API 金鑰，則添加到請求頭
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        return {
            "base_url": self.base_url,
            "timeout": self.timeout,
            "response_type": self.response_type,
            "headers": headers
        } 