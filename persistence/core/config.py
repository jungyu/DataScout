#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
存儲配置管理模組

提供各種存儲處理器的配置類
"""

import os
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from .exceptions import ConfigError

@dataclass
class BaseConfig:
    """基礎配置類"""
    
    # 基本配置
    storage_type: str = "local"  # 存儲類型
    storage_path: str = "data"   # 存儲路徑
    
    # 序列化配置
    serializer: str = "json"     # 序列化器類型
    encoding: str = "utf-8"      # 編碼方式
    compression: bool = False    # 是否壓縮
    
    # 緩存配置
    cache_enabled: bool = True   # 是否啟用緩存
    cache_ttl: int = 3600       # 緩存過期時間（秒）
    cache_max_size: int = 1000  # 緩存最大條數
    
    # 日誌配置
    log_level: str = "INFO"     # 日誌級別
    log_file: Optional[str] = None  # 日誌文件
    
    def validate(self) -> None:
        """驗證配置"""
        if not self.storage_type:
            raise ConfigError("Storage type cannot be empty")
            
        if not self.storage_path:
            raise ConfigError("Storage path cannot be empty")
            
        if self.serializer not in ["json", "pickle", "yaml"]:
            raise ConfigError(f"Unsupported serializer: {self.serializer}")
            
        if self.encoding not in ["utf-8", "ascii", "latin1"]:
            raise ConfigError(f"Unsupported encoding: {self.encoding}")
            
        if self.cache_ttl < 0:
            raise ConfigError("Cache TTL cannot be negative")
            
        if self.cache_max_size < 0:
            raise ConfigError("Cache max size cannot be negative")
            
        if self.log_level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            raise ConfigError(f"Unsupported log level: {self.log_level}")

@dataclass
class StorageConfig:
    """存儲基礎配置類"""
    
    # 路徑配置
    base_dir: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_dir: str = os.path.join(base_dir, "data")
    logs_dir: str = os.path.join(data_dir, "logs")
    errors_dir: str = os.path.join(data_dir, "errors")
    temp_dir: str = os.path.join(data_dir, "temp")
    
    # 日誌配置
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file: str = os.path.join(logs_dir, "storage.log")
    
    def __post_init__(self):
        """初始化後處理"""
        self._create_directories()
    
    def _create_directories(self):
        """創建必要的目錄"""
        directories = [
            self.data_dir,
            self.logs_dir,
            self.errors_dir,
            self.temp_dir
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """將配置轉換為字典
        
        Returns:
            配置字典
        """
        return {
            "base_dir": self.base_dir,
            "data_dir": self.data_dir,
            "logs_dir": self.logs_dir,
            "errors_dir": self.errors_dir,
            "temp_dir": self.temp_dir,
            "log_level": self.log_level,
            "log_format": self.log_format,
            "log_file": self.log_file
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "StorageConfig":
        """從字典創建配置
        
        Args:
            config_dict: 配置字典
            
        Returns:
            配置實例
        """
        return cls(**config_dict)

@dataclass
class LocalStorageConfig(StorageConfig):
    """本地存儲配置類"""
    
    # 路徑配置
    base_path: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "local")
    
    # 備份配置
    enable_backup: bool = True
    backup_path: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data", "backup")
    backup_interval: int = 3600  # 備份間隔（秒）
    max_backups: int = 10  # 最大備份數量
    
    # 文件配置
    file_extension: str = '.json'  # 文件擴展名
    encoding: str = 'utf-8'  # 文件編碼
    create_dir: bool = True  # 是否自動創建目錄
    
    def __post_init__(self):
        """初始化後的驗證"""
        super().__post_init__()
        self.validate_local_config()
    
    def validate_local_config(self) -> None:
        """
        驗證本地存儲特定配置
        
        Raises:
            ConfigError: 配置參數無效
        """
        if not self.base_path:
            raise ConfigError("本地存儲路徑不能為空")
        if not self.file_extension:
            raise ConfigError("文件擴展名不能為空")
        if not self.encoding:
            raise ConfigError("文件編碼不能為空")
        if self.backup_interval < 0:
            raise ConfigError("備份間隔不能為負數")
        if self.max_backups < 0:
            raise ConfigError("最大備份數量不能為負數")

@dataclass
class FileConfig(StorageConfig):
    """文件存儲配置類"""
    
    # 文件配置
    file_extension: str = '.json'  # 文件擴展名
    encoding: str = 'utf-8'  # 文件編碼
    create_dir: bool = True  # 是否自動創建目錄
    
    def __post_init__(self):
        """初始化後的驗證"""
        super().__post_init__()
        self.validate_file_config()
    
    def validate_file_config(self) -> None:
        """
        驗證文件特定配置
        
        Raises:
            ConfigError: 配置參數無效
        """
        if not self.file_extension:
            raise ConfigError("文件擴展名不能為空")
        if not self.encoding:
            raise ConfigError("文件編碼不能為空")

@dataclass
class MongoDBConfig(StorageConfig):
    """MongoDB配置類"""
    
    # MongoDB連接配置
    host: str = 'localhost'  # 主機
    port: int = 27017  # 端口
    username: str = ''  # 用戶名
    password: str = ''  # 密碼
    auth_source: str = 'admin'  # 認證數據庫
    
    # 數據庫配置
    database: str = 'storage'  # 數據庫名
    collection: str = 'data'  # 集合名
    
    # 連接池配置
    max_pool_size: int = 100  # 最大連接數
    min_pool_size: int = 10  # 最小連接數
    max_idle_time_ms: int = 30000  # 最大空閒時間（毫秒）
    
    def __post_init__(self):
        """初始化後的驗證"""
        super().__post_init__()
        self.validate_mongodb_config()
    
    def validate_mongodb_config(self) -> None:
        """
        驗證MongoDB特定配置
        
        Raises:
            ConfigError: 配置參數無效
        """
        if not self.host:
            raise ConfigError("MongoDB主機不能為空")
        if not self.database:
            raise ConfigError("MongoDB數據庫名不能為空")
        if not self.collection:
            raise ConfigError("MongoDB集合名不能為空")
        if self.max_pool_size < 1:
            raise ConfigError("MongoDB最大連接數必須大於0")
        if self.min_pool_size < 1:
            raise ConfigError("MongoDB最小連接數必須大於0")
        if self.max_idle_time_ms < 0:
            raise ConfigError("MongoDB最大空閒時間不能為負數")

@dataclass
class RedisConfig(StorageConfig):
    """Redis配置類"""
    
    # Redis連接配置
    host: str = 'localhost'  # 主機
    port: int = 6379  # 端口
    username: str = ''  # 用戶名
    password: str = ''  # 密碼
    db: int = 0  # 數據庫索引
    
    # 連接池配置
    max_connections: int = 10  # 最大連接數
    socket_timeout: int = 5  # 套接字超時（秒）
    socket_connect_timeout: int = 5  # 套接字連接超時（秒）
    
    # 序列化配置
    serializer: str = 'json'  # 序列化器
    encoding: str = 'utf-8'  # 編碼
    
    # 鍵前綴配置
    key_prefix: str = ''  # 鍵前綴
    key_separator: str = ':'  # 鍵分隔符
    
    def __post_init__(self):
        """初始化後的驗證"""
        super().__post_init__()
        self.validate_redis_config()
    
    def validate_redis_config(self) -> None:
        """
        驗證Redis特定配置
        
        Raises:
            ConfigError: 配置參數無效
        """
        if not self.host:
            raise ConfigError("Redis主機不能為空")
        if self.max_connections < 1:
            raise ConfigError("Redis最大連接數必須大於0")
        if self.socket_timeout < 0:
            raise ConfigError("Redis套接字超時不能為負數")
        if self.socket_connect_timeout < 0:
            raise ConfigError("Redis套接字連接超時不能為負數")
        if not self.serializer:
            raise ConfigError("Redis序列化器不能為空")
        if not self.encoding:
            raise ConfigError("Redis編碼不能為空")

@dataclass
class MySQLConfig(StorageConfig):
    """MySQL配置類"""
    
    # MySQL連接配置
    host: str = 'localhost'  # 主機
    port: int = 3306  # 端口
    username: str = ''  # 用戶名
    password: str = ''  # 密碼
    database: str = 'storage'  # 數據庫名
    
    # 連接池配置
    pool_size: int = 5  # 連接池大小
    pool_recycle: int = 3600  # 連接回收時間（秒）
    pool_timeout: int = 30  # 連接池超時（秒）
    
    # 字符集配置
    charset: str = 'utf8mb4'  # 字符集
    collation: str = 'utf8mb4_unicode_ci'  # 排序規則
    
    # 表配置
    table_name: str = 'storage'  # 表名
    id_field: str = 'id'  # ID字段名
    data_field: str = 'data'  # 數據字段名
    created_at_field: str = 'created_at'  # 創建時間字段名
    updated_at_field: str = 'updated_at'  # 更新時間字段名
    
    def __post_init__(self):
        """初始化後的驗證"""
        super().__post_init__()
        self.validate_mysql_config()
    
    def validate_mysql_config(self) -> None:
        """
        驗證MySQL特定配置
        
        Raises:
            ConfigError: 配置參數無效
        """
        if not self.host:
            raise ConfigError("MySQL主機不能為空")
        if not self.database:
            raise ConfigError("MySQL數據庫名不能為空")
        if self.pool_size < 1:
            raise ConfigError("MySQL連接池大小必須大於0")
        if self.pool_recycle < 0:
            raise ConfigError("MySQL連接回收時間不能為負數")
        if self.pool_timeout < 0:
            raise ConfigError("MySQL連接池超時不能為負數")
        if not self.charset:
            raise ConfigError("MySQL字符集不能為空")
        if not self.collation:
            raise ConfigError("MySQL排序規則不能為空")
        if not self.table_name:
            raise ConfigError("MySQL表名不能為空")

@dataclass
class SupabaseConfig(StorageConfig):
    """Supabase配置類"""
    
    # Supabase連接配置
    url: str = ''  # Supabase URL
    key: str = ''  # Supabase API Key
    
    # 表配置
    table_name: str = 'storage'  # 表名
    id_field: str = 'id'  # ID字段名
    data_field: str = 'data'  # 數據字段名
    created_at_field: str = 'created_at'  # 創建時間字段名
    updated_at_field: str = 'updated_at'  # 更新時間字段名
    
    # 模式配置
    schema: str = 'public'  # 數據庫模式

    # 日誌開關
    enable_logging: bool = True
    
    def __post_init__(self):
        """初始化後的驗證"""
        super().__post_init__()
        self.validate_supabase_config()
    
    def validate_supabase_config(self) -> None:
        """
        驗證Supabase特定配置
        
        Raises:
            ConfigError: 配置參數無效
        """
        if not self.url:
            raise ConfigError("Supabase URL不能為空")
        if not self.key:
            raise ConfigError("Supabase API Key不能為空")
        if not self.table_name:
            raise ConfigError("表名不能為空")
        if not self.schema:
            raise ConfigError("數據庫模式不能為空")

@dataclass
class SQLServerConfig(StorageConfig):
    """SQL Server配置類"""
    
    # SQL Server連接配置
    host: str = 'localhost'  # 主機
    port: int = 1433  # 端口
    username: str = ''  # 用戶名
    password: str = ''  # 密碼
    database: str = 'storage'  # 數據庫名
    instance: str = ''  # 實例名
    
    # 連接池配置
    pool_size: int = 5  # 連接池大小
    pool_recycle: int = 3600  # 連接回收時間（秒）
    pool_timeout: int = 30  # 連接池超時（秒）
    
    # 字符集配置
    charset: str = 'utf8'  # 字符集
    
    # 表配置
    table_name: str = 'storage'  # 表名
    id_field: str = 'id'  # ID字段名
    data_field: str = 'data'  # 數據字段名
    created_at_field: str = 'created_at'  # 創建時間字段名
    updated_at_field: str = 'updated_at'  # 更新時間字段名
    
    # 模式配置
    schema: str = 'dbo'  # 數據庫模式
    
    def __post_init__(self):
        """初始化後的驗證"""
        super().__post_init__()
        self.validate_sqlserver_config()
    
    def validate_sqlserver_config(self) -> None:
        """
        驗證SQL Server特定配置
        
        Raises:
            ConfigError: 配置參數無效
        """
        if not self.host:
            raise ConfigError("SQL Server主機不能為空")
        if not self.database:
            raise ConfigError("SQL Server數據庫名不能為空")
        if self.pool_size < 1:
            raise ConfigError("SQL Server連接池大小必須大於0")
        if self.pool_recycle < 0:
            raise ConfigError("SQL Server連接回收時間不能為負數")
        if self.pool_timeout < 0:
            raise ConfigError("SQL Server連接池超時不能為負數")
        if not self.charset:
            raise ConfigError("SQL Server字符集不能為空")
        if not self.table_name:
            raise ConfigError("SQL Server表名不能為空")
        if not self.schema:
            raise ConfigError("SQL Server數據庫模式不能為空")

@dataclass
class ElasticsearchConfig(StorageConfig):
    """Elasticsearch配置類"""
    
    # 連接配置
    hosts: List[str] = field(default_factory=lambda: ["localhost:9200"])
    username: str = ""
    password: str = ""
    use_ssl: bool = False
    verify_certs: bool = True
    ca_certs: Optional[str] = None
    client_cert: Optional[str] = None
    client_key: Optional[str] = None
    
    # 索引配置
    index_name: str = "data"
    index_settings: Dict[str, Any] = field(default_factory=dict)
    index_mappings: Dict[str, Any] = field(default_factory=dict)
    
    # 文檔配置
    id_field: str = "id"
    data_field: str = "data"
    created_at_field: str = "created_at"
    updated_at_field: str = "updated_at"
    
    # 連接池配置
    max_retries: int = 3
    retry_on_timeout: bool = True
    timeout: int = 30
    max_connections: int = 100
    max_retry_time: int = 30
    
    # 緩存配置
    cache_ttl: int = 300  # 緩存過期時間（秒）
    cache_size: int = 1000  # 最大緩存條數
    
    def __post_init__(self):
        """初始化後驗證"""
        self.validate_elasticsearch_config()
    
    def validate_elasticsearch_config(self) -> None:
        """驗證Elasticsearch配置"""
        if not self.hosts:
            raise ConfigError("Elasticsearch hosts不能為空")
        
        if not self.index_name:
            raise ConfigError("Elasticsearch index_name不能為空")
        
        if not self.id_field:
            raise ConfigError("Elasticsearch id_field不能為空")
        
        if not self.data_field:
            raise ConfigError("Elasticsearch data_field不能為空")
        
        if not self.created_at_field:
            raise ConfigError("Elasticsearch created_at_field不能為空")
        
        if not self.updated_at_field:
            raise ConfigError("Elasticsearch updated_at_field不能為空")
        
        if self.max_retries < 0:
            raise ConfigError("Elasticsearch max_retries不能為負數")
        
        if self.timeout < 0:
            raise ConfigError("Elasticsearch timeout不能為負數")
        
        if self.max_connections < 0:
            raise ConfigError("Elasticsearch max_connections不能為負數")
        
        if self.max_retry_time < 0:
            raise ConfigError("Elasticsearch max_retry_time不能為負數")
        
        if self.cache_ttl < 0:
            raise ConfigError("Elasticsearch cache_ttl不能為負數")
        
        if self.cache_size < 0:
            raise ConfigError("Elasticsearch cache_size不能為負數")

@dataclass
class ClickHouseConfig(StorageConfig):
    """ClickHouse 存儲配置類"""
    # 連接配置
    host: str = field(default="localhost")
    port: int = field(default=9000)
    username: str = field(default="default")
    password: str = field(default="")
    database: str = field(default="default")
    secure: bool = field(default=False)
    verify: bool = field(default=True)
    
    # 連接池配置
    pool_size: int = field(default=10)
    pool_recycle: int = field(default=3600)
    pool_timeout: int = field(default=30)
    
    # 表配置
    table_name: str = field(default="data")
    id_field: str = field(default="id")
    data_field: str = field(default="data")
    created_at_field: str = field(default="created_at")
    updated_at_field: str = field(default="updated_at")
    
    # 分片配置
    sharding_key: Optional[str] = field(default=None)
    sharding_count: int = field(default=1)
    
    # 分區配置
    partition_by: Optional[str] = field(default=None)
    order_by: Optional[str] = field(default=None)
    
    # 壓縮配置
    compression: str = field(default="lz4")
    
    def __post_init__(self):
        """初始化後驗證"""
        self.validate_clickhouse_config()
    
    def validate_clickhouse_config(self):
        """驗證 ClickHouse 配置"""
        if not self.host:
            raise ConfigError("ClickHouse host cannot be empty")
        
        if not isinstance(self.port, int) or self.port <= 0:
            raise ConfigError("ClickHouse port must be a positive integer")
        
        if not self.database:
            raise ConfigError("ClickHouse database cannot be empty")
        
        if not isinstance(self.pool_size, int) or self.pool_size <= 0:
            raise ConfigError("ClickHouse pool size must be a positive integer")
        
        if not isinstance(self.pool_recycle, int) or self.pool_recycle <= 0:
            raise ConfigError("ClickHouse pool recycle must be a positive integer")
        
        if not isinstance(self.pool_timeout, int) or self.pool_timeout <= 0:
            raise ConfigError("ClickHouse pool timeout must be a positive integer")
        
        if not self.table_name:
            raise ConfigError("ClickHouse table name cannot be empty")
        
        if not isinstance(self.sharding_count, int) or self.sharding_count <= 0:
            raise ConfigError("ClickHouse sharding count must be a positive integer")
        
        if self.compression not in ["lz4", "zstd", "none"]:
            raise ConfigError("ClickHouse compression must be one of: lz4, zstd, none")

@dataclass
class PostgreSQLConfig(StorageConfig):
    """PostgreSQL 存儲配置類"""
    # 連接配置
    host: str = field(default="localhost")
    port: int = field(default=5432)
    username: str = field(default="postgres")
    password: str = field(default="")
    database: str = field(default="postgres")
    ssl_mode: str = field(default="prefer")
    
    # 連接池配置
    pool_size: int = field(default=10)
    pool_recycle: int = field(default=3600)
    pool_timeout: int = field(default=30)
    
    # 表配置
    table_name: str = field(default="data")
    id_field: str = field(default="id")
    data_field: str = field(default="data")
    created_at_field: str = field(default="created_at")
    updated_at_field: str = field(default="updated_at")
    
    # 模式配置
    schema: str = field(default="public")
    
    # 索引配置
    index_fields: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """初始化後驗證"""
        self.validate_postgresql_config()
    
    def validate_postgresql_config(self):
        """驗證 PostgreSQL 配置"""
        if not self.host:
            raise ConfigError("PostgreSQL host cannot be empty")
        
        if not isinstance(self.port, int) or self.port <= 0:
            raise ConfigError("PostgreSQL port must be a positive integer")
        
        if not self.database:
            raise ConfigError("PostgreSQL database cannot be empty")
        
        if not isinstance(self.pool_size, int) or self.pool_size <= 0:
            raise ConfigError("PostgreSQL pool size must be a positive integer")
        
        if not isinstance(self.pool_recycle, int) or self.pool_recycle <= 0:
            raise ConfigError("PostgreSQL pool recycle must be a positive integer")
        
        if not isinstance(self.pool_timeout, int) or self.pool_timeout <= 0:
            raise ConfigError("PostgreSQL pool timeout must be a positive integer")
        
        if not self.table_name:
            raise ConfigError("PostgreSQL table name cannot be empty")
        
        if not self.schema:
            raise ConfigError("PostgreSQL schema cannot be empty")
        
        if self.ssl_mode not in ["disable", "allow", "prefer", "require", "verify-ca", "verify-full"]:
            raise ConfigError("PostgreSQL ssl_mode must be one of: disable, allow, prefer, require, verify-ca, verify-full")

@dataclass
class KafkaConfig(StorageConfig):
    """Kafka 存儲配置類"""
    # 連接配置
    bootstrap_servers: List[str] = field(default_factory=lambda: ["localhost:9092"])
    client_id: str = field(default="persistence_client")
    group_id: str = field(default="persistence_group")
    
    # 認證配置
    security_protocol: str = field(default="PLAINTEXT")
    sasl_mechanism: Optional[str] = field(default=None)
    sasl_plain_username: Optional[str] = field(default=None)
    sasl_plain_password: Optional[str] = field(default=None)
    ssl_cafile: Optional[str] = field(default=None)
    ssl_certfile: Optional[str] = field(default=None)
    ssl_keyfile: Optional[str] = field(default=None)
    
    # 主題配置
    topic_name: str = field(default="data")
    partition_count: int = field(default=1)
    replication_factor: int = field(default=1)
    
    # 生產者配置
    acks: str = field(default="all")
    retries: int = field(default=3)
    batch_size: int = field(default=16384)
    linger_ms: int = field(default=5)
    compression_type: str = field(default="gzip")
    
    # 消費者配置
    auto_offset_reset: str = field(default="earliest")
    enable_auto_commit: bool = field(default=True)
    auto_commit_interval_ms: int = field(default=5000)
    max_poll_records: int = field(default=500)
    
    # 序列化配置
    key_serializer: str = field(default="json")
    value_serializer: str = field(default="json")
    
    def __post_init__(self):
        """初始化後驗證"""
        self.validate_kafka_config()
    
    def validate_kafka_config(self):
        """驗證 Kafka 配置"""
        if not self.bootstrap_servers:
            raise ConfigError("Kafka bootstrap_servers cannot be empty")
        
        if not self.client_id:
            raise ConfigError("Kafka client_id cannot be empty")
        
        if not self.group_id:
            raise ConfigError("Kafka group_id cannot be empty")
        
        if not self.topic_name:
            raise ConfigError("Kafka topic_name cannot be empty")
        
        if not isinstance(self.partition_count, int) or self.partition_count <= 0:
            raise ConfigError("Kafka partition_count must be a positive integer")
        
        if not isinstance(self.replication_factor, int) or self.replication_factor <= 0:
            raise ConfigError("Kafka replication_factor must be a positive integer")
        
        if self.acks not in ["0", "1", "all"]:
            raise ConfigError("Kafka acks must be one of: 0, 1, all")
        
        if not isinstance(self.retries, int) or self.retries < 0:
            raise ConfigError("Kafka retries must be a non-negative integer")
        
        if not isinstance(self.batch_size, int) or self.batch_size <= 0:
            raise ConfigError("Kafka batch_size must be a positive integer")
        
        if not isinstance(self.linger_ms, int) or self.linger_ms < 0:
            raise ConfigError("Kafka linger_ms must be a non-negative integer")
        
        if self.compression_type not in ["none", "gzip", "snappy", "lz4", "zstd"]:
            raise ConfigError("Kafka compression_type must be one of: none, gzip, snappy, lz4, zstd")
        
        if self.auto_offset_reset not in ["earliest", "latest", "none"]:
            raise ConfigError("Kafka auto_offset_reset must be one of: earliest, latest, none")
        
        if not isinstance(self.auto_commit_interval_ms, int) or self.auto_commit_interval_ms <= 0:
            raise ConfigError("Kafka auto_commit_interval_ms must be a positive integer")
        
        if not isinstance(self.max_poll_records, int) or self.max_poll_records <= 0:
            raise ConfigError("Kafka max_poll_records must be a positive integer")

@dataclass
class RabbitMQConfig(StorageConfig):
    """RabbitMQ 存儲配置類"""
    
    # 連接配置
    host: str = field(default="localhost")
    port: int = field(default=5672)
    username: str = field(default="guest")
    password: str = field(default="guest")
    virtual_host: str = field(default="/")
    
    # SSL 配置
    ssl_enabled: bool = field(default=False)
    ssl_ca_certs: Optional[str] = field(default=None)
    ssl_certfile: Optional[str] = field(default=None)
    ssl_keyfile: Optional[str] = field(default=None)
    ssl_cert_reqs: str = field(default="CERT_REQUIRED")
    
    # 連接池配置
    connection_attempts: int = field(default=3)
    retry_delay: int = field(default=5)
    socket_timeout: int = field(default=30)
    heartbeat: int = field(default=60)
    
    # 交換機配置
    exchange_name: str = field(default="data")
    exchange_type: str = field(default="direct")
    exchange_durable: bool = field(default=True)
    exchange_auto_delete: bool = field(default=False)
    exchange_internal: bool = field(default=False)
    
    # 隊列配置
    queue_name: str = field(default="data")
    queue_durable: bool = field(default=True)
    queue_exclusive: bool = field(default=False)
    queue_auto_delete: bool = field(default=False)
    queue_max_length: int = field(default=0)  # 0 表示無限制
    queue_overflow: str = field(default="reject-publish")  # reject-publish, reject-latest
    
    # 路由配置
    routing_key: str = field(default="data")
    
    # 消息配置
    message_ttl: int = field(default=0)  # 0 表示永不過期
    message_persistent: bool = field(default=True)
    message_priority: int = field(default=0)
    
    def __post_init__(self):
        """初始化後驗證"""
        self.validate_rabbitmq_config()
    
    def validate_rabbitmq_config(self):
        """驗證 RabbitMQ 配置"""
        if not self.host:
            raise ConfigError("RabbitMQ host cannot be empty")
        
        if not isinstance(self.port, int) or self.port <= 0:
            raise ConfigError("RabbitMQ port must be a positive integer")
        
        if not self.exchange_name:
            raise ConfigError("RabbitMQ exchange_name cannot be empty")
        
        if self.exchange_type not in ["direct", "fanout", "topic", "headers"]:
            raise ConfigError("RabbitMQ exchange_type must be one of: direct, fanout, topic, headers")
        
        if not self.queue_name:
            raise ConfigError("RabbitMQ queue_name cannot be empty")
        
        if not isinstance(self.connection_attempts, int) or self.connection_attempts <= 0:
            raise ConfigError("RabbitMQ connection_attempts must be a positive integer")
        
        if not isinstance(self.retry_delay, int) or self.retry_delay <= 0:
            raise ConfigError("RabbitMQ retry_delay must be a positive integer")
        
        if not isinstance(self.socket_timeout, int) or self.socket_timeout <= 0:
            raise ConfigError("RabbitMQ socket_timeout must be a positive integer")
        
        if not isinstance(self.heartbeat, int) or self.heartbeat <= 0:
            raise ConfigError("RabbitMQ heartbeat must be a positive integer")
        
        if not isinstance(self.message_ttl, int) or self.message_ttl < 0:
            raise ConfigError("RabbitMQ message_ttl must be a non-negative integer")
        
        if self.queue_overflow not in ["reject-publish", "reject-latest"]:
            raise ConfigError("RabbitMQ queue_overflow must be one of: reject-publish, reject-latest")
        
        if self.ssl_enabled:
            if not self.ssl_ca_certs:
                raise ConfigError("SSL CA certificates are required when SSL is enabled")
            if not self.ssl_certfile:
                raise ConfigError("SSL certificate file is required when SSL is enabled")
            if not self.ssl_keyfile:
                raise ConfigError("SSL key file is required when SSL is enabled")
            if self.ssl_cert_reqs not in ["CERT_NONE", "CERT_OPTIONAL", "CERT_REQUIRED"]:
                raise ConfigError("SSL cert_reqs must be one of: CERT_NONE, CERT_OPTIONAL, CERT_REQUIRED")

@dataclass
class NotionConfig(StorageConfig):
    """Notion 配置類"""
    
    # Notion API 配置
    api_key: str = ''  # Notion API Key
    version: str = '2022-06-28'  # API 版本
    
    # 數據庫配置
    database_id: str = ''  # 數據庫 ID
    page_id: str = ''  # 頁面 ID
    
    # 緩存配置
    cache_enabled: bool = True  # 是否啟用緩存
    cache_ttl: int = 3600  # 緩存過期時間（秒）
    cache_max_size: int = 1000  # 最大緩存條數
    
    # 重試配置
    max_retries: int = 3  # 最大重試次數
    retry_delay: int = 1  # 重試延遲（秒）
    
    def __post_init__(self):
        """初始化後的驗證"""
        super().__post_init__()
        self.validate_notion_config()
    
    def validate_notion_config(self) -> None:
        """
        驗證 Notion 特定配置
        
        Raises:
            ConfigError: 配置參數無效
        """
        if not self.api_key:
            raise ConfigError("Notion API Key 不能為空")
        if not self.version:
            raise ConfigError("API 版本不能為空")
        if not self.database_id:
            raise ConfigError("數據庫 ID 不能為空")
        if self.cache_ttl < 0:
            raise ConfigError("緩存過期時間不能為負數")
        if self.cache_max_size < 0:
            raise ConfigError("最大緩存條數不能為負數")
        if self.max_retries < 0:
            raise ConfigError("最大重試次數不能為負數")
        if self.retry_delay < 0:
            raise ConfigError("重試延遲不能為負數") 