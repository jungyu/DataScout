#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Flow 基類

此模組提供了工作流程的基礎類別，用於實現各種自動化流程。
"""

import logging
from typing import Dict, Any

class Flow:
    """工作流程基類"""
    
    def __init__(self):
        """初始化工作流程"""
        self.logger = logging.getLogger(self.__class__.__name__)
        self._running = False
    
    async def start(self) -> None:
        """啟動工作流程"""
        self._running = True
        self.logger.info(f"{self.__class__.__name__} 已啟動")
    
    async def stop(self) -> None:
        """停止工作流程"""
        self._running = False
        self.logger.info(f"{self.__class__.__name__} 已停止")
    
    async def handle_message(self, message: Dict[str, Any]) -> None:
        """處理消息
        
        Args:
            message: 消息內容
        """
        raise NotImplementedError("子類必須實現此方法")
    
    @property
    def is_running(self) -> bool:
        """檢查工作流程是否正在運行"""
        return self._running 