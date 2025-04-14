"""
反檢測配置模組

此模組提供反檢測功能的配置管理，包括：
- 代理設置
- 用戶代理設置
- 瀏覽器指紋設置
- 延遲設置
- 重試設置
- 緩存設置
- 性能指標設置
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Union, Any

from ..exceptions import ConfigError


class AntiDetectionConfig:
    """反檢測配置類
    
    用於管理反檢測功能的配置，包括代理、用戶代理、瀏覽器指紋等設置。
    
    Attributes:
        id (str): 配置ID
        version (str): 配置版本
        description (str): 配置描述
        enabled (bool): 是否啟用
        created_at (datetime): 創建時間
        updated_at (datetime): 更新時間
        last_used (datetime): 最後使用時間
        headless (bool): 是否使用無頭模式
        window_size (Dict[str, int]): 窗口大小
        page_load_timeout (int): 頁面加載超時時間（秒）
        script_timeout (int): 腳本執行超時時間（秒）
        use_proxy (bool): 是否使用代理
        proxies (List[Dict[str, str]]): 代理列表
        use_random_user_agent (bool): 是否使用隨機用戶代理
        user_agents (List[str]): 用戶代理列表
        browser_fingerprint (Dict[str, Any]): 瀏覽器指紋設置
        anti_fingerprint (Dict[str, Any]): 反指紋設置
        delay_config (Dict[str, Any]): 延遲設置
        max_retries (int): 最大重試次數
        retry_delay (int): 重試延遲時間（秒）
        detection_threshold (float): 檢測閾值
        block_threshold (float): 封鎖閾值
        use_cache (bool): 是否使用緩存
        cache_duration (int): 緩存持續時間（秒）
        max_cache_size (int): 最大緩存大小
        metrics (Dict[str, Any]): 性能指標
        metadata (Dict[str, Any]): 元數據
    """
    
    def __init__(
        self,
        id: str = "default",
        version: str = "1.0.0",
        description: str = "Default anti-detection configuration",
        enabled: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        last_used: Optional[datetime] = None,
        headless: bool = False,
        window_size: Optional[Dict[str, int]] = None,
        page_load_timeout: int = 30,
        script_timeout: int = 30,
        use_proxy: bool = False,
        proxies: Optional[List[Dict[str, str]]] = None,
        use_random_user_agent: bool = False,
        user_agents: Optional[List[str]] = None,
        browser_fingerprint: Optional[Dict[str, Any]] = None,
        anti_fingerprint: Optional[Dict[str, Any]] = None,
        delay_config: Optional[Dict[str, Any]] = None,
        max_retries: int = 3,
        retry_delay: int = 5,
        detection_threshold: float = 0.8,
        block_threshold: float = 0.9,
        use_cache: bool = True,
        cache_duration: int = 3600,
        max_cache_size: int = 1000,
        metrics: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """初始化反檢測配置
        
        Args:
            id: 配置ID
            version: 配置版本
            description: 配置描述
            enabled: 是否啟用
            created_at: 創建時間
            updated_at: 更新時間
            last_used: 最後使用時間
            headless: 是否使用無頭模式
            window_size: 窗口大小
            page_load_timeout: 頁面加載超時時間（秒）
            script_timeout: 腳本執行超時時間（秒）
            use_proxy: 是否使用代理
            proxies: 代理列表
            use_random_user_agent: 是否使用隨機用戶代理
            user_agents: 用戶代理列表
            browser_fingerprint: 瀏覽器指紋設置
            anti_fingerprint: 反指紋設置
            delay_config: 延遲設置
            max_retries: 最大重試次數
            retry_delay: 重試延遲時間（秒）
            detection_threshold: 檢測閾值
            block_threshold: 封鎖閾值
            use_cache: 是否使用緩存
            cache_duration: 緩存持續時間（秒）
            max_cache_size: 最大緩存大小
            metrics: 性能指標
            metadata: 元數據
        """
        self.id = id
        self.version = version
        self.description = description
        self.enabled = enabled
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        self.last_used = last_used or datetime.now()
        self.headless = headless
        self.window_size = window_size or {"width": 1920, "height": 1080}
        self.page_load_timeout = page_load_timeout
        self.script_timeout = script_timeout
        self.use_proxy = use_proxy
        self.proxies = proxies or []
        self.use_random_user_agent = use_random_user_agent
        self.user_agents = user_agents or []
        self.browser_fingerprint = browser_fingerprint or {}
        self.anti_fingerprint = anti_fingerprint or {}
        self.delay_config = delay_config or {}
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.detection_threshold = detection_threshold
        self.block_threshold = block_threshold
        self.use_cache = use_cache
        self.cache_duration = cache_duration
        self.max_cache_size = max_cache_size
        self.metrics = metrics or {}
        self.metadata = metadata or {}
        
        self.validate()
    
    def validate(self) -> None:
        """驗證配置
        
        檢查配置是否有效，如果無效則拋出 ConfigError 異常。
        
        Raises:
            ConfigError: 配置無效時拋出
        """
        if not isinstance(self.id, str):
            raise ConfigError("配置ID必須是字符串")
        
        if not isinstance(self.version, str):
            raise ConfigError("配置版本必須是字符串")
        
        if not isinstance(self.description, str):
            raise ConfigError("配置描述必須是字符串")
        
        if not isinstance(self.enabled, bool):
            raise ConfigError("enabled必須是布爾值")
        
        if not isinstance(self.headless, bool):
            raise ConfigError("headless必須是布爾值")
        
        if not isinstance(self.window_size, dict):
            raise ConfigError("window_size必須是字典")
        
        if "width" not in self.window_size or "height" not in self.window_size:
            raise ConfigError("window_size必須包含width和height")
        
        if not isinstance(self.page_load_timeout, int):
            raise ConfigError("page_load_timeout必須是整數")
        
        if not isinstance(self.script_timeout, int):
            raise ConfigError("script_timeout必須是整數")
        
        if not isinstance(self.use_proxy, bool):
            raise ConfigError("use_proxy必須是布爾值")
        
        if not isinstance(self.proxies, list):
            raise ConfigError("proxies必須是列表")
        
        if not isinstance(self.use_random_user_agent, bool):
            raise ConfigError("use_random_user_agent必須是布爾值")
        
        if not isinstance(self.user_agents, list):
            raise ConfigError("user_agents必須是列表")
        
        if not isinstance(self.browser_fingerprint, dict):
            raise ConfigError("browser_fingerprint必須是字典")
        
        if not isinstance(self.anti_fingerprint, dict):
            raise ConfigError("anti_fingerprint必須是字典")
        
        if not isinstance(self.delay_config, dict):
            raise ConfigError("delay_config必須是字典")
        
        if not isinstance(self.max_retries, int):
            raise ConfigError("max_retries必須是整數")
        
        if not isinstance(self.retry_delay, int):
            raise ConfigError("retry_delay必須是整數")
        
        if not isinstance(self.detection_threshold, float):
            raise ConfigError("detection_threshold必須是浮點數")
        
        if not isinstance(self.block_threshold, float):
            raise ConfigError("block_threshold必須是浮點數")
        
        if not isinstance(self.use_cache, bool):
            raise ConfigError("use_cache必須是布爾值")
        
        if not isinstance(self.cache_duration, int):
            raise ConfigError("cache_duration必須是整數")
        
        if not isinstance(self.max_cache_size, int):
            raise ConfigError("max_cache_size必須是整數")
        
        if not isinstance(self.metrics, dict):
            raise ConfigError("metrics必須是字典")
        
        if not isinstance(self.metadata, dict):
            raise ConfigError("metadata必須是字典")
    
    def to_dict(self) -> Dict[str, Any]:
        """將配置轉換為字典
        
        Returns:
            Dict[str, Any]: 配置字典
        """
        return {
            "id": self.id,
            "version": self.version,
            "description": self.description,
            "enabled": self.enabled,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_used": self.last_used.isoformat(),
            "headless": self.headless,
            "window_size": self.window_size,
            "page_load_timeout": self.page_load_timeout,
            "script_timeout": self.script_timeout,
            "use_proxy": self.use_proxy,
            "proxies": self.proxies,
            "use_random_user_agent": self.use_random_user_agent,
            "user_agents": self.user_agents,
            "browser_fingerprint": self.browser_fingerprint,
            "anti_fingerprint": self.anti_fingerprint,
            "delay_config": self.delay_config,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
            "detection_threshold": self.detection_threshold,
            "block_threshold": self.block_threshold,
            "use_cache": self.use_cache,
            "cache_duration": self.cache_duration,
            "max_cache_size": self.max_cache_size,
            "metrics": self.metrics,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AntiDetectionConfig":
        """從字典創建配置
        
        Args:
            data: 配置字典
            
        Returns:
            AntiDetectionConfig: 配置對象
        """
        return cls(
            id=data.get("id", "default"),
            version=data.get("version", "1.0.0"),
            description=data.get("description", "Default anti-detection configuration"),
            enabled=data.get("enabled", True),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if "updated_at" in data else None,
            last_used=datetime.fromisoformat(data["last_used"]) if "last_used" in data else None,
            headless=data.get("headless", False),
            window_size=data.get("window_size", {"width": 1920, "height": 1080}),
            page_load_timeout=data.get("page_load_timeout", 30),
            script_timeout=data.get("script_timeout", 30),
            use_proxy=data.get("use_proxy", False),
            proxies=data.get("proxies", []),
            use_random_user_agent=data.get("use_random_user_agent", False),
            user_agents=data.get("user_agents", []),
            browser_fingerprint=data.get("browser_fingerprint", {}),
            anti_fingerprint=data.get("anti_fingerprint", {}),
            delay_config=data.get("delay_config", {}),
            max_retries=data.get("max_retries", 3),
            retry_delay=data.get("retry_delay", 5),
            detection_threshold=data.get("detection_threshold", 0.8),
            block_threshold=data.get("block_threshold", 0.9),
            use_cache=data.get("use_cache", True),
            cache_duration=data.get("cache_duration", 3600),
            max_cache_size=data.get("max_cache_size", 1000),
            metrics=data.get("metrics", {}),
            metadata=data.get("metadata", {}),
        )
    
    @classmethod
    def from_file(cls, file_path: str) -> "AntiDetectionConfig":
        """從文件加載配置
        
        Args:
            file_path: 配置文件路徑
            
        Returns:
            AntiDetectionConfig: 配置對象
            
        Raises:
            ConfigError: 配置文件不存在或格式錯誤時拋出
        """
        if not os.path.exists(file_path):
            raise ConfigError(f"配置文件不存在: {file_path}")
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return cls.from_dict(data)
        except json.JSONDecodeError as e:
            raise ConfigError(f"配置文件格式錯誤: {e}")
        except Exception as e:
            raise ConfigError(f"加載配置文件失敗: {e}")
    
    def save_to_file(self, file_path: str) -> None:
        """保存配置到文件
        
        Args:
            file_path: 配置文件路徑
            
        Raises:
            ConfigError: 保存配置文件失敗時拋出
        """
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(self.to_dict(), f, indent=4, ensure_ascii=False)
        except Exception as e:
            raise ConfigError(f"保存配置文件失敗: {e}")
    
    def update(self, data: Dict[str, Any]) -> None:
        """更新配置
        
        Args:
            data: 更新數據
            
        Raises:
            ConfigError: 更新數據無效時拋出
        """
        try:
            for key, value in data.items():
                if hasattr(self, key):
                    setattr(self, key, value)
            self.updated_at = datetime.now()
            self.validate()
        except Exception as e:
            raise ConfigError(f"更新配置失敗: {e}")
    
    def reset(self) -> None:
        """重置配置為默認值"""
        self.__init__()
    
    def enable(self) -> None:
        """啟用配置"""
        self.enabled = True
        self.updated_at = datetime.now()
    
    def disable(self) -> None:
        """禁用配置"""
        self.enabled = False
        self.updated_at = datetime.now()
    
    def is_enabled(self) -> bool:
        """檢查配置是否啟用
        
        Returns:
            bool: 是否啟用
        """
        return self.enabled
    
    def get_metrics(self) -> Dict[str, Any]:
        """獲取性能指標
        
        Returns:
            Dict[str, Any]: 性能指標
        """
        return self.metrics
    
    def update_metrics(self, metrics: Dict[str, Any]) -> None:
        """更新性能指標
        
        Args:
            metrics: 性能指標
        """
        self.metrics.update(metrics)
        self.updated_at = datetime.now()
    
    def clear_metrics(self) -> None:
        """清除性能指標"""
        self.metrics = {}
        self.updated_at = datetime.now()
    
    def get_metadata(self) -> Dict[str, Any]:
        """獲取元數據
        
        Returns:
            Dict[str, Any]: 元數據
        """
        return self.metadata
    
    def update_metadata(self, metadata: Dict[str, Any]) -> None:
        """更新元數據
        
        Args:
            metadata: 元數據
        """
        self.metadata.update(metadata)
        self.updated_at = datetime.now()
    
    def clear_metadata(self) -> None:
        """清除元數據"""
        self.metadata = {}
        self.updated_at = datetime.now() 