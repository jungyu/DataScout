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
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Union

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
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


def wait_for_element(driver: webdriver.Chrome, by: str, selector: str, timeout: int = 10) -> Any:
    """等待元素出現並返回"""
    wait = WebDriverWait(driver, timeout)
    return wait.until(EC.presence_of_element_located((by, selector)))


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
    """設置搜尋參數：標案名稱、日期、採購性質等"""
    try:
        print("\n設置搜尋參數...")
        search_params = config.get("search_parameters", {})
        
        # 1. 填入標案名稱
        tender_name_config = search_params.get("tender_name", {})
        if tender_name_config:
            fill_input_field(driver, tender_name_config)
            
        # 2. 填入決標公告開始日期
        start_date_config = search_params.get("award_announce_start_date", {})
        if start_date_config:
            fill_input_field(driver, start_date_config)
            
        # 3. 填入決標公告結束日期 (可能使用當前日期)
        end_date_config = search_params.get("award_announce_end_date", {})
        if end_date_config:
            if end_date_config.get("use_current_date", False):
                # 如果需要使用當前日期
                today = datetime.today().strftime(end_date_config.get("date_format", "yyy/MM/dd"))
                end_date_config["default"] = today
                
            fill_input_field(driver, end_date_config)
            
        # 4. 選擇採購性質 (單選)
        procurement_category_config = search_params.get("procurement_category", {})
        if procurement_category_config:
            select_radio_option(driver, procurement_category_config)
            
        # 5. 選擇標案狀態 (下拉選單)
        tender_status_config = search_params.get("tender_status", {})
        if tender_status_config:
            select_dropdown_option(driver, tender_status_config)
            
        # 6. 選擇招標方式 (下拉選單)
        tender_way_config = search_params.get("tender_way", {})
        if tender_way_config:
            select_dropdown_option(driver, tender_way_config)
            
        # 7. 點擊搜尋按鈕
        search_button_selector = search_params.get("search_button", {}).get("selector")
        if search_button_selector:
            print("點擊搜尋按鈕...")
            search_button = driver.find_element(By.XPATH, search_button_selector)
            if not safe_click(driver, search_button):
                print("點擊搜尋按鈕失敗")
                return False
                
            # 等待搜尋結果載入
            wait_time = search_params.get("search_button", {}).get("wait_after_click", 5)
            time.sleep(wait_time)
            
            return True
        else:
            print("未找到搜尋按鈕選擇器")
            return False
            
    except Exception as e:
        print(f"設置搜尋參數時發生錯誤: {str(e)}")
        return False


def fill_input_field(driver: webdriver.Chrome, field_config: Dict) -> bool:
    """填入輸入框的值"""
    try:
        field_value = field_config.get("default", "")
        selector = field_config.get("selector")
        description = field_config.get("description", "輸入欄位")
        
        print(f"填入{description}: {field_value}")
        
        element = driver.find_element(By.XPATH, selector)
        # 清除現有值並輸入新值
        element.clear()
        element.send_keys(field_value)
        
        return True
    except Exception as e:
        print(f"填入輸入框時發生錯誤: {str(e)}")
        return False


def select_radio_option(driver: webdriver.Chrome, radio_config: Dict) -> bool:
    """選擇單選按鈕選項"""
    try:
        option_value = radio_config.get("default")
        selector = radio_config.get("selector")
        description = radio_config.get("description", "單選選項")
        
        print(f"選擇{description}: {option_value}")
        
        # 根據預設值找到對應選項
        options = radio_config.get("options", [])
        option_selector = selector  # 預設使用基本選擇器
        
        # 如果有指定選項列表，根據值選擇對應的選擇器
        for option in options:
            if option.get("value") == option_value:
                option_selector = option.get("selector")
                break
        
        # 點擊選項
        radio_element = driver.find_element(By.XPATH, option_selector)
        return safe_click(driver, radio_element)
    
    except Exception as e:
        print(f"選擇單選按鈕選項時發生錯誤: {str(e)}")
        return False


