#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
延遲配置類

此模組提供延遲配置的定義和管理，包括：
1. 延遲配置驗證
2. 延遲時間計算
3. 延遲策略管理
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

from ..base_config import BaseConfig

@dataclass
class DelayConfig(BaseConfig):
    """延遲配置類"""
    
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
    
    # 延遲設置
    page_load: Dict[str, float] = field(default_factory=lambda: {"min": 2.0, "max": 5.0})
    between_actions: Dict[str, float] = field(default_factory=lambda: {"min": 1.0, "max": 3.0})
    before_click: Dict[str, float] = field(default_factory=lambda: {"min": 0.5, "max": 2.0})
    typing_speed: Dict[str, float] = field(default_factory=lambda: {"min": 0.05, "max": 0.2})
    
    # 策略設置
    use_random_delay: bool = True
    use_human_like_delay: bool = True
    min_delay: float = 0.1
    max_delay: float = 10.0
    
    # 元數據
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def validate(self) -> bool:
        """驗證延遲配置"""
        try:
            # 檢查延遲範圍
            for delay_type in [self.page_load, self.between_actions, self.before_click, self.typing_speed]:
                if not (0 <= delay_type["min"] <= delay_type["max"] <= self.max_delay):
                    return False
            
            # 檢查最小延遲
            if self.min_delay < 0:
                return False
            
            return True
        except Exception:
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        data = super().to_dict()
        data.update({
            'page_load': self.page_load,
            'between_actions': self.between_actions,
            'before_click': self.before_click,
            'typing_speed': self.typing_speed,
            'use_random_delay': self.use_random_delay,
            'use_human_like_delay': self.use_human_like_delay,
            'min_delay': self.min_delay,
            'max_delay': self.max_delay
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DelayConfig':
        """從字典創建配置"""
        config = super().from_dict(data)
        return cls(
            id=config.id,
            page_load=data.get('page_load', {"min": 2.0, "max": 5.0}),
            between_actions=data.get('between_actions', {"min": 1.0, "max": 3.0}),
            before_click=data.get('before_click', {"min": 0.5, "max": 2.0}),
            typing_speed=data.get('typing_speed', {"min": 0.05, "max": 0.2}),
            use_random_delay=data.get('use_random_delay', True),
            use_human_like_delay=data.get('use_human_like_delay', True),
            min_delay=data.get('min_delay', 0.1),
            max_delay=data.get('max_delay', 10.0),
            created_at=config.created_at,
            updated_at=config.updated_at,
            total_uses=config.total_uses,
            success_count=config.success_count,
            failure_count=config.failure_count,
            last_used=config.last_used,
            last_success=config.last_success,
            last_failure=config.last_failure,
            metadata=config.metadata
        )
    
    def get_delay(self, delay_type: str) -> float:
        """獲取延遲時間"""
        if not self.use_random_delay:
            return self.min_delay
        
        delay_config = getattr(self, delay_type, self.between_actions)
        min_delay = max(delay_config["min"], self.min_delay)
        max_delay = min(delay_config["max"], self.max_delay)
        
        if self.use_human_like_delay:
            # 使用正態分佈生成更自然的延遲時間
            import random
            mean = (min_delay + max_delay) / 2
            std = (max_delay - min_delay) / 4
            delay = random.gauss(mean, std)
            return max(min_delay, min(delay, max_delay))
        else:
            # 使用均勻分佈生成延遲時間
            import random
            return random.uniform(min_delay, max_delay) 