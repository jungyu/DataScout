"""
UberEats 爬蟲程式 (改進版)
基於配置文件的 UberEats 網站資料爬取工具
支持地址搜尋、餐廳搜尋和餐點選擇，自動加入購物車
"""

import os
import re
import json
import time
import urllib.parse
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Union

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains
from lxml import html

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


def normalize_url(url: str, base_domain: str = "https://www.ubereats.com") -> str:
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


def take_screenshot(driver: webdriver.Chrome, config: Dict, page_type: str) -> None:
    """拍攝螢幕截圖"""
    try:
        screenshot_config = config.get("advanced_settings", {}).get("screenshot", {})
        if not screenshot_config.get("enabled", False):
            return
            
        directory = screenshot_config.get("directory", "../screenshots")
        os.makedirs(directory, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename_pattern = screenshot_config.get("filename_pattern", "ubereats_{timestamp}_{page_type}.png")
        filename = filename_pattern.replace("{timestamp}", timestamp).replace("{page_type}", page_type)
        
        filepath = os.path.join(directory, filename)
        driver.save_screenshot(filepath)
        print(f"螢幕截圖已保存: {filepath}")
        
    except Exception as e:
        print(f"拍攝螢幕截圖時發生錯誤: {str(e)}")


def save_page_source(driver: webdriver.Chrome, config: Dict, page_type: str) -> None:
    """保存頁面源碼"""
    try:
        # 確保目錄存在
        output_dir = "examples/data/debug"
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成檔案名稱
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ubereats_{timestamp}_{page_type}.html"
        filepath = os.path.join(output_dir, filename)
        
        # 保存頁面源碼
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
            
        print(f"頁面源碼已保存: {filepath}")
        
    except Exception as e:
        print(f"保存頁面源碼時發生錯誤: {str(e)}")

# ===== Cookie和LocalStorage處理 =====

def save_cookies(driver: webdriver.Chrome, config: Dict) -> None:
    """保存Cookie到文件"""
    try:
        cookies_path = config.get("advanced_settings", {}).get("cookies_path", "cookies/ubereats_cookies.json")
        
        # 確保目錄存在
        os.makedirs(os.path.dirname(cookies_path), exist_ok=True)
        
        # 獲取並保存Cookie
        cookies = driver.get_cookies()
        with open(cookies_path, 'w', encoding='utf-8') as f:
            json.dump(cookies, f)
            
        print(f"Cookie已保存到: {cookies_path}")
        
    except Exception as e:
        print(f"保存Cookie時發生錯誤: {str(e)}")


def load_cookies(driver: webdriver.Chrome, config: Dict) -> bool:
    """從文件加載Cookie"""
    try:
        cookies_path = config.get("advanced_settings", {}).get("cookies_path", "cookies/ubereats_cookies.json")
        
        if not os.path.exists(cookies_path):
            print(f"Cookie文件不存在: {cookies_path}")
            return False
            
        # 加載Cookie
        with open(cookies_path, 'r', encoding='utf-8') as f:
            cookies = json.load(f)
            
        # 設置Cookie
        for cookie in cookies:
            # 某些Cookie可能有其他屬性，需要移除
            if 'expiry' in cookie:
                cookie['expiry'] = int(cookie['expiry'])
            
            try:
                driver.add_cookie(cookie)
            except Exception as e:
                print(f"添加Cookie時發生錯誤: {str(e)}")
                
        print(f"已從 {cookies_path} 加載Cookie")
        return True
        
    except Exception as e:
        print(f"加載Cookie時發生錯誤: {str(e)}")
        return False


def set_local_storage(driver: webdriver.Chrome, config: Dict) -> bool:
    """設置localStorage以記住地址"""
    try:
        address_config = config.get("search_parameters", {}).get("address", {})
        default_address = address_config.get("default")
        
        if not default_address:
            return False
            
        # 嘗試設置localStorage以記住地址
        script = f"""
        try {{
            localStorage.setItem('ubereats:last_used_address', JSON.stringify({{
                address: "{default_address}",
                latitude: 22.05, // 屏東大約緯度
                longitude: 120.5  // 屏東大約經度
            }}));
            return true;
        }} catch (e) {{
            console.error('設置localStorage失敗:', e);
            return false;
        }}
        """
        
        result = driver.execute_script(script)
        if result:
            print(f"已成功設置localStorage記住地址: {default_address}")
            return True
        else:
            print("設置localStorage失敗")
            return False
            
    except Exception as e:
        print(f"設置localStorage時發生錯誤: {str(e)}")
        return False

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
    """設置並初始化 WebDriver，包含自動下載機制"""
    print("正在設置 Chrome WebDriver...")
    
    try:
        # 檢查是否安裝了 webdriver_manager
        try:
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.service import Service
            print("使用 webdriver_manager 自動下載合適的 ChromeDriver")
            use_manager = True
        except ImportError:
            print("未安裝 webdriver_manager，使用默認 WebDriver 設置")
            use_manager = False
        
        chrome_options = webdriver.ChromeOptions()
        
        # 從配置文件獲取 User-Agent
        user_agent = config.get("request", {}).get("headers", {}).get("User-Agent")
        if user_agent:
            chrome_options.add_argument(f'user-agent={user_agent}')
        
        # 基本設置
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-notifications')  
        chrome_options.add_argument('--disable-popup-blocking')
        chrome_options.add_argument('--enable-javascript')
        chrome_options.add_argument('--enable-cookies')
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--allow-running-insecure-content')
        
        # 設置頁面加載策略
        chrome_options.page_load_strategy = 'normal'
        
        # 調試模式：不自動關閉瀏覽器
        chrome_options.add_experimental_option("detach", True)
        
        # 使用 webdriver_manager 自動下載合適的驅動
        if use_manager:
            print("初始化 Chrome WebDriver，使用自動下載")
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
        else:
            print("初始化 Chrome WebDriver，使用默認設置")
            driver = webdriver.Chrome(options=chrome_options)
        
        driver.maximize_window()
        
        # 設置隱式等待時間
        driver.implicitly_wait(10)
        
        # 設置頁面加載超時
        driver.set_page_load_timeout(30)
        
        # 設置腳本超時
        driver.set_script_timeout(30)
        
        print("WebDriver 初始化成功")
        return driver
        
    except Exception as e:
        print(f"WebDriver 初始化失敗: {str(e)}")
        print("嘗試使用備用方法初始化 WebDriver...")
        
        try:
            # 備用方法：嘗試不使用選項初始化
            print("使用無選項初始化")
            driver = webdriver.Chrome()
            print("備用方法成功")
            return driver
        except Exception as e2:
            print(f"備用初始化也失敗: {str(e2)}")
            raise RuntimeError(f"無法初始化 WebDriver: {str(e)}, 備用方法: {str(e2)}")


def wait_for_element(driver: webdriver.Chrome, by: str, selector: str, timeout: int = 10) -> Any:
    """等待元素出現並返回"""
    try:
        wait = WebDriverWait(driver, timeout)
        element = wait.until(EC.presence_of_element_located((by, selector)))
        # 確保元素可見
        if element and not element.is_displayed():
            # 嘗試滾動到元素使其可見
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(0.5)
        return element
    except TimeoutException:
        print(f"等待元素超時: {selector}")
        return None
    except Exception as e:
        print(f"等待元素時發生錯誤: {str(e)}")
        return None


def wait_for_elements(driver: webdriver.Chrome, by: str, selector: str, timeout: int = 10) -> List:
    """等待多個元素出現並返回"""
    try:
        wait = WebDriverWait(driver, timeout)
        return wait.until(EC.presence_of_all_elements_located((by, selector)))
    except TimeoutException:
        print(f"等待元素超時: {selector}")
        return []
    except Exception as e:
        print(f"等待元素時發生錯誤: {str(e)}")
        return []


def safe_click(driver: webdriver.Chrome, element, retries: int = 3) -> bool:
    """安全點擊元素，處理可能的點擊攔截"""
    for attempt in range(retries):
        try:
            # 嘗試滾動到元素
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(0.5)
            
            # 嘗試使元素可見
            driver.execute_script("arguments[0].style.visibility = 'visible'; arguments[0].style.display = 'block';", element)
            
            # 確保元素可見和可點擊
            try:
                WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, f"//*[@id='{element.get_attribute('id')}']")))
            except:
                # 如果無法通過ID定位，就不等待了，直接嘗試點擊
                pass
            
            # 使用ActionChains嘗試點擊
            try:
                ActionChains(driver).move_to_element(element).click().perform()
                time.sleep(0.5)
                return True
            except Exception as e:
                print(f"ActionChains點擊失敗: {str(e)}")
            
            # 直接點擊
            element.click()
            return True
            
        except ElementClickInterceptedException:
            print(f"點擊被攔截，嘗試使用 JavaScript 點擊 (嘗試 {attempt+1}/{retries})")
            try:
                # 先嘗試移除可能的覆蓋元素
                driver.execute_script("""
                    var elements = document.querySelectorAll('div[class*="modal"], div[class*="overlay"], div[class*="dialog"]');
                    for(var i=0; i<elements.length; i++){
                        elements[i].style.display = 'none';
                    }
                """)
                time.sleep(0.5)
                
                # 然後再點擊
                driver.execute_script("arguments[0].click();", element)
                return True
            except Exception as e:
                print(f"JavaScript 點擊失敗: {str(e)}")
                time.sleep(1)
        except Exception as e:
            print(f"點擊失敗: {str(e)}")
            time.sleep(1)
            
            # 最後嘗試發送Enter鍵
            try:
                element.send_keys(Keys.ENTER)
                return True
            except:
                pass
    
    return False


