from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import os

def demo_wait_for_element():
    """展示如何等待元素載入"""
    driver = webdriver.Chrome()
    try:
        driver.get("https://www.python.org/")
        
        # 等待特定元素出現
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "submit"))
        )
        print("元素已找到")
    finally:
        driver.quit()

def demo_javascript_interaction():
    """展示如何與JavaScript互動"""
    driver = webdriver.Chrome()
    try:
        driver.get("https://www.python.org/")
        
        # 執行JavaScript
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        
        # 修改頁面內容
        driver.execute_script("document.body.style.backgroundColor = 'yellow';")
    finally:
        driver.quit()

def demo_file_download():
    """展示如何下載檔案"""
    chrome_options = Options()
    download_path = os.path.expanduser("~/Downloads")
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": download_path,
        "download.prompt_for_download": False
    })
    
    driver = webdriver.Chrome(options=chrome_options)
    try:
        driver.get("https://www.python.org/downloads/")
        # 點擊下載按鈕（實際網站可能需要調整選擇器）
        download_button = driver.find_element(By.CSS_SELECTOR, "a.button")
        download_button.click()
        time.sleep(5)  # 等待下載開始
    finally:
        driver.quit()

def main():
    print("開始展示Selenium進階功能...")
    
    print("\n1. 等待元素載入示範")
    demo_wait_for_element()
    
    print("\n2. JavaScript互動示範")
    demo_javascript_interaction()
    
    print("\n3. 檔案下載示範")
    demo_file_download()
    
    print("\n所有示範完成!")

if __name__ == "__main__":
    main()
