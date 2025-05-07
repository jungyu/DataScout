#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Nikkei Asia 爬蟲 (關鍵字版)

此模組提供日經亞洲版(Nikkei Asia)新聞網站的爬蟲功能，可以批次搜尋關鍵字組合並支援斷點續爬。
加入反爬蟲偵測與處理，以及 URL 參數翻頁功能。
"""

import logging
import json
import csv
import sys
import os
import random
import time
from pathlib import Path
from urllib.parse import quote
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

# 確保能找到相關模組
current_dir = Path(__file__).parent
sys.path.append(str(current_dir.parent.parent.parent))  # 添加專案根目錄

# 從 playwright_base 導入反爬蟲相關功能
from playwright_base import PlaywrightBase, setup_logger
from playwright_base.anti_detection import HumanLikeBehavior, UserAgentManager
from playwright_base.utils.exceptions import PlaywrightBaseException, CaptchaException

# 網站配置
SITE_CONFIG = {
    "base_url": "https://asia.nikkei.com",
    "search_url": "https://asia.nikkei.com/search",
    "save_path": "../data",
    "request": {
        "timeout": 60000
    },
    "max_pages": 5  # 最大翻頁數
}

# 選擇器配置 - 根據 Nikkei Asia 網站結構調整
SELECTORS = {
    "search": {
        "list_item": ".article-card-list__item", # 新聞列表項
        "title": ".article-card__headline", # 標題
        "date": ".article-card__date", # 發布日期
        "summary": ".article-card__summary", # 摘要
        "url": ".article-card__headline a", # 連結
        "count": ".title__search-result" # 總筆數選擇器
    },
    "article": {
        "title": "h1.article-header__title", # 文章標題
        "date": ".article-header__date", # 文章日期
        "author": ".article-header__author", # 作者
        "content": ".ezrichtext-field p", # 文章內容
        "image": ".article-header__image img" # 圖片
    },
    "paywall": {
        "login_button": ".login-link", 
        "paywall": ".piano-container", 
        "cookie_banner": ".cookie-consent, .cookie-banner", # 新增 cookie-banner 選擇器
        "cookie_accept": ".cookie-banner__button[data-acceptance-button], .btn.btn--white-fill.cookie-banner__button", # 更新接受按鈕
        "cookie_close": ".cookie-banner__link--close[data-close-button], .cookie-banner__link.cookie-banner__link--close", # 新增關閉按鈕
        "subscription_banner": ".subscription-prompt",
        "close_button": ".close-button"
    }
}

# 瀏覽器配置
BROWSER_CONFIG = {
    "headless": False,  # 保持為 False 以便處理彈窗
    "browser_type": "chromium",
    "launch_options": {
        "args": [
            "--disable-web-security", 
            "--disable-features=IsolateOrigins,site-per-process",
            "--disable-blink-features=AutomationControlled",
            "--disable-blink-features=SameSiteByDefaultCookies",
            "--disable-site-isolation-trials",
            "--no-sandbox",
            "--disable-setuid-sandbox"
        ]
    },
    "context_options": {
        "viewport": {"width": 1920, "height": 1080},
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "is_mobile": False,
        "locale": "en-US",
        "timezone_id": "America/New_York",
        "accept_downloads": True,
        "ignore_https_errors": True,
        "has_touch": False
    }
}

# 反爬蟲設定
ANTI_DETECTION_CONFIG = {
    "random_delay": True,
    "delay_min": 3.0,
    "delay_max": 7.0,
    "page_delay_min": 5.0,
    "page_delay_max": 15.0,
    "keyword_delay_min": 15.0,
    "keyword_delay_max": 30.0,
    "human_like": True
}

# 日誌檔案路徑
LOGS_FILE = Path(SITE_CONFIG["save_path"]) / "news_nikkei_logs.csv"

# 分頁進度記錄檔案
PAGE_LOGS_FILE = Path(SITE_CONFIG["save_path"]) / "news_nikkei_page_logs.csv"

logger = setup_logger(name=__name__)

class PageException(Exception):
    """頁面操作失敗異常"""
    pass

class ElementException(Exception):
    """元素操作失敗異常"""
    pass

class NikkeiScraper(PlaywrightBase):
    """
    Nikkei Asia 爬蟲類
    繼承自 PlaywrightBase，提供日經亞洲版網站的爬蟲功能
    """

    def __init__(self):
        """初始化 Nikkei Asia 爬蟲"""
        # 檢查並創建 storage.json 如果它不存在
        if not os.path.exists("storage.json"):
            empty_storage = {
                "cookies": [],
                "origins": []
            }
            with open("storage.json", "w") as f:
                json.dump(empty_storage, f)
            logger.info("已創建空的 storage.json 檔案")
            
        self.logger = logging.getLogger(__name__)
        super().__init__(
            headless=BROWSER_CONFIG.get("headless", False),
            browser_type=BROWSER_CONFIG.get("browser_type", "chromium"),
            **BROWSER_CONFIG.get("launch_options", {})
        )

        self.site_config = SITE_CONFIG
        self.selectors = SELECTORS
        self.human_like = HumanLikeBehavior()  # 人類行為模擬
        self.user_agent_manager = UserAgentManager()  # 用戶代理管理

        # 設置瀏覽器上下文選項
        if self._context:
            context_options = BROWSER_CONFIG.get("context_options", {})
            if "viewport" in context_options:
                self._context.set_viewport_size(**context_options["viewport"])

        # 添加掩蓋自動化特徵的腳本
        self._stealth_mode_setup()

        # 設置初始 Cookie
        self._setup_initial_cookies()

        # 啟動瀏覽器
        self.start()

        logger.info("Nikkei Asia 爬蟲已初始化")

    def _stealth_mode_setup(self):
        """設置隱身模式，掩蓋自動化特徵"""
        if self._context:
            stealth_js = """
            () => {
                // 覆蓋 navigator 屬性
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                
                // 注入欺騙性指紋
                const setFingerprintDeception = () => {
                    // 模擬硬體併發數
                    Object.defineProperty(navigator, 'hardwareConcurrency', {
                        get: () => 8
                    });
                    
                    // 模擬記憶體
                    Object.defineProperty(navigator, 'deviceMemory', {
                        get: () => 8
                    });
                    
                    // 模擬語言
                    Object.defineProperty(navigator, 'language', {
                        get: () => 'en-US'
                    });
                    
                    // 模擬 platform
                    Object.defineProperty(navigator, 'platform', {
                        get: () => 'MacIntel'
                    });
                };
                setFingerprintDeception();
                
                // 模擬正常的 Cookie 行為
                const emulateCookieBehavior = () => {
                    const cookieDesc = Object.getOwnPropertyDescriptor(Document.prototype, 'cookie') || {};
                    const cookieGetter = cookieDesc.get || function() {};
                    const cookieSetter = cookieDesc.set || function() {};
                    
                    Object.defineProperty(Document.prototype, 'cookie', {
                        get: function() {
                            return cookieGetter.call(document);
                        },
                        set: function(val) {
                            cookieSetter.call(document, val);
                            return true;
                        },
                        enumerable: true
                    });
                };
                emulateCookieBehavior();
                
                // 模擬普通的滑鼠移動和交互
                const simulateHumanInteractions = () => {
                    const randomMoveInterval = setInterval(() => {
                        const randomX = Math.floor(Math.random() * window.innerWidth);
                        const randomY = Math.floor(Math.random() * window.innerHeight);
                        
                        // 創建滑鼠事件
                        const events = ['mousemove', 'mouseover', 'mouseout'];
                        const event = events[Math.floor(Math.random() * events.length)];
                        
                        const mouseEvent = new MouseEvent(event, {
                            view: window,
                            bubbles: true,
                            cancelable: true,
                            clientX: randomX,
                            clientY: randomY
                        });
                        
                        document.dispatchEvent(mouseEvent);
                    }, 2000 + Math.random() * 3000);
                    
                    // 5分鐘後清除模擬
                    setTimeout(() => {
                        clearInterval(randomMoveInterval);
                    }, 300000);
                };
                
                // 啟動模擬
                setTimeout(simulateHumanInteractions, 5000);
                
                // 覆蓋 Permissions API
                if (navigator.permissions) {
                    const originalQuery = navigator.permissions.query;
                    navigator.permissions.query = function(parameters) {
                        if (parameters.name === 'notifications') {
                            return Promise.resolve({ state: "prompt", onchange: null });
                        }
                        return originalQuery.apply(this, arguments);
                    };
                }
            }
            """
            
            self._context.add_init_script(stealth_js)
            logger.info("已添加隱身模式腳本")

    def _setup_initial_cookies(self):
        """設置初始化 Cookie"""
        try:
            self._context.add_cookies([
                {
                    "name": "visited",
                    "value": "true",
                    "domain": ".asia.nikkei.com",
                    "path": "/"
                },
                {
                    "name": "cookie_consent",
                    "value": "accepted",
                    "domain": ".asia.nikkei.com",
                    "path": "/"
                },
                {
                    "name": "nikkei_cookie_banner_closed",  # 新增
                    "value": "true",
                    "domain": ".asia.nikkei.com",
                    "path": "/"
                },
                {
                    "name": "nikkei_cookie_accepted",  # 新增
                    "value": "true",
                    "domain": ".asia.nikkei.com",
                    "path": "/"
                },
                {
                    "name": "gdpr_cookie_accepted",  # 新增
                    "value": "true",
                    "domain": ".asia.nikkei.com",
                    "path": "/"
                },
                {
                    "name": "visited_articles",
                    "value": "[]",
                    "domain": ".asia.nikkei.com",
                    "path": "/"
                }
            ])
            logger.info("已設置初始 Cookie")
        except Exception as e:
            logger.warning(f"設置初始 Cookie 時發生錯誤: {str(e)}")

    def _random_delay(self, min_delay=None, max_delay=None, delay_type=None):
        """
        隨機延遲以模擬人類行為
        
        Args:
            min_delay: 最小延遲時間（秒）
            max_delay: 最大延遲時間（秒）
            delay_type: 延遲類型 (None, 'page', 'keyword')
        """
        if delay_type == 'page':
            _min_delay = min_delay if min_delay is not None else ANTI_DETECTION_CONFIG.get("page_delay_min", 5.0)
            _max_delay = max_delay if max_delay is not None else ANTI_DETECTION_CONFIG.get("page_delay_max", 15.0)
        elif delay_type == 'keyword':
            _min_delay = min_delay if min_delay is not None else ANTI_DETECTION_CONFIG.get("keyword_delay_min", 15.0)
            _max_delay = max_delay if max_delay is not None else ANTI_DETECTION_CONFIG.get("keyword_delay_max", 30.0)
        else:
            _min_delay = min_delay if min_delay is not None else ANTI_DETECTION_CONFIG.get("delay_min", 3.0)
            _max_delay = max_delay if max_delay is not None else ANTI_DETECTION_CONFIG.get("delay_max", 7.0)
        
        delay = random.uniform(_min_delay, _max_delay)
        logger.info(f"延遲 {delay:.2f} 秒 ({delay_type if delay_type else '一般'})")
        time.sleep(delay)

    def _human_like_scroll(self):
        """模擬人類滾動頁面行為"""
        try:
            # 獲取頁面高度
            page_height = self.page.evaluate("""
                () => document.body.scrollHeight
            """)
            
            # 隨機滾動次數
            scroll_times = random.randint(3, 8)
            
            for i in range(scroll_times):
                # 隨機滾動距離
                scroll_distance = random.randint(300, 700)
                current_position = self.page.evaluate("() => window.pageYOffset")
                target_position = min(current_position + scroll_distance, page_height - 800)
                
                # 模擬平滑滾動
                self.page.evaluate(f"""
                    () => {{
                        window.scrollTo({{
                            top: {target_position}, 
                            behavior: 'smooth'
                        }});
                    }}
                """)
                
                # 短暫等待
                time.sleep(random.uniform(0.5, 2.0))
            
            logger.info("已完成人類化滾動頁面")
            
        except Exception as e:
            logger.warning(f"模擬滾動頁面時發生錯誤: {str(e)}")

    def search_news(self, keyword: str, save_page: bool = False) -> List[Dict[str, Any]]:
        """
        搜索新聞並提取結果
        
        Args:
            keyword: 搜索關鍵字
            save_page: 是否保存頁面內容，默認為False
            
        Returns:
            List[Dict[str, Any]]: 新聞列表
        """
        try:
            url = f"{self.site_config['search_url']}?query={quote(keyword)}"
            logger.info(f"搜索新聞: {keyword}")
            
            # 先訪問主頁
            logger.info("先訪問 Nikkei Asia 主頁以建立 session")
            self.navigate(self.site_config['base_url'])
            self._random_delay(2, 4)
            
            # 處理彈窗或 Cookie 提示
            if self._check_for_paywall_or_popup():
                self._handle_paywall_or_popup()
            
            # 再訪問搜尋頁面
            self.navigate(url)
            self._random_delay(2, 3)
            
            self.wait_for_load_state("networkidle", timeout=self.site_config.get("request", {}).get("timeout", 60000))
            
            # 檢查是否需要處理彈窗或付費牆
            if self._check_for_paywall_or_popup():
                if not self._handle_paywall_or_popup():
                    logger.error("付費牆或彈窗處理失敗")
                    raise CaptchaException("付費牆或彈窗處理失敗")
            
            # 嘗試等待搜索結果加載完成
            try:
                self.page.wait_for_selector(self.selectors["search"]["list_item"], timeout=10000)
            except Exception:
                logger.warning("未找到搜索結果元素，請檢查頁面")
                
                # 保存錯誤頁面以便分析
                self._save_page_content(f"error_{keyword}")
                
                # 可能需要手動操作以通過檢測
                print("\n無法自動處理此頁面。請在瀏覽器中手動操作以通過網站檢測。")
                input("完成手動操作後，請按 Enter 繼續...")
                
                try:
                    self.page.wait_for_selector(self.selectors["search"]["list_item"], timeout=10000)
                except Exception:
                    logger.error("即使手動操作後仍未找到搜索結果")
                    return []
            
            # 模擬人類滾動行為
            self._human_like_scroll()
            
            # 獲取總結果數
            total_count = self._get_total_count()
            if total_count > 0:
                logger.info(f"搜索結果總數: {total_count}")
            
            if save_page:
                self._save_page_content(keyword)
            
            return self._extract_news_list()
            
        except CaptchaException as e:
            logger.error(f"付費牆或彈窗處理錯誤: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"搜尋新聞時發生錯誤: {str(e)}")
            raise PageException(f"搜尋新聞失敗: {str(e)}")

    def _check_for_paywall_or_popup(self) -> bool:
        """檢查頁面是否包含付費牆或彈窗"""
        try:
            # 檢查付費牆和彈窗
            paywall_selectors = [
                self.selectors["paywall"]["paywall"],
                self.selectors["paywall"]["login_button"],
                self.selectors["paywall"]["cookie_banner"],
                self.selectors["paywall"]["subscription_banner"],
                "a.cookie-banner__button[data-acceptance-button]",  # 新增
                ".cookie-banner",  # 新增
                "#piano-container",
                ".gdpr-banner",
                ".newsletter-signup",
                ".modal-dialog",
                ".modal-content",
                ".adblock-detection"
            ]
            
            for selector in paywall_selectors:
                if self.page.query_selector(selector):
                    logger.warning(f"檢測到付費牆或彈窗元素: {selector}")
                    return True
            
            # 檢查頁面內容是否包含付費牆相關文字
            content = self.page.content().lower()
            paywall_keywords = [
                "subscribe", "subscription", "sign in", "log in", "login", 
                "register", "trial", "cookie", "consent", "premium content",
                "paid content", "paywall", "continue reading", "create an account"
            ]
            
            for keyword in paywall_keywords:
                if keyword.lower() in content:
                    logger.warning(f"檢測到付費牆關鍵詞: {keyword}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"檢查付費牆或彈窗時發生錯誤: {str(e)}")
            return False

    def _handle_paywall_or_popup(self) -> bool:
        """處理付費牆或彈窗"""
        try:
            # 特別處理 Nikkei 的 Cookie 彈窗
            nikkei_cookie_selectors = [
                "a.cookie-banner__button[data-acceptance-button]",
                ".btn.btn--white-fill.cookie-banner__button",
                ".cookie-banner__button[data-acceptance-button]"
            ]
            
            for selector in nikkei_cookie_selectors:
                try:
                    if self.page.query_selector(selector):
                        logger.info(f"點擊 Nikkei Cookie 同意按鈕: {selector}")
                        self.page.click(selector)
                        self._random_delay(1, 2)
                        # 儲存接受 cookie 狀態
                        self._save_cookie_acceptance_state()
                        return True
                except Exception as e:
                    logger.warning(f"點擊 Nikkei Cookie 按鈕 {selector} 失敗: {str(e)}")
                    continue
            
            # 處理 Cookie 彈窗 (一般處理)
            cookie_selectors = [
                self.selectors["paywall"]["cookie_accept"],
                ".cookie-consent__button",
                ".gdpr-banner-accept",
                ".accept-cookies",
                "button:has-text('Accept')",
                "button:has-text('Accept All')",
                "button:has-text('I Accept')",
                "button:has-text('Continue')",
                "button:has-text('Agree')"
            ]
            
            for selector in cookie_selectors:
                try:
                    if self.page.query_selector(selector):
                        logger.info(f"點擊 Cookie 同意按鈕: {selector}")
                        self.page.click(selector)
                        self._random_delay(1, 3)
                        return True
                except Exception as e:
                    logger.warning(f"點擊按鈕 {selector} 失敗: {str(e)}")
                    continue
            
            # 處理其他彈窗
            popup_selectors = [
                self.selectors["paywall"]["close_button"],
                ".modal-close",
                ".close-button",
                ".newsletter-signup__close",
                ".modal .close",
                "[aria-label='Close']"
            ]
            
            for selector in popup_selectors:
                try:
                    if self.page.query_selector(selector):
                        logger.info(f"點擊關閉彈窗按鈕: {selector}")
                        self.page.click(selector)
                        self._random_delay(1, 3)
                        return True
                except Exception as e:
                    logger.warning(f"點擊按鈕 {selector} 失敗: {str(e)}")
                    continue
            
            # 如果付費牆不能自動處理，提示用戶手動處理
            if self.page.query_selector(self.selectors["paywall"]["paywall"]) or \
               self.page.query_selector(self.selectors["paywall"]["login_button"]):
                logger.warning("檢測到付費牆，需要手動處理")
                print("\n檢測到 Nikkei Asia 付費牆，請在瀏覽器中手動登入或關閉彈窗。")
                print("如果您有 Nikkei Asia 帳號，請現在登入；如果沒有，請嘗試關閉彈窗或繼續瀏覽。")
                input("完成處理後，請按 Enter 繼續...")
                
                # 等待頁面加載
                self.wait_for_load_state("networkidle")
                self._random_delay(1, 2)
            
            return True
            
        except Exception as e:
            logger.error(f"處理付費牆或彈窗時發生錯誤: {str(e)}")
            return False

    def _save_cookie_acceptance_state(self):
        """儲存 Cookie 接受狀態"""
        try:
            # 設置 Nikkei 特定的 Cookie
            self._context.add_cookies([
                {
                    "name": "nikkei_cookie_banner_closed",
                    "value": "true",
                    "domain": ".asia.nikkei.com",
                    "path": "/"
                },
                {
                    "name": "nikkei_cookie_accepted", 
                    "value": "true",
                    "domain": ".asia.nikkei.com",
                    "path": "/"
                },
                {
                    "name": "gdpr_cookie_accepted",
                    "value": "true",
                    "domain": ".asia.nikkei.com",
                    "path": "/"
                }
            ])
            
            # 將接受狀態儲存到 storage.json
            try:
                storage = self._context.storage_state()
                with open("storage.json", "w") as f:
                    json.dump(storage, f)
                logger.info("已將 Cookie 接受狀態儲存到 storage.json")
            except Exception as e:
                logger.warning(f"儲存 storage 狀態時發生錯誤: {str(e)}")
                
            logger.info("已設置 Nikkei Cookie 接受狀態")
        except Exception as e:
            logger.warning(f"儲存 Cookie 接受狀態時發生錯誤: {str(e)}")

    def _get_total_count(self) -> int:
        """獲取搜索結果的總數量"""
        try:
            count_selector = self.selectors["search"]["count"]
            count_element = self.page.query_selector(count_selector)
            if count_element:
                count_text = count_element.text_content().strip()
                import re
                # 正則表達式匹配數字，例如 "123 results for..."
                numbers = re.findall(r'\d+', count_text)
                if numbers:
                    return int(numbers[0])
            return 0
        except Exception as e:
            logger.warning(f"獲取搜索結果總數時發生錯誤: {str(e)}")
            return 0

    def _save_page_content(self, keyword: str):
        """保存頁面內容和截圖"""
        try:
            base_name = f"nikkei_search_{keyword}"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"{base_name}_{timestamp}"

            save_dir = Path(self.site_config.get("save_path", "../data")) / "pages"
            save_dir.mkdir(parents=True, exist_ok=True)

            content = self.page.content()
            html_path = save_dir / f"{file_name}.html"
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(content)

            screenshot_path = save_dir / f"{file_name}.png"
            self.page.screenshot(path=str(screenshot_path))

            logger.info(f"已保存頁面內容: HTML={html_path}, 截圖={screenshot_path}")
        except Exception as e:
            logger.warning(f"保存頁面內容時發生錯誤: {str(e)}")

    def _extract_news_list(self) -> List[Dict[str, Any]]:
        """從頁面提取新聞列表"""
        news_list = []
        selectors = self.selectors.get("search", {})

        try:
            news_elements = self.page.query_selector_all(selectors.get("list_item", ""))
            logger.info(f"找到 {len(news_elements)} 條新聞")

            for element in news_elements:
                try:
                    news = self._extract_news_data(element, selectors)
                    if news:
                        news_list.append(news)
                except Exception as e:
                    logger.error(f"提取新聞信息失敗: {str(e)}")
                    continue

            logger.info(f"成功提取 {len(news_list)} 條新聞")
            return news_list

        except Exception as e:
            logger.error(f"提取新聞列表時發生錯誤: {str(e)}")
            return []

    def _extract_news_data(self, element, selectors: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """從元素中提取新聞數據"""
        try:
            news = {}

            # 提取標題
            if "title" in selectors:
                try:
                    title_element = element.query_selector(selectors["title"])
                    if title_element:
                        news["title"] = title_element.text_content().strip()
                except Exception:
                    news["title"] = ""

            # 提取日期
            if "date" in selectors:
                try:
                    date_element = element.query_selector(selectors["date"])
                    if date_element:
                        news["date"] = date_element.text_content().strip()
                except Exception:
                    news["date"] = ""

            # 提取摘要
            if "summary" in selectors:
                try:
                    summary_element = element.query_selector(selectors["summary"])
                    if summary_element:
                        news["summary"] = summary_element.text_content().strip()
                except Exception:
                    news["summary"] = ""

            # 提取 URL
            if "url" in selectors:
                try:
                    url_element = element.query_selector(selectors["url"])
                    if url_element:
                        url = url_element.get_attribute("href")
                        if url.startswith("/"):
                            url = f"{self.site_config['base_url']}{url}"
                        news["url"] = url
                except Exception:
                    news["url"] = ""

            return news

        except Exception as e:
            logger.error(f"提取新聞數據時發生錯誤: {str(e)}")
            return None

    def paginate_results(self, keyword: str, max_pages: int = 5) -> List[Dict[str, Any]]:
        """
        使用 URL 參數方式翻頁獲取更多結果

        Args:
            keyword: 搜尋關鍵字
            max_pages: 最大翻頁數，默認為5
            
        Returns:
            List[Dict[str, Any]]: 合併所有頁面的新聞列表
        """
        all_news = []
        
        # 先提取第一頁的新聞
        logger.info(f"提取第 1 頁的新聞")
        initial_news = self._extract_news_list()
        all_news.extend(initial_news)
        
        # 獲取總結果數量
        total_count = self._get_total_count()
        if total_count > 0:
            logger.info(f"搜索結果總數: {total_count}")
        
        # 告知使用者翻頁即將開始
        if max_pages > 1:
            print(f"\n即將開始翻頁，計劃瀏覽 {max_pages} 頁。")
            print("若需要手動處理付費牆或暫停，請按 Ctrl+C")
            try:
                time.sleep(2)  # 給使用者閱讀提示的時間
            except KeyboardInterrupt:
                input("\n程式暫停。完成處理後，請按 Enter 繼續...")
        
        # 通過 URL 參數翻頁
        for page in range(2, max_pages + 1):
            try:
                # 構建帶有頁碼的 URL
                page_url = f"{self.site_config['search_url']}?query={quote(keyword)}&page={page}"
                logger.info(f"訪問第 {page} 頁: {page_url}")
                
                # 顯示進度
                print(f"\n正在獲取第 {page}/{max_pages} 頁的結果...")
                
                # 訪問頁面
                self.navigate(page_url)
                
                # 使用延遲模擬人類行為
                self._random_delay(2, 5, 'page')
                
                # 等待頁面加載
                self.wait_for_load_state("networkidle", timeout=20000)
                
                # 檢查是否需要處理彈窗或付費牆
                if self._check_for_paywall_or_popup():
                    if not self._handle_paywall_or_popup():
                        logger.error("付費牆或彈窗處理失敗")
                        continue
                
                try:
                    # 等待搜索結果列表
                    self.page.wait_for_selector(self.selectors["search"]["list_item"], timeout=10000)
                except Exception:
                    logger.warning(f"第 {page} 頁未找到搜索結果，可能已到達末頁")
                    break
                
                # 模擬人類滾動行為
                self._human_like_scroll()
                
                # 提取當前頁的新聞
                current_page_news = self._extract_news_list()
                
                # 記錄此頁的狀態
                log_page_status(keyword, page, len(current_page_news), "success")
                
                if not current_page_news:
                    logger.info(f"第 {page} 頁未找到新聞，可能已到達末頁")
                    break
                
                # 合併到總列表中
                all_news.extend(current_page_news)
                logger.info(f"已獲取第 {page} 頁，當前總共有 {len(all_news)} 條新聞")
                
            except Exception as e:
                logger.error(f"獲取第 {page} 頁時發生錯誤: {str(e)}")
                log_page_status(keyword, page, 0, "failed")
                break
        
        logger.info(f"成功獲取 {len(all_news)} 條新聞數據")
        return all_news

    def get_article_detail(self, url: str, article_count: int, total_count: int) -> Dict[str, Any]:
        """
        獲取新聞文章詳情

        Args:
            url: 新聞文章 URL
            article_count: 當前處理的文章編號
            total_count: 總文章數量

        Returns:
            Dict[str, Any]: 新聞文章詳情
        """
        try:
            logger.info(f"獲取新聞詳情 ({article_count}/{total_count}): {url}")
            
            # 顯示進度給使用者
            print(f"\r處理文章 {article_count}/{total_count}", end="")

            self.navigate(url)
            self._random_delay(2, 5)  # 增加等待時間
            
            self.wait_for_load_state("networkidle")
            
            # 檢查是否需要處理付費牆或彈窗
            if self._check_for_paywall_or_popup():
                print(f"\n檢測到第 {article_count} 篇文章需要處理付費牆或彈窗")
                if not self._handle_paywall_or_popup():
                    logger.error("付費牆或彈窗處理失敗")
                    raise CaptchaException("付費牆或彈窗處理失敗")

            # 模擬人類閱讀行為
            self._human_like_scroll()

            article = {}
            selectors = self.selectors.get("article", {})

            # 提取標題
            if "title" in selectors:
                try:
                    title_element = self.page.query_selector(selectors["title"])
                    if title_element:
                        article["title"] = title_element.text_content().strip()
                except Exception:
                    article["title"] = ""

            # 提取日期
            if "date" in selectors:
                try:
                    date_element = self.page.query_selector(selectors["date"])
                    if date_element:
                        article["date"] = date_element.text_content().strip()
                except Exception:
                    article["date"] = ""

            # 提取作者
            if "author" in selectors:
                try:
                    author_element = self.page.query_selector(selectors["author"])
                    if author_element:
                        article["author"] = author_element.text_content().strip()
                except Exception:
                    article["author"] = ""

            # 提取內容
            if "content" in selectors:
                try:
                    content_elements = self.page.query_selector_all(selectors["content"])
                    article["content"] = "\n\n".join([p.text_content().strip() for p in content_elements if p.text_content().strip()])
                except Exception:
                    article["content"] = ""

            # 提取圖片
            if "image" in selectors:
                try:
                    image_element = self.page.query_selector(selectors["image"])
                    if image_element:
                        article["image_url"] = image_element.get_attribute("src")
                except Exception:
                    article["image_url"] = ""

            article["url"] = url
            article["retrieved_at"] = datetime.now().isoformat()

            logger.info(f"成功提取新聞詳情: {article.get('title', '')}")
            return article

        except CaptchaException as e:
            logger.error(f"付費牆處理錯誤: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"獲取新聞詳情時發生錯誤: {url}, {str(e)}")
            raise

    def close(self):
        """關閉瀏覽器"""
        super().close()
        logger.info("Nikkei Asia 爬蟲已關閉")

def load_keywords() -> List[List[str]]:
    """從 keywords.json 檔案讀取關鍵字組合"""
    try:
        keywords_file = current_dir / "keywords.json"
        with open(keywords_file, "r") as f:
            keywords = json.load(f)
        logger.info(f"已從 {keywords_file} 載入 {len(keywords)} 組關鍵字")
        return keywords
    except Exception as e:
        logger.error(f"讀取關鍵字檔案時發生錯誤: {str(e)}")
        return []

def save_results(keyword_pair: List[str], news_list: List[Dict[str, Any]]):
    """將搜尋結果保存到 JSON 檔案"""
    try:
        save_dir = Path(SITE_CONFIG["save_path"])
        save_dir.mkdir(parents=True, exist_ok=True)
        
        keyword_str = "_".join(keyword_pair).replace(" ", "_").lower()
        file_name = f"news_nikkei_{keyword_str}.json"
        file_path = save_dir / file_name
        
        # 如果檔案已存在，載入並合併資料
        existing_data = []
        if file_path.exists():
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)
                logger.info(f"已載入現有資料: {file_path} ({len(existing_data)} 條)")
            except Exception as e:
                logger.warning(f"載入現有資料時發生錯誤: {str(e)}")
        
        # 合併並去重
        urls = {item["url"] for item in existing_data}
        for item in news_list:
            if item.get("url") and item["url"] not in urls:
                existing_data.append(item)
                urls.add(item["url"])
        
        # 儲存資料
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"已保存搜尋結果: {file_path} (共 {len(existing_data)} 條)")
    except Exception as e:
        logger.error(f"保存結果時發生錯誤: {str(e)}")

def get_processed_keywords() -> List[Tuple[str, str]]:
    """從日誌檔案讀取已處理的關鍵字組合"""
    processed = []
    if LOGS_FILE.exists():
        try:
            with open(LOGS_FILE, "r", newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                next(reader, None)  # 跳過標題行
                for row in reader:
                    if len(row) >= 2:
                        processed.append((row[0], row[1]))
            logger.info(f"已從日誌檔案讀取 {len(processed)} 組已處理的關鍵字")
        except Exception as e:
            logger.error(f"讀取日誌檔案時發生錯誤: {str(e)}")
    return processed

def log_processed_keyword(keyword_pair: List[str], count: int, status: str):
    """記錄已處理的關鍵字組合到日誌檔案"""
    try:
        file_exists = LOGS_FILE.exists()
        with open(LOGS_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["keyword1", "keyword2", "found_count", "status", "timestamp"])
            writer.writerow([
                keyword_pair[0],
                keyword_pair[1],
                count,
                status,
                datetime.now().isoformat()
            ])
        logger.info(f"已記錄處理狀態: {keyword_pair[0]} + {keyword_pair[1]} => {status}")
    except Exception as e:
        logger.error(f"記錄處理狀態時發生錯誤: {str(e)}")

def log_page_status(keyword: str, page_num: int, count: int, status: str):
    """記錄頁面爬取狀態"""
    try:
        file_exists = PAGE_LOGS_FILE.exists()
        
        with open(PAGE_LOGS_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["keyword", "page_number", "found_count", "status", "timestamp"])
            
            writer.writerow([
                keyword,
                page_num,
                count,
                status,
                datetime.now().isoformat()
            ])
        
        logger.info(f"已記錄頁面狀態: {keyword} 第 {page_num} 頁 => {status}")
    except Exception as e:
        logger.error(f"記錄頁面狀態時發生錯誤: {str(e)}")

def get_processed_pages(keyword: str) -> List[int]:
    """獲取已處理的頁碼"""
    processed_pages = []
    
    if PAGE_LOGS_FILE.exists():
        try:
            with open(PAGE_LOGS_FILE, "r", newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                next(reader, None)  # 跳過標題行
                
                for row in reader:
                    if len(row) >= 4 and row[0] == keyword and row[3] == "success":
                        processed_pages.append(int(row[1]))
            
            logger.info(f"已從日誌讀取 {keyword} 的已處理頁面: {processed_pages}")
        except Exception as e:
            logger.error(f"讀取已處理頁面記錄時發生錯誤: {str(e)}")
    
    return processed_pages

def main():
    """主函數"""
    # 載入關鍵字組合
    keyword_pairs = load_keywords()
    if not keyword_pairs:
        logger.error("未找到有效的關鍵字組合，程式結束")
        return
    
    # 獲取已處理的關鍵字
    processed_keywords = get_processed_keywords()
    processed_set = set(tuple(kw) for kw in processed_keywords)
    
    print(f"總共載入 {len(keyword_pairs)} 組關鍵字，已處理 {len(processed_set)} 組")
    print(f"剩餘 {len(keyword_pairs) - len(processed_set)} 組待處理")
    
    # 初始化爬蟲
    scraper = NikkeiScraper()
    
    try:
        total_keywords = len(keyword_pairs)
        
        # 遍歷每組關鍵字
        for idx, keyword_pair in enumerate(keyword_pairs):
            # 如果已處理過此關鍵字組合，跳過
            if tuple(keyword_pair) in processed_set:
                logger.info(f"跳過已處理的關鍵字組合 ({idx+1}/{total_keywords}): {keyword_pair[0]} + {keyword_pair[1]}")
                continue
            
            print(f"\n開始處理第 {idx+1}/{total_keywords} 組關鍵字: {keyword_pair[0]} + {keyword_pair[1]}")
            
            try:
                # 如果不是第一組關鍵字，增加較長的延遲時間
                if idx > 0:
                    print(f"\n切換到新關鍵字，進行較長時間延遲...")
                    scraper._random_delay(delay_type='keyword')
                
                # 組合關鍵字
                search_query = f"{keyword_pair[0]} {keyword_pair[1]}"
                logger.info(f"處理關鍵字組合: {search_query}")
                
                # 進行搜索
                scraper.search_news(search_query)

                # 使用 URL 參數翻頁獲取更多結果
                max_pages = SITE_CONFIG.get("max_pages", 5)  # 設定最大頁數
                news_list = scraper.paginate_results(search_query, max_pages=max_pages)

                if not news_list:
                    logger.warning(f"未找到搜索結果: {search_query}")
                    log_processed_keyword(keyword_pair, 0, "no_results")
                    continue
                
                # 提取文章詳情
                detailed_news = []
                total_articles = len(news_list)
                
                print(f"\n找到 {total_articles} 篇相關新聞，開始獲取詳細內容")
                
                for i, news in enumerate(news_list):
                    try:
                        if "url" in news and news["url"]:
                            article = scraper.get_article_detail(news["url"], i+1, total_articles)
                            if article:
                                # 合併搜尋結果與文章詳情
                                article["search_keywords"] = keyword_pair
                                detailed_news.append(article)
                                
                                # 每處理一定數量文章就保存一次結果
                                if len(detailed_news) % 3 == 0:  # 每3篇保存一次
                                    save_results(keyword_pair, detailed_news)
                                    logger.info(f"已處理 {len(detailed_news)}/{total_articles} 篇文章")
                    except Exception as e:
                        logger.warning(f"獲取文章詳情時發生錯誤: {news.get('url', '')}, {str(e)}")
                        continue
                
                # 保存最終結果
                if detailed_news:
                    save_results(keyword_pair, detailed_news)
                
                # 記錄已處理的關鍵字
                log_processed_keyword(keyword_pair, len(detailed_news), "success")
                
                print(f"\n成功完成關鍵字組合: {keyword_pair[0]} + {keyword_pair[1]}，找到 {len(detailed_news)} 篇文章")
                
            except Exception as e:
                logger.error(f"處理關鍵字組合時發生錯誤: {keyword_pair}, {str(e)}")
                log_processed_keyword(keyword_pair, 0, "failed")
                print(f"\n處理關鍵字組合時發生錯誤: {keyword_pair}")
    
    except KeyboardInterrupt:
        print("\n\n程序被使用者中斷，將保存已完成的工作")
        logger.warning("程序被使用者中斷")
    except Exception as e:
        logger.error(f"執行爬蟲時發生錯誤: {str(e)}")
    finally:
        scraper.close()
        logger.info("爬蟲程式已結束")
        print("\n爬蟲程式已結束")

if __name__ == "__main__":
    # 檢查並創建 storage.json 如果它不存在
    if not os.path.exists("storage.json"):
        empty_storage = {
            "cookies": [],
            "origins": []
        }
        with open("storage.json", "w") as f:
            json.dump(empty_storage, f)
        print("已創建空的 storage.json 檔案")
        
    main()