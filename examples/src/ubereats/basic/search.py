"""
UberEats 爬蟲程式
基於配置文件的 UberEats 網站資料爬取工具
支持地址搜尋、餐廳搜尋和餐點選擇
"""

import os
import re
import json
import time
import urllib.parse
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Union

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains
from lxml import html


# ===== 工具函數區 =====

def clean_text(text: str) -> str:
    """清理多餘空白字元"""
    if not text:
        return ""
    # 移除多餘空格、換行和 tabs
    text = re.sub(r'\s+', ' ', text)
    # 移除前後空格
    return text.strip()


def format_for_json(obj: Any) -> Any:
    """格式化數據以便 JSON 序列化"""
    if isinstance(obj, dict):
        return {k: format_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [format_for_json(item) for item in obj]
    elif isinstance(obj, datetime):
        return obj.isoformat()
    else:
        return obj


def normalize_url(url: str, base_domain: str = "https://www.ubereats.com") -> str:
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


def encode_url_parameter(param: str) -> str:
    """對URL參數進行編碼，保留特殊字符"""
    return urllib.parse.quote(param)


# ===== 配置處理區 =====

def load_config(config_path: str) -> Dict:
    """載入配置檔案"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print(f"已載入配置檔案: {config_path}")
        return config
    except Exception as e:
        print(f"載入配置檔案失敗: {str(e)}")
        raise


# ===== 瀏覽器控制區 =====

def setup_webdriver(config: Dict) -> webdriver.Chrome:
    """設置並初始化 WebDriver"""
    print("正在設置 Chrome WebDriver...")
    chrome_options = webdriver.ChromeOptions()
    
    # 從配置文件獲取 User-Agent
    user_agent = config.get("request", {}).get("headers", {}).get("User-Agent")
    if user_agent:
        chrome_options.add_argument(f'user-agent={user_agent}')
    
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    # 調試模式：不自動關閉瀏覽器
    chrome_options.add_experimental_option("detach", True)
    
    print("初始化 Chrome WebDriver...")
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    
    # 設置隱式等待時間
    driver.implicitly_wait(10)
    
    return driver


def wait_for_element(driver: webdriver.Chrome, by: str, selector: str, timeout: int = 10) -> Any:
    """等待元素出現並返回"""
    wait = WebDriverWait(driver, timeout)
    return wait.until(EC.presence_of_element_located((by, selector)))


def safe_click(driver: webdriver.Chrome, element, retries: int = 3) -> bool:
    """安全點擊元素，處理可能的點擊攔截"""
    for attempt in range(retries):
        try:
            element.click()
            return True
        except ElementClickInterceptedException:
            print(f"點擊被攔截，嘗試使用 JavaScript 點擊 (嘗試 {attempt+1}/{retries})")
            try:
                driver.execute_script("arguments[0].click();", element)
                return True
            except Exception as e:
                print(f"JavaScript 點擊失敗: {str(e)}")
                time.sleep(1)
        except Exception as e:
            print(f"點擊失敗: {str(e)}")
            time.sleep(1)
    
    return False


# ===== 搜尋參數設置區 =====

def set_search_parameters(driver: webdriver.Chrome, config: Dict) -> bool:
    """設置搜尋參數"""
    try:
        search_params = config.get("search_parameters", {})
        
        # 設置送餐地址
        if not set_address(driver, search_params):
            print("設置送餐地址失敗")
            return False
        
        # 設置搜尋關鍵字
        if not set_search_keyword(driver, search_params):
            print("設置搜尋關鍵字失敗")
            return False
        
        return True
        
    except Exception as e:
        print(f"設置搜尋參數時發生錯誤: {str(e)}")
        return False


def set_address(driver: webdriver.Chrome, search_params: Dict) -> bool:
    """設置送餐地址"""
    try:
        address_config = search_params.get("address", {})
        input_selector = address_config.get("input_selector")
        submit_selector = address_config.get("submit_selector")
        default_address = address_config.get("default")
        
        if not all([input_selector, submit_selector, default_address]):
            print("地址配置不完整")
            return False
            
        # 等待地址輸入框出現
        address_input = wait_for_element(driver, By.XPATH, input_selector)
        if not address_input:
            print("找不到地址輸入框")
            return False
            
        # 清除並輸入地址
        address_input.clear()
        address_input.send_keys(default_address)
        
        # 點擊提交按鈕
        submit_button = wait_for_element(driver, By.XPATH, submit_selector)
        if not submit_button:
            print("找不到提交按鈕")
            return False
            
        if not safe_click(driver, submit_button):
            print("點擊提交按鈕失敗")
            return False
            
        # 等待頁面加載
        time.sleep(address_config.get("wait_after_submit", 5))
        
        return True
        
    except Exception as e:
        print(f"設置地址時發生錯誤: {str(e)}")
        return False


def set_search_keyword(driver: webdriver.Chrome, search_params: Dict) -> bool:
    """設置搜尋關鍵字"""
    try:
        want_config = search_params.get("want", {})
        input_selector = want_config.get("input_selector")
        submit_selector = want_config.get("submit_selector")
        default_keyword = want_config.get("default")
        
        if not all([input_selector, submit_selector, default_keyword]):
            print("搜尋關鍵字配置不完整")
            return False
            
        # 等待搜尋輸入框出現
        search_input = wait_for_element(driver, By.XPATH, input_selector)
        if not search_input:
            print("找不到搜尋輸入框")
            return False
            
        # 清除並輸入關鍵字
        search_input.clear()
        search_input.send_keys(default_keyword)
        
        # 點擊搜尋按鈕
        submit_button = wait_for_element(driver, By.XPATH, submit_selector)
        if not submit_button:
            print("找不到搜尋按鈕")
            return False
            
        if not safe_click(driver, submit_button):
            print("點擊搜尋按鈕失敗")
            return False
            
        # 等待頁面加載
        time.sleep(want_config.get("wait_after_submit", 5))
        
        return True
        
    except Exception as e:
        print(f"設置搜尋關鍵字時發生錯誤: {str(e)}")
        return False


# ===== 資料提取區 =====

def extract_list_items(page_source: str, config: Dict) -> List[Dict]:
    """從列表頁面提取餐廳資訊"""
    try:
        list_config = config.get("list_page", {})
        container_xpath = list_config.get("container_xpath")
        item_xpath = list_config.get("item_xpath")
        fields_config = list_config.get("fields", {})
        
        if not all([container_xpath, item_xpath, fields_config]):
            print("列表頁配置不完整")
            return []
            
        # 解析 HTML
        tree = html.fromstring(page_source)
        
        # 找到容器
        container = tree.xpath(container_xpath)
        if not container:
            print("找不到列表容器")
            return []
            
        # 提取所有餐廳項目
        items = container[0].xpath(item_xpath)
        results = []
        
        for item in items:
            item_data = {}
            for field_name, field_config in fields_config.items():
                xpath = field_config.get("xpath")
                field_type = field_config.get("type", "text")
                
                if not xpath:
                    continue
                    
                try:
                    if field_type == "text":
                        value = item.xpath(xpath)
                        value = value[0] if value else ""
                    elif field_type == "attribute":
                        value = item.xpath(xpath)
                        value = value[0] if value else ""
                    elif field_type == "list":
                        value = item.xpath(xpath)
                    else:
                        value = ""
                        
                    item_data[field_name] = clean_text(value) if isinstance(value, str) else value
                    
                except Exception as e:
                    print(f"提取欄位 {field_name} 時發生錯誤: {str(e)}")
                    item_data[field_name] = ""
                    
            results.append(item_data)
            
        return results
        
    except Exception as e:
        print(f"提取列表項目時發生錯誤: {str(e)}")
        return []


def extract_detail_page(driver: webdriver.Chrome, url: str, config: Dict) -> Dict[str, Any]:
    """提取餐廳詳情頁面資訊"""
    try:
        detail_config = config.get("detail_page", {})
        container_xpath = detail_config.get("container_xpath")
        fields_config = detail_config.get("fields", {})
        
        if not all([container_xpath, fields_config]):
            print("詳情頁配置不完整")
            return {}
            
        # 訪問詳情頁
        driver.get(url)
        time.sleep(config.get("delays", {}).get("page_load", 5))
        
        # 等待容器出現
        container = wait_for_element(driver, By.XPATH, container_xpath)
        if not container:
            print("找不到詳情頁容器")
            return {}
            
        # 提取資訊
        result = {}
        for field_name, field_config in fields_config.items():
            xpath = field_config.get("xpath")
            field_type = field_config.get("type", "text")
            
            if not xpath:
                continue
                
            try:
                element = driver.find_element(By.XPATH, xpath)
                if field_type == "text":
                    value = element.text
                elif field_type == "attribute":
                    value = element.get_attribute("href")
                elif field_type == "list":
                    elements = driver.find_elements(By.XPATH, xpath)
                    value = [el.text for el in elements]
                else:
                    value = ""
                    
                result[field_name] = clean_text(value) if isinstance(value, str) else value
                
            except Exception as e:
                print(f"提取欄位 {field_name} 時發生錯誤: {str(e)}")
                result[field_name] = ""
                
        return result
        
    except Exception as e:
        print(f"提取詳情頁時發生錯誤: {str(e)}")
        return {}


# ===== 主程式區 =====

def main() -> None:
    """主程式"""
    try:
        # 載入配置
        config_path = "examples/config/ubereats/basic/search.json"
        config = load_config(config_path)
        
        # 設置 WebDriver
        driver = setup_webdriver(config)
        
        try:
            # 訪問首頁
            driver.get(config.get("base_url"))
            time.sleep(config.get("delays", {}).get("page_load", 5))
            
            # 設置搜尋參數
            if not set_search_parameters(driver, config):
                print("設置搜尋參數失敗")
                return
                
            # 提取列表頁資訊
            list_items = extract_list_items(driver.page_source, config)
            print(f"找到 {len(list_items)} 個餐廳")
            
            # 提取詳情頁資訊
            results = []
            for item in list_items:
                detail_url = normalize_url(item.get("detail_link", ""), config.get("base_url"))
                if detail_url:
                    detail_data = extract_detail_page(driver, detail_url, config)
                    results.append({**item, "detail": detail_data})
                    
            # 保存結果
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = "examples/data/ubereats"
            os.makedirs(output_dir, exist_ok=True)
            
            output_file = os.path.join(output_dir, f"ubereats_search_{timestamp}.json")
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(format_for_json(results), f, ensure_ascii=False, indent=2)
                
            print(f"結果已保存至: {output_file}")
            
        finally:
            # 關閉瀏覽器
            driver.quit()
            
    except Exception as e:
        print(f"程式執行時發生錯誤: {str(e)}")


if __name__ == "__main__":
    main() 