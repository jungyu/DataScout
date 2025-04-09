#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Cookie 配置

此模組提供 Cookie 相關的配置類，包括：
1. CookieConfig：單個 Cookie 的配置
2. CookiePoolConfig：Cookie 池的配置
"""

import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

@dataclass
class CookieConfig:
    """Cookie 配置"""
    domain: str = ""  # Cookie 域名
    path: str = "/"  # Cookie 路徑
    name: str = ""  # Cookie 名稱
    value: str = ""  # Cookie 值
    secure: bool = True  # 是否只通過 HTTPS 傳輸
    http_only: bool = True  # 是否只允許 HTTP 訪問
    same_site: str = "Lax"  # SameSite 屬性：Strict、Lax、None
    expiry: Optional[int] = None  # 過期時間（秒）
    created_at: int = field(default_factory=lambda: int(time.time()))
    last_used: int = field(default_factory=lambda: int(time.time()))
    use_count: int = 0
    success_count: int = 0
    fail_count: int = 0
    
    @property
    def success_rate(self) -> float:
        """計算成功率"""
        total = self.success_count + self.fail_count
        return self.success_count / total if total > 0 else 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "domain": self.domain,
            "path": self.path,
            "name": self.name,
            "value": self.value,
            "secure": self.secure,
            "http_only": self.http_only,
            "same_site": self.same_site,
            "expiry": self.expiry,
            "created_at": self.created_at,
            "last_used": self.last_used,
            "use_count": self.use_count,
            "success_count": self.success_count,
            "fail_count": self.fail_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CookieConfig':
        """從字典創建實例"""
        return cls(
            domain=data.get("domain", ""),
            path=data.get("path", "/"),
            name=data.get("name", ""),
            value=data.get("value", ""),
            secure=data.get("secure", True),
            http_only=data.get("http_only", True),
            same_site=data.get("same_site", "Lax"),
            expiry=data.get("expiry"),
            created_at=data.get("created_at", int(time.time())),
            last_used=data.get("last_used", int(time.time())),
            use_count=data.get("use_count", 0),
            success_count=data.get("success_count", 0),
            fail_count=data.get("fail_count", 0)
        )

@dataclass
class CookiePoolConfig:
    """Cookie 池配置"""
    max_size: int = 100  # 最大 Cookie 數量
    min_size: int = 10  # 最小 Cookie 數量
    cleanup_interval: int = 3600  # 清理間隔（秒）
    max_age: int = 86400  # 最大年齡（秒）
    min_success_rate: float = 0.8  # 最小成功率
    rotation_interval: int = 300  # 輪換間隔（秒）
    domains: List[str] = field(default_factory=list)  # 支持的域名列表
    paths: List[str] = field(default_factory=lambda: ["/"])  # 支持的路徑列表
    secure_only: bool = True  # 是否只使用安全 Cookie
    http_only_only: bool = True  # 是否只使用 HTTP-only Cookie
    same_site_policy: str = "Lax"  # SameSite 策略
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "max_size": self.max_size,
            "min_size": self.min_size,
            "cleanup_interval": self.cleanup_interval,
            "max_age": self.max_age,
            "min_success_rate": self.min_success_rate,
            "rotation_interval": self.rotation_interval,
            "domains": self.domains,
            "paths": self.paths,
            "secure_only": self.secure_only,
            "http_only_only": self.http_only_only,
            "same_site_policy": self.same_site_policy
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CookiePoolConfig':
        """從字典創建實例"""
        return cls(
            max_size=data.get("max_size", 100),
            min_size=data.get("min_size", 10),
            cleanup_interval=data.get("cleanup_interval", 3600),
            max_age=data.get("max_age", 86400),
            min_success_rate=data.get("min_success_rate", 0.8),
            rotation_interval=data.get("rotation_interval", 300),
            domains=data.get("domains", []),
            paths=data.get("paths", ["/"]),
            secure_only=data.get("secure_only", True),
            http_only_only=data.get("http_only_only", True),
            same_site_policy=data.get("same_site_policy", "Lax")
        ) 