def select_dropdown_option(driver: webdriver.Chrome, dropdown_config: Dict) -> bool:
    """選擇下拉選單選項"""
    try:
        option_value = dropdown_config.get("default")
        container_selector = dropdown_config.get("container_selector")
        description = dropdown_config.get("description", "下拉選單")
        
        print(f"選擇{description}: {option_value}")
        
        # 找到下拉選單元素
        select_element = driver.find_element(By.XPATH, container_selector)
        select_obj = Select(select_element)
        
        # 根據預設值找到對應的option值
        options = dropdown_config.get("options", [])
        option_value_to_select = None
        
        for option in options:
            if option.get("value") == option_value:
                option_value_to_select = option.get("option_value")
                break
        
        if option_value_to_select:
            select_obj.select_by_value(option_value_to_select)
        else:
            # 如果沒找到對應的option值，直接用文本選擇
            select_obj.select_by_visible_text(option_value)
        
        return True
        
    except Exception as e:
        print(f"選擇下拉選單選項時發生錯誤: {str(e)}")
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


def extract_list_items(page_source: str, config: Dict) -> List[Dict]:
    """從頁面源碼提取列表項目"""
    print("解析列表頁面...")
    tree = html.fromstring(page_source)
    
    # 從配置獲取列表容器和項目 XPath
    container_xpath = config.get("list_page", {}).get("container_xpath")
    item_xpath = config.get("list_page", {}).get("item_xpath")
    
    # 定位列表容器和項目
    containers = tree.xpath(container_xpath)
    if not containers:
        print(f"找不到列表容器: {container_xpath}")
        return []
        
    container = containers[0]
    list_items = container.xpath(item_xpath)
    print(f"找到 {len(list_items)} 個列表項目")
    
    # 獲取字段配置
    fields_config = config.get("list_page", {}).get("fields", {})
    
    results = []
    
    for i, item in enumerate(list_items):
        try:
            result = {}
            
            # 提取每個字段
            for field_name, field_config in fields_config.items():
                xpath = field_config.get("xpath")
                field_type = field_config.get("type")
                
                elements = item.xpath(xpath)
                
                # 如果找不到元素且有備用XPath
                if not elements and "fallback_xpath" in field_config:
                    elements = item.xpath(field_config.get("fallback_xpath"))
                
                if elements:
                    if field_type == "text":
                        result[field_name] = clean_text(elements[0])
                    elif field_type == "attribute":
                        attr_value = elements[0]
                        # 如果有正則表達式，從屬性值提取特定部分
                        regex_pattern = field_config.get("regex")
                        if regex_pattern:
                            match = re.search(regex_pattern, attr_value)
                            if match:
                                attr_value = match.group(1)
                        result[field_name] = attr_value
                else:
                    result[field_name] = ""
            
            # 構造詳情頁連結
            if "detail_pk" in result and result["detail_pk"]:
                pk = result["detail_pk"]
                detail_url_pattern = config.get("detail_page", {}).get("url_pattern", "")
                result["detail_url"] = detail_url_pattern.format(pk=pk)
            
            # 輸出結果
            print(f"列表項目 {i+1}: {result.get('tender_name', '')} {result.get('announcement_date', '')} {result.get('award_amount', '')}")
            results.append(result)
            
        except Exception as e:
            print(f"處理列表項目 {i+1} 時發生錯誤: {str(e)}")
    
    return results


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
    
    # 獲取配置參數
    max_pages = config.get("pagination", {}).get("max_pages", 5)  # 限制最大頁數
    
    # 處理第一頁
    print("\n--- 正在處理第 1 頁 ---")
    page_results = extract_list_items(driver.page_source, config)
    all_results.extend(page_results)
    
    # 處理後續頁面
    current_page = 1
    
    while current_page < max_pages and has_next_page(driver, config):
        # 點擊下一頁按鈕
        if not go_to_next_page(driver, config):
            print("無法前往下一頁，中止分頁處理")
            break
            
        # 等待頁面加載
        delay = config.get("delays", {}).get("page_load", 3)
        time.sleep(delay)
        
        # 更新頁碼並解析頁面
        current_page += 1
        print(f"\n--- 正在處理第 {current_page} 頁 ---")
        page_results = extract_list_items(driver.page_source, config)
        all_results.extend(page_results)
        
        # 頁面之間延遲
        delay = config.get("delays", {}).get("between_pages", 2)
        print(f"延遲 {delay} 秒後繼續...")
        time.sleep(delay)
    
    print(f"已處理共 {current_page} 頁，採集了 {len(all_results)} 筆資料")
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
    """訪問詳情頁並提取資料"""
    try:
        print(f"\n訪問詳情頁: {url}")
        driver.get(url)
        
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


