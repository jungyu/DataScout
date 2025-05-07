#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Bloomberg 爬蟲 (關鍵字版)

此模組提供彭博社(Bloomberg)新聞網站的爬蟲功能，可以批次搜尋關鍵字組合並支援斷點續爬。
加入反爬蟲偵測與處理，以及處理「Load More Results」加載更多內容的功能。
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
    "base_url": "https://www.bloomberg.com",
    "search_url": "https://www.bloomberg.com/search",
    "save_path": "../data",
    "request": {
        "timeout": 60000
    },
    "load_more_count": 5  # 點擊 Load More 的最大次數
}

# 選擇器配置
SELECTORS = {
    "search": {
        "list_item": ".storyItem__aedeb3d4e7", # 新聞列表項
        "title": ".headline__3a97736d10", # 標題
        "date": ".publishedAt__dc9dff8350", # 發布日期
        "summary": ".summary__70acfc9d5f", # 摘要
        "url": ".headline__3a97736d4f a", # 連結
        "load_more": "button.button__f6b7ccfb8d.secondary__ed561f3e09", # 加載更多按鈕
        "count": ".searchStory__d4fca28c56 .count" # 總筆數選擇器
    },
    "article": {
        "title": "h1.headline__54d7328f40", # 文章標題
        "date": "time", # 文章日期
        "author": ".byline__54d7328f40", # 作者
        "content": ".body-content p, .body-content h2, .body-content h3", # 文章內容
        "image": ".article-body__image-container img" # 圖片
    },
    "captcha": {
        "recaptcha_frame": "iframe[title*='reCAPTCHA']", # reCAPTCHA 框架
        "cloudflare_challenge": "#challenge-form", # Cloudflare 驗證
        "consent_dialog": ".paywall-inline-tout" # 同意對話框
    }
}

# 改進後的瀏覽器配置
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
    },
    "persistent_context": True  # 使用持久化的瀏覽器內容
}

# 反爬蟲設定 - 增加延遲時間
ANTI_DETECTION_CONFIG = {
    "random_delay": True,
    "delay_min": 3.0,        # 增加到至少 3 秒
    "delay_max": 7.0,        # 增加到最多 7 秒
    "load_more_delay_min": 5.0,   # 加載更多時最小延遲
    "load_more_delay_max": 15.0,  # 加載更多時最大延遲
    "keyword_delay_min": 15.0,  # 切換關鍵字時最小延遲
    "keyword_delay_max": 30.0,  # 切換關鍵字時最大延遲
    "human_like": True
}

# 日誌檔案路徑
LOGS_FILE = Path(SITE_CONFIG["save_path"]) / "news_bloomberg_logs.csv"

# 新增加載進度記錄檔案
LOAD_MORE_LOGS_FILE = Path(SITE_CONFIG["save_path"]) / "news_bloomberg_load_more_logs.csv"

logger = setup_logger(name=__name__)

class PageException(Exception):
    """頁面操作失敗異常"""
    pass

class ElementException(Exception):
    """元素操作失敗異常"""
    pass

