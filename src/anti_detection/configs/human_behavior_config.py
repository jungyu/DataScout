#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
人類行為配置

此模組提供人類行為相關的配置類，包括：
1. HumanBehaviorConfig：人類行為主配置
2. MouseConfig：滑鼠行為配置
3. KeyboardConfig：鍵盤行為配置
4. ScrollConfig：滾動行為配置
5. TimingConfig：時間行為配置
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class MouseConfig:
    """滑鼠行為配置"""
    move_speed: Tuple[float, float] = (0.5, 2.0)  # 移動速度範圍（秒）
    click_duration: Tuple[float, float] = (0.05, 0.15)  # 點擊持續時間範圍（秒）
    double_click_interval: Tuple[float, float] = (0.2, 0.4)  # 雙擊間隔範圍（秒）
    move_pattern: str = "bezier"  # 移動模式：linear, bezier, natural
    click_pattern: str = "natural"  # 點擊模式：instant, natural
    hover_duration: Tuple[float, float] = (0.5, 2.0)  # 懸停時間範圍（秒）
    drag_speed: Tuple[float, float] = (0.3, 1.0)  # 拖拽速度範圍（秒）
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "move_speed": self.move_speed,
            "click_duration": self.click_duration,
            "double_click_interval": self.double_click_interval,
            "move_pattern": self.move_pattern,
            "click_pattern": self.click_pattern,
            "hover_duration": self.hover_duration,
            "drag_speed": self.drag_speed
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MouseConfig':
        """從字典創建實例"""
        return cls(
            move_speed=tuple(data.get("move_speed", (0.5, 2.0))),
            click_duration=tuple(data.get("click_duration", (0.05, 0.15))),
            double_click_interval=tuple(data.get("double_click_interval", (0.2, 0.4))),
            move_pattern=data.get("move_pattern", "bezier"),
            click_pattern=data.get("click_pattern", "natural"),
            hover_duration=tuple(data.get("hover_duration", (0.5, 2.0))),
            drag_speed=tuple(data.get("drag_speed", (0.3, 1.0)))
        )

@dataclass
class KeyboardConfig:
    """鍵盤行為配置"""
    type_speed: Tuple[float, float] = (0.05, 0.2)  # 輸入速度範圍（秒/字符）
    type_pattern: str = "natural"  # 輸入模式：instant, natural
    key_press_duration: Tuple[float, float] = (0.05, 0.15)  # 按鍵持續時間範圍（秒）
    key_interval: Tuple[float, float] = (0.1, 0.3)  # 按鍵間隔範圍（秒）
    typo_probability: float = 0.05  #  typo 機率
    correction_delay: Tuple[float, float] = (0.5, 1.5)  # 修正延遲範圍（秒）
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "type_speed": self.type_speed,
            "type_pattern": self.type_pattern,
            "key_press_duration": self.key_press_duration,
            "key_interval": self.key_interval,
            "typo_probability": self.typo_probability,
            "correction_delay": self.correction_delay
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'KeyboardConfig':
        """從字典創建實例"""
        return cls(
            type_speed=tuple(data.get("type_speed", (0.05, 0.2))),
            type_pattern=data.get("type_pattern", "natural"),
            key_press_duration=tuple(data.get("key_press_duration", (0.05, 0.15))),
            key_interval=tuple(data.get("key_interval", (0.1, 0.3))),
            typo_probability=data.get("typo_probability", 0.05),
            correction_delay=tuple(data.get("correction_delay", (0.5, 1.5)))
        )

