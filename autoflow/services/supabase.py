#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Supabase 服務模組

此模組提供與 Supabase 的互動功能
"""

import logging
from typing import Dict, Any, Optional, List
from supabase import create_client, Client
from autoflow.core.config import Config
from datetime import datetime

logger = logging.getLogger(__name__)

class SupabaseService:
    """Supabase 服務類別"""
    
    def __init__(self):
        """初始化 Supabase 服務"""
        self.config = Config()
        self.client: Optional[Client] = None
        self.logger = logger
    
    async def connect(self) -> None:
        """連接到 Supabase"""
        try:
            # 驗證配置
            if not self.config.supabase_url or not self.config.supabase_service_role:
                raise ValueError("缺少 Supabase 配置")
            
            # 創建客戶端
            self.client = create_client(
                supabase_url=self.config.supabase_url,
                supabase_key=self.config.supabase_service_role
            )
            
            # 測試連接
            response = self.client.table('users').select('count').limit(1).execute()
            self.logger.info("成功連接到 Supabase")
            
        except Exception as e:
            self.logger.error(f"連接 Supabase 失敗: {str(e)}")
            raise
    
    async def disconnect(self) -> None:
        """斷開 Supabase 連接"""
        try:
            if self.client:
                # Supabase 客戶端不需要顯式斷開連接
                self.client = None
                self.logger.info("Supabase 服務已斷開連接")
        except Exception as e:
            self.logger.error(f"斷開 Supabase 連接時發生錯誤：{str(e)}")
            raise
    
    async def get_user(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """獲取用戶信息"""
        try:
            if not self.client:
                raise RuntimeError("Supabase 服務尚未連接")
            
            self.logger.debug(f"正在查詢用戶：telegram_id={telegram_id}")
            
            response = self.client.table('users').select('*').eq('telegram_id', telegram_id).execute()
            
            if not response.data:
                self.logger.debug(f"未找到用戶：telegram_id={telegram_id}")
                return None
                
            self.logger.debug(f"找到用戶：{response.data[0]}")
            return response.data[0]
            
        except Exception as e:
            self.logger.error(f"獲取用戶信息時發生錯誤：{str(e)}, telegram_id={telegram_id}")
            raise
    
    async def create_user(self, telegram_id: int, username: Optional[str] = None,
                         first_name: Optional[str] = None, last_name: Optional[str] = None) -> Dict[str, Any]:
        """創建用戶"""
        try:
            if not self.client:
                raise RuntimeError("Supabase 服務尚未連接")
            
            user_data = {
                'telegram_id': telegram_id,
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
                'created_at': datetime.now().isoformat(),
                'last_active': datetime.now().isoformat(),
                'status': 'active'
            }
            
            self.logger.debug(f"正在創建用戶：{user_data}")
            
            response = self.client.table('users').insert(user_data).execute()
            
            if not response.data:
                raise RuntimeError("創建用戶失敗：沒有返回數據")
                
            self.logger.debug(f"成功創建用戶：{response.data[0]}")
            return response.data[0]
            
        except Exception as e:
            self.logger.error(f"創建用戶時發生錯誤：{str(e)}, telegram_id={telegram_id}")
            raise
    
    async def create_conversation(self, user_id: str, message: str, response: str) -> Dict[str, Any]:
        """記錄對話"""
        try:
            if not self.client:
                raise RuntimeError("Supabase 服務尚未連接")
            
            conversation_data = {
                'user_id': user_id,
                'message': message,
                'response': response,
                'message_type': 'stock_query',
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }
            
            self.logger.debug(f"正在記錄對話：{conversation_data}")
            
            response = self.client.table('conversations').insert(conversation_data).execute()
            
            if not response.data:
                raise RuntimeError("記錄對話失敗：沒有返回數據")
                
            self.logger.debug(f"成功記錄對話：{response.data[0]}")
            return response.data[0]
            
        except Exception as e:
            self.logger.error(f"記錄對話時發生錯誤：{str(e)}, user_id={user_id}")
            raise
    
    async def create(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """創建記錄
        
        Args:
            table: 表名
            data: 要插入的數據
            
        Returns:
            Dict[str, Any]: 創建的記錄
        """
        try:
            if not self.client:
                raise RuntimeError("Supabase 服務尚未連接")
            
            # 確保數據類型正確
            if table == 'bots':
                data = {
                    'bot_id': int(data['bot_id']),
                    'username': str(data['username']),
                    'first_name': str(data['first_name']),
                    'is_bot': bool(data['is_bot']),
                    'can_join_groups': bool(data.get('can_join_groups', False)),
                    'can_read_all_group_messages': bool(data.get('can_read_all_group_messages', False)),
                    'supports_inline_queries': bool(data.get('supports_inline_queries', False)),
                    'created_at': str(data['created_at']),
                    'status': str(data['status'])
                }
            
            self.logger.debug(f"正在向表 {table} 插入數據：{data}")
            
            # 執行插入操作
            response = self.client.table(table).insert(data).execute()
            
            if not response.data:
                raise RuntimeError(f"插入數據失敗：沒有返回數據")
            
            self.logger.debug(f"成功插入數據到表 {table}：{response.data[0]}")
            return response.data[0]
            
        except Exception as e:
            self.logger.error(f"創建記錄時發生錯誤：{str(e)}, 表：{table}, 數據：{data}")
            raise
    
    async def update_user(self, telegram_id: int, **kwargs) -> Dict[str, Any]:
        """更新用戶信息
        
        Args:
            telegram_id: Telegram 用戶 ID
            **kwargs: 要更新的欄位和值
            
        Returns:
            Dict[str, Any]: 更新後的用戶信息
        """
        try:
            if not self.client:
                raise RuntimeError("Supabase 服務尚未連接")
            
            response = self.client.table('users').update(kwargs).eq('telegram_id', telegram_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            self.logger.error(f"更新用戶信息時發生錯誤：{str(e)}")
            raise
    
    async def get_bot(self, bot_id: int) -> Optional[Dict[str, Any]]:
        """獲取機器人信息
        
        Args:
            bot_id: 機器人 ID
            
        Returns:
            Optional[Dict[str, Any]]: 機器人信息字典，如果不存在則返回 None
        """
        try:
            if not self.client:
                raise RuntimeError("Supabase 服務尚未連接")
                
            response = self.client.table('bots').select('*').eq('bot_id', bot_id).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            self.logger.error(f"獲取機器人信息時發生錯誤：{str(e)}")
            return None
            
    async def update_bot(self, bot_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """更新機器人信息
        
        Args:
            bot_id: 機器人 ID
            data: 要更新的數據
            
        Returns:
            Optional[Dict[str, Any]]: 更新後的機器人信息，如果失敗則返回 None
        """
        try:
            if not self.client:
                raise RuntimeError("Supabase 服務尚未連接")
                
            response = self.client.table('bots').update(data).eq('bot_id', bot_id).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            self.logger.error(f"更新機器人信息時發生錯誤：{str(e)}")
            return None 