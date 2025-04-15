#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
適配器配置類別定義
"""

from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class DatabaseConfig:
    """資料庫配置"""
    
    # 連接配置
    host: str = "localhost"
    port: int = 3306
    username: str = "root"
    password: str = ""
    database: str = "default"
    charset: str = "utf8mb4"
    
    # 連接池配置
    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600
    
    # 超時配置
    connect_timeout: int = 10
    read_timeout: int = 30
    write_timeout: int = 30
    
    # SSL配置
    ssl: bool = False
    ssl_ca: Optional[str] = None
    ssl_cert: Optional[str] = None
    ssl_key: Optional[str] = None
    
    # 其他配置
    autocommit: bool = True
    echo: bool = False

@dataclass
class ValidationConfig:
    """驗證配置"""
    
    # 驗證規則
    rules: Dict[str, Any] = field(default_factory=dict)
    
    # 驗證選項
    strict: bool = True
    skip_unknown: bool = False
    strip_whitespace: bool = True
    
    # 錯誤處理
    raise_on_error: bool = True
    collect_errors: bool = False
    max_errors: int = 100

@dataclass
class TransformationConfig:
    """轉換配置"""
    
    # 轉換規則
    rules: Dict[str, Any] = field(default_factory=dict)
    
    # 轉換選項
    preserve_original: bool = False
    skip_errors: bool = False
    default_values: Dict[str, Any] = field(default_factory=dict)
    
    # 性能配置
    batch_size: int = 1000
    max_workers: int = 4
    chunk_size: int = 10000

@dataclass
class LoggingConfig:
    """日誌配置"""
    
    # 日誌級別
    level: str = "INFO"
    
    # 日誌格式
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"
    
    # 檔案配置
    file_path: Optional[Path] = None
    max_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    
    # 控制台配置
    console: bool = True
    color: bool = True

@dataclass
class PluginConfig:
    """插件配置"""
    
    # 插件路徑
    plugin_dir: Path = Path("plugins")
    
    # 插件選項
    enabled: List[str] = field(default_factory=list)
    disabled: List[str] = field(default_factory=list)
    
    # 插件設置
    settings: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AdapterConfig:
    """適配器配置"""
    
    # 基本配置
    name: str = "default"
    version: str = "1.0.0"
    description: str = ""
    
    # 資料庫配置
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    
    # 驗證配置
    validation: ValidationConfig = field(default_factory=ValidationConfig)
    
    # 轉換配置
    transformation: TransformationConfig = field(default_factory=TransformationConfig)
    
    # 日誌配置
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    
    # 插件配置
    plugin: PluginConfig = field(default_factory=PluginConfig)
    
    # 其他配置
    debug: bool = False
    test_mode: bool = False
    cache_enabled: bool = True
    cache_ttl: int = 3600
    
    def validate(self) -> None:
        """
        驗證配置
        
        Raises:
            ConfigurationError: 配置錯誤
        """
        # TODO: 實現配置驗證邏輯
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """
        轉換為字典
        
        Returns:
            Dict[str, Any]: 配置字典
        """
        # TODO: 實現配置轉換邏輯
        pass
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AdapterConfig":
        """
        從字典創建配置
        
        Args:
            data: 配置字典
            
        Returns:
            AdapterConfig: 配置實例
        """
        # TODO: 實現配置創建邏輯
        pass

@dataclass
class MongoDBConfig:
    """MongoDB 配置"""
    
    # 連接配置
    host: str = "localhost"
    port: int = 27017
    username: Optional[str] = None
    password: Optional[str] = None
    auth_source: str = "admin"
    
    # 資料庫配置
    database: str = "momoshop"
    collection: str = "products"
    
    # 連接池配置
    max_pool_size: int = 100
    min_pool_size: int = 0
    max_idle_time_ms: int = 30000
    
    # 超時配置
    connect_timeout_ms: int = 5000
    socket_timeout_ms: int = 30000
    server_selection_timeout_ms: int = 5000
    
    # SSL 配置
    ssl: bool = False
    ssl_cert_reqs: str = "CERT_NONE"
    ssl_ca_certs: Optional[str] = None
    ssl_certfile: Optional[str] = None
    ssl_keyfile: Optional[str] = None
    
    # 其他配置
    retry_writes: bool = True
    retry_reads: bool = True
    compressors: list = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        轉換為字典
        
        Returns:
            Dict[str, Any]: 配置字典
        """
        return {
            "host": self.host,
            "port": self.port,
            "username": self.username,
            "password": self.password,
            "authSource": self.auth_source,
            "database": self.database,
            "collection": self.collection,
            "maxPoolSize": self.max_pool_size,
            "minPoolSize": self.min_pool_size,
            "maxIdleTimeMS": self.max_idle_time_ms,
            "connectTimeoutMS": self.connect_timeout_ms,
            "socketTimeoutMS": self.socket_timeout_ms,
            "serverSelectionTimeoutMS": self.server_selection_timeout_ms,
            "ssl": self.ssl,
            "ssl_cert_reqs": self.ssl_cert_reqs,
            "ssl_ca_certs": self.ssl_ca_certs,
            "ssl_certfile": self.ssl_certfile,
            "ssl_keyfile": self.ssl_keyfile,
            "retryWrites": self.retry_writes,
            "retryReads": self.retry_reads,
            "compressors": self.compressors
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MongoDBConfig":
        """
        從字典創建配置
        
        Args:
            data: 配置字典
            
        Returns:
            MongoDBConfig: 配置實例
        """
        return cls(**data)
        
    def validate(self) -> None:
        """
        驗證配置
        
        Raises:
            ValidationError: 驗證錯誤
        """
        if not self.host:
            raise ValidationError("主機不能為空")
            
        if not isinstance(self.port, int) or self.port <= 0:
            raise ValidationError("端口必須為正整數")
            
        if self.username and not self.password:
            raise ValidationError("設置用戶名時必須設置密碼")
            
        if not self.database:
            raise ValidationError("資料庫名稱不能為空")
            
        if not self.collection:
            raise ValidationError("集合名稱不能為空")
            
        if self.max_pool_size < self.min_pool_size:
            raise ValidationError("最大連接池大小不能小於最小連接池大小")
            
        if self.ssl:
            if self.ssl_cert_reqs not in ["CERT_NONE", "CERT_OPTIONAL", "CERT_REQUIRED"]:
                raise ValidationError("無效的 SSL 證書要求")
                
            if self.ssl_cert_reqs == "CERT_REQUIRED" and not self.ssl_ca_certs:
                raise ValidationError("使用 CERT_REQUIRED 時必須提供 CA 證書")
                
            if (self.ssl_certfile and not self.ssl_keyfile) or (not self.ssl_certfile and self.ssl_keyfile):
                raise ValidationError("SSL 證書和密鑰必須同時提供") 