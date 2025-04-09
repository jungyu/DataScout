"""
蝦皮爬蟲程式
基於配置文件的蝦皮網站資料爬取工具
支援關鍵字搜尋、商店/商品篩選、分類瀏覽等功能
"""
import os
import re
import json
import time
import random
import traceback
import urllib.parse
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Union, Set

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, 
    ElementClickInterceptedException, StaleElementReferenceException
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from lxml import html, etree


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


def normalize_url(url: str, base_domain: str = "https://shopee.tw") -> str:
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


def parse_image_url(style_str: str) -> str:
    """從style屬性中提取圖片URL"""
    match = re.search(r'url\("([^"]+)"\)', style_str)
    if match:
        return match.group(1)
    return ""


def clean_html_tag(html_text: str) -> str:
    """清除HTML標籤，只保留文本內容"""
    soup = BeautifulSoup(html_text, 'html.parser')
    return soup.get_text()


def random_sleep(min_seconds: float = 1.0, max_seconds: float = 3.0) -> None:
    """隨機睡眠一段時間，避免被檢測為爬蟲"""
    time.sleep(random.uniform(min_seconds, max_seconds))


def adaptive_sleep(min_time=1.0, max_time=5.0, factor=1.0):
    """自適應延遲，基於因子調整等待時間"""
    base_time = random.uniform(min_time, max_time)
    sleep_time = base_time * factor
    time.sleep(sleep_time)
    return sleep_time


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
    chrome_options = Options()
    
    # 從配置文件獲取 User-Agent
    user_agent = config.get("request", {}).get("headers", {}).get("User-Agent")
    if user_agent:
        chrome_options.add_argument(f'user-agent={user_agent}')
    
    # 添加常用的選項
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    # 反檢測設定
    anti_detection = config.get("advanced_settings", {}).get("anti_detection", {})
    
    if anti_detection.get("stealth_mode", True):
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
    
    # 隨機視窗大小 (避免使用固定視窗大小被識別)
    if anti_detection.get("randomize_viewport", True):
        width = random.randint(1200, 1600)
        height = random.randint(800, 1000)
        chrome_options.add_argument(f"--window-size={width},{height}")
    else:
        chrome_options.add_argument('--start-maximized')
    
    # 禁用圖片加載 (提高速度，減少記憶體用量)
    if not config.get("advanced_settings", {}).get("load_images", True):
        chrome_options.add_argument('--blink-settings=imagesEnabled=false')
    
    # 啟用效能紀錄器 (提高性能)
    chrome_options.add_argument("--enable-precise-memory-info")
    chrome_options.add_argument("--disable-default-apps")
    chrome_options.add_argument("--disable-extensions")
    
    print("初始化 Chrome WebDriver...")
    try:
        # 嘗試所有初始化方法
        driver = None
        
        # 方法1: 如果配置為使用已開啟的Chrome調試模式
        if config.get("advanced_settings", {}).get("use_debug_port", False):
            debug_port = config.get("advanced_settings", {}).get("debug_port", "9222")
            chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{debug_port}")
            driver = webdriver.Chrome(options=chrome_options)
            print("成功連接到已開啟的Chrome瀏覽器")
        else:
            # 方法2: 使用 undetected_chromedriver (如果有設定)
            if anti_detection.get("undetected_mode", True):
                try:
                    # 嘗試導入 undetected_chromedriver
                    import undetected_chromedriver as uc
                    
                    # 使用 undetected_chromedriver 的選項類型，而不是標準的 selenium 選項
                    uc_options = uc.ChromeOptions()
                    
                    # 從配置文件獲取 User-Agent
                    if user_agent:
                        uc_options.add_argument(f'user-agent={user_agent}')
                    
                    # 添加常用的選項
                    uc_options.add_argument('--no-sandbox')
                    uc_options.add_argument('--disable-dev-shm-usage')
                    
                    # 添加其他必要選項
                    if anti_detection.get("stealth_mode", True):
                        uc_options.add_argument("--disable-blink-features=AutomationControlled")
                        
                    # 隨機視窗大小
                    if anti_detection.get("randomize_viewport", True):
                        width = random.randint(1200, 1600)
                        height = random.randint(800, 1000)
                        uc_options.add_argument(f"--window-size={width},{height}")
                    else:
                        uc_options.add_argument('--start-maximized')
                    
                    # 禁用圖片加載
                    if not config.get("advanced_settings", {}).get("load_images", True):
                        uc_options.add_argument('--blink-settings=imagesEnabled=false')
                    
                    # 啟用效能紀錄器
                    uc_options.add_argument("--enable-precise-memory-info")
                    uc_options.add_argument("--disable-default-apps")
                    
                    # 初始化 undetected_chromedriver
                    driver = uc.Chrome(options=uc_options)
                    print("使用 undetected_chromedriver 成功初始化Chrome瀏覽器")
                    
                except ImportError:
                    print("未找到undetected_chromedriver模組，嘗試其他方法")
                except Exception as uc_e:
                    print(f"使用undetected_chromedriver失敗: {str(uc_e)}")
            
            # 如果前面的方法沒有成功，嘗試標準方法
            if driver is None:
                try:
                    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
                    print("使用webdriver-manager成功初始化Chrome瀏覽器")
                except Exception as e:
                    print(f"使用webdriver-manager失敗: {str(e)}")
                    
                    # 方法3: 嘗試使用默認方式初始化
                    try:
                        driver = webdriver.Chrome(options=chrome_options)
                        print("使用默認方式成功初始化Chrome瀏覽器")
                    except Exception as e2:
                        print(f"使用默認方式失敗: {str(e2)}")
                        
                        # 方法4: 提示用戶手動指定chromedriver路徑
                        print("\n無法自動設置Chrome WebDriver，請手動設置chromedriver路徑")
                        print("您可以從以下網址下載適合您系統的chromedriver: https://chromedriver.chromium.org/downloads")
                        print("下載後請在下方輸入完整路徑")
                        chromedriver_path = input("請輸入chromedriver路徑: ")
                        driver = webdriver.Chrome(service=Service(chromedriver_path), options=chrome_options)
                        print(f"使用指定路徑成功初始化Chrome瀏覽器: {chromedriver_path}")
        
        # 繞過WebDriver檢測
        if anti_detection.get("disable_webdriver", True):
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                """
            })
            print("已設置繞過WebDriver檢測")
        
        # 禁用動畫
        driver.execute_script("document.body.style.webkitAnimationPlayState='paused'")
        
        # 設置cookie
        session_management = config.get("advanced_settings", {}).get("session_management", {})
        if session_management.get("load_cookies", True):
            cookies_file = session_management.get("cookies_file", "./cookies/shopee_cookies.json")
            try:
                if os.path.exists(cookies_file):
                    with open(cookies_file, 'r') as f:
                        cookies = json.load(f)
                        
                    # 先訪問目標網站，然後加入cookie
                    base_url = config.get("base_url", "https://shopee.tw")
                    driver.get(base_url)
                    time.sleep(1)
                    
                    for cookie in cookies:
                        try:
                            driver.add_cookie(cookie)
                        except Exception as cookie_e:
                            print(f"添加cookie時發生錯誤: {str(cookie_e)}")
                    
                    print("已成功載入cookies")
            except Exception as ce:
                print(f"載入cookies失敗: {str(ce)}")
        
        add_evasion_script(driver)
        add_stealth_js(driver)
        
        return driver
    except Exception as e:
        print(f"初始化Chrome WebDriver失敗: {str(e)}")
        traceback.print_exc()
        raise


def wait_for_element(driver: webdriver.Chrome, by: str, selector: str, timeout: int = 10) -> Any:
    """等待元素出現並返回"""
    wait = WebDriverWait(driver, timeout)
    return wait.until(EC.presence_of_element_located((by, selector)))


def safe_click(driver: webdriver.Chrome, element, retries: int = 3) -> bool:
    """安全點擊元素，處理各種點擊異常"""
    for i in range(retries):
        try:
            if isinstance(element, str):
                element = wait_for_element(driver, By.XPATH, element)
            
            # 先嘗試滾動到元素位置
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
            random_sleep(0.5, 1.5)
            
            # 等待元素可點擊
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, element if isinstance(element, str) else ".")))
            
            # 點擊元素
            element.click()
            return True
                
        except ElementClickInterceptedException:
            print(f"點擊被攔截，嘗試JavaScript點擊 (嘗試 {i+1}/{retries})")
            try:
                driver.execute_script("arguments[0].click();", element)
                return True
            except Exception as js_e:
                print(f"JavaScript點擊失敗: {str(js_e)}")
                
        except StaleElementReferenceException:
            print(f"元素已過時，重新獲取 (嘗試 {i+1}/{retries})")
            random_sleep(1.0, 2.0)
            continue
                
        except Exception as e:
            print(f"點擊失敗: {str(e)} (嘗試 {i+1}/{retries})")
            random_sleep(1.0, 2.0)
    
    print("所有點擊嘗試均失敗")
    return False


def scroll_page(driver: webdriver.Chrome, direction: str = "down", amount: int = 500) -> None:
    """滾動頁面"""
    if direction == "down":
        driver.execute_script(f"window.scrollBy(0, {amount});")
    elif direction == "up":
        driver.execute_script(f"window.scrollBy(0, -{amount});")
    elif direction == "top":
        driver.execute_script("window.scrollTo(0, 0);")
    elif direction == "bottom":
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")


def take_screenshot(driver: webdriver.Chrome, config: Dict, page_type: str) -> Optional[str]:
    """截取螢幕截圖"""
    screenshot_config = config.get("advanced_settings", {}).get("screenshot", {})
    if not screenshot_config.get("enabled", False):
        return None
        
    directory = screenshot_config.get("directory", "./screenshots")
    os.makedirs(directory, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename_pattern = screenshot_config.get("filename_pattern", "screenshot_{timestamp}_{page_type}.png")
    filename = filename_pattern.format(timestamp=timestamp, page_type=page_type)
    
    file_path = os.path.join(directory, filename)
    driver.save_screenshot(file_path)
    print(f"已儲存螢幕截圖: {file_path}")
    
    return file_path


def handle_recaptcha(driver: webdriver.Chrome, config: Dict) -> bool:
    """處理reCAPTCHA驗證"""
    recaptcha_config = config.get("advanced_settings", {}).get("recaptcha_handling", {})
    if not recaptcha_config.get("enabled", False):
        return False

    print("檢測是否需要處理reCAPTCHA...")
    
    try:
        # 檢查頁面上是否有reCAPTCHA iframe
        iframe_selector = recaptcha_config.get("iframe_selector", "//iframe[@title='reCAPTCHA']")
        iframes = driver.find_elements(By.XPATH, iframe_selector)
        
        # 增強驗證檢測 - 檢查更多可能的驗證提示
        detect_patterns = recaptcha_config.get("detect_patterns", ["請通過人機驗證", "機器人驗證", "請完成安全驗證"])
        verification_needed = False
        
        # 檢查iframe
        if iframes:
            verification_needed = True
        
        # 檢查文本提示
        for pattern in detect_patterns:
            if pattern in driver.page_source:
                verification_needed = True
                break
                
        # 檢查特定的驗證元素
        verification_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'captcha') or contains(@class, 'verification')]")
        if verification_elements:
            for elem in verification_elements:
                if elem.is_displayed():
                    verification_needed = True
                    break
        
        if not verification_needed:
            print("未檢測到reCAPTCHA")
            return False
            
        print("檢測到驗證碼，嘗試處理...")
        
        # 嘗試多種策略處理驗證碼
        strategies = recaptcha_config.get("bypass_strategies", ["wait_and_click", "iframe_switch", "action_delay"])
        
        # 策略1: 切換到iframe並點擊
        if "iframe_switch" in strategies and iframes:
            # 切換到reCAPTCHA iframe
            driver.switch_to.frame(iframes[0])
            
            # 點擊reCAPTCHA核取方塊
            checkbox_selector = recaptcha_config.get("checkbox_selector", "//div[@class='recaptcha-checkbox-border']")
            try:
                checkbox = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, checkbox_selector))
                )
                safe_click(driver, checkbox)
                random_sleep(2.0, 4.0)
            except Exception as e:
                print(f"點擊驗證框失敗: {str(e)}")
                
            # 切回主頁面
            driver.switch_to.default_content()
        
        # 策略2: 等待和模擬人類行為
        if "wait_and_click" in strategies:
            # 隨機滑鼠移動
            action = ActionChains(driver)
            for _ in range(3):
                action.move_by_offset(random.randint(-100, 100), random.randint(-100, 100))
                action.perform()
                random_sleep(0.3, 1.0)
            
            # 移動到頁面中心
            action.move_to_element(driver.find_element(By.TAG_NAME, "body"))
            action.perform()
            random_sleep(0.5, 1.5)
            
            # 再次檢查並嘗試點擊驗證元素
            try:
                verification_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), '驗證') or contains(text(), '確認') or contains(text(), '繼續')]")
                if verification_buttons:
                    for btn in verification_buttons:
                        if btn.is_displayed():
                            safe_click(driver, btn)
                            random_sleep(1.0, 3.0)
                            break
            except Exception as e:
                print(f"點擊驗證按鈕失敗: {str(e)}")
        
        # 策略3: 動作延遲
        if "action_delay" in strategies:
            random_sleep(5.0, 8.0)
            
        # 截圖記錄驗證處理過程
        take_screenshot(driver, config, "recaptcha_handling")
        
        # 檢查是否成功通過驗證
        for pattern in detect_patterns:
            if pattern in driver.page_source:
                print("可能未成功通過驗證，但繼續執行")
                take_screenshot(driver, config, "recaptcha_failed")
                return False
        
        print("驗證處理完成")
        take_screenshot(driver, config, "recaptcha_handled")
        return True
        
    except Exception as e:
        print(f"處理reCAPTCHA時發生錯誤: {str(e)}")
        traceback.print_exc()
        
        # 確保切回主頁面
        try:
            driver.switch_to.default_content()
        except:
            pass
            
        return False


# ===== 搜尋參數處理區 =====

def search_keyword(driver: webdriver.Chrome, config: Dict) -> bool:
    """搜尋關鍵字"""
    try:
        search_config = config.get("search_parameters", {}).get("keyword", {})
        search_value = search_config.get("default", "")
        
        print(f"搜尋關鍵字: {search_value}")
        
        # 輸入搜尋關鍵字
        input_selector = search_config.get("input_selector")
        if (input_selector):
            try:
                search_input = wait_for_element(driver, By.XPATH, input_selector)
                search_input.clear()
                search_input.send_keys(search_value)
                random_sleep(1.0, 2.0)
            except Exception as input_e:
                print(f"輸入搜尋關鍵字時發生錯誤: {str(input_e)}")
                return False
        
        # 提交搜尋
        submit_selector = search_config.get("submit_selector")
        if submit_selector:
            try:
                submit_button = wait_for_element(driver, By.XPATH, submit_selector)
                safe_click(driver, submit_button)
                
                # 等待頁面加載
                wait_time = search_config.get("wait_after_submit", 5)
                random_sleep(wait_time, wait_time + 2)
            except Exception as submit_e:
                print(f"提交搜尋時發生錯誤: {str(submit_e)}")
                return False
        
        return True
        
    except Exception as e:
        print(f"搜尋關鍵字時發生錯誤: {str(e)}")
        traceback.print_exc()
        return False


def select_shop(driver: webdriver.Chrome, config: Dict) -> bool:
    """選擇商店"""
    try:
        shop_config = config.get("search_parameters", {}).get("shop", {})
        shop_value = shop_config.get("default", "")
        
        if not shop_value:
            print("未指定商店，跳過選擇")
            return True
            
        print(f"選擇商店: {shop_value}")
        
        # 構建商店URL
        base_url = config.get("base_url", "https://shopee.tw")
        shop_url = shop_config.get("url", "")
        
        if shop_url:
            full_url = normalize_url(shop_url, base_url)
            print(f"直接訪問商店URL: {full_url}")
            driver.get(full_url)
            random_sleep(3.0, 5.0)
            return True
        
        # 或透過搜尋找到商店
        selector = shop_config.get("selector").replace("{value}", shop_value)
        alternative_selector = shop_config.get("alternative_selector", "").replace("{value}", shop_value)
        
        selectors = [selector]
        if alternative_selector:
            selectors.append(alternative_selector)
            
        shop_found = False
        for sel in selectors:
            try:
                shop_elements = driver.find_elements(By.XPATH, sel)
                
                if shop_elements:
                    for shop in shop_elements:
                        if shop.is_displayed():
                            # 滾動到商店位置
                            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", shop)
                            random_sleep(1.0, 2.0)
                            
                            # 點擊商店
                            safe_click(driver, shop)
                            
                            # 等待頁面加載
                            wait_time = shop_config.get("wait_after_click", 5)
                            random_sleep(wait_time, wait_time + 2)
                            
                            shop_found = True
                            break
                    
                    if shop_found:
                        break
            except Exception as sel_e:
                print(f"使用選擇器 {sel} 選擇商店失敗: {str(sel_e)}")
        
        # 截圖
        if shop_found:
            take_screenshot(driver, config, "shop_selected")
            return True
        else:
            print(f"找不到商店: {shop_value}")
            take_screenshot(driver, config, "shop_not_found")
            return False
        
    except Exception as e:
        print(f"選擇商店時發生錯誤: {str(e)}")
        traceback.print_exc()
        return False


def select_category(driver: webdriver.Chrome, config: Dict) -> bool:
    """選擇商品類別"""
    try:
        category_config = config.get("search_parameters", {}).get("category", {})
        category_value = category_config.get("default", "")
        
        if not category_value:
            print("未指定商品類別，跳過選擇")
            return True
            
        print(f"選擇商品類別: {category_value}")
        
        # 選擇特定類別
        selector = category_config.get("selector").replace("{value}", category_value)
        try:
            # 等待頁面載入完成
            random_sleep(2.0, 3.0)
            
            category_elements = driver.find_elements(By.XPATH, selector)
            
            if category_elements:
                for category in category_elements:
                    if category.is_displayed():
                        # 滾動到類別位置
                        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", category)
                        random_sleep(1.0, 2.0)
                        
                        # 點擊類別
                        safe_click(driver, category)
                        
                        # 等待頁面加載
                        wait_time = category_config.get("wait_after_click", 3)
                        random_sleep(wait_time, wait_time + 1)
                        
                        take_screenshot(driver, config, "category_selected")
                        return True
            
            print(f"找不到商品類別: {category_value}")
            return False
            
        except TimeoutException:
            print(f"找不到商品類別: {category_value}")
            return False
        
    except Exception as e:
        print(f"選擇商品類別時發生錯誤: {str(e)}")
        traceback.print_exc()
        return False


def select_product(driver: webdriver.Chrome, config: Dict) -> bool:
    """選擇商品"""
    try:
        product_config = config.get("search_parameters", {}).get("product", {})
        product_value = product_config.get("default", "")
        
        if not product_value:
            print("未指定商品，跳過選擇")
            return True
            
        print(f"選擇商品: {product_value}")
        
        # 滾動頁面以確保所有商品都已載入
        scroll_behavior = config.get("advanced_settings", {}).get("scroll_behavior", {})
        if scroll_behavior.get("enable_lazy_loading", True):
            for _ in range(scroll_behavior.get("max_scroll_attempts", 5)):
                scroll_page(driver, "down", 300)
                random_sleep(scroll_behavior.get("scroll_pause", 1.5), scroll_behavior.get("scroll_pause", 1.5) + 1)
        
        # 選擇特定商品
        selector = product_config.get("selector").replace("{value}", product_value)
        
        try:
            product_elements = driver.find_elements(By.XPATH, selector)
            
            if product_elements:
                for product in product_elements:
                    if product.is_displayed():
                        # 滾動到商品位置
                        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", product)
                        random_sleep(1.0, 2.0)
                        
                        # 點擊商品
                        safe_click(driver, product)
                        
                        # 等待頁面加載
                        wait_time = product_config.get("wait_after_click", 3)
                        random_sleep(wait_time, wait_time + 2)
                        
                        # 截圖
                        take_screenshot(driver, config, "product_selected")
                        
                        return True
            
            print(f"找不到商品: {product_value}")
            # 嘗試截圖以便調試
            take_screenshot(driver, config, "product_not_found")
            return False
            
        except Exception as find_e:
            print(f"查找商品時發生錯誤: {str(find_e)}")
            return False
        
    except Exception as e:
        print(f"選擇商品時發生錯誤: {str(e)}")
        traceback.print_exc()
        return False


def select_variation(driver: webdriver.Chrome, config: Dict) -> bool:
    """選擇商品選項"""
    try:
        variation_config = config.get("search_parameters", {}).get("variation", {})
        variation_value = variation_config.get("default", "")
        
        if not variation_value:
            print("未指定商品選項，跳過選擇")
            return True
            
        print(f"選擇商品選項: {variation_value}")
        
        # 等待頁面加載
        random_sleep(2.0, 3.0)
        
        # 選擇特定選項
        selector = variation_config.get("selector").replace("{value}", variation_value)
        try:
            variation_elements = driver.find_elements(By.XPATH, selector)
            
            if variation_elements:
                for variation in variation_elements:
                    if variation.is_displayed():
                        # 滾動到選項位置
                        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", variation)
                        random_sleep(0.5, 1.5)
                        
                        # 點擊選項
                        safe_click(driver, variation)
                        
                        # 等待選擇生效
                        wait_time = variation_config.get("wait_after_click", 1)
                        random_sleep(wait_time, wait_time + 1)
                        
                        return True
            
            print(f"找不到商品選項: {variation_value}")
            return False
            
        except TimeoutException:
            print(f"找不到商品選項: {variation_value}")
            return False
        
    except Exception as e:
        print(f"選擇商品選項時發生錯誤: {str(e)}")
        traceback.print_exc()
        return False


def add_to_cart(driver: webdriver.Chrome, config: Dict) -> bool:
    """加入購物車"""
    try:
        add_to_cart_config = config.get("search_parameters", {}).get("addToCart", {})
        
        print("加入購物車")
        
        # 點擊加入購物車按鈕
        selector = add_to_cart_config.get("selector")
        if selector:
            try:
                add_to_cart_button = wait_for_element(driver, By.XPATH, selector)
                safe_click(driver, add_to_cart_button)
                
                # 等待操作完成
                wait_time = add_to_cart_config.get("wait_after_click", 2)
                random_sleep(wait_time, wait_time + 1)
                
                # 截圖
                take_screenshot(driver, config, "added_to_cart")
                
                return True
                
            except TimeoutException:
                print("找不到加入購物車按鈕")
                return False
        
        return True
        
    except Exception as e:
        print(f"加入購物車時發生錯誤: {str(e)}")
        traceback.print_exc()
        return False


# ===== 列表頁面處理區 =====

def extract_product_list(driver: webdriver.Chrome, config: Dict) -> List[Dict]:
    """從商品列表頁面提取商品數據"""
    print("提取商品列表數據...")
    
    # 確保頁面已完全加載
    scroll_behavior = config.get("advanced_settings", {}).get("scroll_behavior", {})
    if scroll_behavior.get("enable_lazy_loading", True):
        for _ in range(scroll_behavior.get("max_scroll_attempts", 5)):
            scroll_page(driver, "down", 500)
            random_sleep(scroll_behavior.get("scroll_pause", 1.5), scroll_behavior.get("scroll_pause", 1.5) + 1)
    
    # 獲取頁面源碼
    page_source = driver.page_source
    
    # 提取商品列表數據
    return extract_list_items(page_source, config)


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
            
            # 提取每個字段
            for field_name, field_config in fields_config.items():
                field_xpath = field_config.get("xpath")
                field_type = field_config.get("type", "text")
                
                try:
                    if field_type == "text":
                        value = item.xpath(field_xpath)
                        if value:
                            result[field_name] = clean_text(value[0])
                        else:
                            # 嘗試使用備用XPath
                            fallback_xpath = field_config.get("fallback_xpath")
                            if fallback_xpath:
                                fallback_value = item.xpath(fallback_xpath)
                                result[field_name] = clean_text(fallback_value[0]) if fallback_value else ""
                            else:
                                result[field_name] = ""
                    elif field_type == "attribute":
                        value = item.xpath(field_xpath)
                        result[field_name] = value[0] if value else ""
                    elif field_type == "html":
                        elements = item.xpath(field_xpath)
                        if elements:
                            result[field_name] = html.tostring(elements[0], encoding='unicode')
                        else:
                            result[field_name] = ""
                    elif field_type == "list":
                        values = item.xpath(field_xpath)
                        result[field_name] = [clean_text(v) for v in values] if values else []
                        
                except Exception as field_e:
                    print(f"提取字段 '{field_name}' 時發生錯誤: {str(field_e)}")
                    result[field_name] = ""
            
            results.append(result)
            
        except Exception as item_e:
            print(f"處理列表項目 #{i+1} 時發生錯誤: {str(item_e)}")
    
    return results

def fetch_product_list(driver: webdriver.Chrome, config: Dict) -> List[Dict]:
    """獲取商品列表（處理多頁）"""
    print("獲取商品列表...")
    
    # 獲取總頁數
    try:
        total_page_selector = config.get("list_page", {}).get("total_count_xpath", "//span[@class='shopee-mini-page-controller__total']")
        total_page_element = wait_for_element(driver, By.XPATH, total_page_selector)
        total_pages = int(total_page_element.text.strip())
        print(f"總頁數: {total_pages}")
    except:
        print("無法獲取總頁數，假設只有1頁")
        total_pages = 1
    
    # 限制最大頁數
    max_pages = config.get("pagination", {}).get("max_pages", 3)
    if (max_pages > 0 and total_pages > max_pages):
        print(f"限制爬取頁數為 {max_pages}")
        total_pages = max_pages
    
    all_products = []
    
    # 處理首頁
    current_products = extract_product_list(driver, config)
    all_products.extend(current_products)
    
    # 遍歷其餘頁面（如果有）
    for page in range(1, total_pages):
        print(f"處理第 {page+1} 頁...")
        
        # 生成下一頁URL
        if config.get("advanced_settings", {}).get("url_format", {}).get("pattern"):
            url_pattern = config.get("advanced_settings", {}).get("url_format", {}).get("pattern")
            base_url = config.get("base_url", "https://shopee.tw")
            shop_url = config.get("search_parameters", {}).get("shop", {}).get("url", "")
            next_url = url_pattern.format(base_url=base_url, shop_url=shop_url, page=page)
            driver.get(next_url)
        else:
            # 或者點擊下一頁按鈕
            next_page_selector = config.get("pagination", {}).get("next_page_selector")
            try:
                next_button = wait_for_element(driver, By.XPATH, next_page_selector)
                safe_click(driver, next_button)
            except:
                print(f"無法點擊下一頁按鈕，停止爬取更多頁面")
                break
        
        # 等待新頁面加載
        random_sleep(2.0, 4.0)
        
        # 處理reCAPTCHA（如果出現）
        handle_recaptcha(driver, config)
        
        # 提取該頁數據
        current_products = extract_product_list(driver, config)
        all_products.extend(current_products)
        
        # 截圖
        take_screenshot(driver, config, f"list_page_{page+1}")
    
    return all_products


# ===== 詳情頁面處理區 =====

def extract_product_detail(driver: webdriver.Chrome, config: Dict) -> Dict[str, Any]:
    """提取商品詳情頁面數據"""
    print("提取商品詳情頁面數據...")
    
    # 確保頁面已完全加載
    scroll_behavior = config.get("advanced_settings", {}).get("scroll_behavior", {})
    if scroll_behavior.get("enable_lazy_loading", True):
        for _ in range(scroll_behavior.get("max_scroll_attempts", 5)):
            scroll_page(driver, "down", 300)
            random_sleep(scroll_behavior.get("scroll_pause", 1.5), scroll_behavior.get("scroll_pause", 1.5) + 1)
    
    # 處理reCAPTCHA（如果出現）
    handle_recaptcha(driver, config)
    
    # 截圖
    take_screenshot(driver, config, "product_detail")
    
    # 獲取頁面源碼
    page_source = driver.page_source
    
    # 清理HTML標籤
    soup = BeautifulSoup(page_source, 'html.parser')
    # 刪除所有 <style> 標籤
    for tag in soup.find_all('style'):
        tag.extract()
    # 刪除所有 <svg> 標籤
    for tag in soup.find_all('svg'):
        tag.extract()
    # 使用 prettify() 函式進行格式整齊化
    clean_html = soup.prettify()
    
    # 從頁面源碼提取數據
    detail_page_config = config.get("detail_page", {})
    tree = html.fromstring(clean_html)
    
    result = {}
    
    try:
        # 提取基本商品信息
        for field_name, field_config in detail_page_config.get("fields", {}).items():
            field_xpath = field_config.get("xpath")
            field_type = field_config.get("type", "text")
            
            try:
                if field_type == "text":
                    value = tree.xpath(field_xpath)
                    result[field_name] = clean_text(value[0]) if value else ""
                elif field_type == "attribute":
                    value = tree.xpath(field_xpath)
                    
                    # 處理特殊情況，如圖片URL從style屬性中提取
                    if field_name == "images" and field_config.get("pattern"):
                        pattern = field_config.get("pattern")
                        images = []
                        for style_str in value:
                            match = re.search(pattern, style_str)
                            if match:
                                images.append(match.group(1))
                        result[field_name] = images
                    else:
                        result[field_name] = value[0] if value else ""
                elif field_type == "html":
                    elements = tree.xpath(field_xpath)
                    if elements:
                        # 獲取HTML文本
                        element_html = html.tostring(elements[0], encoding='unicode')
                        # 清理HTML，只保留文本
                        result[field_name] = clean_html_tag(element_html)
                    else:
                        result[field_name] = ""
                elif field_type == "list":
                    values = tree.xpath(field_xpath)
                    result[field_name] = [clean_text(v) for v in values] if values else []
                    
            except Exception as field_e:
                print(f"提取字段 '{field_name}' 時發生錯誤: {str(field_e)}")
                result[field_name] = ""
    
    except Exception as e:
        print(f"提取商品詳情頁面數據時發生錯誤: {str(e)}")
        traceback.print_exc()
    
    return result


def fetch_product_details(driver: webdriver.Chrome, products: List[Dict], config: Dict) -> List[Dict]:
    """獲取每個商品的詳細信息"""
    print(f"準備獲取 {len(products)} 個商品的詳細信息...")
    
    product_details = []
    
    for i, product in enumerate(products):
        print(f"獲取第 {i+1}/{len(products)} 個商品詳細信息...")
        
        # 獲取商品詳情頁URL
        detail_link = product.get("detail_link", "")
        if not detail_link:
            print("商品詳情鏈接為空，跳過此商品")
            continue
        
        # 構建完整URL
        base_url = config.get("base_url", "https://shopee.tw")
        product_url = normalize_url(detail_link, base_url)
        
        try:
            # 訪問商品詳情頁
            driver.get(product_url)
            random_sleep(3.0, 5.0)
            
            # 提取詳細信息
            detail_info = extract_product_detail(driver, config)
            
            # 合併基本信息和詳細信息
            full_info = {**product, **detail_info}
            product_details.append(full_info)
            
        except Exception as e:
            print(f"獲取商品詳細信息時發生錯誤: {str(e)}")
            traceback.print_exc()
            # 繼續下一個商品
    
    return product_details


# ===== 結果處理區 =====

def save_results(results: Dict[str, Any], config: Dict) -> Optional[str]:
    """保存結果到JSON檔案"""
    if not results:
        print("沒有結果可保存")
        return None
        
    os.makedirs("output", exist_ok=True)
    
    # 使用商店名稱作為檔名的一部分
    shop = config.get("search_parameters", {}).get("shop", {}).get("default", "")
    keyword = config.get("search_parameters", {}).get("keyword", {}).get("default", "")
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    
    filename = f"shopee_{shop}_{keyword}_{timestamp}"
    # 移除特殊字符
    filename = re.sub(r'[\\/:*?"<>|]', '_', filename)
    
    output_file = f"output/{filename}.json"
    
    # 格式化結果以便 JSON 序列化
    formatted_results = format_for_json(results)
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(formatted_results, f, ensure_ascii=False, indent=2)
    
    print(f"結果已儲存至: {output_file}")
    
    return output_file


def handle_error(driver: webdriver.Chrome, config: Dict, error: Exception) -> None:
    """處理錯誤並保存錯誤頁面"""
    print(f"發生錯誤: {str(error)}")
    traceback.print_exc()
    
    if not driver:
        return
        
    # 檢查是否需要保存錯誤頁面
    if config.get("advanced_settings", {}).get("save_error_page", False):
        error_page_dir = config.get("advanced_settings", {}).get("error_page_dir", "./debug")
        os.makedirs(error_page_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        error_filename = f"error_{timestamp}.html"
        error_filepath = os.path.join(error_page_dir, error_filename)
        
        with open(error_filepath, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
            
        print(f"錯誤頁面已儲存至: {error_filepath}")
        
        # 順便截圖
        screenshot_path = os.path.join(error_page_dir, f"error_{timestamp}.png")
        driver.save_screenshot(screenshot_path)
        print(f"錯誤頁面截圖已儲存至: {screenshot_path}")


# ===== 輔助函數區 =====

def login(driver: webdriver.Chrome, config: Dict) -> bool:
    """登入蝦皮帳號"""
    print("嘗試登入蝦皮帳號...")
    
    login_config = config.get("login", {})
    session_management = config.get("advanced_settings", {}).get("session_management", {})
    
    # 檢查是否需要登入
    if not login_config.get("required", False) and not config.get("advanced_settings", {}).get("login_required", False):
        print("配置不需要登入，跳過登入步驟")
        return True
    
    # 獲取登入頁面
    try:
        login_url = login_config.get("url", f"{config.get('base_url', 'https://shopee.tw')}/buyer/login")
        driver.get(login_url)
        random_sleep(3.0, 5.0)
        
        # 檢查是否已經登入
        try:
            success_indicators = login_config.get("success_indicators", {})
            url_contains = success_indicators.get("url_contains", "user")
            
            if url_contains in driver.current_url:
                print("URL檢查: 已經登入")
                return True
                
            element_present = success_indicators.get("element_present", "//div[contains(@class, 'shopee-avatar')]")
            avatar_elements = driver.find_elements(By.XPATH, element_present)
            
            if avatar_elements and any(e.is_displayed() for e in avatar_elements):
                print("元素檢查: 已經登入，無需再次登入")
                return True
                
        except Exception as check_e:
            print(f"檢查登入狀態時發生錯誤: {str(check_e)}")
        
        # 處理配置中的用戶名和密碼
        username = login_config.get("username", "")
        password = login_config.get("password", "")
        
        if not username or not password:
            print("未設置用戶名或密碼，需要手動登入")
            
            # 提示用戶手動登入
            print("請在瀏覽器中手動登入蝦皮帳號，完成後按Enter繼續...")
            input()
            
            # 等待登入完成
            random_sleep(5.0, 10.0)
            
            # 處理可能的驗證碼
            handle_recaptcha(driver, config)
            
            # 驗證是否登入成功
            try:
                success_wait_time = login_config.get("wait_after_login", 5)
                random_sleep(success_wait_time, success_wait_time + 3)
                
                # 再次檢查是否登入成功
                element_present = success_indicators.get("element_present", "//div[contains(@class, 'shopee-avatar')]")
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, element_present)))
                print("手動登入成功")
                
                # 保存Cookie
                if session_management.get("save_cookies", True):
                    save_cookies(driver, config)
                    
                return True
            except:
                print("無法確認登入狀態，但繼續執行")
                take_screenshot(driver, config, "login_uncertain")
                return True
        
        # 自動登入
        try:
            fields = login_config.get("fields", {})
            
            # 輸入用戶名
            username_selector = fields.get("username_selector", "//input[@name='loginKey']")
            username_input = wait_for_element(driver, By.XPATH, username_selector, timeout=15)
            driver.execute_script("arguments[0].value = '';", username_input)
            random_sleep(0.5, 1.0)
            
            # 模擬人類輸入
            for char in username:
                username_input.send_keys(char)
                random_sleep(0.05, 0.15)
            
            random_sleep(0.5, 1.5)
            
            # 輸入密碼
            password_selector = fields.get("password_selector", "//input[@name='password']")
            password_input = wait_for_element(driver, By.XPATH, password_selector, timeout=15)
            driver.execute_script("arguments[0].value = '';", password_input)
            random_sleep(0.5, 1.0)
            
            # 模擬人類輸入
            for char in password:
                password_input.send_keys(char)
                random_sleep(0.05, 0.1)
            
            random_sleep(1.0, 2.0)
            
            # 點擊登入按鈕
            submit_selector = fields.get("submit_selector", "//button[contains(@class, 'btn-solid-primary')]")
            login_button = wait_for_element(driver, By.XPATH, submit_selector, timeout=15)
            safe_click(driver, login_button)
            
            # 等待登入完成
            success_wait_time = login_config.get("wait_after_login", 5)
            random_sleep(success_wait_time, success_wait_time + 3)
            
            # 處理可能的驗證碼
            handle_recaptcha(driver, config)
            
            # 儲存遊覽器截圖
            take_screenshot(driver, config, "after_login")
            
            # 驗證是否登入成功
            try:
                element_present = success_indicators.get("element_present", "//div[contains(@class, 'shopee-avatar')]")
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, element_present)))
                print("自動登入成功")
                
                # 保存Cookie
                if session_management.get("save_cookies", True):
                    save_cookies(driver, config)
                
                return True
            except:
                print("自動登入可能失敗，但繼續執行")
                take_screenshot(driver, config, "login_failed")
                # 提示用戶手動登入
                print("自動登入可能失敗，請在瀏覽器中手動登入，完成後按Enter繼續...")
                input()
                return True
            
        except Exception as login_e:
            print(f"自動登入過程中發生錯誤: {str(login_e)}")
            traceback.print_exc()
            
            # 提示用戶手動登入
            print("自動登入失敗，請在瀏覽器中手動登入，完成後按Enter繼續...")
            input()
            
            # 保存Cookie
            if session_management.get("save_cookies", True):
                save_cookies(driver, config)
            
            return True
    
    except Exception as e:
        print(f"訪問登入頁面時發生錯誤: {str(e)}")
        traceback.print_exc()
        return False


# 修改 save_cookies 函數，確保完整保存所有必要cookie
def save_cookies(driver, config):
    try:
        session_management = config.get("advanced_settings", {}).get("session_management", {})
        cookies_file = session_management.get("cookies_file", "./cookies/shopee_cookies.json")
        
        # 確保目錄存在
        os.makedirs(os.path.dirname(cookies_file), exist_ok=True)
        
        # 獲取所有cookie，包括HttpOnly
        cookies = driver.get_cookies()
        
        # 添加時間戳，以便追踪cookie有效期
        cookies_data = {
            "timestamp": datetime.now().isoformat(),
            "cookies": cookies
        }
        
        # 保存cookie到文件
        with open(cookies_file, 'w') as f:
            json.dump(cookies_data, f)
        
        print(f"已保存cookies到: {cookies_file}")
    except Exception as e:
        print(f"保存cookies時發生錯誤: {str(e)}")


def parse_product_images(styles: List[str]) -> List[str]:
    """從style屬性中提取商品圖片URL"""
    image_urls = []
    for style in styles:
        match = re.search(r'url\("([^"]+)"\)', style)
        if match:
            image_urls.append(match.group(1))
    return image_urls


def clean_html_content(html_text: str) -> str:
    """清理HTML，只保留文本內容並適當格式化"""
    if not html_text:
        return ""
        
    soup = BeautifulSoup(html_text, 'html.parser')
    
    # 移除所有script和style元素
    for script in soup(["script", "style"]):
        script.extract()
    
    # 獲取文本
    text = soup.get_text()
    
    # 處理多餘空白行
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    text = "\n".join(lines)
    
    return text


def add_evasion_script(driver: webdriver.Chrome) -> None:
    """添加反檢測JavaScript腳本"""
    try:
        evasion_script = """
        // 隱藏 Selenium 特徵
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        
        // 隱藏自動化特徵
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
        
        // 添加假的WebGL
        if (!window.WebGLRenderingContext) {
            window.WebGLRenderingContext = {};
        }
        
        // 修改user-agent信息
        Object.defineProperty(navigator, 'plugins', {
            get: () => {
                // 創建假的插件陣列
                let fakePlugins = [];
                for (let i=0; i<5; i++) {
                    fakePlugins.push({
                        name: `Plugin ${i}`,
                        description: `Fake Plugin ${i}`,
                        filename: `plugin${i}.dll`
                    });
                }
                return fakePlugins;
            }
        });
        
        // 偽造Canvas指紋
        const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
        HTMLCanvasElement.prototype.toDataURL = function(type) {
            if (this.width > 10 && this.height > 10) {
                // 輕微修改Canvas數據
                const context = this.getContext('2d');
                context.fillStyle = 'rgba(0, 0, 0, 0.0001)';
                context.fillRect(0, 0, 1, 1);
            }
            return originalToDataURL.apply(this, arguments);
        };
        """
        
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": evasion_script
        })
        
        print("已添加反檢測腳本")
    except Exception as e:
        print(f"添加反檢測腳本失敗: {str(e)}")


def add_stealth_js(driver):
    """添加 JavaScript 以繞過檢測"""
    js = """
    // 覆蓋 webdriver 屬性
    Object.defineProperty(navigator, 'webdriver', {
        get: () => false,
    });
    
    // 覆蓋 chrome 屬性
    window.chrome = {
        runtime: {},
    };
    
    // 覆蓋語言和平台信息
    const originalNavigator = navigator;
    Object.defineProperty(window, 'navigator', {
        get: () => {
            const nav = {};
            for (let prop in originalNavigator) {
                nav[prop] = originalNavigator[prop];
            }
            nav.languages = ['zh-TW', 'zh', 'en-US', 'en'];
            nav.platform = 'MacIntel';
            return nav;
        }
    });
    
    // 模擬完整的權限API
    const originalQuery = window.navigator.permissions.query;
    window.navigator.permissions.query = (parameters) => (
        parameters.name === 'notifications' ?
        Promise.resolve({ state: Notification.permission }) :
        originalQuery(parameters)
    );
    """
    
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": js
    })
    
    print("已添加增強型反檢測腳本")


# ===== 主程序區 =====

def compose_products(dom):
    """組合商品列表資料"""
    if dom is None:
        return []
        
    links = dom.xpath('//div[contains(@class, "shop-search-result-view__item")]/a/@href')
    titles = dom.xpath('//div[contains(@class, "shop-search-result-view__item")]/a//img/@alt')
    products = []
    
    for idx, link in enumerate(links):
        try:
            products.append({
                'title': titles[idx] if idx < len(titles) else "",
                'link': link
            })
        except Exception as e:
            print(f"處理商品索引 {idx} 時出錯: {str(e)}")
    
    return products


def fetch_products(driver: webdriver.Chrome, product_list: List[Dict], config: Dict) -> List[Dict]:
    """獲取商品詳細信息"""
    products = []
    
    for idx, item in enumerate(product_list):
        print(f'獲取第 {idx+1}/{len(product_list)} 個商品詳細信息')
        
        try:
            # 獲取商品URL
            link = item.get('link', '')
            if not link:
                print("商品鏈接為空，跳過此商品")
                continue
                
            # 拼接完整URL
            base_url = config.get("base_url", "https://shopee.tw")
            full_url = normalize_url(link, base_url)
            
            # 訪問商品頁面
            driver.get(full_url)
            random_sleep(3.0, 5.0)
            
            # 處理可能的reCAPTCHA
            handle_recaptcha(driver, config)
            
            # 等待頁面加載
            wait_for_element(driver, By.XPATH, "//div[@class='product-briefing']")
            
            # 獲取頁面源碼
            results = driver.find_element(By.ID, "main").get_attribute('innerHTML')
            
            # 清理HTML
            soup = BeautifulSoup(results, 'html.parser')
            for tag in soup.find_all(['style', 'script', 'svg', 'path', 'polygon']):
                tag.extract()
                
            # 提取商品詳細信息
            product_info = parse_product_detail(soup, item)
            products.append(product_info)
            
        except TimeoutException:
            print(f"獲取商品 {idx+1} 詳細信息超時，跳過")
            continue
        except Exception as e:
            print(f"獲取商品 {idx+1} 詳細信息時發生錯誤: {str(e)}")
            traceback.print_exc()
            continue
    
    return products


def parse_product_detail(soup: BeautifulSoup, product_info: Dict) -> Dict:
    """解析商品詳細信息"""
    result = {
        'title': product_info.get('title', ''),
        'link': product_info.get('link', '')
    }
    
    # 提取價格
    price = ''
    price_elem = soup.find('div', {'class': 'product-briefing'})
    if price_elem:
        price_text = price_elem.find(string=re.compile(r'\$'))
        if price_text:
            price = price_text.strip().replace("$", "")
    result['price'] = price
    
    # 提取庫存
    stock = ''
    stock_elem = soup.select_one('label:-soup-contains("商品數量") + div')
    if stock_elem:
        stock = stock_elem.text.strip()
    result['stock'] = stock
    
    # 提取出貨地
    from_address = ''
    address_elem = soup.select_one('label:-soup-contains("出貨地") + div')
    if address_elem:
        from_address = address_elem.text.strip()
    result['fromAddress'] = from_address
    
    # 提取商品詳情
    detail = ''
    detail_elem = soup.select_one('div:-soup-contains("商品詳情") + div')
    if detail_elem:
        detail = detail_elem.get_text(strip=True)
        # 不管是斷行幾次，都改成只斷行1次
        detail = re.sub(r'\n+', '\n', detail)
    result['detail'] = detail
    
    # 提取商品規格
    spec_elem = soup.select_one('div:-soup-contains("商品規格") + div')
    if spec_elem:
        result['specifications'] = spec_elem.get_text(strip=True)
    
    # 提取分類標籤
    tag_elems = soup.select('label:-soup-contains("分類") + div a')
    tags = [tag.text.strip() for tag in tag_elems if tag.text.strip() != '蝦皮購物']
    result['tags'] = tags
    
    # 提取商品圖片
    image_elems = soup.select('div[style*="background-image:"]')
    result['images'] = parse_product_images([elem.get('style', '') for elem in image_elems])
    
    return result


def main() -> None:
    """主函數：執行蝦皮爬蟲流程"""
    driver = None
    
    try:
        # 1. 載入配置
        config_path = "../../../config/shopee/basic/product.json"
        config = load_config(config_path)
        
        # 2. 設置WebDriver
        driver = setup_webdriver(config)
        
        # 添加反檢測腳本
        add_evasion_script(driver)
        
        # 獲取參數
        base_url = config.get("base_url", "https://shopee.tw")
        keyword = config.get("search_parameters", {}).get("keyword", {}).get("default", "")
        shop = config.get("search_parameters", {}).get("shop", {}).get("default", "")
        product = config.get("search_parameters", {}).get("product", {}).get("default", "")
        
        # 3. 訪問初始URL
        initial_url = base_url
        print(f"訪問初始URL: {initial_url}")
        driver.get(initial_url)
        
        # 設置隱式等待
        driver.implicitly_wait(5)
        
        # 等待頁面載入完成
        random_sleep(2.0, 4.0)
        
        # 處理reCAPTCHA（如果出現）
        handle_recaptcha(driver, config)
        
        # 4. 登入蝦皮帳號
        print("進行蝦皮帳號登入操作（此步驟必要，否則無法查看商品詳細頁面）")
        retry_count = config.get("login", {}).get("retry_attempts", 2)
        
        login_success = False
        for attempt in range(retry_count + 1):
            if attempt > 0:
                print(f"第 {attempt} 次嘗試登入...")
            
            login_success = login(driver, config)
            if login_success:
                break
            
            random_sleep(2.0, 3.0)
        
        if not login_success:
            print("警告：登入失敗可能導致無法獲取商品詳細資訊，但繼續執行程序")
        else:
            print("登入成功，繼續後續操作")
            
        # 保存登入後的Cookie
        save_cookies(driver, config)
        
        # 執行後續操作...
        # [保持原有的後續流程]
        
        # 獲取參數
        base_url = config.get("base_url", "https://shopee.tw")
        keyword = config.get("search_parameters", {}).get("keyword", {}).get("default", "")
        shop = config.get("search_parameters", {}).get("shop", {}).get("default", "")
        product = config.get("search_parameters", {}).get("product", {}).get("default", "")
        
        # 3. 訪問初始URL
        initial_url = base_url
        print(f"訪問初始URL: {initial_url}")
        driver.get(initial_url)
        
        # 設置隱式等待
        driver.implicitly_wait(5)
        
        # 處理reCAPTCHA（如果出現）
        handle_recaptcha(driver, config)
        
        # 4. 登入蝦皮帳號（蝦皮需要登入才能查看商品詳細頁面）
        print("進行蝦皮帳號登入操作（此步驟必要，否則無法查看商品詳細頁面）")
        login_success = login(driver, config)
        if not login_success:
            print("警告：登入失敗可能導致無法獲取商品詳細資訊，但繼續執行程序")
            # 可以選擇在這裡加入重試機制，或提示用戶重新執行程序
        else:
            print("登入成功，繼續後續操作")
        
        # 5. 搜尋關鍵字
        if keyword:
            print(f"搜尋關鍵字: {keyword}")
            search_keyword(driver, config)
            random_sleep(3.0, 5.0)
            
            # 處理reCAPTCHA（如果出現）
            handle_recaptcha(driver, config)
            
            # 截圖
            take_screenshot(driver, config, "search_results")
        
        # 6. 選擇商店
        if shop:
            select_shop(driver, config)
            random_sleep(3.0, 5.0)
            
            # 處理reCAPTCHA（如果出現）
            handle_recaptcha(driver, config)
            
            # 截圖
            take_screenshot(driver, config, "shop_page")
        
        # 7. 獲取商品列表
        print("獲取商品列表")
        try:
            # 獲取總頁數
            total_page_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//span[@class="shopee-mini-page-controller__total"]'))
            )
            total_pages = int(total_page_element.text)
            print(f"總頁數: {total_pages}")
            
            # 限制爬取頁數
            max_pages = config.get("pagination", {}).get("max_pages", 3)
            if max_pages > 0 and total_pages > max_pages:
                print(f"限制爬取頁數為 {max_pages}")
                total_pages = max_pages
            
            product_list = []
            
            # 處理第一頁
            print("獲取第1頁商品列表")
            
            # 滾動頁面以確保所有商品都已載入
            scroll_behavior = config.get("advanced_settings", {}).get("scroll_behavior", {})
            if scroll_behavior.get("enable_lazy_loading", True):
                for _ in range(scroll_behavior.get("max_scroll_attempts", 5)):
                    scroll_page(driver, "down", 500)
                    random_sleep(scroll_behavior.get("scroll_pause", 1.5), scroll_behavior.get("scroll_pause", 1.5) + 1)
            
            # 獲取結果
            results = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "shop-search-result-view")]'))
            ).get_attribute('innerHTML')
            
            # 解析商品列表
            dom = etree.HTML(results)
            page_products = compose_products(dom)
            product_list.extend(page_products)
            print(f"第1頁獲取到 {len(page_products)} 個商品")
            
            # 處理其他頁面
            for page in range(1, total_pages):
                print(f"獲取第{page+1}頁商品列表")
                
                # 構建下一頁URL
                next_url = f"{base_url}{config.get('search_parameters', {}).get('shop', {}).get('url', '')}" + \
                          f"?sortBy=ctime&page={page}#product_list"
                
                driver.get(next_url)
                random_sleep(3.0, 5.0)
                
                # 處理reCAPTCHA（如果出現）
                handle_recaptcha(driver, config)
                
                # 滾動頁面
                if scroll_behavior.get("enable_lazy_loading", True):
                    for _ in range(scroll_behavior.get("max_scroll_attempts", 5)):
                        scroll_page(driver, "down", 500)
                        random_sleep(scroll_behavior.get("scroll_pause", 1.5), scroll_behavior.get("scroll_pause", 1.5) + 1)
                
                # 獲取結果
                try:
                    results = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "shop-search-result-view")]'))
                    ).get_attribute('innerHTML')
                    
                    # 解析商品列表
                    dom = etree.HTML(results)
                    page_products = compose_products(dom)
                    product_list.extend(page_products)
                    print(f"第{page+1}頁獲取到 {len(page_products)} 個商品")
                except Exception as page_e:
                    print(f"獲取第{page+1}頁商品列表時發生錯誤: {str(page_e)}")
                    traceback.print_exc()
                    break
            
            # 去除重複的商品
            unique_products = []
            seen_links = set()
            for product in product_list:
                if product.get('link') not in seen_links:
                    seen_links.add(product.get('link'))
                    unique_products.append(product)
            
            print(f"總共獲取到 {len(unique_products)} 個不重複商品")
            
            # 8. 如果指定了特定商品，找到並點擊它
            if product:
                print(f"查找特定商品: {product}")
                product_found = False
                
                for idx, item in enumerate(unique_products):
                    if product.lower() in item.get('title', '').lower():
                        print(f"找到匹配的商品: {item.get('title')}")
                        product_link = normalize_url(item.get('link'), base_url)
                        driver.get(product_link)
                        random_sleep(3.0, 5.0)
                        
                        # 處理reCAPTCHA（如果出現）
                        handle_recaptcha(driver, config)
                        
                        # 獲取單個商品詳情
                        product_detail = extract_product_detail(driver, config)
                        
                        # 保存結果
                        result = {
                            "timestamp": datetime.now().isoformat(),
                            "query": {
                                "keyword": keyword,
                                "shop": shop,
                                "product": product
                            },
                            "product_detail": product_detail
                        }
                        
                        save_results(result, config)
                        product_found = True
                        break
                
                if not product_found:
                    print(f"未找到指定商品: {product}")
                    
                    # 如果沒有找到指定商品，可以爬取所有商品
                    print("改為獲取所有商品詳情")
                    
                    # 限制處理的商品數量
                    max_products = config.get("advanced_settings", {}).get("max_results_per_page", 20)
                    if len(unique_products) > max_products:
                        print(f"限制處理的商品數量為 {max_products}")
                        unique_products = unique_products[:max_products]
                    
                    # 獲取所有商品詳情
                    products = fetch_products(driver, unique_products, config)
                    
                    # 保存結果
                    result = {
                        "timestamp": datetime.now().isoformat(),
                        "query": {
                            "keyword": keyword,
                            "shop": shop,
                            "product": product
                        },
                        "products": products
                    }
                    
                    save_results(result, config)
            else:
                # 9. 如果沒有指定特定商品，獲取所有商品詳情
                print("獲取所有商品詳情")
                
                # 限制處理的商品數量
                max_products = config.get("advanced_settings", {}).get("max_results_per_page", 20)
                if len(unique_products) > max_products:
                    print(f"限制處理的商品數量為 {max_products}")
                    unique_products = unique_products[:max_products]
                
                # 獲取所有商品詳情
                products = fetch_products(driver, unique_products, config)
                
                # 保存結果
                result = {
                    "timestamp": datetime.now().isoformat(),
                    "query": {
                        "keyword": keyword,
                        "shop": shop
                    },
                    "products": products
                }
                
                save_results(result, config)
            
        except Exception as e:
            print(f"獲取商品列表時發生錯誤: {str(e)}")
            traceback.print_exc()
            
            # 嘗試處理錯誤
            handle_error(driver, config, e)
        
        print("爬蟲執行完成！")
        
    except TimeoutException:
        print("頁面載入超時")
        handle_error(driver, config, TimeoutException("頁面載入超時"))
    except Exception as e:
        handle_error(driver, config, e)
    finally:
        if driver:
            # 等待一下，讓用戶可以看到最終頁面
            finish_delay = config.get("delays", {}).get("finish", 3)
            time.sleep(finish_delay)
            driver.quit()


if __name__ == "__main__":
    main()