#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
驗證碼服務模組

提供驗證碼處理的核心功能，包括：
1. 驗證碼檢測
2. 驗證碼識別
3. 驗證碼處理
4. 結果驗證
"""

import time
import os
from typing import Optional, Dict, Any, List, Union
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from src.core.utils import (
    BrowserUtils,
    Logger,
    URLUtils,
    DataProcessor,
    ErrorHandler,
    ConfigUtils,
    ImageUtils,
    AudioUtils,
    TextUtils
)

from ..types import CaptchaType, CaptchaResult

class CaptchaService:
    """驗證碼服務類"""
    
    def __init__(self, browser: WebDriver, config: Dict[str, Any]):
        """
        初始化驗證碼服務
        
        Args:
            browser: WebDriver 實例
            config: 配置字典
        """
        self.browser = browser
        self.config = config
        
        # 初始化工具類
        self.logger = Logger(__name__)
        self.error_handler = ErrorHandler()
        self.config_utils = ConfigUtils()
        self.browser_utils = BrowserUtils(self.browser)
        self.url_utils = URLUtils()
        self.data_processor = DataProcessor()
        self.image_utils = ImageUtils()
        self.audio_utils = AudioUtils()
        self.text_utils = TextUtils()
        
        # 初始化配置
        self._init_service()
        
    def _init_service(self) -> None:
        """初始化驗證碼服務"""
        # 初始化服務設置
        self.service_config = {
            'timeout': self.config.get('timeout', 30),
            'retry_count': self.config.get('max_retries', 3),
            'retry_delay': self.config.get('retry_delay', 1.0),
            'captcha_type': self.config.get('captcha_type', 'image'),
            'captcha_source': self.config.get('captcha_source', 'local')
        }
        
        # 初始化目錄
        self.dirs = {
            'temp': os.path.join(self.config['data_dir'], 'temp'),
            'results': os.path.join(self.config['data_dir'], 'results'),
            'samples': os.path.join(self.config['data_dir'], 'samples')
        }
        
        # 創建目錄
        for dir_path in self.dirs.values():
            os.makedirs(dir_path, exist_ok=True)
        
        # 初始化緩存
        self.cache = {
            'results': {},
            'samples': {}
        }
        
        # 初始化驗證碼類型配置
        self.captcha_configs = {
            CaptchaType.IMAGE: {
                'preprocessing': self.config.get('image_preprocessing', True),
                'threshold': self.config.get('image_threshold', 127),
                **self.config.get('image_config', {})
            },
            CaptchaType.AUDIO: {
                'preprocessing': self.config.get('audio_preprocessing', True),
                'sample_rate': self.config.get('audio_sample_rate', 16000),
                **self.config.get('audio_config', {})
            },
            CaptchaType.TEXT: {
                'preprocessing': self.config.get('text_preprocessing', True),
                'min_length': self.config.get('text_min_length', 4),
                **self.config.get('text_config', {})
            },
            CaptchaType.SLIDER: {
                'move_delay': self.config.get('slider_move_delay', 0.1),
                'move_offset': self.config.get('slider_move_offset', 5),
                **self.config.get('slider_config', {})
            }
        }
        
    def detect_captcha(self, selectors: List[str]) -> Optional[WebElement]:
        """
        檢測驗證碼元素
        
        Args:
            selectors: 選擇器列表
            
        Returns:
            Optional[WebElement]: 驗證碼元素
        """
        try:
            for selector in selectors:
                try:
                    element = self.browser_utils.wait_for_element(
                        self.browser,
                        By.CSS_SELECTOR,
                        selector,
                        timeout=self.service_config['timeout']
                    )
                    if element and element.is_displayed():
                        self.logger.info(f"檢測到驗證碼元素: {selector}")
                        return element
                except TimeoutException:
                    continue
                    
            self.logger.warning("未檢測到驗證碼元素")
            return None
            
        except Exception as e:
            self.logger.error(f"檢測驗證碼失敗: {str(e)}")
            return None
            
    def solve_image_captcha(self, element: WebElement) -> CaptchaResult:
        """
        處理圖像驗證碼
        
        Args:
            element: 驗證碼元素
            
        Returns:
            CaptchaResult: 處理結果
        """
        try:
            start_time = datetime.now()
            
            # 獲取圖像
            image = self.browser_utils.get_element_screenshot(element)
            if not image:
                raise Exception("無法獲取驗證碼圖像")
                
            # 保存原始圖像
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            raw_path = Path(self.dirs['temp']) / f"raw_{timestamp}.png"
            self.image_utils.save_image(image, raw_path)
            
            # 預處理圖像
            processed = self.image_utils.preprocess_image(image)
            if not processed:
                raise Exception("圖像預處理失敗")
                
            # 保存處理後的圖像
            processed_path = Path(self.dirs['temp']) / f"processed_{timestamp}.png"
            self.image_utils.save_image(processed, processed_path)
            
            # 識別文本
            text = self.text_utils.recognize_text(processed)
            if not text:
                raise Exception("文本識別失敗")
                
            # 計算處理時間
            duration = (datetime.now() - start_time).total_seconds()
            
            # 返回結果
            result = CaptchaResult(
                success=True,
                captcha_type=CaptchaType.IMAGE,
                solution=text,
                confidence=0.8,
                details={
                    'raw_image': str(raw_path),
                    'processed_image': str(processed_path),
                    'timestamp': timestamp,
                    'duration': duration
                }
            )
            
            # 更新緩存
            self.cache['results'][timestamp] = result
            
            self.logger.info(f"圖像驗證碼處理成功: {text}")
            return result
            
        except Exception as e:
            self.logger.error(f"處理圖像驗證碼失敗: {str(e)}")
            return CaptchaResult(
                success=False,
                captcha_type=CaptchaType.IMAGE,
                error=str(e)
            )
            
    def solve_audio_captcha(self, element: WebElement) -> CaptchaResult:
        """
        處理音頻驗證碼
        
        Args:
            element: 驗證碼元素
            
        Returns:
            CaptchaResult: 處理結果
        """
        try:
            start_time = datetime.now()
            
            # 獲取音頻
            audio = self.browser_utils.get_element_audio(element)
            if not audio:
                raise Exception("無法獲取驗證碼音頻")
                
            # 保存原始音頻
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            raw_path = Path(self.dirs['temp']) / f"raw_{timestamp}.mp3"
            self.audio_utils.save_audio(audio, raw_path)
            
            # 預處理音頻
            processed = self.audio_utils.preprocess_audio(audio)
            if not processed:
                raise Exception("音頻預處理失敗")
                
            # 保存處理後的音頻
            processed_path = Path(self.dirs['temp']) / f"processed_{timestamp}.wav"
            self.audio_utils.save_audio(processed, processed_path)
            
            # 識別文本
            text = self.audio_utils.recognize_speech(processed)
            if not text:
                raise Exception("語音識別失敗")
                
            # 計算處理時間
            duration = (datetime.now() - start_time).total_seconds()
            
            # 返回結果
            result = CaptchaResult(
                success=True,
                captcha_type=CaptchaType.AUDIO,
                solution=text,
                confidence=0.8,
                details={
                    'raw_audio': str(raw_path),
                    'processed_audio': str(processed_path),
                    'timestamp': timestamp,
                    'duration': duration
                }
            )
            
            # 更新緩存
            self.cache['results'][timestamp] = result
            
            self.logger.info(f"音頻驗證碼處理成功: {text}")
            return result
            
        except Exception as e:
            self.logger.error(f"處理音頻驗證碼失敗: {str(e)}")
            return CaptchaResult(
                success=False,
                captcha_type=CaptchaType.AUDIO,
                error=str(e)
            )
            
    def clear_cache(self):
        """清理緩存"""
        try:
            self.cache['results'] = {}
            self.logger.info("服務緩存已清理")
        except Exception as e:
            self.logger.error(f"清理緩存失敗: {str(e)}")

    def validate_result(
        self,
        result: CaptchaResult,
        min_confidence: float = 0.8
    ) -> bool:
        """
        驗證處理結果
        
        Args:
            result: 處理結果
            min_confidence: 最小可信度
            
        Returns:
            是否有效
        """
        try:
            # 檢查成功標誌
            if not result.success:
                return False
                
            # 檢查解決方案
            if not result.solution:
                return False
                
            # 檢查可信度
            if result.confidence < min_confidence:
                return False
                
            # 檢查驗證碼類型
            if result.captcha_type == CaptchaType.UNKNOWN:
                return False
                
            # 驗證文本
            if result.captcha_type in [CaptchaType.IMAGE, CaptchaType.TEXT]:
                if not self.text_utils.validate_text(result.solution):
                    return False
                    
            # 驗證音頻
            if result.captcha_type == CaptchaType.AUDIO:
                if not self.audio_utils.validate_text(result.solution):
                    return False
                    
            # 驗證滑塊
            if result.captcha_type == CaptchaType.SLIDER:
                if not result.details.get('distance') or not result.details.get('tracks'):
                    return False
                    
            return True
            
        except Exception as e:
            self.logger.error(f"結果驗證失敗: {str(e)}")
            return False 