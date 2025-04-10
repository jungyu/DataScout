"""
瀏覽器工具模組
提供通用的瀏覽器操作功能，包括截圖、Cookie管理、頁面源碼保存等
"""

import os
import re
import json
import time
import urllib.parse
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains

class BrowserUtils:
    """瀏覽器工具類"""
    
    def __init__(self, driver: webdriver.Chrome, config: Dict, logger=None):
        """
        初始化瀏覽器工具
        
        Args:
            driver: WebDriver 實例
            config: 配置字典
            logger: 日誌記錄器
        """
        self.driver = driver
        self.config = config
        self.logger = logger or print
        
    def clean_text(self, text: str) -> str:
        """清理多餘空白字元"""
        if not text:
            return ""
        # 移除多餘空格、換行和 tabs
        text = re.sub(r'\s+', ' ', text)
        # 移除前後空格
        return text.strip()
        
    def format_for_json(self, obj: Any) -> Any:
        """格式化數據以便 JSON 序列化"""
        if isinstance(obj, dict):
            return {k: self.format_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self.format_for_json(item) for item in obj]
        elif isinstance(obj, datetime):
            return obj.isoformat()
        else:
            return obj
            
    def normalize_url(self, url: str, base_domain: str) -> str:
        """標準化URL，處理相對路徑"""
        if not url:
            return ""
            
        if url.startswith("//"):
            return f"https:{url}"
        elif url.startswith("/"):
            return f"{base_domain}{url}"
        elif not url.startswith(("http://", "https://")):
            return f"{base_domain}/{url}"
        else:
            return url
            
    def encode_url_parameter(self, param: str) -> str:
        """對URL參數進行編碼，保留特殊字符"""
        return urllib.parse.quote(param)
        
    def take_screenshot(self, page_type: str) -> Optional[str]:
        """拍攝螢幕截圖"""
        try:
            screenshot_config = self.config.get("advanced_settings", {}).get("screenshot", {})
            if not screenshot_config.get("enabled", False):
                return None
                
            directory = screenshot_config.get("directory", "screenshots")
            os.makedirs(directory, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename_pattern = screenshot_config.get("filename_pattern", "{timestamp}_{page_type}.png")
            filename = filename_pattern.replace("{timestamp}", timestamp).replace("{page_type}", page_type)
            
            filepath = os.path.join(directory, filename)
            self.driver.save_screenshot(filepath)
            self.logger(f"螢幕截圖已保存: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger(f"拍攝螢幕截圖時發生錯誤: {str(e)}")
            return None
            
    def save_page_source(self, page_type: str) -> Optional[str]:
        """保存頁面源碼"""
        try:
            # 確保目錄存在
            output_dir = "debug"
            os.makedirs(output_dir, exist_ok=True)
            
            # 生成檔案名稱
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{page_type}.html"
            filepath = os.path.join(output_dir, filename)
            
            # 保存頁面源碼
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
                
            self.logger(f"頁面源碼已保存: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger(f"保存頁面源碼時發生錯誤: {str(e)}")
            return None
            
    def wait_for_element(self, by: str, selector: str, timeout: int = 10) -> Optional[Any]:
        """等待元素出現並返回"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            return wait.until(EC.presence_of_element_located((by, selector)))
        except TimeoutException:
            self.logger(f"等待元素超時: {selector}")
            return None
            
    def wait_for_elements(self, by: str, selector: str, timeout: int = 10) -> List[Any]:
        """等待多個元素出現並返回"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            return wait.until(EC.presence_of_all_elements_located((by, selector)))
        except TimeoutException:
            self.logger(f"等待元素超時: {selector}")
            return []
            
    def safe_click(self, element: Any, retries: int = 3) -> bool:
        """安全點擊元素，處理各種點擊異常"""
        for i in range(retries):
            try:
                # 先嘗試滾動到元素位置
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                time.sleep(0.5)
                
                # 等待元素可點擊
                WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable(element))
                
                # 點擊元素
                element.click()
                return True
                    
            except ElementClickInterceptedException:
                self.logger(f"點擊被攔截，嘗試JavaScript點擊 (嘗試 {i+1}/{retries})")
                try:
                    self.driver.execute_script("arguments[0].click();", element)
                    return True
                except Exception as js_e:
                    self.logger(f"JavaScript點擊失敗: {str(js_e)}")
                    
            except Exception as e:
                self.logger(f"點擊失敗: {str(e)} (嘗試 {i+1}/{retries})")
                time.sleep(1.0)
        
        self.logger("所有點擊嘗試均失敗")
        return False
        
    def scroll_page(self, direction: str = "down", amount: int = 500) -> None:
        """滾動頁面"""
        try:
            if direction == "down":
                self.driver.execute_script(f"window.scrollBy(0, {amount});")
            elif direction == "up":
                self.driver.execute_script(f"window.scrollBy(0, -{amount});")
            elif direction == "top":
                self.driver.execute_script("window.scrollTo(0, 0);")
            elif direction == "bottom":
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                
            # 等待頁面加載
            time.sleep(1.0)
            
        except Exception as e:
            self.logger(f"滾動頁面時發生錯誤: {str(e)}")
            
    def simulate_human_behavior(self) -> None:
        """模擬人類瀏覽行為"""
        try:
            # 隨機滾動
            for _ in range(3):
                scroll_amount = random.randint(300, 800)
                self.driver.execute_script(f"window.scrollBy(0, {scroll_amount})")
                time.sleep(random.uniform(1.0, 2.5))
                
                # 隨機移動滑鼠
                action = ActionChains(self.driver)
                action.move_by_offset(random.randint(-100, 100), random.randint(-50, 50))
                action.perform()
                time.sleep(random.uniform(0.5, 1.5))
                
        except Exception as e:
            self.logger(f"模擬人類行為時發生錯誤: {str(e)}")
            
    def set_local_storage(self, key: str, value: Any) -> bool:
        """設置localStorage"""
        try:
            script = f"""
            try {{
                localStorage.setItem('{key}', JSON.stringify({json.dumps(value)}));
                return true;
            }} catch (e) {{
                console.error('設置localStorage失敗:', e);
                return false;
            }}
            """
            
            result = self.driver.execute_script(script)
            if result:
                self.logger(f"已成功設置localStorage: {key}")
                return True
            else:
                self.logger("設置localStorage失敗")
                return False
                
        except Exception as e:
            self.logger(f"設置localStorage時發生錯誤: {str(e)}")
            return False
            
    def get_local_storage(self, key: str) -> Optional[Any]:
        """獲取localStorage"""
        try:
            script = f"""
            try {{
                const value = localStorage.getItem('{key}');
                return value ? JSON.parse(value) : null;
            }} catch (e) {{
                console.error('獲取localStorage失敗:', e);
                return null;
            }}
            """
            
            return self.driver.execute_script(script)
            
        except Exception as e:
            self.logger(f"獲取localStorage時發生錯誤: {str(e)}")
            return None 