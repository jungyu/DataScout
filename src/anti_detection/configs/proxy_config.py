#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
代理配置模組

此模組提供代理相關的配置類：
1. ProxyConfig - 單個代理的配置
2. ProxyPoolConfig - 代理池的配置
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from ..base_config import BaseConfig

@dataclass
class ProxyConfig(BaseConfig):
    """代理配置類
    
    用於配置單個代理的屬性，包括：
    1. 代理類型（HTTP/HTTPS/SOCKS）
    2. 代理地址和端口
    3. 認證信息
    4. 地理位置
    5. 性能指標
    6. 使用統計
    """
    
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
    
    # 代理類型
    proxy_type: str = "http"  # http, https, socks4, socks5
    
    # 代理地址
    host: str = ""
    port: int = 0
    
    # 認證信息
    username: Optional[str] = None
    password: Optional[str] = None
    
    # 地理位置
    country: str = ""
    region: str = ""
    city: str = ""
    isp: str = ""
    
    # 性能指標
    speed: float = 0.0  # 響應速度（毫秒）
    success_rate: float = 0.0  # 成功率
    last_check: datetime = field(default_factory=datetime.now)
    
    # 使用統計
    use_count: int = 0
    proxy_success_count: int = 0
    fail_count: int = 0
    proxy_last_used: Optional[datetime] = None
    
    # 元數據
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """轉換為字典格式"""
        data = super().to_dict()
        data.update({
            "proxy_type": self.proxy_type,
            "host": self.host,
            "port": self.port,
            "username": self.username,
            "password": self.password,
            "country": self.country,
            "region": self.region,
            "city": self.city,
            "isp": self.isp,
            "speed": self.speed,
            "success_rate": self.success_rate,
            "last_check": self.last_check.isoformat(),
            "use_count": self.use_count,
            "proxy_success_count": self.proxy_success_count,
            "fail_count": self.fail_count,
            "proxy_last_used": self.proxy_last_used.isoformat() if self.proxy_last_used else None
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ProxyConfig':
        """從字典創建實例"""
        config = super().from_dict(data)
        if "last_check" in data:
            data["last_check"] = datetime.fromisoformat(data["last_check"])
        if "proxy_last_used" in data and data["proxy_last_used"]:
            data["proxy_last_used"] = datetime.fromisoformat(data["proxy_last_used"])
        return cls(
            id=config.id,
            proxy_type=data.get("proxy_type", "http"),
            host=data.get("host", ""),
            port=data.get("port", 0),
            username=data.get("username"),
            password=data.get("password"),
            country=data.get("country", ""),
            region=data.get("region", ""),
            city=data.get("city", ""),
            isp=data.get("isp", ""),
            speed=data.get("speed", 0.0),
            success_rate=data.get("success_rate", 0.0),
            last_check=data.get("last_check", datetime.now()),
            use_count=data.get("use_count", 0),
            proxy_success_count=data.get("proxy_success_count", 0),
            fail_count=data.get("fail_count", 0),
            proxy_last_used=data.get("proxy_last_used"),
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
    
    @property
    def url(self) -> str:
        """獲取代理URL"""
        auth = f"{self.username}:{self.password}@" if self.username and self.password else ""
        return f"{self.proxy_type}://{auth}{self.host}:{self.port}"
    
    @property
    def location(self) -> str:
        """獲取地理位置信息"""
        parts = [p for p in [self.city, self.region, self.country] if p]
        return ", ".join(parts)
    
    def update_stats(self, success: bool):
        """更新使用統計"""
        self.use_count += 1
        if success:
            self.proxy_success_count += 1
        else:
            self.fail_count += 1
        self.proxy_last_used = datetime.now()
        self.success_rate = self.proxy_success_count / self.use_count if self.use_count > 0 else 0.0
        self.update_stats(success)

@dataclass
class ProxyPoolConfig(BaseConfig):
    """代理池配置類
    
    用於配置代理池的屬性，包括：
    1. 代理池大小限制
    2. 代理質量要求
    3. 更新策略
    4. 地理位置要求
    5. 性能要求
    """
    
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
    
    # 池大小限制
    max_size: int = 100
    min_size: int = 10
    
    # 更新設置
    update_interval: int = 300  # 更新間隔（秒）
    check_interval: int = 60  # 檢查間隔（秒）
    max_age: int = 86400  # 最大年齡（秒）
    
    # 質量要求
    min_success_rate: float = 0.8
    max_speed: float = 1000.0  # 最大響應時間（毫秒）
    
    # 地理位置要求
    allowed_countries: List[str] = field(default_factory=list)
    blocked_countries: List[str] = field(default_factory=list)
    allowed_regions: List[str] = field(default_factory=list)
    blocked_regions: List[str] = field(default_factory=list)
    
    # ISP要求
    allowed_isps: List[str] = field(default_factory=list)
    blocked_isps: List[str] = field(default_factory=list)
    
    # 代理類型要求
    allowed_types: List[str] = field(default_factory=lambda: ["http", "https", "socks4", "socks5"])
    
    # 元數據
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """轉換為字典格式"""
        data = super().to_dict()
        data.update({
            "max_size": self.max_size,
            "min_size": self.min_size,
            "update_interval": self.update_interval,
            "check_interval": self.check_interval,
            "max_age": self.max_age,
            "min_success_rate": self.min_success_rate,
            "max_speed": self.max_speed,
            "allowed_countries": self.allowed_countries,
            "blocked_countries": self.blocked_countries,
            "allowed_regions": self.allowed_regions,
            "blocked_regions": self.blocked_regions,
            "allowed_isps": self.allowed_isps,
            "blocked_isps": self.blocked_isps,
            "allowed_types": self.allowed_types
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ProxyPoolConfig':
        """從字典創建實例"""
        config = super().from_dict(data)
        return cls(
            id=config.id,
            max_size=data.get("max_size", 100),
            min_size=data.get("min_size", 10),
            update_interval=data.get("update_interval", 300),
            check_interval=data.get("check_interval", 60),
            max_age=data.get("max_age", 86400),
            min_success_rate=data.get("min_success_rate", 0.8),
            max_speed=data.get("max_speed", 1000.0),
            allowed_countries=data.get("allowed_countries", []),
            blocked_countries=data.get("blocked_countries", []),
            allowed_regions=data.get("allowed_regions", []),
            blocked_regions=data.get("blocked_regions", []),
            allowed_isps=data.get("allowed_isps", []),
            blocked_isps=data.get("blocked_isps", []),
            allowed_types=data.get("allowed_types", ["http", "https", "socks4", "socks5"]),
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
    
    def is_proxy_allowed(self, proxy: ProxyConfig) -> bool:
        """檢查代理是否符合要求"""
        # 檢查代理類型
        if proxy.proxy_type not in self.allowed_types:
            return False
        
        # 檢查成功率
        if proxy.success_rate < self.min_success_rate:
            return False
        
        # 檢查響應速度
        if proxy.speed > self.max_speed:
            return False
        
        # 檢查國家
        if self.allowed_countries and proxy.country not in self.allowed_countries:
            return False
        if proxy.country in self.blocked_countries:
            return False
        
        # 檢查地區
        if self.allowed_regions and proxy.region not in self.allowed_regions:
            return False
        if proxy.region in self.blocked_regions:
            return False
        
        # 檢查ISP
        if self.allowed_isps and proxy.isp not in self.allowed_isps:
            return False
        if proxy.isp in self.blocked_isps:
            return False
        
        return True 