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

def find_search_box(driver, wait):
    """定位搜尋框"""
    print("等待搜尋框出現...")
    
    try:
        search_box = wait.until(EC.presence_of_element_located((By.XPATH, "//textarea[@name='q']")))
        print("已找到搜尋框 (使用 XPath)")
        return search_box
    except Exception as e:
        print(f"使用 XPath 定位搜尋框時發生錯誤: {str(e)}")
        raise Exception("無法找到搜尋框")

def perform_search(driver, keyword):
    """執行搜尋操作"""
    print(f"開啟 Google 首頁...")
    driver.get("https://www.google.com")
    
    # 等待並定位搜尋框
    wait = WebDriverWait(driver, 10)
    search_box = find_search_box(driver, wait)
    
    # 輸入搜尋詞並送出
    print(f"搜尋關鍵字: {keyword}")
    search_box.clear()
    search_box.send_keys(keyword)
    search_box.send_keys(Keys.RETURN)
    
    # 等待搜尋結果載入
    print("等待搜尋結果載入...")
    wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='search']")))

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
        
    os.makedirs("output", exist_ok=True)
    output_file = "output/google_search_results.json"
    
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
        perform_search(driver, search_keyword)
        
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
            print("關閉瀏覽器...")
            driver.quit()
        
        print("爬蟲程序已完成")

if __name__ == "__main__":
    main()
