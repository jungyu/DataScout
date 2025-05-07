#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Reuters 爬蟲 (關鍵字版)

此模組提供路透社(Reuters)新聞網站的爬蟲功能，可以批次搜尋關鍵字組合並支援斷點續爬。
加入反爬蟲偵測與處理，以及完善的翻頁功能。
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
    "base_url": "https://www.reuters.com",
    "search_url": "https://www.reuters.com/site-search",
    "save_path": "../data",
    "request": {
        "timeout": 60000
    },
    "page_size": 20  # 每頁顯示的新聞數
}

# 選擇器配置
SELECTORS = {
    "search": {
        "list_item": ".search-results__list-item",
        "title": ".media-story-card__heading__eqhp9",
        "date": ".media-story-card__datetime__eqhp9",
        "summary": ".media-story-card__description__eqhp9",
        "url": "a",
        "count": "//span[contains(@class,'count')]"  # 總筆數選擇器
    },
    "article": {
        "title": "h1",
        "date": "time",
        "author": ".article-header__author__2INF5",
        "content": "[data-testid='paragraph-container']",
        "image": ".article-body__image-container img"
    },
    "captcha": {
        "image_captcha": ".captcha-image",
        "audio_captcha": ".captcha-audio",
        "input": ".captcha-input",
        "submit": ".captcha-submit",
        "refresh": ".captcha-refresh"
    }
}

# 瀏覽器配置 - 增強反爬蟲能力
BROWSER_CONFIG = {
    "headless": False,  # 先設為 False 以便觀察
    "browser_type": "chromium",
    "launch_options": {
        "args": [
            "--disable-web-security", 
            "--disable-features=IsolateOrigins,site-per-process",
            "--disable-blink-features=AutomationControlled"  # 隱藏自動化特徵
        ]
    },
    "context_options": {
        "viewport": {"width": 1920, "height": 1080},
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    }
}

# 反爬蟲設定 - 增加延遲時間
ANTI_DETECTION_CONFIG = {
    "random_delay": True,
    "delay_min": 3.0,        # 增加到至少 3 秒
    "delay_max": 7.0,        # 增加到最多 7 秒
    "page_delay_min": 5.0,   # 翻頁時最小延遲
    "page_delay_max": 15.0,  # 翻頁時最大延遲
    "keyword_delay_min": 15.0,  # 切換關鍵字時最小延遲
    "keyword_delay_max": 30.0,  # 切換關鍵字時最大延遲
    "human_like": True
}

# 日誌檔案路徑
LOGS_FILE = Path(SITE_CONFIG["save_path"]) / "news_reuters_logs.csv"

# 新增頁面進度記錄檔案
PAGE_LOGS_FILE = Path(SITE_CONFIG["save_path"]) / "news_reuters_page_logs.csv"

logger = setup_logger(name=__name__)

class PageException(Exception):
    """頁面操作失敗異常"""
    pass

class ElementException(Exception):
    """元素操作失敗異常"""
    pass

