#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
人類行為模擬器

此模組提供模擬人類行為的功能，包括：
1. 滑鼠移動模擬
2. 點擊行為模擬
3. 滾動行為模擬
4. 輸入行為模擬
"""

import os
import json
import time
import random
import math
import logging
from typing import Dict, Any, List, Tuple, Optional, Union
from datetime import datetime
from pathlib import Path
from selenium.webdriver import ActionChains
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import (
    ElementNotVisibleException,
    ElementNotInteractableException,
    StaleElementReferenceException
)

from ..base_error import BaseError
from src.core.utils.error_handler import retry_on_error, handle_exception
from ..configs.human_behavior_config import HumanBehaviorConfig

class HumanBehaviorError(BaseError):
    """人類行為模擬錯誤"""
    def __init__(self, message: str, code: int = 4000, details: Optional[Dict[str, Any]] = None):
        super().__init__(code=code, message=message, details=details)

class HumanBehaviorResult:
    """人類行為結果"""
    
    def __init__(
        self,
        success: bool,
        action_type: str,
        target_element: Optional[WebElement],
        details: Dict[str, Any],
        timestamp: Optional[float] = None
    ):
        """
        初始化人類行為結果
        
        Args:
            success: 是否成功
            action_type: 行為類型
            target_element: 目標元素
            details: 詳細信息
            timestamp: 時間戳
        """
        self.success = success
        self.action_type = action_type
        self.target_element = target_element
        self.details = details
        self.timestamp = timestamp or time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "success": self.success,
            "action_type": self.action_type,
            "target_element": self.target_element.id if self.target_element else None,
            "details": self.details,
            "timestamp": self.timestamp
        }

class HumanBehaviorSimulator:
    """人類行為模擬器類"""
    
    def __init__(
        self,
        id: str,
        driver: WebDriver,
        config: Optional[Dict[str, Any]] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化人類行為模擬器
        
        Args:
            id: 唯一標識符
            driver: WebDriver實例
            config: 配置字典
            logger: 日誌記錄器
        """
        self.id = id
        self.driver = driver
        self.logger = logger or logging.getLogger(__name__)
        
        # 確保配置包含 id
        if config is None:
            config = {}
        if "id" not in config:
            config["id"] = self.id
            
        try:
            self.config = HumanBehaviorConfig.from_dict(config)
            if not self.config.validate():
                raise HumanBehaviorError("無效的人類行為配置")
        except ValueError as e:
            # 使用預設配置
            self.config = HumanBehaviorConfig(id=self.id)
            self.logger.warning(f"使用預設配置: {str(e)}")
        
        # 移動參數
        self.min_move_time = 0.5
        self.max_move_time = 2.0
        self.move_points = 50
        
        # 點擊參數
        self.min_click_delay = 0.1
        self.max_click_delay = 0.3
        
        # 滾動參數
        self.min_scroll_delay = 0.5
        self.max_scroll_delay = 1.5
        self.scroll_step = 100
        
        # 輸入參數
        self.min_type_delay = 0.1
        self.max_type_delay = 0.3
        
        self.logger.info(f"人類行為模擬器 {self.id} 初始化完成")
    
    def move_to_element(self, element: WebElement, random_offset: bool = True) -> bool:
        """
        模擬人類移動滑鼠到元素
        
        Args:
            element: 目標元素
            random_offset: 是否添加隨機偏移
            
        Returns:
            是否成功
        """
        try:
            # 獲取元素位置和大小
            location = element.location
            size = element.size
            
            # 計算目標點
            target_x = location['x'] + size['width'] // 2
            target_y = location['y'] + size['height'] // 2
            
            # 添加隨機偏移
            if random_offset:
                offset_x = random.randint(-size['width'] // 4, size['width'] // 4)
                offset_y = random.randint(-size['height'] // 4, size['height'] // 4)
                target_x += offset_x
                target_y += offset_y
            
            # 生成貝塞爾曲線路徑
            current_x, current_y = self._get_current_mouse_position()
            path = self._generate_bezier_curve(
                (current_x, current_y),
                (target_x, target_y),
                self.move_points
            )
            
            # 執行移動
            move_time = random.uniform(self.min_move_time, self.max_move_time)
            step_time = move_time / len(path)
            
            actions = ActionChains(self.driver)
            for point in path:
                actions.move_by_offset(point[0] - current_x, point[1] - current_y)
                current_x, current_y = point
                time.sleep(step_time)
            
            actions.perform()
            return True
            
        except Exception as e:
            self.logger.error(f"移動到元素失敗: {str(e)}")
            return False
    
    def click_element(self, element: WebElement, double_click: bool = False) -> bool:
        """
        模擬人類點擊元素
        
        Args:
            element: 目標元素
            double_click: 是否雙擊
            
        Returns:
            是否成功
        """
        try:
            # 先移動到元素
            if not self.move_to_element(element):
                return False
            
            # 添加隨機延遲
            time.sleep(random.uniform(self.min_click_delay, self.max_click_delay))
            
            # 執行點擊
            actions = ActionChains(self.driver)
            if double_click:
                actions.double_click(element)
            else:
                actions.click(element)
            
            actions.perform()
            return True
            
        except Exception as e:
            self.logger.error(f"點擊元素失敗: {str(e)}")
            return False
    
    def scroll_to_element(self, element: WebElement, smooth: bool = True) -> bool:
        """
        模擬人類滾動到元素
        
        Args:
            element: 目標元素
            smooth: 是否平滑滾動
            
        Returns:
            是否成功
        """
        try:
            # 獲取元素位置
            location = element.location
            current_scroll = self.driver.execute_script("return window.pageYOffset;")
            target_scroll = location['y']
            
            if smooth:
                # 計算滾動步驟
                distance = target_scroll - current_scroll
                steps = abs(distance) // self.scroll_step
                
                # 執行平滑滾動
                for _ in range(steps):
                    if distance > 0:
                        current_scroll += self.scroll_step
                    else:
                        current_scroll -= self.scroll_step
                    
                    self.driver.execute_script(f"window.scrollTo(0, {current_scroll});")
                    time.sleep(random.uniform(self.min_scroll_delay, self.max_scroll_delay))
            
            # 最後滾動到精確位置
            self.driver.execute_script(f"window.scrollTo(0, {target_scroll});")
            return True
            
        except Exception as e:
            self.logger.error(f"滾動到元素失敗: {str(e)}")
            return False
    
    def type_text(self, element: WebElement, text: str, clear_first: bool = True) -> bool:
        """
        模擬人類輸入文字
        
        Args:
            element: 目標元素
            text: 要輸入的文字
            clear_first: 是否先清空
            
        Returns:
            是否成功
        """
        try:
            # 先點擊元素
            if not self.click_element(element):
                return False
            
            # 清空輸入框
            if clear_first:
                element.clear()
            
            # 模擬人類輸入
            for char in text:
                element.send_keys(char)
                time.sleep(random.uniform(self.min_type_delay, self.max_type_delay))
            
            return True
            
        except Exception as e:
            self.logger.error(f"輸入文字失敗: {str(e)}")
            return False
    
    def _get_current_mouse_position(self) -> Tuple[int, int]:
        """獲取當前滑鼠位置"""
        return self.driver.execute_script("""
            return [
                window.mouseX || window.event.clientX,
                window.mouseY || window.event.clientY
            ];
        """)
    
    def _generate_bezier_curve(
        self,
        start: Tuple[int, int],
        end: Tuple[int, int],
        points: int
    ) -> List[Tuple[int, int]]:
        """生成貝塞爾曲線路徑"""
        # 生成控制點
        control1 = (
            start[0] + (end[0] - start[0]) // 3,
            start[1] + random.randint(-100, 100)
        )
        control2 = (
            start[0] + 2 * (end[0] - start[0]) // 3,
            end[1] + random.randint(-100, 100)
        )
        
        # 生成路徑點
        path = []
        for i in range(points):
            t = i / (points - 1)
            x = (
                (1 - t) ** 3 * start[0] +
                3 * (1 - t) ** 2 * t * control1[0] +
                3 * (1 - t) * t ** 2 * control2[0] +
                t ** 3 * end[0]
            )
            y = (
                (1 - t) ** 3 * start[1] +
                3 * (1 - t) ** 2 * t * control1[1] +
                3 * (1 - t) * t ** 2 * control2[1] +
                t ** 3 * end[1]
            )
            path.append((int(x), int(y)))
        
        return path

class HumanBehavior:
    """人類行為模擬類"""
    
    def __init__(
        self,
        id: str,
        driver: WebDriver,
        config: Optional[Dict[str, Any]] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化人類行為模擬器
        
        Args:
            id: 唯一標識符
            driver: WebDriver實例
            config: 配置字典
            logger: 日誌記錄器
        """
        self.id = id
        self.driver = driver
        self.logger = logger or logging.getLogger(__name__)
        
        # 確保配置包含 id
        if config is None:
            config = {}
        if "id" not in config:
            config["id"] = self.id
            
        try:
            self.config = HumanBehaviorConfig.from_dict(config)
            if not self.config.validate():
                raise HumanBehaviorError("無效的人類行為配置")
        except ValueError as e:
            # 使用預設配置
            self.config = HumanBehaviorConfig(id=self.id)
            self.logger.warning(f"使用預設配置: {str(e)}")
        
        # 移動參數
        self.min_move_time = 0.5
        self.max_move_time = 2.0
        self.move_points = 50
        
        # 點擊參數
        self.min_click_delay = 0.1
        self.max_click_delay = 0.3
        
        # 滾動參數
        self.min_scroll_delay = 0.5
        self.max_scroll_delay = 1.5
        self.scroll_step = 100
        
        # 輸入參數
        self.min_type_delay = 0.1
        self.max_type_delay = 0.3
        
        self.logger.info(f"人類行為模擬器 {self.id} 初始化完成")
        
        self.behavior_history: List[HumanBehaviorResult] = []
        self.behavior_stats: Dict[str, Dict[str, int]] = {}
    
    def random_sleep(self, min_seconds: float = 1.0, max_seconds: float = 3.0) -> None:
        """
        隨機延遲
        
        Args:
            min_seconds: 最小延遲時間（秒）
            max_seconds: 最大延遲時間（秒）
        """
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    def random_scroll(self, min_scroll: int = 100, max_scroll: int = 500) -> None:
        """
        隨機滾動頁面
        
        Args:
            min_scroll: 最小滾動距離
            max_scroll: 最大滾動距離
        """
        scroll_amount = random.randint(min_scroll, max_scroll)
        self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
        self.random_sleep(0.5, 1.5)
    
    def human_click(self, element: WebElement, offset_range: Tuple[int, int] = (-5, 5)) -> None:
        """
        模擬人類點擊
        
        Args:
            element: 目標元素
            offset_range: 偏移範圍
        """
        # 移動到元素附近
        self.actions.move_to_element_with_offset(
            element,
            random.randint(*offset_range),
            random.randint(*offset_range)
        ).perform()
        
        # 短暫停頓
        self.random_sleep(0.1, 0.3)
        
        # 點擊
        element.click()
    
    def human_type(self, element: WebElement, text: str, min_delay: float = 0.1, max_delay: float = 0.3) -> None:
        """
        模擬人類輸入
        
        Args:
            element: 目標元素
            text: 要輸入的文字
            min_delay: 最小延遲時間（秒）
            max_delay: 最大延遲時間（秒）
        """
        # 點擊元素
        self.human_click(element)
        
        # 逐字符輸入
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(min_delay, max_delay))
    
    def random_mouse_movement(self, element: Optional[WebElement] = None) -> None:
        """
        隨機滑鼠移動
        
        Args:
            element: 目標元素（可選）
        """
        if element:
            # 移動到元素
            self.actions.move_to_element(element)
        else:
            # 隨機移動
            x = random.randint(0, 500)
            y = random.randint(0, 500)
            self.actions.move_by_offset(x, y)
        
        self.actions.perform()
        self.random_sleep(0.1, 0.3)
    
    def simulate_reading(self, min_seconds: float = 2.0, max_seconds: float = 5.0) -> None:
        """
        模擬閱讀行為
        
        Args:
            min_seconds: 最小閱讀時間（秒）
            max_seconds: 最大閱讀時間（秒）
        """
        # 隨機滾動
        for _ in range(random.randint(2, 5)):
            self.random_scroll()
        
        # 隨機停頓
        self.random_sleep(min_seconds, max_seconds)
    
    @handle_exception
    def move_to_element(
        self,
        element: WebElement,
        speed: Optional[float] = None
    ) -> HumanBehaviorResult:
        """
        移動到元素
        
        Args:
            element: 目標元素
            speed: 移動速度（像素/秒）
            
        Returns:
            行為結果
        """
        # 獲取元素位置
        location = element.location
        size = element.size
        
        # 計算目標位置
        target_x = location["x"] + size["width"] / 2
        target_y = location["y"] + size["height"] / 2
        
        # 生成軌跡點
        points = self._generate_mouse_trajectory(
            start_x=0,
            start_y=0,
            end_x=target_x,
            end_y=target_y
        )
        
        # 執行移動
        actions = ActionChains(self.driver)
        for x, y in points:
            actions.move_by_offset(x, y)
            actions.pause(random.uniform(0.01, 0.03))
        
        actions.perform()
        
        # 返回結果
        return HumanBehaviorResult(
            success=True,
            action_type="move",
            target_element=element,
            details={
                "start": (0, 0),
                "end": (target_x, target_y),
                "points": points
            }
        )
    
    @handle_exception
    def click_element(
        self,
        element: WebElement,
        click_type: str = "left"
    ) -> HumanBehaviorResult:
        """
        點擊元素
        
        Args:
            element: 目標元素
            click_type: 點擊類型（left/right/double）
            
        Returns:
            行為結果
        """
        # 移動到元素
        self.move_to_element(element)
        
        # 執行點擊
        actions = ActionChains(self.driver)
        if click_type == "left":
            actions.click()
        elif click_type == "right":
            actions.context_click()
        elif click_type == "double":
            actions.double_click()
        
        actions.perform()
        
        # 返回結果
        return HumanBehaviorResult(
            success=True,
            action_type=f"{click_type}_click",
            target_element=element,
            details={"click_type": click_type}
        )
    
    @handle_exception
    def scroll_to_element(
        self,
        element: WebElement,
        speed: Optional[float] = None
    ) -> HumanBehaviorResult:
        """
        滾動到元素
        
        Args:
            element: 目標元素
            speed: 滾動速度（像素/秒）
            
        Returns:
            行為結果
        """
        # 獲取元素位置
        location = element.location
        
        # 生成滾動軌跡
        points = self._generate_scroll_trajectory(
            start_y=self.driver.execute_script("return window.pageYOffset;"),
            end_y=location["y"]
        )
        
        # 執行滾動
        for y in points:
            self.driver.execute_script(f"window.scrollTo(0, {y});")
            time.sleep(random.uniform(0.01, 0.03))
        
        # 返回結果
        return HumanBehaviorResult(
            success=True,
            action_type="scroll",
            target_element=element,
            details={
                "start_y": points[0],
                "end_y": points[-1],
                "points": points
            }
        )
    
    def _generate_mouse_trajectory(
        self,
        start_x: float,
        start_y: float,
        end_x: float,
        end_y: float
    ) -> List[Tuple[float, float]]:
        """
        生成鼠標軌跡
        
        Args:
            start_x: 起始X坐標
            start_y: 起始Y坐標
            end_x: 結束X坐標
            end_y: 結束Y坐標
            
        Returns:
            軌跡點列表
        """
        points = []
        
        # 生成貝塞爾曲線控制點
        control_points = [
            (start_x, start_y),
            (
                start_x + (end_x - start_x) * random.uniform(0.2, 0.4),
                start_y + (end_y - start_y) * random.uniform(0.2, 0.4)
            ),
            (
                start_x + (end_x - start_x) * random.uniform(0.6, 0.8),
                start_y + (end_y - start_y) * random.uniform(0.6, 0.8)
            ),
            (end_x, end_y)
        ]
        
        # 生成軌跡點
        for t in range(0, 100, 5):
            t = t / 100
            x = (1-t)**3 * control_points[0][0] + \
                3*(1-t)**2 * t * control_points[1][0] + \
                3*(1-t) * t**2 * control_points[2][0] + \
                t**3 * control_points[3][0]
            y = (1-t)**3 * control_points[0][1] + \
                3*(1-t)**2 * t * control_points[1][1] + \
                3*(1-t) * t**2 * control_points[2][1] + \
                t**3 * control_points[3][1]
            points.append((x, y))
        
        return points
    
    def _generate_scroll_trajectory(
        self,
        start_y: float,
        end_y: float
    ) -> List[float]:
        """
        生成滾動軌跡
        
        Args:
            start_y: 起始Y坐標
            end_y: 結束Y坐標
            
        Returns:
            軌跡點列表
        """
        points = []
        
        # 計算總距離
        distance = end_y - start_y
        
        # 生成軌跡點
        for t in range(0, 100, 5):
            t = t / 100
            # 使用緩動函數
            y = start_y + distance * (1 - math.cos(t * math.pi / 2))
            points.append(y)
        
        return points
    
    def get_behavior_report(self) -> Dict[str, Any]:
        """獲取行為報告"""
        return {
            "total_behaviors": len(self.behavior_history),
            "success_rate": sum(1 for r in self.behavior_history if r.success) / len(self.behavior_history),
            "behavior_types": self.behavior_stats,
            "recent_behaviors": [r.to_dict() for r in self.behavior_history[-10:]]
        } 