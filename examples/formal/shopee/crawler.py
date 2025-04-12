#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import re
from urllib.parse import quote
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.remote.webelement import WebElement

"""
蝦皮爬蟲程式

提供蝦皮商品爬取功能，包括：
- 關鍵字搜尋
- 商品詳情爬取
- 驗證碼處理
"""

import json
import logging
from typing import Dict, List, Optional, Union, Generator, Any
from pathlib import Path
from datetime import datetime
import pickle

# 匯入核心模組
from src.core import (
    CrawlerEngine,
    CrawlerStateManager,
    ConfigLoader,
    CrawlerException,
    NavigationError,
    ExtractionError
)
from src.core.webdriver_manager import BrowserConfig, WebDriverManager

# 匯入工具類
from src.core.utils import (
    Logger,
    setup_logger,
    PathUtils,
    ConfigUtils,
    ErrorHandler,
    DataProcessor,
    BrowserUtils,
    URLUtils,
    ImageUtils,
    AudioUtils,
    TextUtils,
    CookieManager,
    SecurityUtils
)

# 匯入反偵測模組
from src.anti_detection import (
    AntiDetectionManager,
    BrowserFingerprint,
    ProxyManager,
    UserAgentManager,
    HumanBehavior,
    BaseScraper
)

# 匯入持久化模組
from src.persistence.manager.storage_manager import StorageManager
from src.persistence.handlers.local_handler import LocalStorageHandler as FileStorageHandler
from src.persistence.handlers.mongodb_handler import MongoDBHandler as DatabaseStorageHandler
from src.persistence.handlers.notion_handler import NotionHandler as CacheStorageHandler
from src.persistence.config import StorageConfig
from src.persistence.utils.core_mixin import CoreMixin

# 匯入驗證碼模組
from src.captcha import (
    CaptchaService,
    CaptchaConfig,
    CaptchaType,
    CaptchaResult
)

# 匯入認證模組
from src.auth import (
    LoginManager,
    SessionManager,
    CookieManager as AuthCookieManager
)

# 設置日誌
logger = setup_logger(__name__)

class ShopeeError(CrawlerException):
    """蝦皮爬蟲錯誤"""
    pass

