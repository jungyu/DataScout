"""
政府電子採購網-決標查詢爬蟲程式
基於配置文件的政府電子採購網資料爬取工具
支援標案名稱、決標日期範圍、採購性質等條件搜尋
"""

import os
import re
import json
import time
import urllib.parse
import traceback
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Union
from urllib.parse import urlencode

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from lxml import html


# ===== 工具函數區 =====

def wait_for_element(driver: webdriver.Chrome, by: str, selector: str, timeout: int = 10) -> Any:
    """等待元素出現並返回"""
    wait = WebDriverWait(driver, timeout)
    return wait.until(EC.presence_of_element_located((by, selector)))

def wait_for_element_clickable(driver: webdriver.Chrome, by: str, selector: str, timeout: int = 10) -> Any:
    """等待元素可點擊並返回"""
    wait = WebDriverWait(driver, timeout)
    return wait.until(EC.element_to_be_clickable((by, selector)))

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


def normalize_url(url: str, base_domain: str = "https://web.pcc.gov.tw") -> str:
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


def safe_click(driver: webdriver.Chrome, element, retries: int = 3) -> bool:
    """安全點擊元素，處理各種點擊異常"""
    for i in range(retries):
        try:
            # 先嘗試滾動到元素位置
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(0.5)
            
            try:
                # 嘗試直接點擊
                element.click()
                return True
            except (ElementClickInterceptedException, Exception) as e:
                print(f"直接點擊失敗 (嘗試 {i+1}/{retries}): {str(e)}")
                # 使用JavaScript點擊
                driver.execute_script("arguments[0].click();", element)
                return True
                
        except Exception as e:
            print(f"點擊失敗 (嘗試 {i+1}/{retries}): {str(e)}")
            time.sleep(1)
    
    print("所有點擊嘗試均失敗")
    return False


# ===== 搜尋參數處理區 =====

def set_search_parameters(driver: webdriver.Chrome, config: Dict) -> bool:
    """設置搜尋參數"""
    try:
        print("\n設置搜尋參數...")
        search_params = config.get("search_parameters", {})
        
        for param_name, param_config in search_params.items():
            if param_name == "search_button":
                continue
                
            param_type = param_config.get("type")
            
            if param_type == "input":
                if not fill_input_field(driver, param_config):
                    print(f"填入 {param_config.get('description', '')} 失敗")
                    return False
                    
            elif param_type == "radio":
                if not select_radio_option(driver, param_config):
                    print(f"選擇 {param_config.get('description', '')} 失敗")
                    return False
                    
            elif param_type == "select":
                if not select_dropdown_option(driver, param_config):
                    print(f"選擇 {param_config.get('description', '')} 失敗")
                    return False
        
        # 點擊搜尋按鈕
        search_button = wait_for_element_clickable(driver, By.XPATH, search_params["search_button"]["selector"])
        if not search_button:
            print("找不到搜尋按鈕")
            return False
            
        search_button.click()
        time.sleep(search_params["search_button"].get("wait_after_click", 3))
        
        return True
        
    except Exception as e:
        print(f"設置搜尋參數時發生錯誤: {str(e)}")
        return False


