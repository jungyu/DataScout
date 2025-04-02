"""
基於 JSON 配置的 Google 搜尋爬蟲範例，專門針對公視新聞網站內容提取
此範例展示如何從 JSON 配置檔案獲取參數並使用 lxml 進行 XPath 解析
"""

import os
import re
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Union

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from lxml import html


# ===== 工具函數區 =====

def remove_tags(text: str) -> str:
    """清空字串內全部的 html tag，只留下內文"""
    TAG_RE = re.compile(r'<[^>]+>')
    return TAG_RE.sub('', text) if text else ""

def clean_text(text: str) -> str:
    """清理多餘空白字元"""
    if not text:
        return ""
    # 移除多餘空格、換行和 tabs
    text = re.sub(r'\s+', ' ', text)
    # 移除前後空格
    return text.strip()

def clean_html(html_content: str, extraction_settings: Dict) -> str:
    """根據設置清理HTML內容"""
    if extraction_settings.get("clean_html", False):
        # 移除 <script> 和 <style> 標籤
        if extraction_settings.get("remove_scripts", False):
            html_content = re.sub(r'<script.*?</script>', '', html_content, flags=re.DOTALL)
            html_content = re.sub(r'<style.*?</style>', '', html_content, flags=re.DOTALL)
        
        # 移除註釋
        html_content = re.sub(r'<!--.*?-->', '', html_content, flags=re.DOTALL)
        
        # 移除廣告
        if extraction_settings.get("remove_ads", False):
            html_content = re.sub(r'<div[^>]*class=[^>]*ad[s]?[^>]*>.*?</div>', '', html_content, flags=re.DOTALL)
    
    return html_content

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

def parse_date(date_str: str) -> Optional[str]:
    """解析各種格式的日期字符串為 ISO 格式"""
    # ISO 格式不需要處理
    if re.match(r'\d{4}-\d{2}-\d{2}T', date_str):
        return date_str
        
    # 嘗試各種可能的日期格式
    patterns = [
        "%Y-%m-%d %H:%M:%S", 
        "%Y/%m/%d %H:%M:%S",
        "%Y年%m月%d日 %H:%M", 
        "%Y-%m-%d", 
        "%Y/%m/%d"
    ]
    
    for pattern in patterns:
        try:
            parsed_date = datetime.strptime(date_str, pattern)
            return parsed_date.isoformat()
        except ValueError:
            continue
    
    return None

def normalize_url(url: str, base_domain: str = "https://news.pts.org.tw") -> str:
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

def find_search_box(driver: webdriver.Chrome, wait: WebDriverWait, config: Dict) -> Any:
    """定位搜尋框"""
    print("等待搜尋框出現...")
    
    # 從配置獲取搜尋框 XPath
    search_box_xpath = config.get("search_page", {}).get("search_box_xpath", "//textarea[@name='q']")
    
    try:
        search_box = wait.until(EC.presence_of_element_located((By.XPATH, search_box_xpath)))
        print("已找到搜尋框 (使用 XPath)")
        return search_box
    except Exception as e:
        print(f"使用 XPath 定位搜尋框時發生錯誤: {str(e)}")
        raise Exception("無法找到搜尋框")


# ===== 搜尋頁面處理區 =====

def perform_search(driver: webdriver.Chrome, keyword: str, config: Dict) -> None:
    """執行搜尋操作"""
    # 從配置獲取基本 URL
    base_url = config.get("base_url", "https://www.google.com")
    print(f"開啟 {config.get('site_name', 'Google')} 首頁...")
    driver.get(base_url)
    
    # 等待並定位搜尋框
    wait = WebDriverWait(driver, 10)
    search_box = find_search_box(driver, wait, config)
    
    # 輸入搜尋詞並送出
    print(f"搜尋關鍵字: {keyword}")
    search_box.clear()
    search_box.send_keys(keyword)
    search_box.send_keys(Keys.RETURN)
    
    # 等待搜尋結果載入
    print("等待搜尋結果載入...")
    result_container_xpath = config.get("search_page", {}).get("result_container_xpath", "//div[@id='search']")
    wait.until(EC.presence_of_element_located((By.XPATH, result_container_xpath)))
    
    # 頁面載入延遲
    page_load_delay = config.get("delays", {}).get("page_load", 1)
    time.sleep(page_load_delay)