def process_detail_pages(driver: webdriver.Chrome, list_results: List[Dict], config: Dict) -> List[Dict]:
    """處理詳情頁面"""
    detailed_results = []
    total_items = len(list_results)
    
    for i, item in enumerate(list_results, 1):
        detail_url = item.get("detail_url")
        if not detail_url:
            print(f"跳過項目 {i}/{total_items}：無詳情頁URL")
            detailed_results.append(item)
            continue
            
        # 獲取詳情頁數據
        print(f"處理詳情頁 {i}/{total_items}：{detail_url}")
        detail_data = extract_detail_page(driver, detail_url, config)
        
        # 將列表數據與詳情數據合併
        item_copy = item.copy()
        item_copy["detail"] = detail_data
        detailed_results.append(item_copy)
        
        # 項目間延遲
        if i < total_items:
            item_delay = config.get("delays", {}).get("between_items", 1)
            print(f"延遲 {item_delay} 秒...")
            time.sleep(item_delay)
    
    return detailed_results


# ===== 結果處理區 =====

def save_results(results: List[Dict], config: Dict) -> Optional[str]:
    """保存結果到JSON檔案"""
    if not results:
        print("沒有結果可保存")
        return None
        
    os.makedirs("output", exist_ok=True)
    
    # 使用搜尋條件作為檔名的一部分
    tender_name = config.get("search_parameters", {}).get("tender_name", {}).get("default", "")
    procurement_category = config.get("search_parameters", {}).get("procurement_category", {}).get("default", "")
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    
    filename = f"pcc_tender_{tender_name}_{procurement_category}_{timestamp}"
    # 移除特殊字符
    filename = re.sub(r'[\\/:*?"<>|]', '_', filename)
    
    output_file = f"output/{filename}.json"
    
    # 格式化結果以便 JSON 序列化
    formatted_results = format_for_json(results)
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(formatted_results, f, ensure_ascii=False, indent=2)
    
    print(f"結果已儲存至: {output_file}")
    
    # 顯示擷取結果摘要
    total_details = sum(1 for result in results if "detail" in result and result["detail"] and not isinstance(result["detail"], dict) or not "error" in result["detail"])
    print(f"共擷取 {len(results)} 筆標案記錄，成功解析 {total_details} 個詳情頁面")
    
    return output_file