class ReutersScraper(PlaywrightBase):
    """
    Reuters 爬蟲類
    繼承自 PlaywrightBase，提供路透社(Reuters)網站的爬蟲功能
    """

    def __init__(self):
        """
        初始化 Reuters 爬蟲
        """
        self.logger = logging.getLogger(__name__)
        super().__init__(
            headless=BROWSER_CONFIG.get("headless", True),
            proxy=BROWSER_CONFIG.get("proxy", None),
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

        # 啟動瀏覽器
        self.start()

        logger.info("Reuters 爬蟲已初始化")

    def _stealth_mode_setup(self):
        """設置隱身模式，掩蓋自動化特徵"""
        # 添加腳本以掩蓋自動化特徵
        if self._context:
            # 定義掩蓋自動化特徵的腳本
            stealth_js = """
            () => {
                // 覆蓋 navigator 屬性
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                
                // 覆蓋 chrome 屬性
                if (window.chrome) {
                    window.chrome.runtime = {};
                }
                
                // 創建假的 plugins 和 mimeTypes
                const makePluginsLookReal = () => {
                    const plugins = [
                        { name: 'Chrome PDF Plugin', filename: 'internal-pdf-viewer' }, 
                        { name: 'Chrome PDF Viewer', filename: 'mhjfbmdgcfjbbpaeojofohoefgiehjai' },
                        { name: 'Native Client', filename: 'internal-nacl-plugin' }
                    ];
                    
                    const mockPlugins = plugins.map(plugin => {
                        const item = { name: plugin.name, filename: plugin.filename };
                        item.description = '';
                        item.version = '';
                        item.length = 1;
                        return item;
                    });
                    
                    if (navigator.__proto__.plugins) {
                        navigator.__proto__.plugins = Object.create(navigator.__proto__.plugins);
                        Object.defineProperty(navigator.__proto__, 'plugins', {
                            get: () => mockPlugins
                        });
                    }
                };
                makePluginsLookReal();
                
                // 覆蓋自動化檢測函數
                const overrideAutomationFunctions = () => {
                    const originalFunctions = {
                        hasFocus: document.hasFocus,
                    };
                    
                    document.hasFocus = function() {
                        return true;
                    };
                };
                overrideAutomationFunctions();
                
                // 模擬用戶交互操作
                const simulateUserEvents = () => {
                    const events = ['mousemove', 'mousedown', 'mouseup', 'mouseover'];
                    events.forEach(event => {
                        const randomX = Math.floor(Math.random() * window.innerWidth);
                        const randomY = Math.floor(Math.random() * window.innerHeight);
                        const mouseEvent = new MouseEvent(event, {
                            view: window,
                            bubbles: true,
                            cancelable: true,
                            clientX: randomX,
                            clientY: randomY
                        });
                        document.dispatchEvent(mouseEvent);
                    });
                };
                setTimeout(simulateUserEvents, 1000);
            }
            """
            self._context.add_init_script(stealth_js)
            logger.info("已添加隱身模式腳本")

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

    def search_news(self, keyword: str, page: int = 1, save_page: bool = False) -> List[Dict[str, Any]]:
        """
        搜索新聞並提取結果

        Args:
            keyword: 搜索關鍵字
            page: 頁碼，默認為1
            save_page: 是否保存頁面內容，默認為False

        Returns:
            List[Dict[str, Any]]: 新聞列表，每個新聞為一個字典
        """
        try:
            # 計算 offset
            offset = (page - 1) * self.site_config.get("page_size", 20)
            url = f"{self.site_config['search_url']}/?query={quote(keyword)}&offset={offset}"
            logger.info(f"搜索新聞: {keyword}, 頁碼: {page}, offset: {offset}")

            self.navigate(url)
            self._random_delay(1, 2)
            
            self.wait_for_load_state("networkidle", timeout=self.site_config.get("request", {}).get("timeout", 60000))

            # 檢查是否需要處理驗證碼
            if self._check_for_captcha():
                if not self._handle_captcha():
                    logger.error("驗證碼處理失敗")
                    raise CaptchaException("驗證碼處理失敗")

            # 嘗試等待搜索結果加載完成
            try:
                self.page.wait_for_selector(self.selectors["search"]["list_item"], timeout=10000)
            except Exception:
                logger.warning("未找到搜索結果元素，可能是搜索結果為空或頁面結構變化")
                
                # 檢查是否被反爬蟲阻擋
                if "I am not a robot" in self.page.content() or "驗證" in self.page.content():
                    logger.warning("檢測到反爬蟲攔截，嘗試處理...")
                    if not self._handle_captcha():
                        logger.error("處理反爬蟲攔截失敗")
                        raise CaptchaException("處理反爬蟲攔截失敗")
                    
                    # 重新等待結果
                    self._random_delay(2, 4)
                    self.page.wait_for_selector(self.selectors["search"]["list_item"], timeout=10000)

            # 模擬人類滾動行為
            self._human_like_scroll()

            # 獲取總結果數
            total_count = self._get_total_count()
            if total_count > 0:
                logger.info(f"搜索結果總數: {total_count}")

            if save_page:
                self._save_page_content(keyword, page)

            return self._extract_news_list()

        except CaptchaException as e:
            logger.error(f"驗證碼處理錯誤: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"搜尋新聞時發生錯誤: {str(e)}")
            raise PageException(f"搜尋新聞失敗: {str(e)}")

    def _check_for_captcha(self) -> bool:
        """檢查頁面是否包含驗證碼"""
        try:
            # 檢查常見的驗證碼元素
            captcha_selectors = [
                ".captcha", 
                "#captcha", 
                "[id*='captcha']", 
                "[class*='captcha']",
                "iframe[src*='captcha']",
                "iframe[src*='recaptcha']",
                "iframe[title*='recaptcha']",
                "iframe[title*='security check']"
            ]
            
            for selector in captcha_selectors:
                if self.page.query_selector(selector):
                    logger.warning(f"檢測到驗證碼元素: {selector}")
                    return True
                    
            # 檢查頁面內容是否包含驗證碼相關文字
            content = self.page.content().lower()
            captcha_keywords = ["captcha", "verify", "human", "robot", "security check", "驗證", "人機驗證"]
            
            for keyword in captcha_keywords:
                if keyword.lower() in content:
                    logger.warning(f"檢測到驗證碼關鍵詞: {keyword}")
                    return True
                    
            return False
            
        except Exception as e:
            logger.error(f"檢查驗證碼時發生錯誤: {str(e)}")
            return False

    def _handle_captcha(self) -> bool:
        """
        處理驗證碼
        
        Returns:
            bool: 是否成功處理
        """
        try:
            # 在此處實現驗證碼處理邏輯
            # 由於真實環境可能需要人工介入，我們會在控制台提示使用者
            logger.warning("檢測到驗證碼，請在瀏覽器中手動解決")
            
            # 這裡給予足夠的時間讓使用者手動處理
            input("完成驗證後，請按 Enter 繼續...")
            
            # 等待頁面加載
            self.wait_for_load_state("networkidle")
            self._random_delay(1, 2)
            
            return True
        except Exception as e:
            logger.error(f"處理驗證碼時發生錯誤: {str(e)}")
            return False

    def _get_total_count(self) -> int:
        """
        獲取搜索結果的總數量
        
        Returns:
            int: 搜索結果總數
        """
        try:
            count_selector = self.selectors["search"]["count"]
            count_element = self.page.locator(count_selector)
            if count_element.count() > 0:
                count_text = count_element.first.text_content().strip()
                # 處理文本，提取數字
                import re
                numbers = re.findall(r'\d+', count_text)
                if numbers:
                    return int(numbers[0])
            return 0
        except Exception as e:
            logger.warning(f"獲取搜索結果總數時發生錯誤: {str(e)}")
            return 0

    def get_all_pages(self, keyword: str, keyword_pair: List[str], max_pages: int = 5) -> List[Dict[str, Any]]:
        """
        獲取所有分頁的新聞數據
        
        Args:
            keyword: 搜索關鍵字
            keyword_pair: 原始關鍵字對 (用於記錄)
            max_pages: 最大頁數限制，默認為5
            
        Returns:
            List[Dict[str, Any]]: 合併所有頁的新聞列表
        """
        all_news = []
        
        # 先獲取第一頁
        logger.info(f"開始獲取第 1 頁數據: {keyword}")
        first_page_news = self.search_news(keyword, page=1)
        all_news.extend(first_page_news)
        
        # 記錄第一頁狀態
        log_page_status(keyword_pair, 1, len(first_page_news), "success")
        
        # 獲取總結果數量
        total_count = self._get_total_count()
        if total_count == 0:
            # 如果未獲取到總數，則使用第一頁新聞數來估算
            total_count = len(first_page_news) * max_pages
            logger.info(f"未找到總結果數，使用估算值: {total_count}")
        
        # 計算總頁數
        page_size = self.site_config.get("page_size", 20)
        total_pages = min(max_pages, (total_count + page_size - 1) // page_size)
        logger.info(f"預計總頁數: {total_pages}")
        
        # 告知使用者翻頁即將開始 (提供互動機會)
        if total_pages > 1:
            print(f"\n即將開始獲取後續頁面，總計 {total_pages} 頁。")
            print("若需要手動處理驗證碼或暫停，請按 Ctrl+C")
            try:
                time.sleep(3)  # 給使用者閱讀提示的時間
            except KeyboardInterrupt:
                input("\n程式暫停。完成驗證或準備繼續後，請按 Enter...")
        
        # 獲取剩餘頁數
        for page in range(2, total_pages + 1):
            try:
                logger.info(f"開始獲取第 {page} 頁數據")
                
                # 使用頁面級別的延遲
                print(f"\n準備獲取第 {page}/{total_pages} 頁，即將進行較長時間延遲...")
                self._random_delay(delay_type='page')  # 頁面間延遲時間更長
                
                page_news = self.search_news(keyword, page=page)
                all_news.extend(page_news)
                
                # 記錄此頁狀態
                log_page_status(keyword_pair, page, len(page_news), "success")
                
                # 如果返回數量少於預期，可能已到達末頁
                if len(page_news) < page_size / 2:
                    logger.info(f"第 {page} 頁數據少於預期，可能已到達末頁")
                    break
                    
            except Exception as e:
                logger.error(f"獲取第 {page} 頁數據時發生錯誤: {str(e)}")
                # 記錄此頁失敗狀態
                log_page_status(keyword_pair, page, 0, "failed")
                break
        
        logger.info(f"成功獲取 {len(all_news)} 條新聞數據")
        return all_news

    def _save_page_content(self, keyword: str, page: int):
        """保存頁面內容和截圖"""
        try:
            base_name = f"reuters_search_{keyword}_{page}"
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
            news_elements = self.page.locator(selectors.get("list_item", "")).all()
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
                    news["title"] = element.locator(selectors["title"]).text_content().strip()
                except Exception:
                    news["title"] = ""

            # 提取日期
            if "date" in selectors:
                try:
                    news["date"] = element.locator(selectors["date"]).text_content().strip()
                except Exception:
                    news["date"] = ""

            # 提取摘要
            if "summary" in selectors:
                try:
                    news["summary"] = element.locator(selectors["summary"]).text_content().strip()
                except Exception:
                    news["summary"] = ""

            # 提取 URL
            if "url" in selectors:
                try:
                    url = element.locator(selectors["url"]).get_attribute("href")
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
            
            # 檢查是否需要處理驗證碼
            if self._check_for_captcha():
                print(f"\n檢測到第 {article_count} 篇文章需要驗證")
                if not self._handle_captcha():
                    logger.error("驗證碼處理失敗")
                    raise CaptchaException("驗證碼處理失敗")

            # 模擬人類閱讀行為
            self._human_like_scroll()

            article = {}
            selectors = self.selectors.get("article", {})

            # 提取標題
            if "title" in selectors:
                try:
                    article["title"] = self.page.locator(selectors["title"]).text_content().strip()
                except Exception:
                    article["title"] = ""

            # 提取日期
            if "date" in selectors:
                try:
                    article["date"] = self.page.locator(selectors["date"]).text_content().strip()
                except Exception:
                    article["date"] = ""

            # 提取作者
            if "author" in selectors:
                try:
                    article["author"] = self.page.locator(selectors["author"]).text_content().strip()
                except Exception:
                    article["author"] = ""

            # 提取內容
            if "content" in selectors:
                try:
                    paragraphs = self.page.locator(selectors["content"]).all()
                    article["content"] = "\n\n".join([p.text_content().strip() for p in paragraphs])
                except Exception:
                    article["content"] = ""

            # 提取圖片
            if "image" in selectors:
                try:
                    article["image_url"] = self.page.locator(selectors["image"]).get_attribute("src")
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
        logger.info("Reuters 爬蟲已關閉")

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
        file_name = f"news_reuters_{keyword_str}.json"
        file_path = save_dir / file_name
        
        # 如果檔案已存在，載入並合併資料
        existing_data = []
        if (file_path.exists()):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)
                logger.info(f"已載入現有資料: {file_path} ({len(existing_data)} 條)")
            except Exception as e:
                logger.warning(f"載入現有資料時發生錯誤: {str(e)}")
        
        # 合併並去重
        urls = {item["url"] for item in existing_data}
        for item in news_list:
            if item["url"] not in urls:
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

def log_page_status(keyword_pair: List[str], page: int, count: int, status: str):
    """
    記錄頁面爬取狀態
    
    Args:
        keyword_pair: 關鍵字組合
        page: 頁碼
        count: 找到的新聞數量
        status: 處理狀態 ('success' 或 'failed')
    """
    try:
        file_exists = PAGE_LOGS_FILE.exists()
        with open(PAGE_LOGS_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["keyword1", "keyword2", "page", "found_count", "status", "timestamp"])
            writer.writerow([
                keyword_pair[0],
                keyword_pair[1],
                page,
                count,
                status,
                datetime.now().isoformat()
            ])
        logger.info(f"已記錄頁面狀態: {keyword_pair[0]} + {keyword_pair[1]}, 第 {page} 頁 => {status}")
    except Exception as e:
        logger.error(f"記錄頁面狀態時發生錯誤: {str(e)}")

def get_processed_pages() -> Dict[Tuple[str, str], List[int]]:
    """
    從頁面日誌檔案讀取已處理的頁面
    
    Returns:
        Dict[Tuple[str, str], List[int]]: 以關鍵字組合為鍵，已處理頁碼列表為值的字典
    """
    processed = {}
    if PAGE_LOGS_FILE.exists():
        try:
            with open(PAGE_LOGS_FILE, "r", newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                next(reader, None)  # 跳過標題行
                for row in reader:
                    if len(row) >= 4:
                        keyword_pair = (row[0], row[1])
                        page = int(row[2])
                        status = row[4]
                        if status == "success":
                            if keyword_pair not in processed:
                                processed[keyword_pair] = []
                            processed[keyword_pair].append(page)
            logger.info(f"已從頁面日誌檔案讀取 {len(processed)} 組關鍵字的頁面記錄")
        except Exception as e:
            logger.error(f"讀取頁面日誌檔案時發生錯誤: {str(e)}")
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
    
    # 獲取已處理的頁面記錄，用於斷點續爬
    processed_pages = get_processed_pages()
    
    # 初始化爬蟲
    scraper = ReutersScraper()
    
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
                
                # 使用改進後的翻頁功能搜尋新聞，傳入關鍵字對用於記錄
                news_list = scraper.get_all_pages(search_query, keyword_pair, max_pages=6)  # 最多取6頁數據
                
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
                                if len(detailed_news) % 3 == 0:  # 改為每3篇保存一次
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