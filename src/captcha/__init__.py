"""
Captcha handling module for the crawler system.
Provides captcha solving capabilities for various types of captchas.
"""

from .captcha_manager import CaptchaManager
from .solvers.text_solver import TextSolver
from .solvers.slider_solver import SliderSolver
from .solvers.click_solver import ClickSolver
from .solvers.recaptcha_solver import RecaptchaSolver

__all__ = [
    'CaptchaManager',
    'TextSolver',
    'SliderSolver',
    'ClickSolver',
    'RecaptchaSolver'
]
