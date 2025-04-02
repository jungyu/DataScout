"""
政府電子採購網-招標公告查詢爬蟲程式
基於配置文件的政府電子採購網資料爬取工具
支援標案名稱、招標日期範圍、採購性質等條件搜尋
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
    """將對象轉換為JSON可序列化格式"""
    if isinstance(obj, dict):
        return {k: format_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [format_for_json(item) for item in obj]
    elif isinstance(obj, datetime):
        return obj.strftime("%Y-%m-%d %H:%M:%S")
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
    """載入配置文件"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            # 移除JSON註解行
            content = ''.join(line for line in f if not line.strip().startswith('//'))
            return json.loads(content)
    except Exception as e:
        print(f"載入配置文件失敗: {str(e)}")
        return {}


# ===== 瀏覽器控制區 =====

def setup_webdriver(config: Dict) -> webdriver.Chrome:
    """設置WebDriver"""
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # 根據配置設置User-Agent
    user_agent = config.get("request", {}).get("headers", {}).get("User-Agent")
    if user_agent:
        options.add_argument(f'user-agent={user_agent}')
    
    driver = webdriver.Chrome(options=options)
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
            
        # 2. 填入招標公告開始日期
        start_date_config = search_params.get("tender_start_date", {})
        if start_date_config:
            fill_input_field(driver, start_date_config)
            
        # 3. 填入招標公告結束日期 (可能使用當前日期)
        end_date_config = search_params.get("tender_end_date", {})
        if end_date_config:
            if end_date_config.get("use_current_date", False):
                # 如果需要使用當前日期
                today = datetime.today().strftime(end_date_config.get("date_format", "yyy/MM/dd"))
                end_date_config["default"] = today
                
            fill_input_field(driver, end_date_config)
            
        # 4. 填入機關代碼 (如果有)
        org_id_config = search_params.get("organization_id", {})
        if org_id_config and org_id_config.get("default"):
            fill_input_field(driver, org_id_config)
            
        # 5. 填入機關名稱 (如果有)
        org_name_config = search_params.get("organization_name", {})
        if org_name_config and org_name_config.get("default"):
            fill_input_field(driver, org_name_config)
            
        # 6. 選擇日期類型 (單選)
        date_type_config = search_params.get("date_type", {})
        if date_type_config:
            select_radio_option(driver, date_type_config)
            
        # 7. 選擇採購性質 (單選)
        procurement_category_config = search_params.get("procurement_category", {})
        if procurement_category_config:
            select_radio_option(driver, procurement_category_config)
            
        # 8. 選擇標案狀態/招標類型 (下拉選單)
        tender_type_config = search_params.get("tender_type", {})
        if tender_type_config:
            select_dropdown_option(driver, tender_type_config)
            
        # 9. 選擇招標方式 (下拉選單)
        tender_way_config = search_params.get("tender_way", {})
        if tender_way_config:
            select_dropdown_option(driver, tender_way_config)
            
        # 10. 點擊搜尋按鈕
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
            
            # 構造詳情頁連結 - 修正為新的URL格式
            if "detail_pk" in result and result["detail_pk"]:
                pk = result["detail_pk"]
                detail_url_pattern = config.get("detail_page", {}).get("url_pattern", "")
                result["detail_url"] = detail_url_pattern.format(pk=pk)
            
            # 輸出結果預覽
            print(f"列表項目 {i+1}: {result.get('tender_case_no', '')} - {result.get('tender_name', '')}")
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
        
        # 解析頁面
        page_source = driver.page_source
        return extract_detail_page_data(page_source, config)
        
    except Exception as e:
        print(f"提取詳情頁時出錯: {e}")
        return {"error": str(e)}


