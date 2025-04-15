#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
基礎配置模組

此模組提供爬蟲的基礎配置類。
"""

import os
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass, field

@dataclass
class BaseConfig:
    """基礎配置類"""
    
    data_dir: str = field(default="data")  # 數據目錄
    browser: Dict[str, Any] = field(default_factory=dict)  # 瀏覽器配置
    request: Dict[str, Any] = field(default_factory=dict)  # 請求配置
    anti_detection: Dict[str, Any] = field(default_factory=dict)  # 反偵測配置
    captcha: Dict[str, Any] = field(default_factory=dict)  # 驗證碼配置
    
    def __post_init__(self):
        """初始化後的驗證"""
        self.validate()
        
    def validate(self) -> None:
        """驗證配置"""
        # 驗證數據目錄
        if not isinstance(self.data_dir, str):
            raise ValueError("data_dir 必須是字符串")
            
        # 創建數據目錄
        os.makedirs(self.data_dir, exist_ok=True)
        
        # 驗證瀏覽器配置
        if not isinstance(self.browser, dict):
            raise ValueError("browser 必須是字典")
            
        # 驗證請求配置
        if not isinstance(self.request, dict):
            raise ValueError("request 必須是字典")
            
        # 驗證反偵測配置
        if not isinstance(self.anti_detection, dict):
            raise ValueError("anti_detection 必須是字典")
            
        # 驗證驗證碼配置
        if not isinstance(self.captcha, dict):
            raise ValueError("captcha 必須是字典")
            
    def save(self, file_path: str) -> None:
        """
        保存配置到文件
        
        Args:
            file_path: 文件路徑
        """
        # 創建目錄
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # 轉換為字典
        config_dict = {
            "data_dir": self.data_dir,
            "browser": self.browser,
            "request": self.request,
            "anti_detection": self.anti_detection,
            "captcha": self.captcha,
        }
        
        # 保存到文件
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(config_dict, f, indent=4, ensure_ascii=False)
            
    @classmethod
    def load(cls, file_path: str) -> "BaseConfig":
        """
        從文件加載配置
        
        Args:
            file_path: 文件路徑
            
        Returns:
            配置實例
        """
        # 檢查文件是否存在
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"配置文件不存在: {file_path}")
            
        # 讀取文件
        with open(file_path, "r", encoding="utf-8") as f:
            config_dict = json.load(f)
            
        # 創建實例
        return cls(**config_dict)
        
    def update(self, config_dict: Dict[str, Any]) -> None:
        """
        更新配置
        
        Args:
            config_dict: 配置字典
        """
        # 更新數據目錄
        if "data_dir" in config_dict:
            self.data_dir = config_dict["data_dir"]
            
        # 更新瀏覽器配置
        if "browser" in config_dict:
            self.browser.update(config_dict["browser"])
            
        # 更新請求配置
        if "request" in config_dict:
            self.request.update(config_dict["request"])
            
        # 更新反偵測配置
        if "anti_detection" in config_dict:
            self.anti_detection.update(config_dict["anti_detection"])
            
        # 更新驗證碼配置
        if "captcha" in config_dict:
            self.captcha.update(config_dict["captcha"])
            
        # 驗證更新後的配置
        self.validate()
        
    def merge(self, other: "BaseConfig") -> None:
        """
        合併另一個配置
        
        Args:
            other: 另一個配置實例
        """
        self.update({
            "data_dir": other.data_dir,
            "browser": other.browser,
            "request": other.request,
            "anti_detection": other.anti_detection,
            "captcha": other.captcha,
        }) 