def scroll_page(driver: webdriver.Chrome, config: Dict) -> None:
    """滾動頁面以加載懶加載內容"""
    scroll_config = config.get("advanced_settings", {}).get("scroll_behavior", {})
    if not scroll_config.get("enable_lazy_loading", True):
        return
        
    scroll_pause = scroll_config.get("scroll_pause", 1.5)
    max_attempts = scroll_config.get("max_scroll_attempts", 5)
    
    print("開始滾動頁面以加載更多內容...")
    
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    for i in range(max_attempts):
        # 滾動到頁面底部
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        # 等待頁面加載
        time.sleep(scroll_pause)
        
        # 計算新的滾動高度
        new_height = driver.execute_script("return document.body.scrollHeight")
        
        # 如果頁面高度沒有變化，停止滾動
        if new_height == last_height:
            break
            
        last_height = new_height
        
    # 滾動回頁面頂部
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(1)

# ===== 搜尋參數設置區 =====

def set_search_parameters(driver: webdriver.Chrome, config: Dict) -> bool:
    """設置搜尋參數"""
    try:
        search_params = config.get("search_parameters", {})
        
        # 設置送餐地址
        print("開始設置送餐地址...")
        if not set_address(driver, search_params):
            print("設置送餐地址失敗")
            return False
            
        # 檢查是否已經轉到搜尋頁面
        current_url = driver.current_url
        if "feed" in current_url or "store" in current_url:
            print("已自動轉到搜尋頁面，繼續設置搜尋關鍵字")
        else:
            print("未自動轉到搜尋頁面，檢查地址設置是否成功")
            # 再次確認地址設置是否生效
            try:
                # 嘗試再次點擊搜尋按鈕
                submit_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), '尋找食物')]")
                if submit_buttons:
                    print("找到'尋找食物'按鈕，再次嘗試點擊")
                    if safe_click(driver, submit_buttons[0]):
                        print("成功點擊按鈕")
                        time.sleep(5)
                    else:
                        print("點擊失敗")
            except Exception as e:
                print(f"再次嘗試點擊按鈕時發生錯誤: {str(e)}")
                
        # 設置搜尋關鍵字
        print("開始設置搜尋關鍵字...")
        if not set_search_keyword(driver, search_params):
            print("設置搜尋關鍵字失敗")
            return False
        
        return True
        
    except Exception as e:
        print(f"設置搜尋參數時發生錯誤: {str(e)}")
        return False


