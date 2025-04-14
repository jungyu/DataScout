"""
檢測處理器

此模組提供檢測處理的功能，包括：
1. 檢測結果分析
2. 檢測策略調整
3. 檢測迴避
4. 檢測報告
"""

import logging
import time
import random
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from selenium_base.anti_detection.base_error import BaseError, handle_error, retry_on_error
from selenium_base.anti_detection.configs.anti_detection_config import AntiDetectionConfig
from selenium_base.anti_detection.fingerprint import BrowserFingerprint
from selenium_base.anti_detection.utils.detection_patterns import DetectionPatterns
from selenium_base.anti_detection.utils.detection_analyzer import DetectionAnalyzer
from selenium_base.anti_detection.utils.detection_evasion import DetectionEvasion


class DetectionError(BaseError):
    """檢測錯誤"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        初始化檢測錯誤
        
        Args:
            message: 錯誤信息
            details: 詳細信息
        """
        super().__init__(code=400, message=message, details=details)


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
        
        # 確保配置包含 id
        if config is None:
            config = {}
        if "id" not in config:
            config["id"] = "detection_handler"
            
        self.config = AntiDetectionConfig.from_dict(config)
        if not self.config.validate():
            raise DetectionError("無效的檢測配置")
        
        # 初始化各個模組
        self.fingerprint = BrowserFingerprint(
            id=f"{self.config.id}_fingerprint",
            logger=self.logger
        )
        self.patterns = DetectionPatterns(
            config=self.config.get("pattern_config", {}),
            logger=self.logger
        )
        self.analyzer = DetectionAnalyzer(
            config=self.config.get("analyzer_config", {}),
            logger=self.logger
        )
        self.evasion = DetectionEvasion(
            config=self.config.get("evasion_config", {}),
            logger=self.logger
        )
        
        self.detection_history: List[DetectionResult] = []
        self.detection_stats: Dict[str, Dict[str, int]] = {}
        
        self.logger.info(f"檢測處理器 {self.config.id} 初始化完成")
    
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
        # 使用檢測模式進行檢查
        detection_result = self.patterns.check_patterns(driver, url)
        if detection_result:
            return detection_result
        
        # 使用分析器進行深入分析
        analysis_result = self.analyzer.analyze(driver, url)
        if analysis_result:
            return analysis_result
        
        # 如果沒有檢測到，返回成功結果
        return DetectionResult(
            success=True,
            detection_type="none",
            confidence=1.0,
            details={"url": url}
        )
    
    @handle_error
    def handle_detection(self, driver: WebDriver) -> bool:
        """
        處理被檢測的情況
        
        Args:
            driver: WebDriver實例
            
        Returns:
            是否成功處理
        """
        # 獲取當前URL
        url = driver.current_url
        
        # 檢查檢測類型
        detection_result = self.check_detection(driver, url)
        if detection_result.success:
            return True
        
        # 記錄檢測結果
        self.detection_history.append(detection_result)
        self._update_stats(detection_result)
        
        # 根據檢測類型選擇迴避策略
        evasion_strategy = self.evasion.get_strategy(detection_result)
        if not evasion_strategy:
            self.logger.warning(f"未找到適合的迴避策略: {detection_result.detection_type}")
            return False
        
        # 執行迴避策略
        try:
            success = evasion_strategy.execute(driver)
            if success:
                self.logger.info(f"成功執行迴避策略: {evasion_strategy.name}")
            else:
                self.logger.warning(f"迴避策略執行失敗: {evasion_strategy.name}")
            return success
        
        except Exception as e:
            self.logger.error(f"執行迴避策略時發生錯誤: {str(e)}")
            return False
    
    def _update_stats(self, result: DetectionResult):
        """更新檢測統計信息"""
        detection_type = result.detection_type
        if detection_type not in self.detection_stats:
            self.detection_stats[detection_type] = {
                "total": 0,
                "success": 0,
                "failure": 0
            }
        
        stats = self.detection_stats[detection_type]
        stats["total"] += 1
        if result.success:
            stats["success"] += 1
        else:
            stats["failure"] += 1
    
    def get_detection_stats(self) -> Dict[str, Dict[str, int]]:
        """獲取檢測統計信息"""
        return self.detection_stats
    
    def get_detection_history(self) -> List[DetectionResult]:
        """獲取檢測歷史記錄"""
        return self.detection_history 