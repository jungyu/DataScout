"""
日誌記錄模組

提供日誌記錄功能
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from typing import Optional
from selenium_base.core.exceptions import LoggerError
from selenium_base.core.utils import Utils

class Logger:
    """日誌記錄類別"""
    
    def __init__(self, name: str, log_dir: str = 'logs', level: str = 'INFO'):
        """初始化日誌記錄類別
        
        Args:
            name: 日誌記錄器名稱
            log_dir: 日誌檔案目錄
            level: 日誌等級
        """
        self.name = name
        self.log_dir = log_dir
        self.level = level
        self.logger = logging.getLogger(name)
        self._setup_logger()
    
    def _setup_logger(self) -> None:
        """設定日誌記錄器"""
        try:
            # 設定日誌等級
            self.logger.setLevel(getattr(logging, self.level.upper()))
            
            # 建立日誌目錄
            Utils.ensure_dir(self.log_dir)
            
            # 設定檔案處理器
            log_file = os.path.join(self.log_dir, f'{self.name}.log')
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
            
            # 設定控制台處理器
            console_handler = logging.StreamHandler()
            
            # 設定格式
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            # 添加處理器
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
            
        except Exception as e:
            raise LoggerError(f'設定日誌記錄器失敗: {e}')
    
    def debug(self, message: str) -> None:
        """記錄除錯訊息
        
        Args:
            message: 訊息內容
        """
        self.logger.debug(message)
    
    def info(self, message: str) -> None:
        """記錄資訊訊息
        
        Args:
            message: 訊息內容
        """
        self.logger.info(message)
    
    def warning(self, message: str) -> None:
        """記錄警告訊息
        
        Args:
            message: 訊息內容
        """
        self.logger.warning(message)
    
    def error(self, message: str) -> None:
        """記錄錯誤訊息
        
        Args:
            message: 訊息內容
        """
        self.logger.error(message)
    
    def critical(self, message: str) -> None:
        """記錄嚴重錯誤訊息
        
        Args:
            message: 訊息內容
        """
        self.logger.critical(message)
    
    def exception(self, message: str) -> None:
        """記錄異常訊息
        
        Args:
            message: 訊息內容
        """
        self.logger.exception(message)
    
    def set_level(self, level: str) -> None:
        """設定日誌等級
        
        Args:
            level: 日誌等級
        """
        try:
            self.logger.setLevel(getattr(logging, level.upper()))
            self.level = level
        except Exception as e:
            raise LoggerError(f'設定日誌等級失敗: {e}')
    
    def get_level(self) -> str:
        """取得日誌等級
        
        Returns:
            日誌等級
        """
        return self.level
    
    def add_file_handler(self, filename: str, level: Optional[str] = None) -> None:
        """添加檔案處理器
        
        Args:
            filename: 檔案名稱
            level: 日誌等級
        """
        try:
            log_file = os.path.join(self.log_dir, filename)
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
            
            if level:
                file_handler.setLevel(getattr(logging, level.upper()))
            
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            
            self.logger.addHandler(file_handler)
            
        except Exception as e:
            raise LoggerError(f'添加檔案處理器失敗: {e}')
    
    def remove_handler(self, handler: logging.Handler) -> None:
        """移除處理器
        
        Args:
            handler: 處理器
        """
        try:
            self.logger.removeHandler(handler)
        except Exception as e:
            raise LoggerError(f'移除處理器失敗: {e}')
    
    def clear_handlers(self) -> None:
        """清除所有處理器"""
        try:
            for handler in self.logger.handlers[:]:
                self.logger.removeHandler(handler)
        except Exception as e:
            raise LoggerError(f'清除處理器失敗: {e}') 