def set_address(driver: webdriver.Chrome, search_params: Dict) -> bool:
    """設置送餐地址"""
    try:
        address_config = search_params.get("address", {})
        input_selector = "//input[@id='location-typeahead-home-input']"  # 直接使用ID選擇器
        submit_selector = "//button[contains(@class, 'e9') and contains(text(), '尋找食物')]"  # 使用類和文本定位按鈕
        default_address = address_config.get("default")
        
        if not default_address:
            print("地址配置不完整")
            return False
        
        # 等待頁面加載
        time.sleep(5)
        
        # 保存頁面源碼以進行調試
        save_page_source(driver, {}, "before_address")
        
        # 取得當前URL以檢查後續是否變化
        start_url = driver.current_url
        print(f"初始URL: {start_url}")
        
        # 等待地址輸入框出現
        print(f"嘗試定位地址輸入框: {input_selector}")
        address_input = wait_for_element(driver, By.XPATH, input_selector)
        
        # 如果找不到，嘗試用其他方法
        if not address_input:
            print("無法通過XPATH找到輸入框，嘗試使用JavaScript和ID查找")
            try:
                # 確認輸入框是否存在
                input_exists = driver.execute_script("""
                    return document.getElementById('location-typeahead-home-input') !== null;
                """)
                
                if not input_exists:
                    print("通過ID無法找到輸入框，嘗試查找所有輸入框")
                    # 嘗試列出所有輸入框的ID以便調試
                    inputs = driver.execute_script("""
                        var inputs = document.getElementsByTagName('input');
                        var ids = [];
                        for (var i = 0; i < inputs.length; i++) {
                            if (inputs[i].id) ids.push(inputs[i].id);
                        }
                        return ids;
                    """)
                    print(f"頁面上的輸入框ID: {inputs}")
                    
                    # 嘗試找到任何可能的地址輸入框
                    driver.execute_script("""
                        var inputs = document.getElementsByTagName('input');
                        for (var i = 0; i < inputs.length; i++) {
                            var input = inputs[i];
                            var placeholder = input.getAttribute('placeholder');
                            if (placeholder && (
                                placeholder.includes('地址') || 
                                placeholder.includes('外送') || 
                                placeholder.includes('address')
                            )) {
                                input.value = arguments[0];
                                input.dispatchEvent(new Event('input', { bubbles: true }));
                                input.dispatchEvent(new Event('change', { bubbles: true }));
                                console.log('找到並設置了地址輸入框: ' + placeholder);
                                return true;
                            }
                        }
                        return false;
                    """, default_address)
                else:
                    # 使用JavaScript直接根據ID查找並輸入地址
                    driver.execute_script(f"""
                        var input = document.getElementById('location-typeahead-home-input');
                        input.value = "{default_address}";
                        input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    """)
                print("使用JavaScript成功設置地址")
                time.sleep(2)
            except Exception as e:
                print(f"JavaScript設置地址失敗: {str(e)}")
                return False
        else:
            # 清除並輸入地址
            print(f"找到地址輸入框，輸入地址: {default_address}")
            address_input.clear()
            address_input.send_keys(default_address)
            time.sleep(1)
        
        # 嘗試所有可能的點擊方法，並在每次嘗試後驗證結果
        
        # 方法1: 使用Action鏈點擊
        print("方法1: 嘗試使用Action鏈點擊'尋找食物'按鈕")
        try:
            # 獲取所有可能的按鈕
            buttons = driver.find_elements(By.XPATH, "//button[contains(text(), '尋找食物')]")
            if buttons:
                print(f"找到{len(buttons)}個'尋找食物'按鈕")
                
                for i, button in enumerate(buttons):
                    try:
                        print(f"嘗試點擊第{i+1}個按鈕")
                        # 確保按鈕可見
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                        time.sleep(0.5)
                        
                        # 使用Action鏈點擊
                        ActionChains(driver).move_to_element(button).click().perform()
                        time.sleep(5)
                        
                        # 檢查URL是否變化
                        current_url = driver.current_url
                        if current_url != start_url:
                            print(f"URL已變更為: {current_url}，點擊成功")
                            return True
                        else:
                            print("URL未變更，點擊可能失敗")
                    except Exception as e:
                        print(f"點擊第{i+1}個按鈕時出錯: {str(e)}")
        except Exception as e:
            print(f"Action鏈點擊失敗: {str(e)}")
        
        # 方法2: 直接使用JavaScript點擊所有可能的按鈕
        print("方法2: 嘗試使用JavaScript點擊所有可能的'尋找食物'按鈕")
        try:
            clicked = driver.execute_script("""
                // 嘗試點擊所有包含文本的按鈕
                var buttons = Array.from(document.getElementsByTagName('button'))
                    .filter(b => b.textContent.includes('尋找食物'));
                
                if (buttons.length > 0) {
                    console.log('找到 ' + buttons.length + ' 個按鈕');
                    for (var i = 0; i < buttons.length; i++) {
                        try {
                            console.log('嘗試點擊按鈕 #' + (i+1));
                            buttons[i].scrollIntoView({block: 'center'});
                            buttons[i].click();
                            return true;
                        } catch (e) {
                            console.log('點擊失敗: ' + e);
                        }
                    }
                }
                
                // 如果按文本找不到，嘗試用類名找
                var eButtons = document.getElementsByClassName('e9');
                if (eButtons.length > 0) {
                    console.log('找到 ' + eButtons.length + ' 個e9類按鈕');
                    for (var i = 0; i < eButtons.length; i++) {
                        try {
                            console.log('嘗試點擊e9按鈕 #' + (i+1));
                            eButtons[i].scrollIntoView({block: 'center'});
                            eButtons[i].click();
                            return true;
                        } catch (e) {
                            console.log('點擊失敗: ' + e);
                        }
                    }
                }
                
                return false;
            """)
            
            print(f"JavaScript點擊結果: {'成功' if clicked else '失敗'}")
            
            # 等待頁面可能的變化
            time.sleep(10)
            
            # 檢查URL是否變更
            current_url = driver.current_url
            if current_url != start_url:
                print(f"URL已變更為: {current_url}，點擊成功")
                return True
                
        except Exception as e:
            print(f"JavaScript點擊按鈕失敗: {str(e)}")
        
        # 方法3: 使用Enter鍵模擬表單提交
        print("方法3: 嘗試使用Enter鍵模擬表單提交")
        try:
            # 先重新找尋輸入框
            input_element = wait_for_element(driver, By.XPATH, input_selector)
            if input_element:
                print("找到輸入框，嘗試按Enter鍵")
                input_element.send_keys(Keys.RETURN)
                time.sleep(5)
                
                # 檢查URL是否變更
                current_url = driver.current_url
                if current_url != start_url:
                    print(f"URL已變更為: {current_url}，Enter鍵提交成功")
                    return True
                else:
                    print("URL未變更，Enter鍵提交可能失敗")
        except Exception as e:
            print(f"Enter鍵提交失敗: {str(e)}")
        
        # 方法4: 原始的XPATH定位和點擊
        print("方法4: 嘗試原始的XPATH定位和點擊")
        try:
            # 嘗試找到按鈕
            submit_button = wait_for_element(driver, By.XPATH, submit_selector)
            
            # 如果找不到，嘗試其他選擇器
            if not submit_button:
                print("無法使用主選擇器找到按鈕，嘗試備用選擇器")
                backup_selectors = [
                    "//button[contains(text(), '尋找食物')]",
                    "//button[@class='e9']",
                    "//button[contains(@class, 'e9')]",
                    "//button[contains(@class, 'eb')]",
                    "//button[contains(@class, 'au')]"  # 這是一個可能的類名
                ]
                
                for selector in backup_selectors:
                    submit_button = wait_for_element(driver, By.XPATH, selector)
                    if submit_button:
                        print(f"使用備用選擇器找到按鈕: {selector}")
                        break
            
            if submit_button:
                print("找到提交按鈕，嘗試點擊")
                
                # 確保按鈕可見
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_button)
                time.sleep(1)
                
                # 直接點擊
                submit_button.click()
                time.sleep(5)
                
                # 檢查URL是否變更
                current_url = driver.current_url
                if current_url != start_url:
                    print(f"URL已變更為: {current_url}，點擊成功")
                    return True
                else:
                    print("URL未變更，點擊可能失敗")
                    
                    # 嘗試JavaScript點擊
                    print("嘗試使用JavaScript直接點擊找到的按鈕")
                    driver.execute_script("arguments[0].click();", submit_button)
                    time.sleep(5)
                    
                    # 再次檢查URL
                    current_url = driver.current_url
                    if current_url != start_url:
                        print(f"URL已變更為: {current_url}，JavaScript點擊成功")
                        return True
            else:
                print("找不到提交按鈕")
        except Exception as e:
            print(f"XPATH點擊失敗: {str(e)}")
        
        # 方法5: 直接使用相對URL訪問搜尋頁面
        print("方法5: 嘗試直接使用相對URL訪問搜尋頁面")
        try:
            # 編碼地址
            encoded_address = urllib.parse.quote(default_address)
            
            # 構建搜尋頁面URL (可能需要根據實際網站調整)
            search_url = f"{driver.current_url.split('?')[0]}feed?pl={encoded_address}"
            print(f"嘗試直接訪問搜尋頁面: {search_url}")
            
            # 訪問URL
            driver.get(search_url)
            time.sleep(5)
            
            # 檢查是否跳轉到搜尋頁面
            current_url = driver.current_url
            if "feed" in current_url or "store" in current_url:
                print(f"成功直接訪問搜尋頁面: {current_url}")
                return True
            else:
                print(f"直接訪問搜尋頁面失敗，當前URL: {current_url}")
        except Exception as e:
            print(f"直接訪問搜尋頁面失敗: {str(e)}")
            
        # 如果以上所有方法都失敗，檢查當前URL是否已經是搜尋頁面
        current_url = driver.current_url
        if "feed" in current_url or "store" in current_url:
            print(f"已經在搜尋頁面: {current_url}")
            return True
        
        # 所有方法都失敗，保存頁面源碼以進行調試
        print("所有嘗試都失敗，保存頁面源碼以進行調試")
        save_page_source(driver, {}, "all_click_methods_failed")
        take_screenshot(driver, {}, "all_click_methods_failed")
        
        return False
        
    except Exception as e:
        print(f"設置地址時發生錯誤: {str(e)}")
        return False


