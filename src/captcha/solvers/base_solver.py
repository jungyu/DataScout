#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
基礎驗證碼求解器模組

提供驗證碼求解的基礎功能。
包括：
1. 驗證碼圖片處理
2. 驗證碼文本識別
3. 驗證碼結果驗證
4. 第三方服務整合
"""

from typing import Dict, Any, Optional, List, Union, Tuple
from pathlib import Path
import time
import json
import base64
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
import os

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException
)

from src.core.utils import (
    BrowserUtils,
    Logger,
    URLUtils,
    DataProcessor,
    ErrorHandler,
    ConfigUtils,
    PathUtils,
    ImageUtils,
    CookieManager
)

from ..types import CaptchaType, CaptchaConfig, CaptchaResult


class BaseSolver(ABC):
    """基礎驗證碼求解器"""
    
    def __init__(self, browser: WebDriver, config: Dict[str, Any]):
        """
        初始化求解器
        
        Args:
            browser: WebDriver 實例
            config: 配置字典
        """
        self.browser = browser
        self.config = config
        
        # 初始化工具類
        self.browser_utils = BrowserUtils()
        self.logger = Logger(__name__)
        self.url_utils = URLUtils()
        self.data_processor = DataProcessor()
        self.image_utils = ImageUtils()
        self.cookie_manager = CookieManager()
        self.error_handler = ErrorHandler()
        self.config_utils = ConfigUtils()
        self.path_utils = PathUtils()
        
        # 初始化配置
        self._init_solver()
        
    def _init_solver(self):
        """初始化求解器配置"""
        try:
            # 設置超時和重試
            self.timeout = self.config.get('timeout', 30)
            self.retry_count = self.config.get('retry_count', 3)
            
            # 設置目錄
            self.screenshot_dir = self.config.get('screenshot_dir', 'screenshots')
            self.temp_dir = self.config.get('temp_dir', 'temp')
            self.sample_dir = self.config.get('sample_dir', 'samples')
            
            # 創建目錄
            for dir_path in [self.screenshot_dir, self.temp_dir, self.sample_dir]:
                os.makedirs(dir_path, exist_ok=True)
                
            # 初始化狀態
            self.solving_status = {
                'current_type': None,
                'retry_count': 0,
                'success_count': 0,
                'failure_count': 0,
                'start_time': None,
                'end_time': None,
                'duration': None
            }
            
            # 初始化緩存
            self.result_cache = {}
            self.sample_cache = {}
            
        except Exception as e:
            self.logger.error(f"初始化求解器失敗: {str(e)}")
            raise
            
    @abstractmethod
    def solve(self, element: WebElement) -> CaptchaResult:
        """
        求解驗證碼
        
        Args:
            element: 驗證碼元素
            
        Returns:
            CaptchaResult: 驗證碼求解結果
        """
        pass
        
    def preprocess_image(self, image_path: Union[str, Path]) -> Optional[str]:
        """
        預處理驗證碼圖片
        
        Args:
            image_path: 圖片路徑
            
        Returns:
            Optional[str]: 處理後的圖片路徑
        """
        try:
            # 讀取圖片
            image = self.image_utils.read_image(image_path)
            if image is None:
                self.logger.error("無法讀取圖片")
                return None
                
            # 圖片預處理
            processed = self.image_utils.preprocess_image(image)
            if processed is None:
                self.logger.error("圖片預處理失敗")
                return None
                
            # 保存處理後的圖片
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = Path(self.temp_dir) / f"processed_{timestamp}.png"
            self.image_utils.save_image(processed, output_path)
            
            self.logger.info(f"圖片預處理完成: {output_path}")
            return str(output_path)
            
        except Exception as e:
            self.logger.error(f"預處理圖片失敗: {str(e)}")
            return None
            
    def extract_text(self, image_path: Union[str, Path]) -> Optional[str]:
        """
        從圖片中提取文本
        
        Args:
            image_path: 圖片路徑
            
        Returns:
            Optional[str]: 提取的文本
        """
        try:
            # 讀取圖片
            image = self.image_utils.read_image(image_path)
            if image is None:
                return None
            
            # 文本識別
            text = self.image_utils.extract_text(image)
            if not text:
                return None
            
            # 文本處理
            text = self.data_processor.clean_text(text)
            
            return text
        except Exception as e:
            self.error_handler.handle_error(e, "從圖片中提取文本失敗")
            return None
    
    def validate_solution(self, solution: str) -> bool:
        """
        驗證求解結果
        
        Args:
            solution: 求解結果
            
        Returns:
            bool: 結果是否有效
        """
        try:
            # 檢查結果是否為空
            if not solution:
                return False
            
            # 檢查結果長度
            if len(solution) < self.config.text_min_length:
                return False
            
            # 檢查結果格式
            if not self.data_processor.validate_text(solution):
                return False
            
            return True
        except Exception as e:
            self.error_handler.handle_error(e, "驗證求解結果失敗")
            return False
    
    def save_sample(
        self,
        image_path: Union[str, Path],
        result: CaptchaResult,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        保存驗證碼樣本
        
        Args:
            image_path: 圖片路徑
            result: 驗證碼結果
            metadata: 元數據
            
        Returns:
            bool: 是否保存成功
        """
        try:
            # 生成樣本ID
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            sample_id = f"sample_{timestamp}"
            
            # 複製圖片到樣本目錄
            sample_path = Path(self.sample_dir) / f"{sample_id}.png"
            self.image_utils.copy_image(image_path, sample_path)
            
            # 保存結果和元數據
            metadata = metadata or {}
            metadata.update({
                'timestamp': timestamp,
                'url': self.browser.current_url,
                'success': result.success,
                'solution': result.solution,
                'duration': result.duration
            })
            
            metadata_path = Path(self.sample_dir) / f"{sample_id}.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
                
            # 更新緩存
            self.sample_cache[sample_id] = {
                'image_path': str(sample_path),
                'metadata_path': str(metadata_path),
                'timestamp': timestamp
            }
            
            self.logger.info(f"已保存驗證碼樣本: {sample_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"保存驗證碼樣本失敗: {str(e)}")
            return False
            
    def clear_cache(self):
        """清理緩存"""
        try:
            self.result_cache = {}
            self.sample_cache = {}
            self.logger.info("求解器緩存已清理")
        except Exception as e:
            self.logger.error(f"清理緩存失敗: {str(e)}")