#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
人類行為模擬管理器模組

此模組提供統一的人類行為模擬功能，包括：
1. 滑鼠移動與點擊
2. 鍵盤輸入
3. 頁面滾動
4. 延遲控制
5. 行為歷史記錄
"""

import time
import random
import math
import json
from typing import Dict, Any, List, Tuple, Optional, Union
from datetime import datetime
from dataclasses import dataclass
from selenium.webdriver import ActionChains
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import (
    ElementNotVisibleException,
    ElementNotInteractableException,
    StaleElementReferenceException
)

from ..base_manager import BaseManager
from ..base_error import AntiDetectionError, handle_error

@dataclass
class DelayConfig:
    """延遲配置"""
    min: float
    max: float
    
    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> 'DelayConfig':
        return cls(
            min=data.get('min', 0.1),
            max=data.get('max', 0.3)
        )

@dataclass
class MouseConfig:
    """滑鼠配置"""
    enabled: bool = True
    movement_speed: DelayConfig = DelayConfig(0.5, 2.0)
    movement_delay: DelayConfig = DelayConfig(0.1, 0.3)
    click_delay: DelayConfig = DelayConfig(0.1, 0.5)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MouseConfig':
        return cls(
            enabled=data.get('enabled', True),
            movement_speed=DelayConfig.from_dict(data.get('movement_speed', {})),
            movement_delay=DelayConfig.from_dict(data.get('movement_delay', {})),
            click_delay=DelayConfig.from_dict(data.get('click_delay', {}))
        )

@dataclass
class KeyboardConfig:
    """鍵盤配置"""
    enabled: bool = True
    typing_speed: DelayConfig = DelayConfig(0.05, 0.2)
    typing_delay: DelayConfig = DelayConfig(0.1, 0.3)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KeyboardConfig':
        return cls(
            enabled=data.get('enabled', True),
            typing_speed=DelayConfig.from_dict(data.get('typing_speed', {})),
            typing_delay=DelayConfig.from_dict(data.get('typing_delay', {}))
        )

@dataclass
class ScrollConfig:
    """滾動配置"""
    enabled: bool = True
    scroll_speed: DelayConfig = DelayConfig(0.5, 2.0)
    scroll_delay: DelayConfig = DelayConfig(0.1, 0.3)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ScrollConfig':
        return cls(
            enabled=data.get('enabled', True),
            scroll_speed=DelayConfig.from_dict(data.get('scroll_speed', {})),
            scroll_delay=DelayConfig.from_dict(data.get('scroll_delay', {}))
        )

class BehaviorResult:
    """人類行為結果類"""
    
    def __init__(
        self,
        success: bool,
        action_type: str,
        target_element: Optional[WebElement] = None,
        details: Optional[Dict[str, Any]] = None,
        timestamp: Optional[float] = None
    ):
        """
        初始化行為結果
        
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
        self.details = details or {}
        self.timestamp = timestamp or time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        轉換為字典
        
        Returns:
            Dict[str, Any]: 結果字典
        """
        return {
            'success': self.success,
            'action_type': self.action_type,
            'target_element': self.target_element.id if self.target_element else None,
            'details': self.details,
            'timestamp': self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BehaviorResult':
        """
        從字典創建結果
        
        Args:
            data: 結果字典
            
        Returns:
            BehaviorResult: 結果實例
        """
        return cls(
            success=data['success'],
            action_type=data['action_type'],
            details=data.get('details'),
            timestamp=data.get('timestamp')
        )
    
    def __str__(self) -> str:
        """字符串表示"""
        status = "成功" if self.success else "失敗"
        return f"行為結果[{self.action_type}]: {status}"
    
    def __repr__(self) -> str:
        """詳細表示"""
        return (
            f"BehaviorResult("
            f"success={self.success}, "
            f"action_type='{self.action_type}', "
            f"target_element={self.target_element.id if self.target_element else None}, "
            f"details={self.details}, "
            f"timestamp={self.timestamp}"
            f")"
        )

class BehaviorManager(BaseManager):
    """人類行為管理器類"""
    
    def __init__(self, driver: WebDriver, config: Optional[Dict] = None):
        """
        初始化人類行為管理器
        
        Args:
            driver: WebDriver 實例
            config: 配置字典
        """
        super().__init__(driver, config)
        self.behavior_history: List[BehaviorResult] = []
        self._init_config()
        
    def _init_config(self) -> None:
        """初始化配置"""
        if not self.config:
            self.config = {
                'mouse': {
                    'enabled': True,
                    'movement_speed': {'min': 0.5, 'max': 2.0},
                    'movement_delay': {'min': 0.1, 'max': 0.3},
                    'click_delay': {'min': 0.1, 'max': 0.5}
                },
                'keyboard': {
                    'enabled': True,
                    'typing_speed': {'min': 0.05, 'max': 0.2},
                    'typing_delay': {'min': 0.1, 'max': 0.3}
                },
                'scroll': {
                    'enabled': True,
                    'scroll_speed': {'min': 0.5, 'max': 2.0},
                    'scroll_delay': {'min': 0.1, 'max': 0.3}
                },
                'delay': {
                    'page_load': {'min': 2.0, 'max': 5.0},
                    'between_actions': {'min': 1.0, 'max': 3.0},
                    'before_click': {'min': 0.5, 'max': 2.0}
                }
            }
            
        # 初始化配置對象
        self.mouse_config = MouseConfig.from_dict(self.config.get('mouse', {}))
        self.keyboard_config = KeyboardConfig.from_dict(self.config.get('keyboard', {}))
        self.scroll_config = ScrollConfig.from_dict(self.config.get('scroll', {}))
        
        # 初始化延遲配置
        self.delay_config = {
            'page_load': DelayConfig.from_dict(
                self.config.get('delay', {}).get('page_load', {'min': 2.0, 'max': 5.0})
            ),
            'between_actions': DelayConfig.from_dict(
                self.config.get('delay', {}).get('between_actions', {'min': 1.0, 'max': 3.0})
            ),
            'before_click': DelayConfig.from_dict(
                self.config.get('delay', {}).get('before_click', {'min': 0.5, 'max': 2.0})
            )
        }
        
    @handle_error()
    def setup(self) -> None:
        """設置行為管理器"""
        if not self._validate_config():
            raise AntiDetectionError("無效的行為配置")
        self.logger.info("行為管理器初始化完成")
        
    @handle_error()
    def cleanup(self) -> None:
        """清理行為管理器"""
        self.behavior_history.clear()
        self.logger.info("行為管理器清理完成")
        
    def _validate_config(self) -> bool:
        """
        驗證配置
        
        Returns:
            bool: 是否有效
        """
        try:
            # 檢查延遲配置
            for delay_config in self.delay_config.values():
                if delay_config.min > delay_config.max:
                    return False
            
            # 檢查滑鼠配置
            if self.mouse_config.movement_speed.min > self.mouse_config.movement_speed.max:
                return False
            if self.mouse_config.movement_delay.min > self.mouse_config.movement_delay.max:
                return False
            if self.mouse_config.click_delay.min > self.mouse_config.click_delay.max:
                return False
            
            # 檢查鍵盤配置
            if self.keyboard_config.typing_speed.min > self.keyboard_config.typing_speed.max:
                return False
            if self.keyboard_config.typing_delay.min > self.keyboard_config.typing_delay.max:
                return False
            
            # 檢查滾動配置
            if self.scroll_config.scroll_speed.min > self.scroll_config.scroll_speed.max:
                return False
            if self.scroll_config.scroll_delay.min > self.scroll_config.scroll_delay.max:
                return False
            
            return True
            
        except Exception:
            return False
            
    @handle_error()
    def move_to_element(
        self,
        element: WebElement,
        use_bezier: bool = True,
        random_offset: bool = True
    ) -> BehaviorResult:
        """
        移動到元素
        
        Args:
            element: 目標元素
            use_bezier: 是否使用貝塞爾曲線
            random_offset: 是否添加隨機偏移
            
        Returns:
            行為結果
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
    def _load_config(self) -> None:
        """加載配置"""
        if not self.config:
            self.config = {
                'mouse_speed': {
                    'min': 0.1,  # 最小移動速度（秒）
                    'max': 0.5   # 最大移動速度（秒）
                },
                'click_delay': {
                    'min': 0.1,  # 最小點擊延遲（秒）
                    'max': 0.3   # 最大點擊延遲（秒）
                },
                'scroll_speed': {
                    'min': 0.1,  # 最小滾動速度（秒）
                    'max': 0.5   # 最大滾動速度（秒）
                },
                'typing_speed': {
                    'min': 0.05,  # 最小打字速度（秒）
                    'max': 0.2    # 最大打字速度（秒）
                },
                'form_fill_delay': {
                    'min': 0.5,  # 最小表單填寫延遲（秒）
                    'max': 2.0   # 最大表單填寫延遲（秒）
                },
                'human_like': True,  # 是否使用人性化行為
                'random_delays': True,  # 是否使用隨機延遲
                'mouse_trail': True,  # 是否使用鼠標軌跡
                'scroll_pattern': 'natural',  # natural, smooth, jump
                'typing_pattern': 'natural',  # natural, fast, slow
                'form_fill_pattern': 'natural'  # natural, fast, slow
            }
            
    @handle_error()
    def _reset_position(self) -> None:
        """重置位置"""
        self.current_position = (0, 0)
        
    @handle_error()
    def _add_to_history(self, behavior: Dict[str, Any]) -> None:
        """
        添加行為到歷史
        
        Args:
            behavior: 行為字典
        """
        self.behavior_history.append({
            'timestamp': time.time(),
            'behavior': behavior
        })
        
        # 限制歷史記錄大小
        if len(self.behavior_history) > 100:
            self.behavior_history.pop(0)
            
    @handle_error()
    def _get_random_delay(self, min_delay: float, max_delay: float) -> float:
        """
        獲取隨機延遲
        
        Args:
            min_delay: 最小延遲
            max_delay: 最大延遲
            
        Returns:
            隨機延遲
        """
        if self.config.get('random_delays', True):
            return random.uniform(min_delay, max_delay)
        return (min_delay + max_delay) / 2
        
    @handle_error()
    def _move_to_element(self, element: WebElement) -> None:
        """
        移動到元素
        
        Args:
            element: 目標元素
        """
        try:
            # 獲取元素位置
            location = element.location
            size = element.size
            
            # 計算目標位置（元素中心）
            target_x = location['x'] + size['width'] / 2
            target_y = location['y'] + size['height'] / 2
            
            # 計算當前位置到目標位置的路徑
            path = self._calculate_path(
                self.current_position,
                (target_x, target_y)
            )
            
            # 移動鼠標
            for point in path:
                self.action_chains.move_by_offset(
                    point[0] - self.current_position[0],
                    point[1] - self.current_position[1]
                )
                self.current_position = point
                
                # 添加延遲
                delay = self._get_random_delay(
                    self.config['mouse_speed']['min'],
                    self.config['mouse_speed']['max']
                )
                time.sleep(delay)
                
            self.action_chains.perform()
            self._add_to_history({
                'type': 'mouse_move',
                'target': {
                    'x': target_x,
                    'y': target_y
                },
                'path': path
            })
        except Exception as e:
            self.logger.error(f"移動到元素失敗: {str(e)}")
            raise
            
    @handle_error()
    def _calculate_path(self, start: Tuple[float, float], end: Tuple[float, float]) -> List[Tuple[float, float]]:
        """
        計算鼠標移動路徑
        
        Args:
            start: 起始位置
            end: 目標位置
            
        Returns:
            路徑點列表
        """
        if not self.config.get('mouse_trail', True):
            return [end]
            
        # 使用貝塞爾曲線生成路徑
        control_points = [
            start,
            (
                start[0] + (end[0] - start[0]) * random.uniform(0.3, 0.7),
                start[1] + (end[1] - start[1]) * random.uniform(0.3, 0.7)
            ),
            end
        ]
        
        # 生成路徑點
        path = []
        steps = 20
        for i in range(steps + 1):
            t = i / steps
            x = (1 - t) ** 2 * control_points[0][0] + 2 * (1 - t) * t * control_points[1][0] + t ** 2 * control_points[2][0]
            y = (1 - t) ** 2 * control_points[0][1] + 2 * (1 - t) * t * control_points[1][1] + t ** 2 * control_points[2][1]
            path.append((x, y))
            
        return path
        
    @handle_error()
    def click(self, element: WebElement) -> None:
        """
        點擊元素
        
        Args:
            element: 目標元素
        """
        try:
            # 移動到元素
            self._move_to_element(element)
            
            # 添加延遲
            delay = self._get_random_delay(
                self.config['click_delay']['min'],
                self.config['click_delay']['max']
            )
            time.sleep(delay)
            
            # 點擊元素
            self.action_chains.click().perform()
            
            self._add_to_history({
                'type': 'click',
                'target': {
                    'x': self.current_position[0],
                    'y': self.current_position[1]
                }
            })
        except Exception as e:
            self.logger.error(f"點擊元素失敗: {str(e)}")
            raise
            
    @handle_error()
    def double_click(self, element: WebElement) -> None:
        """
        雙擊元素
        
        Args:
            element: 目標元素
        """
        try:
            # 移動到元素
            self._move_to_element(element)
            
            # 添加延遲
            delay = self._get_random_delay(
                self.config['click_delay']['min'],
                self.config['click_delay']['max']
            )
            time.sleep(delay)
            
            # 雙擊元素
            self.action_chains.double_click().perform()
            
            self._add_to_history({
                'type': 'double_click',
                'target': {
                    'x': self.current_position[0],
                    'y': self.current_position[1]
                }
            })
        except Exception as e:
            self.logger.error(f"雙擊元素失敗: {str(e)}")
            raise
            
    @handle_error()
    def right_click(self, element: WebElement) -> None:
        """
        右鍵點擊元素
        
        Args:
            element: 目標元素
        """
        try:
            # 移動到元素
            self._move_to_element(element)
            
            # 添加延遲
            delay = self._get_random_delay(
                self.config['click_delay']['min'],
                self.config['click_delay']['max']
            )
            time.sleep(delay)
            
            # 右鍵點擊元素
            self.action_chains.context_click().perform()
            
            self._add_to_history({
                'type': 'right_click',
                'target': {
                    'x': self.current_position[0],
                    'y': self.current_position[1]
                }
            })
        except Exception as e:
            self.logger.error(f"右鍵點擊元素失敗: {str(e)}")
            raise
            
    @handle_error()
    def hover(self, element: WebElement) -> None:
        """
        懸停元素
        
        Args:
            element: 目標元素
        """
        try:
            # 移動到元素
            self._move_to_element(element)
            
            self._add_to_history({
                'type': 'hover',
                'target': {
                    'x': self.current_position[0],
                    'y': self.current_position[1]
                }
            })
        except Exception as e:
            self.logger.error(f"懸停元素失敗: {str(e)}")
            raise
            
    @handle_error()
    def drag_and_drop(self, source: WebElement, target: WebElement) -> None:
        """
        拖放元素
        
        Args:
            source: 源元素
            target: 目標元素
        """
        try:
            # 移動到源元素
            self._move_to_element(source)
            
            # 按下鼠標
            self.action_chains.click_and_hold().perform()
            
            # 移動到目標元素
            self._move_to_element(target)
            
            # 釋放鼠標
            self.action_chains.release().perform()
            
            self._add_to_history({
                'type': 'drag_and_drop',
                'source': {
                    'x': source.location['x'] + source.size['width'] / 2,
                    'y': source.location['y'] + source.size['height'] / 2
                },
                'target': {
                    'x': target.location['x'] + target.size['width'] / 2,
                    'y': target.location['y'] + target.size['height'] / 2
                }
            })
        except Exception as e:
            self.logger.error(f"拖放元素失敗: {str(e)}")
            raise
            
    @handle_error()
    def scroll_to(self, element: WebElement) -> None:
        """
        滾動到元素
        
        Args:
            element: 目標元素
        """
        try:
            # 獲取元素位置
            location = element.location
            size = element.size
            
            # 計算目標位置（元素中心）
            target_y = location['y'] + size['height'] / 2
            
            # 獲取當前滾動位置
            current_y = self.driver.execute_script("return window.pageYOffset;")
            
            # 計算滾動距離
            distance = target_y - current_y
            
            # 根據滾動模式生成滾動路徑
            if self.config['scroll_pattern'] == 'natural':
                # 自然滾動
                steps = abs(int(distance / 100)) + 1
                for i in range(steps):
                    step = distance / steps
                    self.driver.execute_script(f"window.scrollBy(0, {step});")
                    
                    # 添加延遲
                    delay = self._get_random_delay(
                        self.config['scroll_speed']['min'],
                        self.config['scroll_speed']['max']
                    )
                    time.sleep(delay)
            elif self.config['scroll_pattern'] == 'smooth':
                # 平滑滾動
                self.driver.execute_script(f"window.scrollTo({{top: {target_y}, behavior: 'smooth'}});")
                
                # 等待滾動完成
                time.sleep(abs(distance) / 1000)
            else:
                # 跳躍滾動
                self.driver.execute_script(f"window.scrollTo(0, {target_y});")
                
            self._add_to_history({
                'type': 'scroll',
                'target': {
                    'y': target_y
                },
                'pattern': self.config['scroll_pattern']
            })
        except Exception as e:
            self.logger.error(f"滾動到元素失敗: {str(e)}")
            raise
            
    @handle_error()
    def type_text(self, element: WebElement, text: str) -> None:
        """
        輸入文本
        
        Args:
            element: 目標元素
            text: 要輸入的文本
        """
        try:
            # 移動到元素
            self._move_to_element(element)
            
            # 點擊元素
            self.click(element)
            
            # 根據輸入模式生成輸入路徑
            if self.config['typing_pattern'] == 'natural':
                # 自然輸入
                for char in text:
                    # 輸入字符
                    self.action_chains.send_keys(char).perform()
                    
                    # 添加延遲
                    delay = self._get_random_delay(
                        self.config['typing_speed']['min'],
                        self.config['typing_speed']['max']
                    )
                    time.sleep(delay)
                    
                    # 隨機添加錯誤和修正
                    if random.random() < 0.05:
                        # 輸入錯誤字符
                        wrong_char = random.choice('abcdefghijklmnopqrstuvwxyz')
                        self.action_chains.send_keys(wrong_char).perform()
                        time.sleep(delay)
                        
                        # 刪除錯誤字符
                        self.action_chains.send_keys(Keys.BACKSPACE).perform()
                        time.sleep(delay)
            elif self.config['typing_pattern'] == 'fast':
                # 快速輸入
                self.action_chains.send_keys(text).perform()
            else:
                # 慢速輸入
                for char in text:
                    self.action_chains.send_keys(char).perform()
                    time.sleep(self.config['typing_speed']['max'])
                    
            self._add_to_history({
                'type': 'type_text',
                'text': text,
                'pattern': self.config['typing_pattern']
            })
        except Exception as e:
            self.logger.error(f"輸入文本失敗: {str(e)}")
            raise
            
    @handle_error()
    def fill_form(self, form_data: Dict[str, str]) -> None:
        """
        填寫表單
        
        Args:
            form_data: 表單數據字典
        """
        try:
            for field_name, value in form_data.items():
                # 查找表單字段
                element = self.driver.find_element_by_name(field_name)
                
                # 滾動到字段
                self.scroll_to(element)
                
                # 添加延遲
                delay = self._get_random_delay(
                    self.config['form_fill_delay']['min'],
                    self.config['form_fill_delay']['max']
                )
                time.sleep(delay)
                
                # 輸入值
                self.type_text(element, value)
                
            self._add_to_history({
                'type': 'fill_form',
                'form_data': form_data,
                'pattern': self.config['form_fill_pattern']
            })
        except Exception as e:
            self.logger.error(f"填寫表單失敗: {str(e)}")
            raise
            
    @handle_error()
    def get_behavior_history(self) -> List[Dict[str, Any]]:
        """
        獲取行為歷史
        
        Returns:
            行為歷史
        """
        return self.behavior_history.copy()
        
    @handle_error()
    def save_behavior_history(self, file_path: str) -> None:
        """
        保存行為歷史到文件
        
        Args:
            file_path: 文件路徑
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'behavior_history': self.behavior_history,
                    'config': self.config
                }, f, ensure_ascii=False, indent=2)
            self.logger.info(f"行為歷史已保存到: {file_path}")
        except Exception as e:
            self.logger.error(f"保存行為歷史失敗: {str(e)}")
            raise
            
    @handle_error()
    def load_behavior_history(self, file_path: str) -> None:
        """
        從文件加載行為歷史
        
        Args:
            file_path: 文件路徑
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            self.behavior_history = data.get('behavior_history', [])
            self.config.update(data.get('config', {}))
            
            self.logger.info(f"已從 {file_path} 加載行為歷史")
        except Exception as e:
            self.logger.error(f"加載行為歷史失敗: {str(e)}")
            raise 