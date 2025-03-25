from typing import Dict, Any, List, Optional, Type
import logging
import time
import json
import os
from selenium.webdriver.remote.webdriver import WebDriver

from .solvers.base_solver import BaseCaptchaSolver
from .solvers.text_solver import TextCaptchaSolver
from .solvers.slider_solver import SliderCaptchaSolver
from .solvers.click_solver import ClickCaptchaSolver
from .solvers.rotate_solver import RotateCaptchaSolver
from .solvers.recaptcha_solver import ReCaptchaSolver

class CaptchaManager:
    """驗證碼管理器，協調各類驗證碼解決器的工作"""
    
    def __init__(self, driver: WebDriver, config_path: str = None):
        """
        初始化驗證碼管理器
        
        Args:
            driver: WebDriver實例
            config_path: 配置文件路徑
        """
        self.driver = driver
        self.logger = logging.getLogger(__name__)
        
        # 統計數據
        self.stats = {
            'total_attempts': 0,
            'success_count': 0,
            'failure_count': 0,
            'solver_stats': {}
        }
        
        # 加載配置
        self.config = self._load_config(config_path)
        
        # 初始化解決器
        self.solvers = self._init_solvers()
        
        # 初始化每個解決器的統計
        for solver in self.solvers:
            solver_name = solver.__class__.__name__
            self.stats['solver_stats'][solver_name] = {
                'attempts': 0,
                'success': 0,
                'failure': 0
            }
        
        self.logger.info(f"驗證碼管理器初始化完成，已加載 {len(self.solvers)} 個解決器")

    def update_config(self, new_config: Dict[str, Any]) -> None:
        """更新運行時配置"""
        self.config.update(new_config)
        # 更新所有解決器的配置
        for solver in self.solvers:
            solver_name = solver.__class__.__name__.lower().replace('solver', '')
            if solver_name in new_config:
                solver.update_config(new_config[solver_name])

    def get_stats(self) -> Dict[str, Any]:
        """獲取驗證碼解決統計數據"""
        return self.stats

    def check_solver_status(self) -> Dict[str, bool]:
        """檢查所有解決器的狀態"""
        status = {}
        for solver in self.solvers:
            solver_name = solver.__class__.__name__
            try:
                is_ready = solver.is_ready() if hasattr(solver, 'is_ready') else True
                status[solver_name] = is_ready
            except Exception as e:
                self.logger.error(f"{solver_name} 狀態檢查失敗: {str(e)}")
                status[solver_name] = False
        return status

    def _update_stats(self, solver_name: str, success: bool) -> None:
        """更新統計數據"""
        self.stats['total_attempts'] += 1
        if success:
            self.stats['success_count'] += 1
        else:
            self.stats['failure_count'] += 1
            
        solver_stats = self.stats['solver_stats'].get(solver_name, {
            'attempts': 0,
            'success': 0,
            'failure': 0
        })
        solver_stats['attempts'] += 1
        if success:
            solver_stats['success'] += 1
        else:
            solver_stats['failure'] += 1
        self.stats['solver_stats'][solver_name] = solver_stats
    
    def _load_config(self, config_path: str = None) -> Dict[str, Any]:
        """加載配置文件"""
        default_config = {
            "general": {
                "max_retries": 3,
                "save_samples": True,
                "sample_dir": "../captchas",
                "enable_machine_learning": False
            },
            "text_captcha": {"enabled": True},
            "slider_captcha": {"enabled": True},
            "click_captcha": {"enabled": True},
            "rotate_captcha": {"enabled": True},
            "recaptcha": {"enabled": True},
            "logging": {"enabled": True, "level": "INFO"}
        }
        
        if not config_path:
            # 使用預設配置
            return default_config
        
        try:
            # 讀取配置文件
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self.logger.info(f"成功加載配置文件: {config_path}")
            return config
            
        except Exception as e:
            self.logger.error(f"加載配置文件失敗: {str(e)}，使用預設配置")
            return default_config
    
    def _init_solvers(self) -> List[BaseCaptchaSolver]:
        """初始化所有驗證碼解決器"""
        solvers = []
        
        # 根據配置初始化各類解決器
        if self.config.get('text_captcha', {}).get('enabled', True):
            solvers.append(TextCaptchaSolver(self.driver, self.config.get('text_captcha', {})))
            
        if self.config.get('slider_captcha', {}).get('enabled', True):
            solvers.append(SliderCaptchaSolver(self.driver, self.config.get('slider_captcha', {})))
            
        if self.config.get('click_captcha', {}).get('enabled', True):
            solvers.append(ClickCaptchaSolver(self.driver, self.config.get('click_captcha', {})))
            
        if self.config.get('rotate_captcha', {}).get('enabled', True):
            solvers.append(RotateCaptchaSolver(self.driver, self.config.get('rotate_captcha', {})))
            
        if self.config.get('recaptcha', {}).get('enabled', True):
            solvers.append(ReCaptchaSolver(self.driver, self.config.get('recaptcha', {})))
        
        return solvers
    
    def detect_and_solve(self) -> bool:
        """檢測並解決頁面上的驗證碼"""
        # 最大重試次數
        max_retries = self.config.get('general', {}).get('max_retries', 3)
        # 對每種解決器進行檢測
        for solver in self.solvers:
            # 檢測是否存在此類型的驗證碼
            if solver.detect():
                solver_name = solver.__class__.__name__
                self.logger.info(f"檢測到 {solver_name}")
                
                # 嘗試解決驗證碼
                for attempt in range(1, max_retries + 1):
                    self.logger.info(f"嘗試解決 {solver_name}, 第 {attempt}/{max_retries} 次")
                    
                    # 解決驗證碼
                    success = solver.solve()
                    
                    # 更新統計數據
                    self._update_stats(solver_name, success)
                    
                    if success:
                        self.logger.info(f"成功解決 {solver_name}")
                        return True
                        
                    # 如果失敗但還有重試機會
                    if attempt < max_retries:
                        self.logger.warning(f"{solver_name} 解決失敗，將重試")
                        time.sleep(1)  # 等待一下再重試
                    else:
                        self.logger.error(f"{solver_name} 解決失敗，已達最大重試次數")
                
                # 該類型驗證碼解決失敗
                return False
        
        # 未檢測到任何支持的驗證碼類型
        self.logger.info("未檢測到任何驗證碼")
        return True
    
    def solve_specific(self, captcha_type: str) -> bool:
        """解決特定類型的驗證碼"""
        # 類型名稱映射
        type_mapping = {
            'text': TextCaptchaSolver,
            'slider': SliderCaptchaSolver,
            'click': ClickCaptchaSolver,
            'rotate': RotateCaptchaSolver,
            'recaptcha': ReCaptchaSolver
        }
        
        # 檢查是否支持該類型
        if captcha_type not in type_mapping:
            self.logger.error(f"不支持的驗證碼類型: {captcha_type}")
            return False
            
        # 查找對應的解決器
        solver_class = type_mapping[captcha_type]
        solver = None
        
        for s in self.solvers:
            if isinstance(s, solver_class):
                solver = s
                break
                
        if not solver:
            self.logger.error(f"未找到 {captcha_type} 類型的解決器")
            return False
            
        # 檢測並解決
        if not solver.detect():
            self.logger.warning(f"未檢測到 {captcha_type} 類型的驗證碼")
            return False
            
        # 最大重試次數
        max_retries = self.config.get('general', {}).get('max_retries', 3)
        
        # 嘗試解決
        for attempt in range(1, max_retries + 1):
            self.logger.info(f"嘗試解決 {captcha_type}, 第 {attempt}/{max_retries} 次")
            
            success = solver.solve()
            
            # 更新統計數據
            self._update_stats(solver.__class__.__name__, success)
            
            if success:
                self.logger.info(f"成功解決 {captcha_type}")
                return True
                
            # 如果失敗但還有重試機會
            if attempt < max_retries:
                self.logger.warning(f"{captcha_type} 解決失敗，將重試")
                time.sleep(1)  # 等待一下再重試
            else:
                self.logger.error(f"{captcha_type} 解決失敗，已達最大重試次數")
        
        return False