#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
驗證碼基礎配置模組

提供驗證碼相關的基礎配置
"""

import os
import json
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field

from ...core.config import BaseConfig
from ...core.utils import Utils
from ...core.logger import setup_logger

logger = setup_logger(__name__)

@dataclass
class DetectionConfig:
    """檢測配置"""
    enabled: bool = False
    check_image: bool = True
    check_text: bool = True
    check_slider: bool = True
    check_audio: bool = True
    check_recaptcha: bool = True
    check_hcaptcha: bool = True
    detection_threshold: float = 0.8
    detection_timeout: int = 10

@dataclass
class RecognitionConfig:
    """識別配置"""
    enabled: bool = False
    use_ocr: bool = True
    use_ml: bool = True
    use_api: bool = False
    api_key: Optional[str] = None
    api_url: Optional[str] = None
    recognition_timeout: int = 30
    recognition_threshold: float = 0.9

@dataclass
class SolverConfig:
    """求解配置"""
    enabled: bool = False
    use_local: bool = True
    use_remote: bool = False
    remote_url: Optional[str] = None
    remote_key: Optional[str] = None
    solver_timeout: int = 60
    max_retries: int = 3

@dataclass
class ValidationConfig:
    """驗證配置"""
    enabled: bool = False
    validate_input: bool = True
    validate_output: bool = True
    validation_timeout: int = 10
    validation_threshold: float = 0.95

@dataclass
class CaptchaConfig(BaseConfig):
    """驗證碼配置"""
    detection: DetectionConfig = field(default_factory=DetectionConfig)
    recognition: RecognitionConfig = field(default_factory=RecognitionConfig)
    solver: SolverConfig = field(default_factory=SolverConfig)
    validation: ValidationConfig = field(default_factory=ValidationConfig)
    
    def save(self, path: str) -> None:
        """
        保存配置到文件
        
        Args:
            path: 文件路徑
        """
        try:
            Utils.ensure_dir(os.path.dirname(path))
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=4, ensure_ascii=False)
            logger.info(f"配置已保存到：{path}")
        except Exception as e:
            logger.error(f"保存配置失敗：{str(e)}")
            raise
            
    def load(self, path: str) -> None:
        """
        從文件加載配置
        
        Args:
            path: 文件路徑
        """
        try:
            with open(path, 'r', encoding='utf-8') as f:
                config_dict = json.load(f)
            self.__dict__.update(self.from_dict(config_dict).__dict__)
            logger.info(f"配置已從 {path} 加載")
        except Exception as e:
            logger.error(f"加載配置失敗：{str(e)}")
            raise
            
    def validate(self) -> bool:
        """
        驗證配置
        
        Returns:
            配置是否有效
        """
        try:
            # 驗證檢測配置
            if self.detection.enabled:
                if not isinstance(self.detection.detection_threshold, float):
                    return False
                if not isinstance(self.detection.detection_timeout, int):
                    return False
                    
            # 驗證識別配置
            if self.recognition.enabled:
                if self.recognition.use_api:
                    if not self.recognition.api_key or not self.recognition.api_url:
                        return False
                        
            # 驗證求解配置
            if self.solver.enabled:
                if self.solver.use_remote:
                    if not self.solver.remote_url or not self.solver.remote_key:
                        return False
                        
            # 驗證驗證配置
            if self.validation.enabled:
                if not isinstance(self.validation.validation_threshold, float):
                    return False
                if not isinstance(self.validation.validation_timeout, int):
                    return False
                    
            return True
        except Exception as e:
            logger.error(f"驗證配置失敗：{str(e)}")
            return False
            
    def merge(self, other: Union[Dict, 'CaptchaConfig']) -> None:
        """
        合併配置
        
        Args:
            other: 要合併的配置
        """
        if isinstance(other, dict):
            other = self.from_dict(other)
        self.__dict__.update(other.__dict__)
    
    def to_dict(self) -> Dict:
        """轉換為字典"""
        return {
            "detection": {
                "enabled": self.detection.enabled,
                "check_image": self.detection.check_image,
                "check_text": self.detection.check_text,
                "check_slider": self.detection.check_slider,
                "check_audio": self.detection.check_audio,
                "check_recaptcha": self.detection.check_recaptcha,
                "check_hcaptcha": self.detection.check_hcaptcha,
                "detection_threshold": self.detection.detection_threshold,
                "detection_timeout": self.detection.detection_timeout,
            },
            "recognition": {
                "enabled": self.recognition.enabled,
                "use_ocr": self.recognition.use_ocr,
                "use_ml": self.recognition.use_ml,
                "use_api": self.recognition.use_api,
                "api_key": self.recognition.api_key,
                "api_url": self.recognition.api_url,
                "recognition_timeout": self.recognition.recognition_timeout,
                "recognition_threshold": self.recognition.recognition_threshold,
            },
            "solver": {
                "enabled": self.solver.enabled,
                "use_local": self.solver.use_local,
                "use_remote": self.solver.use_remote,
                "remote_url": self.solver.remote_url,
                "remote_key": self.solver.remote_key,
                "solver_timeout": self.solver.solver_timeout,
                "max_retries": self.solver.max_retries,
            },
            "validation": {
                "enabled": self.validation.enabled,
                "validate_input": self.validation.validate_input,
                "validate_output": self.validation.validate_output,
                "validation_timeout": self.validation.validation_timeout,
                "validation_threshold": self.validation.validation_threshold,
            },
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict) -> 'CaptchaConfig':
        """從字典創建配置"""
        detection_config = DetectionConfig(**config_dict.get("detection", {}))
        recognition_config = RecognitionConfig(**config_dict.get("recognition", {}))
        solver_config = SolverConfig(**config_dict.get("solver", {}))
        validation_config = ValidationConfig(**config_dict.get("validation", {}))
        
        return cls(
            detection=detection_config,
            recognition=recognition_config,
            solver=solver_config,
            validation=validation_config,
        ) 