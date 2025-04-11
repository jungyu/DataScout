"""
驗證碼處理器模組
提供驗證碼相關的存儲和處理功能
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

from .base_handler import StorageHandler
from src.captcha.types import CaptchaType
from src.captcha import CaptchaManager
from src.core.utils.logger import setup_logger

class CaptchaDetectionResult:
    """驗證碼檢測結果"""
    def __init__(self, 
                 captcha_type: CaptchaType,
                 confidence: float,
                 location: Dict[str, int],
                 metadata: Optional[Dict[str, Any]] = None):
        self.captcha_type = captcha_type
        self.confidence = confidence
        self.location = location
        self.metadata = metadata or {}
        self.timestamp = datetime.now()

class CaptchaHandler(StorageHandler):
    """驗證碼處理器"""
    
    def __init__(self, config: Dict[str, Any], logger: Optional[logging.Logger] = None):
        """
        初始化驗證碼處理器
        
        Args:
            config: 配置字典
            logger: 日誌記錄器
        """
        super().__init__(config)
        self.logger = logger or setup_logger(__name__)
        self.captcha_manager = None
        self._init_storage()
        
    def _init_storage(self) -> None:
        """初始化存儲"""
        try:
            # 創建存儲目錄
            self.storage_dir = Path(self.config.get("storage_dir", "data/captcha"))
            self.storage_dir.mkdir(parents=True, exist_ok=True)
            
            # 創建子目錄
            self.detection_dir = self.storage_dir / "detections"
            self.solution_dir = self.storage_dir / "solutions"
            self.backup_dir = self.storage_dir / "backups"
            
            for dir_path in [self.detection_dir, self.solution_dir, self.backup_dir]:
                dir_path.mkdir(exist_ok=True)
                
        except Exception as e:
            self.logger.error(f"初始化存儲失敗: {str(e)}")
            raise
            
    def set_captcha_manager(self, manager: CaptchaManager) -> None:
        """
        設置驗證碼管理器
        
        Args:
            manager: 驗證碼管理器實例
        """
        self.captcha_manager = manager
        
    def save_detection_result(self, result: CaptchaDetectionResult) -> bool:
        """
        保存驗證碼檢測結果
        
        Args:
            result: 檢測結果
            
        Returns:
            是否保存成功
        """
        try:
            if not self.detection_dir.exists():
                self.detection_dir.mkdir(parents=True)
                
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"detection_{timestamp}.json"
            filepath = self.detection_dir / filename
            
            # 準備數據
            data = {
                "captcha_type": result.captcha_type.value,
                "confidence": result.confidence,
                "location": result.location,
                "metadata": result.metadata,
                "timestamp": result.timestamp.isoformat()
            }
            
            # 保存到文件
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            self.logger.info(f"驗證碼檢測結果已保存到: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"保存驗證碼檢測結果失敗: {str(e)}")
            return False
            
    def save_solution_result(self, 
                           captcha_type: CaptchaType,
                           success: bool,
                           metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        保存驗證碼解決結果
        
        Args:
            captcha_type: 驗證碼類型
            success: 是否成功
            metadata: 額外信息
            
        Returns:
            是否保存成功
        """
        try:
            if not self.solution_dir.exists():
                self.solution_dir.mkdir(parents=True)
                
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"solution_{timestamp}.json"
            filepath = self.solution_dir / filename
            
            # 準備數據
            data = {
                "captcha_type": captcha_type.value,
                "success": success,
                "metadata": metadata or {},
                "timestamp": datetime.now().isoformat()
            }
            
            # 保存到文件
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            self.logger.info(f"驗證碼解決結果已保存到: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"保存驗證碼解決結果失敗: {str(e)}")
            return False
            
    def get_detection_history(self, 
                            captcha_type: Optional[CaptchaType] = None,
                            limit: int = 100) -> List[Dict[str, Any]]:
        """
        獲取檢測歷史
        
        Args:
            captcha_type: 驗證碼類型過濾
            limit: 返回結果數量限制
            
        Returns:
            檢測歷史列表
        """
        try:
            results = []
            for filepath in sorted(self.detection_dir.glob("*.json"), reverse=True):
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                if captcha_type and data["captcha_type"] != captcha_type.value:
                    continue
                    
                results.append(data)
                if len(results) >= limit:
                    break
                    
            return results
            
        except Exception as e:
            self.logger.error(f"獲取檢測歷史失敗: {str(e)}")
            return []
            
    def get_solution_history(self,
                           captcha_type: Optional[CaptchaType] = None,
                           success_only: bool = False,
                           limit: int = 100) -> List[Dict[str, Any]]:
        """
        獲取解決歷史
        
        Args:
            captcha_type: 驗證碼類型過濾
            success_only: 是否只返回成功的結果
            limit: 返回結果數量限制
            
        Returns:
            解決歷史列表
        """
        try:
            results = []
            for filepath in sorted(self.solution_dir.glob("*.json"), reverse=True):
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                if captcha_type and data["captcha_type"] != captcha_type.value:
                    continue
                    
                if success_only and not data["success"]:
                    continue
                    
                results.append(data)
                if len(results) >= limit:
                    break
                    
            return results
            
        except Exception as e:
            self.logger.error(f"獲取解決歷史失敗: {str(e)}")
            return []
            
    def clear_history(self, days: Optional[int] = None) -> bool:
        """
        清理歷史記錄
        
        Args:
            days: 保留最近幾天的記錄，None 表示清理所有
            
        Returns:
            是否清理成功
        """
        try:
            if days is None:
                # 清理所有記錄
                for filepath in self.detection_dir.glob("*.json"):
                    filepath.unlink()
                for filepath in self.solution_dir.glob("*.json"):
                    filepath.unlink()
            else:
                # 清理指定天數之前的記錄
                cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)
                
                for dir_path in [self.detection_dir, self.solution_dir]:
                    for filepath in dir_path.glob("*.json"):
                        if filepath.stat().st_mtime < cutoff:
                            filepath.unlink()
                            
            self.logger.info(f"已清理歷史記錄 (保留天數: {days if days else '全部'})")
            return True
            
        except Exception as e:
            self.logger.error(f"清理歷史記錄失敗: {str(e)}")
            return False 