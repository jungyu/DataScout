#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
檢測處理器

此模組提供檢測處理的功能，包括：
1. 檢測結果分析
2. 檢測策略調整
3. 檢測迴避
4. 檢測報告
"""

import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from .base_error import BaseError, handle_error, retry_on_error
from .configs.anti_detection_config import AntiDetectionConfig

class DetectionError(BaseError):
    """檢測錯誤"""
    pass

class DetectionResult:
    """檢測結果"""
    
    def __init__(
        self,
        success: bool,
        detection_type: str,
        confidence: float,
        details: Dict[str, Any],
        timestamp: Optional[datetime] = None
    ):
        """
        初始化檢測結果
        
        Args:
            success: 是否成功
            detection_type: 檢測類型
            confidence: 置信度
            details: 詳細信息
            timestamp: 時間戳
        """
        self.success = success
        self.detection_type = detection_type
        self.confidence = confidence
        self.details = details
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "success": self.success,
            "detection_type": self.detection_type,
            "confidence": self.confidence,
            "details": self.details,
            "timestamp": self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DetectionResult":
        """從字典創建實例"""
        return cls(
            success=data["success"],
            detection_type=data["detection_type"],
            confidence=data["confidence"],
            details=data["details"],
            timestamp=datetime.fromisoformat(data["timestamp"])
        )

class DetectionHandler:
    """檢測處理器"""
    
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化檢測處理器
        
        Args:
            config: 配置字典
            logger: 日誌記錄器
        """
        self.logger = logger or logging.getLogger(__name__)
        self.config = AntiDetectionConfig.from_dict(config or {})
        if not self.config.validate():
            raise DetectionError("無效的檢測配置")
        
        self.detection_history: List[DetectionResult] = []
        self.detection_stats: Dict[str, Dict[str, int]] = {}
    
    @handle_error
    def check_detection(
        self,
        driver: WebDriver,
        url: str
    ) -> DetectionResult:
        """
        檢查是否被檢測
        
        Args:
            driver: WebDriver實例
            url: 目標URL
            
        Returns:
            檢測結果
        """
        # 檢查頁面標題
        title = driver.title.lower()
        if any(keyword in title for keyword in ["captcha", "robot", "verify"]):
            return DetectionResult(
                success=False,
                detection_type="title",
                confidence=0.9,
                details={"title": title}
            )
        
        # 檢查URL
        if any(keyword in url.lower() for keyword in ["captcha", "robot", "verify"]):
            return DetectionResult(
                success=False,
                detection_type="url",
                confidence=0.9,
                details={"url": url}
            )
        
        # 檢查頁面內容
        page_source = driver.page_source.lower()
        if any(keyword in page_source for keyword in ["captcha", "robot", "verify"]):
            return DetectionResult(
                success=False,
                detection_type="content",
                confidence=0.8,
                details={"keywords": ["captcha", "robot", "verify"]}
            )
        
        # 檢查JavaScript變量
        js_vars = driver.execute_script("""
            return {
                navigator: window.navigator.userAgent,
                platform: window.navigator.platform,
                language: window.navigator.language,
                webdriver: window.navigator.webdriver
            };
        """)
        
        if js_vars.get("webdriver"):
            return DetectionResult(
                success=False,
                detection_type="javascript",
                confidence=0.7,
                details={"js_vars": js_vars}
            )
        
        # 檢查Cookie
        cookies = driver.get_cookies()
        if any(cookie.get("name", "").lower() in ["captcha", "robot", "verify"] for cookie in cookies):
            return DetectionResult(
                success=False,
                detection_type="cookie",
                confidence=0.6,
                details={"cookies": cookies}
            )
        
        # 檢查請求頭
        headers = driver.execute_script("return window.performance.getEntries();")
        if any(entry.get("name", "").lower() in ["captcha", "robot", "verify"] for entry in headers):
            return DetectionResult(
                success=False,
                detection_type="headers",
                confidence=0.5,
                details={"headers": headers}
            )
        
        # 未檢測到異常
        return DetectionResult(
            success=True,
            detection_type="none",
            confidence=1.0,
            details={}
        )
    
    @handle_error
    def handle_detection(
        self,
        driver: WebDriver,
        result: DetectionResult
    ) -> bool:
        """
        處理檢測結果
        
        Args:
            driver: WebDriver實例
            result: 檢測結果
            
        Returns:
            是否成功處理
        """
        # 記錄檢測結果
        self.detection_history.append(result)
        self._update_stats(result)
        
        # 如果檢測成功，直接返回
        if result.success:
            return True
        
        # 根據檢測類型處理
        if result.detection_type == "title":
            return self._handle_title_detection(driver)
        elif result.detection_type == "url":
            return self._handle_url_detection(driver)
        elif result.detection_type == "content":
            return self._handle_content_detection(driver)
        elif result.detection_type == "javascript":
            return self._handle_javascript_detection(driver)
        elif result.detection_type == "cookie":
            return self._handle_cookie_detection(driver)
        elif result.detection_type == "headers":
            return self._handle_headers_detection(driver)
        
        return False
    
    def _handle_title_detection(self, driver: WebDriver) -> bool:
        """處理標題檢測"""
        # 嘗試修改標題
        driver.execute_script("document.title = 'Normal Page';")
        return True
    
    def _handle_url_detection(self, driver: WebDriver) -> bool:
        """處理URL檢測"""
        # 嘗試修改URL
        driver.execute_script("window.history.pushState({}, '', '/');")
        return True
    
    def _handle_content_detection(self, driver: WebDriver) -> bool:
        """處理內容檢測"""
        # 嘗試移除檢測相關元素
        driver.execute_script("""
            document.querySelectorAll('*').forEach(function(element) {
                if (element.textContent.toLowerCase().includes('captcha') ||
                    element.textContent.toLowerCase().includes('robot') ||
                    element.textContent.toLowerCase().includes('verify')) {
                    element.remove();
                }
            });
        """)
        return True
    
    def _handle_javascript_detection(self, driver: WebDriver) -> bool:
        """處理JavaScript檢測"""
        # 嘗試修改JavaScript變量
        driver.execute_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: function() { return undefined; }
            });
        """)
        return True
    
    def _handle_cookie_detection(self, driver: WebDriver) -> bool:
        """處理Cookie檢測"""
        # 嘗試刪除檢測相關Cookie
        cookies = driver.get_cookies()
        for cookie in cookies:
            if cookie.get("name", "").lower() in ["captcha", "robot", "verify"]:
                driver.delete_cookie(cookie["name"])
        return True
    
    def _handle_headers_detection(self, driver: WebDriver) -> bool:
        """處理請求頭檢測"""
        # 嘗試修改請求頭
        driver.execute_script("""
            window.performance.getEntries = function() {
                return [];
            };
        """)
        return True
    
    def _update_stats(self, result: DetectionResult):
        """更新統計信息"""
        if result.detection_type not in self.detection_stats:
            self.detection_stats[result.detection_type] = {
                "total": 0,
                "success": 0,
                "failure": 0
            }
        
        stats = self.detection_stats[result.detection_type]
        stats["total"] += 1
        if result.success:
            stats["success"] += 1
        else:
            stats["failure"] += 1
    
    def get_detection_report(self) -> Dict[str, Any]:
        """獲取檢測報告"""
        return {
            "total_detections": len(self.detection_history),
            "success_rate": sum(1 for r in self.detection_history if r.success) / len(self.detection_history),
            "detection_types": self.detection_stats,
            "recent_detections": [r.to_dict() for r in self.detection_history[-10:]]
        }