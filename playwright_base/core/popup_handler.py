"""
popup_handler.py - 處理網站常見彈窗

處理 cookie banner、訂閱彈窗、付費牆等干擾爬取的彈窗元素
"""
from typing import Dict, List, Union, Optional
from loguru import logger
import re


def check_and_handle_popup(page, selectors: Optional[Dict[str, List[str]]] = None) -> bool:
    """
    檢查並處理常見網頁彈窗
    
    Args:
        page: Playwright 頁面對象
        selectors: 自定義的選擇器字典，格式如 {
            "cookie": ["#cookie-banner", ".cookie-consent", ...], 
            "popup": [".modal", "#popup", ...],
            "paywall": [".paywall", "#subscribe-wall", ...]
        }
        
    Returns:
        bool: 是否有處理任何彈窗
    """
    # 預設常見的彈窗選擇器
    default_selectors = {
        "cookie": [
            "#cookie-banner",
            ".cookie-consent",
            ".cookie-notice",
            "#cookie-consent",
            ".cookie-popup",
            "#cookieConsent",
            "[class*='cookie']",
            "#cookies-eu-banner",
            "#cookie_directive_container",
            ".cookie-agree-button",
            ".js-cookie-banner",
            "#customer-cookie-disclaimer"
        ],
        "popup": [
            ".modal",
            ".modal-dialog",
            ".popup",
            ".overlay",
            "#newsletter-popup",
            "#popup-container",
            "#subscribe-popup",
            ".subscription-overlay",
            ".signup-modal",
            ".newsletter-signup",
            "#exit-intent-modal",
            "[class*='modal'][class*='show']",
            "[class*='popup'][style*='display: block']"
        ],
        "paywall": [
            ".paywall",
            "#paywall",
            ".subscribe-wall",
            "#subscription-wall",
            ".premium-required",
            ".paid-content",
            ".meter-paywall",
            ".payment-module-redesign"
        ],
        "welcome": [
            ".welcome-dialog",
            "#welcome-message",
            ".first-time-visit",
            ".intro-popup",
            ".welcome-overlay",
            ".welcome-modal",
            "#welcome-popup"
        ],
        "close": [
            ".close",
            ".dismiss",
            ".close-button",
            ".modal-close",
            ".popup-close",
            ".btn-close",
            "#close-button",
            "[aria-label='Close']",
            "[data-dismiss='modal']",
            "[class*='close']",
            ".icon-close",
            ".dialog__close",
            ".js-dismissButton"
        ],
        "accept": [
            ".accept",
            ".accept-button",
            ".accept-cookies",
            "#accept-cookies",
            ".agree-button",
            ".consent-accept",
            ".cookie-accept",
            "[class*='accept']",
            "[class*='agree']",
            "button[value='Accept']",
            "button[value='OK']",
            "button.accept",
            "button.agree",
            "button.ok",
            "button.allow"
        ],
        "xpath_buttons": [
            "//button[text()='Accept']",
            "//button[text()='OK']",
            "//button[text()='Allow']",
            "//button[text()='I agree']",
            "//button[text()='I Agree']",
            "//button[text()='Accept All']",
            "//button[text()='Accept all']",
            "//button[text()='Accept Cookies']",
            "//button[contains(text(), 'Accept')]",
            "//button[contains(text(), 'Allow')]"
        ]
    }
    
    # 合併自定義選擇器與預設選擇器
    if selectors:
        for category, selector_list in selectors.items():
            if category in default_selectors:
                default_selectors[category].extend(selector_list)
            else:
                default_selectors[category] = selector_list
    
    handled = False
    
    try:
        # 嘗試優先處理關閉按鈕
        for close_selector in default_selectors.get("close", []):
            try:
                close_elements = page.locator(close_selector).all()
                for close_element in close_elements:
                    visible = close_element.is_visible()
                    if visible:
                        # 嘗試點擊關閉按鈕
                        close_element.click()
                        logger.info(f"已點擊關閉按鈕: {close_selector}")
                        handled = True
            except Exception as e:
                logger.debug(f"嘗試點擊關閉按鈕時出錯 ({close_selector}): {str(e)}")
        
        # 處理接受按鈕（特別是 Cookie 相關）
        for accept_selector in default_selectors.get("accept", []):
            try:
                accept_elements = page.locator(accept_selector).all()
                for accept_element in accept_elements:
                    visible = accept_element.is_visible()
                    if visible:
                        # 檢查按鈕上的文字（避免誤點訂閱按鈕）
                        text = accept_element.inner_text().lower()
                        safe_texts = ["accept", "agree", "ok", "allow", "cookie", "consent"]
                        if any(safe in text for safe in safe_texts):
                            accept_element.click()
                            logger.info(f"已點擊接受按鈕: {accept_selector} ('{text}')")
                            handled = True
            except Exception as e:
                logger.debug(f"嘗試點擊接受按鈕時出錯 ({accept_selector}): {str(e)}")
        
        # 處理 XPath 按鈕選擇器 - 針對包含指定文字的按鈕
        for xpath in default_selectors.get("xpath_buttons", []):
            try:
                # 使用 page.locator 的 xpath 方法處理 XPath 選擇器
                xpath_elements = page.locator(f"xpath={xpath}").all()
                for element in xpath_elements:
                    visible = element.is_visible()
                    if visible:
                        element.click()
                        logger.info(f"已點擊 XPath 按鈕: {xpath}")
                        handled = True
                        break
            except Exception as e:
                logger.debug(f"嘗試點擊 XPath 按鈕時出錯 ({xpath}): {str(e)}")
        
        # 檢查各種類型的彈窗
        for popup_type in ["cookie", "popup", "paywall", "welcome"]:
            for selector in default_selectors.get(popup_type, []):
                try:
                    popup_elements = page.locator(selector).all()
                    for popup in popup_elements:
                        visible = popup.is_visible()
                        if visible:
                            logger.info(f"檢測到 {popup_type} 彈窗: {selector}")
                            
                            # 先尋找彈窗內的關閉按鈕
                            for close_sel in default_selectors.get("close", []):
                                try:
                                    if popup.locator(close_sel).count() > 0:
                                        popup.locator(close_sel).first.click()
                                        logger.info(f"已點擊 {popup_type} 彈窗中的關閉按鈕: {close_sel}")
                                        handled = True
                                        break
                                except:
                                    pass
                            
                            # 對於 cookie 彈窗，尋找接受按鈕
                            if popup_type == "cookie":
                                for accept_sel in default_selectors.get("accept", []):
                                    try:
                                        if popup.locator(accept_sel).count() > 0:
                                            popup.locator(accept_sel).first.click()
                                            logger.info(f"已點擊 cookie 彈窗中的接受按鈕: {accept_sel}")
                                            handled = True
                                            break
                                    except:
                                        pass
                            
                            # 對於無法關閉的付費牆，可以嘗試隱藏
                            if popup_type == "paywall" and not handled:
                                try:
                                    # 注入腳本隱藏元素並恢復頁面滾動
                                    page.evaluate(f"""
                                        (selector) => {{
                                            const elements = document.querySelectorAll(selector);
                                            for (const el of elements) {{
                                                el.style.display = 'none';
                                            }}
                                            document.body.style.overflow = 'auto';
                                            document.documentElement.style.overflow = 'auto';
                                        }}
                                    """, selector)
                                    logger.info(f"已通過CSS隱藏付費牆元素: {selector}")
                                    handled = True
                                except:
                                    pass
                except Exception as e:
                    logger.debug(f"處理 {popup_type} 彈窗時出錯 ({selector}): {str(e)}")
        
        # 如果頁面被覆蓋（通常是彈窗引起），嘗試修復滾動
        if handled:
            try:
                page.evaluate("""
                    () => {
                        document.body.style.overflow = 'auto';
                        document.documentElement.style.overflow = 'auto';
                    }
                """)
            except:
                pass
                
        return handled
        
    except Exception as e:
        logger.warning(f"處理彈窗過程中發生錯誤: {str(e)}")
        return handled