def extract_detail_page_data(page_source: str, config: Dict) -> Dict:
    """從詳情頁面提取數據"""
    print("解析詳情頁面...")
    tree = html.fromstring(page_source)
    
    # 從配置獲取字段定義
    fields_config = config.get("detail_page", {}).get("fields", {})
    
    result = {}
    
    # 提取每個字段
    for field_name, field_config in fields_config.items():
        try:
            xpath = field_config.get("xpath")
            field_type = field_config.get("type", "text")
            regex_pattern = field_config.get("regex")
            description = field_config.get("description", field_name)
            
            elements = tree.xpath(xpath)
            
            if elements:
                if field_type == "text":
                    # 特殊處理機關地址
                    if field_name == "organization_address":
                        # 合併所有地址部分
                        address_parts = []
                        raw_parts = tree.xpath("//td[contains(text(), '機關地址')]/following-sibling::td[1]//text()[normalize-space()]")
                        for part in raw_parts:
                            part = part.strip()
                            if part:
                                address_parts.append(part)
                        value = ' '.join(address_parts)
                    # 特殊處理聯絡電話
                    elif field_name == "contact_phone":
                        phone_parts = []
                        raw_parts = tree.xpath("//td[contains(text(), '聯絡電話')]/following-sibling::td[1]//text()[normalize-space()]")
                        for part in raw_parts:
                            part = part.strip()
                            if part:
                                phone_parts.append(part)
                        value = ''.join(phone_parts)
                    # 特殊處理標的分類
                    elif field_name == "subject_category":
                        category_parts = []
                        raw_parts = tree.xpath("//td[contains(text(), '標的分類')]/following-sibling::td[1]//text()[normalize-space()]")
                        for part in raw_parts:
                            part = part.strip()
                            if part:
                                category_parts.append(part)
                        value = ' '.join(category_parts)
                    # 特殊處理開標時間
                    elif field_name == "bid_opening_date":
                        # 一般情況下使用span[@id='opdt']，但它可能是隱藏的
                        bid_time = tree.xpath("//td[contains(text(), '開標時間')]/following-sibling::td[1]/text()[normalize-space()]")
                        if bid_time:
                            value = clean_text(bid_time[0])
                        else:
                            value = ""
                    # 特殊處理押標金相關字段
                    elif field_name == "bid_deposit_required":
                        value = clean_text(elements[0])
                    elif field_name == "bid_deposit_amount":
                        deposit_text = tree.xpath("//td[contains(text(), '是否須繳納押標金')]/following-sibling::td[1]//div[contains(text(), '押標金額度')]/text()")
                        if deposit_text:
                            value = clean_text(deposit_text[0])
                        else:
                            value = ""
                    else:
                        value = clean_text(elements[0])
                    
                    # 如果有正則表達式，應用它
                    if regex_pattern and value:
                        match = re.search(regex_pattern, value)
                        if match:
                            value = match.group(1)
                    
                    result[field_name] = value
                    print(f"提取 {description}: {value[:50]}{'...' if len(value) > 50 else ''}")
                elif field_type == "attribute":
                    attr_value = elements[0]
                    # 如果有正則表達式，從屬性值提取特定部分
                    if regex_pattern:
                        match = re.search(regex_pattern, attr_value)
                        if match:
                            attr_value = match.group(1)
                    result[field_name] = attr_value
                    print(f"提取 {description}: {attr_value[:50]}{'...' if len(attr_value) > 50 else ''}")
            else:
                result[field_name] = ""
                print(f"未找到字段 {description}")
        except Exception as e:
            print(f"提取字段 {field_name} 時發生錯誤: {str(e)}")
            result[field_name] = ""
    
    return result


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
    # 獲取基本URL
    search_url = config.get("search_url")
    
    # 獲取參數
    search_params = config.get("search_parameters", {})
    
    # ===== 從搜索參數提取值 =====
    # 基本參數
    tender_name = search_params.get("tender_name", {}).get("default", "")
    organization_name = search_params.get("organization_name", {}).get("default", "")
    organization_id = search_params.get("organization_id", {}).get("default", "")
    
    # ===== 日期參數 =====
    tender_start_date = search_params.get("tender_start_date", {}).get("default", "")
    tender_end_date = search_params.get("tender_end_date", {}).get("default", "")
    if search_params.get("tender_end_date", {}).get("use_current_date", False) and not tender_end_date:
        date_format = search_params.get("tender_end_date", {}).get("date_format", "yyy/MM/dd")
        tender_end_date = datetime.today().strftime(date_format)
    
    # ===== 日期類型參數 =====
    # 從配置檔獲取正確的選項值
    date_type_config = search_params.get("date_type", {})
    date_type = "isSpdt"  # 預設使用等標期內
    
    if date_type_config:
        date_type_value = date_type_config.get("default", "等標期內")
        options = date_type_config.get("options", [])
        for option in options:
            if option.get("value") == date_type_value:
                date_type = option.get("option_value", "isSpdt")
                break
    
    # ===== 採購性質參數 =====
    procurement_category = search_params.get("procurement_category", {}).get("default", "")
    procurement_category_value = ""
    
    if procurement_category:
        options = search_params.get("procurement_category", {}).get("options", [])
        for option in options:
            if option.get("value") == procurement_category:
                procurement_category_value = option.get("option_value", "")
                break
    
    # ===== 招標類型與方式參數 =====
    # 1. 招標類型
    tender_type = search_params.get("tender_type", {}).get("default", "招標公告")
    tender_type_value = "TENDER_DECLARATION"  # 預設值
    
    if tender_type:
        options = search_params.get("tender_type", {}).get("options", [])
        for option in options:
            if option.get("value") == tender_type:
                tender_type_value = option.get("option_value", "TENDER_DECLARATION")
                break
    
    # 2. 招標方式
    tender_way = search_params.get("tender_way", {}).get("default", "公開招標")
    tender_way_value = "TENDER_WAY_1"  # 預設值
    
    if tender_way:
        options = search_params.get("tender_way", {}).get("options", [])
        for option in options:
            if option.get("value") == tender_way:
                tender_way_value = option.get("option_value", "TENDER_WAY_1")
                break
    
    # ===== URL參數編碼 =====
    tender_name = urllib.parse.quote(tender_name)
    organization_name = urllib.parse.quote(organization_name)
    organization_id = urllib.parse.quote(organization_id)
    tender_start_date = urllib.parse.quote(tender_start_date)
    tender_end_date = urllib.parse.quote(tender_end_date)
    
    # ===== 構建完整URL =====
    url = f"{search_url}?pageSize=50&firstSearch=true&searchType=basic&isBinding=N&isLogIn=N&level_1=on" \
          f"&orgName={organization_name}&orgId={organization_id}&tenderName={tender_name}&tenderId=" \
          f"&tenderType={tender_type_value}&tenderWay={tender_way_value}" \
          f"&dateType={date_type}&tenderStartDate={tender_start_date}&tenderEndDate={tender_end_date}" \
          f"&radProctrgCate={procurement_category_value}&policyAdvocacy="
    
    print(f"構建的搜尋URL: {url}")
    return url


def main() -> None:
    """主函數：執行政府電子採購網爬蟲流程"""
    driver = None
    
    try:
        # 步驟1：載入配置檔案
        config_path = os.path.join(os.path.dirname(__file__), "basic_pcc_tender.json")
        config = load_config(config_path)
        
        # 步驟2：設置WebDriver
        driver = setup_webdriver(config)
        
        # 執行方式選擇
        search_method = "direct_url" # 改為使用直接URL方式
        
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