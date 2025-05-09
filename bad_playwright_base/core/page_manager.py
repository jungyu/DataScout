#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
頁面管理模組

此模組提供序列化頁面處理功能，用於爬蟲的列表頁和詳情頁的處理。
設計理念：爬蟲應該按照以下順序處理頁面：
1. 搜索/入口頁面
2. 序列化處理列表頁（依次翻頁）
3. 收集所有內容頁 URL
4. 序列化處理內容頁
"""

from typing import List, Dict, Any, Optional, Callable, Union
import asyncio
import time
from datetime import datetime
import random
from loguru import logger
from playwright.sync_api import Page
import threading


class PageManager:
    """
    頁面管理器，實現序列化頁面訪問，避免過多頁面同時打開
    """

    def __init__(self, browser_context):
        """
        初始化頁面管理器
        
        Args:
            browser_context: Playwright 瀏覽器上下文
        """
        self.context = browser_context
        self.main_page = None
        self.current_list_page = None
        self.content_page = None  # 新增：用於內容頁處理的單一頁面
        self.content_urls = []
        self.visited_urls = set()
        self.max_retry = 3
        self.retry_delay = 5
        self.page_delay_range = (2, 5)
        self.content_batch_size = 1
        self.next_page_selector = None
        self.content_selectors = []
        self._page_lock = threading.Lock()  # 新增：頁面操作鎖
        
    def set_main_page(self, page: Page) -> None:
        """
        設置主頁面
        
        Args:
            page: Playwright 頁面對象
        """
        self.main_page = page
        self.current_list_page = page
        
    def configure(
        self, 
        max_retry: int = 3, 
        retry_delay: int = 5,
        page_delay_range: tuple = (2, 5),
        content_batch_size: int = 1,
        next_page_selector: str = None,
        content_selectors: List[str] = None
    ) -> None:
        """
        配置頁面管理器
        
        Args:
            max_retry: 最大重試次數
            retry_delay: 重試延遲（秒）
            page_delay_range: 頁面間延遲範圍（秒）
            content_batch_size: 內容頁批次大小
            next_page_selector: 下一頁按鈕選擇器
            content_selectors: 內容頁鏈接選擇器列表
        """
        self.max_retry = max_retry
        self.retry_delay = retry_delay
        self.page_delay_range = page_delay_range
        self.content_batch_size = max(1, min(content_batch_size, 3))  # 限制批次大小在 1-3 之間
        
        if next_page_selector:
            self.next_page_selector = next_page_selector
            
        if content_selectors:
            self.content_selectors = content_selectors
            
    def navigate_to_search_page(self, url: str, timeout: int = 30000) -> bool:
        """
        導航到搜索/入口頁面
        
        Args:
            url: 目標 URL
            timeout: 超時時間（毫秒）
            
        Returns:
            bool: 是否成功
        """
        try:
            if not self.main_page:
                self.main_page = self.context.new_page()
                
            response = self.main_page.goto(
                url,
                timeout=timeout,
                wait_until="domcontentloaded"
            )
            
            self.current_list_page = self.main_page
            
            if not response:
                logger.warning(f"導航到 {url} 未收到響應")
                return False
                
            if response.status >= 400:
                logger.warning(f"導航到 {url} 返回錯誤狀態碼: {response.status}")
                return False
                
            # 記錄已訪問 URL
            self.visited_urls.add(url)
            logger.info(f"成功導航到搜索頁面: {url}")
            return True
            
        except Exception as e:
            logger.error(f"導航到搜索頁面失敗: {str(e)}")
            return False
            
    def process_list_pages(
        self, 
        max_pages: int = 5, 
        extract_content_links: bool = True
    ) -> List[str]:
        """
        處理列表頁，依次翻頁並收集內容頁 URL
        
        Args:
            max_pages: 最大處理頁數
            extract_content_links: 是否提取內容頁鏈接
            
        Returns:
            List[str]: 收集到的內容頁 URL 列表
        """
        if not self.current_list_page:
            logger.error("當前列表頁未初始化")
            return []
            
        if not self.next_page_selector:
            logger.error("未配置下一頁選擇器")
            return []
            
        if extract_content_links and not self.content_selectors:
            logger.error("未配置內容頁選擇器")
            return []
            
        page_count = 0
        content_urls = []
        
        try:
            while page_count < max_pages:
                # 等待頁面加載完成
                self.current_list_page.wait_for_load_state("domcontentloaded")
                
                # 提取當前頁的內容連結
                if extract_content_links:
                    page_content_urls = self._extract_content_urls(self.current_list_page)
                    content_urls.extend(page_content_urls)
                    logger.info(f"第 {page_count + 1} 頁：提取到 {len(page_content_urls)} 個內容頁 URL")
                
                # 檢查是否有下一頁
                next_page_visible = self.current_list_page.is_visible(self.next_page_selector)
                if not next_page_visible:
                    logger.info(f"已到達最後一頁，共處理 {page_count + 1} 頁")
                    break
                    
                # 點擊下一頁
                try:
                    self.current_list_page.click(self.next_page_selector)
                    page_count += 1
                    logger.info(f"已進入第 {page_count + 1} 頁")
                    
                    # 隨機延遲
                    delay = random.uniform(self.page_delay_range[0], self.page_delay_range[1])
                    time.sleep(delay)
                    
                except Exception as e:
                    logger.error(f"點擊下一頁按鈕失敗: {str(e)}")
                    break
        
        except Exception as e:
            logger.error(f"處理列表頁時發生錯誤: {str(e)}")
            
        # 更新內容頁 URL 列表並去重
        self.content_urls = list(set(self.content_urls + content_urls))
        logger.info(f"共收集到 {len(self.content_urls)} 個內容頁 URL（去重後）")
        
        return content_urls
        
    def _extract_content_urls(self, page: Page) -> List[str]:
        """
        從當前頁面提取內容頁 URL
        
        Args:
            page: Playwright 頁面對象
            
        Returns:
            List[str]: 內容頁 URL 列表
        """
        urls = []
        
        for selector in self.content_selectors:
            try:
                # 獲取所有匹配的元素
                elements = page.query_selector_all(selector)
                
                for element in elements:
                    try:
                        # 獲取元素的 href 屬性
                        href = element.get_attribute("href")
                        
                        if href:
                            # 轉換為絕對 URL
                            absolute_url = page.evaluate("(url) => new URL(url, window.location.href).href", href)
                            
                            if absolute_url and absolute_url not in urls:
                                urls.append(absolute_url)
                                
                    except Exception as e:
                        logger.debug(f"處理元素的 href 時發生錯誤: {str(e)}")
                        
            except Exception as e:
                logger.warning(f"使用選擇器 {selector} 提取連結時發生錯誤: {str(e)}")
                
        return urls
        
    def process_content_pages(
        self, 
        processor_func: Callable[[Page, str], Any],
        urls: List[str] = None,
        max_pages: int = None
    ) -> List[Any]:
        """
        序列化處理內容頁
        
        Args:
            processor_func: 處理函數，接收頁面和 URL 作為參數
            urls: 內容頁 URL 列表，如果為 None 則使用內部存儲的 URL
            max_pages: 最大處理頁面數，None 表示不限制
            
        Returns:
            List[Any]: 處理結果列表
        """
        if not urls:
            urls = self.content_urls
            
        if not urls:
            logger.warning("沒有內容頁 URL 需要處理")
            return []
            
        if max_pages:
            urls = urls[:max_pages]
            
        results = []
        processed_count = 0
        
        with self._page_lock:
            try:
                # 如果沒有內容頁，創建一個
                if not self.content_page or self.content_page.is_closed():
                    self.content_page = self.context.new_page()
                    logger.info("創建新的內容處理頁面")
                
                for i, url in enumerate(urls):
                    if url in self.visited_urls:
                        logger.info(f"跳過已訪問的 URL: {url}")
                        continue
                        
                    success = False
                    retry_count = 0
                    
                    while retry_count < self.max_retry and not success:
                        try:
                            logger.info(f"處理內容頁 ({i+1}/{len(urls)}): {url}")
                            
                            response = self.content_page.goto(
                                url,
                                wait_until="domcontentloaded"
                            )
                            
                            if not response or response.status >= 400:
                                logger.warning(f"導航到 {url} 失敗或返回錯誤狀態碼")
                                retry_count += 1
                                time.sleep(self.retry_delay)
                                continue
                                
                            result = processor_func(self.content_page, url)
                            results.append(result)
                            
                            self.visited_urls.add(url)
                            processed_count += 1
                            success = True
                            
                            # 添加隨機延遲
                            delay = random.uniform(*self.page_delay_range)
                            time.sleep(delay)
                            
                        except Exception as e:
                            logger.error(f"處理內容頁 {url} 時發生錯誤: {str(e)}")
                            retry_count += 1
                            time.sleep(self.retry_delay)
                            
                    if not success:
                        logger.error(f"處理內容頁 {url} 失敗，已達到最大重試次數")
                        
                # 處理完成後關閉內容頁
                if self.content_page and not self.content_page.is_closed():
                    self.content_page.close()
                    self.content_page = None
                    
                logger.info(f"內容頁處理完成，共處理 {processed_count} 個頁面")
                return results
                
            except Exception as e:
                logger.error(f"處理內容頁時發生錯誤: {str(e)}")
                # 確保在發生錯誤時也關閉頁面
                if self.content_page and not self.content_page.is_closed():
                    try:
                        self.content_page.close()
                    except:
                        pass
                    self.content_page = None
                return results
        
    def process_batch_content_pages(
        self, 
        processor_func: Callable[[Page, str], Any],
        urls: List[str] = None,
        max_pages: int = None
    ) -> List[Any]:
        """
        批量處理內容頁
        
        Args:
            processor_func: 處理函數，接收頁面和 URL 作為參數
            urls: 內容頁 URL 列表，如果為 None 則使用內部存儲的 URL
            max_pages: 最大處理頁面數，None 表示不限制
            
        Returns:
            List[Any]: 處理結果列表
        """
        if not urls:
            urls = self.content_urls
            
        if not urls:
            logger.warning("沒有內容頁 URL 需要處理")
            return []
            
        if max_pages:
            urls = urls[:max_pages]
            
        results = []
        processed_count = 0
        active_pages = {}  # 當前活動的頁面 {url: page}
        
        with self._page_lock:
            try:
                i = 0
                while i < len(urls):
                    # 填充活動頁面至批次大小
                    while len(active_pages) < self.content_batch_size and i < len(urls):
                        url = urls[i]
                        i += 1
                        
                        if url in self.visited_urls:
                            logger.info(f"跳過已訪問的 URL: {url}")
                            continue
                            
                        # 重用現有頁面或創建新頁面
                        if len(active_pages) < self.content_batch_size:
                            try:
                                page = self.context.new_page()
                                active_pages[url] = page
                                
                                logger.info(f"導航到內容頁 ({processed_count+1}/{len(urls)}): {url}")
                                response = page.goto(
                                    url,
                                    wait_until="domcontentloaded"
                                )
                                
                                if not response or response.status >= 400:
                                    logger.warning(f"導航到 {url} 失敗或返回錯誤狀態碼")
                                    page.close()
                                    del active_pages[url]
                                    continue
                                    
                            except Exception as e:
                                logger.error(f"導航到 {url} 時發生錯誤: {str(e)}")
                                if url in active_pages:
                                    try:
                                        active_pages[url].close()
                                    except:
                                        pass
                                    del active_pages[url]
                                continue
                    
                    # 處理當前活動的頁面
                    for url, page in list(active_pages.items()):
                        try:
                            result = processor_func(page, url)
                            results.append(result)
                            self.visited_urls.add(url)
                            processed_count += 1
                            
                            # 關閉已處理的頁面
                            page.close()
                            del active_pages[url]
                            
                            # 添加隨機延遲
                            delay = random.uniform(*self.page_delay_range)
                            time.sleep(delay)
                            
                        except Exception as e:
                            logger.error(f"處理內容頁 {url} 時發生錯誤: {str(e)}")
                            try:
                                page.close()
                            except:
                                pass
                            if url in active_pages:
                                del active_pages[url]
                    
                    # 檢查是否所有頁面都已處理
                    if i >= len(urls) and not active_pages:
                        break
                    
                    # 添加批次間延遲
                    if active_pages:
                        time.sleep(random.uniform(*self.page_delay_range))
                
                # 確保所有頁面都已關閉
                for page in active_pages.values():
                    try:
                        page.close()
                    except:
                        pass
                
                logger.info(f"批量內容頁處理完成，共處理 {processed_count} 個頁面")
                return results
                
            except Exception as e:
                logger.error(f"批量處理內容頁時發生錯誤: {str(e)}")
                # 確保在發生錯誤時關閉所有頁面
                for page in active_pages.values():
                    try:
                        page.close()
                    except:
                        pass
                return results
        
    def add_content_urls(self, urls: List[str]) -> None:
        """
        添加內容頁 URL
        
        Args:
            urls: 內容頁 URL 列表
        """
        if not urls:
            return
            
        new_urls = [url for url in urls if url not in self.content_urls]
        self.content_urls.extend(new_urls)
        logger.info(f"添加了 {len(new_urls)} 個新的內容頁 URL，總計 {len(self.content_urls)} 個")
        
    def clear_content_urls(self) -> None:
        """清空內容頁 URL 列表"""
        self.content_urls = []
        
    def get_content_urls(self) -> List[str]:
        """
        獲取內容頁 URL 列表
        
        Returns:
            List[str]: 內容頁 URL 列表
        """
        return self.content_urls

    def get_page_count(self) -> int:
        """
        獲取當前頁面數量
        
        Returns:
            int: 當前頁面數量
        """
        return len(self.context.pages) if self.context else 0

    def close(self) -> None:
        """
        關閉所有頁面並清理資源
        """
        try:
            if self.main_page and not self.main_page.is_closed():
                self.main_page.close()
            if self.current_list_page and not self.current_list_page.is_closed():
                self.current_list_page.close()
            if self.content_page and not self.content_page.is_closed():
                self.content_page.close()
                
            self.main_page = None
            self.current_list_page = None
            self.content_page = None
            self.content_urls = []
            self.visited_urls.clear()
            
            logger.info("頁面管理器已關閉")
        except Exception as e:
            logger.error(f"關閉頁面管理器時發生錯誤: {str(e)}")

# 請勿在此模組頂層執行任何流程或實例化，僅保留 PageManager 類定義。
# 如需範例，請參考 docs/ 或 examples/ 目錄。