#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
API 存儲處理模組

此模組提供 API 相關數據的存儲功能，包括：
1. API 調用記錄存儲
2. API 響應緩存
3. API 配置管理
4. API 元數據處理
"""

import json
import logging
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from enum import Enum

class APIRecordType(Enum):
    """API 記錄類型"""
    REQUEST = "request"
    RESPONSE = "response"
    ERROR = "error"
    CACHE = "cache"
    CONFIG = "config"
    METADATA = "metadata"

@dataclass
class APIRecord:
    """API 記錄"""
    type: APIRecordType
    api_name: str
    timestamp: datetime
    data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class APIStorageConfig:
    """API 存儲配置"""
    storage_dir: str = "api_data"
    cache_dir: str = "api_cache"
    record_dir: str = "api_records"
    config_dir: str = "api_configs"
    metadata_dir: str = "api_metadata"
    cache_ttl: int = 3600  # 緩存過期時間（秒）
    max_cache_size: int = 1000  # 最大緩存條數
    record_format: str = "json"  # 記錄格式（json/csv）
    compression: bool = False  # 是否壓縮
    encoding: str = "utf-8"  # 文件編碼

class APIStorageHandler:
    """API 存儲處理器"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化 API 存儲處理器
        
        Args:
            config: 配置字典
        """
        self.logger = logging.getLogger(__name__)
        
        # 加載配置
        self.config = APIStorageConfig(**(config or {}))
        
        # 初始化目錄
        self._init_directories()
        
        self.logger.info("API 存儲處理器初始化完成")
    
    def _init_directories(self) -> None:
        """初始化存儲目錄"""
        try:
            # 創建主目錄
            base_dir = Path(self.config.storage_dir)
            base_dir.mkdir(parents=True, exist_ok=True)
            
            # 創建子目錄
            (base_dir / self.config.cache_dir).mkdir(exist_ok=True)
            (base_dir / self.config.record_dir).mkdir(exist_ok=True)
            (base_dir / self.config.config_dir).mkdir(exist_ok=True)
            (base_dir / self.config.metadata_dir).mkdir(exist_ok=True)
            
            self.logger.debug("已初始化存儲目錄")
        
        except Exception as e:
            self.logger.error(f"初始化存儲目錄失敗: {str(e)}")
            raise
    
    def save_record(self, record: APIRecord) -> bool:
        """
        保存 API 記錄
        
        Args:
            record: API 記錄
            
        Returns:
            是否成功保存
        """
        try:
            # 構建文件路徑
            record_dir = Path(self.config.storage_dir) / self.config.record_dir
            file_path = record_dir / f"{record.api_name}_{record.type.value}_{record.timestamp.strftime('%Y%m%d_%H%M%S')}.{self.config.record_format}"
            
            # 準備數據
            data = {
                "type": record.type.value,
                "api_name": record.api_name,
                "timestamp": record.timestamp.isoformat(),
                "data": record.data,
                "metadata": record.metadata
            }
            
            # 保存文件
            with open(file_path, 'w', encoding=self.config.encoding) as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.logger.debug(f"已保存 API 記錄: {file_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"保存 API 記錄失敗: {str(e)}")
            return False
    
    def get_records(
        self,
        api_name: Optional[str] = None,
        record_type: Optional[APIRecordType] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[APIRecord]:
        """
        獲取 API 記錄
        
        Args:
            api_name: API 名稱
            record_type: 記錄類型
            start_time: 開始時間
            end_time: 結束時間
            
        Returns:
            API 記錄列表
        """
        try:
            records = []
            record_dir = Path(self.config.storage_dir) / self.config.record_dir
            
            # 遍歷記錄文件
            for file_path in record_dir.glob(f"*.{self.config.record_format}"):
                try:
                    with open(file_path, 'r', encoding=self.config.encoding) as f:
                        data = json.load(f)
                    
                    # 解析記錄
                    record = APIRecord(
                        type=APIRecordType(data["type"]),
                        api_name=data["api_name"],
                        timestamp=datetime.fromisoformat(data["timestamp"]),
                        data=data["data"],
                        metadata=data["metadata"]
                    )
                    
                    # 過濾記錄
                    if api_name and record.api_name != api_name:
                        continue
                    if record_type and record.type != record_type:
                        continue
                    if start_time and record.timestamp < start_time:
                        continue
                    if end_time and record.timestamp > end_time:
                        continue
                    
                    records.append(record)
                
                except Exception as e:
                    self.logger.warning(f"解析記錄文件失敗: {file_path}, {str(e)}")
                    continue
            
            self.logger.debug(f"已獲取 {len(records)} 條 API 記錄")
            return records
        
        except Exception as e:
            self.logger.error(f"獲取 API 記錄失敗: {str(e)}")
            return []
    
    def save_cache(self, api_name: str, key: str, data: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """
        保存 API 緩存
        
        Args:
            api_name: API 名稱
            key: 緩存鍵
            data: 緩存數據
            ttl: 過期時間（秒）
            
        Returns:
            是否成功保存
        """
        try:
            # 構建文件路徑
            cache_dir = Path(self.config.storage_dir) / self.config.cache_dir
            file_path = cache_dir / f"{api_name}_{key}.json"
            
            # 準備數據
            cache_data = {
                "data": data,
                "timestamp": datetime.now().isoformat(),
                "ttl": ttl or self.config.cache_ttl
            }
            
            # 保存文件
            with open(file_path, 'w', encoding=self.config.encoding) as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
            self.logger.debug(f"已保存 API 緩存: {file_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"保存 API 緩存失敗: {str(e)}")
            return False
    
    def get_cache(self, api_name: str, key: str) -> Optional[Dict[str, Any]]:
        """
        獲取 API 緩存
        
        Args:
            api_name: API 名稱
            key: 緩存鍵
            
        Returns:
            緩存數據，不存在或已過期時返回 None
        """
        try:
            # 構建文件路徑
            cache_dir = Path(self.config.storage_dir) / self.config.cache_dir
            file_path = cache_dir / f"{api_name}_{key}.json"
            
            # 檢查文件是否存在
            if not file_path.exists():
                return None
            
            # 讀取文件
            with open(file_path, 'r', encoding=self.config.encoding) as f:
                cache_data = json.load(f)
            
            # 檢查是否過期
            timestamp = datetime.fromisoformat(cache_data["timestamp"])
            ttl = cache_data["ttl"]
            if (datetime.now() - timestamp).total_seconds() > ttl:
                self.logger.debug(f"API 緩存已過期: {file_path}")
                return None
            
            self.logger.debug(f"已獲取 API 緩存: {file_path}")
            return cache_data["data"]
        
        except Exception as e:
            self.logger.error(f"獲取 API 緩存失敗: {str(e)}")
            return None
    
    def clear_cache(self, api_name: Optional[str] = None) -> bool:
        """
        清除 API 緩存
        
        Args:
            api_name: API 名稱，為 None 時清除所有緩存
            
        Returns:
            是否成功清除
        """
        try:
            cache_dir = Path(self.config.storage_dir) / self.config.cache_dir
            
            if api_name:
                # 清除指定 API 的緩存
                pattern = f"{api_name}_*.json"
                for file_path in cache_dir.glob(pattern):
                    file_path.unlink()
            else:
                # 清除所有緩存
                for file_path in cache_dir.glob("*.json"):
                    file_path.unlink()
            
            self.logger.debug("已清除 API 緩存")
            return True
        
        except Exception as e:
            self.logger.error(f"清除 API 緩存失敗: {str(e)}")
            return False
    
    def save_config(self, api_name: str, config: Dict[str, Any]) -> bool:
        """
        保存 API 配置
        
        Args:
            api_name: API 名稱
            config: API 配置
            
        Returns:
            是否成功保存
        """
        try:
            # 構建文件路徑
            config_dir = Path(self.config.storage_dir) / self.config.config_dir
            file_path = config_dir / f"{api_name}.json"
            
            # 保存文件
            with open(file_path, 'w', encoding=self.config.encoding) as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            self.logger.debug(f"已保存 API 配置: {file_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"保存 API 配置失敗: {str(e)}")
            return False
    
    def get_config(self, api_name: str) -> Optional[Dict[str, Any]]:
        """
        獲取 API 配置
        
        Args:
            api_name: API 名稱
            
        Returns:
            API 配置，不存在時返回 None
        """
        try:
            # 構建文件路徑
            config_dir = Path(self.config.storage_dir) / self.config.config_dir
            file_path = config_dir / f"{api_name}.json"
            
            # 檢查文件是否存在
            if not file_path.exists():
                return None
            
            # 讀取文件
            with open(file_path, 'r', encoding=self.config.encoding) as f:
                config = json.load(f)
            
            self.logger.debug(f"已獲取 API 配置: {file_path}")
            return config
        
        except Exception as e:
            self.logger.error(f"獲取 API 配置失敗: {str(e)}")
            return None
    
    def save_metadata(self, api_name: str, metadata: Dict[str, Any]) -> bool:
        """
        保存 API 元數據
        
        Args:
            api_name: API 名稱
            metadata: API 元數據
            
        Returns:
            是否成功保存
        """
        try:
            # 構建文件路徑
            metadata_dir = Path(self.config.storage_dir) / self.config.metadata_dir
            file_path = metadata_dir / f"{api_name}.json"
            
            # 保存文件
            with open(file_path, 'w', encoding=self.config.encoding) as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            self.logger.debug(f"已保存 API 元數據: {file_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"保存 API 元數據失敗: {str(e)}")
            return False
    
    def get_metadata(self, api_name: str) -> Optional[Dict[str, Any]]:
        """
        獲取 API 元數據
        
        Args:
            api_name: API 名稱
            
        Returns:
            API 元數據，不存在時返回 None
        """
        try:
            # 構建文件路徑
            metadata_dir = Path(self.config.storage_dir) / self.config.metadata_dir
            file_path = metadata_dir / f"{api_name}.json"
            
            # 檢查文件是否存在
            if not file_path.exists():
                return None
            
            # 讀取文件
            with open(file_path, 'r', encoding=self.config.encoding) as f:
                metadata = json.load(f)
            
            self.logger.debug(f"已獲取 API 元數據: {file_path}")
            return metadata
        
        except Exception as e:
            self.logger.error(f"獲取 API 元數據失敗: {str(e)}")
            return None
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        pass 