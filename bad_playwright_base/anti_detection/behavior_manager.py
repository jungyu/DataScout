#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
人類行為模擬模組

此模組提供人類行為模擬功能，包括：
1. 鼠標移動軌跡
2. 鍵盤輸入模式
3. 滾動行為
4. 點擊行為
5. 表單填寫行為
"""

from typing import Dict, Any, List, Tuple, Optional
import random
import time
import math
from datetime import datetime
from loguru import logger

from ..utils.exceptions import AntiDetectionException


class BehaviorManager:
    """人類行為管理器"""
    
    def __init__(self):
        """初始化人類行為管理器"""
        # 行為配置
        self.behavior_config = {
            "enabled": True,
            "mouse_speed": {
                "min": 0.5,
                "max": 2.0
            },
            "typing_speed": {
                "min": 100,
                "max": 300
            },
            "scroll_speed": {
                "min": 100,
                "max": 500
            },
            "click_delay": {
                "min": 0.1,
                "max": 0.5
            },
            "form_delay": {
                "min": 0.5,
                "max": 2.0
            }
        }
    
    def set_behavior_config(self, config: Dict[str, Any]) -> None:
        """
        設置行為配置
        
        Args:
            config: 行為配置字典
        """
        try:
            self.behavior_config.update(config)
            logger.info("已更新行為配置")
        except Exception as e:
            logger.error(f"更新行為配置時發生錯誤: {str(e)}")
            raise AntiDetectionException(f"更新行為配置失敗: {str(e)}")
    
    def get_bezier_curve_points(self, start: Tuple[int, int], end: Tuple[int, int], control_points: int = 2) -> List[Tuple[int, int]]:
        """
        生成貝塞爾曲線路徑點
        
        Args:
            start: 起始點坐標
            end: 終點坐標
            control_points: 控制點數量
            
        Returns:
            List[Tuple[int, int]]: 路徑點列表
        """
        try:
            points = []
            # 生成隨機控制點
            control = []
            for _ in range(control_points):
                x = random.randint(min(start[0], end[0]), max(start[0], end[0]))
                y = random.randint(min(start[1], end[1]), max(start[1], end[1]))
                control.append((x, y))
            
            # 計算貝塞爾曲線上的點
            steps = 50
            for i in range(steps + 1):
                t = i / steps
                x = (1 - t) ** 3 * start[0] + 3 * (1 - t) ** 2 * t * control[0][0] + 3 * (1 - t) * t ** 2 * control[1][0] + t ** 3 * end[0]
                y = (1 - t) ** 3 * start[1] + 3 * (1 - t) ** 2 * t * control[0][1] + 3 * (1 - t) * t ** 2 * control[1][1] + t ** 3 * end[1]
                points.append((int(x), int(y)))
            
            return points
        except Exception as e:
            logger.error(f"生成貝塞爾曲線路徑點時發生錯誤: {str(e)}")
            raise AntiDetectionException(f"生成貝塞爾曲線路徑點失敗: {str(e)}")
    
    async def move_mouse(self, page, target: Tuple[int, int]) -> None:
        """
        模擬人類鼠標移動
        
        Args:
            page: Playwright 頁面對象
            target: 目標坐標
        """
        try:
            if not self.behavior_config["enabled"]:
                await page.mouse.move(target[0], target[1])
                return
            
            # 獲取當前鼠標位置
            current_position = await page.evaluate("""() => {
                return [window.mouseX || 0, window.mouseY || 0];
            }""")
            
            # 生成移動路徑
            points = self.get_bezier_curve_points(current_position, target)
            
            # 執行移動
            for point in points:
                await page.mouse.move(point[0], point[1])
                # 添加隨機延遲
                await page.wait_for_timeout(random.randint(10, 30))
            
            logger.debug(f"已移動鼠標到: {target}")
        except Exception as e:
            logger.error(f"移動鼠標時發生錯誤: {str(e)}")
            raise AntiDetectionException(f"移動鼠標失敗: {str(e)}")
    
    async def type_text(self, page, selector: str, text: str) -> None:
        """
        模擬人類鍵盤輸入
        
        Args:
            page: Playwright 頁面對象
            selector: 元素選擇器
            text: 要輸入的文本
        """
        try:
            if not self.behavior_config["enabled"]:
                await page.type(selector, text)
                return
            
            # 點擊輸入框
            await page.click(selector)
            
            # 逐字符輸入
            for char in text:
                await page.type(selector, char)
                # 添加隨機延遲
                delay = random.randint(
                    self.behavior_config["typing_speed"]["min"],
                    self.behavior_config["typing_speed"]["max"]
                )
                await page.wait_for_timeout(delay)
            
            logger.debug(f"已輸入文本: {text}")
        except Exception as e:
            logger.error(f"輸入文本時發生錯誤: {str(e)}")
            raise AntiDetectionException(f"輸入文本失敗: {str(e)}")
    
    async def scroll_page(self, page, distance: int = None) -> None:
        """
        模擬人類頁面滾動
        
        Args:
            page: Playwright 頁面對象
            distance: 滾動距離（像素）
        """
        try:
            if not self.behavior_config["enabled"]:
                if distance:
                    await page.evaluate(f"window.scrollBy(0, {distance})")
                else:
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                return
            
            # 如果沒有指定距離，滾動到頁面底部
            if not distance:
                distance = await page.evaluate("document.body.scrollHeight")
            
            # 分段滾動
            steps = random.randint(5, 10)
            step_distance = distance / steps
            
            for _ in range(steps):
                # 添加隨機偏移
                offset = random.randint(-50, 50)
                await page.evaluate(f"window.scrollBy(0, {step_distance + offset})")
                
                # 添加隨機延遲
                delay = random.randint(
                    self.behavior_config["scroll_speed"]["min"],
                    self.behavior_config["scroll_speed"]["max"]
                )
                await page.wait_for_timeout(delay)
            
            logger.debug(f"已滾動頁面: {distance}px")
        except Exception as e:
            logger.error(f"滾動頁面時發生錯誤: {str(e)}")
            raise AntiDetectionException(f"滾動頁面失敗: {str(e)}")
    
    async def click_element(self, page, selector: str) -> None:
        """
        模擬人類點擊行為
        
        Args:
            page: Playwright 頁面對象
            selector: 元素選擇器
        """
        try:
            if not self.behavior_config["enabled"]:
                await page.click(selector)
                return
            
            # 獲取元素位置
            element = await page.query_selector(selector)
            if not element:
                raise AntiDetectionException(f"未找到元素: {selector}")
            
            box = await element.bounding_box()
            target = (
                box["x"] + box["width"] / 2 + random.randint(-5, 5),
                box["y"] + box["height"] / 2 + random.randint(-5, 5)
            )
            
            # 移動鼠標
            await self.move_mouse(page, target)
            
            # 添加隨機延遲
            delay = random.uniform(
                self.behavior_config["click_delay"]["min"],
                self.behavior_config["click_delay"]["max"]
            )
            await page.wait_for_timeout(int(delay * 1000))
            
            # 點擊
            await page.mouse.click(target[0], target[1])
            
            logger.debug(f"已點擊元素: {selector}")
        except Exception as e:
            logger.error(f"點擊元素時發生錯誤: {str(e)}")
            raise AntiDetectionException(f"點擊元素失敗: {str(e)}")
    
    async def fill_form(self, page, form_data: Dict[str, str]) -> None:
        """
        模擬人類表單填寫行為
        
        Args:
            page: Playwright 頁面對象
            form_data: 表單數據字典
        """
        try:
            if not self.behavior_config["enabled"]:
                for selector, value in form_data.items():
                    await page.fill(selector, value)
                return
            
            for selector, value in form_data.items():
                # 點擊輸入框
                await self.click_element(page, selector)
                
                # 輸入文本
                await self.type_text(page, selector, value)
                
                # 添加隨機延遲
                delay = random.uniform(
                    self.behavior_config["form_delay"]["min"],
                    self.behavior_config["form_delay"]["max"]
                )
                await page.wait_for_timeout(int(delay * 1000))
            
            logger.debug(f"已填寫表單: {form_data}")
        except Exception as e:
            logger.error(f"填寫表單時發生錯誤: {str(e)}")
            raise AntiDetectionException(f"填寫表單失敗: {str(e)}") 