def fill_input_field(driver: webdriver.Chrome, field_config: Dict) -> bool:
    """填入輸入框"""
    try:
        # 獲取輸入框元素
        elements = driver.find_elements(By.XPATH, field_config["selector"])
        if not elements:
            print(f"找不到輸入框: {field_config.get('description', '')}")
            return False
            
        # 獲取值
        value = field_config.get("value", "")
        
        # 處理日期格式
        if not value and field_config.get("use_current_date"):
            current_date = datetime.now()
            if field_config.get("use_roc_year", False):
                roc_year = current_date.year - 1911
                if "開始日期" in field_config.get("description", ""):
                    value = "114/01/01"
                else:
                    value = f"{roc_year:03d}/{current_date.month:02d}/{current_date.day:02d}"
                print(f"使用中華民國年: {value}")
            else:
                date_format = field_config.get("date_format", "%Y/%m/%d")
                value = current_date.strftime(date_format)
                print(f"使用西元年: {value}")
        
        print(f"填入 {field_config.get('description', '')}: {value}")
        
        # 清除並填入值（使用重試機制）
        max_retries = 3
        for attempt in range(max_retries):
            try:
                success = True
                for element in elements:
                    # 等待元素可交互
                    wait = WebDriverWait(driver, 10)
                    wait.until(EC.element_to_be_clickable((By.XPATH, field_config["selector"])))
                    
                    # 先嘗試滾動到元素位置
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                    time.sleep(0.5)
                    
                    # 使用 JavaScript 清除和設置值
                    driver.execute_script("""
                        var input = arguments[0];
                        input.value = '';
                        input.value = arguments[1];
                        input.dispatchEvent(new Event('input', { bubbles: true }));
                        input.dispatchEvent(new Event('change', { bubbles: true }));
                    """, element, value)
                    time.sleep(0.5)
                    
                    # 驗證值是否正確設置
                    actual_value = element.get_attribute("value")
                    if actual_value != value:
                        success = False
                        break
                
                if success:
                    return True
                    
            except Exception as e:
                print(f"填入輸入框嘗試 {attempt + 1}/{max_retries} 失敗: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(1)
                else:
                    print("所有填入嘗試均失敗")
                    return False
        
        return True
        
    except Exception as e:
        print(f"填入輸入框時發生錯誤: {str(e)}")
        return False


def select_radio_option(driver: webdriver.Chrome, field_config: Dict) -> bool:
    """選擇單選按鈕選項"""
    try:
        value = field_config.get("value")
        if not value:
            print(f"未指定 {field_config.get('description', '')} 的值")
            return False
            
        for option in field_config.get("options", []):
            if option["value"] == value:
                element = wait_for_element_clickable(driver, By.XPATH, option["selector"])
                if not element:
                    print(f"找不到選項: {value}")
                    return False
                    
                # 使用 JavaScript 點擊
                driver.execute_script("arguments[0].click();", element)
                time.sleep(0.5)
                
                # 驗證是否選中
                if element.is_selected():
                    return True
                else:
                    # 如果 JavaScript 點擊失敗，嘗試直接設置 checked 屬性
                    driver.execute_script("arguments[0].checked = true;", element)
                    time.sleep(0.5)
                    return element.is_selected()
                    
        print(f"找不到符合的選項: {value}")
        return False
        
    except Exception as e:
        print(f"選擇單選按鈕時發生錯誤: {str(e)}")
        return False


def select_dropdown_option(driver: webdriver.Chrome, field_config: Dict) -> bool:
    """選擇下拉選單選項"""
    try:
        value = field_config.get("value")
        if not value:
            print(f"未指定 {field_config.get('description', '')} 的值")
            return False
            
        # 找到下拉選單容器
        container = wait_for_element_clickable(driver, By.XPATH, field_config["container_selector"])
        if not container:
            print("找不到下拉選單容器")
            return False
            
        # 先滾動到元素位置
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", container)
        time.sleep(0.5)
        
        # 使用 JavaScript 直接設置值
        for option in field_config.get("options", []):
            if option["value"] == value:
                try:
                    script = """
                        var select = arguments[0];
                        var value = arguments[1];
                        select.value = value;
                        select.dispatchEvent(new Event('change'));
                    """
                    driver.execute_script(script, container, option["option_value"])
                    time.sleep(0.5)
                    
                    # 驗證值是否正確設置
                    actual_value = container.get_attribute("value")
                    if actual_value == option["option_value"]:
                        print(f"成功選擇 {field_config.get('description', '')}: {value}")
                        return True
                        
                    print(f"選擇值驗證失敗: 期望 {option['option_value']}, 實際 {actual_value}")
                    return False
                    
                except Exception as e:
                    print(f"設置下拉選單值時發生錯誤: {str(e)}")
                    return False
                    
        print(f"找不到符合的選項: {value}")
        return False
        
    except Exception as e:
        print(f"選擇下拉選單時發生錯誤: {str(e)}")
        return False


# ===== 列表頁面處理區 =====

def get_total_records_count(driver: webdriver.Chrome, config: Dict) -> int:
    """取得搜尋結果總筆數"""
    try:
        total_count_xpath = config.get("list_page", {}).get("total_count_xpath")
        if not total_count_xpath:
            return 0
            
        # 解析頁面獲取總筆數
        tree = html.fromstring(driver.page_source)
        elements = tree.xpath(total_count_xpath)
        
        if elements:
            # 嘗試提取文本中的數字
            text_content = elements[0]
            if isinstance(text_content, str) and text_content.isdigit():
                return int(text_content)
        
        # 如果無法從總筆數標籤獲取，嘗試計算當前頁面的項目數量
        item_xpath = config.get("list_page", {}).get("item_xpath")
        if item_xpath:
            items = tree.xpath(item_xpath)
            return len(items)
            
        return 0
            
    except Exception as e:
        print(f"獲取總筆數時發生錯誤: {str(e)}")
        return 0


def extract_list_items(driver: webdriver.Chrome, config: Dict) -> List[Dict]:
    """解析列表頁面的項目"""
    try:
        # 等待列表容器出現
        container_xpath = config["list_page"]["container_xpath"]
        print(f"等待列表容器出現: {container_xpath}")
        
        # 使用 WebDriverWait 等待元素出現
        wait = WebDriverWait(driver, 10)
        container = wait.until(EC.presence_of_element_located((By.XPATH, container_xpath)))
        
        if not container:
            print("找不到列表容器")
            return []
            
        # 使用 lxml 解析頁面
        tree = html.fromstring(driver.page_source)
        items = tree.xpath(config["list_page"]["item_xpath"])
        
        if not items:
            print("找不到列表項目")
            return []
            
        results = []
        for item in items:
            try:
                result = {}
                for field_name, field_config in config["list_page"]["fields"].items():
                    try:
                        if field_config["type"] == "text":
                            elements = item.xpath(field_config["xpath"])
                            if elements:
                                result[field_name] = elements[0].strip()
                            else:
                                result[field_name] = ""
                                
                        elif field_config["type"] == "attribute":
                            elements = item.xpath(field_config["xpath"])
                            if elements:
                                value = elements[0]
                                if "regex" in field_config:
                                    match = re.search(field_config["regex"], value)
                                    if match:
                                        pk = match.group(1)
                                        if field_name == "detail_pk":
                                            # 構建詳細頁面 URL
                                            result["detail_url"] = f"https://web.pcc.gov.tw/tps/atm/AtmAwardWithoutSso/QueryAtmAwardDetail?pkAtmMain={pk}"
                                            print(f"成功提取詳細頁面 URL: {result['detail_url']}")
                                        else:
                                            result[field_name] = pk
                                    else:
                                        print(f"正則表達式匹配失敗: {value}")
                                        result[field_name] = ""
                                else:
                                    result[field_name] = value
                            else:
                                print(f"找不到 {field_name} 的元素")
                                result[field_name] = ""
                                
                    except Exception as e:
                        print(f"解析欄位 {field_name} 時發生錯誤: {str(e)}")
                        result[field_name] = ""
                        
                results.append(result)
                
            except Exception as e:
                print(f"解析項目時發生錯誤: {str(e)}")
                continue
                
        print(f"成功提取 {len(results)} 筆資料")
        return results
        
    except TimeoutException:
        print("等待列表容器超時")
        return []
        
    except Exception as e:
        print(f"解析列表頁面時發生錯誤: {str(e)}")
        return []


# ===== 分頁控制區 =====

def has_next_page(driver: webdriver.Chrome, config: Dict) -> bool:
    """檢查是否有下一頁"""
    has_next_check = config.get("pagination", {}).get("has_next_page_check")
    if not has_next_check:
        return False
        
    try:
        # 執行 XPath 表達式以檢查是否有下一頁按鈕
        return bool(driver.execute_script(
            f"return Boolean(document.evaluate('{has_next_check}', document, null, XPathResult.BOOLEAN_TYPE, null).booleanValue);"
        ))
    except Exception:
        return False


def go_to_next_page(driver: webdriver.Chrome, config: Dict) -> bool:
    """點擊下一頁按鈕"""
    next_button_xpath = config.get("pagination", {}).get("next_button_xpath")
    if not next_button_xpath:
        return False
        
    try:
        print("嘗試前往下一頁...")
        next_button = driver.find_element(By.XPATH, next_button_xpath)
        return safe_click(driver, next_button)
    except NoSuchElementException:
        print("找不到下一頁按鈕")
        return False
    except Exception as e:
        print(f"前往下一頁時發生錯誤: {str(e)}")
        return False


def process_pagination(driver: webdriver.Chrome, config: Dict) -> List[Dict]:
    """處理分頁爬取"""
    all_results = []
    current_page = 1
    max_pages = config["pagination"]["max_pages"]
    max_retries = config.get("retries", {}).get("max_retries", 3)
    
    print("\n開始處理分頁爬取...")
    
    while current_page <= max_pages:
        print(f"\n--- 正在處理第 {current_page} 頁 ---")
        retry_count = 0
        success = False
        
        while retry_count < max_retries and not success:
            try:
                # 等待頁面加載
                time.sleep(config["delays"]["page_load"])
                
                # 解析列表頁面
                print("解析列表頁面...")
                results = extract_list_items(driver, config)
                
                if results:
                    all_results.extend(results)
                    print(f"第 {current_page} 頁成功提取 {len(results)} 筆資料")
                    success = True
                else:
                    print(f"第 {current_page} 頁未找到任何資料")
                    retry_count += 1
                    if retry_count < max_retries:
                        print(f"重試第 {retry_count + 1} 次...")
                        time.sleep(config["delays"]["retry"])
                    else:
                        print("已達最大重試次數，放棄當前頁面")
                        break
                        
            except Exception as e:
                print(f"處理第 {current_page} 頁時發生錯誤: {str(e)}")
                retry_count += 1
                if retry_count < max_retries:
                    print(f"重試第 {retry_count + 1} 次...")
                    time.sleep(config["delays"]["retry"])
                else:
                    print("已達最大重試次數，放棄當前頁面")
                    break
                    
        if not success:
            break
            
        # 檢查是否有下一頁
        try:
            has_next = driver.execute_script(config["pagination"]["has_next_page_check"])
            if not has_next:
                print("沒有下一頁了")
                break
                
            # 點擊下一頁
            next_button = driver.find_element(By.XPATH, config["pagination"]["next_button_xpath"])
            driver.execute_script("arguments[0].click();", next_button)
            time.sleep(config["delays"]["between_pages"])
            current_page += 1
            
        except Exception as e:
            print(f"檢查下一頁時發生錯誤: {str(e)}")
            break
            
    print(f"\n分頁爬取完成，共爬取 {len(all_results)} 筆資料")
    return all_results


# ===== 詳情頁面處理區 =====

def expand_sections(driver: webdriver.Chrome, config: Dict) -> bool:
    """展開詳情頁面中的摺疊區塊"""
    expand_sections_config = config.get("detail_page", {}).get("expand_sections", [])
    if not expand_sections_config:
        return True
    
    success = True
    
    for section in expand_sections_config:
        try:
            button_selector = section.get("button_selector")
            target_selector = section.get("target_selector")
            wait_time = section.get("wait_time", 1)
            description = section.get("description", "摺疊區塊")
            
            print(f"嘗試展開{description}...")
            
            # 找到展開按鈕並點擊
            try:
                expand_button = driver.find_element(By.XPATH, button_selector)
                if safe_click(driver, expand_button):
                    # 等待區塊展開
                    time.sleep(wait_time)
                    
                    # 檢查目標是否已顯示
                    target = driver.find_element(By.XPATH, target_selector)
                    if target.is_displayed():
                        print(f"已成功展開{description}")
                    else:
                        print(f"未能成功展開{description}")
                        success = False
                else:
                    print(f"點擊展開按鈕失敗: {description}")
                    success = False
            except NoSuchElementException:
                print(f"找不到展開按鈕: {button_selector}")
                success = False
                
        except Exception as e:
            print(f"展開區塊時發生錯誤: {str(e)}")
            success = False
    
    return success


def extract_detail_nested_fields(container_element, fields_config: Dict) -> Dict:
    """抽取嵌套欄位的數據"""
    result = {}
    
    for field_name, field_config in fields_config.items():
        try:
            xpath = field_config.get("xpath")
            field_type = field_config.get("type")
            multiple = field_config.get("multiple", False)
            
            # 提取元素
            elements = container_element.xpath(xpath)
            
            if elements:
                # 依據元素類型處理
                if field_type == "text":
                    if multiple:
                        result[field_name] = [clean_text(el) for el in elements]
                    else:
                        result[field_name] = clean_text(elements[0])
                        
                elif field_type == "attribute":
                    attr_values = elements
                    # 如果有正則表達式，從屬性值提取特定部分
                    regex_pattern = field_config.get("regex")
                    if regex_pattern:
                        attr_values = []
                        for val in elements:
                            match = re.search(regex_pattern, val)
                            if match:
                                attr_values.append(match.group(1))
                            else:
                                attr_values.append(val)
                    
                    if multiple:
                        result[field_name] = attr_values
                    else:
                        result[field_name] = attr_values[0] if attr_values else None
                        
                elif field_type == "elements" and "fields" in field_config:
                    # 處理嵌套欄位
                    nested_fields = []
                    for el in elements:
                        nested_data = extract_detail_nested_fields(el, field_config.get("fields", {}))
                        if nested_data:
                            nested_fields.append(nested_data)
                    
                    if nested_fields:
                        result[field_name] = nested_fields
        
        except Exception as e:
            print(f"提取嵌套欄位 '{field_name}' 時出錯: {e}")
    
    return result


def extract_detail_page(driver: webdriver.Chrome, url: str, config: Dict) -> Dict[str, Any]:
    """提取詳細頁面資訊"""
    try:
        # 標準化URL
        detail_url = normalize_url(url)
        if not detail_url:
            print(f"無效的詳細頁面URL: {url}")
            return {}
            
        print(f"\n正在處理詳細頁面: {detail_url}")
        driver.get(detail_url)
        
        # 等待頁面加載
        page_load_delay = config.get("delays", {}).get("page_load", 3)
        time.sleep(page_load_delay)
        
        # 等待詳情內容載入
        container_xpath = config.get("detail_page", {}).get("container_xpath")
        try:
            wait_for_element(driver, By.XPATH, container_xpath)
        except TimeoutException:
            print("詳情頁面未正確加載，可能無法獲取完整數據")
        
        # 展開所有摺疊區塊
        expand_sections(driver, config)
        
        # 解析頁面
        page_source = driver.page_source
        tree = html.fromstring(page_source)
        
        # 檢查是否有主容器
        container_elements = tree.xpath(container_xpath)
        if not container_elements:
            print(f"未找到詳情頁面內容容器: {container_xpath}")
            return {"error": "找不到詳情頁面容器"}
        
        # 設定主容器作為XPath的起點
        container = container_elements[0]
        
        # 提取配置中定義的所有字段
        detail_fields = config.get("detail_page", {}).get("fields", {})
        result = {}
        
        # 提取所有配置的字段
        for field_name, field_config in detail_fields.items():
            try:
                xpath = field_config.get("xpath")
                field_type = field_config.get("type")
                multiple = field_config.get("multiple", False)
                
                # 從容器中提取元素
                elements = container.xpath(xpath)
                
                if elements:
                    if field_type == "text":
                        if multiple:
                            result[field_name] = [clean_text(el) for el in elements]
                        else:
                            text_value = clean_text(elements[0])
                            # 如果有正則表達式，提取指定部分
                            regex_pattern = field_config.get("regex")
                            if regex_pattern and text_value:
                                match = re.search(regex_pattern, text_value)
                                if match:
                                    text_value = match.group(1)
                            result[field_name] = text_value
                            
                    elif field_type == "attribute":
                        attr_values = elements
                        # 如果有正則表達式，從屬性值提取特定部分
                        regex_pattern = field_config.get("regex")
                        if regex_pattern:
                            attr_values = []
                            for val in elements:
                                match = re.search(regex_pattern, val)
                                if match:
                                    attr_values.append(match.group(1))
                                else:
                                    attr_values.append(val)
                        
                        if multiple:
                            result[field_name] = attr_values
                        else:
                            result[field_name] = attr_values[0] if attr_values else None
                    
                    elif field_type == "elements" and "fields" in field_config:
                        # 處理嵌套欄位
                        nested_fields = []
                        for el in elements:
                            nested_data = extract_detail_nested_fields(el, field_config.get("fields", {}))
                            if nested_data:
                                nested_fields.append(nested_data)
                    
                        if nested_fields:
                            result[field_name] = nested_fields
                
                # 輸出結果預覽
                if field_name in result:
                    description = field_config.get("description", field_name)
                    value_preview = str(result[field_name])
                    if len(value_preview) > 50:
                        value_preview = value_preview[:47] + "..."
                    print(f"  提取 {description}: {value_preview}")
            
            except Exception as e:
                print(f"  提取字段 '{field_name}' 時出錯: {e}")
                result[field_name] = None
        
        fields_count = len([k for k, v in result.items() if v is not None])
        print(f"已提取 {fields_count} 個詳情字段")
        return result
        
    except Exception as e:
        print(f"提取詳情頁時出錯: {e}")
        return {"error": str(e)}


def process_detail_pages(driver: webdriver.Chrome, results: List[Dict], config: Dict) -> List[Dict]:
    """處理詳情頁面"""
    detailed_results = []
    item_delay = config.get("delays", {}).get("item_delay", 1)
    max_retries = config.get("retries", {}).get("max_retries", 3)
    
    for i, item in enumerate(results, 1):
        detail_url = item.get("detail_url")
        if not detail_url:
            print(f"跳過項目 {i}/{len(results)}：無詳情頁URL")
            continue
            
        print(f"處理詳情頁 {i}/{len(results)}：{detail_url}")
        
        # 重試機制
        for retry in range(max_retries):
            try:
                # 檢查瀏覽器視窗是否還存在
                try:
                    driver.current_url
                except:
                    print("瀏覽器視窗已關閉，重新初始化...")
                    driver = setup_webdriver(config)
                    driver.get(config["urls"]["base"])
                    time.sleep(config["delays"]["page_load"])
                
                # 訪問詳情頁
                print(f"訪問詳情頁: {detail_url}")
                driver.get(detail_url)
                time.sleep(config["delays"]["page_load"])
                
                # 展開所有作業歷程
                expand_sections(driver, config)
                
                # 提取詳情字段
                detail_data = extract_detail_page(driver, detail_url, config)
                
                # 合併搜尋結果和詳情數據
                item.update(detail_data)
                detailed_results.append(item)
                
                # 成功處理後跳出重試循環
                break
                
            except Exception as e:
                print(f"提取詳情頁時出錯 (嘗試 {retry + 1}/{max_retries}): {str(e)}")
                if retry == max_retries - 1:
                    print(f"無法處理詳情頁 {detail_url}，跳過此項目")
                    detailed_results.append(item)  # 保留原始數據
                else:
                    time.sleep(item_delay * 2)  # 失敗後等待更長時間
                    
        time.sleep(item_delay)
        
    return detailed_results


# ===== 結果處理區 =====

def save_results(results: List[Dict], output_path: str) -> Optional[str]:
    """保存結果到JSON檔案"""
    if not results:
        print("沒有結果可保存")
        return None
        
    # 確保輸出目錄存在
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # 格式化結果以便 JSON 序列化
    formatted_results = format_for_json(results)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(formatted_results, f, ensure_ascii=False, indent=2)
    
    print(f"結果已儲存至: {output_path}")
    
    # 顯示擷取結果摘要
    total_details = sum(1 for result in results if result.get("detail") and not isinstance(result.get("detail"), str))
    print(f"共擷取 {len(results)} 筆標案記錄，成功解析 {total_details} 個詳情頁面")
    
    return output_path


def handle_error(driver: webdriver.Chrome, config: Dict, error: Exception) -> None:
    """處理錯誤並保存錯誤頁面"""
    print(f"發生錯誤: {str(error)}")
    traceback.print_exc()
    
    if not driver:
        return
        
    # 檢查是否需要保存錯誤頁面
    if config.get("advanced_settings", {}).get("save_error_page", False):
        try:
            # 獲取錯誤頁面保存目錄
            error_dir = config.get("advanced_settings", {}).get("error_page_dir", "../debug")
            os.makedirs(error_dir, exist_ok=True)
            
            # 生成檔案名
            timestamp = int(time.time())
            filename_base = f"error_{timestamp}"
            
            # 儲存截圖
            screenshot_path = os.path.join(error_dir, f"{filename_base}.png")
            driver.save_screenshot(screenshot_path)
            
            # 儲存頁面源碼
            html_path = os.path.join(error_dir, f"{filename_base}.html")
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
                
            print(f"已儲存錯誤頁面: 截圖={screenshot_path}, HTML={html_path}")
        except Exception as e:
            print(f"儲存錯誤頁面失敗: {str(e)}")


# ===== 主程序區 =====

def build_search_url(config: Dict) -> str:
    """建構搜尋 URL"""
    base_url = config.get("urls", {}).get("search", "")
    if not base_url:
        raise ValueError("未設定搜尋 URL")

    # 從配置中獲取所有搜尋參數
    params = {}
    search_params = config.get("search_parameters", {})
    for key, param in search_params.items():
        if param.get("type") == "hidden" or param.get("value"):
            # 特殊處理某些參數名稱
            if key == "procurement_category":
                api_key = "radProctrgCate"
            else:
                # 將底線轉換為駝峰命名
                words = key.split("_")
                api_key = words[0] + "".join(word.capitalize() for word in words[1:])
            params[api_key] = param.get("value", "")

    # 構建查詢字串
    query_string = urlencode(params)
    return f"{base_url}?{query_string}"


def perform_search(driver: webdriver.Chrome, search_keyword: str, config: Dict) -> webdriver.Chrome:
    """執行搜尋操作"""
    max_retries = config.get("retries", {}).get("max_retries", 3)
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # 訪問基礎頁面
            base_url = config.get("urls", {}).get("base", "")
            print(f"訪問基礎頁面: {base_url}")
            driver.get(base_url)
            time.sleep(config["delays"]["page_load"])
            
            # 設置搜尋參數
            print("設置搜尋參數...")
            for param_name, param_config in config["search_parameters"].items():
                if param_name == "search_button":
                    continue
                    
                try:
                    if param_config["type"] == "input":
                        element = driver.find_element(By.XPATH, param_config["selector"])
                        if param_name == "tender_name":
                            element.clear()
                            element.send_keys(search_keyword)
                        else:
                            value = param_config.get("value", "")
                            if param_config.get("use_current_date"):
                                date_format = param_config.get("date_format", "%y/%m/%d")
                                value = datetime.now().strftime(date_format)
                                print(f"使用當前日期: {value}")
                            element.clear()
                            element.send_keys(value)
                            
                    elif param_config["type"] == "radio":
                        for option in param_config["options"]:
                            if option["value"] == param_config["value"]:
                                element = driver.find_element(By.XPATH, option["selector"])
                                if not element.is_selected():
                                    element.click()
                                break
                                
                except Exception as e:
                    print(f"設置參數 {param_name} 時出錯: {str(e)}")
                    continue
            
            # 點擊查詢按鈕
            print("等待查詢按鈕出現...")
            wait = WebDriverWait(driver, 10)
            search_button = wait.until(EC.element_to_be_clickable(
                (By.XPATH, config["search_parameters"]["search_button"]["selector"])
            ))
            
            print("點擊查詢按鈕...")
            # 使用 JavaScript 直接觸發函數
            driver.execute_script("agentTenderSearch();")
            
            # 等待頁面加載
            wait_time = config["search_parameters"]["search_button"].get("wait_after_click", 5)
            print(f"等待 {wait_time} 秒...")
            time.sleep(wait_time)
            
            # 檢查是否需要重定向到搜尋URL
            search_url = config.get("urls", {}).get("search", "")
            current_url = driver.current_url
            
            if search_url and current_url != search_url:
                print(f"重定向到搜尋頁面: {search_url}")
                driver.get(search_url)
                time.sleep(config["delays"]["page_load"])
            
            return driver
            
        except Exception as e:
            print(f"搜尋操作失敗 (嘗試 {retry_count + 1}/{max_retries}): {str(e)}")
            retry_count += 1
            if retry_count < max_retries:
                print("重新初始化 WebDriver...")
                driver.quit()
                driver = setup_webdriver(config)
            else:
                print("已達最大重試次數，放棄搜尋")
                raise
    
    return driver


def main():
    """主程式入口"""
    try:
        # 步驟1：載入配置
        config_path = "examples/config/pcc/basic/award.json"
        config = load_config(config_path)
        if not config:
            return
            
        # 步驟2：初始化WebDriver
        driver = setup_webdriver(config)
        
        # 步驟3：直接訪問搜尋結果頁面
        search_url = build_search_url(config)
        print(f"\n訪問搜尋結果頁面: {search_url}")
        
        driver.get(search_url)
        time.sleep(config.get("delays", {}).get("page_load", 3))
        
        # 步驟4：處理分頁爬取
        print("\n開始處理分頁爬取...")
        all_results = process_pagination(driver, config)
        
        if not all_results:
            print("未找到任何資料")
            return
            
        print(f"\n分頁爬取完成，共獲取 {len(all_results)} 筆資料")
        
        # 步驟5：處理詳情頁
        print("\n開始處理詳情頁...")
        detailed_results = process_detail_pages(driver, all_results, config)
        
        if not detailed_results:
            print("詳情頁處理失敗")
            return
            
        print(f"\n詳情頁處理完成，成功處理 {len(detailed_results)} 筆資料")
        
        # 步驟6：保存結果
        output_path = config.get("output", {}).get("path", "output.json")
        save_results(detailed_results, output_path)
        print(f"\n結果已保存至: {output_path}")
        
    except Exception as e:
        print(f"程序執行過程中發生錯誤: {str(e)}")
        traceback.print_exc()
    finally:
        if driver:
            driver.quit()
            print("\n瀏覽器已關閉")


if __name__ == "__main__":
    main()