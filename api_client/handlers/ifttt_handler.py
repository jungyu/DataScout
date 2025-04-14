#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
IFTTT 處理器
提供與 IFTTT 平台的整合功能
"""

import json
import logging
import requests
from typing import Dict, Any, Optional, Union, List
from api_client.core.base_client import BaseClient
from api_client.core.config import APIConfig
from api_client.core.exceptions import APIError, AuthenticationError, RequestError
from api_client.utils.utils import Utils

class IFTTTHandler(BaseClient):
    """IFTTT 處理器"""
    
    def __init__(self, config: Union[Dict[str, Any], APIConfig]):
        """初始化 IFTTT 處理器
        
        Args:
            config: 配置對象，可以是字典或配置類實例
        """
        # 設置 API 類型
        if isinstance(config, dict):
            config["api_type"] = "rest"
            config["base_url"] = config.get("base_url", "https://maker.ifttt.com/trigger")
            config["auth_type"] = config.get("auth_type", "api_key")
        else:
            config.api_type = "rest"
            config.base_url = config.base_url or "https://maker.ifttt.com/trigger"
            config.auth_type = config.auth_type or "api_key"
        
        # 初始化父類
        super().__init__(config)
        
        # 初始化工具類
        self.utils = Utils()
        
        # 設置 IFTTT 特定參數
        if isinstance(config, dict):
            self.webhook_key = config.get("webhook_key", "")
        else:
            self.webhook_key = getattr(config, "webhook_key", "")
    
    def trigger_event(self, event_name: str, value1: Optional[str] = None, value2: Optional[str] = None, value3: Optional[str] = None) -> Dict[str, Any]:
        """觸發 IFTTT 事件
        
        Args:
            event_name: 事件名稱
            value1: 第一個值
            value2: 第二個值
            value3: 第三個值
            
        Returns:
            觸發結果
        """
        url = f"/{event_name}/with/key/{self.webhook_key}"
        
        data = {}
        if value1 is not None:
            data["value1"] = value1
        if value2 is not None:
            data["value2"] = value2
        if value3 is not None:
            data["value3"] = value3
        
        return self.post(url, json=data)
    
    def trigger_event_with_json(self, event_name: str, json_data: Dict[str, Any]) -> Dict[str, Any]:
        """使用 JSON 數據觸發 IFTTT 事件
        
        Args:
            event_name: 事件名稱
            json_data: JSON 數據
            
        Returns:
            觸發結果
        """
        url = f"/{event_name}/with/key/{self.webhook_key}"
        return self.post(url, json=json_data)
    
    def trigger_event_with_form(self, event_name: str, form_data: Dict[str, Any]) -> Dict[str, Any]:
        """使用表單數據觸發 IFTTT 事件
        
        Args:
            event_name: 事件名稱
            form_data: 表單數據
            
        Returns:
            觸發結果
        """
        url = f"/{event_name}/with/key/{self.webhook_key}"
        return self.post(url, data=form_data)
    
    def trigger_event_with_xml(self, event_name: str, xml_data: str) -> Dict[str, Any]:
        """使用 XML 數據觸發 IFTTT 事件
        
        Args:
            event_name: 事件名稱
            xml_data: XML 數據
            
        Returns:
            觸發結果
        """
        url = f"/{event_name}/with/key/{self.webhook_key}"
        headers = {"Content-Type": "application/xml"}
        return self.post(url, data=xml_data, headers=headers)
    
    def trigger_event_with_text(self, event_name: str, text_data: str) -> Dict[str, Any]:
        """使用純文本數據觸發 IFTTT 事件
        
        Args:
            event_name: 事件名稱
            text_data: 純文本數據
            
        Returns:
            觸發結果
        """
        url = f"/{event_name}/with/key/{self.webhook_key}"
        headers = {"Content-Type": "text/plain"}
        return self.post(url, data=text_data, headers=headers)
    
    def trigger_event_with_binary(self, event_name: str, binary_data: bytes, content_type: str) -> Dict[str, Any]:
        """使用二進制數據觸發 IFTTT 事件
        
        Args:
            event_name: 事件名稱
            binary_data: 二進制數據
            content_type: 內容類型
            
        Returns:
            觸發結果
        """
        url = f"/{event_name}/with/key/{self.webhook_key}"
        headers = {"Content-Type": content_type}
        return self.post(url, data=binary_data, headers=headers)
    
    def trigger_event_with_file(self, event_name: str, file_path: str, content_type: Optional[str] = None) -> Dict[str, Any]:
        """使用文件觸發 IFTTT 事件
        
        Args:
            event_name: 事件名稱
            file_path: 文件路徑
            content_type: 內容類型（可選）
            
        Returns:
            觸發結果
        """
        url = f"/{event_name}/with/key/{self.webhook_key}"
        
        with open(file_path, "rb") as f:
            file_data = f.read()
        
        if content_type is None:
            content_type = self.utils.guess_content_type(file_path)
        
        headers = {"Content-Type": content_type}
        return self.post(url, data=file_data, headers=headers) 