#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
錯誤處理系統
提供更詳細的錯誤類型和錯誤信息
"""

from typing import Any, Dict, Optional
from datetime import datetime

class DataScoutError(Exception):
    """基礎錯誤類別"""
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        code: Optional[str] = None,
        timestamp: Optional[datetime] = None
    ):
        """
        初始化錯誤
        
        Args:
            message: 錯誤訊息
            details: 錯誤詳情
            code: 錯誤代碼
            timestamp: 錯誤時間
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.code = code
        self.timestamp = timestamp or datetime.now()
        
    def to_dict(self) -> Dict[str, Any]:
        """
        轉換為字典
        
        Returns:
            Dict[str, Any]: 錯誤信息字典
        """
        return {
            "message": self.message,
            "details": self.details,
            "code": self.code,
            "timestamp": self.timestamp.isoformat()
        }
        
class ValidationError(DataScoutError):
    """驗證錯誤"""
    pass
    
class ConnectionError(DataScoutError):
    """連接錯誤"""
    pass
    
class AuthenticationError(DataScoutError):
    """認證錯誤"""
    pass
    
class DatabaseError(DataScoutError):
    """資料庫錯誤"""
    pass
    
class QueryError(DatabaseError):
    """查詢錯誤"""
    pass
    
class InsertError(DatabaseError):
    """插入錯誤"""
    pass
    
class UpdateError(DatabaseError):
    """更新錯誤"""
    pass
    
class DeleteError(DatabaseError):
    """刪除錯誤"""
    pass
    
class TransactionError(DatabaseError):
    """事務錯誤"""
    pass
    
class IndexError(DatabaseError):
    """索引錯誤"""
    pass
    
class AggregationError(DatabaseError):
    """聚合錯誤"""
    pass
    
class BulkWriteError(DatabaseError):
    """批量寫入錯誤"""
    pass
    
class CacheError(DataScoutError):
    """快取錯誤"""
    pass
    
class CacheKeyError(CacheError):
    """快取鍵錯誤"""
    pass
    
class CacheValueError(CacheError):
    """快取值錯誤"""
    pass
    
class CacheTimeoutError(CacheError):
    """快取超時錯誤"""
    pass
    
class CacheFullError(CacheError):
    """快取已滿錯誤"""
    pass
    
class EncryptionError(DataScoutError):
    """加密錯誤"""
    pass
    
class DecryptionError(EncryptionError):
    """解密錯誤"""
    pass
    
class KeyError(EncryptionError):
    """密鑰錯誤"""
    pass
    
class CompressionError(DataScoutError):
    """壓縮錯誤"""
    pass
    
class DecompressionError(CompressionError):
    """解壓縮錯誤"""
    pass
    
class FormatError(DataScoutError):
    """格式錯誤"""
    pass
    
class ConversionError(FormatError):
    """轉換錯誤"""
    pass
    
class SerializationError(FormatError):
    """序列化錯誤"""
    pass
    
class DeserializationError(FormatError):
    """反序列化錯誤"""
    pass
    
class NetworkError(DataScoutError):
    """網路錯誤"""
    pass
    
class TimeoutError(NetworkError):
    """超時錯誤"""
    pass
    
class ConnectionTimeoutError(TimeoutError):
    """連接超時錯誤"""
    pass
    
class ReadTimeoutError(TimeoutError):
    """讀取超時錯誤"""
    pass
    
class WriteTimeoutError(TimeoutError):
    """寫入超時錯誤"""
    pass
    
class ResourceError(DataScoutError):
    """資源錯誤"""
    pass
    
class MemoryError(ResourceError):
    """記憶體錯誤"""
    pass
    
class DiskError(ResourceError):
    """磁碟錯誤"""
    pass
    
class CPUError(ResourceError):
    """CPU 錯誤"""
    pass
    
class PermissionError(DataScoutError):
    """權限錯誤"""
    pass
    
class AccessDeniedError(PermissionError):
    """訪問拒絕錯誤"""
    pass
    
