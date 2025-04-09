#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
人類行為模擬

此模組提供人類行為模擬的功能，包括：
1. 鼠標移動
2. 點擊操作
3. 滾動操作
4. 文本輸入
"""

import logging
from typing import Dict, Any, List, Tuple, Optional
import random
import time
import math

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from .base_error import BaseError, handle_error, retry_on_error
from .configs.human_behavior_config import HumanBehaviorConfig

class HumanBehaviorError(BaseError):
    """人類行為錯誤"""
    pass

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
    """人類行為模擬器"""
    
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化人類行為模擬器
        
        Args:
            config: 配置字典
            logger: 日誌記錄器
        """
        self.logger = logger or logging.getLogger(__name__)
        self.config = HumanBehaviorConfig.from_dict(config or {})
        if not self.config.validate():
            raise HumanBehaviorError("無效的人類行為配置")
        
        self.behavior_history: List[HumanBehaviorResult] = []
        self.behavior_stats: Dict[str, Dict[str, int]] = {}
    
    @handle_error
    def move_to_element(
        self,
        driver: WebDriver,
        element: WebElement,
        speed: Optional[float] = None
    ) -> HumanBehaviorResult:
        """
        移動到元素
        
        Args:
            driver: WebDriver實例
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
        actions = ActionChains(driver)
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
    
    @handle_error
    def click_element(
        self,
        driver: WebDriver,
        element: WebElement,
        click_type: str = "left"
    ) -> HumanBehaviorResult:
        """
        點擊元素
        
        Args:
            driver: WebDriver實例
            element: 目標元素
            click_type: 點擊類型（left/right/double）
            
        Returns:
            行為結果
        """
        # 移動到元素
        self.move_to_element(driver, element)
        
        # 執行點擊
        actions = ActionChains(driver)
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
    
    @handle_error
    def scroll_to_element(
        self,
        driver: WebDriver,
        element: WebElement,
        speed: Optional[float] = None
    ) -> HumanBehaviorResult:
        """
        滾動到元素
        
        Args:
            driver: WebDriver實例
            element: 目標元素
            speed: 滾動速度（像素/秒）
            
        Returns:
            行為結果
        """
        # 獲取元素位置
        location = element.location
        
        # 生成滾動軌跡
        points = self._generate_scroll_trajectory(
            start_y=driver.execute_script("return window.pageYOffset;"),
            end_y=location["y"]
        )
        
        # 執行滾動
        for y in points:
            driver.execute_script(f"window.scrollTo(0, {y});")
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
    
    @handle_error
    def type_text(
        self,
        driver: WebDriver,
        element: WebElement,
        text: str,
        speed: Optional[float] = None
    ) -> HumanBehaviorResult:
        """
        輸入文本
        
        Args:
            driver: WebDriver實例
            element: 目標元素
            text: 要輸入的文本
            speed: 輸入速度（字符/秒）
            
        Returns:
            行為結果
        """
        # 移動到元素並點擊
        self.move_to_element(driver, element)
        self.click_element(driver, element)
        
        # 執行輸入
        actions = ActionChains(driver)
        for char in text:
            actions.send_keys(char)
            actions.pause(random.uniform(0.05, 0.2))
        
        actions.perform()
        
        # 返回結果
        return HumanBehaviorResult(
            success=True,
            action_type="type",
            target_element=element,
            details={"text": text}
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

    def apply_stealth_mode(self, driver: WebDriver) -> None:
        """應用隱身模式"""
        try:
            # 注入腳本
            inject_stealth_script(driver)
            
            # 應用配置
            config = self.config.to_dict()
            driver.execute_script("applyStealthMode(arguments[0]);", config)
            
            self.logger.info("隱身模式應用成功")
        except Exception as e:
            self.logger.error(f"應用隱身模式失敗: {str(e)}")
            raise FingerprintError("應用隱身模式失敗") from e

def inject_stealth_script(driver):
    # 讀取配置文件
    with open('src/anti_detection/stealth_scripts/config.js', 'r') as f:
        config_script = f.read()
    
    # 讀取主腳本
    with open('src/anti_detection/stealth_scripts/browser_fp.js', 'r') as f:
        main_script = f.read()
    
    # 注入腳本
    driver.execute_script(config_script)
    driver.execute_script(main_script)