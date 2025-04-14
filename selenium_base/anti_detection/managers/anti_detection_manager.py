#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
反檢測管理器模組

此模組提供反檢測管理功能，包括：
1. 配置管理
2. 代理管理
3. 用戶代理管理
4. Cookie 管理
5. 指紋規避
6. 行為模擬
"""

import json
import logging
from typing import Dict, List, Optional, Union

from selenium.webdriver.remote.webdriver import WebDriver

from .base_error import AntiDetectionError, handle_error
from .base_manager import BaseManager
from .configs.anti_detection_config import AntiDetectionConfig
from .configs.config_manager import ConfigManager
from .cookie_manager import CookieManager
from .evasion_scripts import EvasionScripts
from .proxy_manager import ProxyManager
from .user_agent_manager import UserAgentManager

logger = logging.getLogger(__name__)

class AntiDetectionManager(BaseManager):
    """反檢測管理器類"""
    
    def __init__(
        self,
        driver: WebDriver,
        config: Optional[AntiDetectionConfig] = None,
        config_dir: Optional[str] = None
    ):
        """
        初始化反檢測管理器
        
        Args:
            driver: WebDriver 實例
            config: 反檢測配置
            config_dir: 配置目錄路徑
        """
        super().__init__(driver, config)
        self.config_dir = config_dir
        self.config_manager = ConfigManager(config_dir) if config_dir else None
        
        # 初始化子管理器
        self.proxy_manager = ProxyManager(driver, self.config)
        self.user_agent_manager = UserAgentManager(driver, self.config)
        self.cookie_manager = CookieManager(driver, self.config)
        self.evasion_scripts = EvasionScripts(driver)
        
    @handle_error
    def setup(self) -> None:
        """設置反檢測環境"""
        logger.info("開始設置反檢測環境")
        
        # 設置代理
        if self.config.use_proxy:
            self.proxy_manager.setup()
            
        # 設置用戶代理
        if self.config.use_random_user_agent:
            self.user_agent_manager.setup()
            
        # 設置 Cookie
        self.cookie_manager.setup()
        
        # 注入規避腳本
        self.evasion_scripts.inject_evasion_scripts()
        
        logger.info("反檢測環境設置完成")
        
    @handle_error
    def cleanup(self) -> None:
        """清理反檢測環境"""
        logger.info("開始清理反檢測環境")
        
        # 清理代理
        if self.config.use_proxy:
            self.proxy_manager.cleanup()
            
        # 清理用戶代理
        if self.config.use_random_user_agent:
            self.user_agent_manager.cleanup()
            
        # 清理 Cookie
        self.cookie_manager.cleanup()
        
        logger.info("反檢測環境清理完成")
        
    @handle_error
    def switch_config(self, config_id: str) -> bool:
        """
        切換反檢測配置
        
        Args:
            config_id: 配置 ID
            
        Returns:
            是否成功
        """
        if not self.config_manager:
            raise AntiDetectionError("配置管理器未初始化")
            
        config = self.config_manager.get_config(config_id)
        if not config:
            raise AntiDetectionError(f"找不到配置：{config_id}")
            
        self.config = config
        self.setup()
        
        return True
        
    @handle_error
    def check_detection(self) -> Dict[str, bool]:
        """
        檢查檢測狀態
        
        Returns:
            檢測狀態檢查結果
        """
        results = {}
        
        # 檢查代理狀態
        if self.config.use_proxy:
            results['proxy'] = self.proxy_manager.check_proxy()
            
        # 檢查用戶代理狀態
        if self.config.use_random_user_agent:
            results['user_agent'] = self.user_agent_manager.check_user_agent()
            
        # 檢查 Cookie 狀態
        results['cookie'] = self.cookie_manager.check_cookies()
        
        # 檢查規避腳本效果
        results.update(self.evasion_scripts.check_evasion_effectiveness())
        
        return results
        
    @handle_error
    def get_metrics(self) -> Dict[str, Union[int, float]]:
        """
        獲取性能指標
        
        Returns:
            性能指標數據
        """
        metrics = {
            'detection_count': 0,
            'evasion_success_rate': 0.0,
            'proxy_success_rate': 0.0,
            'cookie_success_rate': 0.0
        }
        
        # 獲取檢測次數
        detection_results = self.check_detection()
        metrics['detection_count'] = sum(1 for result in detection_results.values() if not result)
        
        # 計算規避成功率
        evasion_results = self.evasion_scripts.check_evasion_effectiveness()
        metrics['evasion_success_rate'] = sum(1 for result in evasion_results.values() if result) / len(evasion_results)
        
        # 計算代理成功率
        if self.config.use_proxy:
            proxy_results = self.proxy_manager.check_proxy()
            metrics['proxy_success_rate'] = 1.0 if proxy_results else 0.0
            
        # 計算 Cookie 成功率
        cookie_results = self.cookie_manager.check_cookies()
        metrics['cookie_success_rate'] = 1.0 if cookie_results else 0.0
        
        return metrics
        
    @handle_error
    def save_state(self, file_path: str) -> None:
        """
        保存當前狀態
        
        Args:
            file_path: 文件路徑
        """
        state = {
            'config': self.config.to_dict(),
            'metrics': self.get_metrics(),
            'detection_status': self.check_detection()
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
            
    @handle_error
    def load_state(self, file_path: str) -> None:
        """
        載入保存的狀態
        
        Args:
            file_path: 文件路徑
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            state = json.load(f)
            
        self.config = AntiDetectionConfig.from_dict(state['config'])
        self.setup() 