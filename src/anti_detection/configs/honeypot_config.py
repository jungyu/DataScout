#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
蜜罐配置類

此模組提供蜜罐配置的定義和管理，包括：
1. 蜜罐檢測規則
2. 蜜罐特徵定義
3. 蜜罐處理策略
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime

from ..base_config import BaseConfig

@dataclass
class HoneypotConfig:
    """蜜罐配置類"""
    
    # 基本屬性（必需參數）
    id: str
    
    # 基本屬性（可選參數）
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # 統計信息
    total_uses: int = 0
    success_count: int = 0
    failure_count: int = 0
    last_used: Optional[datetime] = None
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    
    # 檢測規則
    check_invisible_elements: bool = True
    check_hidden_links: bool = True
    check_fake_forms: bool = True
    check_trap_inputs: bool = True
    
    # 特徵定義
    honeypot_classes: List[str] = field(default_factory=lambda: [
        "hidden", "display-none", "invisible", "trap"
    ])
    honeypot_ids: List[str] = field(default_factory=lambda: [
        "bot-trap", "spam-trap", "honey-pot"
    ])
    honeypot_attributes: List[str] = field(default_factory=lambda: [
        "data-bot-trap", "data-honeypot", "data-trap"
    ])
    
    # 處理策略
    ignore_honeypots: bool = True
    report_honeypots: bool = True
    max_honeypots_per_page: int = 5
    honeypot_timeout: int = 30
    
    # 元數據
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """初始化後的處理"""
        self.base_config = BaseConfig(
            id=self.id,
            created_at=self.created_at,
            updated_at=self.updated_at,
            total_uses=self.total_uses,
            success_count=self.success_count,
            failure_count=self.failure_count,
            last_used=self.last_used,
            last_success=self.last_success,
            last_failure=self.last_failure,
            metadata=self.metadata
        )
    
    def validate(self) -> bool:
        """驗證蜜罐配置"""
        try:
            # 檢查超時設置
            if self.honeypot_timeout <= 0:
                return False
            
            # 檢查最大蜜罐數量
            if self.max_honeypots_per_page <= 0:
                return False
            
            # 檢查特徵列表
            if not (self.honeypot_classes and self.honeypot_ids and self.honeypot_attributes):
                return False
            
            return True
        except Exception:
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        data = self.base_config.to_dict()
        data.update({
            'check_invisible_elements': self.check_invisible_elements,
            'check_hidden_links': self.check_hidden_links,
            'check_fake_forms': self.check_fake_forms,
            'check_trap_inputs': self.check_trap_inputs,
            'honeypot_classes': self.honeypot_classes,
            'honeypot_ids': self.honeypot_ids,
            'honeypot_attributes': self.honeypot_attributes,
            'ignore_honeypots': self.ignore_honeypots,
            'report_honeypots': self.report_honeypots,
            'max_honeypots_per_page': self.max_honeypots_per_page,
            'honeypot_timeout': self.honeypot_timeout
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HoneypotConfig':
        """從字典創建配置"""
        base_config = BaseConfig.from_dict(data)
        return cls(
            id=base_config.id,
            check_invisible_elements=data.get('check_invisible_elements', True),
            check_hidden_links=data.get('check_hidden_links', True),
            check_fake_forms=data.get('check_fake_forms', True),
            check_trap_inputs=data.get('check_trap_inputs', True),
            honeypot_classes=data.get('honeypot_classes', ["hidden", "display-none", "invisible", "trap"]),
            honeypot_ids=data.get('honeypot_ids', ["bot-trap", "spam-trap", "honey-pot"]),
            honeypot_attributes=data.get('honeypot_attributes', ["data-bot-trap", "data-honeypot", "data-trap"]),
            ignore_honeypots=data.get('ignore_honeypots', True),
            report_honeypots=data.get('report_honeypots', True),
            max_honeypots_per_page=data.get('max_honeypots_per_page', 5),
            honeypot_timeout=data.get('honeypot_timeout', 30),
            created_at=base_config.created_at,
            updated_at=base_config.updated_at,
            total_uses=base_config.total_uses,
            success_count=base_config.success_count,
            failure_count=base_config.failure_count,
            last_used=base_config.last_used,
            last_success=base_config.last_success,
            last_failure=base_config.last_failure,
            metadata=base_config.metadata
        )
    
    def update_stats(self, success: bool):
        """更新統計信息"""
        self.base_config.update_stats(success)
        self.total_uses = self.base_config.total_uses
        self.success_count = self.base_config.success_count
        self.failure_count = self.base_config.failure_count
        self.last_used = self.base_config.last_used
        self.last_success = self.base_config.last_success
        self.last_failure = self.base_config.last_failure
    
    def is_honeypot(self, element_data: Dict[str, Any]) -> bool:
        """
        檢查元素是否為蜜罐
        
        Args:
            element_data: 元素數據，包含class、id、attributes等信息
            
        Returns:
            是否為蜜罐
        """
        # 檢查class
        if any(cls in element_data.get('class', []) for cls in self.honeypot_classes):
            return True
        
        # 檢查id
        if element_data.get('id') in self.honeypot_ids:
            return True
        
        # 檢查屬性
        for attr in self.honeypot_attributes:
            if attr in element_data.get('attributes', {}):
                return True
        
        return False 