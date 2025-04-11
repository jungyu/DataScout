#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
第三方驗證碼服務客戶端模組

提供統一的第三方驗證碼服務接口，支持：
1. 2captcha
2. Anti-Captcha
3. DeathByCaptcha
等服務。
"""

import time
import os
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By

from src.core.utils import (
    BrowserUtils,
    Logger,
    URLUtils,
    DataProcessor,
    ErrorHandler,
    ConfigUtils,
    ImageUtils,
    AudioUtils,
    TextUtils,
    CookieManager
)

from ..types import CaptchaResult


class ThirdPartyServiceClient:
    """第三方驗證碼服務客戶端"""
    
    def __init__(self, browser: WebDriver, config: Dict[str, Any]):
        """
        初始化第三方服務客戶端
        
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
        self.cookie_manager = CookieManager()
        
        # 初始化配置
        self._init_client()
        
    def _init_client(self):
        """初始化客戶端配置"""
        try:
            # 設置超時和重試
            self.timeout = self.config.get('timeout', 30)
            self.retry_count = self.config.get('retry_count', 3)
            self.retry_delay = self.config.get('retry_delay', 1.0)
            
            # 設置目錄
            self.temp_dir = self.config.get('temp_dir', 'temp')
            self.result_dir = self.config.get('result_dir', 'results')
            
            # 創建目錄
            for dir_path in [self.temp_dir, self.result_dir]:
                os.makedirs(dir_path, exist_ok=True)
                
            # 設置API端點
            self.api_endpoints = {
                '2captcha': {
                    'submit': 'https://2captcha.com/in.php',
                    'result': 'https://2captcha.com/res.php'
                },
                'anti_captcha': {
                    'submit': 'https://api.anti-captcha.com/createTask',
                    'result': 'https://api.anti-captcha.com/getTaskResult'
                },
                'death_by_captcha': {
                    'submit': 'http://api.dbcapi.me/api/captcha',
                    'result': 'http://api.dbcapi.me/api/captcha/{captcha_id}'
                }
            }
            
            # 初始化狀態
            self.client_status = {
                'current_service': None,
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
            
        except Exception as e:
            self.logger.error(f"初始化客戶端失敗: {str(e)}")
            raise
            
    def solve_captcha(self, element: WebElement, captcha_type: str) -> CaptchaResult:
        """
        使用第三方服務解決驗證碼
        
        Args:
            element: 驗證碼元素
            captcha_type: 驗證碼類型
            
        Returns:
            CaptchaResult: 驗證碼結果
        """
        try:
            # 更新狀態
            self.client_status['current_type'] = captcha_type
            self.client_status['start_time'] = datetime.now()
            
            # 獲取驗證碼數據
            captcha_data = self._get_captcha_data(element, captcha_type)
            if not captcha_data:
                raise Exception("無法獲取驗證碼數據")
                
            # 遍歷可用服務
            for service in self.config.get('services', []):
                service_type = service.get('type')
                service_key = service.get('key')
                
                if not all([service_type, service_key]):
                    self.logger.warning(f"服務配置不完整: {service}")
                    continue
                    
                # 檢查服務支持
                if captcha_type not in service.get('supported_types', []):
                    self.logger.debug(f"服務 {service_type} 不支持 {captcha_type} 驗證碼")
                    continue
                    
                # 更新狀態
                self.client_status['current_service'] = service_type
                
                # 調用服務
                try:
                    if service_type == '2captcha':
                        result = self._solve_with_2captcha(service_key, captcha_data)
                    elif service_type == 'anti_captcha':
                        result = self._solve_with_anti_captcha(service_key, captcha_data)
                    elif service_type == 'death_by_captcha':
                        result = self._solve_with_death_by_captcha(service_key, captcha_data)
                    else:
                        self.logger.warning(f"不支持的服務類型: {service_type}")
                        continue
                        
                    if result.success:
                        # 更新狀態
                        self.client_status['end_time'] = datetime.now()
                        self.client_status['duration'] = (
                            self.client_status['end_time'] - 
                            self.client_status['start_time']
                        ).total_seconds()
                        self.client_status['success_count'] += 1
                        
                        # 更新緩存
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        self.result_cache[timestamp] = result
                        
                        self.logger.info(f"使用服務 {service_type} 解決驗證碼成功")
                        return result
                        
                except Exception as e:
                    self.logger.error(f"使用服務 {service_type} 時發生錯誤: {str(e)}")
                    self.client_status['failure_count'] += 1
                    continue
                    
            # 所有服務都失敗
            raise Exception("所有可用服務都無法解決驗證碼")
            
        except Exception as e:
            self.logger.error(f"解決驗證碼失敗: {str(e)}")
            return CaptchaResult(
                success=False,
                error=str(e)
            )
            
    def _get_captcha_data(self, element: WebElement, captcha_type: str) -> Optional[Dict[str, Any]]:
        """
        獲取驗證碼數據
        
        Args:
            element: 驗證碼元素
            captcha_type: 驗證碼類型
            
        Returns:
            Optional[Dict[str, Any]]: 驗證碼數據
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            if captcha_type == 'image':
                # 獲取並保存圖像
                image = self.browser_utils.get_element_screenshot(element)
                if not image:
                    return None
                    
                image_path = Path(self.temp_dir) / f"captcha_{timestamp}.png"
                self.image_utils.save_image(image, image_path)
                
                return {
                    'type': 'ImageToTextTask',
                    'image_path': str(image_path)
                }
                
            elif captcha_type == 'recaptcha':
                # 獲取 reCAPTCHA 數據
                site_key = element.get_attribute('data-sitekey')
                if not site_key:
                    return None
                    
                return {
                    'type': 'RecaptchaV2Task',
                    'website_url': self.browser.current_url,
                    'website_key': site_key
                }
                
            elif captcha_type == 'hcaptcha':
                # 獲取 hCaptcha 數據
                site_key = element.get_attribute('data-sitekey')
                if not site_key:
                    return None
                    
                return {
                    'type': 'HcaptchaTask',
                    'website_url': self.browser.current_url,
                    'website_key': site_key
                }
                
            else:
                self.logger.warning(f"不支持的驗證碼類型: {captcha_type}")
                return None
                
        except Exception as e:
            self.logger.error(f"獲取驗證碼數據失敗: {str(e)}")
            return None
            
    def _solve_with_2captcha(self, api_key: str, captcha_data: Dict[str, Any]) -> CaptchaResult:
        """使用 2captcha 服務解決驗證碼"""
        try:
            # 提交任務
            response = self.url_utils.post_request(
                self.api_endpoints['2captcha']['submit'],
                data={
                    'key': api_key,
                    'method': 'base64',
                    'json': 1,
                    **captcha_data
                }
            )
            
            if not response.get('status'):
                raise Exception(response.get('error'))
                
            # 獲取結果
            task_id = response['request']
            for _ in range(self.retry_count):
                time.sleep(self.retry_delay)
                
                response = self.url_utils.get_request(
                    self.api_endpoints['2captcha']['result'],
                    params={
                        'key': api_key,
                        'action': 'get',
                        'id': task_id,
                        'json': 1
                    }
                )
                
                if response.get('status'):
                    return CaptchaResult(
                        success=True,
                        solution=response['request'],
                        duration=time.time() - self.client_status['start_time'].timestamp(),
                        metadata={
                            'service': '2captcha',
                            'task_id': task_id
                        }
                    )
                    
            raise Exception("等待結果超時")
            
        except Exception as e:
            self.logger.error(f"使用 2captcha 服務失敗: {str(e)}")
            return CaptchaResult(
                success=False,
                error=str(e)
            )
            
    def _solve_with_anti_captcha(self, api_key: str, captcha_data: Dict[str, Any]) -> CaptchaResult:
        """使用 Anti-Captcha 服務解決驗證碼"""
        try:
            # 提交任務
            response = self.url_utils.post_request(
                self.api_endpoints['anti_captcha']['submit'],
                json={
                    'clientKey': api_key,
                    'task': captcha_data
                }
            )
            
            if response.get('errorId'):
                raise Exception(response.get('errorDescription'))
                
            # 獲取結果
            task_id = response['taskId']
            for _ in range(self.retry_count):
                time.sleep(self.retry_delay)
                
                response = self.url_utils.post_request(
                    self.api_endpoints['anti_captcha']['result'],
                    json={
                        'clientKey': api_key,
                        'taskId': task_id
                    }
                )
                
                if response.get('status') == 'ready':
                    return CaptchaResult(
                        success=True,
                        solution=response['solution']['text'],
                        duration=time.time() - self.client_status['start_time'].timestamp(),
                        metadata={
                            'service': 'anti_captcha',
                            'task_id': task_id
                        }
                    )
                    
            raise Exception("等待結果超時")
            
        except Exception as e:
            self.logger.error(f"使用 Anti-Captcha 服務失敗: {str(e)}")
            return CaptchaResult(
                success=False,
                error=str(e)
            )
            
    def _solve_with_death_by_captcha(self, api_key: str, captcha_data: Dict[str, Any]) -> CaptchaResult:
        """使用 Death By Captcha 服務解決驗證碼"""
        try:
            # 提交任務
            response = self.url_utils.post_request(
                self.api_endpoints['death_by_captcha']['submit'],
                auth=(api_key, 'password'),
                data=captcha_data
            )
            
            if not response.get('captcha'):
                raise Exception(response.get('error'))
                
            # 獲取結果
            captcha_id = response['captcha']
            for _ in range(self.retry_count):
                time.sleep(self.retry_delay)
                
                response = self.url_utils.get_request(
                    self.api_endpoints['death_by_captcha']['result'].format(
                        captcha_id=captcha_id
                    ),
                    auth=(api_key, 'password')
                )
                
                if response.get('text'):
                    return CaptchaResult(
                        success=True,
                        solution=response['text'],
                        duration=time.time() - self.client_status['start_time'].timestamp(),
                        metadata={
                            'service': 'death_by_captcha',
                            'captcha_id': captcha_id
                        }
                    )
                    
            raise Exception("等待結果超時")
            
        except Exception as e:
            self.logger.error(f"使用 Death By Captcha 服務失敗: {str(e)}")
            return CaptchaResult(
                success=False,
                error=str(e)
            )
            
    def clear_cache(self):
        """清理緩存"""
        try:
            self.result_cache = {}
            self.logger.info("客戶端緩存已清理")
        except Exception as e:
            self.logger.error(f"清理緩存失敗: {str(e)}")