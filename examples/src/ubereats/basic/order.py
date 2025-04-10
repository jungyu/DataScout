"""
UberEats爬蟲程式
基於配置文件的UberEats網站資料爬取工具
支援地址搜尋、餐廳/餐點篩選、分類瀏覽等功能
"""
import os
import re
import json
import time
import traceback
import urllib.parse
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Union

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains  # 添加這行
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, 
    ElementClickInterceptedException, StaleElementReferenceException
)
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
    
    print("初始化 Chrome WebDriver...")
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    return driver


def wait_for_element(driver: webdriver.Chrome, by: str, selector: str, timeout: int = 10) -> Any:
    """等待元素出現並返回"""
    wait = WebDriverWait(driver, timeout)
    return wait.until(EC.presence_of_element_located((by, selector)))


def safe_click(driver: webdriver.Chrome, element, retries: int = 3) -> bool:
    """安全點擊元素，處理各種點擊異常"""
    for i in range(retries):
        try:
            if isinstance(element, str):
                element = wait_for_element(driver, By.XPATH, element)
            
            # 先嘗試滾動到元素位置
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
            time.sleep(0.5)
            
            # 等待元素可點擊
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, element if isinstance(element, str) else element.get_attribute("xpath"))))
            
            # 點擊元素
            element.click()
            return True
                
        except ElementClickInterceptedException:
            print(f"點擊被攔截，嘗試JavaScript點擊 (嘗試 {i+1}/{retries})")
            try:
                driver.execute_script("arguments[0].click();", element)
                return True
            except Exception as js_e:
                print(f"JavaScript點擊失敗: {str(js_e)}")
                
        except StaleElementReferenceException:
            print(f"元素已過時，重新獲取 (嘗試 {i+1}/{retries})")
            time.sleep(1)
            continue
                
        except Exception as e:
            print(f"點擊失敗: {str(e)} (嘗試 {i+1}/{retries})")
            time.sleep(1)
    
    print("所有點擊嘗試均失敗")
    return False


def scroll_page(driver: webdriver.Chrome, direction: str = "down", amount: int = 500) -> None:
    """滾動頁面"""
    if direction == "down":
        driver.execute_script(f"window.scrollBy(0, {amount});")
    elif direction == "up":
        driver.execute_script(f"window.scrollBy(0, -{amount});")
    elif direction == "top":
        driver.execute_script("window.scrollTo(0, 0);")
    elif direction == "bottom":
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")