def set_search_keyword(driver: webdriver.Chrome, search_params: Dict) -> bool:
    """設置搜尋關鍵字並使用Enter鍵提交"""
    try:
        want_config = search_params.get("want", {})
        default_keyword = want_config.get("default")
        
        if not default_keyword:
            print("搜尋關鍵字配置不完整")
            return False
        
        # 等待頁面加載
        time.sleep(3)
        
        print(f"準備搜尋關鍵字: {default_keyword}")
        
        # 先使用最新的CSS選擇器定位搜索框
        search_selectors = [
            "input[data-testid='search-input']",
            "input[role='combobox']",
            "input[placeholder*='搜尋']",
            "input[id*='search']"
        ]
        
        # 嘗試所有可能的選擇器
        search_input = None
        for selector in search_selectors:
            try:
                print(f"嘗試選擇器: {selector}")
                search_input = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                if search_input:
                    print(f"找到搜索框使用選擇器: {selector}")
                    break
            except:
                continue
        
        if not search_input:
            print("無法找到搜尋輸入框，嘗試JavaScript方法")
            # 使用JavaScript查找所有輸入框並選擇可能的搜索框
            search_input_exists = driver.execute_script("""
                var inputs = document.getElementsByTagName('input');
                for (var i = 0; i < inputs.length; i++) {
                    var input = inputs[i];
                    if (input.type === 'text' || 
                        input.placeholder.includes('搜尋') || 
                        input.id.includes('search') ||
                        input.getAttribute('role') === 'combobox') {
                        // 先聚焦元素
                        input.focus();
                        // 清除當前值
                        input.value = '';
                        // 設置新值
                        input.value = arguments[0];
                        // 觸發輸入事件
                        input.dispatchEvent(new Event('input', { bubbles: true }));
                        return true;
                    }
                }
                return false;
            """, default_keyword)
            
            if not search_input_exists:
                print("JavaScript無法找到適合的搜索框")
                return False
                
            # 給一點時間讓輸入事件生效
            time.sleep(1)
            
            # 使用JavaScript模擬Enter鍵
            enter_pressed = driver.execute_script("""
                var inputs = document.getElementsByTagName('input');
                for (var i = 0; i < inputs.length; i++) {
                    var input = inputs[i];
                    if (input.type === 'text' || 
                        input.placeholder.includes('搜尋') || 
                        input.id.includes('search') ||
                        input.getAttribute('role') === 'combobox') {
                        // 創建一個鍵盤事件
                        var e = new KeyboardEvent('keydown', {
                            bubbles: true, 
                            cancelable: true, 
                            key: 'Enter',
                            keyCode: 13
                        });
                        input.dispatchEvent(e);
                        return true;
                    }
                }
                return false;
            """)
            
            print(f"JavaScript模擬Enter鍵: {'成功' if enter_pressed else '失敗'}")
        else:
            # 如果找到了搜索框，先清除它
            search_input.clear()
            # 輸入關鍵字
            search_input.send_keys(default_keyword)
            print(f"輸入搜尋關鍵字: {default_keyword}")
            time.sleep(1)
            
            # 嘗試三種方法提交搜索
            
            # 方法1: 直接按Enter
            print("方法1: 使用Enter鍵提交搜索")
            search_input.send_keys(Keys.RETURN)
            time.sleep(2)
            
            # 檢查是否有結果出現
            try:
                results = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='list'], a[href*='/store/']"))
                )
                print("找到搜索結果，Enter鍵提交成功")
                return True
            except:
                print("未檢測到搜索結果，嘗試方法2")
            
            # 方法2: 點擊搜索按鈕
            try:
                print("方法2: 尋找並點擊搜索按鈕")
                search_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit'], button[aria-label*='搜尋']"))
                )
                search_button.click()
                print("點擊搜索按鈕")
                time.sleep(3)
                return True
            except:
                print("未找到搜索按鈕，嘗試方法3")
            
            # 方法3: JavaScript模擬Enter
            print("方法3: 使用JavaScript模擬Enter鍵")
            driver.execute_script("""
                var event = new KeyboardEvent('keydown', {
                    key: 'Enter',
                    code: 'Enter',
                    keyCode: 13,
                    which: 13,
                    bubbles: true
                });
                arguments[0].dispatchEvent(event);
            """, search_input)
            time.sleep(3)
        
        # 等待頁面加載
        time.sleep(want_config.get("wait_after_submit", 5))
        
        # 保存截圖和源碼以便調試
        take_screenshot(driver, {}, "after_search_enter")
        save_page_source(driver, {}, "after_search_enter")
        
        # 檢查結果頁面的特徵
        try:
            # 檢查是否有常見的結果頁面元素
            result_indicators = [
                "div[role='list']",
                "a[href*='/store/']",
                "div[data-testid='store-list']",
                "div[class*='restaurant-list']"
            ]
            
            for indicator in result_indicators:
                try:
                    result_element = driver.find_element(By.CSS_SELECTOR, indicator)
                    if result_element:
                        print(f"搜索成功，找到結果指示器: {indicator}")
                        return True
                except:
                    continue
            
            # 檢查URL是否包含搜索參數
            current_url = driver.current_url
            if "q=" in current_url or "query=" in current_url or "search=" in current_url:
                print(f"URL包含搜索參數: {current_url}")
                return True
                
            print("無法確認搜索是否成功，但已嘗試所有方法")
            return True  # 即使不確定，也繼續執行後續步驟
            
        except Exception as e:
            print(f"檢查搜索結果時出錯: {str(e)}")
            return True  # 即使有錯誤，也繼續執行後續步驟
            
    except Exception as e:
        print(f"設置搜尋關鍵字時發生錯誤: {str(e)}")
        # 保存出錯狀態的截圖和源碼
        take_screenshot(driver, {}, "search_keyword_error")
        save_page_source(driver, {}, "search_keyword_error")
        return False
    