def extract_title(result: html.HtmlElement, config: Dict) -> str:
    """提取搜尋結果的標題"""
    title_xpath = config.get("list_page", {}).get("fields", {}).get("title", {}).get("xpath", ".//h3")
    title_elements = result.xpath(title_xpath)
    return title_elements[0].text_content().strip() if title_elements else "無標題"


def extract_link(result: html.HtmlElement, config: Dict) -> str:
    """提取搜尋結果的連結"""
    link_xpath = config.get("list_page", {}).get("fields", {}).get("link", {}).get("xpath", ".//a[h3]/@href")
    fallback_xpath = config.get("list_page", {}).get("fields", {}).get("link", {}).get("fallback_xpath", ".//a/@href")
    
    link_elements = result.xpath(link_xpath) or result.xpath(fallback_xpath)
    return link_elements[0] if link_elements else ""


def extract_description(result: html.HtmlElement, config: Dict) -> str:
    """提取搜尋結果的描述"""
    try:
        desc_xpath = config.get("list_page", {}).get("fields", {}).get("description", {}).get("xpath", ".//div[contains(@class, 'VwiC3b')]")
        max_length = config.get("list_page", {}).get("fields", {}).get("description", {}).get("max_length", 300)
        
        desc_elements = result.xpath(desc_xpath)
        description = ""
        if desc_elements:
            description = desc_elements[0].text_content().strip()

        # 清理描述文字
        if description:
            # 檢查是否需要移除額外空白
            if config.get("advanced_settings", {}).get("text_cleaning", {}).get("remove_extra_whitespace", True):
                description = ' '.join(description.split())
            
            # 截斷過長的描述
            if len(description) > max_length:
                description = description[:max_length-3] + "..."
        
        return description
    except Exception as e:
        print(f"提取描述時出錯: {str(e)}")
        return ""


def extract_search_results(page_source: str, config: Dict, max_results: Optional[int] = None) -> List[Dict]:
    """從頁面源碼提取搜尋結果"""
    print("解析搜尋結果頁面...")
    tree = html.fromstring(page_source)
    
    # 從配置獲取項目 XPath
    item_xpath = config.get("list_page", {}).get("item_xpath", "//div[contains(@class, 'N54PNb')]")
    
    # 定位搜尋結果
    search_results = tree.xpath(item_xpath)
    print(f"找到 {len(search_results)} 個搜尋結果")
    
    # 從配置獲取每頁最大結果數
    if max_results is None:
        max_results = config.get("advanced_settings", {}).get("max_results_per_page", 10)
    
    results = []
    count = min(max_results, len(search_results))
    
    for i, result in enumerate(search_results[:count]):
        try:
            # 提取標題、連結、描述
            title = extract_title(result, config)
            link = extract_link(result, config)
            description = extract_description(result, config)
            
            # 將結果加入列表
            results.append({
                "排名": i + 1,
                "標題": title,
                "連結": link,
                "描述": description
            })
            
            # 輸出結果
            print(f"搜尋結果 {i+1}: {title}")
            print(f"  連結: {link}")
            print(f"  描述: {description[:50]}..." if description else "  描述: 無")
            print("-" * 50)
            
            # 項目間延遲
            if i < count - 1:
                item_delay = config.get("delays", {}).get("between_items", 0)
                time.sleep(item_delay)
            
        except Exception as e:
            print(f"處理結果 {i+1} 時發生錯誤: {str(e)}")
    
    return results


# ===== 分頁控制區 =====

def has_next_page(driver: webdriver.Chrome, config: Dict) -> bool:
    """檢查是否有下一頁"""
    has_next_check = config.get("pagination", {}).get("has_next_page_check")
    if not has_next_check:
        return False
        
    tree = html.fromstring(driver.page_source)
    # 使用 XPath 函數 boolean() 檢查是否有下一頁
    return bool(tree.xpath(has_next_check))


def go_to_next_page(driver: webdriver.Chrome, wait: WebDriverWait, config: Dict) -> bool:
    """前往下一頁"""
    next_button_xpath = config.get("pagination", {}).get("next_button_xpath")
    if not next_button_xpath:
        return False
        
    try:
        # 嘗試透過按鈕點擊前往下一頁
        return try_click_next_button(driver, wait, next_button_xpath, config)
    except Exception as e:
        print(f"點擊下一頁按鈕失敗: {str(e)}")
        
        # 嘗試備用方法：直接修改URL
        return try_url_navigation(driver, wait, config)


