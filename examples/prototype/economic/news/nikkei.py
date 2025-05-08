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
import threading  # 添加 threading 模組
from pathlib import Path
from urllib.parse import quote, urlencode
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Union

# 確保能找到相關模組
current_dir = Path(__file__).parent
sys.path.append(str(current_dir.parent.parent.parent))  # 添加專案根目錄

from examples.prototype.economic.config.nikkei_config import SITE_CONFIG, SELECTORS
from playwright_base import PlaywrightBase, setup_logger
from playwright_base.anti_detection import HumanLikeBehavior
from extractors.handlers.news import NewsListExtractor, NewsContentExtractor

# 設置日誌
logger = setup_logger(name=__name__)

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
        
        # 從 SITE_CONFIG 中提取瀏覽器參數
        browser_config = SITE_CONFIG.get("browser", {})
        headless = browser_config.get("headless", False)
        browser_type = browser_config.get("browser_type", "chromium")
        
        # 提取 launch_options 中的參數
        launch_args = browser_config.get("launch_options", {}).get("args", [])
        
        # 初始化 PlaywrightBase
        super().__init__(
            headless=headless,
            browser_type=browser_type,
            args=launch_args
        )
        
        # 設定網站特有參數
        self.site_config = SITE_CONFIG
        self.selectors = SELECTORS
        
        # 初始化輔助元件
        self.human_like = HumanLikeBehavior()
        self.list_extractor = NewsListExtractor()
        self.content_extractor = NewsContentExtractor()
        
        # 存儲定時器引用，便於清理
        self._timers = []
        
        # 啟動瀏覽器 - 這是關鍵步驟
        logger.info("正在啟動瀏覽器...")
        self.start()
        
        # 設定 context 選項
        if self._context and browser_config.get("context_options", {}).get("viewport"):
            viewport = browser_config.get("context_options", {}).get("viewport")
            self.page.set_viewport_size(viewport)
            logger.info(f"已設定視窗大小: {viewport['width']}x{viewport['height']}")
        
        # 啟用隱身模式
        self.enable_stealth_mode()
        
        # 設置初始 Cookie
        self._setup_initial_cookies()
        
        # 註冊頁面事件處理器，監控頁面創建
        self._register_page_event_handlers()
        
        logger.info("Nikkei Asia 爬蟲已初始化完成")
        
    def _setup_initial_cookies(self):
        """設置初始化 Cookie"""
        try:
            if not self._context:
                logger.error("瀏覽器上下文未初始化，無法設置 Cookie")
                return
                
            cookies = [
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
            ]
            
            self._context.add_cookies(cookies)
            logger.info(f"已設置初始 Cookie: {len(cookies)} 筆")
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
        # 設定延遲參數
        _min_delay, _max_delay = 2.0, 5.0  # 預設值
        
        if delay_type == 'page':
            _min_delay, _max_delay = 4.0, 8.0
        elif delay_type == 'keyword':
            _min_delay, _max_delay = 8.0, 15.0
        
        # 如果有傳入的值，則覆蓋預設值
        if min_delay is not None:
            _min_delay = min_delay
        if max_delay is not None:
            _max_delay = max_delay
        
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
            
    def _check_for_paywall_or_popup(self) -> bool:
        """檢查頁面是否包含付費牆或彈窗"""
        try:
            # 檢查付費牆和彈窗
            paywall_selectors = [
                self.selectors.get("paywall", {}).get("paywall", ""),
                self.selectors.get("paywall", {}).get("login_button", ""),
                self.selectors.get("paywall", {}).get("cookie_banner", ""),
                self.selectors.get("paywall", {}).get("cookie_accept", ""),
                self.selectors.get("paywall", {}).get("subscription_banner", ""),
                self.selectors.get("paywall", {}).get("close_button", ""),
            ]
            
            for selector in paywall_selectors:
                if selector and self.page.query_selector(selector):
                    logger.warning(f"檢測到付費牆或彈窗元素: {selector}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"檢查付費牆或彈窗時發生錯誤: {str(e)}")
            return False
            
    def _handle_paywall_or_popup(self) -> bool:
        """處理付費牆或彈窗"""
        try:
            selectors = self.selectors.get("paywall", {})
            
            # 處理 Cookie 彈窗
            if selectors.get("cookie_accept") and self.page.query_selector(selectors["cookie_accept"]):
                logger.info(f"點擊 Cookie 接受按鈕")
                self.page.click(selectors["cookie_accept"])
                time.sleep(1)
                return True
                
            # 處理訂閱提示
            if selectors.get("close_button") and self.page.query_selector(selectors["close_button"]):
                logger.info(f"點擊關閉按鈕")
                self.page.click(selectors["close_button"])
                time.sleep(1)
                return True
            
            # 如果以上方法無法處理，提示用戶手動操作
            if selectors.get("paywall") and self.page.query_selector(selectors["paywall"]):
                logger.warning("檢測到付費牆，需要手動處理")
                print("\n檢測到 Nikkei 付費牆，請在瀏覽器中手動登入或關閉彈窗。")
                print("完成處理後，請按 Enter 繼續...")
                input()
                
                # 等待頁面加載
                self.wait_for_load_state("networkidle")
                time.sleep(1)
            
            return True
            
        except Exception as e:
            logger.error(f"處理付費牆或彈窗時發生錯誤: {str(e)}")
            return False

    def _ensure_single_page(self):
        """確保 context 只保留一個分頁，並將 self._page 指向唯一分頁"""
        if not self._context:
            return
        pages = self._context.pages
        # 若有多個分頁，只保留第一個，其他全部關閉
        if len(pages) > 1:
            main_page = pages[0]
            for p in pages[1:]:
                try:
                    p.close()
                except Exception:
                    pass
            self._page = main_page
        elif pages:
            self._page = pages[0]
        else:
            # 沒有分頁就新建一個
            self._page = self._context.new_page()

    def navigate(self, url: str, timeout: int = 30000) -> None:
        """重寫 navigate，導航前強制只保留一個分頁"""
        self._ensure_single_page()
        super().navigate(url, timeout=timeout)

    def search_news(self, keyword: str) -> List[Dict[str, Any]]:
        """搜尋新聞並提取結果

        Args:
            keyword: 搜索關鍵字

        Returns:
            List[Dict[str, Any]]: 新聞列表
        """
        max_retries = 3
        timeout = self.site_config.get("request", {}).get("timeout", 60000)
        retry_delay = 5
        
        # 使用 urlencode 處理查詢參數，避免編碼問題
        query_params = {"query": keyword}
        encoded_params = urlencode(query_params)
        url = f"{self.site_config['search_url']}?{encoded_params}"
        
        logger.info(f"搜尋新聞: {keyword}, URL: {url}")
        
        for attempt in range(1, max_retries + 1):
            try:
                # 使用較長的超時時間
                self.navigate(url, timeout=timeout)
                logger.info(f"成功導航到搜尋頁面 (嘗試 {attempt}/{max_retries})")
                
                # 等待網路活動結束
                self.wait_for_load_state("networkidle", timeout=timeout)
                
                # 處理可能出現的彈窗
                self.handle_popups()
                
                # 確保內容已載入
                try:
                    self.page.wait_for_selector(
                        self.selectors["search"]["list_item"],
                        timeout=15000,
                        state="visible"
                    )
                except Exception as e:
                    logger.warning(f"未能找到內容元素: {str(e)}, 繼續執行")
                
                # 執行滾動頁面操作
                try:
                    self.human_like.scroll_page(self.page, **self.site_config["scroll"])
                except Exception as e:
                    logger.warning(f"滾動頁面時發生錯誤: {str(e)}, 繼續執行")
                
                # 提取新聞列表
                results = self.list_extractor.extract_news_list(
                    self.page,
                    self.selectors["search"]["list_item"],
                    lambda el: self.list_extractor.extract_news_item(
                        el, self.selectors["search"], self.site_config["base_url"]
                    )
                )
                logger.info(f"成功找到 {len(results)} 篇新聞")
                return results
                
            except Exception as e:
                logger.error(f"搜尋過程中發生錯誤 (嘗試 {attempt}/{max_retries}): {str(e)}")
                if attempt < max_retries:
                    logger.info(f"等待 {retry_delay} 秒後重試...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # 指數退避策略
                else:
                    logger.error(f"搜尋失敗，已達最大重試次數: {max_retries}")
                    return []

    def paginate_results(self, keyword: str) -> List[Dict[str, Any]]:
        """按頁面獲取搜索結果

        Args:
            keyword: 搜索關鍵字

        Returns:
            List[Dict[str, Any]]: 所有頁面的新聞列表
        """
        all_news: List[Dict[str, Any]] = []
        max_pages = self.site_config["pagination"].get("max_pages", 5)
        timeout = self.site_config.get("request", {}).get("timeout", 60000)
        retry_attempts = 2
        
        logger.info(f"開始獲取 {keyword} 的翻頁結果，計劃獲取 {max_pages} 頁")
        
        for page in range(1, max_pages + 1):
            try:
                # 使用 urlencode 處理查詢參數，避免編碼問題
                query_params = {"query": keyword, "page": str(page)}
                encoded_params = urlencode(query_params)
                url = f"{self.site_config['search_url']}?{encoded_params}"
                
                logger.info(f"獲取第 {page}/{max_pages} 頁: {url}")
                
                for attempt in range(1, retry_attempts + 1):
                    try:
                        # 檢查並清理多餘頁面，防止積累過多頁面
                        self.manage_pages()
                        
                        # 導航到頁面
                        self.navigate(url, timeout=timeout)
                        logger.info(f"成功導航到第 {page} 頁 (嘗試 {attempt}/{retry_attempts})")
                        
                        # 等待網路活動結束
                        self.wait_for_load_state("networkidle", timeout=timeout)
                        
                        # 處理彈窗
                        self.handle_popups()
                        
                        # 等待內容載入
                        try:
                            self.page.wait_for_selector(
                                self.selectors["search"]["list_item"],
                                timeout=15000,
                                state="visible"
                            )
                        except Exception as e:
                            logger.warning(f"第 {page} 頁未找到內容元素: {str(e)}，繼續執行")
                        
                        # 滾動頁面
                        try:
                            self.human_like.scroll_page(self.page, **self.site_config["scroll"])
                        except Exception as e:
                            logger.warning(f"第 {page} 頁滾動失敗: {str(e)}，繼續執行")
                        
                        # 提取數據
                        news = self.list_extractor.extract_news_list(
                            self.page,
                            self.selectors["search"]["list_item"],
                            lambda el: self.list_extractor.extract_news_item(
                                el, self.selectors["search"], self.site_config["base_url"]
                            )
                        )
                        
                        if not news:
                            logger.info(f"第 {page} 頁未找到新聞，可能已到達最後一頁")
                            return all_news
                        
                        logger.info(f"第 {page} 頁成功提取 {len(news)} 篇新聞")
                        all_news.extend(news)
                        break  # 成功獲取，跳出重試循環
                        
                    except Exception as e:
                        logger.error(f"獲取第 {page} 頁時發生錯誤 (嘗試 {attempt}/{retry_attempts}): {str(e)}")
                        if attempt < retry_attempts:
                            retry_delay = 5 * attempt  # 逐步增加延遲
                            logger.info(f"將在 {retry_delay} 秒後重試...")
                            time.sleep(retry_delay)
                        else:
                            logger.error(f"第 {page} 頁獲取失敗，跳至下一頁")
                            break
            
            except Exception as e:
                logger.error(f"處理第 {page} 頁時發生未預期的錯誤: {str(e)}")
                continue
        
        logger.info(f"翻頁完成，共獲取 {len(all_news)} 篇新聞")
        return all_news

    def get_article_detail(self, url: str) -> Dict[str, Any]:
        """獲取新聞文章詳情

        Args:
            url: 新聞文章 URL

        Returns:
            Dict[str, Any]: 文章詳細內容
        """
        max_retries = 3
        retry_delay = 4
        timeout = self.site_config.get("request", {}).get("timeout", 60000)
        
        logger.info(f"開始獲取文章詳情: {url}")
        
        for attempt in range(1, max_retries + 1):
            try:
                # 導航到文章頁面
                self.navigate(url, timeout=timeout)
                logger.info(f"成功導航到文章頁面 (嘗試 {attempt}/{max_retries})")
                
                # 等待網路活動結束
                self.wait_for_load_state("networkidle", timeout=timeout)
                
                # 處理彈窗，包括付費牆、cookie提示等
                self.handle_popups()
                
                # 確保文章內容已載入
                try:
                    self.page.wait_for_selector(
                        self.selectors["article"]["title"],
                        timeout=15000,
                        state="visible"
                    )
                except Exception as e:
                    logger.warning(f"未能找到文章標題元素: {str(e)}，繼續執行")
                
                # 模擬人類閱讀行為，滾動頁面
                try:
                    self.human_like.scroll_page(self.page, **self.site_config["scroll"])
                except Exception as e:
                    logger.warning(f"滾動文章頁面時發生錯誤: {str(e)}，繼續執行")
                
                # 提取文章詳情
                article = self.content_extractor.extract_article_content(
                    self.page, 
                    self.selectors["article"], 
                    self.site_config["base_url"]
                )
                
                # 添加元資料
                article["url"] = url
                article["retrieved_at"] = datetime.now().isoformat()
                
                # 驗證內容是否提取成功
                if not article.get("title") or not article.get("content"):
                    raise ValueError("文章標題或內容提取失敗")
                
                logger.info(f"成功獲取文章詳情: {article.get('title', '')[:30]}...")
                return article
                
            except Exception as e:
                logger.error(f"獲取文章詳情時發生錯誤 (嘗試 {attempt}/{max_retries}): {str(e)}")
                if attempt < max_retries:
                    retry_delay_time = retry_delay * attempt
                    logger.info(f"將在 {retry_delay_time} 秒後重試...")
                    time.sleep(retry_delay_time)
                else:
                    logger.error(f"獲取文章詳情失敗，已達最大重試次數: {max_retries}")
                    # 返回部分信息，避免完全失敗
                    return {
                        "url": url,
                        "title": "(提取失敗)",
                        "content": "",
                        "retrieved_at": datetime.now().isoformat(),
                        "error": str(e),
                        "status": "failed"
                    }

    def handle_popups(self) -> bool:
        """處理頁面彈窗、Cookie 提示和付費牆
        
        Returns:
            bool: 是否成功處理
        """
        try:
            # 先檢查是否有彈窗
            if self._check_for_paywall_or_popup():
                # 如果有彈窗，嘗試處理
                if not self._handle_paywall_or_popup():
                    # 如果內建方法失敗，嘗試使用 human_like 模組
                    return self.human_like.handle_popups(self.page, self.selectors.get("paywall", {}))
            return True
        except Exception as e:
            logger.warning(f"處理彈窗時發生錯誤: {str(e)}, 繼續執行")
            return False
            
    def close(self) -> None:
        """安全關閉爬蟲器，確保資源釋放"""
        try:
            # 保存當前 storage 狀態
            try:
                if self._context and self._context.pages:
                    # 確保至少有一個頁面開啟且不是分離狀態
                    main_page = self._context.pages[0]
                    if (main_page and main_page.url != "about:blank"):
                        try:
                            storage = self._context.storage_state()
                            with open("storage.json", "w", encoding="utf-8") as f:
                                json.dump(storage, f, ensure_ascii=False, indent=2)
                            logger.info("關閉前已保存 storage 狀態")
                        except Exception as e:
                            logger.warning(f"保存 storage 狀態時發生錯誤: {str(e)}")
                    else:
                        logger.warning("無法保存 storage：頁面可能已分離或是空白頁")
                else:
                    logger.warning("無法保存 storage：瀏覽器上下文不可用或沒有開啟頁面")
            except Exception as e:
                logger.warning(f"保存 storage 狀態時發生錯誤: {str(e)}")
            
            # 清理定時器
            for timer in self._timers:
                if timer and timer.is_alive():
                    timer.cancel()
            logger.info(f"已清理 {len(self._timers)} 個定時器")
            
            # 使用基類的關閉方法
            super().close()
            logger.info("Nikkei 爬蟲器已安全關閉")
        except Exception as e:
            logger.error(f"關閉爬蟲器時發生錯誤: {str(e)}")
            
    def close_pages(self, keep_main: bool = True) -> None:
        """關閉多餘頁面，只保留主頁面
        
        Args:
            keep_main: 是否保留主頁面
        """
        if not self._context:
            return
            
        try:
            pages = self._context.pages
            if len(pages) <= 1 and keep_main:
                return
                
            logger.info(f"發現 {len(pages)} 個頁面，開始清理...")
            
            # 遍歷所有頁面
            for i, page in enumerate(pages):
                # 如果是最後一個頁面且需要保留主頁面，則跳過
                if i == len(pages) - 1 and keep_main:
                    logger.info(f"保留主頁面: {page.url}")
                    self._page = page  # 確保主頁面被正確引用
                    continue
                    
                try:
                    url = page.url
                    page.close()
                    logger.info(f"已關閉頁面: {url}")
                except Exception as e:
                    logger.warning(f"關閉頁面時發生錯誤: {str(e)}")
                    
            logger.info("頁面清理完成")
            
        except Exception as e:
            logger.error(f"清理頁面時發生錯誤: {str(e)}")
            
    def manage_pages(self) -> None:
        """管理頁面，防止頁面無限增長
        
        此方法會檢查目前開啟的頁面數量，若超過閾值則關閉多餘頁面
        """
        if not self._context:
            return
            
        try:
            pages = self._context.pages
            max_pages = 3  # 允許最大頁面數量
            
            # 如果頁面數量超過閾值，則進行清理
            if len(pages) > max_pages:
                logger.warning(f"檢測到頁面數量({len(pages)})超過閾值({max_pages})，執行頁面清理")
                self.close_pages(keep_main=True)
            else:
                logger.debug(f"目前頁面數量({len(pages)})未超過閾值({max_pages})，無需清理")
                
        except Exception as e:
            logger.error(f"管理頁面時發生錯誤: {str(e)}")
            
    def _register_page_event_handlers(self):
        """註冊頁面事件處理器，監控頁面創建
        
        此方法會監聽頁面創建和關閉事件，以便追蹤頁面數量
        """
        if not self._context:
            return
            
        try:
            # 監聽頁面創建事件
            self._context.on("page", lambda page: logger.info(f"檢測到新頁面創建: {page.url}"))
            
            # 定期檢查並管理頁面
            def check_pages():
                pages_count = len(self._context.pages) if self._context else 0
                logger.info(f"定期檢查: 目前有 {pages_count} 個頁面開啟")
                if pages_count > 3:  # 如果超過閾值，執行清理
                    self.manage_pages()
            
            # 每隔一段時間檢查一次頁面狀態
            threading_timer = threading.Timer(30.0, check_pages)  # 30 秒檢查一次
            threading_timer.daemon = True  # 設為守護線程，不阻塞程式結束
            threading_timer.start()
            
            # 存儲定時器引用，便於清理
            self._timers.append(threading_timer)
            
            logger.info("已註冊頁面事件處理器")
            
        except Exception as e:
            logger.error(f"註冊頁面事件處理器時發生錯誤: {str(e)}")

def load_keywords():
    """從 keywords.json 檔案讀取關鍵字，若檔案不存在則返回預設關鍵字"""
    try:
        keywords_file = current_dir / "keywords.json"
        if (keywords_file.exists()):
            with open(keywords_file, "r", encoding="utf-8") as f:
                keywords = json.load(f)
            logger.info(f"已從 {keywords_file} 載入 {len(keywords)} 組關鍵字")
            return keywords
        else:
            # 預設關鍵字
            default_keywords = ["economy japan", "trade asia", "market trend"]
            logger.info(f"未找到關鍵字檔案，使用預設關鍵字: {default_keywords}")
            return default_keywords
    except Exception as e:
        logger.error(f"讀取關鍵字檔案時發生錯誤: {str(e)}")
        return ["economy", "trade", "market"]  # 簡單備用關鍵字

# main 流程只需組合上述方法

def save_results(filename: str, data: List[Dict[str, Any]]) -> None:
    """儲存爬取結果至JSON檔案

    Args:
        filename: 檔案名稱
        data: 要儲存的資料
    """
    try:
        # 確保目錄存在
        save_dir = Path("data") / "json"
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # 儲存至檔案
        file_path = save_dir / filename
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        logger.info(f"已儲存資料至: {file_path}")
    except Exception as e:
        logger.error(f"儲存資料時發生錯誤: {e}")

def main() -> None:
    """主程序入口點，處理整個爬取流程 - 每次只執行 1 組關鍵字"""
    scraper = None
    try:
        # 初始化爬蟲器
        logger.info("初始化 Nikkei 爬蟲器...")
        scraper = NikkeiScraper()
        
        # 載入關鍵字
        keywords = load_keywords()
        logger.info(f"載入關鍵字完成，共 {len(keywords)} 個")
        
        # 儲存已處理關鍵字的檔案路徑
        processed_file = Path("data") / "processed_keywords.json"
        
        # 讀取已處理的關鍵字
        processed_keywords = []
        if processed_file.exists():
            try:
                with open(processed_file, "r", encoding="utf-8") as f:
                    processed_keywords = json.load(f)
                logger.info(f"已從 {processed_file} 載入 {len(processed_keywords)} 個已處理關鍵字")
            except Exception as e:
                logger.error(f"讀取已處理關鍵字檔案時發生錯誤: {str(e)}")
        
        # 過濾出未處理的關鍵字
        remaining_keywords = [kw for kw in keywords if kw not in processed_keywords]
        logger.info(f"剩餘 {len(remaining_keywords)} 個未處理的關鍵字")
        
        # 如果沒有剩餘關鍵字，結束程式
        if not remaining_keywords:
            logger.info("所有關鍵字都已處理完畢，程式結束")
            return
        
        # 只處理第一個未處理的關鍵字
        current_keyword = remaining_keywords[0]
        logger.info(f"本次將處理關鍵字: {current_keyword}")
        
        # 儲存結果的容器
        all_results = []
        
        try:
            # 確保清理多餘頁面
            scraper.close_pages(keep_main=True)
            logger.info("已清理多餘頁面，開始新的關鍵字處理")
            
            # 使用 paginate_results 獲取所有頁面的新聞
            logger.info(f"開始處理關鍵字: {current_keyword}")
            news_list = scraper.paginate_results(current_keyword)
            
            # 清理頁面
            scraper.manage_pages()
            
            if not news_list:
                logger.warning(f"關鍵字 '{current_keyword}' 未找到結果")
                # 即使沒有結果也標記為已處理
                processed_keywords.append(current_keyword)
                
                # 保存已處理關鍵字
                processed_file.parent.mkdir(parents=True, exist_ok=True)
                with open(processed_file, "w", encoding="utf-8") as f:
                    json.dump(processed_keywords, f, ensure_ascii=False, indent=2)
                logger.info(f"已更新已處理關鍵字列表: {processed_file}")
                return
            
            logger.info(f"關鍵字 '{current_keyword}' 找到 {len(news_list)} 篇新聞")
            
            # 處理每篇文章 (限制處理數量避免過載)
            max_articles = min(len(news_list), 20)  # 每個關鍵字最多處理 20 篇文章
            filtered_news = news_list[:max_articles]
            
            logger.info(f"將處理前 {max_articles}/{len(news_list)} 篇文章")
            
            for i, news in enumerate(filtered_news):
                try:
                    # 每處理5篇文章清理一次頁面
                    if i > 0 and i % 5 == 0:
                        scraper.manage_pages()
                        logger.info(f"處理 {i} 篇文章後清理頁面，防止頁面堆積")
                        
                    # 檢查 URL 有效性
                    if "url" not in news or not news["url"]:
                        logger.warning(f"跳過缺少 URL 的文章: {news.get('title', '無標題')}")
                        continue
                    
                    # 顯示進度
                    logger.info(f"處理文章 [{i+1}/{max_articles}]: {news.get('title', '')[:30]}...")
                    
                    # 獲取文章詳情
                    detail = scraper.get_article_detail(news["url"])
                    
                    if detail:
                        # 合併文章基本資訊與詳情
                        full_article = {**news, **detail}
                        full_article["keyword"] = current_keyword  # 添加關鍵字信息
                        all_results.append(full_article)
                        
                        # 每 5 篇文章儲存一次結果，避免資料丟失
                        if len(all_results) % 5 == 0:
                            save_results(f"nikkei_{current_keyword.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.json", all_results)
                
                except Exception as e:
                    logger.error(f"處理文章時發生錯誤: {str(e)}")
                    continue
            
            # 處理完當前關鍵字後保存結果
            if all_results:
                save_results(f"nikkei_{current_keyword.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.json", all_results)
                logger.info(f"已保存關鍵字 '{current_keyword}' 的 {len(all_results)} 篇文章")
            
            # 標記當前關鍵字為已處理
            processed_keywords.append(current_keyword)
            
            # 保存已處理關鍵字
            processed_file.parent.mkdir(parents=True, exist_ok=True)
            with open(processed_file, "w", encoding="utf-8") as f:
                json.dump(processed_keywords, f, ensure_ascii=False, indent=2)
            logger.info(f"已更新已處理關鍵字列表: {processed_file}")
            
            # 提示剩餘未處理關鍵字
            remaining = len(keywords) - len(processed_keywords)
            logger.info(f"已完成關鍵字 '{current_keyword}' 處理，剩餘 {remaining} 個關鍵字未處理")
            
        except Exception as e:
            logger.error(f"處理關鍵字 '{current_keyword}' 時發生錯誤: {str(e)}")
        
    except KeyboardInterrupt:
        logger.info("使用者中斷程式執行")
    except Exception as e:
        logger.error(f"執行過程中發生錯誤: {str(e)}")
    finally:
        # 確保資源被釋放
        if scraper:
            try:
                logger.info("關閉爬蟲器並釋放資源...")
                scraper.close()
                logger.info("爬蟲器已關閉")
            except Exception as e:
                logger.error(f"關閉爬蟲器時發生錯誤: {str(e)}")
        
        # 最終保存結果
        if 'all_results' in locals() and all_results:
            final_filename = f"nikkei_{current_keyword.replace(' ', '_')}_final_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            save_results(final_filename, all_results)
            logger.info(f"已最終保存 {len(all_results)} 筆結果至 {final_filename}")

if __name__ == "__main__":
    main()