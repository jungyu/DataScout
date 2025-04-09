#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
基礎配置類

此模組提供所有配置類的基礎功能，包括：
1. 配置驗證
2. 配置轉換
3. 配置比較
4. 配置統計
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class BaseConfig:
    """基礎配置類"""
    
    # 基本屬性
    id: str
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # 統計信息
    total_uses: int = 0
    success_count: int = 0
    failure_count: int = 0
    last_used: Optional[datetime] = None
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    
    # 元數據
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def validate(self) -> bool:
        """驗證配置"""
        try:
            # 子類實現具體的驗證邏輯
            return True
        except Exception:
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            'id': self.id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'total_uses': self.total_uses,
            'success_count': self.success_count,
            'failure_count': self.failure_count,
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'last_success': self.last_success.isoformat() if self.last_success else None,
            'last_failure': self.last_failure.isoformat() if self.last_failure else None,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseConfig':
        """從字典創建配置"""
        return cls(
            id=data['id'],
            created_at=datetime.fromisoformat(data['created_at']),
            updated_at=datetime.fromisoformat(data['updated_at']),
            total_uses=data['total_uses'],
            success_count=data['success_count'],
            failure_count=data['failure_count'],
            last_used=datetime.fromisoformat(data['last_used']) if data['last_used'] else None,
            last_success=datetime.fromisoformat(data['last_success']) if data['last_success'] else None,
            last_failure=datetime.fromisoformat(data['last_failure']) if data['last_failure'] else None,
            metadata=data['metadata']
        )
    
    def update_stats(self, success: bool):
        """更新統計信息"""
        self.total_uses += 1
        if success:
            self.success_count += 1
            self.last_success = datetime.now()
        else:
            self.failure_count += 1
            self.last_failure = datetime.now()
        self.last_used = datetime.now()
        self.updated_at = datetime.now()
    
    @property
    def success_rate(self) -> float:
        """計算成功率"""
        if self.total_uses == 0:
            return 0.0
        return self.success_count / self.total_uses
    
    def __eq__(self, other: Any) -> bool:
        """比較配置是否相等"""
        if not isinstance(other, BaseConfig):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        """計算哈希值"""
        return hash(self.id) 