def try_click_next_button(driver: webdriver.Chrome, wait: WebDriverWait, next_button_xpath: str, config: Dict) -> bool:
    """嘗試透過按鈕點擊前往下一頁"""
    # 找到下一頁按鈕
    next_button = driver.find_element(By.XPATH, next_button_xpath)
    
    # 滾動到下一頁按鈕使其可見
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
    scroll_delay = config.get("delays", {}).get("scroll", 1)
    time.sleep(scroll_delay)  # 等待滾動完成
    
    try:
        # 嘗試直接點擊
        next_button.click()
    except Exception as e:
        print(f"直接點擊失敗: {str(e)}")
        print("嘗試使用JavaScript點擊...")
        # 使用JavaScript點擊
        driver.execute_script("arguments[0].click();", next_button)
    
    return wait_for_page_change(driver, wait, config)


def try_url_navigation(driver: webdriver.Chrome, wait: WebDriverWait, config: Dict) -> bool:
    """嘗試透過修改URL前往下一頁"""
    try:
        print("嘗試通過URL參數導航到下一頁...")
        current_url = driver.current_url
        next_url = ""
        
        if "start=" in current_url:
            # 修改start參數
            start_value = int(re.search(r'start=(\d+)', current_url).group(1))
            next_start = start_value + 10
            next_url = re.sub(r'start=\d+', f'start={next_start}', current_url)
        else:
            # 添加start參數
            next_url = current_url + ("&" if "?" in current_url else "?") + "start=10"
        
        print(f"導航到: {next_url}")
        driver.get(next_url)
        
        return wait_for_page_change(driver, wait, config)
        
    except Exception as e:
        print(f"通過URL參數導航也失敗: {str(e)}")
        return False


def wait_for_page_change(driver: webdriver.Chrome, wait: WebDriverWait, config: Dict) -> bool:
    """等待頁面變更完成，返回是否成功"""
    try:
        # 等待新頁面加載
        container_xpath = config.get("search_page", {}).get("result_container_xpath", "//div[@id='search']")
        wait.until(EC.presence_of_element_located((By.XPATH, container_xpath)))
        
        # 頁面間延遲
        delay = config.get("delays", {}).get("between_pages", 2)
        time.sleep(delay)
        
        return True
    except Exception as e:
        print(f"等待頁面變更時出錯: {str(e)}")
        return False


# ===== 詳情頁面處理區 =====

def extract_youtube_embed(tree: html.HtmlElement, config: Dict) -> Optional[str]:
    """提取 YouTube 嵌入影片連結"""
    detail_fields = config.get("detail_page", {}).get("fields", {})
    youtube_xpath = detail_fields.get("youtube_embed", {}).get("xpath")
    
    if youtube_xpath:
        youtube_elements = tree.xpath(youtube_xpath)
        if youtube_elements:
            return youtube_elements[0]
    return None


def extract_text_field(element: html.HtmlElement, field_type: str) -> str:
    """提取文本型字段"""
    if field_type == "text":
        return clean_text(element.text_content())
    return ""


def extract_attribute_field(element: html.HtmlElement) -> str:
    """提取屬性型字段"""
    return element


def extract_html_field(elements: List[html.HtmlElement], config: Dict) -> Tuple[str, str]:
    """提取HTML型字段，返回(html內容, 純文本)"""
    if not elements:
        return "", ""
        
    # 獲取HTML內容
    html_content = html.tostring(elements[0], encoding='unicode')
    
    # 清理HTML
    extraction_settings = config.get("detail_page", {}).get("extraction_settings", {})
    html_content = clean_html(html_content, extraction_settings)
    
    # 提取純文本
    plain_text = clean_text(remove_tags(html_content))
    # 優化格式
    plain_text = re.sub(r'\n\s*\n', '\n\n', plain_text)
    
    return html_content, plain_text


def process_compound_field(element: html.HtmlElement, field_config: Dict) -> Dict:
    """處理複合型字段"""
    result = {}
    
    for sub_field_name, sub_field_config in field_config.get("fields", {}).items():
        sub_xpath = sub_field_config.get("xpath")
        sub_type = sub_field_config.get("type")
        
        sub_elements = element.xpath(sub_xpath)
        if sub_elements:
            if sub_type == "text":
                result[sub_field_name] = clean_text(sub_elements[0].text_content())
            elif sub_type == "attribute":
                result[sub_field_name] = sub_elements[0]
                
                # 處理URL
                if "url" in sub_field_name.lower() and result[sub_field_name]:
                    result[sub_field_name] = normalize_url(result[sub_field_name])
    
    return result


