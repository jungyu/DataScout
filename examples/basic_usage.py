from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def main():
    # 初始化 Chrome WebDriver
    driver = webdriver.Chrome()
    
    try:
        # 開啟 Google 首頁
        driver.get("https://www.google.com")
        
        # 找到搜尋框並輸入搜尋詞
        search_box = driver.find_element(By.NAME, "q")
        search_box.send_keys("Python Selenium")
        search_box.send_keys(Keys.RETURN)
        
        # 等待搜尋結果載入
        wait = WebDriverWait(driver, 10)
        search_results = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.g"))
        )
        
        # 印出前三個搜尋結果的標題
        for i, result in enumerate(search_results[:3]):
            title = result.find_element(By.CSS_SELECTOR, "h3").text
            print(f"搜尋結果 {i+1}: {title}")
            
        # 暫停 3 秒以便觀察結果
        time.sleep(3)
        
    except Exception as e:
        print(f"發生錯誤: {e}")
        
    finally:
        # 關閉瀏覽器
        driver.quit()

if __name__ == "__main__":
    main()