# ===== 餐廳和餐點選擇區 =====

def find_and_click_store(driver: webdriver.Chrome, config: Dict) -> bool:
    """尋找並點擊目標餐廳"""
    try:
        search_params = config.get("search_parameters", {})
        store_config = search_params.get("wantStore", {})
        store_name = store_config.get("default")
        selector = store_config.get("selector").replace("{value}", store_name)
        backup_selectors = store_config.get("backup_selectors", [])
        wait_time = store_config.get("wait_after_click", 5)
        
        if not store_name:
            print("餐廳配置不完整")
            return False
        
        print(f"尋找餐廳: {store_name}")
        
        # 等待頁面加載
        time.sleep(5)
        
        # 保存頁面源碼以進行調試
        save_page_source(driver, {}, "before_find_store")
        
        # 滾動頁面以顯示所有餐廳
        print("滾動頁面以顯示所有餐廳...")
        scroll_page(driver, config)
        
        # 嘗試使用主選擇器找餐廳
        print(f"使用選擇器尋找餐廳: {selector}")
        store_element = wait_for_element(driver, By.XPATH, selector)
        
        # 如果主選擇器找不到，嘗試備用選擇器
        if not store_element and backup_selectors:
            print("使用主選擇器找不到餐廳，嘗試備用選擇器")
            for backup_selector in backup_selectors:
                try:
                    full_selector = backup_selector.replace("{value}", store_name)
                    print(f"嘗試備用選擇器: {full_selector}")
                    store_element = wait_for_element(driver, By.XPATH, full_selector)
                    if store_element:
                        print(f"使用備用選擇器找到餐廳: {full_selector}")
                        break
                except Exception as e:
                    print(f"使用備用選擇器時發生錯誤: {str(e)}")
        
        # 如果還是找不到，嘗試在頁面中查找任何包含餐廳名稱的元素
        if not store_element:
            print("嘗試在頁面中查找任何包含餐廳名稱的元素...")
            
            # 嘗試使用更一般的選擇器
            general_selectors = [
                f"//a[contains(., '{store_name}')]",
                f"//h3[contains(., '{store_name}')]/ancestor::a",
                f"//div[contains(., '{store_name}')]/ancestor::a",
                f"//*[contains(text(), '{store_name}')]/ancestor::a"
            ]
            
            for selector in general_selectors:
                store_element = wait_for_element(driver, By.XPATH, selector)
                if store_element:
                    print(f"使用一般選擇器找到餐廳: {selector}")
                    break
            
            # 如果還是找不到，嘗試使用模糊匹配
            if not store_element:
                print("使用模糊匹配搜尋餐廳...")
                
                # 獲取所有可能的餐廳連結
                restaurant_links = driver.find_elements(By.XPATH, "//a[contains(@href, '/store/') or contains(@href, '/restaurant/')]")
                
                # 嘗試在它們中找到包含餐廳名稱的元素
                for link in restaurant_links:
                    try:
                        link_text = link.text.strip()
                        if store_name.lower() in link_text.lower():
                            store_element = link
                            print(f"使用模糊匹配找到餐廳: {link_text}")
                            break
                    except Exception:
                        continue
        
        if not store_element:
            print(f"找不到餐廳: {store_name}")
            save_page_source(driver, {}, "store_not_found")
            return False
        
        # 嘗試點擊餐廳
        print(f"找到餐廳: {store_name}，嘗試點擊...")
        
        # 確保元素在視窗中
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", store_element)
        time.sleep(1)
        
        if not safe_click(driver, store_element):
            print(f"點擊餐廳失敗: {store_name}，嘗試JavaScript點擊")
            driver.execute_script("arguments[0].click();", store_element)
        
        # 等待頁面加載
        time.sleep(wait_time)
        
        # 拍攝螢幕截圖
        take_screenshot(driver, config, "store_page")
        
        # 保存頁面源碼以進行調試
        save_page_source(driver, {}, "store_page")
        
        return True
        
    except Exception as e:
        print(f"選擇餐廳時發生錯誤: {str(e)}")
        return False


