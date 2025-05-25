#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SupabaseHandler 測試腳本
"""

import os
import asyncio
import pytest
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
from persistence import SupabaseHandler, SupabaseConfig

# 測試配置
TEST_CONFIG = SupabaseConfig(
    url=os.getenv('SUPABASE_URL'),
    key=os.getenv('SUPABASE_KEY')
)

@pytest.fixture
def handler():
    """創建測試用的 SupabaseHandler 實例"""
    return SupabaseHandler(TEST_CONFIG)

@pytest.mark.asyncio
async def test_create_user(handler):
    """測試創建用戶"""
    # 創建測試用戶
    user = await handler.create('users', {
        'telegram_id': int(datetime.now().timestamp()),
        'username': 'test_user',
        'first_name': 'Test',
        'last_name': 'User'
    })
    
    assert user is not None
    assert 'id' in user
    assert user['username'] == 'test_user'
    
    return user

@pytest.mark.asyncio
async def test_get_user(handler):
    """測試獲取用戶"""
    # 先創建用戶
    user = await test_create_user(handler)
    
    # 查詢用戶
    users = await handler.read('users', {'telegram_id': user['telegram_id']})
    
    assert len(users) > 0
    assert users[0]['id'] == user['id']

@pytest.mark.asyncio
async def test_create_conversation(handler):
    """測試創建對話"""
    # 先創建用戶
    user = await test_create_user(handler)
    
    # 創建對話
    conversation = await handler.create('conversations', {
        'user_id': user['id'],
        'message': '測試消息',
        'response': '測試回應',
        'intend': '測試意圖',
        'command': '測試指令'
    })
    
    assert conversation is not None
    assert conversation['user_id'] == user['id']
    assert conversation['message'] == '測試消息'
    
    return conversation

@pytest.mark.asyncio
async def test_get_conversations(handler):
    """測試獲取對話"""
    # 先創建對話
    conversation = await test_create_conversation(handler)
    
    # 查詢對話
    conversations = await handler.read('conversations', {'user_id': conversation['user_id']})
    
    assert len(conversations) > 0
    assert conversations[0]['id'] == conversation['id']

@pytest.mark.asyncio
async def test_save_image(handler):
    """測試保存圖片"""
    # 先創建對話
    conversation = await test_create_conversation(handler)
    
    # 保存圖片
    image = await handler.save_image('images',
        image_data=b"test_image_data",
        metadata={
            'conversation_id': conversation['id'],
            'title': '測試圖片',
            'tags': ['測試', '圖片']
        }
    )
    
    assert image is not None
    assert image['conversation_id'] == conversation['id']
    assert image['title'] == '測試圖片'
    
    return image

@pytest.mark.asyncio
async def test_get_images(handler):
    """測試獲取圖片"""
    # 先保存圖片
    image = await test_save_image(handler)
    
    # 查詢圖片
    images = await handler.get_images('images', {'conversation_id': image['conversation_id']})
    
    assert len(images) > 0
    assert images[0]['id'] == image['id']

@pytest.mark.asyncio
async def test_update_conversation(handler):
    """測試更新對話"""
    # 先創建對話
    conversation = await test_create_conversation(handler)
    
    # 更新對話
    updated = await handler.update('conversations',
        query={'id': conversation['id']},
        data={'message': '更新後的消息'}
    )
    
    assert updated is not None
    assert updated['message'] == '更新後的消息'

@pytest.mark.asyncio
async def test_delete_conversation(handler):
    """測試刪除對話"""
    # 先創建對話
    conversation = await test_create_conversation(handler)
    
    # 刪除對話
    result = await handler.delete('conversations', {'id': conversation['id']})
    
    assert result is True
    
    # 確認已刪除
    conversations = await handler.read('conversations', {'id': conversation['id']})
    assert len(conversations) == 0

if __name__ == '__main__':
    asyncio.run(pytest.main([__file__, '-v'])) 