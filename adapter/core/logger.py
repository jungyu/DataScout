#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
日誌系統
提供更多的日誌級別和更詳細的日誌信息
"""

import logging
import logging.handlers
import json
import os
import sys
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from pathlib import Path

class LoggerManager:
    """日誌管理器"""
    
    def __init__(
        self,
        name: str = "datascout",
        level: Union[str, int] = logging.INFO,
        format: Optional[str] = None,
        file_path: Optional[str] = None,
        max_bytes: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5
    ):
        """
        初始化日誌管理器
        
        Args:
            name: 日誌名稱
            level: 日誌級別
            format: 日誌格式
            file_path: 日誌文件路徑
            max_bytes: 最大文件大小
            backup_count: 備份文件數量
        """
        self.name = name
        self.level = level if isinstance(level, int) else getattr(logging, level.upper())
        self.format = format or (
            "%(asctime)s - %(name)s - %(levelname)s - "
            "%(filename)s:%(lineno)d - %(funcName)s - %(message)s"
        )
        self.file_path = file_path
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.level)
        
        # 設置控制台處理器
        self._setup_console_handler()
        
        # 設置文件處理器
        if file_path:
            self._setup_file_handler()
            
    def _setup_console_handler(self) -> None:
        """設置控制台處理器"""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.level)
        console_handler.setFormatter(logging.Formatter(self.format))
        self.logger.addHandler(console_handler)
        
    def _setup_file_handler(self) -> None:
        """設置文件處理器"""
        # 確保日誌目錄存在
        log_dir = os.path.dirname(self.file_path)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
            
        file_handler = logging.handlers.RotatingFileHandler(
            self.file_path,
            maxBytes=self.max_bytes,
            backupCount=self.backup_count
        )
        file_handler.setLevel(self.level)
        file_handler.setFormatter(logging.Formatter(self.format))
        self.logger.addHandler(file_handler)
        
    def add_file_handler(
        self,
        file_path: str,
        level: Optional[Union[str, int]] = None,
        format: Optional[str] = None,
        max_bytes: Optional[int] = None,
        backup_count: Optional[int] = None
    ) -> None:
        """
        添加文件處理器
        
        Args:
            file_path: 日誌文件路徑
            level: 日誌級別
            format: 日誌格式
            max_bytes: 最大文件大小
            backup_count: 備份文件數量
        """
        level = level if isinstance(level, int) else getattr(logging, (level or "INFO").upper())
        format = format or self.format
        max_bytes = max_bytes or self.max_bytes
        backup_count = backup_count or self.backup_count
        
        # 確保日誌目錄存在
        log_dir = os.path.dirname(file_path)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
            
        file_handler = logging.handlers.RotatingFileHandler(
            file_path,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(logging.Formatter(format))
        self.logger.addHandler(file_handler)
        
    def remove_file_handler(self, file_path: str) -> None:
        """
        移除文件處理器
        
        Args:
            file_path: 日誌文件路徑
        """
        for handler in self.logger.handlers[:]:
            if isinstance(handler, logging.handlers.RotatingFileHandler):
                if handler.baseFilename == file_path:
                    self.logger.removeHandler(handler)
                    
    def debug(self, message: str, **kwargs: Any) -> None:
        """
        記錄調試日誌
        
        Args:
            message: 日誌訊息
            **kwargs: 額外參數
        """
        self.logger.debug(self._format_message(message, **kwargs))
        
    def info(self, message: str, **kwargs: Any) -> None:
        """
        記錄信息日誌
        
        Args:
            message: 日誌訊息
            **kwargs: 額外參數
        """
        self.logger.info(self._format_message(message, **kwargs))
        
    def warning(self, message: str, **kwargs: Any) -> None:
        """
        記錄警告日誌
        
        Args:
            message: 日誌訊息
            **kwargs: 額外參數
        """
        self.logger.warning(self._format_message(message, **kwargs))
        
    def error(self, message: str, **kwargs: Any) -> None:
        """
        記錄錯誤日誌
        
        Args:
            message: 日誌訊息
            **kwargs: 額外參數
        """
        self.logger.error(self._format_message(message, **kwargs))
        
    def critical(self, message: str, **kwargs: Any) -> None:
        """
        記錄嚴重錯誤日誌
        
        Args:
            message: 日誌訊息
            **kwargs: 額外參數
        """
        self.logger.critical(self._format_message(message, **kwargs))
        
    def exception(self, message: str, **kwargs: Any) -> None:
        """
        記錄異常日誌
        
        Args:
            message: 日誌訊息
            **kwargs: 額外參數
        """
        self.logger.exception(self._format_message(message, **kwargs))
        
    def _format_message(self, message: str, **kwargs: Any) -> str:
        """
        格式化日誌訊息
        
        Args:
            message: 日誌訊息
            **kwargs: 額外參數
            
        Returns:
            str: 格式化後的訊息
        """
        if not kwargs:
            return message
            
        try:
            # 嘗試將額外參數轉換為 JSON
            extra = json.dumps(kwargs, ensure_ascii=False)
            return f"{message} - {extra}"
        except:
            # 如果無法轉換為 JSON，則使用字符串表示
            extra = str(kwargs)
            return f"{message} - {extra}"
            
    def log_error(self, error: Exception, **kwargs: Any) -> None:
        """
        記錄錯誤
        
        Args:
            error: 錯誤對象
            **kwargs: 額外參數
        """
        error_info = {
            "type": error.__class__.__name__,
            "message": str(error),
            "timestamp": datetime.now().isoformat()
        }
        
        if hasattr(error, "to_dict"):
            error_info.update(error.to_dict())
            
        self.error("發生錯誤", error=error_info, **kwargs)
        
    def log_request(self, method: str, url: str, **kwargs: Any) -> None:
        """
        記錄請求
        
        Args:
            method: 請求方法
            url: 請求 URL
            **kwargs: 額外參數
        """
        request_info = {
            "method": method,
            "url": url,
            "timestamp": datetime.now().isoformat()
        }
        
        self.info("發送請求", request=request_info, **kwargs)
        
    def log_response(self, method: str, url: str, status: int, **kwargs: Any) -> None:
        """
        記錄響應
        
        Args:
            method: 請求方法
            url: 請求 URL
            status: 響應狀態碼
            **kwargs: 額外參數
        """
        response_info = {
            "method": method,
            "url": url,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
        
        if 200 <= status < 300:
            self.info("收到響應", response=response_info, **kwargs)
        elif 300 <= status < 400:
            self.warning("收到重定向響應", response=response_info, **kwargs)
        elif 400 <= status < 500:
            self.error("收到客戶端錯誤響應", response=response_info, **kwargs)
        else:
            self.error("收到服務器錯誤響應", response=response_info, **kwargs)
            
    def log_performance(self, operation: str, duration: float, **kwargs: Any) -> None:
        """
        記錄性能
        
        Args:
            operation: 操作名稱
            duration: 執行時間（秒）
            **kwargs: 額外參數
        """
        performance_info = {
            "operation": operation,
            "duration": duration,
            "timestamp": datetime.now().isoformat()
        }
        
        if duration < 0.1:
            self.debug("性能指標", performance=performance_info, **kwargs)
        elif duration < 1.0:
            self.info("性能指標", performance=performance_info, **kwargs)
        else:
            self.warning("性能指標", performance=performance_info, **kwargs)
            
    def log_state(self, state: str, **kwargs: Any) -> None:
        """
        記錄狀態
        
        Args:
            state: 狀態名稱
            **kwargs: 額外參數
        """
        state_info = {
            "state": state,
            "timestamp": datetime.now().isoformat()
        }
        
        self.info("狀態變更", state=state_info, **kwargs)
        
    def log_metric(self, name: str, value: Union[int, float], **kwargs: Any) -> None:
        """
        記錄指標
        
        Args:
            name: 指標名稱
            value: 指標值
            **kwargs: 額外參數
        """
        metric_info = {
            "name": name,
            "value": value,
            "timestamp": datetime.now().isoformat()
        }
        
        self.info("記錄指標", metric=metric_info, **kwargs)
        
    def log_event(self, event: str, **kwargs: Any) -> None:
        """
        記錄事件
        
        Args:
            event: 事件名稱
            **kwargs: 額外參數
        """
        event_info = {
            "event": event,
            "timestamp": datetime.now().isoformat()
        }
        
        self.info("記錄事件", event=event_info, **kwargs)
        
    def log_security(self, action: str, **kwargs: Any) -> None:
        """
        記錄安全事件
        
        Args:
            action: 安全動作
            **kwargs: 額外參數
        """
        security_info = {
            "action": action,
            "timestamp": datetime.now().isoformat()
        }
        
        self.warning("安全事件", security=security_info, **kwargs)
        
    def log_audit(self, action: str, user: str, **kwargs: Any) -> None:
        """
        記錄審計事件
        
        Args:
            action: 審計動作
            user: 用戶名稱
            **kwargs: 額外參數
        """
        audit_info = {
            "action": action,
            "user": user,
            "timestamp": datetime.now().isoformat()
        }
        
        self.info("審計事件", audit=audit_info, **kwargs)
        
    def log_health(self, status: str, **kwargs: Any) -> None:
        """
        記錄健康狀態
        
        Args:
            status: 健康狀態
            **kwargs: 額外參數
        """
        health_info = {
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
        
        if status == "healthy":
            self.info("健康檢查", health=health_info, **kwargs)
        elif status == "degraded":
            self.warning("健康檢查", health=health_info, **kwargs)
        else:
            self.error("健康檢查", health=health_info, **kwargs)
            
    def log_config(self, config: Dict[str, Any], **kwargs: Any) -> None:
        """
        記錄配置
        
        Args:
            config: 配置信息
            **kwargs: 額外參數
        """
        config_info = {
            "config": config,
            "timestamp": datetime.now().isoformat()
        }
        
        self.info("配置更新", config=config_info, **kwargs)
        
    def log_dependency(self, name: str, status: str, **kwargs: Any) -> None:
        """
        記錄依賴狀態
        
        Args:
            name: 依賴名稱
            status: 依賴狀態
            **kwargs: 額外參數
        """
        dependency_info = {
            "name": name,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
        
        if status == "up":
            self.info("依賴狀態", dependency=dependency_info, **kwargs)
        elif status == "degraded":
            self.warning("依賴狀態", dependency=dependency_info, **kwargs)
        else:
            self.error("依賴狀態", dependency=dependency_info, **kwargs)
            
    def log_resource(self, name: str, usage: float, **kwargs: Any) -> None:
        """
        記錄資源使用
        
        Args:
            name: 資源名稱
            usage: 使用率
            **kwargs: 額外參數
        """
        resource_info = {
            "name": name,
            "usage": usage,
            "timestamp": datetime.now().isoformat()
        }
        
        if usage < 0.7:
            self.debug("資源使用", resource=resource_info, **kwargs)
        elif usage < 0.9:
            self.warning("資源使用", resource=resource_info, **kwargs)
        else:
            self.error("資源使用", resource=resource_info, **kwargs)
            
    def log_cache(self, operation: str, **kwargs: Any) -> None:
        """
        記錄快取操作
        
        Args:
            operation: 快取操作
            **kwargs: 額外參數
        """
        cache_info = {
            "operation": operation,
            "timestamp": datetime.now().isoformat()
        }
        
        self.debug("快取操作", cache=cache_info, **kwargs)
        
    def log_transaction(self, operation: str, **kwargs: Any) -> None:
        """
        記錄事務操作
        
        Args:
            operation: 事務操作
            **kwargs: 額外參數
        """
        transaction_info = {
            "operation": operation,
            "timestamp": datetime.now().isoformat()
        }
        
        self.info("事務操作", transaction=transaction_info, **kwargs)
        
    def log_validation(self, field: str, error: str, **kwargs: Any) -> None:
        """
        記錄驗證錯誤
        
        Args:
            field: 欄位名稱
            error: 錯誤信息
            **kwargs: 額外參數
        """
        validation_info = {
            "field": field,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        
        self.error("驗證錯誤", validation=validation_info, **kwargs)
        
    def log_encryption(self, operation: str, **kwargs: Any) -> None:
        """
        記錄加密操作
        
        Args:
            operation: 加密操作
            **kwargs: 額外參數
        """
        encryption_info = {
            "operation": operation,
            "timestamp": datetime.now().isoformat()
        }
        
        self.debug("加密操作", encryption=encryption_info, **kwargs)
        
    def log_compression(self, operation: str, **kwargs: Any) -> None:
        """
        記錄壓縮操作
        
        Args:
            operation: 壓縮操作
            **kwargs: 額外參數
        """
        compression_info = {
            "operation": operation,
            "timestamp": datetime.now().isoformat()
        }
        
        self.debug("壓縮操作", compression=compression_info, **kwargs)
        
    def log_rate_limit(self, limit: int, remaining: int, **kwargs: Any) -> None:
        """
        記錄速率限制
        
        Args:
            limit: 限制值
            remaining: 剩餘值
            **kwargs: 額外參數
        """
        rate_limit_info = {
            "limit": limit,
            "remaining": remaining,
            "timestamp": datetime.now().isoformat()
        }
        
        if remaining < limit * 0.1:
            self.warning("速率限制", rate_limit=rate_limit_info, **kwargs)
        else:
            self.debug("速率限制", rate_limit=rate_limit_info, **kwargs)
            
    def log_permission(self, action: str, user: str, **kwargs: Any) -> None:
        """
        記錄權限操作
        
        Args:
            action: 權限動作
            user: 用戶名稱
            **kwargs: 額外參數
        """
        permission_info = {
            "action": action,
            "user": user,
            "timestamp": datetime.now().isoformat()
        }
        
        self.info("權限操作", permission=permission_info, **kwargs)
        
    def log_cleanup(self, operation: str, **kwargs: Any) -> None:
        """
        記錄清理操作
        
        Args:
            operation: 清理操作
            **kwargs: 額外參數
        """
        cleanup_info = {
            "operation": operation,
            "timestamp": datetime.now().isoformat()
        }
        
        self.info("清理操作", cleanup=cleanup_info, **kwargs) 