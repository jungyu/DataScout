#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
存儲處理器工廠
用於根據配置創建不同的存儲處理器
"""

from typing import Dict, Any, Union, Type, List
from persistence.core.storage_interface import StorageInterface
from persistence.handlers.rabbitmq_handler import RabbitMQHandler
from persistence.handlers.elasticsearch_handler import ElasticsearchHandler
from persistence.handlers.clickhouse_handler import ClickHouseHandler
from persistence.handlers.postgresql_handler import PostgreSQLHandler
from persistence.core.exceptions import ConfigError

class StorageFactory:
    """存儲處理器工廠類"""
    
    # 存儲處理器映射表
    _handlers: Dict[str, Type[StorageInterface]] = {
        "rabbitmq": RabbitMQHandler,
        "elasticsearch": ElasticsearchHandler,
        "clickhouse": ClickHouseHandler,
        "postgresql": PostgreSQLHandler
    }
    
    @classmethod
    def create_handler(cls, storage_type: str, config: Union[Dict[str, Any], Any]) -> StorageInterface:
        """創建存儲處理器
        
        Args:
            storage_type: 存儲類型，如 "rabbitmq", "elasticsearch" 等
            config: 配置對象，可以是字典或配置類實例
            
        Returns:
            存儲處理器實例
            
        Raises:
            ConfigError: 當存儲類型不支持時
        """
        # 獲取處理器類
        handler_class = cls._handlers.get(storage_type.lower())
        if not handler_class:
            raise ConfigError(f"Unsupported storage type: {storage_type}")
        
        # 創建處理器實例
        return handler_class(config)
    
    @classmethod
    def register_handler(cls, storage_type: str, handler_class: Type[StorageInterface]) -> None:
        """註冊存儲處理器
        
        Args:
            storage_type: 存儲類型
            handler_class: 處理器類
        """
        cls._handlers[storage_type.lower()] = handler_class
    
    @classmethod
    def get_supported_types(cls) -> List[str]:
        """獲取支持的存儲類型列表
        
        Returns:
            存儲類型列表
        """
        return list(cls._handlers.keys()) 