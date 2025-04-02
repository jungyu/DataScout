"""
基於 JSON 配置的 Google 搜尋爬蟲範例
此範例展示如何從 JSON 配置檔案獲取參數並使用 lxml 進行 XPath 解析
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import json
import os
from lxml import html

def load_config(config_path):
    """載入配置檔案"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print(f"已載入配置檔案: {config_path}")
        return config
    except Exception as e:
        print(f"載入配置檔案失敗: {str(e)}")
        raise

def setup_webdriver(config):
    """設置並初始化WebDriver"""
    print("正在設置 Chrome WebDriver...")
    chrome_options = webdriver.ChromeOptions()
    # 取消註解下行以啟用無頭模式（執行時不顯示瀏覽器窗口）
    # chrome_options.add_argument('--headless')
    
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

def find_search_box(driver, wait, config):
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

def perform_search(driver, keyword, config):
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

def extract_search_results(page_source, config, max_results=None):
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
            # 提取標題
            title = extract_title(result, config)
            
            # 提取連結
            link = extract_link(result, config)
            
            # 提取描述
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

def extract_title(result, config):
    """提取搜尋結果的標題"""
    # 從配置獲取標題 XPath
    title_xpath = config.get("list_page", {}).get("fields", {}).get("title", {}).get("xpath", ".//h3")
    
    title_elements = result.xpath(title_xpath)
    return title_elements[0].text_content().strip() if title_elements else "無標題"

def extract_link(result, config):
    """提取搜尋結果的連結"""
    # 從配置獲取連結 XPath
    link_xpath = config.get("list_page", {}).get("fields", {}).get("link", {}).get("xpath", ".//a[h3]/@href")
    fallback_xpath = config.get("list_page", {}).get("fields", {}).get("link", {}).get("fallback_xpath", ".//a/@href")
    
    link_elements = result.xpath(link_xpath) or result.xpath(fallback_xpath)
    return link_elements[0] if link_elements else ""

def extract_description(result, config):
    """提取搜尋結果的描述"""
    try:
        # 從配置獲取描述 XPath 和最大長度
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

def save_results(results, config):
    """保存結果到JSON檔案"""
    if not results:
        print("沒有結果可保存")
        return None
        
    os.makedirs("output", exist_ok=True)
    output_file = f"output/{config.get('site_name', 'google_search')}_results.json"
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"結果已儲存至: {output_file}")
    return output_file

def has_next_page(driver, config):
    """檢查是否有下一頁"""
    has_next_check = config.get("pagination", {}).get("has_next_page_check")
    if not has_next_check:
        return False
        
    tree = html.fromstring(driver.page_source)
    # 使用 XPath 函數 boolean() 檢查是否有下一頁
    return bool(tree.xpath(has_next_check))

def go_to_next_page(driver, wait, config):
    """前往下一頁"""
    next_button_xpath = config.get("pagination", {}).get("next_button_xpath")
    if not next_button_xpath:
        return False
        
    try:
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
        
        # 等待新頁面加載
        container_xpath = config.get("search_page", {}).get("result_container_xpath", "//div[@id='search']")
        wait.until(EC.presence_of_element_located((By.XPATH, container_xpath)))
        
        # 確保頁面已經變化
        old_url = driver.current_url
        try:
            wait.until(lambda driver: driver.current_url != old_url)
        except TimeoutException:
            print("URL沒有變化，檢查是否有其他跡象表明頁面已更新...")
            # 可以嘗試檢查頁面中的某些元素是否更新
        
        # 頁面間延遲
        delay = config.get("delays", {}).get("between_pages", 2)
        time.sleep(delay)
        
        return True
    except Exception as e:
        print(f"前往下一頁時出錯: {str(e)}")
        
        # 嘗試備用方法：直接修改URL
        try:
            print("嘗試通過URL參數導航到下一頁...")
            current_url = driver.current_url
            if "start=" in current_url:
                # 修改start參數
                import re
                start_value = int(re.search(r'start=(\d+)', current_url).group(1))
                next_start = start_value + 10
                next_url = re.sub(r'start=\d+', f'start={next_start}', current_url)
            else:
                # 添加start參數
                next_url = current_url + ("&" if "?" in current_url else "?") + "start=10"
            
            print(f"導航到: {next_url}")
            driver.get(next_url)
            
            # 等待新頁面加載
            container_xpath = config.get("search_page", {}).get("result_container_xpath")
            wait.until(EC.presence_of_element_located((By.XPATH, container_xpath)))
            
            # 頁面延遲
            time.sleep(config.get("delays", {}).get("page_load", 3))
            return True
        except Exception as e:
            print(f"通過URL參數導航也失敗: {str(e)}")
            return False

def main():
    """主函數：執行搜尋爬蟲流程"""
    driver = None
    
    try:
        # 步驟1：載入配置檔案
        config_path = os.path.join(os.path.dirname(__file__), "basic_google_search.json")
        config = load_config(config_path)
        
        # 步驟2：設置WebDriver
        driver = setup_webdriver(config)
        
        # 步驟3：執行搜尋 (從配置中獲取搜尋關鍵字)
        search_keyword = config.get("search", {}).get("keyword", "Google")
        perform_search(driver, search_keyword, config)
        
        # 步驟4：擷取頁面內容和解析搜尋結果
        all_results = []
        current_page = 1
        # 從配置中獲取最大頁數
        max_pages = config.get("pagination", {}).get("max_pages", 1)
        
        while current_page <= max_pages:
            print(f"\n--- 正在處理第 {current_page} 頁 ---")
            
            # 解析當前頁面結果
            page_results = extract_search_results(driver.page_source, config)
            all_results.extend(page_results)
            
            # 如果已經達到最大頁數或沒有下一頁，則結束
            if current_page >= max_pages or not has_next_page(driver, config):
                break
                
            # 前往下一頁
            print(f"前往第 {current_page + 1} 頁...")
            wait = WebDriverWait(driver, 10)
            if not go_to_next_page(driver, wait, config):
                break
                
            current_page += 1
        
        # 步驟5：保存結果
        save_results(all_results, config)
        
        print(f"完成爬取 {current_page} 頁，共 {len(all_results)} 條結果")
        finish_delay = config.get("delays", {}).get("finish", 3)
        print(f"暫停 {finish_delay} 秒...")
        time.sleep(finish_delay)
        
    except TimeoutException:
        print("載入頁面逾時，請檢查網路連線或網站可用性")
    except Exception as e:
        print(f"發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # 檢查是否需要保存錯誤頁面
        if driver and config.get("advanced_settings", {}).get("save_error_page", False):
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
    finally:
        # 步驟6：清理資源
        if driver:
            print("關閉瀏覽器...")
            driver.quit()
        
        print("爬蟲程序已完成")

if __name__ == "__main__":
    main()