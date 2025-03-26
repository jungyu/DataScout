#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import logging
import requests
from typing import Dict, List, Optional, Any

from selenium import webdriver
from selenium.webdriver.common.by import By


class ThirdPartyServiceClient:
    """第三方驗證碼解決服務的統一接口"""
    
    def __init__(self, services: List[Dict], default_api_key: str = None, logger=None):
        """
        初始化第三方服務客戶端
        
        Args:
            services: 服務配置列表
            default_api_key: 默認API密鑰
            logger: 日誌記錄器
        """
        self.services = services
        self.default_api_key = default_api_key
        self.logger = logger or logging.getLogger(__name__)
        
        # API端點配置
        self.api_endpoints = {
            "2captcha": {
                "submit": "https://2captcha.com/in.php",
                "result": "https://2captcha.com/res.php"
            },
            "anticaptcha": {
                "submit": "https://api.anti-captcha.com/createTask",
                "result": "https://api.anti-captcha.com/getTaskResult"
            }
        }
    
    def solve_captcha(self, captcha_type: str, captcha_data: Dict, driver: webdriver.Remote) -> bool:
        """
        使用第三方服務解決驗證碼
        
        Args:
            captcha_type: 驗證碼類型
            captcha_data: 驗證碼數據
            driver: WebDriver實例
            
        Returns:
            是否成功解決
        """
        for service in self.services:
            service_type = service.get("type")
            service_api = service.get("api")
            service_key = service.get("key") or self.default_api_key
            
            if not all([service_type, service_api, service_key]):
                self.logger.warning(f"第三方服務配置不完整: {service}")
                continue
            
            # 檢查服務是否支持此類型的驗證碼
            if captcha_type not in service.get("supported_types", []):
                self.logger.debug(f"服務 {service_type} 不支持 {captcha_type} 驗證碼")
                continue
            
            self.logger.info(f"嘗試使用第三方服務 {service_type} 解決 {captcha_type} 驗證碼")
            
            try:
                # 調用第三方服務API
                if service_type == "2captcha":
                    return self._solve_with_2captcha(service_api, service_key, captcha_type, captcha_data, driver)
                elif service_type == "anticaptcha":
                    return self._solve_with_anticaptcha(service_api, service_key, captcha_type, captcha_data, driver)
                else:
                    self.logger.warning(f"不支持的第三方服務類型: {service_type}")
                    continue
            
            except Exception as e:
                self.logger.error(f"使用第三方服務 {service_type} 時發生錯誤: {str(e)}")
        
        return False
    
    def _solve_with_2captcha(self, api_url: str, api_key: str, captcha_type: str, 
                            captcha_data: Dict, driver: webdriver.Remote) -> bool:
        """使用2Captcha服務解決驗證碼"""
        # 整合原有代碼，處理不同類型的驗證碼
        # ...
    
    def _solve_with_anticaptcha(self, api_url: str, api_key: str, captcha_type: str, 
                                captcha_data: Dict, driver: webdriver.Remote) -> bool:
        """使用Anti-Captcha服務解決驗證碼"""
        # 整合原有代碼，處理不同類型的驗證碼
        # ...