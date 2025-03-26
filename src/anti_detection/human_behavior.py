#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import random
import logging
from typing import Dict

from selenium import webdriver
from selenium.webdriver import ActionChains


class HumanBehaviorSimulator:
    """模擬人類行為"""
    
    def __init__(self, delays: Dict, logger=None):
        """
        初始化人類行為模擬器
        
        Args:
            delays: 延遲配置
            logger: 日誌記錄器
        """
        self.delays = delays
        self.logger = logger or logging.getLogger(__name__)
    
    def random_delay(self, delay_type: str = "between_actions"):
        """
        根據配置的延遲範圍，生成隨機延遲時間並等待
        
        Args:
            delay_type: 延遲類型，可選值：page_load, between_actions, before_click, typing_speed
        """
        delay_config = self.delays.get(delay_type, {"min": 1, "max": 3})
        min_delay = delay_config.get("min", 1)
        max_delay = delay_config.get("max", 3)
        
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    def simulate_human_typing(self, element, text: str, focus_first: bool = True):
        """
        模擬人類輸入文字
        
        Args:
            element: 要輸入的元素
            text: 要輸入的文字
            focus_first: 是否先聚焦元素
        """
        try:
            if focus_first:
                element.click()
            
            # 清除現有內容
            element.clear()
            
            typing_speed = self.delays.get("typing_speed", {"min": 0.05, "max": 0.2})
            min_speed = typing_speed.get("min", 0.05)
            max_speed = typing_speed.get("max", 0.2)
            
            # 逐字輸入
            for char in text:
                element.send_keys(char)
                delay = random.uniform(min_speed, max_speed)
                time.sleep(delay)
            
            # 輸入完成後的延遲
            self.random_delay("before_click")
        
        except Exception as e:
            self.logger.error(f"模擬人類輸入失敗: {str(e)}")
    
    def simulate_human_scroll(self, driver: webdriver.Remote, scroll_amount: int = None, direction: str = "down"):
        """
        模擬人類滾動頁面
        
        Args:
            driver: WebDriver實例
            scroll_amount: 滾動量，為None時隨機滾動
            direction: 滾動方向，可選值：up, down
        """
        try:
            # 如果未指定滾動量，生成隨機值
            if scroll_amount is None:
                scroll_amount = random.randint(100, 800)
            
            # 根據方向調整滾動量
            if direction.lower() == "up":
                scroll_amount = -scroll_amount
            
            # 使用JavaScript滾動
            script = f"window.scrollBy(0, {scroll_amount});"
            driver.execute_script(script)
            
            # 滾動後的延遲
            self.random_delay("between_actions")
        
        except Exception as e:
            self.logger.error(f"模擬人類滾動失敗: {str(e)}")
    
    def simulate_human_mouse_movement(self, driver: webdriver.Remote, target_element=None):
        """
        模擬人類鼠標移動
        
        Args:
            driver: WebDriver實例
            target_element: 目標元素，為None時隨機移動
        """
        try:
            actions = ActionChains(driver)
            
            if target_element:
                # 移動到目標元素
                actions.move_to_element(target_element)
            else:
                # 隨機移動
                x = random.randint(100, 700)
                y = random.randint(100, 500)
                actions.move_by_offset(x, y)
            
            actions.perform()
            
            # 移動後的延遲
            self.random_delay("between_actions")
        
        except Exception as e:
            self.logger.error(f"模擬人類鼠標移動失敗: {str(e)}")