"""
人類行為模擬模組
提供隨機延遲和人類行為模擬功能
"""

import random
import time
import math
import logging
from typing import Dict, Any, List, Tuple, Optional
from selenium.webdriver import ActionChains
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from ..base_error import BaseError, handle_error, retry_on_error
from ..configs.human_behavior_config import HumanBehaviorConfig

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

class HumanBehavior:
    """人類行為模擬類"""
    
    def __init__(
        self,
        driver: WebDriver,
        config: Optional[Dict[str, Any]] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化
        
        Args:
            driver: WebDriver 實例
            config: 配置字典
            logger: 日誌記錄器
        """
        self.driver = driver
        self.actions = ActionChains(driver)
        self.logger = logger or logging.getLogger(__name__)
        self.config = HumanBehaviorConfig.from_dict(config or {})
        if not self.config.validate():
            raise HumanBehaviorError("無效的人類行為配置")
        
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
    
    @handle_error
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
    
    @handle_error
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
    
    @handle_error
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