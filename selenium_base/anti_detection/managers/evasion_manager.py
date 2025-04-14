#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
規避腳本管理器模組

此模組提供規避腳本管理功能，包括：
1. 腳本注入
2. 腳本執行
3. 腳本效果檢查
4. 腳本配置管理
"""

import json
from typing import Dict, List, Optional, Union

from selenium.webdriver.remote.webdriver import WebDriver

from .base_manager import BaseManager
from .base_error import AntiDetectionError, handle_error
from .evasion_scripts import EvasionScripts

class EvasionManager(BaseManager):
    """規避腳本管理器類"""
    
    def __init__(self, driver: WebDriver, config: Optional[Dict] = None):
        """
        初始化規避腳本管理器
        
        Args:
            driver: WebDriver 實例
            config: 配置字典
        """
        super().__init__(driver, config)
        self.evasion_scripts = EvasionScripts()
        self.injected_scripts = set()
        
    @handle_error()
    def setup(self) -> None:
        """設置規避腳本"""
        self._load_config()
        self._inject_scripts()
        self._check_effectiveness()
        
    @handle_error()
    def cleanup(self) -> None:
        """清理規避腳本"""
        self._remove_scripts()
        self.injected_scripts.clear()
        
    @handle_error()
    def _load_config(self) -> None:
        """加載配置"""
        if not self.config:
            self.config = {
                'enabled_evasions': [
                    'webgl',
                    'canvas',
                    'audio',
                    'font',
                    'plugin',
                    'timezone',
                    'language',
                    'screen'
                ],
                'check_effectiveness': True
            }
            
    @handle_error()
    def _inject_scripts(self) -> None:
        """注入腳本"""
        scripts = self.evasion_scripts.get_all_evasions()
        for name, script in scripts.items():
            if name in self.config['enabled_evasions']:
                try:
                    self.driver.execute_script(script)
                    self.injected_scripts.add(name)
                except Exception as e:
                    self.logger.error(f"注入腳本 {name} 失敗: {str(e)}")
                    
    @handle_error()
    def _remove_scripts(self) -> None:
        """移除注入的腳本"""
        try:
            from .evasion_cleanup import EvasionCleanup
            EvasionCleanup.cleanup_all(self.driver)
            self.logger.info("成功移除所有注入的腳本")
        except Exception as e:
            self.logger.error(f"移除腳本時發生錯誤: {str(e)}")
            raise
        
    @handle_error()
    def _check_effectiveness(self) -> None:
        """檢查規避效果"""
        if not self.config.get('check_effectiveness', True):
            return
            
        results = {}
        for name in self.injected_scripts:
            try:
                result = self._check_single_effectiveness(name)
                results[name] = result
            except Exception as e:
                self.logger.error(f"檢查腳本 {name} 效果失敗: {str(e)}")
                results[name] = False
                
        self.logger.info(f"規避效果檢查結果: {json.dumps(results, indent=2)}")
        
    @handle_error()
    def _check_single_effectiveness(self, name: str) -> bool:
        """
        檢查單個腳本效果
        
        Args:
            name: 腳本名稱
            
        Returns:
            是否有效
        """
        if name == 'webgl':
            return self.driver.execute_script("""
                const canvas = document.createElement('canvas');
                const gl = canvas.getContext('webgl');
                return gl.getParameter(37445) === 'Intel Open Source Technology Center';
            """)
        elif name == 'canvas':
            return self.driver.execute_script("""
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');
                ctx.fillText('Test', 10, 10);
                const imageData = ctx.getImageData(0, 0, 10, 10);
                return imageData.data.some((value, index) => value !== 0);
            """)
        elif name == 'audio':
            return self.driver.execute_script("""
                const audioContext = new AudioContext();
                const buffer = audioContext.createBuffer(1, 100, 100);
                const channelData = buffer.getChannelData(0);
                return channelData.some(value => value !== 0);
            """)
        elif name == 'font':
            return self.driver.execute_script("""
                return window.matchMedia('(font-family: test)').matches;
            """)
        elif name == 'plugin':
            return self.driver.execute_script("""
                return navigator.plugins.length > 0;
            """)
        elif name == 'timezone':
            return self.driver.execute_script("""
                return new Date().getTimezoneOffset() === -480;
            """)
        elif name == 'language':
            return self.driver.execute_script("""
                return navigator.language === 'zh-CN';
            """)
        elif name == 'screen':
            return self.driver.execute_script("""
                return window.screen.width === 1920 && 
                       window.screen.height === 1080 && 
                       window.screen.colorDepth === 24;
            """)
        return False
        
    @handle_error()
    def get_injected_scripts(self) -> List[str]:
        """
        獲取已注入的腳本列表
        
        Returns:
            已注入的腳本列表
        """
        return list(self.injected_scripts)
        
    @handle_error()
    def is_script_injected(self, name: str) -> bool:
        """
        檢查腳本是否已注入
        
        Args:
            name: 腳本名稱
            
        Returns:
            是否已注入
        """
        return name in self.injected_scripts
        
    @handle_error()
    def inject_script(self, name: str) -> bool:
        """
        注入單個腳本
        
        Args:
            name: 腳本名稱
            
        Returns:
            是否成功
        """
        if name in self.injected_scripts:
            return True
            
        scripts = self.evasion_scripts.get_all_evasions()
        if name not in scripts:
            self.logger.error(f"腳本 {name} 不存在")
            return False
            
        try:
            self.driver.execute_script(scripts[name])
            self.injected_scripts.add(name)
            return True
        except Exception as e:
            self.logger.error(f"注入腳本 {name} 失敗: {str(e)}")
            return False
            
    @handle_error()
    def remove_script(self, name: str) -> bool:
        """
        移除單個腳本
        
        Args:
            name: 腳本名稱
            
        Returns:
            是否成功
        """
        if name not in self.injected_scripts:
            return True
            
        try:
            # 這裡需要實現腳本移除邏輯
            self.injected_scripts.remove(name)
            return True
        except Exception as e:
            self.logger.error(f"移除腳本 {name} 失敗: {str(e)}")
            return False 