def take_screenshot(driver: webdriver.Chrome, config: Dict, page_type: str) -> Optional[str]:
    """截取螢幕截圖"""
    screenshot_config = config.get("advanced_settings", {}).get("screenshot", {})
    if not screenshot_config.get("enabled", False):
        return None
        
    directory = screenshot_config.get("directory", "../screenshots")
    os.makedirs(directory, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename_pattern = screenshot_config.get("filename_pattern", "screenshot_{timestamp}_{page_type}.png")
    filename = filename_pattern.format(timestamp=timestamp, page_type=page_type)
    
    file_path = os.path.join(directory, filename)
    driver.save_screenshot(file_path)
    print(f"已儲存螢幕截圖: {file_path}")
    
    return file_path


# ===== 搜尋參數處理區 =====

def build_initial_url(config: Dict) -> str:
    """構建初始搜尋URL"""
    url_format = config.get("advanced_settings", {}).get("url_format", {})
    if not url_format:
        return config.get("base_url", "https://www.ubereats.com")
    
    pattern = url_format.get("pattern")
    if not pattern:
        return config.get("base_url", "https://www.ubereats.com")
    
    # 獲取地址和搜尋關鍵字
    base_url = config.get("base_url", "https://www.ubereats.com")
    address = config.get("search_parameters", {}).get("address", {}).get("default", "")
    search = config.get("search_parameters", {}).get("want", {}).get("default", "")
    
    # 如果需要編碼參數
    if url_format.get("encode_parameters", False):
        encoded_address = encode_url_parameter(address)
        encoded_search = encode_url_parameter(search)
    else:
        encoded_address = address
        encoded_search = search
    
    # 構建URL
    url = pattern.format(
        base_url=base_url,
        encoded_address=encoded_address,
        encoded_search=encoded_search
    )
    
    return url


def set_address(driver: webdriver.Chrome, config: Dict) -> bool:
    """設置送餐地址"""
    try:
        address_config = config.get("search_parameters", {}).get("address", {})
        address_value = address_config.get("default", "")
        
        print(f"設置送餐地址: {address_value}")
        
        # 輸入地址
        input_selector = address_config.get("input_selector")
        if input_selector:
            address_input = wait_for_element(driver, By.XPATH, input_selector)
            address_input.clear()
            address_input.send_keys(address_value)
            time.sleep(1)
        
        # 提交地址
        submit_selector = address_config.get("submit_selector")
        if submit_selector:
            submit_button = wait_for_element(driver, By.XPATH, submit_selector)
            safe_click(driver, submit_button)
            
            # 等待頁面加載
            wait_time = address_config.get("wait_after_submit", 5)
            time.sleep(wait_time)
        
        return True
        
    except Exception as e:
        print(f"設置送餐地址時發生錯誤: {str(e)}")
        traceback.print_exc()
        return False


def search_keyword(driver: webdriver.Chrome, config: Dict) -> bool:
    """搜尋關鍵字"""
    try:
        search_config = config.get("search_parameters", {}).get("want", {})
        search_value = search_config.get("default", "")
        
        print(f"搜尋關鍵字: {search_value}")
        
        # 輸入搜尋關鍵字
        input_selector = search_config.get("input_selector")
        if input_selector:
            try:
                search_input = wait_for_element(driver, By.XPATH, input_selector)
                search_input.clear()
                search_input.send_keys(search_value)
                time.sleep(1)
            except Exception as input_e:
                print(f"輸入搜尋關鍵字時發生錯誤: {str(input_e)}")
                return False
        
        # 提交搜尋
        submit_selector = search_config.get("submit_selector")
        if submit_selector:
            try:
                submit_button = wait_for_element(driver, By.XPATH, submit_selector)
                safe_click(driver, submit_button)
                
                # 等待頁面加載
                wait_time = search_config.get("wait_after_submit", 5)
                time.sleep(wait_time)
            except Exception as submit_e:
                print(f"提交搜尋時發生錯誤: {str(submit_e)}")
                return False
        
        return True
        
    except Exception as e:
        print(f"搜尋關鍵字時發生錯誤: {str(e)}")
        traceback.print_exc()
        return False


def select_restaurant(driver: webdriver.Chrome, config: Dict) -> bool:
    """選擇餐廳"""
    try:
        restaurant_config = config.get("search_parameters", {}).get("wantStore", {})
        restaurant_value = restaurant_config.get("default", "")
        
        print(f"選擇餐廳: {restaurant_value}")
        
        # 滾動頁面以確保所有餐廳都已載入
        scroll_behavior = config.get("advanced_settings", {}).get("scroll_behavior", {})
        if scroll_behavior.get("enable_lazy_loading", True):
            for _ in range(scroll_behavior.get("max_scroll_attempts", 5)):
                scroll_page(driver, "bottom")
                time.sleep(scroll_behavior.get("scroll_pause", 1.5))
        
        # 選擇特定餐廳
        selector = restaurant_config.get("selector").replace("{value}", restaurant_value)
        try:
            restaurant_element = wait_for_element(driver, By.XPATH, selector)
            safe_click(driver, restaurant_element)
            
            # 等待頁面加載
            wait_time = restaurant_config.get("wait_after_click", 5)
            time.sleep(wait_time)
            
            # 截圖
            take_screenshot(driver, config, "restaurant_selected")
            
            return True
            
        except TimeoutException:
            print(f"找不到餐廳: {restaurant_value}")
            # 嘗試截圖以便調試
            take_screenshot(driver, config, "restaurant_not_found")
            return False
        
    except Exception as e:
        print(f"選擇餐廳時發生錯誤: {str(e)}")
        traceback.print_exc()
        return False


def select_category(driver: webdriver.Chrome, config: Dict) -> bool:
    """選擇菜單類別"""
    try:
        category_config = config.get("search_parameters", {}).get("wantCategory", {})
        category_value = category_config.get("default", "")
        
        if not category_value:
            print("未指定菜單類別，跳過選擇")
            return True
            
        print(f"選擇菜單類別: {category_value}")
        
        # 選擇特定菜單類別
        selector = category_config.get("selector").replace("{value}", category_value)
        try:
            category_element = wait_for_element(driver, By.XPATH, selector)
            safe_click(driver, category_element)
            
            # 等待頁面加載
            wait_time = category_config.get("wait_after_click", 3)
            time.sleep(wait_time)
            
            return True
            
        except TimeoutException:
            print(f"找不到菜單類別: {category_value}")
            return False
        
    except Exception as e:
        print(f"選擇菜單類別時發生錯誤: {str(e)}")
        traceback.print_exc()
        return False


def select_menu_item(driver: webdriver.Chrome, config: Dict) -> bool:
    """選擇餐點"""
    try:
        item_config = config.get("search_parameters", {}).get("wantItem", {})
        item_value = item_config.get("default", "")
        
        if not item_value:
            print("未指定餐點，跳過選擇")
            return True
            
        print(f"選擇餐點: {item_value}")
        
        # 滾動頁面以確保所有餐點都已載入
        scroll_behavior = config.get("advanced_settings", {}).get("scroll_behavior", {})
        if scroll_behavior.get("enable_lazy_loading", True):
            for _ in range(scroll_behavior.get("max_scroll_attempts", 5)):
                scroll_page(driver, "down", 300)
                time.sleep(scroll_behavior.get("scroll_pause", 1.5))
        
        # 選擇特定餐點
        selector = item_config.get("selector").replace("{value}", item_value)
        try:
            item_element = wait_for_element(driver, By.XPATH, selector)
            safe_click(driver, item_element)
            
            # 等待頁面加載
            wait_time = item_config.get("wait_after_click", 3)
            time.sleep(wait_time)
            
            # 截圖
            take_screenshot(driver, config, "item_selected")
            
            return True
            
        except TimeoutException:
            print(f"找不到餐點: {item_value}")
            # 嘗試截圖以便調試
            take_screenshot(driver, config, "item_not_found")
            return False
        
    except Exception as e:
        print(f"選擇餐點時發生錯誤: {str(e)}")
        traceback.print_exc()
        return False


def select_item_option(driver: webdriver.Chrome, config: Dict) -> bool:
    """選擇餐點選項"""
    try:
        option_config = config.get("search_parameters", {}).get("wantOption", {})
        option_value = option_config.get("default", "")
        
        if not option_value:
            print("未指定餐點選項，跳過選擇")
            return True
            
        print(f"選擇餐點選項: {option_value}")
        
        # 選擇特定餐點選項
        selector = option_config.get("selector").replace("{value}", option_value)
        try:
            option_element = wait_for_element(driver, By.XPATH, selector)
            safe_click(driver, option_element)
            
            # 等待選擇生效
            wait_time = option_config.get("wait_after_click", 1)
            time.sleep(wait_time)
            
            return True
            
        except TimeoutException:
            print(f"找不到餐點選項: {option_value}")
            return False
        
    except Exception as e:
        print(f"選擇餐點選項時發生錯誤: {str(e)}")
        traceback.print_exc()
        return False


def add_to_cart(driver: webdriver.Chrome, config: Dict) -> bool:
    """加入購物車"""
    try:
        add_to_cart_config = config.get("search_parameters", {}).get("addToCart", {})
        
        print("加入購物車")
        
        # 點擊加入購物車按鈕
        selector = add_to_cart_config.get("selector")
        if selector:
            try:
                add_to_cart_button = wait_for_element(driver, By.XPATH, selector)
                safe_click(driver, add_to_cart_button)
                
                # 等待操作完成
                wait_time = add_to_cart_config.get("wait_after_click", 2)
                time.sleep(wait_time)
                
                # 截圖
                take_screenshot(driver, config, "added_to_cart")
                
                return True
                
            except TimeoutException:
                print("找不到加入購物車按鈕")
                return False
        
        return True
        
    except Exception as e:
        print(f"加入購物車時發生錯誤: {str(e)}")
        traceback.print_exc()
        return False


# ===== 列表頁面處理區 =====

def extract_restaurant_list(driver: webdriver.Chrome, config: Dict) -> List[Dict]:
    """從餐廳列表頁面提取餐廳數據"""
    print("提取餐廳列表數據...")
    
    # 確保頁面已完全加載
    scroll_behavior = config.get("advanced_settings", {}).get("scroll_behavior", {})
    if scroll_behavior.get("enable_lazy_loading", True):
        for _ in range(scroll_behavior.get("max_scroll_attempts", 5)):
            scroll_page(driver, "down", 500)
            time.sleep(scroll_behavior.get("scroll_pause", 1.5))
    
    # 獲取頁面源碼
    page_source = driver.page_source
    
    # 提取餐廳列表數據
    return extract_list_items(page_source, config)


def extract_list_items(page_source: str, config: Dict) -> List[Dict]:
    """從頁面源碼提取列表項目"""
    print("解析列表頁面...")
    tree = html.fromstring(page_source)
    
    # 從配置獲取項目 XPath
    item_xpath = config.get("list_page", {}).get("item_xpath")
    
    # 定位列表項目
    list_items = tree.xpath(item_xpath)
    print(f"找到 {len(list_items)} 個列表項目")
    
    # 獲取字段配置
    fields_config = config.get("list_page", {}).get("fields", {})
    
    results = []
    
    for i, item in enumerate(list_items):
        try:
            result = {}
            
            # 提取每個字段
            for field_name, field_config in fields_config.items():
                field_xpath = field_config.get("xpath")
                field_type = field_config.get("type", "text")
                
                try:
                    if field_type == "text":
                        value = item.xpath(field_xpath)
                        if (value):
                            result[field_name] = clean_text(value[0])
                        else:
                            # 嘗試使用備用XPath
                            fallback_xpath = field_config.get("fallback_xpath")
                            if fallback_xpath:
                                fallback_value = item.xpath(fallback_xpath)
                                result[field_name] = clean_text(fallback_value[0]) if fallback_value else ""
                            else:
                                result[field_name] = ""
                    elif field_type == "attribute":
                        value = item.xpath(field_xpath)
                        result[field_name] = value[0] if value else ""
                    elif field_type == "html":
                        elements = item.xpath(field_xpath)
                        if elements:
                            result[field_name] = html.tostring(elements[0], encoding='unicode')
                        else:
                            result[field_name] = ""
                    elif field_type == "list":
                        values = item.xpath(field_xpath)
                        result[field_name] = [clean_text(v) for v in values] if values else []
                        
                except Exception as field_e:
                    print(f"提取字段 '{field_name}' 時發生錯誤: {str(field_e)}")
                    result[field_name] = ""
            
            results.append(result)
            
        except Exception as item_e:
            print(f"處理列表項目 #{i+1} 時發生錯誤: {str(item_e)}")
    
    return results


# ===== 詳情頁面處理區 =====

def extract_restaurant_detail(driver: webdriver.Chrome, config: Dict) -> Dict[str, Any]:
    """提取餐廳詳情頁面數據"""
    print("提取餐廳詳情頁面數據...")
    
    # 確保頁面已完全加載
    scroll_behavior = config.get("advanced_settings", {}).get("scroll_behavior", {})
    if scroll_behavior.get("enable_lazy_loading", True):
        for _ in range(scroll_behavior.get("max_scroll_attempts", 5)):
            scroll_page(driver, "down", 300)
            time.sleep(scroll_behavior.get("scroll_pause", 1.5))
    
    # 截圖
    take_screenshot(driver, config, "restaurant_detail")
    
    # 獲取頁面源碼
    page_source = driver.page_source
    
    # 從頁面源碼提取數據
    detail_page_config = config.get("detail_page", {})
    tree = html.fromstring(page_source)
    
    result = {}
    
    try:
        # 提取基本餐廳信息
        for field_name, field_config in detail_page_config.get("fields", {}).items():
            if field_name == "menu_items":
                continue  # 菜單項目需要單獨處理
                
            field_xpath = field_config.get("xpath")
            field_type = field_config.get("type", "text")
            
            try:
                if field_type == "text":
                    value = tree.xpath(field_xpath)
                    result[field_name] = clean_text(value[0]) if value else ""
                elif field_type == "attribute":
                    value = tree.xpath(field_xpath)
                    result[field_name] = value[0] if value else ""
                elif field_type == "html":
                    elements = tree.xpath(field_xpath)
                    if elements:
                        result[field_name] = html.tostring(elements[0], encoding='unicode')
                    else:
                        result[field_name] = ""
                elif field_type == "list":
                    values = tree.xpath(field_xpath)
                    result[field_name] = [clean_text(v) for v in values]
                    
            except Exception as field_e:
                print(f"提取字段 '{field_name}' 時發生錯誤: {str(field_e)}")
                result[field_name] = ""
        
        # 提取菜單項目
        menu_items_config = detail_page_config.get("fields", {}).get("menu_items", {})
        if menu_items_config:
            container_xpath = menu_items_config.get("container_xpath")
            item_xpath = menu_items_config.get("item_xpath")
            
            container = tree.xpath(container_xpath)
            if container:
                menu_items = container[0].xpath(item_xpath)
                result["menu_items"] = []
                
                for item in menu_items:
                    menu_item = {}
                    
                    for field_name, field_config in menu_items_config.get("fields", {}).items():
                        field_xpath = field_config.get("xpath")
                        field_type = field_config.get("type", "text")
                        
                        try:
                            if field_type == "text":
                                value = item.xpath(field_xpath)
                                menu_item[field_name] = clean_text(value[0]) if value else ""
                            elif field_type == "attribute":
                                value = item.xpath(field_xpath)
                                menu_item[field_name] = value[0] if value else ""
                            elif field_type == "html":
                                elements = item.xpath(field_xpath)
                                if elements:
                                    menu_item[field_name] = html.tostring(elements[0], encoding='unicode')
                                else:
                                    menu_item[field_name] = ""
                                
                        except Exception as field_e:
                            print(f"提取菜單項目字段 '{field_name}' 時發生錯誤: {str(field_e)}")
                            menu_item[field_name] = ""
                    
                    result["menu_items"].append(menu_item)
            else:
                result["menu_items"] = []
    
    except Exception as e:
        print(f"提取餐廳詳情頁面數據時發生錯誤: {str(e)}")
        traceback.print_exc()
    
    return result


def extract_menu_item_detail(driver: webdriver.Chrome, config: Dict) -> Dict[str, Any]:
    """提取餐點詳情數據"""
    print("提取餐點詳情數據...")
    
    # 截圖
    take_screenshot(driver, config, "menu_item_detail")
    
    # 獲取頁面源碼
    page_source = driver.page_source
    
    # 從頁面源碼提取數據
    result = {
        "item_name": "",
        "item_price": "",
        "item_description": "",
        "options": [],
        "option_selected": config.get("search_parameters", {}).get("wantOption", {}).get("default", "")
    }
    
    try:
        tree = html.fromstring(page_source)
        
        # 提取餐點名稱
        name_elements = tree.xpath("//h1[contains(@class, 'item-title')]/text()")
        if name_elements:
            result["item_name"] = clean_text(name_elements[0])
        
        # 提取餐點價格
        price_elements = tree.xpath("//div[contains(@class, 'item-price')]/text()")
        if price_elements:
            result["item_price"] = clean_text(price_elements[0])
        
        # 提取餐點描述
        desc_elements = tree.xpath("//div[contains(@class, 'item-description')]/text()")
        if desc_elements:
            result["item_description"] = clean_text(desc_elements[0])
        
        # 提取選項
        option_elements = tree.xpath("//label[contains(@class, 'option-label')]")
        for option_el in option_elements:
            option_text = option_el.xpath("./text()")
            if option_text:
                result["options"].append(clean_text(option_text[0]))
    
    except Exception as e:
        print(f"提取餐點詳情數據時發生錯誤: {str(e)}")
        traceback.print_exc()
    
    return result


# ===== 結果處理區 =====

def save_results(results: Dict[str, Any], config: Dict) -> Optional[str]:
    """保存結果到JSON檔案"""
    if not results:
        print("沒有結果可保存")
        return None
        
    os.makedirs("output", exist_ok=True)
    
    # 使用餐廳名稱作為檔名的一部分
    restaurant = config.get("search_parameters", {}).get("wantStore", {}).get("default", "")
    item = config.get("search_parameters", {}).get("wantItem", {}).get("default", "")
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    
    filename = f"ubereats_{restaurant}_{item}_{timestamp}"
    # 移除特殊字符
    filename = re.sub(r'[\\/:*?"<>|]', '_', filename)
    
    output_file = f"output/{filename}.json"
    
    # 格式化結果以便 JSON 序列化
    formatted_results = format_for_json(results)
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(formatted_results, f, ensure_ascii=False, indent=2)
    
    print(f"結果已儲存至: {output_file}")
    
    return output_file


def handle_error(driver: webdriver.Chrome, config: Dict, error: Exception) -> None:
    """處理錯誤並保存錯誤頁面"""
    print(f"發生錯誤: {str(error)}")
    traceback.print_exc()
    
    if not driver:
        return
        
    # 檢查是否需要保存錯誤頁面
    if config.get("advanced_settings", {}).get("save_error_page", False):
        error_page_dir = config.get("advanced_settings", {}).get("error_page_dir", "../debug")
        os.makedirs(error_page_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        error_filename = f"error_{timestamp}.html"
        error_filepath = os.path.join(error_page_dir, error_filename)
        
        with open(error_filepath, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
            
        print(f"錯誤頁面已儲存至: {error_filepath}")
        
        # 順便截圖
        screenshot_path = os.path.join(error_page_dir, f"error_{timestamp}.png")
        driver.save_screenshot(screenshot_path)
        print(f"錯誤頁面截圖已儲存至: {screenshot_path}")


# ===== 主程序區 =====

def composeStores(dom):
    """組合餐廳列表資料"""
    links = dom.xpath('//a/@href')
    titles = dom.xpath('//a/h3/text()')
    images = dom.xpath('//img/@src')
    stores = []

    for idx, title in enumerate(titles):
        try:
            stores.append({
                'title': titles[idx],
                'link': links[idx],
                'image': images[idx]
            })
        except:
            print(f"處理餐廳索引 {idx} 時出錯")

    return stores


def parseWantStore(stores, wantStore):
    """在餐廳列表中尋找指定餐廳"""
    for store in stores:
        for key in store:
            if key == "title" and store[key] == wantStore:
                return store['link']
    return None


def main() -> None:
    """主函數：執行UberEats爬蟲流程"""
    driver = None
    
    try:
        # 1. 載入配置
        config_path = "../../../config/ubereats/basic/order.json"
        config = load_config(config_path)
        
        # 2. 設置WebDriver
        driver = setup_webdriver(config)
        
        # 獲取參數
        base_url = config.get("base_url", "https://www.ubereats.com")
        address = config.get("search_parameters", {}).get("address", {}).get("default", "")
        want = config.get("search_parameters", {}).get("want", {}).get("default", "")
        want_store = config.get("search_parameters", {}).get("wantStore", {}).get("default", "")
        want_category = config.get("search_parameters", {}).get("wantCategory", {}).get("default", "")
        want_item = config.get("search_parameters", {}).get("wantItem", {}).get("default", "")
        want_option = config.get("search_parameters", {}).get("wantOption", {}).get("default", "")
        
        # 3. 訪問初始URL
        initial_url = f"{base_url}/tw"
        print(f"訪問初始URL: {initial_url}")
        driver.get(initial_url)
        
        # 設置隱式等待
        driver.implicitly_wait(5)
        
        # 禁用動畫以提高穩定性
        driver.execute_script("document.body.style.webkitAnimationPlayState='paused'")
        
        # 4. 輸入取餐地址
        print(f"設置取餐地址: {address}")
        try:
            # 輸入地址
            address_input = driver.find_element(By.ID, 'location-typeahead-home-input')
            address_input.send_keys(address)
            driver.implicitly_wait(5)
            
            # 選擇第一個建議地址
            address_suggestion = driver.find_element(By.ID, 'location-typeahead-home-item-0')
            address_suggestion.click()
            driver.implicitly_wait(3)
            
            # 截圖
            take_screenshot(driver, config, "address_set")
        except Exception as e:
            print(f"設置地址時發生錯誤: {str(e)}")
            traceback.print_exc()
            raise Exception("設置地址失敗")
        
        # 5. 選擇外帶選項
        print("選擇外帶選項")
        try:
            takeout_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//div[@aria-label="外帶"]'))
            )
            takeout_button.click()
            driver.implicitly_wait(5)
            
            # 截圖
            take_screenshot(driver, config, "takeout_selected")
        except Exception as e:
            print(f"選擇外帶選項時發生錯誤: {str(e)}")
            traceback.print_exc()
            # 這個錯誤不是致命的，可以繼續執行
        
        # 6. 搜尋關鍵字
        print(f"搜尋關鍵字: {want}")
        try:
            # 等待搜尋框出現
            search_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'search-suggestions-typeahead-input'))
            )
            search_input.send_keys(want)
            search_input.send_keys(Keys.ENTER)
            driver.implicitly_wait(10)
            
            # 截圖
            take_screenshot(driver, config, "search_results")
        except Exception as e:
            print(f"搜尋關鍵字時發生錯誤: {str(e)}")
            traceback.print_exc()
            raise Exception("搜尋關鍵字失敗")
        
        # 7. 獲取搜尋結果
        print("獲取搜尋結果列表")
        try:
            # 等待搜尋結果載入
            time.sleep(5)
            
            # 滾動頁面以載入所有結果
            scroll_behavior = config.get("advanced_settings", {}).get("scroll_behavior", {})
            if scroll_behavior.get("enable_lazy_loading", True):
                for _ in range(scroll_behavior.get("max_scroll_attempts", 5)):
                    scroll_page(driver, "down", 500)
                    time.sleep(scroll_behavior.get("scroll_pause", 1.5))
            
            # 獲取結果HTML
            results_html = driver.find_element(By.XPATH, '//h3/parent::a/parent::div/parent::div/parent::div/parent::div').get_attribute('innerHTML')
            dom = html.fromstring(results_html)
            
            # 解析餐廳列表
            stores = composeStores(dom)
            print(f"找到 {len(stores)} 家餐廳")
        except Exception as e:
            print(f"獲取搜尋結果時發生錯誤: {str(e)}")
            traceback.print_exc()
            stores = []
        
        # 8. 進入指定餐廳
        print(f"進入指定餐廳: {want_store}")
        try:
            # 查找餐廳索引
            time.sleep(3)
            idx = next((i for i, item in enumerate(stores) if item["title"] == want_store), None)
            
            if idx is not None:
                store_url = base_url + stores[idx]['link']
                print(f"餐廳URL: {store_url}")
                driver.get(store_url)
                driver.implicitly_wait(8)
                
                # 截圖
                take_screenshot(driver, config, "restaurant_page")
            else:
                print(f"找不到餐廳: {want_store}")
                # 嘗試使用XPath直接搜尋餐廳
                try:
                    store_element = driver.find_element(By.XPATH, f"//h3[text()='{want_store}']/parent::a")
                    store_url = store_element.get_attribute("href")
                    driver.get(store_url)
                    driver.implicitly_wait(8)
                except Exception as inner_e:
                    print(f"嘗試直接搜尋餐廳也失敗: {str(inner_e)}")
                    raise Exception(f"找不到餐廳: {want_store}")
        except Exception as e:
            print(f"進入餐廳時發生錯誤: {str(e)}")
            traceback.print_exc()
            raise Exception("進入餐廳失敗")
        
        # 9. 獲取餐廳分類列表
        print("獲取商品分類列表")
        try:
            # 嘗試多種選擇器找到分類選項卡
            tab_list_selectors = [
                "//div[@data-baseweb='tab-list']",
                "//nav[@role='navigation']",
                "//div[@role='tablist']"
            ]
            
            tab_list_element = None
            for selector in tab_list_selectors:
                try:
                    tab_list_element = WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                    print(f"找到分類選項卡: {selector}")
                    break
                except:
                    continue
            
            if not tab_list_element:
                print("無法找到分類選項卡，將使用默認分類")
                driver.categories = []
            else:
                # 獲取分類按鈕
                tab_selectors = [
                    ".//button[@data-baseweb='tab']",
                    ".//button",
                    ".//button//span"
                ]
                
                category_buttons = []
                for selector in tab_selectors:
                    try:
                        category_buttons = tab_list_element.find_elements(By.XPATH, selector)
                        if category_buttons:
                            print(f"使用選擇器 {selector} 找到 {len(category_buttons)} 個分類按鈕")
                            break
                    except:
                        continue
                
                # 提取分類名稱
                categories = []
                for button in category_buttons:
                    try:
                        # 嘗試不同方式獲取按鈕文本
                        try:
                            category_name = button.find_element(By.XPATH, ".//span").text
                        except:
                            category_name = button.text
                        
                        if category_name:
                            categories.append({
                                'name': category_name,
                                'element': button
                            })
                            print(f"- {category_name}")
                    except Exception as btn_e:
                        print(f"解析分類按鈕失敗: {str(btn_e)}")
                
                # 保存分類列表
                driver.categories = categories
                print(f"總共找到 {len(categories)} 個分類")
            
            # 截圖
            take_screenshot(driver, config, "categories_list")
        except Exception as e:
            print(f"獲取分類列表時發生錯誤: {str(e)}")
            traceback.print_exc()
            driver.categories = []
        
        # 10. 選擇指定分類
        if (want_category and hasattr(driver, 'categories') and driver.categories):
            print(f"選擇分類: {want_category}")
            
            category_found = False
            # 嘗試精確匹配
            for cat in driver.categories:
                if cat['name'].lower() == want_category.lower():
                    print(f"找到精確匹配分類: {cat['name']}")
                    try:
                        # 滾動到按鈕位置
                        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", cat['element'])
                        time.sleep(1)
                        
                        # 點擊分類
                        driver.execute_script("arguments[0].click();", cat['element'])
                        time.sleep(2)
                        category_found = True
                        break
                    except Exception as click_e:
                        print(f"點擊分類失敗: {str(click_e)}")
            
            # 如果精確匹配失敗，嘗試模糊匹配
            if not category_found:
                for cat in driver.categories:
                    if want_category.lower() in cat['name'].lower():
                        print(f"找到模糊匹配分類: {cat['name']}")
                        try:
                            # 滾動到按鈕位置
                            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", cat['element'])
                            time.sleep(1)
                            
                            # 點擊分類
                            driver.execute_script("arguments[0].click();", cat['element'])
                            time.sleep(2)
                            category_found = True
                            break
                        except Exception as click_e:
                            print(f"點擊分類失敗: {str(click_e)}")
        
        # 11. 選購指定商品
        print(f"選購指定商品: {want_item}")
        try:
            # 等待頁面載入
            time.sleep(3)
            
            # 使用多種選擇器嘗試找到商品
            product_selectors = [
                # 精確匹配商品名稱的 span 元素
                f'//span[text()="{want_item}"]/ancestor::a',
                # 包含商品名稱的 span 元素
                f'//span[contains(text(), "{want_item}")]/ancestor::a',
                # 根據數據屬性定位餐點卡片
                f'//li[@data-testid="store-item"]//span[contains(text(), "{want_item}")]/ancestor::li',
                # 嘗試更模糊的匹配
                f'//*[contains(text(), "{want_item}")]/ancestor::a'
            ]
            
            product_found = False
            for selector in product_selectors:
                try:
                    print(f"嘗試使用選擇器: {selector}")
                    product_elements = driver.find_elements(By.XPATH, selector)
                    
                    if product_elements:
                        # 找到第一個可見的元素
                        for element in product_elements:
                            if element.is_displayed():
                                # 滾動到商品位置
                                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
                                time.sleep(1)
                                
                                # 使用 JavaScript 點擊元素
                                driver.execute_script("arguments[0].click();", element)
                                product_found = True
                                
                                print(f"已成功找到並點擊商品: {want_item}")
                                time.sleep(3)  # 等待商品選擇生效
                                break
                        
                        if product_found:
                            break
                except Exception as selector_e:
                    print(f"使用選擇器 {selector} 定位商品失敗: {str(selector_e)}")
            
            # 如果找不到商品，嘗試搜尋所有可能包含商品名稱的元素
            if not product_found:
                try:
                    print("嘗試搜尋所有包含商品名稱的元素")
                    # 獲取頁面源碼
                    page_source = driver.page_source
                    soup = html.fromstring(page_source)
                    
                    # 嘗試通過截圖輔助調試
                    take_screenshot(driver, config, "product_search")
                    
                    # 使用ActionChains嘗試點擊
                    actions = ActionChains(driver)
                    
                    # 找到所有可能的元素
                    items = driver.find_elements(By.XPATH, f"//*[contains(text(), '{want_item}')]")
                    for item in items:
                        if item.is_displayed():
                            print(f"找到可能的商品元素: {item.text}")
                            try:
                                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", item)
                                time.sleep(1)
                                actions.move_to_element(item).click().perform()
                                time.sleep(2)
                                product_found = True
                                break
                            except:
                                continue
                except Exception as e:
                    print(f"最後嘗試也失敗: {str(e)}")
            
            if not product_found:
                raise Exception(f"找不到商品: {want_item}")
            
        except Exception as e:
            print(f"選購商品時發生錯誤: {str(e)}")
            traceback.print_exc()
            raise Exception("選購商品失敗")
        
        # 12. 在對話框中選擇選項
        print(f"選擇商品選項: {want_option}")
        try:
            # 等待對話框加載
            time.sleep(3)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//main[@id="main-content"]//h1')))
            
            # 定位選項按鈕
            option_selectors = [
                f'//div[@data-testid="customization-pick-one"]//label//div[contains(text(),"{want_option}")]/ancestor::label',
                f'//label//div[contains(text(),"{want_option}")]/ancestor::label',
                f'//label[contains(.,"{want_option}")]'
            ]
            
            option_found = False
            for selector in option_selectors:
                try:
                    option_elements = driver.find_elements(By.XPATH, selector)
                    
                    if option_elements:
                        for option in option_elements:
                            if option.is_displayed():
                                # 滾動到選項位置
                                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", option)
                                time.sleep(1)
                                
                                # 點擊選項
                                driver.execute_script("arguments[0].click();", option)
                                time.sleep(1)
                                option_found = True
                                print(f"已選擇選項: {want_option}")
                                break
                        
                        if option_found:
                            break
                except Exception as selector_e:
                    print(f"使用選擇器 {selector} 選擇選項失敗: {str(selector_e)}")
            
            # 截圖
            take_screenshot(driver, config, "option_selected")
        except Exception as e:
            print(f"選擇選項時發生錯誤: {str(e)}")
            traceback.print_exc()
            print("選項選擇失敗，繼續執行")
        
        # 13. 加入購物車
        print("加入購物車")
        try:
            # 定位加入購物車按鈕
            add_to_cart_selectors = [
                '//main[@id="main-content"]//div[@data-test="add-to-cart-cta"]/button',
                '//button[contains(text(), "加入購物車")]',
                '//button[@data-test="add-to-cart"]',
                '//button[contains(@class, "add-to-cart")]'
            ]
            
            cart_button_found = False
            for selector in add_to_cart_selectors:
                try:
                    cart_buttons = driver.find_elements(By.XPATH, selector)
                    
                    if cart_buttons:
                        for button in cart_buttons:
                            if button.is_displayed():
                                # 滾動到按鈕位置
                                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", button)
                                time.sleep(1)
                                
                                # 點擊按鈕
                                driver.execute_script("arguments[0].click();", button)
                                time.sleep(2)
                                cart_button_found = True
                                print("已加入購物車")
                                break
                        
                        if cart_button_found:
                            break
                except Exception as selector_e:
                    print(f"使用選擇器 {selector} 點擊加入購物車失敗: {str(selector_e)}")
            
            # 截圖
            take_screenshot(driver, config, "added_to_cart")
        except Exception as e:
            print(f"加入購物車時發生錯誤: {str(e)}")
            traceback.print_exc()
            print("加入購物車失敗，繼續執行")
        
        # 14. 獲取當前頁面資訊
        print("獲取最終頁面資訊")
        try:
            # 獲取頁面源碼
            page_source = driver.page_source
            
            # 解析頁面資訊
            menu_item_detail = extract_menu_item_detail(driver, config)
            
            # 組織最終結果
            final_results = {
                "timestamp": datetime.now().isoformat(),
                "search_parameters": {
                    "address": address,
                    "keyword": want,
                    "restaurant": want_store,
                    "category": want_category,
                    "menu_item": want_item,
                    "option": want_option
                },
                "restaurant_info": {
                    "name": want_store,
                    "url": driver.current_url
                },
                "menu_item_detail": menu_item_detail
            }
            
            # 保存結果
            save_results(final_results, config)
        except Exception as e:
            print(f"獲取頁面資訊時發生錯誤: {str(e)}")
            traceback.print_exc()
        
        print("爬蟲執行完成！")
        
    except TimeoutException:
        print("頁面載入超時")
        handle_error(driver, config, TimeoutException("頁面載入超時"))
    except Exception as e:
        handle_error(driver, config, e)
    finally:
        if driver:
            # 等待一下，讓用戶可以看到最終頁面
            finish_delay = config.get("delays", {}).get("finish", 3)
            time.sleep(finish_delay)
            driver.quit()

if __name__ == "__main__":
    main()