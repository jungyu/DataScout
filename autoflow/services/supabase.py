#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Supabase 服務

此模組提供了與 Supabase 數據庫交互的功能。
"""

import os
import logging
from typing import Dict, Any, Optional
from supabase import create_client, Client

class SupabaseService:
    """Supabase 服務類"""
    
    def __init__(self):
        """初始化 Supabase 服務"""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.url = os.getenv('SUPABASE_URL')
        self.key = os.getenv('SUPABASE_KEY')
        if not self.url or not self.key:
            raise ValueError("未設置 SUPABASE_URL 或 SUPABASE_KEY 環境變數")
        self.client: Client = create_client(self.url, self.key)
    
    async def get_user(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """獲取用戶信息
        
        Args:
            telegram_id: Telegram 用戶 ID
            
        Returns:
            用戶信息字典，如果不存在則返回 None
        """
        try:
            response = self.client.table('users').select('*').eq('telegram_id', telegram_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            self.logger.error(f"獲取用戶信息時發生錯誤：{str(e)}")
            return None
    
    async def create_user(self, telegram_id: int, username: Optional[str] = None,
                         first_name: Optional[str] = None, last_name: Optional[str] = None) -> Dict[str, Any]:
        """創建新用戶
        
        Args:
            telegram_id: Telegram 用戶 ID
            username: 用戶名
            first_name: 名字
            last_name: 姓氏
            
        Returns:
            創建的用戶信息
        """
        try:
            data = {
                'telegram_id': telegram_id,
                'username': username,
                'first_name': first_name,
                'last_name': last_name
            }
            response = self.client.table('users').insert(data).execute()
            return response.data[0]
        except Exception as e:
            self.logger.error(f"創建用戶時發生錯誤：{str(e)}")
            raise
    
    async def create_conversation(self, user_id: str, message: str, response: str) -> None:
        """記錄對話
        
        Args:
            user_id: 用戶 ID
            message: 用戶消息
            response: 機器人回應
        """
        try:
            data = {
                'user_id': user_id,
                'message': message,
                'response': response
            }
            self.client.table('conversations').insert(data).execute()
        except Exception as e:
            self.logger.error(f"記錄對話時發生錯誤：{str(e)}")
            raise
    
    async def create(self, table: str, data: Dict[str, Any]) -> None:
        """創建記錄
        
        Args:
            table: 表名
            data: 數據
        """
        try:
            self.client.table(table).insert(data).execute()
        except Exception as e:
            self.logger.error(f"創建記錄時發生錯誤：{str(e)}")
            raise 