def handle_popups(page, auto_close_popups: bool = True, custom_selectors: Optional[Dict[str, List[str]]] = None) -> bool:
    """
    通用的彈窗處理函數，支援自定義選擇器和各類型彈窗
    
    Args:
        page: Playwright 頁面對象
        auto_close_popups: 是否自動關閉彈窗
        custom_selectors: 自定義的選擇器字典
        
    Returns:
        bool: 如果處理了任何彈窗則返回 True，否則返回 False
    """
    if not auto_close_popups:
        return False
    
    try:
        # 使用標準的 CSS 選擇器，避免使用不支援的選擇器語法
        popup_selectors = {
            'popup': ['.modal', '.popup', '[id*="popup"]', '[class*="popup"]', '.overlay', '.dialog'],
            'paywall': ['.paywall', '.require-subscription', '.subscription-banner'],
            'cookie': ['.cookie-banner', '.cookie-policy', '[class*="cookie"]', '.cookie-consent', '.cookie-notice'],
            'newsletter': ['.newsletter-signup', '.subscription-form'],
            'close': [
                '.close', '.dismiss', '.close-button', '[aria-label="Close"]',
                '.modal-close', '.btn-close', 'button[data-dismiss="modal"]'
            ],
            'accept': [
                '.accept-cookies', '.accept-button', '.agree-button',
                'button.accept', 'button.ok', 'button.confirm',
                'button[value="Accept"]', 'button.allow'
            ],
            'xpath_buttons': [
                "//button[text()='OK']",
                "//button[text()='Accept']",
                "//button[text()='Close']",
                "//button[text()='Allow']",
                "//button[text()='I Agree']"
            ]
        }
        
        # 合併自定義選擇器
        if custom_selectors:
            for category, selectors in custom_selectors.items():
                if category in popup_selectors:
                    popup_selectors[category].extend(selectors)
                else:
                    popup_selectors[category] = selectors
        
        # 使用 check_and_handle_popup 處理彈窗
        popups_handled = check_and_handle_popup(page, popup_selectors)
        
        # 如果沒有成功處理，嘗試使用 XPath 選擇器手動處理
        if not popups_handled:
            for xpath in popup_selectors.get("xpath_buttons", []):
                try:
                    # 使用 page.locator 的 xpath 方法處理 XPath 選擇器
                    xpath_elements = page.locator(f"xpath={xpath}").all()
                    for element in xpath_elements:
                        if element.is_visible():
                            element.click()
                            logger.info(f"已點擊 XPath 按鈕: {xpath}")
                            popups_handled = True
                            break
                except Exception as e:
                    logger.debug(f"嘗試點擊 XPath 按鈕時出錯 ({xpath}): {str(e)}")
        
        if popups_handled:
            logger.info("已自動關閉彈窗/廣告")
            return True
            
    except Exception as e:
        # 特別處理可能的 :contains 選擇器錯誤
        error_str = str(e)
        if "querySelectorAll" in error_str and ":contains" in error_str:
            logger.error(
                "偵測到不合法的 CSS selector ':contains'，"
                "請檢查 popup handler 的選擇器設定，移除所有 :contains 用法"
            )
        else:
            logger.warning(f"處理彈窗時出錯: {error_str}")
    
    return False
