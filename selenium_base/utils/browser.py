"""
瀏覽器工具模組

此模組提供了瀏覽器相關的工具函數，包含以下功能：
- 瀏覽器配置管理
- 瀏覽器操作工具
- 頁面等待工具
- 元素定位工具
"""

import time
import random
from typing import Any, Dict, List, Optional, Union
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    WebDriverException,
    NoSuchElementException,
    StaleElementReferenceException,
)

from ..core.config import BaseConfig
from ..core.exceptions import BrowserError

class BrowserProfile:
    """瀏覽器配置類別"""
    
    def __init__(self, config: BaseConfig):
        """
        初始化瀏覽器配置
        
        Args:
            config: 配置物件
        """
        self.config = config
        self.logger = config.logger
        
    def apply(self, options: Options):
        """
        應用瀏覽器配置
        
        Args:
            options: 瀏覽器選項
        """
        try:
            # 基本設定
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-infobars")
            options.add_argument("--disable-notifications")
            options.add_argument("--disable-popup-blocking")
            
            # 效能設定
            options.add_argument("--disable-software-rasterizer")
            options.add_argument("--disable-features=site-per-process")
            options.add_argument("--disable-features=IsolateOrigins")
            options.add_argument("--disable-features=NetworkService")
            
            # 隱私設定
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)
            
            # 其他設定
            prefs = {
                "profile.default_content_setting_values.notifications": 2,
                "profile.default_content_settings.popups": 0,
                "profile.managed_default_content_settings.images": 1,
                "profile.default_content_setting_values.cookies": 1,
            }
            options.add_experimental_option("prefs", prefs)
            
        except Exception as e:
            self.logger.error(f"應用瀏覽器配置失敗: {str(e)}")
            raise BrowserError(f"應用瀏覽器配置失敗: {str(e)}")
            
