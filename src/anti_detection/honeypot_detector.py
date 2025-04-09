#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
蜜罐檢測器

此模組提供蜜罐檢測的功能，包括：
1. 蜜罐元素檢測
2. 蜜罐行為檢測
3. 蜜罐特徵分析
4. 蜜罐迴避
"""

import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By

from .base_error import BaseError, handle_error, retry_on_error
from .configs.honeypot_config import HoneypotConfig

class HoneypotError(BaseError):
    """蜜罐錯誤"""
    pass

class HoneypotResult:
    """蜜罐檢測結果"""
    
    def __init__(
        self,
        is_honeypot: bool,
        honeypot_type: str,
        confidence: float,
        details: Dict[str, Any],
        timestamp: Optional[datetime] = None
    ):
        """
        初始化蜜罐檢測結果
        
        Args:
            is_honeypot: 是否為蜜罐
            honeypot_type: 蜜罐類型
            confidence: 置信度
            details: 詳細信息
            timestamp: 時間戳
        """
        self.is_honeypot = is_honeypot
        self.honeypot_type = honeypot_type
        self.confidence = confidence
        self.details = details
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "is_honeypot": self.is_honeypot,
            "honeypot_type": self.honeypot_type,
            "confidence": self.confidence,
            "details": self.details,
            "timestamp": self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HoneypotResult":
        """從字典創建實例"""
        return cls(
            is_honeypot=data["is_honeypot"],
            honeypot_type=data["honeypot_type"],
            confidence=data["confidence"],
            details=data["details"],
            timestamp=datetime.fromisoformat(data["timestamp"])
        )

class HoneypotDetector:
    """蜜罐檢測器"""
    
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化蜜罐檢測器
        
        Args:
            config: 配置字典
            logger: 日誌記錄器
        """
        self.logger = logger or logging.getLogger(__name__)
        self.config = HoneypotConfig.from_dict(config or {})
        if not self.config.validate():
            raise HoneypotError("無效的蜜罐配置")
        
        self.detection_history: List[HoneypotResult] = []
        self.detection_stats: Dict[str, Dict[str, int]] = {}
    
    @handle_error
    def check_honeypot(
        self,
        driver: WebDriver,
        element: Optional[WebElement] = None
    ) -> HoneypotResult:
        """
        檢查是否為蜜罐
        
        Args:
            driver: WebDriver實例
            element: 要檢查的元素
            
        Returns:
            蜜罐檢測結果
        """
        # 檢查隱藏元素
        if self._check_hidden_elements(driver):
            return HoneypotResult(
                is_honeypot=True,
                honeypot_type="hidden",
                confidence=0.9,
                details={"reason": "發現隱藏元素"}
            )
        
        # 檢查不可見元素
        if self._check_invisible_elements(driver):
            return HoneypotResult(
                is_honeypot=True,
                honeypot_type="invisible",
                confidence=0.8,
                details={"reason": "發現不可見元素"}
            )
        
        # 檢查透明元素
        if self._check_transparent_elements(driver):
            return HoneypotResult(
                is_honeypot=True,
                honeypot_type="transparent",
                confidence=0.7,
                details={"reason": "發現透明元素"}
            )
        
        # 檢查重疊元素
        if self._check_overlapping_elements(driver):
            return HoneypotResult(
                is_honeypot=True,
                honeypot_type="overlapping",
                confidence=0.6,
                details={"reason": "發現重疊元素"}
            )
        
        # 檢查表單蜜罐
        if self._check_form_honeypot(driver):
            return HoneypotResult(
                is_honeypot=True,
                honeypot_type="form",
                confidence=0.5,
                details={"reason": "發現表單蜜罐"}
            )
        
        # 未檢測到蜜罐
        return HoneypotResult(
            is_honeypot=False,
            honeypot_type="none",
            confidence=1.0,
            details={}
        )
    
    def _check_hidden_elements(self, driver: WebDriver) -> bool:
        """檢查隱藏元素"""
        hidden_selectors = [
            "input[type='hidden']",
            "input[style*='display: none']",
            "input[style*='visibility: hidden']",
            "input[style*='opacity: 0']"
        ]
        
        for selector in hidden_selectors:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                return True
        
        return False
    
    def _check_invisible_elements(self, driver: WebDriver) -> bool:
        """檢查不可見元素"""
        invisible_selectors = [
            "input[style*='position: absolute']",
            "input[style*='left: -9999px']",
            "input[style*='top: -9999px']"
        ]
        
        for selector in invisible_selectors:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                return True
        
        return False
    
    def _check_transparent_elements(self, driver: WebDriver) -> bool:
        """檢查透明元素"""
        transparent_selectors = [
            "input[style*='opacity: 0']",
            "input[style*='transparent']"
        ]
        
        for selector in transparent_selectors:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                return True
        
        return False
    
    def _check_overlapping_elements(self, driver: WebDriver) -> bool:
        """檢查重疊元素"""
        script = """
        function isOverlapping(element) {
            const rect = element.getBoundingClientRect();
            const elements = document.elementsFromPoint(
                rect.left + rect.width / 2,
                rect.top + rect.height / 2
            );
            return elements.length > 1;
        }
        
        const inputs = document.querySelectorAll('input');
        for (const input of inputs) {
            if (isOverlapping(input)) {
                return true;
            }
        }
        return false;
        """
        
        return driver.execute_script(script)
    
    def _check_form_honeypot(self, driver: WebDriver) -> bool:
        """檢查表單蜜罐"""
        honeypot_indicators = [
            "input[name*='honeypot']",
            "input[id*='honeypot']",
            "input[class*='honeypot']",
            "input[data-honeypot]",
            "input[aria-hidden='true']"
        ]
        
        for selector in honeypot_indicators:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                return True
        
        return False
    
    @handle_error
    def handle_honeypot(
        self,
        driver: WebDriver,
        result: HoneypotResult
    ) -> bool:
        """
        處理蜜罐
        
        Args:
            driver: WebDriver實例
            result: 蜜罐檢測結果
            
        Returns:
            是否成功處理
        """
        # 記錄檢測結果
        self.detection_history.append(result)
        self._update_stats(result)
        
        # 如果不是蜜罐，直接返回
        if not result.is_honeypot:
            return True
        
        # 根據蜜罐類型處理
        if result.honeypot_type == "hidden":
            return self._handle_hidden_honeypot(driver)
        elif result.honeypot_type == "invisible":
            return self._handle_invisible_honeypot(driver)
        elif result.honeypot_type == "transparent":
            return self._handle_transparent_honeypot(driver)
        elif result.honeypot_type == "overlapping":
            return self._handle_overlapping_honeypot(driver)
        elif result.honeypot_type == "form":
            return self._handle_form_honeypot(driver)
        
        return False
    
    def _handle_hidden_honeypot(self, driver: WebDriver) -> bool:
        """處理隱藏蜜罐"""
        script = """
        document.querySelectorAll('input[type="hidden"]').forEach(function(element) {
            element.remove();
        });
        """
        driver.execute_script(script)
        return True
    
    def _handle_invisible_honeypot(self, driver: WebDriver) -> bool:
        """處理不可見蜜罐"""
        script = """
        document.querySelectorAll('input[style*="position: absolute"]').forEach(function(element) {
            element.remove();
        });
        """
        driver.execute_script(script)
        return True
    
    def _handle_transparent_honeypot(self, driver: WebDriver) -> bool:
        """處理透明蜜罐"""
        script = """
        document.querySelectorAll('input[style*="opacity: 0"]').forEach(function(element) {
            element.remove();
        });
        """
        driver.execute_script(script)
        return True
    
    def _handle_overlapping_honeypot(self, driver: WebDriver) -> bool:
        """處理重疊蜜罐"""
        script = """
        function removeOverlappingElements() {
            const inputs = document.querySelectorAll('input');
            inputs.forEach(function(input) {
                const rect = input.getBoundingClientRect();
                const elements = document.elementsFromPoint(
                    rect.left + rect.width / 2,
                    rect.top + rect.height / 2
                );
                if (elements.length > 1) {
                    input.remove();
                }
            });
        }
        removeOverlappingElements();
        """
        driver.execute_script(script)
        return True
    
    def _handle_form_honeypot(self, driver: WebDriver) -> bool:
        """處理表單蜜罐"""
        script = """
        document.querySelectorAll('input[name*="honeypot"], input[id*="honeypot"], input[class*="honeypot"], input[data-honeypot], input[aria-hidden="true"]').forEach(function(element) {
            element.remove();
        });
        """
        driver.execute_script(script)
        return True
    
    def _update_stats(self, result: HoneypotResult):
        """更新統計信息"""
        if result.honeypot_type not in self.detection_stats:
            self.detection_stats[result.honeypot_type] = {
                "total": 0,
                "detected": 0,
                "handled": 0
            }
        
        stats = self.detection_stats[result.honeypot_type]
        stats["total"] += 1
        if result.is_honeypot:
            stats["detected"] += 1
        else:
            stats["handled"] += 1
    
    def get_honeypot_report(self) -> Dict[str, Any]:
        """獲取蜜罐檢測報告"""
        return {
            "total_detections": len(self.detection_history),
            "detection_rate": sum(1 for r in self.detection_history if r.is_honeypot) / len(self.detection_history),
            "honeypot_types": self.detection_stats,
            "recent_detections": [r.to_dict() for r in self.detection_history[-10:]]
        }