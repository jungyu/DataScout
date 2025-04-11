"""瀏覽器指紋配置模塊"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional, List

@dataclass
class BrowserFingerprintConfig:
    """瀏覽器指紋配置類"""
    
    id: str
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # 指紋生成配置
    user_agent: Optional[str] = None
    platform: Optional[str] = None
    screen_resolution: Optional[str] = None
    color_depth: Optional[int] = None
    pixel_ratio: Optional[float] = None
    language: Optional[str] = None
    timezone: Optional[str] = None
    plugins: List[str] = field(default_factory=list)
    fonts: List[str] = field(default_factory=list)
    
    # 統計信息
    success_count: int = 0
    fail_count: int = 0
    total_count: int = 0
    last_used: Optional[datetime] = None
    
    def validate(self) -> bool:
        """驗證配置是否有效"""
        return bool(self.id)
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            'id': self.id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'user_agent': self.user_agent,
            'platform': self.platform,
            'screen_resolution': self.screen_resolution,
            'color_depth': self.color_depth,
            'pixel_ratio': self.pixel_ratio,
            'language': self.language,
            'timezone': self.timezone,
            'plugins': self.plugins,
            'fonts': self.fonts,
            'success_count': self.success_count,
            'fail_count': self.fail_count,
            'total_count': self.total_count,
            'last_used': self.last_used.isoformat() if self.last_used else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BrowserFingerprintConfig':
        """從字典創建實例"""
        if not data:
            raise ValueError("配置數據不能為空")
            
        if 'created_at' in data:
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if 'updated_at' in data:
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        if 'last_used' in data and data['last_used']:
            data['last_used'] = datetime.fromisoformat(data['last_used'])
            
        return cls(**data) 