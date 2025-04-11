"""
基礎 Selenium + lxml XPath 爬蟲範例
此範例展示如何結合 Selenium 控制瀏覽器並使用 lxml 進行 XPath 解析
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

def setup_webdriver():
    """設置並初始化WebDriver"""
    print("正在設置 Chrome WebDriver...")
    chrome_options = webdriver.ChromeOptions()
    # 取消註解下行以啟用無頭模式（執行時不顯示瀏覽器窗口）
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36')
    
    print("初始化 Chrome WebDriver...")
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    return driver

def find_search_box(driver, wait, config):
    """定位搜尋框"""
    print("等待搜尋框出現...")
    
    try:
        # 先等待頁面完全載入
        wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
        
        # 嘗試多個可能的搜尋框選擇器
        search_box_selectors = [
            "//textarea[@name='q']",
            "//input[@name='q']",
            "//input[@title='搜尋']",
            "//textarea[@title='搜尋']"
        ]
        
        for selector in search_box_selectors:
            try:
                print(f"嘗試使用選擇器: {selector}")
                search_box = wait.until(EC.presence_of_element_located((By.XPATH, selector)))
                
                # 確保元素可見且可互動
                wait.until(EC.visibility_of_element_located((By.XPATH, selector)))
                wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                
                # 滾動到元素位置
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", search_box)
                time.sleep(1)  # 等待滾動完成
                
                print(f"已找到搜尋框 (使用選擇器: {selector})")
                return search_box
            except Exception as e:
                print(f"使用選擇器 {selector} 失敗: {str(e)}")
                continue
        
        raise Exception("所有選擇器都無法找到可互動的搜尋框")
    except Exception as e:
        print(f"定位搜尋框時發生錯誤: {str(e)}")
        raise Exception("無法找到搜尋框")

def perform_search(driver, keyword, config):
    """執行搜尋操作"""
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # 從配置獲取基本 URL
            base_url = config.get("base_url", "https://www.google.com")
            print(f"開啟 {config.get('site_name', 'Google')} 首頁...")
            driver.get(base_url)
            
            # 等待頁面完全載入
            wait = WebDriverWait(driver, 20)
            wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
            
            # 等待並定位搜尋框
            search_box = find_search_box(driver, wait, config)
            
            # 輸入搜尋詞並送出
            print(f"搜尋關鍵字: {keyword}")
            
            # 清除搜尋框內容
            try:
                search_box.clear()
            except:
                # 如果清除失敗，使用 JavaScript 清除
                driver.execute_script("arguments[0].value = '';", search_box)
            
            # 輸入關鍵字
            search_box.send_keys(keyword)
            time.sleep(1)  # 等待輸入完成
            
            # 嘗試多種方式提交搜尋
            try:
                search_box.send_keys(Keys.RETURN)
            except:
                try:
                    search_box.submit()
                except:
                    print("嘗試使用 JavaScript 提交搜尋...")
                    driver.execute_script("document.querySelector('form[action*=\"search\"]').submit();")
            
            # 等待搜尋結果載入
            print("等待搜尋結果載入...")
            result_container_xpath = config.get("search_page", {}).get("result_container_xpath", "//div[@id='search']")
            
            # 等待結果容器出現
            wait.until(EC.presence_of_element_located((By.XPATH, result_container_xpath)))
            
            # 確保結果容器可見
            wait.until(EC.visibility_of_element_located((By.XPATH, result_container_xpath)))
            
            # 頁面載入延遲
            page_load_delay = config.get("delays", {}).get("page_load", 3)
            time.sleep(page_load_delay)
            
            # 如果成功執行到這裡，跳出重試迴圈
            break
            
        except Exception as e:
            retry_count += 1
            print(f"第 {retry_count} 次嘗試失敗: {str(e)}")
            
            if retry_count >= max_retries:
                print("已達最大重試次數，放棄執行")
                raise
            
            print(f"等待 {retry_count * 2} 秒後重試...")
            time.sleep(retry_count * 2)
            
            # 重新初始化 WebDriver
            if driver:
                try:
                    driver.quit()
                except:
                    pass
            driver = setup_webdriver()
            
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
        scroll_delay = config.get("delays", {}).get("scroll", 2)  # 增加滾動延遲到 2 秒
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
        delay = config.get("delays", {}).get("between_pages", 3)  # 增加頁面間延遲到 3 秒
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
            time.sleep(config.get("delays", {}).get("page_load", 5))  # 增加頁面載入延遲到 5 秒
            return True
        except Exception as e:
            print(f"通過URL參數導航也失敗: {str(e)}")
            return False

def extract_search_results(page_source, max_results=10):
    """從頁面源碼提取搜尋結果"""
    print("解析搜尋結果頁面...")
    tree = html.fromstring(page_source)
    
    # 定位搜尋結果
    search_results = tree.xpath("//div[contains(@class, 'N54PNb')]")
    print(f"找到 {len(search_results)} 個搜尋結果")
    
    results = []
    count = min(max_results, len(search_results))
    
    for i, result in enumerate(search_results[:count]):
        try:
            # 提取標題
            title = extract_title(result)
            
            # 提取連結
            link = extract_link(result)
            
            # 提取描述
            description = extract_description(result)
            
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
            
        except Exception as e:
            print(f"處理結果 {i+1} 時發生錯誤: {str(e)}")
    
    return results

def extract_title(result):
    """提取搜尋結果的標題"""
    title_elements = result.xpath(".//h3")
    return title_elements[0].text_content().strip() if title_elements else "無標題"

def extract_link(result):
    """提取搜尋結果的連結"""
    link_elements = result.xpath(".//a[h3]/@href") or result.xpath(".//a/@href")
    return link_elements[0] if link_elements else ""

def extract_description(result):
    """提取搜尋結果的描述"""
    try:
        desc_elements = result.xpath(".//div[contains(@class, 'VwiC3b')]")
        if desc_elements:
            description = desc_elements[0].text_content().strip()

        # 清理描述文字
        if description:
            description = ' '.join(description.split())
            if len(description) > 300:
                description = description[:297] + "..."
        
        return description
    except Exception as e:
        print(f"提取描述時出錯: {str(e)}")
        return ""

def save_results(results):
    """保存結果到JSON檔案"""
    if not results:
        print("沒有結果可保存")
        return None
        
    os.makedirs("examples/data/output", exist_ok=True)
    output_file = "examples/data/output/google_search_results.json"
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"結果已儲存至: {output_file}")
    return output_file

def main():
    """主函數：執行搜尋爬蟲流程"""
    driver = None
    
    try:
        # 步驟1：設置WebDriver
        driver = setup_webdriver()
        
        # 步驟2：執行搜尋
        search_keyword = "地震 site:news.pts.org.tw"
        config = {
            "base_url": "https://www.google.com",
            "site_name": "Google",
            "search_page": {
                "result_container_xpath": "//div[@id='search']"
            },
            "delays": {
                "page_load": 3,
                "scroll": 2,
                "between_pages": 3
            }
        }
        perform_search(driver, search_keyword, config)
        
        # 步驟3：擷取頁面內容
        page_source = driver.page_source
        
        # 步驟4：解析搜尋結果
        results = extract_search_results(page_source, max_results=10)
        
        # 步驟5：保存結果
        save_results(results)
        
        print("完成爬取，暫停 3 秒...")
        time.sleep(3)
        
    except TimeoutException:
        print("載入頁面逾時，請檢查網路連線或網站可用性")
    except Exception as e:
        print(f"發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        # 步驟6：清理資源
        if driver:
            try:
                print("關閉瀏覽器...")
                driver.quit()
            except:
                pass
        
        print("爬蟲程序已完成")

if __name__ == "__main__":
    main()