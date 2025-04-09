#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Captcha handling module for the crawler system.
Provides captcha solving capabilities for various types of captchas.
"""

from enum import Enum
from typing import Dict, Any, Optional

from .detection import CaptchaDetector, CaptchaDetectionResult
from .captcha_manager import CaptchaManager
from .solvers.text_solver import TextSolver
from .solvers.slider_solver import SliderSolver
from .solvers.click_solver import ClickSolver
from .solvers.recaptcha_solver import RecaptchaSolver


class CaptchaType(Enum):
    """驗證碼類型枚舉"""
    RECAPTCHA = "recaptcha"    # Google reCAPTCHA
    HCAPTCHA = "hcaptcha"      # hCaptcha
    IMAGE_CAPTCHA = "image"    # 傳統圖片驗證碼
    SLIDER_CAPTCHA = "slider"  # 滑塊驗證碼
    ROTATE_CAPTCHA = "rotate"  # 旋轉驗證碼
    CLICK_CAPTCHA = "click"    # 點擊驗證碼
    TEXT_CAPTCHA = "text"      # 文字問答驗證碼
    MANUAL = "manual"          # 人工手動驗證
    CUSTOM = "custom"          # 自定義驗證函式
    UNKNOWN = "unknown"        # 未知類型


__all__ = [
    'CaptchaType',
    'CaptchaDetector',
    'CaptchaDetectionResult',
    'CaptchaManager',
    'TextSolver',
    'SliderSolver',
    'ClickSolver',
    'RecaptchaSolver'
]