@dataclass
class ScrollConfig:
    """滾動行為配置"""
    scroll_speed: Tuple[float, float] = (0.3, 1.0)  # 滾動速度範圍（秒）
    scroll_pattern: str = "natural"  # 滾動模式：instant, natural
    scroll_amount: Tuple[int, int] = (100, 300)  # 滾動量範圍（像素）
    scroll_interval: Tuple[float, float] = (0.5, 2.0)  # 滾動間隔範圍（秒）
    smooth_scroll: bool = True  # 是否使用平滑滾動
    scroll_easing: str = "easeInOutQuad"  # 滾動緩動函數
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "scroll_speed": self.scroll_speed,
            "scroll_pattern": self.scroll_pattern,
            "scroll_amount": self.scroll_amount,
            "scroll_interval": self.scroll_interval,
            "smooth_scroll": self.smooth_scroll,
            "scroll_easing": self.scroll_easing
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ScrollConfig':
        """從字典創建實例"""
        return cls(
            scroll_speed=tuple(data.get("scroll_speed", (0.3, 1.0))),
            scroll_pattern=data.get("scroll_pattern", "natural"),
            scroll_amount=tuple(data.get("scroll_amount", (100, 300))),
            scroll_interval=tuple(data.get("scroll_interval", (0.5, 2.0))),
            smooth_scroll=data.get("smooth_scroll", True),
            scroll_easing=data.get("scroll_easing", "easeInOutQuad")
        )

@dataclass
class TimingConfig:
    """時間行為配置"""
    action_interval: Tuple[float, float] = (1.0, 3.0)  # 動作間隔範圍（秒）
    page_load_wait: Tuple[float, float] = (2.0, 5.0)  # 頁面加載等待範圍（秒）
    element_wait: Tuple[float, float] = (0.5, 2.0)  # 元素等待範圍（秒）
    random_delay: Tuple[float, float] = (0.1, 0.5)  # 隨機延遲範圍（秒）
    session_duration: Tuple[float, float] = (300, 1800)  # 會話持續時間範圍（秒）
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "action_interval": self.action_interval,
            "page_load_wait": self.page_load_wait,
            "element_wait": self.element_wait,
            "random_delay": self.random_delay,
            "session_duration": self.session_duration
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TimingConfig':
        """從字典創建實例"""
        return cls(
            action_interval=tuple(data.get("action_interval", (1.0, 3.0))),
            page_load_wait=tuple(data.get("page_load_wait", (2.0, 5.0))),
            element_wait=tuple(data.get("element_wait", (0.5, 2.0))),
            random_delay=tuple(data.get("random_delay", (0.1, 0.5))),
            session_duration=tuple(data.get("session_duration", (300, 1800)))
        )

@dataclass
class HumanBehaviorConfig:
    """人類行為配置"""
    id: str
    mouse_config: MouseConfig = field(default_factory=MouseConfig)  # 滑鼠配置
    keyboard_config: KeyboardConfig = field(default_factory=KeyboardConfig)  # 鍵盤配置
    scroll_config: ScrollConfig = field(default_factory=ScrollConfig)  # 滾動配置
    timing_config: TimingConfig = field(default_factory=TimingConfig)  # 時間配置
    behavior_pattern: str = "natural"  # 行為模式：natural, aggressive, cautious
    randomize_behavior: bool = True  # 是否隨機化行為
    session_pattern: str = "normal"  # 會話模式：normal, quick, thorough
    created_at: datetime = field(default_factory=datetime.now)  # 創建時間
    updated_at: datetime = field(default_factory=datetime.now)  # 更新時間
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "id": self.id,
            "mouse_config": self.mouse_config.to_dict(),
            "keyboard_config": self.keyboard_config.to_dict(),
            "scroll_config": self.scroll_config.to_dict(),
            "timing_config": self.timing_config.to_dict(),
            "behavior_pattern": self.behavior_pattern,
            "randomize_behavior": self.randomize_behavior,
            "session_pattern": self.session_pattern,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HumanBehaviorConfig':
        """從字典創建實例"""
        if 'created_at' in data:
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if 'updated_at' in data:
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
            
        return cls(
            id=data.get("id"),
            mouse_config=MouseConfig.from_dict(data.get("mouse_config", {})),
            keyboard_config=KeyboardConfig.from_dict(data.get("keyboard_config", {})),
            scroll_config=ScrollConfig.from_dict(data.get("scroll_config", {})),
            timing_config=TimingConfig.from_dict(data.get("timing_config", {})),
            behavior_pattern=data.get("behavior_pattern", "natural"),
            randomize_behavior=data.get("randomize_behavior", True),
            session_pattern=data.get("session_pattern", "normal"),
            created_at=data.get('created_at', datetime.now()),
            updated_at=data.get('updated_at', datetime.now())
        ) 