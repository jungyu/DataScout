#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
驗證碼適配器使用示例

此示例展示如何使用驗證碼適配器：
1. 初始化驗證碼適配器
2. 檢測驗證碼
3. 解決各種類型的驗證碼
4. 獲取已解決的驗證碼列表
"""

import asyncio
import os
import time
from loguru import logger

from playwright.async_api import async_playwright
from ..captcha.adapter import CaptchaAdapter


async def main():
    """主函數"""
    # 設置驗證碼 API 密鑰
    api_key = os.getenv("CAPTCHA_API_KEY")
    if not api_key:
        logger.error("未設置驗證碼 API 密鑰")
        return
    
    async with async_playwright() as p:
        # 啟動瀏覽器
        browser = await p.chromium.launch(
            headless=False,
            args=['--no-sandbox']
        )
        
        # 創建新頁面
        page = await browser.new_page()
        
        try:
            # 初始化驗證碼適配器
            captcha_adapter = CaptchaAdapter(
                page=page,
                api_key=api_key,
                service="2captcha",
                timeout=120,
                retry_count=3
            )
            
            # 訪問目標網站
            await page.goto('https://example.com')
            
            # 檢測驗證碼
            selectors = {
                "recaptcha": "iframe[title*='reCAPTCHA']",
                "hcaptcha": "iframe[title*='hCaptcha']",
                "image_captcha": "#captcha-image",
                "slider_captcha": "#slider"
            }
            
            if captcha_adapter.detect_captcha(selectors):
                logger.info("檢測到驗證碼")
                
                # 解決 reCAPTCHA
                if await page.locator(selectors["recaptcha"]).count() > 0:
                    logger.info("解決 reCAPTCHA")
                    result = await captcha_adapter.solve_recaptcha(
                        site_key="your-site-key",
                        action="submit"
                    )
                    logger.info(f"reCAPTCHA 解決結果: {result}")
                
                # 解決 hCaptcha
                if await page.locator(selectors["hcaptcha"]).count() > 0:
                    logger.info("解決 hCaptcha")
                    result = await captcha_adapter.solve_hcaptcha(
                        site_key="your-site-key"
                    )
                    logger.info(f"hCaptcha 解決結果: {result}")
                
                # 解決圖像驗證碼
                if await page.locator(selectors["image_captcha"]).count() > 0:
                    logger.info("解決圖像驗證碼")
                    result = await captcha_adapter.solve_image_captcha(
                        selector=selectors["image_captcha"]
                    )
                    logger.info(f"圖像驗證碼解決結果: {result}")
                
                # 解決滑塊驗證碼
                if await page.locator(selectors["slider_captcha"]).count() > 0:
                    logger.info("解決滑塊驗證碼")
                    result = await captcha_adapter.solve_slider_captcha(
                        slider_selector=selectors["slider_captcha"],
                        background_selector="#background"
                    )
                    logger.info(f"滑塊驗證碼解決結果: {result}")
                
                # 獲取已解決的驗證碼列表
                solved_captchas = captcha_adapter.get_solved_captchas()
                logger.info(f"已解決的驗證碼列表: {solved_captchas}")
                
                # 清空已解決的驗證碼列表
                captcha_adapter.clear_solved_captchas()
                logger.info("已清空驗證碼列表")
            else:
                logger.info("未檢測到驗證碼")
            
        except Exception as e:
            logger.error(f"發生錯誤: {str(e)}")
        
        finally:
            # 關閉瀏覽器
            await browser.close()


if __name__ == '__main__':
    asyncio.run(main()) 