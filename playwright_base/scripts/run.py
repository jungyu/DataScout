#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
PlaywrightBase 獨立執行腳本

此腳本提供了命令行界面來執行 PlaywrightBase 的功能。
"""

import asyncio
import argparse
from playwright_base import PlaywrightBase
from playwright_base.anti_detection import HumanLikeBehavior

async def main():
    # 解析命令行參數
    parser = argparse.ArgumentParser(description='PlaywrightBase 命令行工具')
    parser.add_argument('--url', type=str, help='要訪問的網址')
    parser.add_argument('--headless', action='store_true', help='是否使用無頭模式')
    parser.add_argument('--screenshot', type=str, help='截圖保存路徑')
    args = parser.parse_args()

    # 創建瀏覽器實例
    browser = PlaywrightBase(headless=args.headless)
    
    try:
        # 啟動瀏覽器
        await browser.start()
        
        if args.url:
            # 訪問網頁
            await browser.goto(args.url)
            
            # 等待頁面載入
            await browser.wait_for_load_state("networkidle")
            
            if args.screenshot:
                # 截取截圖
                await browser.screenshot(args.screenshot)
                print(f"截圖已保存至: {args.screenshot}")
            
            # 獲取頁面標題
            title = await browser.page.title()
            print(f"頁面標題: {title}")
            
    except Exception as e:
        print(f"發生錯誤: {str(e)}")
    finally:
        # 關閉瀏覽器
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main()) 