def select_food_category(driver: webdriver.Chrome, config: Dict) -> bool:
    """選擇食物類別"""
    try:
        search_params = config.get("search_parameters", {})
        category_config = search_params.get("wantCategory", {})
        category_name = category_config.get("default")
        selector = category_config.get("selector").replace("{value}", category_name)
        backup_selectors = category_config.get("backup_selectors", [])
        wait_time = category_config.get("wait_after_click", 3)
        
        if not category_name:
            print("食物類別配置不完整")
            return False
        
        print(f"選擇食物類別: {category_name}")
        
        # 等待頁面加載
        time.sleep(3)
        
        # 保存頁面源碼以進行調試
        save_page_source(driver, {}, "before_select_category")
        
        # 嘗試找到類別選項
        print(f"使用選擇器尋找類別: {selector}")
        category_element = wait_for_element(driver, By.XPATH, selector)
        
        # 如果主選擇器找不到元素，嘗試備用選擇器
        if not category_element and backup_selectors:
            print("使用主選擇器找不到類別，嘗試備用選擇器")
            for backup_selector in backup_selectors:
                try:
                    full_selector = backup_selector.replace("{value}", category_name)
                    print(f"嘗試備用選擇器: {full_selector}")
                    category_element = wait_for_element(driver, By.XPATH, full_selector)
                    if category_element:
                        print(f"使用備用選擇器找到類別: {full_selector}")
                        break
                except Exception as e:
                    print(f"使用備用選擇器時發生錯誤: {str(e)}")
        
        # 尋找標籤列表並點擊
        if not category_element:
            tab_list_selector = category_config.get("tab_list_selector")
            if tab_list_selector:
                print(f"嘗試在標籤列表中查找: {tab_list_selector}")
                tab_list = wait_for_element(driver, By.XPATH, tab_list_selector)
                if tab_list:
                    print("找到標籤列表，嘗試找尋類別按鈕...")
                    tabs = tab_list.find_elements(By.XPATH, ".//button")
                    for tab in tabs:
                        try:
                            tab_text = tab.text.strip()
                            if category_name in tab_text:
                                category_element = tab
                                print(f"在標籤列表中找到類別: {category_name}")
                                break
                        except Exception:
                            continue
        
        # 如果找不到類別，嘗試查找所有按鈕並比較文本
        if not category_element:
            print("嘗試搜尋所有按鈕...")
            buttons = driver.find_elements(By.XPATH, "//button")
            for button in buttons:
                try:
                    button_text = button.text.strip()
                    if category_name in button_text:
                        category_element = button
                        print(f"在所有按鈕中找到類別: {category_name}")
                        break
                except Exception:
                    continue
        
        if not category_element:
            print(f"找不到食物類別: {category_name}，但會繼續嘗試選擇餐點")
            return False
        
        print(f"找到食物類別: {category_name}，嘗試點擊...")
        if not safe_click(driver, category_element):
            print(f"點擊食物類別失敗: {category_name}，嘗試JavaScript點擊")
            driver.execute_script("arguments[0].click();", category_element)
        
        # 等待頁面加載
        time.sleep(wait_time)
        
        # 拍攝螢幕截圖
        take_screenshot(driver, config, "category_selected")
        
        return True
        
    except Exception as e:
        print(f"選擇食物類別時發生錯誤: {str(e)}")
        return False


def select_food_item(driver: webdriver.Chrome, config: Dict) -> bool:
    """選擇餐點"""
    try:
        search_params = config.get("search_parameters", {})
        item_config = search_params.get("wantItem", {})
        item_name = item_config.get("default")
        backup_items = item_config.get("backup_items", [])
        selector = item_config.get("selector").replace("{value}", item_name)
        backup_selectors = item_config.get("backup_selectors", [])
        wait_time = item_config.get("wait_after_click", 3)
        
        if not item_name:
            print("餐點配置不完整")
            return False
        
        print(f"選擇餐點: {item_name}")
        
        # 等待頁面加載
        time.sleep(3)
        
        # 滾動頁面以加載所有餐點
        print("滾動頁面以顯示所有餐點...")
        scroll_page(driver, config)
        
        # 保存頁面源碼以進行調試
        save_page_source(driver, {}, "before_select_item")
        
        # 嘗試找到餐點
        print(f"使用選擇器尋找餐點: {selector}")
        item_element = wait_for_element(driver, By.XPATH, selector)
        
        # 如果主選擇器找不到元素，嘗試備用選擇器
        if not item_element and backup_selectors:
            print("使用主選擇器找不到餐點，嘗試備用選擇器")
            for backup_selector in backup_selectors:
                try:
                    full_selector = backup_selector.replace("{value}", item_name)
                    print(f"嘗試備用選擇器: {full_selector}")
                    item_element = wait_for_element(driver, By.XPATH, full_selector)
                    if item_element:
                        print(f"使用備用選擇器找到餐點: {item_name}")
                        break
                except Exception as e:
                    print(f"使用備用選擇器時發生錯誤: {str(e)}")
        
        # 如果找不到主要餐點，嘗試備用餐點
        if not item_element and backup_items:
            print("嘗試尋找備用餐點...")
            for backup_item in backup_items:
                print(f"嘗試備用餐點: {backup_item}")
                for sel in [selector] + backup_selectors:
                    try:
                        full_selector = sel.replace("{value}", backup_item)
                        print(f"嘗試選擇器: {full_selector}")
                        item_element = wait_for_element(driver, By.XPATH, full_selector)
                        if item_element:
                            print(f"找到備用餐點: {backup_item}")
                            item_name = backup_item  # 更新為實際找到的餐點名稱
                            break
                    except Exception as e:
                        print(f"尋找備用餐點時發生錯誤: {str(e)}")
                if item_element:
                    break
        
        # 如果還是找不到，嘗試在整個頁面中尋找包含餐點名稱的元素
        if not item_element:
            print("嘗試在頁面中查找任何包含餐點名稱的元素...")
            
            # 嘗試更一般的選擇器
            general_selectors = [
                f"//a[contains(., '{item_name}')]",
                f"//div[contains(., '{item_name}')]/ancestor::a",
                f"//span[contains(., '{item_name}')]/ancestor::a",
                f"//h4[contains(., '{item_name}')]/ancestor::a",
                f"//*[contains(text(), '{item_name}')]"
            ]
            
            for selector in general_selectors:
                elements = driver.find_elements(By.XPATH, selector)
                for element in elements:
                    try:
                        # 檢查元素是否可見
                        if element.is_displayed():
                            item_element = element
                            print(f"找到可見的餐點元素: {item_name}")
                            break
                    except Exception:
                        continue
                
                if item_element:
                    break
        
        if not item_element:
            print(f"找不到餐點: {item_name}")
            save_page_source(driver, {}, "item_not_found")
            return False
        
        print(f"找到餐點: {item_name}，嘗試點擊...")
        
        # 確保元素在視窗中
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", item_element)
        time.sleep(1)
        
        if not safe_click(driver, item_element):
            print(f"點擊餐點失敗: {item_name}，嘗試JavaScript點擊")
            driver.execute_script("arguments[0].click();", item_element)
        
        # 等待頁面加載
        time.sleep(wait_time)
        
        # 拍攝螢幕截圖
        take_screenshot(driver, config, "item_selected")
        
        # 保存頁面源碼以進行調試
        save_page_source(driver, {}, "item_selected")
        
        return True
        
    except Exception as e:
        print(f"選擇餐點時發生錯誤: {str(e)}")
        return False