def process_field(field_name: str, field_config: Dict, tree: html.HtmlElement, config: Dict) -> Any:
    """處理單個字段的提取邏輯"""
    xpath = field_config.get("xpath")
    field_type = field_config.get("type")
    is_multiple = field_config.get("multiple", False)
    
    # 找元素
    elements = tree.xpath(xpath)
    
    # 嘗試備用XPath
    if not elements and "fallback_xpath" in field_config:
        elements = tree.xpath(field_config.get("fallback_xpath"))
    
    # 處理找不到元素的情況
    if not elements:
        return [] if is_multiple else None
    
    # 根據字段類型處理
    if field_type == "compound" and is_multiple:
        # 處理複合字段
        return [process_compound_field(element, field_config) for element in elements]
        
    elif is_multiple:
        # 處理多值字段
        values = []
        for element in elements:
            if field_type == "text":
                text = clean_text(element.text_content())
                if text:  # 確保不是空值
                    values.append(text)
            elif field_type == "attribute":
                values.append(element)
        return values
        
    else:
        # 處理單值字段
        if field_type == "text":
            return clean_text(elements[0].text_content())
        elif field_type == "attribute":
            return elements[0]
        elif field_type == "html":
            html_content, plain_text = extract_html_field(elements, config)
            return {
                "html": html_content,
                "text": plain_text
            }
    
    return None


def post_process_field(field_name: str, value: Any) -> Any:
    """對已提取的字段進行後處理"""
    if value is None:
        return None
        
    # 作者字段特殊處理
    if field_name == "author" and isinstance(value, str):
        # 深度清理作者字段
        value = clean_text(value)
        # 統一分隔符號格式
        value = re.sub(r'\s+/\s+', ' / ', value)
        # 移除多餘的換行符和頭尾符號
        return re.sub(r'^\s*[/,、]\s*|\s*[/,、]\s*$', '', value)
    
    # 日期字段特殊處理
    if field_name in ["publish_time", "update_time"] and isinstance(value, str):
        parsed_date = parse_date(value)
        if parsed_date:
            return parsed_date
    
    # 圖片URL處理
    if field_name == "main_image" and isinstance(value, str):
        return normalize_url(value)
            
    return value


def extract_tags_fallback(tree: html.HtmlElement) -> List[str]:
    """使用備用方法提取文章標籤"""
    # 嘗試各種可能的標籤選擇器
    tag_paths = [
        "//ul[@x-data='articleTags']//li/a",
        "//ul[@x-data='articleTags']/li",
        "//div[contains(@class, 'articleTags')]/a",
        "//div[contains(@class, 'article-tags')]/a",
        "//div[contains(@class, 'tag-list')]/a",
        "//section[contains(@class, 'tag')]/a",
        "//ul[contains(@class, 'tags')]/li/a"
    ]
    
    for path in tag_paths:
        tags = tree.xpath(path)
        if tags:
            return [clean_text(tag.text_content()) for tag in tags if tag.text_content().strip()]
    
    return []


def extract_detail_page(driver: webdriver.Chrome, url: str, config: Dict) -> Dict[str, Any]:
    """訪問新聞詳情頁並提取元數據"""
    try:
        print(f"\n訪問新聞詳情頁: {url}")
        driver.get(url)
        
        # 等待頁面加載
        page_load_delay = config.get("delays", {}).get("page_load", 3)
        time.sleep(page_load_delay)
        
        # 解析頁面
        page_source = driver.page_source
        tree = html.fromstring(page_source)
        
        # 提取配置中定義的所有字段
        detail_fields = config.get("detail_page", {}).get("fields", {})
        result = {}
        
        # 檢查是否有YouTube影片
        youtube_url = extract_youtube_embed(tree, config)
        if youtube_url:
            result["youtube_embed"] = youtube_url
            print(f"  發現 YouTube 影片: {youtube_url}")
        
        # 提取所有配置的字段
        for field_name, field_config in detail_fields.items():
            try:
                # 提取原始值
                value = process_field(field_name, field_config, tree, config)
                
                # 如果是HTML字段，分別儲存HTML和文本版本
                if isinstance(value, dict) and "html" in value and "text" in value:
                    result[field_name + "_html"] = value["html"]
                    result[field_name] = value["text"]
                else:
                    # 後處理字段
                    processed_value = post_process_field(field_name, value)
                    result[field_name] = processed_value
                
                # 輸出結果預覽
                if field_name in result:
                    value_preview = str(result[field_name])
                    if len(value_preview) > 100:
                        value_preview = value_preview[:97] + "..."
                    print(f"  提取 {field_config.get('description', field_name)}: {value_preview}")
            
            except Exception as e:
                print(f"  提取字段 '{field_name}' 時出錯: {e}")
                result[field_name] = None
        
        # 特殊處理：標籤額外檢查
        if "tags" not in result or not result.get("tags"):
            tags = extract_tags_fallback(tree)
            if tags:
                result["tags"] = tags
                print(f"  使用備用方法提取標籤: {tags}")
        
        print(f"已提取 {len(result)} 個元數據字段")
        return result
        
    except Exception as e:
        print(f"提取詳情頁時出錯: {e}")
        return {"error": str(e)}


