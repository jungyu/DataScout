"""
error_handler.py - 網頁爬取中常見錯誤處理工具

處理 HTTP 錯誤、403 禁止訪問、人機驗證等常見阻礙
"""

import time
import random
from pathlib import Path
from typing import Optional, Dict, Any
from playwright.sync_api import Page

from playwright_base.utils.logger import setup_logger

# 設置日誌
logger = setup_logger(name=__name__)

class ErrorHandler:
    """處理網頁爬取過程中的各種錯誤和阻礙"""
    
    @staticmethod
    def handle_403_error(page: Page) -> bool:
        """處理 403 Forbidden 錯誤
        
        有時網站會使用 403 錯誤來阻止爬蟲。
        此方法嘗試通過各種方式來繞過這個限制。
        
        Args:
            page: Playwright 頁面對象
            
        Returns:
            bool: 如果成功處理了 403 錯誤則返回 True，否則返回 False
        """
        try:
            # 檢查頁面內容是否包含 403 或 "Access Denied" 相關文字
            page_content = page.content().lower()
            page_text = page.inner_text('body').lower()
            
            is_403_page = (
                "403" in page_text or
                "forbidden" in page_text or 
                "access denied" in page_text or
                "403" in page_content or
                "forbidden" in page_content or
                "access denied" in page_content
            )
            
            if not is_403_page:
                return False
            
            logger.warning("檢測到 403 錯誤頁面，嘗試繞過...")
            
            # 保存錯誤頁面截圖
            try:
                timestamp = int(time.time())
                logs_dir = Path("logs")
                logs_dir.mkdir(exist_ok=True)
                page.screenshot(path=f"logs/error403_{timestamp}.png")
            except Exception:
                pass
            
            # 方法 1: 清除所有 cookies 並重新載入
            try:
                context = page.context
                context.clear_cookies()
                logger.info("已清除所有 cookies")
                page.reload(wait_until="domcontentloaded")
                page.wait_for_load_state("networkidle")
                
                # 檢查是否仍然有 403 錯誤
                if "403" not in page.content() and "access denied" not in page.content().lower():
                    logger.info("清除 cookies 後成功繞過 403 錯誤")
                    return True
            except Exception as e:
                logger.debug(f"清除 cookies 方法失敗: {str(e)}")
            
            # 方法 2: 修改 User-Agent 並重新載入
            try:
                current_url = page.url
                # 選擇一個非常普通的 Chrome/Firefox User-Agent
                new_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
                
                # 通過 JavaScript 修改 User-Agent
                page.evaluate(f"""
                    () => {{
                        Object.defineProperty(navigator, 'userAgent', {{
                            get: function() {{ return '{new_user_agent}'; }}
                        }});
                    }}
                """)
                
                logger.info(f"已修改 User-Agent")
                page.reload(wait_until="domcontentloaded")
                
                # 檢查是否仍然有 403 錯誤
                if "403" not in page.content() and "access denied" not in page.content().lower():
                    logger.info("修改 User-Agent 後成功繞過 403 錯誤")
                    return True
            except Exception as e:
                logger.debug(f"修改 User-Agent 方法失敗: {str(e)}")
                
            # 方法 3: 等待後再次嘗試
            logger.info("等待 5 秒後再嘗試...")
            page.wait_for_timeout(5000)
            page.reload(wait_until="domcontentloaded")
            
            # 檢查是否仍然有 403 錯誤
            if "403" not in page.content() and "access denied" not in page.content().lower():
                logger.info("等待後重試成功繞過 403 錯誤")
                return True
                
            # 方法 4: 使用 JS fetch API 嘗試繞過
            try:
                logger.info("使用 fetch API 嘗試繞過 403 錯誤...")
                
                # 使用自定義標頭進行 fetch 請求
                html_content = page.evaluate("""
                    async (url) => {
                        try {
                            const response = await fetch(url, {
                                method: 'GET',
                                headers: {
                                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0',
                                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                                    'Accept-Language': 'en-US,en;q=0.9',
                                    'Referer': 'https://www.google.com/',
                                    'DNT': '1',
                                    'Connection': 'keep-alive',
                                    'Upgrade-Insecure-Requests': '1'
                                },
                                credentials: 'include'
                            });
                            
                            if (!response.ok) {
                                return null;
                            }
                            
                            return await response.text();
                        } catch(e) {
                            return null;
                        }
                    }
                """, current_url)
                
                if html_content:
                    # 如果成功獲取內容，將其設置為當前頁面內容
                    page.set_content(html_content)
                    logger.info("成功使用 fetch API 繞過 403 錯誤")
                    return True
            except Exception as e:
                logger.debug(f"使用 fetch API 方法失敗: {str(e)}")
            
            logger.warning("所有嘗試繞過 403 錯誤的方法都失敗了")
            return False
            
        except Exception as e:
            logger.debug(f"處理 403 錯誤時出現問題: {str(e)}")
            return False
            
    @staticmethod
    def handle_hold_button_verification(page: Page) -> bool:
        """處理需要按住按鈕驗證的頁面
        
        有些網站會顯示「檢測到不尋常活動」頁面，
        要求使用者按住「按住不放」按鈕一段時間才能通過驗證。
        
        Args:
            page: Playwright 頁面對象
            
        Returns:
            bool: 如果檢測到並處理了驗證頁面則返回 True，否則返回 False
        """
        try:
            # 首先保存完整頁面截圖和源碼到指定日誌目錄，方便診斷問題
            try:
                logs_dir = Path("logs")
                logs_dir.mkdir(exist_ok=True)
                timestamp = int(time.time())
                
                # 保存截圖
                screenshot_path = f"logs/page_capture_{timestamp}.png"
                page.screenshot(path=screenshot_path)
                
                # 保存頁面源碼
                html_path = f"logs/page_html_{timestamp}.html"
                html_content = page.content()
                with open(html_path, "w", encoding="utf-8") as f:
                    f.write(html_content)
                    
                logger.info(f"已保存頁面截圖至 {screenshot_path} 和源碼至 {html_path}")
            except Exception as e:
                logger.debug(f"保存頁面診斷信息出錯: {str(e)}")
            
            # 檢測是否是403頁面
            try:
                title = page.title()
                if "403" in title or "Forbidden" in title:
                    logger.info("從標題檢測到403頁面")
                    return ErrorHandler.handle_403_error(page)
                    
                # 從頁面內容檢測是否為403錯誤
                content = page.content()
                if "403 Forbidden" in content or "Access Denied" in content:
                    logger.info("從內容檢測到403頁面")
                    return ErrorHandler.handle_403_error(page)
            except Exception:
                pass
            
            # 檢查是否存在驗證頁面特徵
            verification_detected = False
            
            # 檢查頁面上是否有明確的反爬蟲驗證提示
            try:
                page_text = page.inner_text('body')
                verification_phrases = [
                    "We've detected unusual activity",
                    "我們檢測到不尋常的活動",
                    "按住不放",
                    "Hold to continue",
                    "Please hold the button",
                    "Press and hold",
                    "Verify you're not a robot"
                ]
                
                for phrase in verification_phrases:
                    if phrase in page_text:
                        verification_detected = True
                        logger.info(f"從頁面文本檢測到驗證頁面: '{phrase}'")
                        break
            except Exception:
                pass

            # 如果沒有檢測到驗證頁面，嘗試查找驗證按鈕
            if not verification_detected:
                # 嘗試直接查找驗證按鈕的存在
                button_texts = ["按住不放", "Hold", "Hold And Release", "Press"]
                for text in button_texts:
                    try:
                        button = page.get_by_text(text, exact=False)
                        if button.count() > 0:
                            verification_detected = True
                            logger.info(f"找到可能的驗證按鈕: '{text}'")
                            break
                    except Exception:
                        continue
                        
            # 最後嘗試通過頁面 URL 來判斷
            try:
                url = page.url
                if "captcha" in url or "verification" in url or "challenge" in url:
                    verification_detected = True
                    logger.info(f"從 URL 檢測到潛在的驗證頁面: {url}")
            except Exception:
                pass

            # 如果沒有檢測到驗證頁面，返回 False
            if not verification_detected:
                return False
                
            # 直接打印頁面上所有按鈕的文字，用於診斷
            try:
                logger.info("頁面上的所有按鈕:")
                buttons = page.query_selector_all("button")
                for i, button in enumerate(buttons):
                    try:
                        button_text = button.inner_text().strip()
                        if button_text:
                            logger.info(f"  按鈕 {i+1}: '{button_text}'")
                    except:
                        continue
            except Exception as e:
                logger.debug(f"列出按鈕時出錯: {str(e)}")
            
            logger.info("嘗試處理驗證...")
            
            # 使用更靈活的方法查找和處理驗證按鈕
            verification_button = None
            
            # 1. 嘗試通過內容查找
            try:
                content_matches = [
                    page.get_by_text("按住不放"),
                    page.get_by_text("Hold"),
                    page.get_by_text("Press and hold"),
                    page.get_by_role("button", name="Hold"),
                    page.get_by_role("button", name="按住不放")
                ]
                
                for match in content_matches:
                    try:
                        if match.count() > 0:
                            verification_button = match.first
                            logger.info(f"找到驗證按鈕: {match.first.inner_text() if hasattr(match.first, 'inner_text') else 'unknown'}")
                            break
                    except Exception:
                        continue
            except Exception as e:
                logger.debug(f"通過內容查找按鈕時出錯: {str(e)}")
                
            # 2. 如果找不到明確的按鈕，嘗試模糊匹配
            if not verification_button:
                try:
                    # 獲取所有可見按鈕
                    buttons = page.query_selector_all("button")
                    
                    for button in buttons:
                        try:
                            button_text = button.inner_text().lower()
                            if any(kw.lower() in button_text for kw in ["hold", "press", "按住"]):
                                verification_button = button
                                logger.info(f"通過模糊匹配找到驗證按鈕: '{button_text}'")
                                break
                        except Exception:
                            continue
                except Exception as e:
                    logger.debug(f"模糊匹配按鈕時出錯: {str(e)}")
            
            # 3. 如果仍然找不到按鈕，嘗試針對具體頁面結構查找
            if not verification_button:
                try:
                    # 常見容器中的按鈕
                    containers = [
                        ".captcha-container button",
                        ".verification-container button",
                        ".challenge-container button",
                        ".modal-body button",
                        ".main-container button",
                        ".container button"
                    ]
                    
                    for container in containers:
                        try:
                            btn = page.query_selector(container)
                            if btn:
                                verification_button = btn
                                logger.info(f"在容器中找到可能的驗證按鈕: '{container}'")
                                break
                        except Exception:
                            continue
                except Exception as e:
                    logger.debug(f"通過容器查找按鈕時出錯: {str(e)}")
            
            # 如果無法找到按鈕，則嘗試直接操作頁面中央位置
            if not verification_button:
                logger.warning("無法找到具體的驗證按鈕，嘗試點擊頁面中央")
                try:
                    # 獲取頁面尺寸
                    viewport = page.viewport_size
                    center_x = viewport["width"] // 2
                    center_y = viewport["height"] // 2
                    
                    # 模擬在頁面中央按住滑鼠
                    page.mouse.move(center_x, center_y)
                    page.wait_for_timeout(1000)
                    page.mouse.down()
                    
                    # 保持按住 8 秒
                    logger.info("在頁面中央按住滑鼠 8 秒...")
                    page.wait_for_timeout(8000)
                    
                    # 釋放滑鼠
                    page.mouse.up()
                    logger.info("已釋放滑鼠")
                    
                    # 等待頁面可能的變化
                    page.wait_for_timeout(3000)
                    
                    # 檢查頁面是否變化
                    current_url = page.url
                    if "captcha" not in current_url and "verification" not in current_url:
                        logger.info("頁面已變化，可能驗證成功")
                        return True
                    
                    return False
                except Exception as e:
                    logger.error(f"嘗試點擊頁面中央時出錯: {str(e)}")
                    return False
            
            # 執行按住操作
            try:
                # 確保按鈕在視窗內
                verification_button.scroll_into_view_if_needed()
                page.wait_for_timeout(1000)
                
                # 獲取按鈕位置
                box = verification_button.bounding_box()
                if not box:
                    logger.error("無法獲取按鈕位置")
                    return False
                
                center_x = box["x"] + box["width"] / 2
                center_y = box["y"] + box["height"] / 2
                
                # 先嘗試點擊按鈕（有時需要先點擊激活）
                page.mouse.click(center_x, center_y)
                page.wait_for_timeout(1000)
                
                # 移動到按鈕上方
                page.mouse.move(center_x, center_y)
                page.wait_for_timeout(500)
                
                # 按下滑鼠
                logger.info("開始按住按鈕...")
                page.mouse.down()
                
                # 隨機生成較長的按住時間 (8-10秒)，增加成功率
                hold_time = random.uniform(8000, 10000)
                logger.info(f"按住滑鼠 {hold_time/1000:.1f} 秒...")
                page.wait_for_timeout(int(hold_time))
                
                # 釋放滑鼠按鍵
                page.mouse.up()
                logger.info("已釋放滑鼠按鈕")
                
                # 等待頁面可能的跳轉或變化
                logger.info("等待頁面變化...")
                page.wait_for_timeout(5000)
                
                # 檢查頁面是否變化
                try:
                    current_url = page.url
                    page_text = page.inner_text('body')
                    
                    # 檢查是否還有驗證相關文字
                    verification_still_present = any(phrase in page_text for phrase in verification_phrases)
                    
                    if not verification_still_present:
                        logger.info("驗證成功，頁面已變化!")
                        return True
                    else:
                        logger.warning("驗證可能未成功，頁面仍顯示驗證內容")
                        return False
                except Exception as e:
                    logger.error(f"檢查驗證結果時出錯: {str(e)}")
                    return False
                
            except Exception as e:
                logger.error(f"執行按住操作時出錯: {str(e)}")
                return False
                
        except Exception as e:
            logger.error(f"處理驗證頁面時出錯: {str(e)}")
            return False