def select_food_option(driver: webdriver.Chrome, config: Dict) -> bool:
    """選擇餐點選項"""
    try:
        search_params = config.get("search_parameters", {})
        option_config = search_params.get("wantOption", {})
        option_name = option_config.get("default")
        selector = option_config.get("selector").replace("{value}", option_name) if option_name else ""
        backup_selectors = option_config.get("backup_selectors", [])
        wait_time = option_config.get("wait_after_click", 1)
        
        # 如果沒有選項配置，表示不需要選擇選項，直接返回成功
        if not option_name:
            print("沒有設置餐點選項，跳過此步驟")
            return True
        
        print(f"選擇餐點選項: {option_name}")
        
        # 等待頁面加載
        time.sleep(2)
        
        # 保存頁面源碼以進行調試
        save_page_source(driver, {}, "before_select_option")
        
        # 等待選項出現
        print(f"使用選擇器尋找選項: {selector}")
        option_element = wait_for_element(driver, By.XPATH, selector)
        
        # 如果主選擇器找不到元素，嘗試備用選擇器
        if not option_element and backup_selectors:
            print("使用主選擇器找不到選項，嘗試備用選擇器")
            for backup_selector in backup_selectors:
                try:
                    full_selector = backup_selector.replace("{value}", option_name)
                    print(f"嘗試備用選擇器: {full_selector}")
                    option_element = wait_for_element(driver, By.XPATH, full_selector)
                    if option_element:
                        print(f"使用備用選擇器找到選項: {option_name}")
                        break
                except Exception as e:
                    print(f"使用備用選擇器時發生錯誤: {str(e)}")
        
        # 如果找不到選項，嘗試在頁面中尋找包含選項名稱的元素
        if not option_element:
            print("嘗試在頁面中查找任何包含選項名稱的元素...")
            
            # 嘗試更一般的選擇器
            general_selectors = [
                f"//label[contains(., '{option_name}')]",
                f"//div[contains(., '{option_name}')]/ancestor::label",
                f"//span[contains(., '{option_name}')]/ancestor::label",
                f"//*[contains(text(), '{option_name}')]/ancestor::label"
            ]
            
            for selector in general_selectors:
                option_element = wait_for_element(driver, By.XPATH, selector)
                if option_element:
                    print(f"使用一般選擇器找到選項: {selector}")
                    break
        
        if not option_element:
            print(f"找不到餐點選項: {option_name}，但會繼續嘗試加入購物車")
            return False
        
        print(f"找到餐點選項: {option_name}，嘗試點擊...")
        
        # 確保元素在視窗中
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", option_element)
        time.sleep(1)
        
        if not safe_click(driver, option_element):
            print(f"點擊餐點選項失敗: {option_name}，嘗試JavaScript點擊")
            driver.execute_script("arguments[0].click();", option_element)
        
        # 等待頁面加載
        time.sleep(wait_time)
        
        # 拍攝螢幕截圖
        take_screenshot(driver, config, "option_selected")
        
        return True
        
    except Exception as e:
        print(f"選擇餐點選項時發生錯誤: {str(e)}")
        return False


def add_to_cart(driver: webdriver.Chrome, config: Dict) -> bool:
    """將餐點加入購物車"""
    try:
        search_params = config.get("search_parameters", {})
        cart_config = search_params.get("addToCart", {})
        selector = cart_config.get("selector")
        backup_selectors = cart_config.get("backup_selectors", [])
        wait_time = cart_config.get("wait_after_click", 2)
        
        if not selector:
            print("加入購物車按鈕配置不完整")
            return False
        
        print("嘗試加入購物車...")
        
        # 等待頁面加載
        time.sleep(2)
        
        # 保存頁面源碼以進行調試
        save_page_source(driver, {}, "before_add_to_cart")
        
        # 等待加入購物車按鈕出現
        print(f"使用選擇器尋找加入購物車按鈕: {selector}")
        cart_button = wait_for_element(driver, By.XPATH, selector)
        
        # 如果主選擇器找不到元素，嘗試備用選擇器
        if not cart_button and backup_selectors:
            print("使用主選擇器找不到加入購物車按鈕，嘗試備用選擇器")
            for backup_selector in backup_selectors:
                print(f"嘗試備用選擇器: {backup_selector}")
                cart_button = wait_for_element(driver, By.XPATH, backup_selector)
                if cart_button:
                    print(f"使用備用選擇器找到加入購物車按鈕: {backup_selector}")
                    break
        
        # 如果找不到按鈕，嘗試找尋其他可能的加入購物車按鈕
        if not cart_button:
            print("尋找替代的加入購物車按鈕...")
            alternatives = [
                "//button[contains(., '加入購物車')]",
                "//button[contains(., '添加到购物车')]",
                "//button[contains(., 'Add to cart')]",
                "//button[contains(., 'Add to bag')]",
                "//button[contains(@class, 'add-to-cart')]",
                "//button[contains(@id, 'add-to-cart')]",
                "//button[contains(@class, 'cart')]",
                "//button[contains(@id, 'cart')]",
                "//button[text()='加入']",
                "//button[text()='Add']"
            ]
            
            for alt_selector in alternatives:
                cart_button = wait_for_element(driver, By.XPATH, alt_selector)
                if cart_button:
                    print(f"找到替代的加入購物車按鈕: {alt_selector}")
                    break
        
        if not cart_button:
            print("找不到加入購物車按鈕")
            save_page_source(driver, {}, "add_to_cart_button_not_found")
            return False
        
        print("找到加入購物車按鈕，嘗試點擊...")
        
        # 確保元素在視窗中
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", cart_button)
        time.sleep(1)
        
        if not safe_click(driver, cart_button):
            print("點擊加入購物車按鈕失敗，嘗試JavaScript點擊")
            driver.execute_script("arguments[0].click();", cart_button)
        
        # 等待頁面加載
        time.sleep(wait_time)
        
        # 拍攝螢幕截圖
        take_screenshot(driver, config, "added_to_cart")
        
        # 保存頁面源碼以進行調試
        save_page_source(driver, {}, "added_to_cart")
        
        return True
        
    except Exception as e:
        print(f"加入購物車時發生錯誤: {str(e)}")
        return False

