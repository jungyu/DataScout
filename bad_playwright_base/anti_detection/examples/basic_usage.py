#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
反檢測模組使用示例

此示例展示如何使用反檢測模組的基本功能：
1. 初始化反檢測管理器
2. 配置反檢測選項
3. 應用反檢測功能
4. 模擬人類行為
5. 管理代理和用戶代理
"""

import asyncio
from playwright.async_api import async_playwright
from loguru import logger

from ..anti_detection_manager import AntiDetectionManager


async def main():
    """主函數"""
    # 初始化反檢測管理器
    anti_detection = AntiDetectionManager()
    
    # 配置反檢測選項
    config = {
        "enabled": True,
        "fingerprint": {
            "enabled": True,
            "webgl": True,
            "canvas": True,
            "audio": True,
            "font": True,
            "screen": True,
            "platform": True
        },
        "proxy": {
            "enabled": True,
            "rotation_interval": 300,  # 5分鐘
            "blacklist_duration": 3600  # 1小時
        },
        "behavior": {
            "enabled": True,
            "mouse_speed": {
                "min": 0.5,
                "max": 2.0
            },
            "typing_speed": {
                "min": 100,
                "max": 300
            },
            "scroll_speed": {
                "min": 100,
                "max": 500
            },
            "click_delay": {
                "min": 0.1,
                "max": 0.5
            },
            "form_delay": {
                "min": 0.5,
                "max": 2.0
            }
        },
        "user_agent": {
            "enabled": True,
            "rotation_interval": 3600,  # 1小時
            "blacklist_duration": 86400  # 24小時
        }
    }
    anti_detection.set_config(config)
    
    # 添加代理
    proxy = {
        "server": "http://proxy.example.com:8080",
        "username": "user",
        "password": "pass"
    }
    anti_detection.add_proxy(proxy)
    
    async with async_playwright() as p:
        # 啟動瀏覽器
        browser = await p.chromium.launch(
            headless=False,
            args=['--no-sandbox']
        )
        
        # 創建新頁面
        page = await browser.new_page()
        
        try:
            # 應用反檢測功能
            await anti_detection.apply_anti_detection(page)
            
            # 訪問目標網站
            await page.goto('https://example.com')
            
            # 模擬人類行為
            # 1. 滾動頁面
            await anti_detection.scroll_page(page)
            
            # 2. 移動鼠標到元素
            button = await page.query_selector('#submit-button')
            if button:
                box = await button.bounding_box()
                if box:
                    await anti_detection.move_mouse(page, (box['x'] + box['width']/2, box['y'] + box['height']/2))
            
            # 3. 填寫表單
            form_data = {
                '#username': 'test_user',
                '#password': 'test_pass',
                '#email': 'test@example.com'
            }
            await anti_detection.fill_form(page, form_data)
            
            # 4. 點擊提交按鈕
            await anti_detection.click_element(page, '#submit-button')
            
            # 等待結果
            await page.wait_for_load_state('networkidle')
            
            # 檢查結果
            if await page.query_selector('.success-message'):
                logger.info("表單提交成功")
            else:
                logger.warning("表單提交失敗")
            
        except Exception as e:
            logger.error(f"發生錯誤: {str(e)}")
        
        finally:
            # 關閉瀏覽器
            await browser.close()
            
            # 清理黑名單
            anti_detection.clean_blacklists()


if __name__ == '__main__':
    asyncio.run(main()) 