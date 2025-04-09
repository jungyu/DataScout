#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
反檢測配置類

此模組提供反檢測配置的定義和管理，包括：
1. 反檢測配置驗證
2. 反檢測策略管理
3. 反檢測性能統計
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime

from ..base_config import BaseConfig
from .proxy_config import ProxyConfig
from .user_agent_config import UserAgentConfig
from .delay_config import DelayConfig

@dataclass
class AntiDetectionConfig(BaseConfig):
    """反檢測配置類"""
    
    # 基本設置
    headless: bool = True
    window_size: Dict[str, int] = field(default_factory=lambda: {"width": 1920, "height": 1080})
    page_load_timeout: int = 30
    script_timeout: int = 30
    
    # 代理設置
    use_proxy: bool = False
    proxies: List[ProxyConfig] = field(default_factory=list)
    proxy_rotation_strategy: str = "round_robin"  # round_robin, random, performance
    
    # 用戶代理設置
    use_random_user_agent: bool = True
    user_agents: List[UserAgentConfig] = field(default_factory=list)
    user_agent_rotation_strategy: str = "round_robin"  # round_robin, random, performance
    
    # 延遲設置
    delay_config: DelayConfig = field(default_factory=DelayConfig)
    
    # 檢測設置
    max_retries: int = 3
    retry_delay: int = 5
    detection_threshold: float = 0.8
    
    def validate(self) -> bool:
        """驗證反檢測配置"""
        try:
            # 檢查窗口大小
            if not (0 < self.window_size["width"] <= 7680 and 0 < self.window_size["height"] <= 4320):
                return False
            
            # 檢查超時設置
            if not (0 < self.page_load_timeout <= 300 and 0 < self.script_timeout <= 300):
                return False
            
            # 檢查代理設置
            if self.use_proxy and not self.proxies:
                return False
            
            # 檢查用戶代理設置
            if self.use_random_user_agent and not self.user_agents:
                return False
            
            # 檢查延遲配置
            if not self.delay_config.validate():
                return False
            
            # 檢查檢測設置
            if not (0 < self.max_retries <= 10 and 0 < self.retry_delay <= 60):
                return False
            
            return True
        except Exception:
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        data = super().to_dict()
        data.update({
            'headless': self.headless,
            'window_size': self.window_size,
            'page_load_timeout': self.page_load_timeout,
            'script_timeout': self.script_timeout,
            'use_proxy': self.use_proxy,
            'proxies': [proxy.to_dict() for proxy in self.proxies],
            'proxy_rotation_strategy': self.proxy_rotation_strategy,
            'use_random_user_agent': self.use_random_user_agent,
            'user_agents': [ua.to_dict() for ua in self.user_agents],
            'user_agent_rotation_strategy': self.user_agent_rotation_strategy,
            'delay_config': self.delay_config.to_dict(),
            'max_retries': self.max_retries,
            'retry_delay': self.retry_delay,
            'detection_threshold': self.detection_threshold
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AntiDetectionConfig':
        """從字典創建配置"""
        config = super().from_dict(data)
        return cls(
            id=config.id,
            headless=data.get('headless', True),
            window_size=data.get('window_size', {"width": 1920, "height": 1080}),
            page_load_timeout=data.get('page_load_timeout', 30),
            script_timeout=data.get('script_timeout', 30),
            use_proxy=data.get('use_proxy', False),
            proxies=[ProxyConfig.from_dict(p) for p in data.get('proxies', [])],
            proxy_rotation_strategy=data.get('proxy_rotation_strategy', 'round_robin'),
            use_random_user_agent=data.get('use_random_user_agent', True),
            user_agents=[UserAgentConfig.from_dict(ua) for ua in data.get('user_agents', [])],
            user_agent_rotation_strategy=data.get('user_agent_rotation_strategy', 'round_robin'),
            delay_config=DelayConfig.from_dict(data.get('delay_config', {})),
            max_retries=data.get('max_retries', 3),
            retry_delay=data.get('retry_delay', 5),
            detection_threshold=data.get('detection_threshold', 0.8),
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
    
    def get_next_proxy(self) -> Optional[ProxyConfig]:
        """獲取下一個代理"""
        if not self.proxies:
            return None
        
        if self.proxy_rotation_strategy == "round_robin":
            # 輪詢策略
            proxy = self.proxies[self.total_uses % len(self.proxies)]
        elif self.proxy_rotation_strategy == "random":
            # 隨機策略
            import random
            proxy = random.choice(self.proxies)
        else:
            # 性能策略
            proxy = max(self.proxies, key=lambda x: x.success_rate)
        
        return proxy
    
    def get_next_user_agent(self) -> Optional[UserAgentConfig]:
        """獲取下一個用戶代理"""
        if not self.user_agents:
            return None
        
        if self.user_agent_rotation_strategy == "round_robin":
            # 輪詢策略
            user_agent = self.user_agents[self.total_uses % len(self.user_agents)]
        elif self.user_agent_rotation_strategy == "random":
            # 隨機策略
            import random
            user_agent = random.choice(self.user_agents)
        else:
            # 性能策略
            user_agent = max(self.user_agents, key=lambda x: x.success_rate)
        
        return user_agent 