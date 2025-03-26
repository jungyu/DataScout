"""
基礎 Selenium 爬蟲範例
此範例展示如何使用 Selenium 進行簡單的網頁爬取
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

def main():
    """
    基礎爬蟲示範：從 Google 搜尋結果中提取資訊
    """
    # 設置 Chrome 選項
    chrome_options = webdriver.ChromeOptions()
    # 取消註解下行以啟用無頭模式（執行時不顯示瀏覽器窗口）
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    # 初始化 WebDriver
    print("正在初始化 Chrome WebDriver...")
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    
    results = []
    
    try:
        print("正在開啟 Google 首頁...")
        driver.get("https://www.google.com")
        
        # 定義關鍵字
        search_keyword = "Python Selenium 教學"
        
        # 找到搜尋框並輸入搜尋詞
        print(f"正在搜尋: {search_keyword}")
        search_box = driver.find_element(By.NAME, "q")
        search_box.clear()
        search_box.send_keys(search_keyword)
        search_box.send_keys(Keys.RETURN)
        
        # 等待搜尋結果載入
        print("等待搜尋結果載入...")
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.g")))
        
        # 找出所有搜尋結果
        search_results = driver.find_elements(By.CSS_SELECTOR, "div.g")
        print(f"找到 {len(search_results)} 個搜尋結果")
        
        # 提取前 5 個搜尋結果的資訊
        max_results = min(5, len(search_results))
        for i, result in enumerate(search_results[:max_results]):
            try:
                title_element = result.find_element(By.CSS_SELECTOR, "h3")
                title = title_element.text
                
                # 嘗試提取連結
                link = ""
                try:
                    link_element = result.find_element(By.CSS_SELECTOR, "a")
                    link = link_element.get_attribute("href")
                except NoSuchElementException:
                    pass
                
                # 嘗試提取描述
                description = ""
                try:
                    desc_element = result.find_element(By.CSS_SELECTOR, "div[data-sncf='1']")
                    description = desc_element.text
                except NoSuchElementException:
                    pass
                
                # 將結果加入列表
                results.append({
                    "排名": i + 1,
                    "標題": title,
                    "連結": link,
                    "描述": description
                })
                
                print(f"搜尋結果 {i+1}: {title}")
                print(f"  連結: {link}")
                print(f"  描述: {description[:50]}..." if description else "  描述: 無")
                print("-" * 50)
            
            except Exception as e:
                print(f"處理結果 {i+1} 時發生錯誤: {str(e)}")
        
        # 保存結果到 JSON 檔案
        if results:
            os.makedirs("output", exist_ok=True)
            output_file = "output/google_search_results.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"結果已儲存至: {output_file}")
            
        # 暫停以便觀察結果 (在實際應用中可移除)
        print("完成爬取，暫停 3 秒...")
        time.sleep(3)
        
    except TimeoutException:
        print("載入頁面逾時，請檢查網路連線或網站可用性")
    except Exception as e:
        print(f"發生錯誤: {str(e)}")
        
    finally:
        # 關閉瀏覽器
        print("關閉瀏覽器...")
        driver.quit()
        print("爬蟲程序已完成")

if __name__ == "__main__":
    main()