def handle_error(driver: webdriver.Chrome, config: Dict, error: Exception) -> None:
    """處理錯誤並保存錯誤頁面"""
    print(f"發生錯誤: {str(error)}")
    import traceback
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
    """根據搜尋參數構建URL"""
    url_format = config.get("advanced_settings", {}).get("url_format", {})
    if not url_format:
        return config.get("search_url")
    
    pattern = url_format.get("pattern")
    if not pattern:
        return config.get("search_url")
    
    # 獲取基本URL
    search_url = config.get("search_url")
    
    # 獲取參數
    search_params = config.get("search_parameters", {})
    
    # 從搜索參數提取值
    tender_name = search_params.get("tender_name", {}).get("default", "")
    award_announce_start_date = search_params.get("award_announce_start_date", {}).get("default", "")
    award_announce_end_date = search_params.get("award_announce_end_date", {}).get("default", "")
    if search_params.get("award_announce_end_date", {}).get("use_current_date", False) and not award_announce_end_date:
        # 如果需要使用當前日期
        date_format = search_params.get("award_announce_end_date", {}).get("date_format", "yyy/MM/dd")
        award_announce_end_date = datetime.today().strftime(date_format)
    
    # 獲取採購類型
    procurement_category = search_params.get("procurement_category", {}).get("default", "")
    
    # 獲取標案狀態
    tender_status = search_params.get("tender_status", {}).get("default", "")
    
    # 獲取招標方式
    tender_way = search_params.get("tender_way", {}).get("default", "")
    
    # 從映射表獲取參數值
    param_mapping = url_format.get("parameter_mapping", {})
    value_mapping = url_format.get("value_mapping", {})
    
    # 轉換值
    if procurement_category and "procurement_category" in value_mapping:
        procurement_category_value = value_mapping["procurement_category"].get(procurement_category, "")
    else:
        procurement_category_value = procurement_category
        
    if tender_status and "tender_status" in value_mapping:
        tender_status_value = value_mapping["tender_status"].get(tender_status, "")
    else:
        tender_status_value = tender_status
        
    if tender_way and "tender_way" in value_mapping:
        tender_way_value = value_mapping["tender_way"].get(tender_way, "")
    else:
        tender_way_value = tender_way
    
    # 編碼參數
    if url_format.get("encode_parameters", False):
        tender_name = encode_url_parameter(tender_name)
        award_announce_start_date = encode_url_parameter(award_announce_start_date)
        award_announce_end_date = encode_url_parameter(award_announce_end_date)
        procurement_category_value = encode_url_parameter(procurement_category_value)
        tender_status_value = encode_url_parameter(tender_status_value)
        tender_way_value = encode_url_parameter(tender_way_value)
    
    # 構建URL
    url = pattern.format(
        search_url=search_url,
        tender_name=tender_name,
        award_announce_start_date=award_announce_start_date,
        award_announce_end_date=award_announce_end_date,
        procurement_category=procurement_category_value,
        tender_status=tender_status_value,
        tender_way=tender_way_value
    )
    
    return url


def main() -> None:
    """主函數：執行政府電子採購網爬蟲流程"""
    driver = None
    
    try:
        # 步驟1：載入配置檔案
        config_path = os.path.join(os.path.dirname(__file__), "basic_pcc_award.json")
        config = load_config(config_path)
        
        # 步驟2：設置WebDriver
        driver = setup_webdriver(config)
        
        # 執行方式選擇
        search_method = "search_form"  # 'search_form' 或 'direct_url'
        
        if search_method == "search_form":
            # 方法1：使用網站搜尋表單
            # 步驟3：開啟政府電子採購網首頁
            print(f"開啟政府電子採購網首頁...")
            driver.get(config.get("base_url"))
            
            # 等待頁面加載
            page_load_delay = config.get("delays", {}).get("page_load", 3)
            time.sleep(page_load_delay)
            
            # 步驟4：設置搜尋參數
            if not set_search_parameters(driver, config):
                print("設置搜尋參數失敗，程序終止")
                return
                
        else:
            # 方法2：直接使用構建的URL
            # 構建搜尋URL
            search_url = build_search_url(config)
            print(f"直接訪問搜尋URL: {search_url}")
            
            # 開啟搜尋結果頁面
            driver.get(search_url)
            
            # 等待頁面加載
            page_load_delay = config.get("delays", {}).get("page_load", 3)
            time.sleep(page_load_delay)
        
        # 步驟5：處理列表頁面和分頁
        list_results = process_pagination(driver, config)
        
        # 步驟6：處理詳情頁面
        process_details = True  # 設置為False可以跳過詳情頁處理
        
        if process_details and list_results:
            detailed_results = process_detail_pages(driver, list_results, config)
        else:
            detailed_results = list_results
        
        # 步驟7：保存結果
        if detailed_results:
            save_results(detailed_results, config)
        else:
            print("沒有找到符合條件的資料")
        
        # 完成
        print(f"完成爬取，共 {len(detailed_results)} 筆標案資料")
        finish_delay = config.get("delays", {}).get("finish", 3)
        print(f"暫停 {finish_delay} 秒...")
        time.sleep(finish_delay)
        
    except TimeoutException:
        print("載入頁面逾時，請檢查網路連線或網站可用性")
    except Exception as e:
        handle_error(driver, config, e)
    finally:
        # 清理資源
        if driver:
            print("關閉瀏覽器...")
            driver.quit()
        
        print("爬蟲程序已完成")


if __name__ == "__main__":
    main()