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

# 確保必要的目錄存在
os.makedirs("examples/data/output", exist_ok=True)
os.makedirs("examples/data/screenshots", exist_ok=True)
os.makedirs("examples/data/debug", exist_ok=True)


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
    
    # 不使用隨機視窗大小，改為精確指定常見的視窗大小
    if anti_detection.get("randomize_viewport", True):
        common_resolutions = [
            (1920, 1080),  # Full HD
            (1366, 768),   # 常見筆電解析度
            (1440, 900),   # MacBook Air
            (1536, 864)    # 常見 Windows 解析度
        ]
        width, height = random.choice(common_resolutions)
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
        enhance_browser_stealth(driver)
        
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
    """擷取頁面截圖"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"shopee_{timestamp}_{page_type}.png"
        screenshot_path = os.path.join("examples/data/screenshots", filename)
        driver.save_screenshot(screenshot_path)
        print(f"已保存截圖：{screenshot_path}")
        return screenshot_path
    except Exception as e:
        print(f"截圖失敗：{str(e)}")
        return None


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


def enhance_browser_stealth(driver):
    """增強反爬蟲能力，修改更多瀏覽器指紋"""
    # 更全面的指紋修改腳本
    stealth_js = """
    // 更徹底地隱藏自動化特徵
    const newProto = navigator.__proto__
    delete newProto.webdriver
    navigator.__proto__ = newProto
    
    // 偽造更多瀏覽器特性
    const originalQuery = window.navigator.permissions.query
    window.navigator.permissions.query = (parameters) => (
        parameters.name === 'notifications' || 
        parameters.name === 'geolocation' ||
        parameters.name === 'midi' || 
        parameters.name === 'camera' || 
        parameters.name === 'microphone'
        ? Promise.resolve({ state: Notification.permission }) 
        : originalQuery(parameters)
    )
    
    // 偽造螢幕分辨率和顏色深度
    Object.defineProperty(window.screen, 'width', { value: 1920 })
    Object.defineProperty(window.screen, 'height', { value: 1080 })
    Object.defineProperty(window.screen, 'availWidth', { value: 1920 })
    Object.defineProperty(window.screen, 'availHeight', { value: 1030 })
    Object.defineProperty(window.screen, 'colorDepth', { value: 24 })
    Object.defineProperty(window.screen, 'pixelDepth', { value: 24 })
    
    // 混淆 WebGL 指紋
    const getParameter = WebGLRenderingContext.prototype.getParameter
    WebGLRenderingContext.prototype.getParameter = function(parameter) {
      if (parameter === 37445) {
        return 'Intel Open Source Technology Center'
      }
      if (parameter === 37446) {
        return 'Mesa DRI Intel(R) HD Graphics 5500 (Broadwell GT2)'
      }
      return getParameter.apply(this, arguments)
    }
    """
    
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": stealth_js
    })
    
    print("已加載增強型反指紋腳本")


def simulate_human_browsing_after_login(driver, config):
    """登入後模擬人類瀏覽行為"""
    print("模擬登入後的瀏覽行為...")
    
    try:
        # 捲動頁面瀀覽
        for _ in range(3):
            # 隨機捲動頁面
            scroll_amount = random.randint(300, 800)
            driver.execute_script(f"window.scrollBy(0, {scroll_amount})")
            random_sleep(1.0, 2.5)
            
            # 隨機移動滑鼠
            action = ActionChains(driver)
            action.move_by_offset(random.randint(-100, 100), random.randint(-50, 50))
            action.perform()
            random_sleep(0.5, 1.5)
        
        # 隨機點擊某個推薦項目或類別 (如果有的話)
        try:
            categories = driver.find_elements(By.XPATH, "//a[contains(@class, 'home-category-list') or contains(@class, 'recommend')]")
            if categories and len(categories) > 3:
                random_index = random.randint(0, min(5, len(categories)-1))
                target = categories[random_index]
                
                # 滾動到元素位置
                driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", target)
                random_sleep(1.0, 2.0)
                
                # 點擊元素
                safe_click(driver, target)
                random_sleep(3.0, 5.0)
                
                # 回到首頁
                driver.execute_script("window.history.go(-1)")
                random_sleep(2.0, 3.0)
        except Exception as e:
            print(f"模擬點擊類別時發生錯誤: {str(e)}")
        
        print("完成人類行為模擬")
        return True
    except Exception as e:
        print(f"模擬人類瀏覽行為時發生錯誤: {str(e)}")
        return False


# 修改 login 函數，在登入成功後增加以下程式碼
if login_success:
    print("登入成功，進行人類行為模擬和強化 Cookie 處理")
    
    # 強化瀏覽器指紋隱藏
    enhance_browser_stealth(driver)
    
    # 模擬人類瀏覽行為
    simulate_human_browsing_after_login(driver, config)
    
    # 強化 Cookie 處理
    cookies = improve_cookie_handling(driver, config)
    
    # 保存強化後的 Cookie
    if session_management.get("save_cookies", True):
        save_cookies(driver, config)
        
    # 隨機暫停一下
    random_sleep(3.0, 5.0)