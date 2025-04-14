#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
基礎爬取模組

提供基礎爬取功能
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
from .base_error import AntiDetectionError

logger = setup_logger(__name__)

class BaseScraper(Browser):
    """基礎爬取類別"""
    
    def __init__(self, driver: webdriver.Remote, config: Union[Dict, BaseConfig], logger: Optional[Any] = None):
        """
        初始化基礎爬取類別
        
        Args:
            driver: 瀏覽器驅動程式
            config: 配置字典或配置對象
            logger: 日誌記錄器
        """
        super().__init__(driver, config)
        self.logger = logger or setup_logger(self.__class__.__name__)
        
    @abstractmethod
    def setup(self) -> None:
        """設置爬取環境"""
        super().setup()
        
    @abstractmethod
    def cleanup(self) -> None:
        """清理爬取環境"""
        super().cleanup()
        
    def navigate(self, url: str) -> None:
        """
        導航到指定URL
        
        Args:
            url: 目標URL
        """
        try:
            super().navigate(url)
            self.logger.info(f"成功導航到：{url}")
        except Exception as e:
            self.logger.error(f"導航失敗：{str(e)}")
            raise AntiDetectionError(f"導航失敗：{str(e)}")
            
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
            return super().wait_for_element(by, value, timeout, condition)
        except TimeoutException:
            self.logger.error(f"等待元素超時：{value}")
            raise AntiDetectionError(f"等待元素超時：{value}")
            
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
            return super().find_element(by, value)
        except NoSuchElementException:
            self.logger.error(f"未找到元素：{value}")
            raise AntiDetectionError(f"未找到元素：{value}")
            
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
            return super().find_elements(by, value)
        except Exception as e:
            self.logger.error(f"查找元素失敗：{str(e)}")
            raise AntiDetectionError(f"查找元素失敗：{str(e)}")
            
    def click(self, element: Any) -> None:
        """
        點擊元素
        
        Args:
            element: 要點擊的元素
        """
        try:
            super().click(element)
        except Exception as e:
            self.logger.error(f"點擊元素失敗：{str(e)}")
            raise AntiDetectionError(f"點擊元素失敗：{str(e)}")
            
    def input_text(self, element: Any, text: str) -> None:
        """
        輸入文本
        
        Args:
            element: 要輸入的元素
            text: 要輸入的文本
        """
        try:
            super().input_text(element, text)
        except Exception as e:
            self.logger.error(f"輸入文本失敗：{str(e)}")
            raise AntiDetectionError(f"輸入文本失敗：{str(e)}")
            
    def get_text(self, element: Any) -> str:
        """
        獲取元素文本
        
        Args:
            element: 要獲取文本的元素
            
        Returns:
            元素文本
        """
        try:
            return super().get_text(element)
        except Exception as e:
            self.logger.error(f"獲取文本失敗：{str(e)}")
            raise AntiDetectionError(f"獲取文本失敗：{str(e)}")
            
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
            return super().get_attribute(element, attribute)
        except Exception as e:
            self.logger.error(f"獲取屬性失敗：{str(e)}")
            raise AntiDetectionError(f"獲取屬性失敗：{str(e)}")
            
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
            return super().execute_script(script, *args)
        except Exception as e:
            self.logger.error(f"執行腳本失敗：{str(e)}")
            raise AntiDetectionError(f"執行腳本失敗：{str(e)}")
            
    def __enter__(self):
        """上下文管理器入口"""
        self.setup()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.cleanup() 