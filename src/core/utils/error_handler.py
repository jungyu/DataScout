#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
錯誤處理工具模組

提供統一的錯誤處理和異常管理功能。
支持自定義異常類和錯誤處理策略。
支持錯誤分類、統計、恢復和通知。
"""

import logging
import traceback
import json
import time
import smtplib
import requests
import os
import sys
import platform
import psutil
from typing import Optional, Type, Callable, Dict, Any, Union, List, Tuple
from functools import wraps
from datetime import datetime
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class ScraperError(Exception):
    """爬蟲基礎異常類"""
    pass

class ConfigError(ScraperError):
    """配置相關異常"""
    pass

class BrowserError(ScraperError):
    """瀏覽器操作相關異常"""
    pass

class NetworkError(ScraperError):
    """網絡相關異常"""
    pass

class DataError(ScraperError):
    """數據處理相關異常"""
    pass

class ErrorHandler:
    """錯誤處理工具類"""
    
    def __init__(
        self,
        logger: Optional[logging.Logger] = None,
        error_dir: Optional[str] = None,
        notification_config: Optional[Dict[str, Any]] = None
    ):
        """
        初始化錯誤處理器
        
        Args:
            logger: 日誌記錄器
            error_dir: 錯誤報告目錄
            notification_config: 通知配置
        """
        self.logger = logger or logging.getLogger(__name__)
        self.error_handlers: Dict[Type[Exception], Callable] = {}
        self.default_handler: Optional[Callable] = None
        self.error_dir = error_dir or "errors"
        self.notification_config = notification_config
        self.error_stats: Dict[str, int] = {}
        self.error_history: List[Dict[str, Any]] = []
        self.error_categories: Dict[str, List[str]] = {
            'network': ['ConnectionError', 'Timeout', 'NetworkError'],
            'browser': ['WebDriverException', 'BrowserError'],
            'data': ['ValueError', 'KeyError', 'DataError'],
            'config': ['ConfigError'],
            'system': ['OSError', 'IOError']
        }
        os.makedirs(self.error_dir, exist_ok=True)
        
    def register_handler(
        self,
        exception_type: Type[Exception],
        handler: Callable[[Exception, Any], None]
    ) -> None:
        """
        註冊異常處理器
        
        Args:
            exception_type: 異常類型
            handler: 處理函數
        """
        self.error_handlers[exception_type] = handler
        
    def set_default_handler(self, handler: Callable[[Exception, Any], None]) -> None:
        """
        設置默認異常處理器
        
        Args:
            handler: 處理函數
        """
        self.default_handler = handler
        
    def handle_error(self, error: Exception, context: Any = None) -> None:
        """
        處理異常
        
        Args:
            error: 異常實例
            context: 上下文信息
        """
        # 更新錯誤統計
        error_type = type(error).__name__
        self.error_stats[error_type] = self.error_stats.get(error_type, 0) + 1
        
        # 記錄錯誤歷史
        error_record = {
            'timestamp': datetime.now().isoformat(),
            'type': error_type,
            'message': str(error),
            'traceback': traceback.format_exc(),
            'context': str(context) if context else None,
            'category': self._get_error_category(error_type),
            'system_info': self._get_system_info()
        }
        self.error_history.append(error_record)
        
        # 查找匹配的處理器
        for exception_type, handler in self.error_handlers.items():
            if isinstance(error, exception_type):
                try:
                    handler(error, context)
                    return
                except Exception as e:
                    self.logger.error(f"處理異常時出錯: {str(e)}")
                    
        # 使用默認處理器
        if self.default_handler:
            try:
                self.default_handler(error, context)
            except Exception as e:
                self.logger.error(f"默認處理器出錯: {str(e)}")
                
        # 記錄未處理的異常
        self.logger.error(f"未處理的異常: {str(error)}")
        self.logger.debug(f"異常堆棧: {traceback.format_exc()}")
        
        # 發送錯誤通知
        self._send_notification(error, context)
        
    def handle_errors(self, context: Any = None) -> Callable:
        """
        異常處理裝飾器
        
        Args:
            context: 上下文信息
            
        Returns:
            裝飾器函數
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    self.handle_error(e, context)
                    raise
            return wrapper
        return decorator
        
    def retry_on_error(
        self,
        max_retries: int = 3,
        delay: float = 1.0,
        exceptions: Union[Type[Exception], tuple] = Exception,
        backoff_factor: float = 2.0
    ) -> Callable:
        """
        重試裝飾器
        
        Args:
            max_retries: 最大重試次數
            delay: 重試延遲時間(秒)
            exceptions: 需要重試的異常類型
            backoff_factor: 退避因子
            
        Returns:
            裝飾器函數
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                last_error = None
                current_delay = delay
                
                for attempt in range(max_retries):
                    try:
                        return func(*args, **kwargs)
                    except exceptions as e:
                        last_error = e
                        if attempt < max_retries - 1:
                            self.logger.warning(
                                f"操作失敗 (嘗試 {attempt + 1}/{max_retries}): {str(e)}"
                            )
                            time.sleep(current_delay)
                            current_delay *= backoff_factor
                raise last_error
            return wrapper
        return decorator
        
    def safe_call(
        self,
        func: Callable,
        *args,
        default: Any = None,
        **kwargs
    ) -> Any:
        """
        安全調用函數
        
        Args:
            func: 要調用的函數
            default: 出錯時的默認返回值
            args: 位置參數
            kwargs: 關鍵字參數
            
        Returns:
            函數返回值或默認值
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            self.handle_error(e)
            return default
            
    def log_error(self, error: Exception, message: Optional[str] = None) -> None:
        """
        記錄錯誤
        
        Args:
            error: 異常實例
            message: 自定義消息
        """
        error_type = type(error).__name__
        error_msg = message or str(error)
        self.logger.error(f"{error_type}: {error_msg}")
        self.logger.debug(f"異常堆棧: {traceback.format_exc()}")
        
    def is_retryable_error(self, error: Exception) -> bool:
        """
        判斷錯誤是否可重試
        
        Args:
            error: 異常實例
            
        Returns:
            是否可重試
        """
        retryable_errors = (
            NetworkError,
            TimeoutError,
            ConnectionError,
            requests.exceptions.RequestException
        )
        return isinstance(error, retryable_errors)
        
    def get_error_details(self, error: Exception) -> Dict[str, Any]:
        """
        獲取錯誤詳細信息
        
        Args:
            error: 異常實例
            
        Returns:
            錯誤詳細信息
        """
        return {
            'type': type(error).__name__,
            'message': str(error),
            'traceback': traceback.format_exc(),
            'category': self._get_error_category(type(error).__name__),
            'timestamp': datetime.now().isoformat(),
            'system_info': self._get_system_info()
        }
        
    def get_error_stats(self) -> Dict[str, Any]:
        """
        獲取錯誤統計信息
        
        Returns:
            錯誤統計信息
        """
        stats = {
            'total_errors': sum(self.error_stats.values()),
            'error_types': self.error_stats,
            'categories': {},
            'recent_errors': self.error_history[-10:] if self.error_history else []
        }
        
        # 按類別統計
        for category, error_types in self.error_categories.items():
            count = sum(
                self.error_stats.get(error_type, 0)
                for error_type in error_types
            )
            stats['categories'][category] = count
            
        return stats
        
    def clear_error_history(self) -> None:
        """清除錯誤歷史記錄"""
        self.error_history.clear()
        self.error_stats.clear()
        
    def save_error_report(self, filename: Optional[str] = None) -> str:
        """
        保存錯誤報告
        
        Args:
            filename: 報告文件名，如果為None則自動生成
            
        Returns:
            報告文件路徑
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"error_report_{timestamp}.json"
            
        filepath = os.path.join(self.error_dir, filename)
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'stats': self.get_error_stats(),
            'history': self.error_history,
            'system_info': self._get_system_info()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        return filepath
        
    def _send_notification(self, error: Exception, context: Any = None) -> None:
        """
        發送錯誤通知
        
        Args:
            error: 異常實例
            context: 上下文信息
        """
        if not self.notification_config:
            return
            
        try:
            if 'email' in self.notification_config:
                self._send_email_notification(error, context)
            if 'webhook' in self.notification_config:
                self._send_webhook_notification(error, context)
        except Exception as e:
            self.logger.error(f"發送錯誤通知失敗: {str(e)}")
            
    def _send_email_notification(self, error: Exception, context: Any = None) -> None:
        """
        發送郵件通知
        
        Args:
            error: 異常實例
            context: 上下文信息
        """
        if not self.notification_config.get('email'):
            return
            
        email_config = self.notification_config['email']
        msg = MIMEMultipart()
        msg['From'] = email_config['from']
        msg['To'] = email_config['to']
        msg['Subject'] = f"錯誤通知: {type(error).__name__}"
        
        body = f"""
        錯誤類型: {type(error).__name__}
        錯誤信息: {str(error)}
        發生時間: {datetime.now().isoformat()}
        上下文信息: {context if context else '無'}
        
        堆棧跟踪:
        {traceback.format_exc()}
        
        系統信息:
        {json.dumps(self._get_system_info(), indent=2, ensure_ascii=False)}
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        try:
            with smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port']) as server:
                if email_config.get('use_tls'):
                    server.starttls()
                if 'username' in email_config and 'password' in email_config:
                    server.login(email_config['username'], email_config['password'])
                server.send_message(msg)
        except Exception as e:
            self.logger.error(f"發送郵件通知失敗: {str(e)}")
            
    def _send_webhook_notification(self, error: Exception, context: Any = None) -> None:
        """
        發送Webhook通知
        
        Args:
            error: 異常實例
            context: 上下文信息
        """
        if not self.notification_config.get('webhook'):
            return
            
        webhook_config = self.notification_config['webhook']
        payload = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'timestamp': datetime.now().isoformat(),
            'context': str(context) if context else None,
            'traceback': traceback.format_exc(),
            'system_info': self._get_system_info()
        }
        
        try:
            response = requests.post(
                webhook_config['url'],
                json=payload,
                headers=webhook_config.get('headers', {}),
                timeout=webhook_config.get('timeout', 5)
            )
            response.raise_for_status()
        except Exception as e:
            self.logger.error(f"發送Webhook通知失敗: {str(e)}")
            
    def get_recovery_strategy(self, error: Exception) -> Optional[Dict[str, Any]]:
        """
        獲取錯誤恢復策略
        
        Args:
            error: 異常實例
            
        Returns:
            恢復策略，如果沒有則返回None
        """
        error_type = type(error).__name__
        category = self._get_error_category(error_type)
        
        strategies = {
            'network': {
                'action': 'retry',
                'max_retries': 3,
                'delay': 5,
                'backoff_factor': 2
            },
            'browser': {
                'action': 'restart',
                'cleanup': True,
                'reload_config': True
            },
            'data': {
                'action': 'skip',
                'log_error': True,
                'continue': True
            },
            'config': {
                'action': 'reload',
                'fallback': 'default'
            },
            'system': {
                'action': 'exit',
                'save_state': True,
                'notify': True
            }
        }
        
        return strategies.get(category)
        
    def _get_error_category(self, error_type: str) -> str:
        """
        獲取錯誤類別
        
        Args:
            error_type: 錯誤類型名稱
            
        Returns:
            錯誤類別
        """
        for category, error_types in self.error_categories.items():
            if error_type in error_types:
                return category
        return 'unknown'
        
    def _get_system_info(self) -> Dict[str, Any]:
        """
        獲取系統信息
        
        Returns:
            系統信息
        """
        return {
            'platform': platform.platform(),
            'python_version': sys.version,
            'cpu_count': psutil.cpu_count(),
            'memory_total': psutil.virtual_memory().total,
            'memory_available': psutil.virtual_memory().available,
            'disk_usage': psutil.disk_usage('/').percent,
            'process_id': os.getpid(),
            'process_memory': psutil.Process().memory_info().rss
        } 