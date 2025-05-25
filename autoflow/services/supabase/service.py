#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Supabase 服務模組

此模組提供與 Supabase 資料庫的交互功能。
"""

from typing import Dict, Any, List, Optional
import os
from .handler import SupabaseHandler
from .config import SupabaseConfig

class SupabaseService:
    """Supabase 服務類"""
    
    def __init__(self):
        """初始化 Supabase 客戶端"""
        config = SupabaseConfig(
            url=os.getenv('SUPABASE_URL'),
            key=os.getenv('SUPABASE_KEY')
        )
        self.handler = SupabaseHandler(config)
    
    async def create_user(self, telegram_id: int, username: str = None,
                         first_name: str = None, last_name: str = None) -> Dict[str, Any]:
        """創建用戶"""
        data = {
            'telegram_id': telegram_id,
            'username': username,
            'first_name': first_name,
            'last_name': last_name
        }
        return await self.handler.create('users', data)
    
    async def get_user(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """獲取用戶信息"""
        users = await self.handler.read('users', {'telegram_id': telegram_id})
        return users[0] if users else None
    
    async def create_conversation(
        self,
        user_id: str,
        message: str,
        response: str,
        intend: str = None,
        command: str = None
    ) -> Dict[str, Any]:
        """創建對話記錄"""
        data = {
            'user_id': user_id,
            'message': message,
            'response': response,
            'intend': intend,
            'command': command
        }
        return await self.handler.create('conversations', data)
    
    async def get_user_conversations(self, user_id: str,
                                   limit: int = 10) -> List[Dict[str, Any]]:
        """獲取用戶對話記錄"""
        conversations = await self.handler.read('conversations', {'user_id': user_id})
        return conversations[:limit]
    
    async def save_image(
        self,
        conversation_id: str,
        image_data: bytes,
        image_type: str,
        title: str = None,
        tags: List[str] = None
    ) -> Dict[str, Any]:
        """保存圖片"""
        metadata = {
            'conversation_id': conversation_id,
            'image_type': image_type,
            'title': title,
            'tags': tags
        }
        return await self.handler.save_image('images', image_data, metadata)
    
    async def get_conversation_images(self, conversation_id: str) -> List[Dict[str, Any]]:
        """獲取對話相關的圖片"""
        return await self.handler.get_images('images', {'conversation_id': conversation_id}) 