#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
中央氣象局 API 配置
"""

from typing import Dict, Any, Optional
from api_client.core.config import APIConfig

class CWAConfig(APIConfig):
    """中央氣象局 API 配置類"""
    
    def __init__(self, api_key: str, **kwargs):
        """初始化配置
        
        Args:
            api_key: API 金鑰
            **kwargs: 其他配置參數
        """
        # 設置基本配置
        config = {
            "api_type": "rest",
            "base_url": "https://opendata.cwa.gov.tw/api/v1/rest/datastore",
            "version": "v1",
            "timeout": 30,
            "retry_times": 3,
            
            # 認證配置
            "auth_type": "api_key",
            "api_key": api_key,
            "api_key_header": "Authorization",
            
            # 請求配置
            "headers": {
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            
            # 響應配置
            "response_type": "json",
            "success_codes": [200],
            "error_codes": [400, 401, 403, 404, 500]
        }
        
        # 更新配置
        config.update(kwargs)
        
        # 調用父類初始化
        super().__init__(**config)
    
    def validate(self) -> bool:
        """驗證配置
        
        Returns:
            bool: 配置是否有效
        """
        if not self.api_key:
            raise ValueError("API 金鑰是必需的")
        return super().validate() 