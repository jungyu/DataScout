"""
反檢測配置驗證器模組

此模組提供反檢測配置的驗證功能，包括：
- 配置格式驗證
- 配置值範圍驗證
- 配置依賴關係驗證
- 配置衝突檢測
"""

from typing import Dict, List, Optional, Union, Any
from datetime import datetime

from .anti_detection_config import AntiDetectionConfig


class ConfigValidator:
    """反檢測配置驗證器
    
    用於驗證反檢測配置的有效性。
    
    Attributes:
        config (AntiDetectionConfig): 要驗證的配置對象
        errors (List[str]): 錯誤信息列表
        warnings (List[str]): 警告信息列表
    """
    
    def __init__(self, config: AntiDetectionConfig):
        """初始化配置驗證器
        
        Args:
            config: 要驗證的配置對象
        """
        self.config = config
        self.errors = []
        self.warnings = []
    
    def validate(self) -> bool:
        """驗證配置
        
        Returns:
            bool: 配置是否有效
        """
        self.errors = []
        self.warnings = []
        
        self._validate_basic_info()
        self._validate_browser_settings()
        self._validate_proxy_settings()
        self._validate_user_agent_settings()
        self._validate_fingerprint_settings()
        self._validate_delay_settings()
        self._validate_retry_settings()
        self._validate_threshold_settings()
        self._validate_cache_settings()
        self._validate_dependencies()
        self._validate_conflicts()
        
        return len(self.errors) == 0
    
    def _validate_basic_info(self) -> None:
        """驗證基本信息"""
        if not self.config.id:
            self.errors.append("配置ID不能為空")
        
        if not self.config.version:
            self.errors.append("配置版本不能為空")
        
        if not self.config.description:
            self.warnings.append("配置描述為空")
        
        if not isinstance(self.config.enabled, bool):
            self.errors.append("enabled必須是布爾值")
        
        if not isinstance(self.config.created_at, datetime):
            self.errors.append("created_at必須是datetime對象")
        
        if not isinstance(self.config.updated_at, datetime):
            self.errors.append("updated_at必須是datetime對象")
        
        if not isinstance(self.config.last_used, datetime):
            self.errors.append("last_used必須是datetime對象")
    
    def _validate_browser_settings(self) -> None:
        """驗證瀏覽器設置"""
        if not isinstance(self.config.headless, bool):
            self.errors.append("headless必須是布爾值")
        
        if not isinstance(self.config.window_size, dict):
            self.errors.append("window_size必須是字典")
        else:
            if "width" not in self.config.window_size:
                self.errors.append("window_size必須包含width字段")
            elif not isinstance(self.config.window_size["width"], int):
                self.errors.append("window_size.width必須是整數")
            
            if "height" not in self.config.window_size:
                self.errors.append("window_size必須包含height字段")
            elif not isinstance(self.config.window_size["height"], int):
                self.errors.append("window_size.height必須是整數")
        
        if not isinstance(self.config.page_load_timeout, int):
            self.errors.append("page_load_timeout必須是整數")
        elif self.config.page_load_timeout < 0:
            self.errors.append("page_load_timeout不能為負數")
        
        if not isinstance(self.config.script_timeout, int):
            self.errors.append("script_timeout必須是整數")
        elif self.config.script_timeout < 0:
            self.errors.append("script_timeout不能為負數")
    
    def _validate_proxy_settings(self) -> None:
        """驗證代理設置"""
        if not isinstance(self.config.use_proxy, bool):
            self.errors.append("use_proxy必須是布爾值")
        
        if not isinstance(self.config.proxies, list):
            self.errors.append("proxies必須是列表")
        else:
            for i, proxy in enumerate(self.config.proxies):
                if not isinstance(proxy, dict):
                    self.errors.append(f"proxies[{i}]必須是字典")
                    continue
                
                if "type" not in proxy:
                    self.errors.append(f"proxies[{i}]必須包含type字段")
                elif proxy["type"] not in ["http", "socks4", "socks5"]:
                    self.errors.append(f"proxies[{i}].type必須是http、socks4或socks5")
                
                if "host" not in proxy:
                    self.errors.append(f"proxies[{i}]必須包含host字段")
                elif not isinstance(proxy["host"], str):
                    self.errors.append(f"proxies[{i}].host必須是字符串")
                
                if "port" not in proxy:
                    self.errors.append(f"proxies[{i}]必須包含port字段")
                elif not isinstance(proxy["port"], int):
                    self.errors.append(f"proxies[{i}].port必須是整數")
                elif proxy["port"] < 1 or proxy["port"] > 65535:
                    self.errors.append(f"proxies[{i}].port必須在1-65535之間")
    
    def _validate_user_agent_settings(self) -> None:
        """驗證用戶代理設置"""
        if not isinstance(self.config.use_random_user_agent, bool):
            self.errors.append("use_random_user_agent必須是布爾值")
        
        if not isinstance(self.config.user_agents, list):
            self.errors.append("user_agents必須是列表")
        else:
            for i, user_agent in enumerate(self.config.user_agents):
                if not isinstance(user_agent, str):
                    self.errors.append(f"user_agents[{i}]必須是字符串")
    
    def _validate_fingerprint_settings(self) -> None:
        """驗證指紋設置"""
        if not isinstance(self.config.browser_fingerprint, dict):
            self.errors.append("browser_fingerprint必須是字典")
        else:
            required_fields = [
                "platform",
                "webgl_vendor",
                "webgl_renderer",
                "language",
                "timezone",
                "screen_resolution",
                "color_depth",
                "pixel_ratio"
            ]
            
            for field in required_fields:
                if field not in self.config.browser_fingerprint:
                    self.errors.append(f"browser_fingerprint必須包含{field}字段")
                elif not isinstance(self.config.browser_fingerprint[field], str):
                    self.errors.append(f"browser_fingerprint.{field}必須是字符串")
        
        if not isinstance(self.config.anti_fingerprint, dict):
            self.errors.append("anti_fingerprint必須是字典")
        else:
            for key, value in self.config.anti_fingerprint.items():
                if not isinstance(value, bool):
                    self.errors.append(f"anti_fingerprint.{key}必須是布爾值")
    
    def _validate_delay_settings(self) -> None:
        """驗證延遲設置"""
        if not isinstance(self.config.delay_config, dict):
            self.errors.append("delay_config必須是字典")
        else:
            if "min_delay" not in self.config.delay_config:
                self.errors.append("delay_config必須包含min_delay字段")
            elif not isinstance(self.config.delay_config["min_delay"], (int, float)):
                self.errors.append("delay_config.min_delay必須是數字")
            elif self.config.delay_config["min_delay"] < 0:
                self.errors.append("delay_config.min_delay不能為負數")
            
            if "max_delay" not in self.config.delay_config:
                self.errors.append("delay_config必須包含max_delay字段")
            elif not isinstance(self.config.delay_config["max_delay"], (int, float)):
                self.errors.append("delay_config.max_delay必須是數字")
            elif self.config.delay_config["max_delay"] < 0:
                self.errors.append("delay_config.max_delay不能為負數")
            
            if "min_delay" in self.config.delay_config and "max_delay" in self.config.delay_config:
                if self.config.delay_config["min_delay"] > self.config.delay_config["max_delay"]:
                    self.errors.append("delay_config.min_delay不能大於max_delay")
            
            for key in ["random_delay", "mouse_movement_delay", "typing_delay", "scroll_delay", "click_delay"]:
                if key not in self.config.delay_config:
                    self.errors.append(f"delay_config必須包含{key}字段")
                elif not isinstance(self.config.delay_config[key], bool):
                    self.errors.append(f"delay_config.{key}必須是布爾值")
    
    def _validate_retry_settings(self) -> None:
        """驗證重試設置"""
        if not isinstance(self.config.max_retries, int):
            self.errors.append("max_retries必須是整數")
        elif self.config.max_retries < 0:
            self.errors.append("max_retries不能為負數")
        
        if not isinstance(self.config.retry_delay, int):
            self.errors.append("retry_delay必須是整數")
        elif self.config.retry_delay < 0:
            self.errors.append("retry_delay不能為負數")
    
    def _validate_threshold_settings(self) -> None:
        """驗證閾值設置"""
        if not isinstance(self.config.detection_threshold, float):
            self.errors.append("detection_threshold必須是浮點數")
        elif self.config.detection_threshold < 0 or self.config.detection_threshold > 1:
            self.errors.append("detection_threshold必須在0-1之間")
        
        if not isinstance(self.config.block_threshold, float):
            self.errors.append("block_threshold必須是浮點數")
        elif self.config.block_threshold < 0 or self.config.block_threshold > 1:
            self.errors.append("block_threshold必須在0-1之間")
        
        if self.config.detection_threshold >= self.config.block_threshold:
            self.errors.append("detection_threshold必須小於block_threshold")
    
    def _validate_cache_settings(self) -> None:
        """驗證緩存設置"""
        if not isinstance(self.config.use_cache, bool):
            self.errors.append("use_cache必須是布爾值")
        
        if not isinstance(self.config.cache_duration, int):
            self.errors.append("cache_duration必須是整數")
        elif self.config.cache_duration < 0:
            self.errors.append("cache_duration不能為負數")
        
        if not isinstance(self.config.max_cache_size, int):
            self.errors.append("max_cache_size必須是整數")
        elif self.config.max_cache_size < 0:
            self.errors.append("max_cache_size不能為負數")
    
    def _validate_dependencies(self) -> None:
        """驗證配置依賴關係"""
        if self.config.use_proxy and not self.config.proxies:
            self.warnings.append("啟用代理但未配置代理服務器")
        
        if self.config.use_random_user_agent and not self.config.user_agents:
            self.warnings.append("啟用隨機用戶代理但未配置用戶代理列表")
        
        if any(self.config.anti_fingerprint.values()) and not self.config.browser_fingerprint:
            self.warnings.append("啟用反指紋但未配置瀏覽器指紋")
    
    def _validate_conflicts(self) -> None:
        """驗證配置衝突"""
        if self.config.headless and self.config.window_size["width"] == 0:
            self.warnings.append("無頭模式下窗口寬度為0")
        
        if self.config.headless and self.config.window_size["height"] == 0:
            self.warnings.append("無頭模式下窗口高度為0")
        
        if self.config.page_load_timeout < self.config.script_timeout:
            self.warnings.append("頁面加載超時小於腳本執行超時")
        
        if self.config.use_cache and self.config.cache_duration == 0:
            self.warnings.append("啟用緩存但緩存時間為0")
        
        if self.config.use_cache and self.config.max_cache_size == 0:
            self.warnings.append("啟用緩存但最大緩存大小為0")
    
    def get_errors(self) -> List[str]:
        """獲取錯誤信息
        
        Returns:
            List[str]: 錯誤信息列表
        """
        return self.errors
    
    def get_warnings(self) -> List[str]:
        """獲取警告信息
        
        Returns:
            List[str]: 警告信息列表
        """
        return self.warnings
    
    def has_errors(self) -> bool:
        """是否有錯誤
        
        Returns:
            bool: 是否有錯誤
        """
        return len(self.errors) > 0
    
    def has_warnings(self) -> bool:
        """是否有警告
        
        Returns:
            bool: 是否有警告
        """
        return len(self.warnings) > 0
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """獲取驗證摘要
        
        Returns:
            Dict[str, Any]: 驗證摘要
        """
        return {
            "is_valid": not self.has_errors(),
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "errors": self.errors,
            "warnings": self.warnings
        } 