# ===== 結果處理區 =====

def save_results(results: List[Dict], config: Dict) -> Optional[str]:
    """保存結果到JSON檔案"""
    if not results:
        print("沒有結果可保存")
        return None
        
    os.makedirs("output", exist_ok=True)
    output_file = f"output/{config.get('site_name', 'google_search')}_results.json"
    
    # 格式化結果以便 JSON 序列化
    formatted_results = format_for_json(results)
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(formatted_results, f, ensure_ascii=False, indent=2)
    
    print(f"結果已儲存至: {output_file}")
    
    # 顯示擷取結果摘要
    total_details = sum(1 for result in results if "詳情" in result and result["詳情"])
    print(f"共擷取 {len(results)} 條搜尋結果，成功解析 {total_details} 個詳情頁面")
    
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

def process_search_page(driver: webdriver.Chrome, config: Dict) -> List[Dict]:
    """處理搜索頁面並進行分頁爬取"""
    all_results = []
    current_page = 1
    max_pages = config.get("pagination", {}).get("max_pages", 1)
    
    while current_page <= max_pages:
        print(f"\n--- 正在處理第 {current_page} 頁 ---")
        
        # 解析當前頁面結果
        page_results = extract_search_results(driver.page_source, config)
        
        # 為每個搜尋結果訪問詳情頁，提取元數據
        detailed_results = process_detail_pages(driver, page_results, config)
        all_results.extend(detailed_results)
        
        # 如果已經達到最大頁數或沒有下一頁，則結束
        if current_page >= max_pages or not has_next_page(driver, config):
            break
            
        # 前往下一頁
        print(f"前往第 {current_page + 1} 頁...")
        wait = WebDriverWait(driver, 10)
        if not go_to_next_page(driver, wait, config):
            break
            
        current_page += 1
    
    return all_results


def process_detail_pages(driver: webdriver.Chrome, page_results: List[Dict], config: Dict) -> List[Dict]:
    """處理搜尋結果的詳情頁"""
    detailed_results = []
    
    for result in page_results:
        link = result.get("連結")
        if not link or not link.startswith("http"):
            print(f"跳過無效連結: {link}")
            continue
        
        # 檢查是否為公視新聞網站
        if "news.pts.org.tw" in link:
            # 獲取詳情頁數據
            detail_data = extract_detail_page(driver, link, config)
            
            # 合併搜索結果和詳情頁數據
            result["詳情"] = detail_data
        else:
            print(f"跳過非公視新聞連結: {link}")
        
        detailed_results.append(result)
    
    return detailed_results


def main() -> None:
    """主函數：執行搜尋爬蟲流程"""
    driver = None
    
    try:
        # 步驟1：載入配置檔案
        config_path = os.path.join(os.path.dirname(__file__), "basic_google_search_pts.json")
        config = load_config(config_path)
        
        # 步驟2：設置WebDriver
        driver = setup_webdriver(config)
        
        # 步驟3：執行搜尋 (從配置中獲取搜尋關鍵字)
        search_keyword = config.get("search", {}).get("keyword", "Google")
        perform_search(driver, search_keyword, config)
        
        # 步驟4：處理搜尋結果頁面
        all_results = process_search_page(driver, config)
        
        # 步驟5：保存結果
        save_results(all_results, config)
        
        # 完成
        print(f"完成爬取，共 {len(all_results)} 條結果")
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