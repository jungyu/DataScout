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
        self.content_urls = []  # 存儲所有內容頁 URL
        self.visited_urls = set()  # 已訪問過的 URL
        self.max_retry = 3  # 最大重試次數
        self.retry_delay = 5  # 重試延遲（秒）
        self.page_delay_range = (2, 5)  # 頁面間延遲範圍（秒）
        self.content_batch_size = 1  # 內容頁批次大小，預設為 1（序列化處理）
        self.next_page_selector = None  # 下一頁按鈕選擇器
        self.content_selectors = []  # 內容頁鏈接選擇器
        
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
        依次處理內容頁
        
        Args:
            processor_func: 頁面處理函數，參數為 (page, url)
            urls: 內容頁 URL 列表，如未提供則使用之前收集的 URL
            max_pages: 最大處理頁數
            
        Returns:
            List[Any]: 頁面處理結果列表
        """
        if not urls:
            urls = self.content_urls
            
        if not urls:
            logger.error("沒有可處理的內容頁 URL")
            return []
            
        if max_pages and max_pages > 0:
            urls = urls[:max_pages]
            
        results = []
        processed_count = 0
        
        # 創建一個新頁面用於內容頁處理
        content_page = self.context.new_page()
        
        try:
            for i, url in enumerate(urls):
                # 檢查 URL 是否已訪問
                if url in self.visited_urls:
                    logger.info(f"跳過已訪問的 URL: {url}")
                    continue
                    
                # 嘗試訪問頁面
                success = False
                retry_count = 0
                
                while retry_count < self.max_retry and not success:
                    try:
                        logger.info(f"處理內容頁 ({i+1}/{len(urls)}): {url}")
                        
                        # 導航到頁面
                        response = content_page.goto(
                            url,
                            wait_until="domcontentloaded"
                        )
                        
                        if not response:
                            logger.warning(f"導航到 {url} 未收到響應")
                            retry_count += 1
                            time.sleep(self.retry_delay)
                            continue
                            
                        if response.status >= 400:
                            logger.warning(f"導航到 {url} 返回錯誤狀態碼: {response.status}")
                            retry_count += 1
                            time.sleep(self.retry_delay)
                            continue
                            
                        # 處理頁面
                        result = processor_func(content_page, url)
                        results.append(result)
                        
                        # 標記為已訪問
                        self.visited_urls.add(url)
                        processed_count += 1
                        success = True
                        
                    except Exception as e:
                        retry_count += 1
                        logger.warning(f"處理頁面 {url} 時發生錯誤: {str(e)}，重試 {retry_count}/{self.max_retry}")
                        time.sleep(self.retry_delay)
                        
                # 隨機延遲
                delay = random.uniform(self.page_delay_range[0], self.page_delay_range[1])
                time.sleep(delay)
                
        except Exception as e:
            logger.error(f"處理內容頁時發生錯誤: {str(e)}")
            
        finally:
            # 關閉內容頁
            try:
                if content_page and not content_page.is_closed():
                    content_page.close()
            except:
                pass
                
        logger.info(f"已處理 {processed_count}/{len(urls)} 個內容頁")
        return results
        
    def process_batch_content_pages(
        self, 
        processor_func: Callable[[Page, str], Any],
        urls: List[str] = None,
        max_pages: int = None
    ) -> List[Any]:
        """
        批次處理內容頁（適用於資源較豐富的情況，但批次大小有限制，預設為 1）
        
        Args:
            processor_func: 頁面處理函數，參數為 (page, url)
            urls: 內容頁 URL 列表，如未提供則使用之前收集的 URL
            max_pages: 最大處理頁數
            
        Returns:
            List[Any]: 頁面處理結果列表
        """
        if self.content_batch_size <= 1:
            # 如果批次大小為 1，則使用序列化處理
            return self.process_content_pages(processor_func, urls, max_pages)
            
        if not urls:
            urls = self.content_urls
            
        if not urls:
            logger.error("沒有可處理的內容頁 URL")
            return []
            
        if max_pages and max_pages > 0:
            urls = urls[:max_pages]
            
        results = []
        processed_count = 0
        active_pages = {}  # 當前活動的頁面 {url: page}
        
        try:
            # 處理所有 URL
            i = 0
            while i < len(urls):
                # 填充活動頁面至批次大小
                while len(active_pages) < self.content_batch_size and i < len(urls):
                    url = urls[i]
                    i += 1
                    
                    # 檢查 URL 是否已訪問
                    if url in self.visited_urls:
                        logger.info(f"跳過已訪問的 URL: {url}")
                        continue
                        
                    # 創建新頁面
                    page = self.context.new_page()
                    
                    # 導航到頁面
                    try:
                        logger.info(f"導航到內容頁 ({processed_count+1}/{len(urls)}): {url}")
                        response = page.goto(
                            url,
                            wait_until="domcontentloaded"
                        )
                        
                        if not response or response.status >= 400:
                            logger.warning(f"導航到 {url} 失敗或返回錯誤狀態碼")
                            page.close()
                        else:
                            active_pages[url] = page
                            
                    except Exception as e:
                        logger.error(f"導航到 {url} 時發生錯誤: {str(e)}")
                        try:
                            page.close()
                        except:
                            pass
                
                # 處理當前活動的頁面
                completed_urls = []
                for url, page in active_pages.items():
                    try:
                        # 處理頁面
                        result = processor_func(page, url)
                        results.append(result)
                        
                        # 標記為已訪問
                        self.visited_urls.add(url)
                        processed_count += 1
                        completed_urls.append(url)
                        
                    except Exception as e:
                        logger.error(f"處理頁面 {url} 時發生錯誤: {str(e)}")
                        completed_urls.append(url)
                        
                    finally:
                        # 關閉頁面
                        try:
                            if not page.is_closed():
                                page.close()
                        except:
                            pass
                
                # 從活動頁面中移除已完成的頁面
                for url in completed_urls:
                    if url in active_pages:
                        del active_pages[url]
                
                # 隨機延遲
                delay = random.uniform(self.page_delay_range[0], self.page_delay_range[1])
                time.sleep(delay)
                
        except Exception as e:
            logger.error(f"批次處理內容頁時發生錯誤: {str(e)}")
            
        finally:
            # 關閉所有活動頁面
            for page in active_pages.values():
                try:
                    if not page.is_closed():
                        page.close()
                except:
                    pass
                    
        logger.info(f"已處理 {processed_count}/{len(urls)} 個內容頁")
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

# 請勿在此模組頂層執行任何流程或實例化，僅保留 PageManager 類定義。
# 如需範例，請參考 docs/ 或 examples/ 目錄。