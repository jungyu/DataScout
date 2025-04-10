"""
政府電子採購網-決標公告查詢爬蟲程式
基於配置文件的政府電子採購網決標資料爬取工具
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

def build_search_url(config: Dict, params: Dict = None) -> str:
    """構建搜尋 URL"""
    base_url = config.get("search_url")
    url_format = config.get("advanced_settings", {}).get("url_format", {})
    pattern = url_format.get("pattern", "")
    
    # 準備參數
    search_params = {
        "orgName": "",
        "orgId": "",
        "tenderName": config.get("search_parameters", {}).get("tenderName", {}).get("default", ""),
        "tenderId": "",
        "tenderStatus": "TENDER_STATUS_1",  # 決標公告
        "tenderWay": "TENDER_WAY_1",  # 公開招標
        "awardAnnounceStartDate": config.get("search_parameters", {}).get("awardAnnounceStartDate", {}).get("default", ""),
        "awardAnnounceEndDate": config.get("search_parameters", {}).get("awardAnnounceEndDate", {}).get("default", ""),
        "radProctrgCate": "",
        "tenderRange": "TENDER_RANGE_ALL",
        "pageSize": "100",
        "firstSearch": "true",
        "isQuery": "true",
        "isBinding": "N",
        "isLogIn": "N"
    }
    
    if params:
        search_params.update(params)
    
    # 使用 pattern 格式化 URL
    try:
        if pattern:
            url = pattern.format(**search_params)
        else:
            # 如果沒有pattern，則基於 base_url 和 search_params 構建 URL
            url = f"{base_url}?{urlencode(search_params)}"
            
        # 處理參數編碼
        if url_format.get("encode_parameters", True):
            parsed = urllib.parse.urlparse(url)
            query = urllib.parse.parse_qs(parsed.query)
            encoded_query = {k: encode_url_parameter(v[0]) for k, v in query.items()}
            url = urllib.parse.urlunparse((
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                parsed.params,
                urllib.parse.urlencode(encoded_query),
                parsed.fragment
            ))
        return url
    except Exception as e:
        print(f"構建搜尋 URL 時發生錯誤: {str(e)}")
        return base_url


def execute_search(driver: webdriver.Chrome, config: Dict) -> bool:
    """執行搜尋"""
    try:
        print("\n開始執行搜尋...")
        search_url = build_search_url(config)
        print(f"訪問列表頁面: {search_url}")
        
        driver.get(search_url)
        time.sleep(config.get("delays", {}).get("page_load", 3))
        
        return True
    except Exception as e:
        print(f"執行搜尋時發生錯誤: {str(e)}")
        return False


def extract_list_items(driver: webdriver.Chrome, config: Dict) -> List[Dict]:
    """提取列表頁面的項目"""
    print("\n開始提取列表項目...")
    
    items = []
    list_items = driver.find_elements(By.XPATH, config["list_page"]["container"])
    print(f"找到 {len(list_items)} 個列表項目")
    
    for i, item in enumerate(list_items, 1):
        print(f"\n處理第 {i} 個項目")
        item_data = {}
        
        # 提取詳細頁面主鍵
        try:
            pk_config = config["list_page"]["fields"]["detail_pk"]
            
            # 修正 XPath，去除 @href 部分
            xpath = pk_config["xpath"]
            if "@href" in xpath:
                element_xpath = xpath.split("/@")[0]  # 取得元素部分的 XPath
                element = item.find_element(By.XPATH, element_xpath)
            else:
                element = item.find_element(By.XPATH, xpath)
                
            # 獲取 href 屬性
            href = element.get_attribute("href") if element else None
            
            if href and "extract_pattern" in pk_config:
                match = re.search(pk_config["extract_pattern"], href)
                if match:
                    item_data["detail_pk"] = match.group(1)
                    print(f"  提取到 detail_pk: {item_data['detail_pk']}")
                else:
                    # 嘗試尋找 pkAtmMain 參數，這是決標公告的主鍵格式
                    match = re.search(r'pkAtmMain=([A-Za-z0-9+/=]+)', href)
                    if match:
                        item_data["detail_pk"] = match.group(1)
                        print(f"  提取到 pkAtmMain: {item_data['detail_pk']}")
                    else:
                        print(f"  無法從 href 中提取 detail_pk 或 pkAtmMain: {href}")
            else:
                print(f"  無法獲取有效的 href 或缺少 extract_pattern")
        except Exception as e:
            print(f"  提取 detail_pk 時發生錯誤: {str(e)}")
        
        if "detail_pk" in item_data:  # 只有成功提取 detail_pk 才添加項目
            items.append(item_data)
            print(f"  成功添加第 {i} 個項目")
    
    return items


def has_next_page(driver: webdriver.Chrome, config: Dict) -> bool:
    """檢查是否有下一頁"""
    try:
        next_button_xpath = config.get("pagination", {}).get("next_button_xpath")
        if not next_button_xpath:
            return False
            
        next_button = driver.find_elements(By.XPATH, next_button_xpath)
        return len(next_button) > 0
        
    except Exception as e:
        print(f"檢查下一頁時發生錯誤: {str(e)}")
        return False


def go_to_next_page(driver: webdriver.Chrome, config: Dict) -> bool:
    """前往下一頁"""
    try:
        next_button_xpath = config.get("pagination", {}).get("next_button_xpath")
        if not next_button_xpath:
            return False
            
        next_button = wait_for_element_clickable(driver, By.XPATH, next_button_xpath, timeout=10)
        if not next_button:
            return False
            
        # 使用安全點擊
        if not safe_click(driver, next_button):
            return False
            
        # 等待頁面加載
        time.sleep(config.get("delays", {}).get("between_pages", 2))
        
        return True
        
    except Exception as e:
        print(f"前往下一頁時發生錯誤: {str(e)}")
        return False


def process_pagination(driver: webdriver.Chrome, config: Dict) -> List[Dict]:
    """處理分頁"""
    try:
        all_results = []
        max_pages = config.get("pagination", {}).get("max_pages", 1)  # 預設為 1 頁
        current_page = 1
        
        print(f"\n開始處理分頁，最大頁數限制: {max_pages}")
        
        while True:  # 改用 while True 配合 break 條件
            print(f"\n處理第 {current_page} 頁")
            
            # 提取當前頁面的項目
            page_results = extract_list_items(driver, config)
            if not page_results:
                print("當前頁面沒有結果")
                break
                
            all_results.extend(page_results)
            print(f"已收集 {len(all_results)} 個結果")
            
            # 檢查是否達到最大頁數限制
            if current_page >= max_pages:
                print(f"已達到最大頁數限制 ({max_pages} 頁)")
                break
                
            # 檢查是否有下一頁
            if not has_next_page(driver, config):
                print("沒有下一頁")
                break
                
            # 前往下一頁
            if not go_to_next_page(driver, config):
                print("前往下一頁失敗")
                break
                
            current_page += 1
            
        print(f"\n分頁處理完成，共處理 {current_page} 頁")
        return all_results
        
    except Exception as e:
        print(f"處理分頁時發生錯誤: {str(e)}")
        traceback.print_exc()
        return []


def process_detail_pages(driver: webdriver.Chrome, items: List[Dict], config: Dict) -> List[Dict]:
    """處理詳細頁面"""
    print("\n開始處理詳細頁面...")
    
    for i, item in enumerate(items):
        try:
            # 獲取詳細頁面 pk
            pk = item.get('detail_pk')
            if not pk:
                print(f"項目 {i+1} 無詳細頁面主鍵，跳過處理")
                continue
            
            # 構建詳細頁面 URL
            detail_url = config["detail_page"]["url_pattern"].format(pk=pk)
            
            # 訪問詳細頁面
            print(f"\n處理第 {i+1} 個詳細頁面: {detail_url}")
            driver.get(detail_url)
            time.sleep(config.get("delays", {}).get("page_load", 3))
            
            # 初始化詳細頁面資料結構（根據award.json配置）
            item_data = {
                "機關資料": {},
                "已公告資料": {},
                "投標廠商": {},
                "決標品項": {},
                "決標資料": {}
            }
            
            # 提取各個分類的資料
            for category in item_data.keys():
                if category in config.get("detail_page", {}).get("fields", {}):
                    for field_name, field_config in config["detail_page"]["fields"][category].items():
                        try:
                            xpath = field_config.get("xpath")
                            if not xpath:
                                continue
                                
                            elements = driver.find_elements(By.XPATH, xpath)
                            if not elements:
                                print(f"  無法找到欄位 {category}/{field_name} 的元素")
                                continue
                                
                            # 取得元素文本
                            value = clean_text(elements[0].text)
                            item_data[category][field_name] = value
                            print(f"  成功提取 {category}/{field_name}: {value}")
                            
                        except Exception as e:
                            print(f"  提取欄位 {category}/{field_name} 時發生錯誤: {str(e)}")
                            item_data[category][field_name] = None
            
            # 更新原始項目資料
            item.update(item_data)
            print(f"完成第 {i+1} 個詳細頁面處理")
            
        except Exception as e:
            print(f"處理第 {i+1} 個詳細頁面時發生錯誤: {str(e)}")
            traceback.print_exc()
            continue
            
    return items


def save_results(results: List[Dict], output_path: str) -> Optional[str]:
    """保存結果到文件"""
    try:
        # 確保目錄存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 格式化數據
        formatted_results = format_for_json(results)
        
        # 保存為JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(formatted_results, f, ensure_ascii=False, indent=2)
            
        print(f"結果已保存到: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"保存結果時發生錯誤: {str(e)}")
        return None


def handle_error(driver: webdriver.Chrome, config: Dict, error: Exception) -> None:
    """處理錯誤"""
    try:
        # 保存錯誤頁面
        if config.get("advanced_settings", {}).get("save_error_page", False):
            error_page_dir = config.get("advanced_settings", {}).get("error_page_dir", "error_pages")
            os.makedirs(error_page_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            error_page_path = os.path.join(error_page_dir, f"error_page_{timestamp}.html")
            
            with open(error_page_path, 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
                
            print(f"錯誤頁面已保存到: {error_page_path}")
            
    except Exception as e:
        print(f"處理錯誤時發生錯誤: {str(e)}")


def main():
    """主函數"""
    driver = None
    try:
        print("開始執行程式...")
        
        # 載入配置
        config_path = "examples/config/pcc/basic/award.json"
        print(f"載入配置文件: {config_path}")
        config = load_config(config_path)
        
        # 檢查必要的配置
        required_configs = ["search_url", "list_page", "detail_page"]
        for config_name in required_configs:
            if config_name not in config:
                print(f"錯誤：缺少必要的配置項 {config_name}")
                return
                
        # 設置WebDriver
        print("初始化 WebDriver...")
        driver = setup_webdriver(config)
        
        try:
            # 執行搜尋
            print("\n開始執行搜尋...")
            if not execute_search(driver, config):
                print("執行搜尋失敗")
                return
            
            # 處理分頁
            print("\n開始處理分頁...")
            results = process_pagination(driver, config)
            if not results:
                print("沒有找到結果")
                return
            
            print(f"\n共找到 {len(results)} 個結果")
            
            # 處理詳細頁面
            if config.get("detail_page", {}).get("enabled", True):
                results = process_detail_pages(driver, results, config)
                print(f"成功處理 {len(results)} 個詳細頁面")
            else:
                print("跳過處理詳細頁面（已在配置中禁用）")
            
            # 保存結果
            output_path = config.get("output", {}).get("path", "examples/data/output/award_results.json")
            if save_results(results, output_path):
                print("程式執行完成")
            else:
                print("保存結果失敗")
            
        except Exception as e:
            print(f"處理過程中發生錯誤: {str(e)}")
            traceback.print_exc()
            if driver:
                handle_error(driver, config, e)
            
        finally:
            # 關閉瀏覽器
            if driver:
                print("\n關閉瀏覽器...")
                driver.quit()
            
    except Exception as e:
        print(f"程式初始化時發生錯誤: {str(e)}")
        traceback.print_exc()
        if driver:
            handle_error(driver, config, e)
            driver.quit()


if __name__ == "__main__":
    main()