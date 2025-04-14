#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
反檢測行為模組

提供以下功能：
1. 行為管理器
2. 鼠標行為
3. 鍵盤行為
4. 滾動行為
5. 表單行為
"""

from .behavior_manager import BehaviorManager
from .mouse_behavior import MouseBehavior
from .keyboard_behavior import KeyboardBehavior
from .scroll_behavior import ScrollBehavior
from .form_behavior import FormBehavior

__all__ = [
    'BehaviorManager',
    'MouseBehavior',
    'KeyboardBehavior',
    'ScrollBehavior',
    'FormBehavior'
] 