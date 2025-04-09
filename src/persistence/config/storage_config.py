#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
存儲配置管理模組
提供統一的存儲配置管理功能
"""

import json
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from pathlib import Path


@dataclass
class StorageConfig:
    """存儲配置類"""
    storage_mode: str = "local"  # local, mongodb, notion
    data_dir: str = "data"
    default_collection: str = "crawl_data"
    field_mappings: Dict[str, str] = field(default_factory=dict)
    timestamp_field: str = "timestamp"
    id_field: str = "id"
    batch_size: int = 100
    retry_count: int = 3
    retry_delay: int = 1
    backup_enabled: bool = True
    auto_save: bool = True
    auto_save_interval: int = 300
    max_backups: int = 5
    encoding: str = "utf-8"
    indent: int = 2
    
    # 本地存儲配置
    local_formats: List[str] = field(default_factory=lambda: ["json", "pickle", "csv"])
    local_indent: int = 2
    local_csv_headers: List[str] = field(default_factory=list)
    
    # MongoDB 配置
    mongodb_host: str = "localhost"
    mongodb_port: int = 27017
    mongodb_username: Optional[str] = None
    mongodb_password: Optional[str] = None
    mongodb_database: str = "crawler_db"
    mongodb_collection: str = "crawled_data"
    mongodb_auth_source: str = "admin"
    mongodb_timeout: int = 5000
    mongodb_max_pool_size: int = 100
    
    # Notion 配置
    notion_token: str = ""
    notion_database_id: str = ""
    notion_page_size: int = 100
    
    @classmethod
    def from_credentials(cls, credentials_path: str = "config/credentials.json") -> "StorageConfig":
        """從 credentials.json 創建配置"""
        try:
            # 讀取 credentials.json
            cred_path = Path(credentials_path)
            if not cred_path.exists():
                return cls()
            
            with open(cred_path, "r", encoding="utf-8") as f:
                creds = json.load(f)
            
            # 創建配置實例
            config = cls()
            
            # 更新 MongoDB 配置
            if "mongodb" in creds:
                mongo = creds["mongodb"]
                config.mongodb_host = mongo.get("host", config.mongodb_host)
                config.mongodb_port = mongo.get("port", config.mongodb_port)
                config.mongodb_username = mongo.get("username", config.mongodb_username)
                config.mongodb_password = mongo.get("password", config.mongodb_password)
                config.mongodb_database = mongo.get("database", config.mongodb_database)
                config.mongodb_collection = mongo.get("collection", config.mongodb_collection)
                
                if "options" in mongo:
                    opts = mongo["options"]
                    config.mongodb_auth_source = opts.get("auth_source", config.mongodb_auth_source)
                    config.mongodb_timeout = opts.get("connect_timeout_ms", config.mongodb_timeout)
            
            # 更新 Notion 配置
            if "notion" in creds:
                notion = creds["notion"]
                config.notion_token = notion.get("api_key", config.notion_token)
                if "oauth_token" in notion:
                    config.notion_token = notion["oauth_token"]
            
            return config
            
        except Exception as e:
            print(f"從 credentials.json 讀取配置失敗: {str(e)}")
            return cls()
    
    def validate(self) -> bool:
        """驗證配置是否有效"""
        try:
            # 驗證存儲模式
            if self.storage_mode not in ["local", "mongodb", "notion"]:
                print(f"不支持的存儲模式: {self.storage_mode}")
                return False
            
            # 驗證數據目錄
            data_path = Path(self.data_dir)
            if not data_path.exists():
                data_path.mkdir(parents=True, exist_ok=True)
            
            # 驗證 MongoDB 配置
            if self.storage_mode == "mongodb":
                if not self.mongodb_host or not self.mongodb_port:
                    print("MongoDB 配置不完整")
                    return False
            
            # 驗證 Notion 配置
            if self.storage_mode == "notion":
                if not self.notion_token or not self.notion_database_id:
                    print("Notion 配置不完整")
                    return False
            
            return True
            
        except Exception as e:
            print(f"配置驗證失敗: {str(e)}")
            return False
    
    def get_mongodb_uri(self) -> str:
        """獲取 MongoDB 連接 URI"""
        if self.mongodb_username and self.mongodb_password:
            return f"mongodb://{self.mongodb_username}:{self.mongodb_password}@{self.mongodb_host}:{self.mongodb_port}"
        return f"mongodb://{self.mongodb_host}:{self.mongodb_port}"
    
    def get_storage_path(self) -> Path:
        """獲取存儲路徑"""
        return Path(self.data_dir) 