# ===== 資料提取區 =====

def extract_list_items(page_source: str, config: Dict) -> List[Dict]:
    """從列表頁面提取餐廳資訊"""
    try:
        list_config = config.get("list_page", {})
        container_xpath = list_config.get("container_xpath")
        item_xpath = list_config.get("item_xpath")
        fields_config = list_config.get("fields", {})
        
        if not all([container_xpath, item_xpath, fields_config]):
            print("列表頁配置不完整")
            return []
        
        # 解析 HTML
        tree = html.fromstring(page_source)
        
        # 找到容器
        container = tree.xpath(container_xpath)
        if not container:
            print("找不到列表容器")
            return []
        
        # 提取所有餐廳項目
        items = container[0].xpath(item_xpath)
        results = []
        
        for item in items:
            item_data = {}
            for field_name, field_config in fields_config.items():
                xpath = field_config.get("xpath")
                field_type = field_config.get("type", "text")
                
                if not xpath:
                    continue
                
                try:
                    if field_type == "text":
                        value = item.xpath(xpath)
                        value = value[0] if value else ""
                    elif field_type == "attribute":
                        value = item.xpath(xpath)
                        value = value[0] if value else ""
                    elif field_type == "list":
                        value = item.xpath(xpath)
                    else:
                        value = ""
                    
                    item_data[field_name] = clean_text(value) if isinstance(value, str) else value
                    
                except Exception as e:
                    print(f"提取欄位 {field_name} 時發生錯誤: {str(e)}")
                    item_data[field_name] = ""
            
            results.append(item_data)
        
        return results
        
    except Exception as e:
        print(f"提取列表項目時發生錯誤: {str(e)}")
        return []


# ===== 主程式區 =====

def main() -> None:
    """主程式"""
    try:
        # 載入配置
        config_path = "examples/config/ubereats/basic/search.json"
        config = load_config(config_path)
        
        # 設置 WebDriver
        driver = setup_webdriver(config)
        
        try:
            # 訪問首頁
            driver.get(config.get("base_url"))
            print(f"已訪問網站: {config.get('base_url')}")
            time.sleep(config.get("delays", {}).get("page_load", 5))
            
            # 嘗試通過localStorage設置地址
            set_local_storage(driver, config)
            
            # 嘗試加載Cookie
            load_cookies(driver, config)
            
            # 拍攝螢幕截圖
            take_screenshot(driver, config, "homepage")
            
            # 保存頁面源碼以便調試
            save_page_source(driver, config, "homepage")
            
            # 設置搜尋參數(地址和搜尋關鍵字)
            if not set_search_parameters(driver, config):
                print("設置搜尋參數失敗，嘗試手動處理")
                
                # 手動處理地址設置
                if not set_address(driver, config.get("search_parameters", {})):
                    print("手動設置地址失敗")
                    return
                    
                # 檢查當前URL，判斷是否需要設置搜尋關鍵字
                current_url = driver.current_url
                if "feed" in current_url or "store" in current_url:
                    print("已進入搜尋頁面，設置搜尋關鍵字")
                    if not set_search_keyword(driver, config.get("search_parameters", {})):
                        print("設置搜尋關鍵字失敗")
                        return
            
            # 保存成功的Cookie
            save_cookies(driver, config)
            
            # 拍攝螢幕截圖
            take_screenshot(driver, config, "search_results")
            
            # 提取列表頁資訊
            list_items = extract_list_items(driver.page_source, config)
            print(f"找到 {len(list_items)} 個餐廳")
            
            if len(list_items) == 0:
                print("未找到任何餐廳，保存頁面源碼以進行調試")
                save_page_source(driver, config, "no_restaurants_found")
            
            # 選擇餐廳
            if not find_and_click_store(driver, config):
                print("選擇餐廳失敗")
                return
            
            # 選擇食物類別
            if not select_food_category(driver, config):
                print("選擇食物類別失敗，嘗試繼續執行")
                # 繼續執行，有些餐廳可能沒有明確的類別
            
            # 選擇餐點
            if not select_food_item(driver, config):
                print("選擇餐點失敗")
                return
            
            # 選擇餐點選項（如果有）
            if not select_food_option(driver, config):
                print("選擇餐點選項失敗，嘗試繼續執行")
                # 繼續執行，有些餐點可能沒有選項
            
            # 加入購物車
            if not add_to_cart(driver, config):
                print("加入購物車失敗")
                return
            
            print("成功將餐點加入購物車！")
            take_screenshot(driver, config, "cart_success")
            
            # 保存結果
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = "examples/data/output"
            os.makedirs(output_dir, exist_ok=True)
            
            output_file = os.path.join(output_dir, f"ubereats_order_{timestamp}.json")
            
            # 簡單記錄成功訊息
            result = {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "message": "成功將餐點加入購物車",
                "details": {
                    "restaurant": config.get("search_parameters", {}).get("wantStore", {}).get("default"),
                    "item": config.get("search_parameters", {}).get("wantItem", {}).get("default"),
                    "category": config.get("search_parameters", {}).get("wantCategory", {}).get("default"),
                }
            }
            
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(format_for_json(result), f, ensure_ascii=False, indent=2)
            
            print(f"結果已保存至: {output_file}")
            
        finally:
            # 關閉瀏覽器（調試模式下不會自動關閉）
            if config.get("advanced_settings", {}).get("debug_mode", False):
                print("調試模式：瀏覽器保持開啟")
            else:
                driver.quit()
                print("已關閉瀏覽器")
            
    except Exception as e:
        print(f"程式執行時發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()