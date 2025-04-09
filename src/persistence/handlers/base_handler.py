#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
存儲處理器基類模組
定義所有存儲處理器必須實現的接口
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from ..config.storage_config import StorageConfig
from src.captcha import CaptchaManager, CaptchaType
from src.captcha.third_party.config import ThirdPartyServiceConfig


class StorageHandler(ABC):
    """存儲處理器基類"""
    
    def __init__(self, config: StorageConfig):
        """初始化存儲處理器"""
        self.config = config
        if not config.validate():
            raise ValueError("配置驗證失敗")
    
    @abstractmethod
    def save_data(self, data: Dict[str, Any]) -> bool:
        """保存數據"""
        pass
    
    @abstractmethod
    def save_batch(self, data_list: List[Dict[str, Any]]) -> bool:
        """批量保存數據"""
        pass
    
    @abstractmethod
    def load_data(self, query: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """加載數據"""
        pass
    
    @abstractmethod
    def delete_data(self, query: Dict[str, Any]) -> bool:
        """刪除數據"""
        pass
    
    @abstractmethod
    def clear_data(self) -> bool:
        """清空數據"""
        pass
    
    @abstractmethod
    def get_data_count(self, query: Optional[Dict[str, Any]] = None) -> int:
        """獲取數據數量"""
        pass
    
    @abstractmethod
    def create_backup(self) -> bool:
        """創建備份"""
        pass
    
    @abstractmethod
    def restore_backup(self, backup_id: str) -> bool:
        """恢復備份"""
        pass
    
    @abstractmethod
    def list_backups(self) -> List[str]:
        """列出所有備份"""
        pass
    
    @abstractmethod
    def delete_backup(self, backup_id: str) -> bool:
        """刪除備份"""
        pass
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        pass 

# 創建第三方服務配置
third_party_config = ThirdPartyServiceConfig(
    type="2captcha",
    api_key="your_api_key",
    site_key="your_site_key"
)

# 創建驗證碼管理器
captcha_manager = CaptchaManager(
    driver=driver,
    third_party_service=third_party_config
)

# 檢測驗證碼
result = captcha_manager.detect_captcha()
if result:
    # 解決驗證碼
    success = captcha_manager.solve_captcha(result)
    if success:
        print("驗證碼解決成功")
    else:
        print("驗證碼解決失敗") 