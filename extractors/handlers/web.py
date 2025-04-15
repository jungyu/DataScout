#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
網頁提取器模組

提供網頁數據提取功能，包括：
1. 元素定位
2. 數據提取
3. 頁面導航
4. 狀態管理
"""

import logging
from typing import Any, Dict, List, Optional, Union
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from ..core.base import BaseExtractor
from ..core.error import ExtractorError, handle_extractor_error

class WebExtractor(BaseExtractor):
    """網頁提取器類別"""
    
    def __init__(
        self,
        driver: WebDriver,
        config: Optional[Union[Dict[str, Any], BaseConfig]] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化網頁提取器
        
        Args:
            driver: WebDriver 實例
            config: 配置字典或配置對象
            logger: 日誌記錄器
        """
        super().__init__(config, logger)
        self.driver = driver
        self.wait = WebDriverWait(driver, self.config.get('timeout', 10))
        
    def _setup(self) -> None:
        """設置提取器環境"""
        self.driver.implicitly_wait(self.config.get('implicit_wait', 0))
        
    def _cleanup(self) -> None:
        """清理提取器環境"""
        pass
        
    def _validate_config(self) -> bool:
        """
        驗證配置
        
        Returns:
            是否驗證通過
        """
        required_fields = ['timeout', 'implicit_wait']
        return all(field in self.config for field in required_fields)
        
    @handle_extractor_error()
    def find_element(self, by: By, value: str, timeout: Optional[float] = None) -> WebElement:
        """
        查找元素
        
        Args:
            by: 定位方式
            value: 定位值
            timeout: 超時時間
            
        Returns:
            元素對象
        """
        try:
            return self.wait.until(
                EC.presence_of_element_located((by, value)),
                timeout=timeout
            )
        except TimeoutException:
            raise ExtractorError(f"元素未找到：{by}={value}")
            
    @handle_extractor_error()
    def find_elements(self, by: By, value: str, timeout: Optional[float] = None) -> List[WebElement]:
        """
        查找多個元素
        
        Args:
            by: 定位方式
            value: 定位值
            timeout: 超時時間
            
        Returns:
            元素對象列表
        """
        try:
            return self.wait.until(
                EC.presence_of_all_elements_located((by, value)),
                timeout=timeout
            )
        except TimeoutException:
            return []
            
    @handle_extractor_error()
    def get_text(self, by: By, value: str, timeout: Optional[float] = None) -> str:
        """
        獲取元素文本
        
        Args:
            by: 定位方式
            value: 定位值
            timeout: 超時時間
            
        Returns:
            元素文本
        """
        element = self.find_element(by, value, timeout)
        return element.text.strip()
        
    @handle_extractor_error()
    def get_attribute(self, by: By, value: str, name: str, timeout: Optional[float] = None) -> str:
        """
        獲取元素屬性
        
        Args:
            by: 定位方式
            value: 定位值
            name: 屬性名
            timeout: 超時時間
            
        Returns:
            屬性值
        """
        element = self.find_element(by, value, timeout)
        return element.get_attribute(name)
        
    @handle_extractor_error()
    def click(self, by: By, value: str, timeout: Optional[float] = None) -> None:
        """
        點擊元素
        
        Args:
            by: 定位方式
            value: 定位值
            timeout: 超時時間
        """
        element = self.find_element(by, value, timeout)
        element.click()
        
    @handle_extractor_error()
    def input_text(self, by: By, value: str, text: str, timeout: Optional[float] = None) -> None:
        """
        輸入文本
        
        Args:
            by: 定位方式
            value: 定位值
            text: 要輸入的文本
            timeout: 超時時間
        """
        element = self.find_element(by, value, timeout)
        element.clear()
        element.send_keys(text)
        
    @handle_extractor_error()
    def wait_for_element(self, by: By, value: str, condition: str = 'presence', timeout: Optional[float] = None) -> WebElement:
        """
        等待元素滿足條件
        
        Args:
            by: 定位方式
            value: 定位值
            condition: 等待條件
            timeout: 超時時間
            
        Returns:
            元素對象
        """
        conditions = {
            'presence': EC.presence_of_element_located,
            'visibility': EC.visibility_of_element_located,
            'clickable': EC.element_to_be_clickable
        }
        
        if condition not in conditions:
            raise ExtractorError(f"不支持的等待條件：{condition}")
            
        try:
            return self.wait.until(
                conditions[condition]((by, value)),
                timeout=timeout
            )
        except TimeoutException:
            raise ExtractorError(f"等待元素超時：{by}={value}")
            
    @handle_extractor_error()
    def execute_script(self, script: str, *args: Any) -> Any:
        """
        執行 JavaScript
        
        Args:
            script: JavaScript 代碼
            *args: 參數
            
        Returns:
            執行結果
        """
        return self.driver.execute_script(script, *args)
        
    @handle_extractor_error()
    def extract(self, *args: Any, **kwargs: Any) -> Any:
        """
        執行提取
        
        Args:
            *args: 位置參數
            **kwargs: 關鍵字參數
            
        Returns:
            提取結果
        """
        return self._extract(*args, **kwargs)
        
    @abstractmethod
    def _extract(self, *args: Any, **kwargs: Any) -> Any:
        """具體的提取邏輯"""
        pass 