class ShopeeCrawler(BaseScraper):
    """蝦皮爬蟲"""
    
    def __init__(self, config_dir: str = None, config_name: str = None):
        """
        初始化蝦皮爬蟲
        
        Args:
            config_dir: 配置目錄
            config_name: 配置文件名
        """
        # 構建完整的配置文件路徑
        config_path = os.path.join(config_dir, config_name) if config_dir and config_name else None
        data_dir = "./data"
        domain = "shopee.tw"
        
        # 調用父類初始化
        super().__init__(
            config_path=config_path,
            data_dir=data_dir,
            domain=domain,
            debug_mode=False
        )
        
        try:
            # 初始化基本URL
            self.base_url = f"https://{self.domain}"
            self.search_url = f"{self.base_url}/search"
            
            # 初始化WebDriver配置
            webdriver_config = {
                'headless': self.config.get('crawler', {}).get('headless', False),
                'proxy': self.config.get('security', {}).get('proxy'),
                'user_agent': self.config.get('security', {}).get('user_agent'),
                'window_size': (
                    self.config.get('crawler', {}).get('window_width', 1920),
                    self.config.get('crawler', {}).get('window_height', 1080)
                )
            }
            
            # 初始化WebDriver管理器
            self.webdriver_manager = WebDriverManager(webdriver_config)
            
            # 初始化反爬蟲管理器
            self.anti_detection_config = {
                "id": "shopee_crawler",
                "enabled": True,
                "max_retries": 3,
                "retry_delay": 5,
                "browser_fingerprint": {
                    "webgl": {
                        "noise": 0.15,
                        "vendor": "Google Inc.",
                        "renderer": "ANGLE (Intel)"
                    },
                    "canvas": {
                        "noise": 0.15,
                        "mode": "noise"
                    }
                },
                "human_behavior": {
                    "mouse_movement": True,
                    "keyboard_input": True,
                    "scroll_behavior": True,
                    "typing": {
                        "speed": {"min": 0.1, "max": 0.3},
                        "mistakes": True
                    },
                    "scrolling": {
                        "speed": "variable",
                        "pattern": "natural"
                    }
                },
                "proxy": {
                    "enabled": False,
                    "rotation": False
                },
                "request": {
                    "timeout": 60,
                    "headers": {
                        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
                    }
                }
            }
            self.anti_detection_manager = AntiDetectionManager(
                id="shopee_crawler",
                config=self.anti_detection_config
            )
            
            # 初始化選擇器
            self._init_selectors()
            
            # 初始化超時設置
            self._init_timeouts()
            
            # 初始化瀏覽器
            self.browser = self.webdriver_manager.get_driver()
            
            # 初始化驗證碼服務
            self.captcha_service = CaptchaService(
                browser=self.browser,
                config=self.config
            )
            
            # 初始化存儲管理器
            storage_config = StorageConfig(
                storage_mode="local",
                data_dir=self.config['crawler'].get('data_dir', 'examples/data/shopee'),
                default_collection="shopee_products",
                backup_enabled=True,
                auto_save=True,
                auto_save_interval=300,
                max_backups=5,
                encoding="utf-8",
                indent=2
            )
            storage_config.core_mixin = CoreMixin()
            storage_config.core_mixin.init_core_utils()
            self.storage_manager = StorageManager(
                config=storage_config
            )
            
            # 初始化狀態
            self.is_logged_in = False
            self.search_results = []
            self.product_details = []
            
            self.logger.info("操作成功: connect")
            
        except Exception as e:
            self.logger.error(f"初始化失敗: {str(e)}")
            raise

    def _init_selectors(self):
        """初始化選擇器"""
        # 搜索相關選擇器
        self.selectors = {
            'search': {
                'input': 'input.shopee-searchbar-input__input',
                'button': 'button.shopee-searchbar__search-button',
                'suggestions': 'div.shopee-searchbar-menu',
                'suggestion_items': 'div.shopee-searchbar-menu-item'
            },
            'product': {
                'items': '.shopee-search-item-result__item',
                'title': '.yQmmFK._1POlWt._36CEnF',
                'price': '.zp9xm9._1y2DMk._36CEnF',
                'sold': '.r6HknA.uEPGHT',
                'location': '.zGGwiV',
                'rating': '.shopee-rating-stars__star-wrapper',
                'link': 'a[data-sqe="link"]'
            },
            'pagination': {
                'next': 'button.shopee-icon-button--right',
                'current': '.shopee-mini-page-controller__current',
                'total': '.shopee-mini-page-controller__total'
            },
            'captcha': {
                'slider': '.shopee-rms-slider',
                'image': '.shopee-rms-image',
                'input': '.shopee-rms-input',
                'submit': '.shopee-rms-button'
            },
            'login': {
                'popup': '.shopee-popup',
                'close_button': '.shopee-popup__close-btn'
            }
        }

    def _init_timeouts(self):
        """初始化超時設置"""
        self.timeouts = {
            'page_load': 30,
            'element_wait': 20,
            'search_input': 10,
            'search_result': 40,
            'product_load': 35,
            'captcha_solve': 30,
            'scroll_wait': 2,
            'animation': 1
        }

    def close(self):
        """關閉爬蟲"""
        try:
            if self.webdriver_manager:
                self.webdriver_manager.close_all()
            if self.crawler_engine:
                self.crawler_engine.stop()
        except Exception as e:
            self.logger.error(f"關閉爬蟲失敗: {str(e)}")

    def search_products(self, keyword: str, max_pages: int = 1) -> Generator[Dict[str, Any], None, None]:
        """
        搜尋商品並返回結果
        
        Args:
            keyword: 搜尋關鍵字
            max_pages: 最大爬取頁數
            
        Yields:
            商品數據
        """
        try:
            search_url = f"{self.search_url}?keyword={quote(keyword)}"
            self.logger.info(f"開始搜尋商品: {keyword}")
            
            # 獲取 WebDriver 並設置指紋
            driver = self.webdriver_manager.get_driver()
            
            # 設置瀏覽器指紋
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5]
                    });
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['zh-TW', 'zh', 'en-US', 'en']
                    });
                    window.chrome = {
                        app: {
                            isInstalled: false,
                        },
                        webstore: {
                            onInstallStageChanged: {},
                            onDownloadProgress: {},
                        },
                        runtime: {
                            PlatformOs: {
                                MAC: 'mac',
                                WIN: 'win',
                                ANDROID: 'android',
                                CROS: 'cros',
                                LINUX: 'linux',
                                OPENBSD: 'openbsd',
                            },
                            PlatformArch: {
                                ARM: 'arm',
                                X86_32: 'x86-32',
                                X86_64: 'x86-64',
                            },
                            PlatformNaclArch: {
                                ARM: 'arm',
                                X86_32: 'x86-32',
                                X86_64: 'x86-64',
                            },
                            RequestUpdateCheckStatus: {
                                THROTTLED: 'throttled',
                                NO_UPDATE: 'no_update',
                                UPDATE_AVAILABLE: 'update_available',
                            },
                            OnInstalledReason: {
                                INSTALL: 'install',
                                UPDATE: 'update',
                                CHROME_UPDATE: 'chrome_update',
                                SHARED_MODULE_UPDATE: 'shared_module_update',
                            },
                            OnRestartRequiredReason: {
                                APP_UPDATE: 'app_update',
                                OS_UPDATE: 'os_update',
                                PERIODIC: 'periodic',
                            },
                        }
                    };
                    
                    // 修改 WebGL
                    const getParameter = WebGLRenderingContext.prototype.getParameter;
                    WebGLRenderingContext.prototype.getParameter = function(parameter) {
                        if (parameter === 37445) {
                            return 'Intel Inc.'
                        }
                        if (parameter === 37446) {
                            return 'Intel(R) Iris(TM) Plus Graphics'
                        }
                        return getParameter.apply(this, [parameter]);
                    };
                """
            })
            
            # 隨機延遲
            time.sleep(random.uniform(2, 5))
            
            # 訪問搜尋頁面
            driver.get(search_url)
            
            # 模擬人類行為：隨機滾動和移動
            for _ in range(random.randint(3, 6)):
                # 隨機滾動
                scroll_height = random.randint(100, 500)
                driver.execute_script(f"window.scrollTo({{top: {scroll_height}, behavior: 'smooth'}});")
                time.sleep(random.uniform(0.8, 2.5))
                
                # 隨機移動滑鼠
                element = driver.find_element(By.TAG_NAME, "body")
                action = ActionChains(driver)
                action.move_to_element_with_offset(
                    element,
                    random.randint(0, 1000),
                    random.randint(0, 1000)
                ).perform()
                time.sleep(random.uniform(0.3, 1.0))
                
                # 偶爾點擊空白處
                if random.random() < 0.3:
                    action.click().perform()
                    time.sleep(random.uniform(0.5, 1.5))
            
            # 檢查並關閉登入彈窗
            try:
                login_popup = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors['login']['popup']))
                )
                if login_popup:
                    # 模擬人類行為：移動滑鼠
                    close_button = driver.find_element(By.CSS_SELECTOR, self.selectors['login']['close_button'])
                    action = ActionChains(driver)
                    
                    # 先移動到附近
                    action.move_to_element_with_offset(
                        close_button,
                        random.randint(-10, 10),
                        random.randint(-10, 10)
                    ).perform()
                    time.sleep(random.uniform(0.2, 0.5))
                    
                    # 再移動到按鈕上
                    action.move_to_element(close_button).perform()
                    time.sleep(random.uniform(0.3, 0.7))
                    
                    # 點擊
                    action.click().perform()
                    time.sleep(random.uniform(1.0, 2.0))
            except:
                pass
            
            # 等待商品列表加載
            try:
                WebDriverWait(driver, self.timeouts['search_result']).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, self.selectors['product']['items']))
                )
            except:
                self.logger.error("無法載入商品列表，可能需要登入")
                return
            
            # 處理驗證碼
            if self.captcha_service.detect_captcha():
                self.logger.info("檢測到驗證碼，嘗試解決...")
                if not self.captcha_service.solve_captcha():
                    self.logger.error("解決驗證碼失敗")
                    return
            
            # 隨機暫停
            time.sleep(random.uniform(2, 6))
            
            # 爬取指定頁數
            current_page = 1
            while current_page <= max_pages:
                self.logger.info(f"正在爬取第 {current_page} 頁")
                
                # 等待商品列表加載
                time.sleep(self.timeouts['search_result'])
                
                # 提取商品數據
                product_elements = driver.find_elements(By.CSS_SELECTOR, self.selectors['product']['items'])
                
                for element in product_elements:
                    try:
                        product_data = self._extract_product_data(element)
                        if product_data:
                            yield product_data
                    except Exception as e:
                        self.logger.error(f"提取商品數據失敗: {str(e)}")
                        continue
                
                # 檢查是否有下一頁
                if current_page < max_pages:
                    try:
                        next_button = driver.find_element(By.CSS_SELECTOR, self.selectors['pagination']['next'])
                        if not next_button.is_enabled():
                            self.logger.info("已到達最後一頁")
                            break
                        
                        # 點擊下一頁
                        next_button.click()
                        current_page += 1
                        
                        # 等待新頁面加載
                        time.sleep(self.timeouts['page_load'])
                    except Exception as e:
                        self.logger.error(f"翻頁失敗: {str(e)}")
                        break
                else:
                    break
                    
        except Exception as e:
            self.logger.error(f"搜尋商品時發生錯誤: {str(e)}")
            raise
            
    def _extract_product_data(self, element: WebElement) -> Optional[Dict[str, Any]]:
        """
        從商品元素中提取數據
        
        Args:
            element: 商品元素
            
        Returns:
            商品數據
        """
        try:
            # 提取商品連結和ID
            link_element = element.find_element(By.CSS_SELECTOR, self.selectors['product']['link'])
            product_url = link_element.get_attribute('href')
            product_id = None
            
            # 從URL中提取商品ID
            if product_url:
                match = re.search(r'i\.(\d+)\.', product_url)
                if match:
                    product_id = match.group(1)
            
            # 提取商品標題
            title_element = element.find_element(By.CSS_SELECTOR, self.selectors['product']['title'])
            title = title_element.text.strip()
            
            # 提取商品價格
            price_element = element.find_element(By.CSS_SELECTOR, self.selectors['product']['price'])
            price_text = price_element.text.strip()
            price = float(re.sub(r'[^\d.]', '', price_text))
            
            # 提取銷量
            sold_element = element.find_element(By.CSS_SELECTOR, self.selectors['product']['sold'])
            sold_text = sold_element.text.strip()
            sold = int(re.sub(r'[^\d]', '', sold_text)) if sold_text else 0
            
            # 提取評分
            rating = None
            try:
                rating_element = element.find_element(By.CSS_SELECTOR, self.selectors['product']['rating'])
                rating = float(rating_element.text.strip())
            except:
                pass
            
            # 提取商品圖片
            image_url = None
            try:
                image_element = element.find_element(By.TAG_NAME, 'img')
                image_url = image_element.get_attribute('src')
            except:
                pass
            
            # 提取商家位置
            location = None
            try:
                location_element = element.find_element(By.CSS_SELECTOR, self.selectors['product']['location'])
                location = location_element.text.strip()
            except:
                pass
            
            # 構建商品數據
            product_data = {
                'id': product_id,
                'title': title,
                'price': price,
                'sold': sold,
                'rating': rating,
                'location': location,
                'image_url': image_url,
                'product_url': product_url
            }
            
            # 清理數據
            return DataProcessor.clean_product_data(product_data)
            
        except Exception as e:
            self.logger.error(f"提取商品數據時發生錯誤: {str(e)}")
            return None

    # 其他方法保持不變
    # ...