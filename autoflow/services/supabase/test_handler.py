#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Supabase Handler 測試模組

此模組用於測試 SupabaseHandler 的自動初始化功能。
"""

import os
import asyncio
from typing import Dict, Any
from .handler import SupabaseHandler
from .config import SupabaseConfig

async def test_handler_initialization():
    """測試 Handler 的自動初始化功能"""
    print("開始測試 SupabaseHandler 自動初始化...")
    
    # 初始化配置
    config = SupabaseConfig(
        url=os.getenv('SUPABASE_URL'),
        key=os.getenv('SUPABASE_KEY')
    )
    
    # 創建 handler 實例
    handler = SupabaseHandler(config)
    print("Handler 實例已創建")
    
    # 測試創建用戶
    test_user = {
        'telegram_id': 123456789,
        'username': 'test_user',
        'first_name': 'Test',
        'last_name': 'User'
    }
    
    try:
        # 這裡會觸發自動初始化
        result = await handler.create('users', test_user)
        print(f"用戶創建成功: {result}")
        
        # 測試讀取用戶
        users = await handler.read('users', {'telegram_id': test_user['telegram_id']})
        print(f"讀取用戶成功: {users}")
        
        if users:
            user_id = users[0]['id']
            # 測試更新用戶
            update_data = {'username': 'updated_test_user'}
            updated_user = await handler.update('users', user_id, update_data)
            print(f"更新用戶成功: {updated_user}")
            
            # 測試刪除用戶
            delete_result = await handler.delete('users', user_id)
            print(f"刪除用戶成功: {delete_result}")
        
    except Exception as e:
        print(f"測試過程中發生錯誤: {str(e)}")
        raise

async def main():
    """主測試函數"""
    try:
        await test_handler_initialization()
        print("所有測試完成！")
    except Exception as e:
        print(f"測試失敗: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 