class BrowserUtils:
    """瀏覽器工具類別"""
    
    def __init__(self, driver: webdriver.Chrome, config: BaseConfig):
        """
        初始化瀏覽器工具
        
        Args:
            driver: 瀏覽器驅動
            config: 配置物件
        """
        self.driver = driver
        self.config = config
        self.logger = config.logger
        
    def wait_for_element(
        self,
        by: By,
        value: str,
        timeout: int = 10,
        condition: str = "presence"
    ) -> Optional[webdriver.remote.webelement.WebElement]:
        """
        等待元素出現
        
        Args:
            by: 定位方式
            value: 定位值
            timeout: 超時時間（秒）
            condition: 等待條件（presence/visibility/clickable）
            
        Returns:
            元素物件
        """
        try:
            if condition == "presence":
                element = WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((by, value))
                )
            elif condition == "visibility":
                element = WebDriverWait(self.driver, timeout).until(
                    EC.visibility_of_element_located((by, value))
                )
            elif condition == "clickable":
                element = WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable((by, value))
                )
            else:
                raise ValueError(f"不支援的等待條件: {condition}")
                
            return element
            
        except TimeoutException:
            self.logger.error(f"等待元素超時: {value}")
            raise BrowserError(f"等待元素超時: {value}")
            
    def find_elements(
        self,
        by: By,
        value: str,
        timeout: int = 10
    ) -> List[webdriver.remote.webelement.WebElement]:
        """
        尋找多個元素
        
        Args:
            by: 定位方式
            value: 定位值
            timeout: 超時時間（秒）
            
        Returns:
            元素列表
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_all_elements_located((by, value))
            )
            return self.driver.find_elements(by, value)
        except TimeoutException:
            self.logger.error(f"尋找元素超時: {value}")
            return []
            
    def scroll_to_element(self, element: webdriver.remote.webelement.WebElement):
        """
        滾動到元素位置
        
        Args:
            element: 目標元素
        """
        try:
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(random.uniform(0.5, 1.5))
        except Exception as e:
            self.logger.error(f"滾動到元素失敗: {str(e)}")
            
    def scroll_to_bottom(self):
        """滾動到頁面底部"""
        try:
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            time.sleep(random.uniform(1.0, 2.0))
        except Exception as e:
            self.logger.error(f"滾動到頁面底部失敗: {str(e)}")
            
    def simulate_human_scroll(self, scroll_times: int = 3):
        """
        模擬人類滾動行為
        
        Args:
            scroll_times: 滾動次數
        """
        try:
            for _ in range(scroll_times):
                # 隨機滾動距離
                scroll_height = random.randint(300, 700)
                self.driver.execute_script(f"window.scrollBy(0, {scroll_height});")
                # 隨機等待時間
                time.sleep(random.uniform(0.5, 1.5))
                
            # 最後滾動到底部
            self.scroll_to_bottom()
            
        except Exception as e:
            self.logger.error(f"模擬人類滾動失敗: {str(e)}")
            
    def get_page_source(self) -> str:
        """
        獲取頁面原始碼
        
        Returns:
            頁面原始碼
        """
        try:
            return self.driver.page_source
        except Exception as e:
            self.logger.error(f"獲取頁面原始碼失敗: {str(e)}")
            raise BrowserError(f"獲取頁面原始碼失敗: {str(e)}")
            
    def execute_script(self, script: str, *args) -> Any:
        """
        執行 JavaScript 腳本
        
        Args:
            script: 腳本內容
            *args: 腳本參數
            
        Returns:
            腳本執行結果
        """
        try:
            return self.driver.execute_script(script, *args)
        except Exception as e:
            self.logger.error(f"執行腳本失敗: {str(e)}")
            raise BrowserError(f"執行腳本失敗: {str(e)}")
            
    def take_screenshot(self, file_path: str):
        """
        截取頁面截圖
        
        Args:
            file_path: 截圖檔案路徑
        """
        try:
            self.driver.save_screenshot(file_path)
        except Exception as e:
            self.logger.error(f"截取頁面截圖失敗: {str(e)}")
            raise BrowserError(f"截取頁面截圖失敗: {str(e)}")
            
    def get_cookies(self) -> List[Dict[str, str]]:
        """
        獲取瀏覽器 Cookie
        
        Returns:
            Cookie 列表
        """
        try:
            return self.driver.get_cookies()
        except Exception as e:
            self.logger.error(f"獲取 Cookie 失敗: {str(e)}")
            raise BrowserError(f"獲取 Cookie 失敗: {str(e)}")
            
    def add_cookies(self, cookies: List[Dict[str, str]]):
        """
        添加 Cookie
        
        Args:
            cookies: Cookie 列表
        """
        try:
            for cookie in cookies:
                self.driver.add_cookie(cookie)
        except Exception as e:
            self.logger.error(f"添加 Cookie 失敗: {str(e)}")
            raise BrowserError(f"添加 Cookie 失敗: {str(e)}")
            
    def clear_cookies(self):
        """清除所有 Cookie"""
        try:
            self.driver.delete_all_cookies()
        except Exception as e:
            self.logger.error(f"清除 Cookie 失敗: {str(e)}")
            raise BrowserError(f"清除 Cookie 失敗: {str(e)}")
            
    def switch_to_frame(self, frame_reference: Union[str, int, webdriver.remote.webelement.WebElement]):
        """
        切換到指定框架
        
        Args:
            frame_reference: 框架參考（ID/索引/元素）
        """
        try:
            self.driver.switch_to.frame(frame_reference)
        except Exception as e:
            self.logger.error(f"切換框架失敗: {str(e)}")
            raise BrowserError(f"切換框架失敗: {str(e)}")
            
    def switch_to_default_content(self):
        """切換回預設內容"""
        try:
            self.driver.switch_to.default_content()
        except Exception as e:
            self.logger.error(f"切換回預設內容失敗: {str(e)}")
            raise BrowserError(f"切換回預設內容失敗: {str(e)}")
            
    def accept_alert(self):
        """接受警告框"""
        try:
            alert = self.driver.switch_to.alert
            alert.accept()
        except Exception as e:
            self.logger.error(f"接受警告框失敗: {str(e)}")
            raise BrowserError(f"接受警告框失敗: {str(e)}")
            
    def dismiss_alert(self):
        """取消警告框"""
        try:
            alert = self.driver.switch_to.alert
            alert.dismiss()
        except Exception as e:
            self.logger.error(f"取消警告框失敗: {str(e)}")
            raise BrowserError(f"取消警告框失敗: {str(e)}")
            
    def get_alert_text(self) -> str:
        """
        獲取警告框文字
        
        Returns:
            警告框文字
        """
        try:
            alert = self.driver.switch_to.alert
            return alert.text
        except Exception as e:
            self.logger.error(f"獲取警告框文字失敗: {str(e)}")
            raise BrowserError(f"獲取警告框文字失敗: {str(e)}")
            
    def send_keys_to_alert(self, text: str):
        """
        向警告框發送文字
        
        Args:
            text: 要發送的文字
        """
        try:
            alert = self.driver.switch_to.alert
            alert.send_keys(text)
        except Exception as e:
            self.logger.error(f"向警告框發送文字失敗: {str(e)}")
            raise BrowserError(f"向警告框發送文字失敗: {str(e)}")
            
    def get_window_handles(self) -> List[str]:
        """
        獲取所有視窗句柄
        
        Returns:
            視窗句柄列表
        """
        try:
            return self.driver.window_handles
        except Exception as e:
            self.logger.error(f"獲取視窗句柄失敗: {str(e)}")
            raise BrowserError(f"獲取視窗句柄失敗: {str(e)}")
            
    def switch_to_window(self, handle: str):
        """
        切換到指定視窗
        
        Args:
            handle: 視窗句柄
        """
        try:
            self.driver.switch_to.window(handle)
        except Exception as e:
            self.logger.error(f"切換視窗失敗: {str(e)}")
            raise BrowserError(f"切換視窗失敗: {str(e)}")
            
    def close_window(self):
        """關閉當前視窗"""
        try:
            self.driver.close()
        except Exception as e:
            self.logger.error(f"關閉視窗失敗: {str(e)}")
            raise BrowserError(f"關閉視窗失敗: {str(e)}")
            
    def maximize_window(self):
        """最大化視窗"""
        try:
            self.driver.maximize_window()
        except Exception as e:
            self.logger.error(f"最大化視窗失敗: {str(e)}")
            raise BrowserError(f"最大化視窗失敗: {str(e)}")
            
    def minimize_window(self):
        """最小化視窗"""
        try:
            self.driver.minimize_window()
        except Exception as e:
            self.logger.error(f"最小化視窗失敗: {str(e)}")
            raise BrowserError(f"最小化視窗失敗: {str(e)}")
            
    def set_window_size(self, width: int, height: int):
        """
        設置視窗大小
        
        Args:
            width: 視窗寬度
            height: 視窗高度
        """
        try:
            self.driver.set_window_size(width, height)
        except Exception as e:
            self.logger.error(f"設置視窗大小失敗: {str(e)}")
            raise BrowserError(f"設置視窗大小失敗: {str(e)}")
            
    def get_window_size(self) -> Dict[str, int]:
        """
        獲取視窗大小
        
        Returns:
            視窗大小
        """
        try:
            size = self.driver.get_window_size()
            return {"width": size["width"], "height": size["height"]}
        except Exception as e:
            self.logger.error(f"獲取視窗大小失敗: {str(e)}")
            raise BrowserError(f"獲取視窗大小失敗: {str(e)}")
            
    def get_window_position(self) -> Dict[str, int]:
        """
        獲取視窗位置
        
        Returns:
            視窗位置
        """
        try:
            position = self.driver.get_window_position()
            return {"x": position["x"], "y": position["y"]}
        except Exception as e:
            self.logger.error(f"獲取視窗位置失敗: {str(e)}")
            raise BrowserError(f"獲取視窗位置失敗: {str(e)}")
            
    def set_window_position(self, x: int, y: int):
        """
        設置視窗位置
        
        Args:
            x: X 座標
            y: Y 座標
        """
        try:
            self.driver.set_window_position(x, y)
        except Exception as e:
            self.logger.error(f"設置視窗位置失敗: {str(e)}")
            raise BrowserError(f"設置視窗位置失敗: {str(e)}")
            
    def get_current_url(self) -> str:
        """
        獲取當前 URL
        
        Returns:
            當前 URL
        """
        try:
            return self.driver.current_url
        except Exception as e:
            self.logger.error(f"獲取當前 URL 失敗: {str(e)}")
            raise BrowserError(f"獲取當前 URL 失敗: {str(e)}")
            
    def get_title(self) -> str:
        """
        獲取頁面標題
        
        Returns:
            頁面標題
        """
        try:
            return self.driver.title
        except Exception as e:
            self.logger.error(f"獲取頁面標題失敗: {str(e)}")
            raise BrowserError(f"獲取頁面標題失敗: {str(e)}")
            
    def refresh(self):
        """重新整理頁面"""
        try:
            self.driver.refresh()
        except Exception as e:
            self.logger.error(f"重新整理頁面失敗: {str(e)}")
            raise BrowserError(f"重新整理頁面失敗: {str(e)}")
            
    def back(self):
        """返回上一頁"""
        try:
            self.driver.back()
        except Exception as e:
            self.logger.error(f"返回上一頁失敗: {str(e)}")
            raise BrowserError(f"返回上一頁失敗: {str(e)}")
            
    def forward(self):
        """前進下一頁"""
        try:
            self.driver.forward()
        except Exception as e:
            self.logger.error(f"前進下一頁失敗: {str(e)}")
            raise BrowserError(f"前進下一頁失敗: {str(e)}")
            
    def quit(self):
        """關閉瀏覽器"""
        try:
            self.driver.quit()
        except Exception as e:
            self.logger.error(f"關閉瀏覽器失敗: {str(e)}")
            raise BrowserError(f"關閉瀏覽器失敗: {str(e)}")
            
    def __enter__(self):
        """上下文管理器進入"""
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.quit() 