class AuthenticationRequiredError(PermissionError):
    """需要認證錯誤"""
    pass
    
class AuthorizationError(PermissionError):
    """授權錯誤"""
    pass
    
class RateLimitError(DataScoutError):
    """速率限制錯誤"""
    pass
    
class QuotaExceededError(RateLimitError):
    """配額超限錯誤"""
    pass
    
class ThrottlingError(RateLimitError):
    """節流錯誤"""
    pass
    
class StateError(DataScoutError):
    """狀態錯誤"""
    pass
    
class InvalidStateError(StateError):
    """無效狀態錯誤"""
    pass
    
class StateTransitionError(StateError):
    """狀態轉換錯誤"""
    pass
    
class InitializationError(DataScoutError):
    """初始化錯誤"""
    pass
    
class ConfigurationError(InitializationError):
    """配置錯誤"""
    pass
    
class DependencyError(InitializationError):
    """依賴錯誤"""
    pass
    
class EnvironmentError(InitializationError):
    """環境錯誤"""
    pass
    
class CleanupError(DataScoutError):
    """清理錯誤"""
    pass
    
class ResourceCleanupError(CleanupError):
    """資源清理錯誤"""
    pass
    
class ConnectionCleanupError(CleanupError):
    """連接清理錯誤"""
    pass
    
class CacheCleanupError(CleanupError):
    """快取清理錯誤"""
    pass

class AdapterError(Exception):
    """適配器基礎異常類"""
    def __init__(self, message: str, code: int = None, details: dict = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)

class ConfigError(AdapterError):
    """配置錯誤"""
    pass

class ResourceNotFoundError(AdapterError):
    """資源未找到錯誤"""
    pass

class ResourceConflictError(AdapterError):
    """資源衝突錯誤"""
    pass

class InvalidRequestError(AdapterError):
    """無效請求錯誤"""
    pass

class InvalidResponseError(AdapterError):
    """無效響應錯誤"""
    pass

class DataProcessingError(AdapterError):
    """數據處理錯誤"""
    pass

class StorageError(AdapterError):
    """存儲錯誤"""
    pass

class ServiceUnavailableError(AdapterError):
    """服務不可用錯誤"""
    pass

class InternalServerError(AdapterError):
    """內部服務器錯誤"""
    pass

class ExternalServiceError(AdapterError):
    """外部服務錯誤"""
    pass

class TransformationError(AdapterError):
    """轉換錯誤"""
    pass

class SchemaError(AdapterError):
    """結構錯誤"""
    pass

class MappingError(AdapterError):
    """映射錯誤"""
    pass

class BatchError(AdapterError):
    """批量處理錯誤"""
    pass

class IncrementalError(AdapterError):
    """增量同步錯誤"""
    pass

class RollbackError(AdapterError):
    """回滾錯誤"""
    pass

class PluginError(AdapterError):
    """插件錯誤"""
    pass

class FileError(AdapterError):
    """檔案錯誤"""
    pass

class FieldMappingError(TransformationError):
    """欄位映射異常"""
    pass

class TypeConversionError(TransformationError):
    """類型轉換異常"""
    pass

class ValueFormatError(TransformationError):
    """值格式化異常"""
    pass

class DataCleaningError(TransformationError):
    """資料清洗異常"""
    pass

class RuleExecutionError(TransformationError):
    """規則執行異常"""
    pass

class BatchProcessingError(TransformationError):
    """批量處理異常"""
    pass

class SchemaValidationError(ValidationError):
    """結構驗證異常"""
    pass

class ConstraintValidationError(ValidationError):
    """約束驗證異常"""
    pass

class DataIntegrityError(ValidationError):
    """資料完整性異常"""
    pass

class InvalidConfigurationError(ConfigError):
    """無效配置異常"""
    pass

class MissingConfigurationError(ConfigError):
    """缺失配置異常"""
    pass

class InvalidTransformerError(ConfigError):
    """無效轉換器異常"""
    pass

class InvalidRuleError(ConfigError):
    """無效規則異常"""
    pass 