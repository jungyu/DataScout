#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
高級反檢測模組

提供更複雜的反檢測功能，包含：
1. 代理池管理
2. 用戶代理池管理
3. 黑名單管理
4. 複雜的人類行為模擬
"""

import asyncio
import random
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from loguru import logger


class AdvancedAntiDetection:
    """高級反檢測類"""
    
    def __init__(self):
        """初始化高級反檢測類"""
        # 代理池
        self.proxy_pool: List[Dict[str, Any]] = []
        
        # 用戶代理池
        self.ua_pool: List[str] = []
        
        # 黑名單
        self.blacklist: Dict[str, List[Dict[str, Any]]] = {
            "proxy": [],
            "ua": []
        }
        
        # 人類行為配置
        self.behavior_config = {
            "mouse_movement": {
                "min_speed": 0.5,
                "max_speed": 2.0,
                "min_steps": 10,
                "max_steps": 30
            },
            "scroll": {
                "min_times": 3,
                "max_times": 8,
                "min_distance": 100,
                "max_distance": 800,
                "min_delay": 0.5,
                "max_delay": 2.0
            },
            "typing": {
                "min_delay": 0.05,
                "max_delay": 0.3,
                "mistake_probability": 0.05
            }
        }
    
    def load_proxy_pool(self, proxies: List[Dict[str, Any]]) -> None:
        """
        載入代理池
        
        Args:
            proxies: 代理列表，每個代理為包含 server, username, password 的字典
        """
        self.proxy_pool = proxies
        logger.info(f"已載入 {len(proxies)} 個代理")
    
    def load_ua_pool(self, user_agents: List[str]) -> None:
        """
        載入用戶代理池
        
        Args:
            user_agents: 用戶代理字串列表
        """
        self.ua_pool = user_agents
        logger.info(f"已載入 {len(user_agents)} 個用戶代理")
    
    def get_random_proxy(self) -> Optional[Dict[str, Any]]:
        """
        獲取隨機代理
        
        Returns:
            Dict[str, Any]: 代理配置，如果沒有可用代理則返回 None
        """
        active_proxies = [p for p in self.proxy_pool if not self._is_blacklisted(p, "proxy")]
        return random.choice(active_proxies) if active_proxies else None
    
    def get_random_ua(self) -> Optional[str]:
        """
        獲取隨機用戶代理
        
        Returns:
            str: 用戶代理字符串，如果沒有可用用戶代理則返回 None
        """
        active_uas = [ua for ua in self.ua_pool if not self._is_blacklisted({"ua": ua}, "ua")]
        return random.choice(active_uas) if active_uas else None
    
    def add_to_blacklist(self, item: Dict[str, Any], blacklist_type: str) -> None:
        """
        將項目添加到黑名單
        
        Args:
            item: 要添加到黑名單的項目
            blacklist_type: 黑名單類型（proxy/ua）
        """
        if blacklist_type not in self.blacklist:
            logger.warning(f"嘗試添加項目到不存在的黑名單類型: {blacklist_type}")
            return
        
        item["added_at"] = datetime.now()
        self.blacklist[blacklist_type].append(item)
        logger.info(f"已將項目添加到 {blacklist_type} 黑名單")
    
    def _is_blacklisted(self, item: Dict[str, Any], blacklist_type: str) -> bool:
        """
        檢查項目是否在黑名單中
        
        Args:
            item: 要檢查的項目
            blacklist_type: 黑名單類型（proxy/ua）
            
        Returns:
            bool: 項目是否在黑名單中
        """
        if blacklist_type == "proxy":
            return any(b.get("server") == item.get("server") for b in self.blacklist["proxy"])
        elif blacklist_type == "ua":
            return any(b.get("ua") == item.get("ua") for b in self.blacklist["ua"])
        return False
    
    def clean_blacklist(self) -> None:
        """清理過期的黑名單項目（預設24小時過期）"""
        current_time = datetime.now()
        
        for blacklist_type, items in self.blacklist.items():
            before_count = len(items)
            self.blacklist[blacklist_type] = [
                item for item in items
                if current_time - item["added_at"] < timedelta(hours=24)
            ]
            after_count = len(self.blacklist[blacklist_type])
            if before_count != after_count:
                logger.info(f"已從 {blacklist_type} 黑名單清理 {before_count - after_count} 個過期項目")
    
    async def simulate_human_behavior(self, page) -> None:
        """
        模擬複雜的人類行為
        
        Args:
            page: Playwright 頁面對象
        """
        # 隨機滾動
        await self._simulate_human_scroll(page)
        
        # 隨機移動鼠標
        await self._simulate_human_mouse_movement(page)
        
        # 隨機點擊
        await self._simulate_human_click(page)
        
        logger.info("已完成人類行為模擬")
    
    async def _simulate_human_scroll(self, page) -> None:
        """
        模擬人類滾動頁面
        
        Args:
            page: Playwright 頁面對象
        """
        config = self.behavior_config["scroll"]
        scroll_times = random.randint(config["min_times"], config["max_times"])
        
        logger.info(f"開始模擬人類滾動，將執行 {scroll_times} 次滾動操作")
        
        for i in range(scroll_times):
            distance = random.randint(config["min_distance"], config["max_distance"])
            
            # 生成平滑滾動的步驟
            steps = random.randint(5, 15)
            step_distance = distance / steps
            
            for step in range(steps):
                await page.evaluate(f"window.scrollBy(0, {step_distance});")
                await asyncio.sleep(random.uniform(0.01, 0.05))
            
            logger.debug(f"已滾動 {distance}px（第 {i+1}/{scroll_times} 次）")
            await asyncio.sleep(random.uniform(config["min_delay"], config["max_delay"]))
    
    async def _simulate_human_mouse_movement(self, page) -> None:
        """
        模擬人類鼠標移動
        
        Args:
            page: Playwright 頁面對象
        """
        config = self.behavior_config["mouse_movement"]
        
        # 找到可點擊元素
        elements = await page.query_selector_all('a, button, input, select, textarea')
        if not elements:
            logger.debug("頁面上未找到可互動的元素，跳過鼠標移動模擬")
            return
        
        # 隨機選擇2-5個元素
        num_elements = min(len(elements), random.randint(2, 5))
        selected_elements = random.sample(elements, num_elements)
        
        logger.info(f"開始模擬人類鼠標移動，將訪問 {num_elements} 個元素")
        
        # 獲取當前鼠標位置
        current_x, current_y = 100, 100  # 初始位置
        
        for i, element in enumerate(selected_elements):
            try:
                # 獲取元素位置
                box = await element.bounding_box()
                if not box:
                    continue
                
                target_x = box["x"] + box["width"] / 2
                target_y = box["y"] + box["height"] / 2
                
                # 計算路徑點
                steps = random.randint(config["min_steps"], config["max_steps"])
                
                # 使用貝塞爾曲線生成自然移動路徑
                control_x = (current_x + target_x) / 2 + random.uniform(-100, 100)
                control_y = (current_y + target_y) / 2 + random.uniform(-100, 100)
                
                for step in range(steps):
                    t = step / steps
                    # 二次貝塞爾曲線
                    x = (1 - t) ** 2 * current_x + 2 * (1 - t) * t * control_x + t ** 2 * target_x
                    y = (1 - t) ** 2 * current_y + 2 * (1 - t) * t * control_y + t ** 2 * target_y
                    
                    await page.mouse.move(x, y)
                    await asyncio.sleep(random.uniform(0.01, 0.05))
                
                # 更新當前位置
                current_x, current_y = target_x, target_y
                
                # 在元素上暫停
                await asyncio.sleep(random.uniform(0.2, 1.0))
                
                logger.debug(f"已移動到元素 {i+1}/{num_elements}")
                
            except Exception as e:
                logger.warning(f"移動鼠標到元素時出錯: {str(e)}")
    
    async def _simulate_human_click(self, page) -> None:
        """
        模擬人類點擊行為
        
        Args:
            page: Playwright 頁面對象
        """
        # 找到可點擊元素
        elements = await page.query_selector_all('a, button, input[type="submit"], input[type="button"]')
        if not elements:
            logger.debug("頁面上未找到可點擊的元素，跳過點擊模擬")
            return
        
        # 隨機選擇一個元素
        element = random.choice(elements)
        
        try:
            # 獲取元素位置
            box = await element.bounding_box()
            if not box:
                return
            
            # 計算點擊座標（稍微偏離中心點）
            x = box["x"] + box["width"] / 2 + random.uniform(-10, 10)
            y = box["y"] + box["height"] / 2 + random.uniform(-5, 5)
            
            tag_name = await element.evaluate("el => el.tagName.toLowerCase()")
            attr = await element.get_attribute("type") or ""
            
            # 對於某些元素避免實際點擊
            safe_elements = ["input", "button"]
            dangerous_types = ["submit", "button"]
            
            if tag_name.lower() in safe_elements and attr.lower() in dangerous_types:
                logger.info(f"識別到可能會觸發表單提交的元素 ({tag_name}[type='{attr}']), 跳過點擊")
                return
            
            # 點擊元素前懸停
            await page.mouse.move(x, y)
            await asyncio.sleep(random.uniform(0.3, 1.0))
            
            # 實際點擊
            await page.mouse.click(x, y)
            logger.info(f"已點擊 {tag_name} 元素")
            
            # 點擊後等待
            await asyncio.sleep(random.uniform(1.0, 3.0))
            
        except Exception as e:
            logger.warning(f"模擬點擊時出錯: {str(e)}")
    
    async def simulate_human_typing(self, page, selector: str, text: str) -> None:
        """
        模擬人類打字
        
        Args:
            page: Playwright 頁面對象
            selector: 輸入框選擇器
            text: 要輸入的文本
        """
        config = self.behavior_config["typing"]
        
        try:
            # 先聚焦元素
            await page.focus(selector)
            await asyncio.sleep(random.uniform(0.3, 0.7))
            
            # 逐字輸入
            for char in text:
                # 隨機模擬打字錯誤
                if random.random() < config["mistake_probability"]:
                    # 輸入錯誤字符
                    wrong_char = chr(ord(char) + random.randint(1, 5))
                    await page.keyboard.press(wrong_char)
                    await asyncio.sleep(random.uniform(0.1, 0.3))
                    # 刪除錯誤字符
                    await page.keyboard.press("Backspace")
                    await asyncio.sleep(random.uniform(0.1, 0.3))
                
                # 輸入正確字符
                await page.keyboard.press(char)
                await asyncio.sleep(random.uniform(config["min_delay"], config["max_delay"]))
            
            logger.info(f"已完成人類打字模擬，輸入文本長度: {len(text)}")
            
        except Exception as e:
            logger.warning(f"模擬人類打字時出錯: {str(e)}")

    async def run(self, page, url: str) -> None:
        """
        運行高級反檢測
        
        Args:
            page: Playwright 頁面對象
            url: 目標網址
        """
        try:
            logger.info(f"開始訪問 {url} 並應用高級反檢測技術")
            
            # 訪問目標網站
            await page.goto(url)
            
            # 等待頁面加載完成
            await page.wait_for_load_state("networkidle")
            
            # 模擬人類行為
            await self.simulate_human_behavior(page)
            
            # 清理黑名單
            self.clean_blacklist()
            
            logger.info("高級反檢測流程完成")
            
        except Exception as e:
            logger.error(f"執行高級反檢測時發生錯誤: {str(e)}")
            raise Exception(f"高級反檢測失敗: {str(e)}")
