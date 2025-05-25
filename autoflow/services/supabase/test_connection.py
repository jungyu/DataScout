#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Supabase 連線測試腳本

此腳本用於測試 Supabase 資料庫的連線狀態和基本操作。
"""

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

import asyncio
from datetime import datetime
import time

from autoflow.services.supabase.service import SupabaseService
from autoflow.services.supabase.config import SupabaseConfig

async def test_connection():
    """測試 Supabase 連線"""
    print("開始測試 Supabase 連線...")
    
    try:
        # 初始化服務
        supabase = SupabaseService()
        print("✅ Supabase 服務初始化成功")
        
        # 測試創建用戶
        telegram_id = int(time.time())  # 使用當前時間戳作為 telegram_id
        test_user = await supabase.create_user(
            telegram_id=telegram_id,
            username="test_user",
            first_name="Test",
            last_name="User"
        )
        print("✅ 用戶創建成功:", test_user)
        
        # 測試查詢用戶
        user = await supabase.get_user(telegram_id)
        print("✅ 用戶查詢成功:", user)
        
        # 測試創建對話
        conversation = await supabase.create_conversation(
            user_id=test_user['id'],
            message="測試消息",
            response="測試回應",
            intend="測試意圖",
            command="測試指令"
        )
        print("✅ 對話創建成功:", conversation)
        
        # 測試查詢對話
        conversations = await supabase.get_user_conversations(test_user['id'])
        print("✅ 對話查詢成功:", conversations)
        
        # 測試保存圖片
        test_image_data = b"test_image_data"
        test_image = await supabase.save_image(
            conversation_id=conversation['id'],
            image_data=test_image_data,
            image_type="test/png",
            title="測試圖片",
            tags=["測試", "圖片", "示例"]
        )
        print("✅ 圖片保存成功:", test_image)
        
        # 測試查詢圖片
        images = await supabase.get_conversation_images(conversation['id'])
        print("✅ 圖片查詢成功:", images)
        
        print("\n所有測試完成！✅")
        
    except Exception as e:
        print(f"\n❌ 測試失敗：{str(e)}")
        raise

if __name__ == "__main__":
    # 檢查環境變數
    print("SUPABASE_URL:", os.getenv('SUPABASE_URL'))
    print("SUPABASE_KEY:", os.getenv('SUPABASE_KEY'))
    if not os.getenv('SUPABASE_URL') or not os.getenv('SUPABASE_KEY'):
        print("❌ 錯誤：未設置 SUPABASE_URL 或 SUPABASE_KEY 環境變數")
        sys.exit(1)
    
    # 運行測試
    asyncio.run(test_connection()) 