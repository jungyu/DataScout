#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
反檢測模組高級使用示例

此示例展示如何使用反檢測模組的高級功能：
1. 自定義指紋生成
2. 代理池管理
3. 複雜的人類行為模擬
4. 用戶代理輪換策略
5. 黑名單管理
"""

import asyncio
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
from playwright.async_api import async_playwright
from loguru import logger

from ..anti_detection_manager import AntiDetectionManager
from ..fingerprint import FingerprintManager
from ..proxy_manager import ProxyManager
from ..behavior_manager import BehaviorManager
from ..user_agent_manager import UserAgentManager


class AdvancedAntiDetection:
    """高級反檢測類"""
    
    def __init__(self):
        """初始化高級反檢測類"""
        self.anti_detection = AntiDetectionManager()
        self.fingerprint_manager = FingerprintManager()
        self.proxy_manager = ProxyManager()
        self.behavior_manager = BehaviorManager()
        self.ua_manager = UserAgentManager()
        
        # 代理池
        self.proxy_pool: List[Dict[str, Any]] = []
        
        # 用戶代理池
        self.ua_pool: List[str] = []
        
        # 黑名單
        self.blacklist: Dict[str, List[Dict[str, Any]]] = {
            "proxy": [],
            "ua": []
        }
    
    def load_proxy_pool(self, proxies: List[Dict[str, Any]]) -> None:
        """
        載入代理池
        
        Args:
            proxies: 代理列表
        """
        self.proxy_pool = proxies
        for proxy in proxies:
            self.proxy_manager.add_proxy(proxy)
    
    def load_ua_pool(self, user_agents: List[str]) -> None:
        """
        載入用戶代理池
        
        Args:
            user_agents: 用戶代理列表
        """
        self.ua_pool = user_agents
        for ua in user_agents:
            self.ua_manager.add_to_blacklist({"ua": ua, "added_at": datetime.now()})
    
    def get_random_proxy(self) -> Dict[str, Any]:
        """
        獲取隨機代理
        
        Returns:
            Dict[str, Any]: 代理配置
        """
        return random.choice(self.proxy_pool) if self.proxy_pool else None
    
    def get_random_ua(self) -> str:
        """
        獲取隨機用戶代理
        
        Returns:
            str: 用戶代理字符串
        """
        return random.choice(self.ua_pool) if self.ua_pool else None
    
    def add_to_blacklist(self, item: Dict[str, Any], blacklist_type: str) -> None:
        """
        將項目添加到黑名單
        
        Args:
            item: 要添加到黑名單的項目
            blacklist_type: 黑名單類型（proxy/ua）
        """
        if blacklist_type not in self.blacklist:
            return
        
        item["added_at"] = datetime.now()
        self.blacklist[blacklist_type].append(item)
        self.anti_detection.add_to_blacklist(item, blacklist_type)
    
    def clean_blacklist(self) -> None:
        """清理過期的黑名單項目"""
        current_time = datetime.now()
        
        for blacklist_type, items in self.blacklist.items():
            self.blacklist[blacklist_type] = [
                item for item in items
                if current_time - item["added_at"] < timedelta(hours=24)
            ]
        
        self.anti_detection.clean_blacklists()
    
    async def simulate_human_behavior(self, page) -> None:
        """
        模擬複雜的人類行為
        
        Args:
            page: Playwright 頁面對象
        """
        # 隨機滾動
        scroll_times = random.randint(3, 7)
        for _ in range(scroll_times):
            await self.anti_detection.scroll_page(page)
            await asyncio.sleep(random.uniform(0.5, 2.0))
        
        # 隨機移動鼠標
        elements = await page.query_selector_all('a, button, input')
        if elements:
            for _ in range(random.randint(2, 5)):
                element = random.choice(elements)
                box = await element.bounding_box()
                if box:
                    await self.anti_detection.move_mouse(
                        page,
                        (box['x'] + box['width']/2, box['y'] + box['height']/2)
                    )
                await asyncio.sleep(random.uniform(0.3, 1.0))
        
        # 隨機點擊
        if elements:
            element = random.choice(elements)
            await self.anti_detection.click_element(page, await element.get_attribute('id'))
            await asyncio.sleep(random.uniform(1.0, 3.0))
    
    async def run(self, url: str) -> None:
        """
        運行高級反檢測
        
        Args:
            url: 目標網址
        """
        async with async_playwright() as p:
            # 啟動瀏覽器
            browser = await p.chromium.launch(
                headless=False,
                args=['--no-sandbox']
            )
            
            # 創建新頁面
            page = await browser.new_page()
            
            try:
                # 應用反檢測功能
                await self.anti_detection.apply_anti_detection(page)
                
                # 訪問目標網站
                await page.goto(url)
                
                # 模擬人類行為
                await self.simulate_human_behavior(page)
                
                # 等待結果
                await page.wait_for_load_state('networkidle')
                
                # 檢查結果
                if await page.query_selector('.success-message'):
                    logger.info("操作成功")
                else:
                    logger.warning("操作失敗")
                
            except Exception as e:
                logger.error(f"發生錯誤: {str(e)}")
            
            finally:
                # 關閉瀏覽器
                await browser.close()
                
                # 清理黑名單
                self.clean_blacklist()


async def main():
    """主函數"""
    # 初始化高級反檢測
    anti_detection = AdvancedAntiDetection()
    
    # 載入代理池
    proxies = [
        {
            "server": "http://proxy1.example.com:8080",
            "username": "user1",
            "password": "pass1"
        },
        {
            "server": "http://proxy2.example.com:8080",
            "username": "user2",
            "password": "pass2"
        }
    ]
    anti_detection.load_proxy_pool(proxies)
    
    # 載入用戶代理池
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    ]
    anti_detection.load_ua_pool(user_agents)
    
    # 運行高級反檢測
    await anti_detection.run('https://example.com')


if __name__ == '__main__':
    asyncio.run(main()) 