class BloombergScraper(PlaywrightBase):
    """
    Bloomberg 爬蟲類
    繼承自 PlaywrightBase，提供彭博社(Bloomberg)網站的爬蟲功能
    """

    def __init__(self):
        """
        初始化 Bloomberg 爬蟲
        """
        self.logger = logging.getLogger(__name__)
        super().__init__(
            headless=BROWSER_CONFIG.get("headless", False),
            # 移除 user_data_dir 參數
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

        logger.info("Bloomberg 爬蟲已初始化")

    def _stealth_mode_setup(self):
        """更強大的隱身模式設置，掩蓋自動化特徵"""
        if self._context:
            # 增強版的隱身模式 JavaScript
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
            logger.info("已添加增強版隱身模式腳本")

    def _setup_initial_cookies(self):
        """設置初始化 Cookie 以通過 Bloomberg 檢查"""
        try:
            # 設置一些常見的 Cookie 來模擬正常瀏覽器
            self._context.add_cookies([
                {
                    "name": "session_visited",
                    "value": "true",
                    "domain": ".bloomberg.com",
                    "path": "/",
                },
                {
                    "name": "cookie_consent",
                    "value": "accepted",
                    "domain": ".bloomberg.com",
                    "path": "/",
                },
                {
                    "name": "seen_cookie_banner",
                    "value": "true",
                    "domain": ".bloomberg.com",
                    "path": "/",
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
            delay_type: 延遲類型 (None, 'load_more', 'keyword')
        """
        if delay_type == 'load_more':
            _min_delay = min_delay if min_delay is not None else ANTI_DETECTION_CONFIG.get("load_more_delay_min", 5.0)
            _max_delay = max_delay if max_delay is not None else ANTI_DETECTION_CONFIG.get("load_more_delay_max", 15.0)
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
        """改進的搜索新聞函數"""
        try:
            url = f"{self.site_config['search_url']}?query={quote(keyword)}"
            logger.info(f"搜索新聞: {keyword}")
            
            # 先訪問主頁
            logger.info("先訪問 Bloomberg 主頁以建立 session")
            self.navigate(self.site_config['base_url'])
            self._random_delay(2, 4)
            
            # 處理彈窗或 Cookie 提示
            if self._check_for_captcha_or_popup():
                self._handle_captcha_or_popup()
            
            # 設置初始 Cookie
            self._setup_initial_cookies()
            
            # 再訪問搜尋頁面
            self.navigate(url)
            self._random_delay(2, 3)
            
            self.wait_for_load_state("networkidle", timeout=self.site_config.get("request", {}).get("timeout", 60000))
            
            # 重新檢查是否有彈窗
            if self._check_for_captcha_or_popup():
                if not self._handle_captcha_or_popup():
                    logger.error("驗證碼或彈窗處理失敗")
                    raise CaptchaException("驗證碼或彈窗處理失敗")
            
            # 檢查是否加載了錯誤頁面
            if "JavaScript and cookies" in self.page.content():
                logger.error("頁面要求啟用 JavaScript 和 Cookie")
                print("\n網站顯示 JavaScript 和 Cookie 錯誤，嘗試刷新頁面...")
                self.page.reload()
                self._random_delay(3, 5)
                
                # 再次處理彈窗
                if self._check_for_captcha_or_popup():
                    self._handle_captcha_or_popup()
            
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
            logger.error(f"驗證碼或彈窗處理錯誤: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"搜尋新聞時發生錯誤: {str(e)}")
            raise PageException(f"搜尋新聞失敗: {str(e)}")

    def _check_for_captcha_or_popup(self) -> bool:
        """檢查頁面是否包含驗證碼或彈窗"""
        try:
            # 檢查彈窗和驗證碼
            captcha_selectors = [
                self.selectors["captcha"]["recaptcha_frame"],
                self.selectors["captcha"]["cloudflare_challenge"],
                self.selectors["captcha"]["consent_dialog"],
                "iframe[src*='captcha']",
                "iframe[src*='recaptcha']",
                "#challenge-form",
                ".consent-banner",
                ".cookie-banner",
                ".cookie-consent",
                ".subscription-banner",
                ".paywall",
                "#paywall"
            ]
            
            for selector in captcha_selectors:
                if self.page.query_selector(selector):
                    logger.warning(f"檢測到驗證碼或彈窗元素: {selector}")
                    return True
                    
            # 檢查頁面內容是否包含驗證碼相關文字
            content = self.page.content().lower()
            captcha_keywords = [
                "captcha", "verify", "human", "robot", 
                "security check", "驗證", "人機驗證", 
                "subscribe", "subscription", "登入", "login", 
                "register", "sign up", "cookies", "consent"
            ]
            
            for keyword in captcha_keywords:
                if keyword.lower() in content:
                    logger.warning(f"檢測到特殊關鍵詞: {keyword}")
                    return True
                    
            return False
            
        except Exception as e:
            logger.error(f"檢查驗證碼或彈窗時發生錯誤: {str(e)}")
            return False

    def _handle_captcha_or_popup(self) -> bool:
        """改進的彈窗和 Cookie 處理函數"""
        try:
            # Bloomberg 特定的 Cookie 同意按鈕選擇器
            cookie_selectors = [
                "button[data-testid='cookie-accept-button']",
                ".cookie-notification button",
                ".cookie-banner button",
                "#consent-accept",
                ".accept-cookies",
                "[aria-label*='cookie'] button",
                "[aria-label*='Cookie'] button",
                "button:has-text('Accept')",
                "button:has-text('Accept All')",
                "button:has-text('I Accept')"
            ]
            
            for selector in cookie_selectors:
                try:
                    if self.page.query_selector(selector):
                        logger.info(f"點擊 Cookie 同意按鈕: {selector}")
                        self.page.click(selector)
                        self._random_delay(1, 3)  # 點擊後等待
                        return True
                except Exception as e:
                    logger.warning(f"點擊 Cookie 按鈕 {selector} 失敗: {str(e)}")
                    continue
                    
            # 如果自動處理失敗，提示用戶手動處理
            logger.warning("Cookie 或彈窗需要手動處理")
            print("\n請在瀏覽器中手動處理 Cookie 同意或彈窗。")
            input("完成處理後，請按 Enter 繼續...")
            
            # 等待頁面加載
            self.wait_for_load_state("networkidle")
            self._random_delay(1, 2)
            
            return True
        except Exception as e:
            logger.error(f"處理 Cookie 或彈窗時發生錯誤: {str(e)}")
            return False

    def _get_total_count(self) -> int:
        """
        獲取搜索結果的總數量
        
        Returns:
            int: 搜索結果總數
        """
        try:
            count_selector = self.selectors["search"]["count"]
            count_element = self.page.query_selector(count_selector)
            if count_element:
                count_text = count_element.text_content().strip()
                # 處理文本，提取數字
                import re
                numbers = re.findall(r'\d+', count_text)
                if numbers:
                    return int(numbers[0])
            return 0
        except Exception as e:
            logger.warning(f"獲取搜索結果總數時發生錯誤: {str(e)}")
            return 0

    def load_more_results(self, keyword_pair: List[str], max_loads: int = 5) -> List[Dict[str, Any]]:
        """
        點擊「Load More Results」按鈕加載更多結果
        
        Args:
            keyword_pair: 關鍵字組合 (用於記錄)
            max_loads: 最大加載次數，默認為5
            
        Returns:
            List[Dict[str, Any]]: 合併所有加載的新聞列表
        """
        all_news = []
        
        # 先提取初始加載的新聞
        logger.info(f"提取初始加載的新聞")
        initial_news = self._extract_news_list()
        all_news.extend(initial_news)
        
        # 記錄初始新聞狀態
        log_load_more_status(keyword_pair, 0, len(initial_news), "success")
        
        # 獲取總結果數量
        total_count = self._get_total_count()
        if total_count == 0:
            total_count = len(initial_news) * (max_loads + 1)
            logger.info(f"未找到總結果數，使用估算值: {total_count}")
        
        # 告知使用者加載更多即將開始
        if max_loads > 0:
            print(f"\n即將開始加載更多結果，計劃加載 {max_loads} 次。")
            print("若需要手動處理驗證碼或暫停，請按 Ctrl+C")
            try:
                time.sleep(3)  # 給使用者閱讀提示的時間
            except KeyboardInterrupt:
                input("\n程式暫停。完成驗證或準備繼續後，請按 Enter...")
        
        # 點擊 Load More Results 按鈕
        load_more_button = self.selectors["search"]["load_more"]
        for load_count in range(1, max_loads + 1):
            try:
                # 檢查是否有 Load More Results 按鈕
                if not self.page.query_selector(load_more_button):
                    logger.info(f"未找到「Load More Results」按鈕，可能已到達末頁")
                    break
                
                logger.info(f"點擊「Load More Results」按鈕 ({load_count}/{max_loads})")
                print(f"\n準備加載更多結果 ({load_count}/{max_loads})，即將進行較長時間延遲...")
                
                # 滾動到按鈕位置
                self.page.evaluate(f"""
                    () => {{
                        const button = document.querySelector('{load_more_button}');
                        if (button) {{
                            button.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                        }}
                    }}
                """)
                time.sleep(1)  # 等待滾動完成
                
                # 使用延遲點擊模擬人類行為
                self._random_delay(delay_type='load_more')
                
                # 點擊按鈕
                self.page.click(load_more_button)
                
                # 等待新內容加載
                self.wait_for_load_state("networkidle", timeout=20000)
                time.sleep(2)  # 確保內容完全加載
                
                # 模擬人類滾動行為
                self._human_like_scroll()
                
                # 提取新加載的新聞
                current_news = self._extract_news_list()
                
                # 記錄此次加載狀態
                log_load_more_status(keyword_pair, load_count, len(current_news), "success")
                
                # 如果沒有新增內容，可能已到達末頁
                if len(current_news) <= len(all_news):
                    logger.info(f"加載 {load_count} 次後無新增內容，可能已到達末頁")
                    break
                
                # 更新總列表（注意：需要去重，因為提取的是整個頁面的內容）
                all_news = current_news
                logger.info(f"已加載 {load_count} 次，當前總共有 {len(all_news)} 條新聞")
                
            except Exception as e:
                logger.error(f"點擊「Load More Results」按鈕時發生錯誤: {str(e)}")
                log_load_more_status(keyword_pair, load_count, 0, "failed")
                break
        
        logger.info(f"成功獲取 {len(all_news)} 條新聞數據")
        return all_news

    def _save_page_content(self, keyword: str):
        """保存頁面內容和截圖"""
        try:
            base_name = f"bloomberg_search_{keyword}"
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
        """
        從頁面提取新聞列表

        Returns:
            List[Dict[str, Any]]: 新聞列表
        """
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
            
            # 檢查是否需要處理驗證碼或彈窗
            if self._check_for_captcha_or_popup():
                print(f"\n檢測到第 {article_count} 篇文章需要處理彈窗或驗證")
                if not self._handle_captcha_or_popup():
                    logger.error("驗證碼或彈窗處理失敗")
                    raise CaptchaException("驗證碼或彈窗處理失敗")

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
            logger.error(f"驗證碼處理錯誤: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"獲取新聞詳情時發生錯誤: {url}, {str(e)}")
            raise

    def close(self):
        """
        關閉瀏覽器
        """
        super().close()
        logger.info("Bloomberg 爬蟲已關閉")

def load_keywords() -> List[List[str]]:
    """
    從 keywords.json 檔案讀取關鍵字組合
    
    Returns:
        List[List[str]]: 關鍵字組合列表
    """
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
    """
    將搜尋結果保存到 JSON 檔案
    
    Args:
        keyword_pair: 關鍵字組合
        news_list: 新聞列表
    """
    try:
        save_dir = Path(SITE_CONFIG["save_path"])
        save_dir.mkdir(parents=True, exist_ok=True)
        
        keyword_str = "_".join(keyword_pair).replace(" ", "_").lower()
        file_name = f"news_bloomberg_{keyword_str}.json"
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
    """
    從日誌檔案讀取已處理的關鍵字組合
    
    Returns:
        List[Tuple[str, str]]: 已處理的關鍵字組合列表
    """
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
    """
    記錄已處理的關鍵字組合到日誌檔案
    
    Args:
        keyword_pair: 關鍵字組合
        count: 找到的新聞數量
        status: 處理狀態 ('success' 或 'failed')
    """
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

def log_load_more_status(keyword_pair: List[str], load_count: int, count: int, status: str):
    """
    記錄加載更多的狀態
    
    Args:
        keyword_pair: 關鍵字組合
        load_count: 加載次數 (0表示初始加載)
        count: 找到的新聞數量
        status: 處理狀態 ('success' 或 'failed')
    """
    try:
        file_exists = LOAD_MORE_LOGS_FILE.exists()
        with open(LOAD_MORE_LOGS_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["keyword1", "keyword2", "load_count", "found_count", "status", "timestamp"])
            writer.writerow([
                keyword_pair[0],
                keyword_pair[1],
                load_count,
                count,
                status,
                datetime.now().isoformat()
            ])
        logger.info(f"已記錄加載狀態: {keyword_pair[0]} + {keyword_pair[1]}, 加載次數 {load_count} => {status}")
    except Exception as e:
        logger.error(f"記錄加載狀態時發生錯誤: {str(e)}")

def get_processed_loads() -> Dict[Tuple[str, str], List[int]]:
    """
    從加載更多日誌檔案讀取已處理的加載次數
    
    Returns:
        Dict[Tuple[str, str], List[int]]: 以關鍵字組合為鍵，已處理加載次數列表為值的字典
    """
    processed = {}
    if LOAD_MORE_LOGS_FILE.exists():
        try:
            with open(LOAD_MORE_LOGS_FILE, "r", newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                next(reader, None)  # 跳過標題行
                for row in reader:
                    if len(row) >= 4:
                        keyword_pair = (row[0], row[1])
                        load_count = int(row[2])
                        status = row[4]
                        if status == "success":
                            if keyword_pair not in processed:
                                processed[keyword_pair] = []
                            processed[keyword_pair].append(load_count)
            logger.info(f"已從加載更多日誌檔案讀取 {len(processed)} 組關鍵字的加載記錄")
        except Exception as e:
            logger.error(f"讀取加載更多日誌檔案時發生錯誤: {str(e)}")
    return processed

def main():
    """
    主函數
    """
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
    
    # 獲取已處理的加載記錄，用於斷點續爬
    processed_loads = get_processed_loads()
    
    # 初始化爬蟲
    scraper = BloombergScraper()
    
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
                
                # 使用 "Load More Results" 功能加載更多結果
                max_loads = SITE_CONFIG.get("load_more_count", 5)
                news_list = scraper.load_more_results(keyword_pair, max_loads=max_loads)
                
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
                
                # 記錄已處理的關鍵字 - 完成後立即記錄
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
    main()