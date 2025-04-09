"""
實價登錄爬蟲程式
基於配置文件的實價登錄網站資料爬取工具
支持縣市、鄉鎮區和建物型態選擇，URL參數式分頁
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


def normalize_url(url: str, base_domain: str = "https://price.houseprice.tw") -> str:
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
    """設置搜尋參數：縣市、鄉鎮區和建物型態"""
    try:
        print("\n設置搜尋參數...")
        search_params = config.get("search_parameters", {})
        
        # 1. 選擇縣市
        if not select_city(driver, search_params):
            print("縣市選擇失敗")
            return False
            
        # 2. 選擇鄉鎮區
        if not select_district(driver, search_params):
            print("鄉鎮區選擇失敗")
            return False
            
        # 3. 選擇建物型態
        if not select_building_type(driver, search_params):
            print("建物型態選擇失敗")
            return False
        
        # 4. 點擊搜尋按鈕
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


def select_city(driver: webdriver.Chrome, search_params: Dict) -> bool:
    """選擇縣市"""
    try:
        city_config = search_params.get("city", {})
        city_value = city_config.get("default")
        
        print(f"選擇縣市: {city_value}")
        
        # 1. 點擊打開縣市選擇框
        open_selector = city_config.get("open_selector")
        if open_selector:
            city_dropdown = driver.find_element(By.XPATH, open_selector)
            safe_click(driver, city_dropdown)
            time.sleep(1)  # 等待下拉框展開
        
        # 2. 選擇指定縣市
        option_selector = city_config.get("option_selector").replace("{value}", city_value)
        city_option = driver.find_element(By.XPATH, option_selector)
        safe_click(driver, city_option)
        time.sleep(2)  # 等待縣市選擇生效
        
        return True
        
    except Exception as e:
        print(f"選擇縣市時發生錯誤: {str(e)}")
        return False


def select_district(driver: webdriver.Chrome, search_params: Dict) -> bool:
    """選擇鄉鎮區"""
    try:
        district_config = search_params.get("district", {})
        district_value = district_config.get("default")
        
        print(f"選擇鄉鎮區: {district_value}")
        
        # 檢查鄉鎮區選擇區域是否已顯示
        if district_config.get("wait_after_city", False):
            # 等待鄉鎮區選擇區域顯示
            container_selector = district_config.get("container_selector")
            wait_for_element(driver, By.XPATH, container_selector)
            time.sleep(1)
        
        # 選擇指定鄉鎮區
        option_selector = district_config.get("option_selector").replace("{value}", district_value)
        district_option = driver.find_element(By.XPATH, option_selector)
        safe_click(driver, district_option)
        time.sleep(1)  # 等待鄉鎮區選擇生效
        
        return True
        
    except Exception as e:
        print(f"選擇鄉鎮區時發生錯誤: {str(e)}")
        return False


def select_building_type(driver: webdriver.Chrome, search_params: Dict) -> bool:
    """選擇建物型態"""
    try:
        building_type_config = search_params.get("building_type", {})
        building_type_value = building_type_config.get("default")
        
        print(f"選擇建物型態: {building_type_value}")
        
        # 1. 點擊打開建物型態選擇框
        open_selector = building_type_config.get("open_selector")
        if open_selector:
            building_dropdown = driver.find_element(By.XPATH, open_selector)
            safe_click(driver, building_dropdown)
            time.sleep(1)  # 等待下拉框展開
        
        # 2. 選擇指定建物型態
        option_selector = building_type_config.get("option_selector").replace("{value}", building_type_value)
        building_option = driver.find_element(By.XPATH, option_selector)
        safe_click(driver, building_option)
        time.sleep(1)  # 等待建物型態選擇生效
        
        return True
        
    except Exception as e:
        print(f"選擇建物型態時發生錯誤: {str(e)}")
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
            text_content = " ".join([e.text_content() for e in elements if e.text_content()])
            matches = re.search(r'共\s*(\d+)\s*筆', text_content)
            if matches:
                return int(matches.group(1))
        
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
            
            # 提取 data-sid 屬性 (詳情頁關鍵)
            data_sid = item.get("data-sid")
            if data_sid:
                result["detail_link"] = data_sid
                result["detail_url"] = config.get("detail_page", {}).get("url_pattern", "").format(sid=data_sid)
            
            # 提取每個字段
            for field_name, field_config in fields_config.items():
                # 跳過已處理的 detail_link 字段
                if field_name == "detail_link" and "detail_link" in result:
                    continue
                    
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
                        result[field_name] = elements[0]
                else:
                    result[field_name] = ""
            
            # 輸出結果
            print(f"列表項目 {i+1}: {result.get('transaction_date', '')} {result.get('address', '')} {result.get('total', '')}萬元")
            results.append(result)
            
        except Exception as e:
            print(f"處理列表項目 {i+1} 時發生錯誤: {str(e)}")
    
    return results


# ===== 分頁控制區 =====

def calculate_total_pages(total_records: int, items_per_page: int) -> int:
    """計算總頁數"""
    if total_records <= 0 or items_per_page <= 0:
        return 1
    return (total_records + items_per_page - 1) // items_per_page


def generate_page_url(base_url: str, page_number: int) -> str:
    """生成分頁URL"""
    if '?' in base_url:
        # 已經有其他參數
        if 'p=' in base_url:
            # 已經有頁碼參數，替換它
            return re.sub(r'p=\d+', f'p={page_number}', base_url)
        else:
            # 添加頁碼參數
            return f"{base_url}&p={page_number}"
    else:
        # 沒有其他參數
        return f"{base_url}?p={page_number}"


def process_pagination(driver: webdriver.Chrome, config: Dict, base_url: str) -> List[Dict]:
    """處理分頁爬取"""
    all_results = []
    
    # 獲取配置參數
    items_per_page = config.get("pagination", {}).get("items_per_page", 20)
    max_pages = min(config.get("pagination", {}).get("max_pages", 5), 10)  # 限制最大頁數
    
    # 獲取總記錄數
    total_records = get_total_records_count(driver, config)
    if total_records <= 0:
        print("未找到總記錄數，僅處理當前頁面")
        # 解析當前頁面
        return extract_list_items(driver.page_source, config)
    
    # 計算總頁數
    total_pages = calculate_total_pages(total_records, items_per_page)
    print(f"共找到 {total_records} 筆記錄，每頁 {items_per_page} 筆，共 {total_pages} 頁")
    
    # 限制實際處理的頁數
    pages_to_process = min(total_pages, max_pages)
    print(f"根據配置將處理 {pages_to_process} 頁")
    
    # 處理每一頁
    for page in range(1, pages_to_process + 1):
        print(f"\n--- 正在處理第 {page}/{pages_to_process} 頁 ---")
        
        if page > 1:
            # 生成並訪問分頁URL
            page_url = generate_page_url(base_url, page)
            print(f"訪問頁面: {page_url}")
            driver.get(page_url)
            
            # 等待頁面加載
            page_load_delay = config.get("delays", {}).get("page_load", 3)
            time.sleep(page_load_delay)
        
        # 解析當前頁面
        page_results = extract_list_items(driver.page_source, config)
        all_results.extend(page_results)
        
        # 頁面之間延遲
        if page < pages_to_process:
            delay = config.get("delays", {}).get("between_pages", 2)
            print(f"延遲 {delay} 秒後繼續...")
            time.sleep(delay)
    
    return all_results


# ===== 詳情頁面處理區 =====

def extract_detail_page(driver: webdriver.Chrome, url: str, config: Dict) -> Dict[str, Any]:
    """訪問詳情頁並提取元數據"""
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
                
                # 從容器中提取元素
                elements = container.xpath(xpath)
                
                if elements:
                    if field_type == "text":
                        result[field_name] = clean_text(elements[0])
                    elif field_type == "attribute":
                        result[field_name] = elements[0]
                    elif field_type == "html":
                        # 提取元素的HTML內容
                        html_content = "".join([html.tostring(el, encoding='unicode') for el in elements])
                        result[field_name] = clean_text(html_content)
                
                # 輸出結果預覽
                if field_name in result:
                    print(f"  提取 {field_config.get('description', field_name)}: {result[field_name]}")
            
            except Exception as e:
                print(f"  提取字段 '{field_name}' 時出錯: {e}")
                result[field_name] = None
        
        print(f"已提取 {len(result)} 個詳情字段")
        return result
        
    except Exception as e:
        print(f"提取詳情頁時出錯: {e}")
        return {"error": str(e)}


def process_detail_pages(driver: webdriver.Chrome, list_results: List[Dict], config: Dict) -> List[Dict]:
    """處理詳情頁面"""
    detailed_results = []
    total_items = len(list_results)
    
    for i, result in enumerate(list_results, 1):
        detail_url = result.get("detail_url")
        if not detail_url:
            print(f"跳過項目 {i}/{total_items}：無詳情頁URL")
            detailed_results.append(result)
            continue
            
        # 獲取詳情頁數據
        print(f"處理詳情頁 {i}/{total_items}：{detail_url}")
        detail_data = extract_detail_page(driver, detail_url, config)
        
        # 合併列表結果和詳情頁數據
        result["detail"] = detail_data
        detailed_results.append(result)
        
        # 項目間延遲
        if i < total_items:
            item_delay = config.get("delays", {}).get("between_items", 0.5)
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
    
    # 使用縣市和鄉鎮區資訊作為檔名的一部分
    city = config.get("search_parameters", {}).get("city", {}).get("default", "")
    district = config.get("search_parameters", {}).get("district", {}).get("default", "")
    building_type = config.get("search_parameters", {}).get("building_type", {}).get("default", "")
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    
    filename = f"{city}_{district}_{building_type}_{timestamp}"
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
    print(f"共擷取 {len(results)} 筆交易記錄，成功解析 {total_details} 個詳情頁面")
    
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
        return config.get("base_url")
    
    pattern = url_format.get("pattern")
    if not pattern:
        return config.get("base_url")
    
    # 獲取參數
    base_url = config.get("base_url")
    city = config.get("search_parameters", {}).get("city", {}).get("default", "")
    district = config.get("search_parameters", {}).get("district", {}).get("default", "")
    building_type_value = config.get("search_parameters", {}).get("building_type", {}).get("default", "")
    
    # 獲取建物類型URL參數映射
    building_type_mapping = url_format.get("building_type_mapping", {})
    building_type_param = building_type_mapping.get(building_type_value, "")
    
    # 如果需要編碼參數
    if url_format.get("encode_parameters", False):
        city = encode_url_parameter(city)
        district = encode_url_parameter(district)
        if building_type_param:
            building_type_param = encode_url_parameter(building_type_param)
    
    # 構建URL
    url = pattern.format(
        base_url=base_url,
        city=city,
        district=district,
        building_type_param=building_type_param
    )
    
    # 移除多餘的斜線
    url = re.sub(r'([^:])//+', r'\1/', url)
    
    return url


def main() -> None:
    """主函數：執行實價登錄爬蟲流程"""
    driver = None
    
    try:
        # 步驟1：載入配置檔案
        config_path = "../../../config/price_house/basic/query.json"
        config = load_config(config_path)
        
        # 步驟2：設置WebDriver
        driver = setup_webdriver(config)
        
        # 執行方式選擇
        search_method = "direct_url"  # 'search_form' 或 'direct_url'
        
        if search_method == "search_form":
            # 方法1：使用網站搜尋表單
            # 步驟3：開啟實價登錄首頁
            print(f"開啟實價登錄首頁...")
            driver.get(config.get("base_url"))
            
            # 等待頁面加載
            page_load_delay = config.get("delays", {}).get("page_load", 3)
            time.sleep(page_load_delay)
            
            # 步驟4：設置搜尋參數
            if not set_search_parameters(driver, config):
                print("設置搜尋參數失敗，程序終止")
                return
                
            # 獲取當前URL作為基礎URL
            current_url = driver.current_url
            
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
            
            # 獲取當前URL作為基礎URL
            current_url = driver.current_url
        
        # 步驟5：處理列表頁面和分頁
        list_results = process_pagination(driver, config, current_url)
        
        # 步驟6：處理詳情頁面 (可選)
        process_details = True  # 設置為False可以跳過詳情頁處理
        
        if process_details:
            detailed_results = process_detail_pages(driver, list_results, config)
        else:
            detailed_results = list_results
        
        # 步驟7：保存結果
        save_results(detailed_results, config)
        
        # 完成
        print(f"完成爬取，共 {len(detailed_results)} 筆實價登錄資料")
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