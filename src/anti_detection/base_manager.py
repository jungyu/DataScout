#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
基礎管理器類

此模組提供所有管理器類的基礎功能，包括：
1. 配置文件管理
2. 隊列管理
3. 統計更新
4. 資源清理
"""

import os
import json
import logging
from typing import Dict, List, Type, TypeVar, Generic, Optional
from queue import Queue
from .base_config import BaseConfig

T = TypeVar('T', bound=BaseConfig)

class BaseManager(Generic[T]):
    """基礎管理器類"""
    
    def __init__(
        self,
        config_class: Type[T],
        config_file: str,
        max_size: int = 100,
        min_success_rate: float = 0.5
    ):
        """
        初始化管理器
        
        Args:
            config_class: 配置類
            config_file: 配置文件路徑
            max_size: 最大配置數量
            min_success_rate: 最小成功率
        """
        self.config_class = config_class
        self.config_file = config_file
        self.max_size = max_size
        self.min_success_rate = min_success_rate
        self.configs: Dict[str, T] = {}
        self.queue: Queue = Queue()
        self.logger = logging.getLogger(self.__class__.__name__)
        
        self._load_configs()
        self._init_queue()
    
    def _load_configs(self):
        """加載配置文件"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.configs = {
                        k: self.config_class.from_dict(v)
                        for k, v in data.items()
                    }
        except Exception as e:
            self.logger.error(f"加載配置文件失敗: {e}")
    
    def _save_configs(self):
        """保存配置文件"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(
                    {k: v.to_dict() for k, v in self.configs.items()},
                    f,
                    indent=2,
                    ensure_ascii=False
                )
        except Exception as e:
            self.logger.error(f"保存配置文件失敗: {e}")
    
    def _init_queue(self):
        """初始化隊列"""
        # 清空隊列
        while not self.queue.empty():
            self.queue.get()
        
        # 按成功率排序並添加到隊列
        sorted_configs = sorted(
            self.configs.values(),
            key=lambda x: x.success_rate,
            reverse=True
        )
        for config in sorted_configs:
            if config.success_rate >= self.min_success_rate:
                self.queue.put(config)
    
    def get_config(self) -> Optional[T]:
        """獲取一個配置"""
        try:
            return self.queue.get_nowait()
        except:
            return None
    
    def update_stats(self, config: T, success: bool):
        """更新統計信息"""
        config.update_stats(success)
        self._save_configs()
        self._init_queue()
    
    def add_config(self, key: str, config: T):
        """添加配置"""
        if len(self.configs) >= self.max_size:
            # 移除成功率最低的配置
            worst_config = min(
                self.configs.values(),
                key=lambda x: x.success_rate
            )
            self.configs.pop(worst_config.__dict__['key'])
        
        self.configs[key] = config
        self._save_configs()
        self._init_queue()
    
    def remove_config(self, key: str):
        """移除配置"""
        if key in self.configs:
            del self.configs[key]
            self._save_configs()
            self._init_queue()
    
    def clear(self):
        """清空所有配置"""
        self.configs.clear()
        self._save_configs()
        self._init_queue() 