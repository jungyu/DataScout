#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Cookie 管理器

此模組提供 Cookie 管理相關功能，包括：
1. Cookie 的生成和驗證
2. Cookie 池的管理和輪換
3. Cookie 的版本控制
4. Cookie 的統計分析
5. Cookie 的自動更新
6. Cookie 的加密存儲
7. Cookie 的過期管理
8. Cookie 的並發控制
"""

import os
import json
import time
import random
import logging
import hashlib
import base64
import threading
import queue
from typing import Dict, List, Optional, Union, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from .base_error import BaseError, handle_error, retry_on_error
from .configs.cookie_config import CookieConfig, CookiePoolConfig

class CookieError(BaseError):
    """Cookie 錯誤"""
    pass

@dataclass
class CookieResult:
    """Cookie 結果"""
    success: bool
    cookie: Optional[Dict[str, Any]]
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            "success": self.success,
            "cookie": self.cookie,
            "error": self.error,
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }

class CookieManager:
    """
    Cookie 管理器，負責 Cookie 的生成、驗證和管理
    """
    
    def __init__(
        self,
        config_path: str = "config/cookie.json",
        logger: Optional[logging.Logger] = None,
        encryption_key: Optional[str] = None
    ):
        """
        初始化 Cookie 管理器
        
        Args:
            config_path: 配置文件路徑
            logger: 日誌記錄器
            encryption_key: 加密密鑰
        """
        self.logger = logger or logging.getLogger(__name__)
        self.config_path = Path(config_path)
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 初始化加密
        self.encryption_key = encryption_key or self._generate_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # 初始化配置
        self.pool_config = CookiePoolConfig()
        self.cookie_pool: Dict[str, CookieConfig] = {}
        self.cookie_queue: queue.Queue = queue.Queue()
        
        # 初始化鎖
        self._lock = threading.Lock()
        self._load_lock = threading.Lock()
        self._save_lock = threading.Lock()
        
        # 加載配置
        self._load_config()
        
        # 初始化 Cookie 隊列
        self._init_cookie_queue()
        
        # 啟動自動清理線程
        self._start_cleanup_thread()
    
    def _generate_encryption_key(self) -> bytes:
        """生成加密密鑰"""
        salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000
        )
        key = base64.urlsafe_b64encode(kdf.derive(os.urandom(32)))
        return key
    
    @handle_error
    def _load_config(self):
        """加載配置"""
        with self._load_lock:
            try:
                if self.config_path.exists():
                    with open(self.config_path, 'rb') as f:
                        encrypted_data = f.read()
                    decrypted_data = self.cipher_suite.decrypt(encrypted_data)
                    data = json.loads(decrypted_data)
                    
                    self.pool_config = CookiePoolConfig.from_dict(data.get('pool_config', {}))
                    self.cookie_pool = {
                        k: CookieConfig.from_dict(v)
                        for k, v in data.get('cookie_pool', {}).items()
                    }
                    
                    self.logger.info(f"已加載 {len(self.cookie_pool)} 個 Cookie 配置")
            except Exception as e:
                self.logger.error(f"加載配置失敗: {str(e)}")
                raise CookieError("加載配置失敗") from e
    
    @handle_error
    def _save_config(self):
        """保存配置"""
        with self._save_lock:
            try:
                data = {
                    'pool_config': self.pool_config.to_dict(),
                    'cookie_pool': {
                        k: v.to_dict()
                        for k, v in self.cookie_pool.items()
                    }
                }
                
                encrypted_data = self.cipher_suite.encrypt(
                    json.dumps(data).encode()
                )
                
                with open(self.config_path, 'wb') as f:
                    f.write(encrypted_data)
                
                self.logger.info("配置已保存")
            except Exception as e:
                self.logger.error(f"保存配置失敗: {str(e)}")
                raise CookieError("保存配置失敗") from e
    
    @handle_error
    def add_cookie(self, cookie_config: CookieConfig) -> CookieResult:
        """
        添加 Cookie
        
        Args:
            cookie_config: Cookie 配置
            
        Returns:
            Cookie 結果
        """
        with self._lock:
            try:
                cookie_key = self._generate_cookie_key(cookie_config)
                
                if cookie_key in self.cookie_pool:
                    self.logger.warning(f"Cookie 已存在: {cookie_key}")
                    return CookieResult(
                        success=False,
                        cookie=None,
                        error="Cookie 已存在"
                    )
                
                self.cookie_pool[cookie_key] = cookie_config
                self._save_config()
                self._update_cookie_queue()
                
                self.logger.info(f"已添加 Cookie: {cookie_key}")
                return CookieResult(
                    success=True,
                    cookie=self._generate_cookie(cookie_config),
                    metadata={"cookie_key": cookie_key}
                )
            except Exception as e:
                self.logger.error(f"添加 Cookie 失敗: {str(e)}")
                return CookieResult(
                    success=False,
                    cookie=None,
                    error=str(e)
                )
    
    @handle_error
    def remove_cookie(self, cookie_key: str) -> CookieResult:
        """
        移除 Cookie
        
        Args:
            cookie_key: Cookie 鍵值
            
        Returns:
            Cookie 結果
        """
        with self._lock:
            try:
                if cookie_key not in self.cookie_pool:
                    self.logger.warning(f"Cookie 不存在: {cookie_key}")
                    return CookieResult(
                        success=False,
                        cookie=None,
                        error="Cookie 不存在"
                    )
                
                del self.cookie_pool[cookie_key]
                self._save_config()
                self._update_cookie_queue()
                
                self.logger.info(f"已移除 Cookie: {cookie_key}")
                return CookieResult(
                    success=True,
                    cookie=None,
                    metadata={"cookie_key": cookie_key}
                )
            except Exception as e:
                self.logger.error(f"移除 Cookie 失敗: {str(e)}")
                return CookieResult(
                    success=False,
                    cookie=None,
                    error=str(e)
                )
    
    @handle_error
    def get_cookie(self, domain: str) -> CookieResult:
        """
        獲取 Cookie
        
        Args:
            domain: 域名
            
        Returns:
            Cookie 結果
        """
        try:
            cookie_key = self.cookie_queue.get_nowait()
            cookie_config = self.cookie_pool.get(cookie_key)
            
            if not cookie_config:
                self.logger.warning(f"Cookie 不存在: {cookie_key}")
                return CookieResult(
                    success=False,
                    cookie=None,
                    error="Cookie 不存在"
                )
            
            # 檢查過期
            if cookie_config.expiry and time.time() > cookie_config.expiry:
                self.logger.warning(f"Cookie 已過期: {cookie_key}")
                self.remove_cookie(cookie_key)
                return CookieResult(
                    success=False,
                    cookie=None,
                    error="Cookie 已過期"
                )
            
            # 更新使用統計
            cookie_config.last_used = int(time.time())
            cookie_config.use_count += 1
            self._save_config()
            
            # 將 Cookie 放回隊列
            self.cookie_queue.put(cookie_key)
            
            self.logger.debug(f"已獲取 Cookie: {cookie_key}")
            return CookieResult(
                success=True,
                cookie=self._generate_cookie(cookie_config),
                metadata={"cookie_key": cookie_key}
            )
        except queue.Empty:
            self.logger.warning("Cookie 隊列為空")
            return CookieResult(
                success=False,
                cookie=None,
                error="Cookie 隊列為空"
            )
        except Exception as e:
            self.logger.error(f"獲取 Cookie 失敗: {str(e)}")
            return CookieResult(
                success=False,
                cookie=None,
                error=str(e)
            )
    
    def _init_cookie_queue(self):
        """初始化 Cookie 隊列"""
        with self._lock:
            try:
                # 清空隊列
                while not self.cookie_queue.empty():
                    self.cookie_queue.get_nowait()
                
                # 添加有效的 Cookie
                for cookie_key, cookie_config in self.cookie_pool.items():
                    if not cookie_config.expiry or time.time() <= cookie_config.expiry:
                        self.cookie_queue.put(cookie_key)
                
                self.logger.info(f"已初始化 Cookie 隊列，共 {self.cookie_queue.qsize()} 個")
            except Exception as e:
                self.logger.error(f"初始化 Cookie 隊列失敗: {str(e)}")
                raise CookieError("初始化 Cookie 隊列失敗") from e
    
    def _update_cookie_queue(self):
        """更新 Cookie 隊列"""
        self._init_cookie_queue()
    
    def _generate_cookie_key(self, cookie_config: CookieConfig) -> str:
        """
        生成 Cookie 鍵值
        
        Args:
            cookie_config: Cookie 配置
            
        Returns:
            Cookie 鍵值
        """
        data = f"{cookie_config.domain}:{cookie_config.path}:{cookie_config.name}"
        return hashlib.sha256(data.encode()).hexdigest()
    
    def _generate_cookie(self, cookie_config: CookieConfig) -> Dict[str, Any]:
        """
        生成 Cookie
        
        Args:
            cookie_config: Cookie 配置
            
        Returns:
            Cookie 字典
        """
        return {
            "name": cookie_config.name,
            "value": cookie_config.value,
            "domain": cookie_config.domain,
            "path": cookie_config.path,
            "secure": cookie_config.secure,
            "httpOnly": cookie_config.http_only,
            "sameSite": cookie_config.same_site,
            "expiry": cookie_config.expiry
        }
    
    @handle_error
    def update_cookie_stats(self, cookie_key: str, success: bool) -> CookieResult:
        """
        更新 Cookie 統計
        
        Args:
            cookie_key: Cookie 鍵值
            success: 是否成功
            
        Returns:
            Cookie 結果
        """
        with self._lock:
            try:
                cookie_config = self.cookie_pool.get(cookie_key)
                if not cookie_config:
                    return CookieResult(
                        success=False,
                        cookie=None,
                        error="Cookie 不存在"
                    )
                
                if success:
                    cookie_config.success_count += 1
                else:
                    cookie_config.fail_count += 1
                
                self._save_config()
                
                return CookieResult(
                    success=True,
                    cookie=None,
                    metadata={
                        "cookie_key": cookie_key,
                        "success_rate": cookie_config.success_rate
                    }
                )
            except Exception as e:
                self.logger.error(f"更新 Cookie 統計失敗: {str(e)}")
                return CookieResult(
                    success=False,
                    cookie=None,
                    error=str(e)
                )
    
    @handle_error
    def get_cookie_stats(self) -> CookieResult:
        """
        獲取 Cookie 統計
        
        Returns:
            Cookie 結果
        """
        try:
            stats = []
            for cookie_key, cookie_config in self.cookie_pool.items():
                stats.append({
                    "cookie_key": cookie_key,
                    "domain": cookie_config.domain,
                    "name": cookie_config.name,
                    "use_count": cookie_config.use_count,
                    "success_count": cookie_config.success_count,
                    "fail_count": cookie_config.fail_count,
                    "success_rate": cookie_config.success_rate,
                    "created_at": cookie_config.created_at,
                    "last_used": cookie_config.last_used,
                    "expiry": cookie_config.expiry
                })
            
            return CookieResult(
                success=True,
                cookie=None,
                metadata={"stats": stats}
            )
        except Exception as e:
            self.logger.error(f"獲取 Cookie 統計失敗: {str(e)}")
            return CookieResult(
                success=False,
                cookie=None,
                error=str(e)
            )
    
    def _start_cleanup_thread(self):
        """啟動清理線程"""
        def cleanup_task():
            while True:
                try:
                    time.sleep(3600)  # 每小時檢查一次
                    self._cleanup_expired_cookies()
                except Exception as e:
                    self.logger.error(f"清理過期 Cookie 失敗: {str(e)}")
        
        thread = threading.Thread(target=cleanup_task, daemon=True)
        thread.start()
    
    @handle_error
    def _cleanup_expired_cookies(self):
        """清理過期 Cookie"""
        with self._lock:
            try:
                current_time = time.time()
                expired_keys = [
                    k for k, v in self.cookie_pool.items()
                    if v.expiry and current_time > v.expiry
                ]
                
                for key in expired_keys:
                    del self.cookie_pool[key]
                
                if expired_keys:
                    self._save_config()
                    self._update_cookie_queue()
                    self.logger.info(f"已清理 {len(expired_keys)} 個過期 Cookie")
            except Exception as e:
                self.logger.error(f"清理過期 Cookie 失敗: {str(e)}")
                raise CookieError("清理過期 Cookie 失敗") from e
    
    @handle_error
    def cleanup(self):
        """清理資源"""
        try:
            self._save_config()
            self.logger.info("資源已清理")
        except Exception as e:
            self.logger.error(f"清理資源失敗: {str(e)}")
            raise CookieError("清理資源失敗") from e
    
    def __enter__(self):
        """上下文管理器入口"""
        return this
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        this.cleanup() 