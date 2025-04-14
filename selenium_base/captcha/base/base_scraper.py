#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
驗證碼基礎爬取模組

提供驗證碼相關的基礎爬取功能
"""

from typing import Dict, Any, Optional, List, Union, Callable
from abc import ABC, abstractmethod

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from ...core.browser import Browser
from ...core.logger import setup_logger
from ...core.config import BaseConfig
from .base_error import CaptchaError, handle_error

logger = setup_logger(__name__)

class BaseScraper(Browser):
    """驗證碼基礎爬取類別"""
    
    def __init__(self, driver: webdriver.Remote, config: Union[Dict, BaseConfig], logger: Optional[Any] = None):
        """
        初始化驗證碼基礎爬取類別
        
        Args:
            driver: 瀏覽器驅動程式
            config: 配置字典或配置對象
            logger: 日誌記錄器
        """
        self.driver = driver
        self.config = config if isinstance(config, BaseConfig) else BaseConfig(config)
        self.logger = logger or setup_logger(self.__class__.__name__)
        self._initialized = False
        self._state: Dict[str, Any] = {}
        
    @abstractmethod
    def setup(self) -> None:
        """設置爬取環境"""
        self._initialized = True
        
    @abstractmethod
    def cleanup(self) -> None:
        """清理爬取環境"""
        self._initialized = False
        
    @handle_error()
    def navigate(self, url: str) -> None:
        """
        導航到指定URL
        
        Args:
            url: 目標URL
        """
        try:
            self.driver.get(url)
            self.logger.info(f"成功導航到：{url}")
        except Exception as e:
            self.logger.error(f"導航失敗：{str(e)}")
            raise CaptchaError(f"導航失敗：{str(e)}")
            
    @handle_error()
    def wait_for_element(
        self,
        by: By,
        value: str,
        timeout: Optional[int] = None,
        condition: Callable = EC.presence_of_element_located
    ) -> Any:
        """
        等待元素出現
        
        Args:
            by: 定位方式
            value: 定位值
            timeout: 超時時間（秒）
            condition: 等待條件
            
        Returns:
            找到的元素
        """
        try:
            timeout = timeout or self.config.get("timeout", 10)
            element = WebDriverWait(self.driver, timeout).until(
                condition((by, value))
            )
            return element
        except TimeoutException:
            self.logger.error(f"等待元素超時：{value}")
            raise CaptchaError(f"等待元素超時：{value}")
            
    @handle_error()
    def find_element(self, by: By, value: str) -> Any:
        """
        查找元素
        
        Args:
            by: 定位方式
            value: 定位值
            
        Returns:
            找到的元素
        """
        try:
            return self.driver.find_element(by, value)
        except NoSuchElementException:
            self.logger.error(f"未找到元素：{value}")
            raise CaptchaError(f"未找到元素：{value}")
            
    @handle_error()
    def find_elements(self, by: By, value: str) -> List[Any]:
        """
        查找多個元素
        
        Args:
            by: 定位方式
            value: 定位值
            
        Returns:
            找到的元素列表
        """
        try:
            return self.driver.find_elements(by, value)
        except Exception as e:
            self.logger.error(f"查找元素失敗：{str(e)}")
            raise CaptchaError(f"查找元素失敗：{str(e)}")
            
    @handle_error()
    def click(self, element: Any) -> None:
        """
        點擊元素
        
        Args:
            element: 要點擊的元素
        """
        try:
            element.click()
        except Exception as e:
            self.logger.error(f"點擊元素失敗：{str(e)}")
            raise CaptchaError(f"點擊元素失敗：{str(e)}")
            
    @handle_error()
    def input_text(self, element: Any, text: str) -> None:
        """
        輸入文本
        
        Args:
            element: 要輸入的元素
            text: 要輸入的文本
        """
        try:
            element.clear()
            element.send_keys(text)
        except Exception as e:
            self.logger.error(f"輸入文本失敗：{str(e)}")
            raise CaptchaError(f"輸入文本失敗：{str(e)}")
            
    @handle_error()
    def get_text(self, element: Any) -> str:
        """
        獲取元素文本
        
        Args:
            element: 要獲取文本的元素
            
        Returns:
            元素文本
        """
        try:
            return element.text
        except Exception as e:
            self.logger.error(f"獲取文本失敗：{str(e)}")
            raise CaptchaError(f"獲取文本失敗：{str(e)}")
            
    @handle_error()
    def get_attribute(self, element: Any, attribute: str) -> str:
        """
        獲取元素屬性
        
        Args:
            element: 要獲取屬性的元素
            attribute: 屬性名稱
            
        Returns:
            屬性值
        """
        try:
            return element.get_attribute(attribute)
        except Exception as e:
            self.logger.error(f"獲取屬性失敗：{str(e)}")
            raise CaptchaError(f"獲取屬性失敗：{str(e)}")
            
    @handle_error()
    def execute_script(self, script: str, *args) -> Any:
        """
        執行JavaScript腳本
        
        Args:
            script: JavaScript腳本
            args: 腳本參數
            
        Returns:
            腳本執行結果
        """
        try:
            return self.driver.execute_script(script, *args)
        except Exception as e:
            self.logger.error(f"執行腳本失敗：{str(e)}")
            raise CaptchaError(f"執行腳本失敗：{str(e)}")
            
    @handle_error()
    def get_state(self) -> Dict[str, Any]:
        """
        獲取當前狀態
        
        Returns:
            當前狀態字典
        """
        return self._state.copy()
        
    @handle_error()
    def set_state(self, state: Dict[str, Any]) -> None:
        """
        設置當前狀態
        
        Args:
            state: 狀態字典
        """
        self._state = state.copy()
        
    @handle_error()
    def update_state(self, updates: Dict[str, Any]) -> None:
        """
        更新當前狀態
        
        Args:
            updates: 更新字典
        """
        self._state.update(updates)
        
    @handle_error()
    def clear_state(self) -> None:
        """
        清除當前狀態
        """
        self._state.clear()
        
    @handle_error()
    def is_initialized(self) -> bool:
        """
        檢查是否已初始化
        
        Returns:
            是否已初始化
        """
        return self._initialized
        
    def __enter__(self):
        """上下文管理器入口"""
        self.setup()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.cleanup() 