#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Supabase 配置模組

此模組提供 Supabase 資料庫的配置和連線設置。
"""

from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

class SupabaseConfig:
    """Supabase 配置類"""
    
    def __init__(self, url: Optional[str] = None, key: Optional[str] = None):
        """初始化 Supabase 配置
        
        Args:
            url: Supabase URL，如果為 None 則從環境變數讀取
            key: Supabase API Key，如果為 None 則從環境變數讀取
        """
        self.url = url or os.getenv('SUPABASE_URL')
        self.key = key or os.getenv('SUPABASE_KEY')
        
        if not self.url or not self.key:
            raise ValueError("Supabase URL 和 API Key 必須提供")
    
    # 資料表結構定義
    TABLES = {
        'users': {
            'name': 'users',
            'columns': {
                'id': 'uuid PRIMARY KEY DEFAULT uuid_generate_v4()',
                'telegram_id': 'BIGINT UNIQUE NOT NULL',
                'username': 'VARCHAR(255)',
                'first_name': 'VARCHAR(255)',
                'last_name': 'VARCHAR(255)',
                'created_at': 'TIMESTAMP WITH TIME ZONE DEFAULT NOW()',
                'updated_at': 'TIMESTAMP WITH TIME ZONE DEFAULT NOW()'
            }
        },
        'conversations': {
            'name': 'conversations',
            'columns': {
                'id': 'uuid PRIMARY KEY DEFAULT uuid_generate_v4()',
                'user_id': 'uuid REFERENCES users(id)',
                'message': 'text',
                'response': 'text',
                'intend': 'VARCHAR(100)',
                'command': 'VARCHAR(100)',
                'created_at': 'TIMESTAMP WITH TIME ZONE DEFAULT NOW()'
            }
        },
        'images': {
            'name': 'images',
            'columns': {
                'id': 'uuid PRIMARY KEY DEFAULT uuid_generate_v4()',
                'conversation_id': 'uuid REFERENCES conversations(id)',
                'title': 'VARCHAR(255)',
                'tags': 'TEXT[]',
                'image_data': 'BYTEA',
                'image_type': 'VARCHAR(50)',
                'created_at': 'TIMESTAMP WITH TIME ZONE DEFAULT NOW()'
            }
        }
    }
    
    def get_connection_config(self) -> Dict[str, Any]:
        """獲取資料庫連線配置"""
        return {
            'url': self.url,
            'key': self.key,
            'options': {
                'schema': 'public',
                'headers': {
                    'apikey': self.key,
                    'Authorization': f"Bearer {self.key}"
                }
            }
        }
    
    @classmethod
    def get_table_definition(cls, table_name: str) -> Dict[str, str]:
        """獲取資料表結構定義"""
        return cls.TABLES.get(table_name, {}) 