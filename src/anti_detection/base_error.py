#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
基礎錯誤處理類

此模組提供所有錯誤類的基礎功能，包括：
1. 錯誤碼管理
2. 錯誤信息格式化
3. 錯誤追蹤
4. 錯誤恢復
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

class BaseError(Exception):
    """基礎錯誤類"""
    
    def __init__(
        self,
        code: int,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        初始化錯誤
        
        Args:
            code: 錯誤碼
            message: 錯誤信息
            details: 詳細信息
        """
        self.code = code
        self.message = message
        self.details = details or {}
        self.timestamp = datetime.now()
        self.logger = logging.getLogger(self.__class__.__name__)
        
        super().__init__(self.format_message())
        self._log_error()
    
    def format_message(self) -> str:
        """格式化錯誤信息"""
        return f"[{self.code}] {self.message}"
    
    def _log_error(self):
        """記錄錯誤"""
        self.logger.error(
            f"{self.format_message()}\n"
            f"Details: {self.details}\n"
            f"Timestamp: {self.timestamp}"
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            'code': self.code,
            'message': self.message,
            'details': self.details,
            'timestamp': self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseError':
        """從字典創建錯誤"""
        return cls(
            code=data['code'],
            message=data['message'],
            details=data.get('details')
        )
    
    def recover(self) -> bool:
        """嘗試恢復錯誤"""
        try:
            # 子類實現具體的恢復邏輯
            return True
        except Exception as e:
            self.logger.error(f"恢復失敗: {e}")
            return False 