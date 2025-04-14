#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Shopee 爬蟲模組

提供蝦皮商品爬蟲功能，包括：
- 關鍵字搜尋
- 商品詳情爬取
- 驗證碼處理
- 進階反爬蟲技術
"""

import os
import time
import re
import json
import logging
import random
from typing import Dict, List, Optional, Union, Generator, Any
from pathlib import Path
from datetime import datetime
from urllib.parse import quote
import pickle

from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException
)
from selenium.webdriver.remote.webelement import WebElement

from src.core.base_crawler import BaseCrawler, CrawlerState
from src.core.exceptions import CrawlerException, BrowserException, RequestException
from src.config.base_config import BaseConfig

from selenium_base.services.browser_profile import BrowserProfile
from selenium_base.services.browser_fingerprint import BrowserFingerprint
from selenium_base.services.request_controller import RequestController

class ShopeeCrawlerError(CrawlerException):
    """蝦皮爬蟲錯誤"""
    def __init__(self, message: str, code: int = 5400, details: Optional[Dict[str, Any]] = None):
        super().__init__(code=code, message=message, details=details)

class ShopeeCrawler(BaseCrawler):
    """蝦皮爬蟲類"""
    
    def __init__(
        self,
        config: BaseConfig,
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化蝦皮爬蟲
        
        Args:
            config: 爬蟲配置
            logger: 日誌記錄器
        """
        super().__init__(config, logger)
        self.browser_profile = BrowserProfile(config)
        self.browser_fingerprint = BrowserFingerprint(config)
        self.request_controller = RequestController(config)
        
    def _setup_browser(self) -> None:
        """設置瀏覽器"""
        try:
            super()._setup_browser()
            
            # 設置蝦皮特有的瀏覽器配置
            self.browser_profile = BrowserProfile(
                driver=self.driver,
                config=self.config.browser
            )
            
            self.request_controller = RequestController(
                driver=self.driver,
                config=self.config.request
            )
            
            self.browser_fingerprint = BrowserFingerprint(
                driver=self.driver,
                config=self.config.fingerprint
            )
            
            self.logger.info("成功設置蝦皮瀏覽器")
            
        except Exception as e:
            self.logger.error(f"設置蝦皮瀏覽器失敗: {str(e)}")
            raise ShopeeCrawlerError("設置蝦皮瀏覽器失敗", details={"error": str(e)})
        
    def search_products(
        self,
        keyword: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        搜索商品
        
        Args:
            keyword: 搜索關鍵字
            limit: 結果數量限制
            
        Returns:
            商品列表
        """
        try:
            # 使用 selenium_base 的服務進行爬取
            driver = self.browser_profile.create_driver()
            self.browser_fingerprint.setup(driver)
            
            # 構建搜索 URL
            search_url = f"https://shopee.tw/search?keyword={quote(keyword)}"
            
            # 訪問搜索頁面
            driver.get(search_url)
            
            # 等待商品列表加載
            self.wait_for_element(By.CSS_SELECTOR, "div[data-sqe='item']")
            
            # 模擬人類滾動
            self.browser_profile.simulate_human_scrolling()
            
            # 提取商品信息
            products = []
            product_elements = driver.find_elements(By.CSS_SELECTOR, "div[data-sqe='item']")
            
            for element in product_elements[:limit]:
                try:
                    product = {
                        "title": element.find_element(By.CSS_SELECTOR, "div[data-sqe='name']").text,
                        "price": element.find_element(By.CSS_SELECTOR, "div[data-sqe='price']").text,
                        "url": element.find_element(By.CSS_SELECTOR, "a").get_attribute("href")
                    }
                    products.append(product)
                except NoSuchElementException:
                    continue
            
            self.logger.info(f"成功搜索到 {len(products)} 個商品")
            return products
            
        except Exception as e:
            self.logger.error(f"搜索商品失敗: {str(e)}")
            raise ShopeeCrawlerError("搜索商品失敗", details={"error": str(e)})
        finally:
            driver.quit()
    
    def get_product_details(self, url: str) -> Dict[str, Any]:
        """
        獲取商品詳情
        
        Args:
            url: 商品 URL
            
        Returns:
            商品詳情
        """
        try:
            # 使用 selenium_base 的服務進行爬取
            session = self.request_controller.create_session()
            
            # 訪問商品頁面
            self.navigate(url)
            
            # 等待商品詳情加載
            self.wait_for_element(By.CSS_SELECTOR, "div[data-sqe='name']")
            
            # 模擬人類滾動
            self.browser_profile.simulate_human_scrolling()
            
            # 提取商品詳情
            details = {
                "title": self.driver.find_element(By.CSS_SELECTOR, "div[data-sqe='name']").text,
                "price": self.driver.find_element(By.CSS_SELECTOR, "div[data-sqe='price']").text,
                "description": self.driver.find_element(By.CSS_SELECTOR, "div[data-sqe='description']").text,
                "images": [img.get_attribute("src") for img in self.driver.find_elements(By.CSS_SELECTOR, "img[data-sqe='image']")]
            }
            
            self.logger.info("成功獲取商品詳情")
            return details
            
        except Exception as e:
            self.logger.error(f"獲取商品詳情失敗: {str(e)}")
            raise ShopeeCrawlerError("獲取商品詳情失敗", details={"error": str(e)})
        finally:
            session.close()
    
    def check_and_handle_captcha(self) -> bool:
        """
        檢查並處理驗證碼
        
        Returns:
            是否成功處理驗證碼
        """
        try:
            # 檢查是否存在驗證碼
            captcha_elements = self.driver.find_elements(By.CSS_SELECTOR, "div[data-sqe='captcha']")
            if not captcha_elements:
                return True
                
            self.logger.info("檢測到驗證碼，開始處理")
            
            # 處理驗證碼
            for element in captcha_elements:
                try:
                    # 點擊驗證碼
                    element.click()
                    time.sleep(2)
                    
                    # 等待驗證完成
                    WebDriverWait(self.driver, 10).until_not(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-sqe='captcha']"))
                    )
                    
                    self.logger.info("驗證碼處理成功")
                    return True
                except TimeoutException:
                    continue
                    
            self.logger.warning("驗證碼處理失敗")
            return False
            
        except Exception as e:
            self.logger.error(f"處理驗證碼失敗: {str(e)}")
            return False