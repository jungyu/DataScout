"""
實價登錄爬蟲程式
基於配置文件的實價登錄網站資料爬取工具
支持縣市、鄉鎮區和建物型態選擇，URL參數式分頁
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


def normalize_url(url: str, base_domain: str = "https://price.houseprice.tw") -> str:
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
    
    # 調試模式：不自動關閉瀏覽器
    chrome_options.add_experimental_option("detach", True)
    
    print("初始化 Chrome WebDriver...")
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    
    # 設置隱式等待時間
    driver.implicitly_wait(10)
    
    return driver


def wait_for_element(driver: webdriver.Chrome, by: str, selector: str, timeout: int = 10) -> Any:
    """等待元素出現並返回"""
    wait = WebDriverWait(driver, timeout)
    return wait.until(EC.presence_of_element_located((by, selector)))


def safe_click(driver: webdriver.Chrome, element, retries: int = 3) -> bool:
    """安全點擊元素，處理可能的點擊攔截"""
    for attempt in range(retries):
        try:
            element.click()
            return True
        except ElementClickInterceptedException:
            print(f"點擊被攔截，嘗試使用 JavaScript 點擊 (嘗試 {attempt+1}/{retries})")
            try:
                driver.execute_script("arguments[0].click();", element)
                return True
            except Exception as e:
                print(f"JavaScript 點擊失敗: {str(e)}")
                time.sleep(1)
        except Exception as e:
            print(f"點擊失敗: {str(e)}")
            time.sleep(1)
    
    return False


# ===== 搜尋參數設置區 =====

def set_search_parameters(driver: webdriver.Chrome, config: Dict) -> bool:
    """設置搜尋參數並點擊搜尋按鈕"""
    try:
        search_params = config.get("search_parameters", {})
        
        # 設置縣市
        if not select_city(driver, search_params):
            print("設置縣市失敗")
            return False
        
        # 設置鄉鎮區
        if not select_district(driver, search_params):
            print("設置鄉鎮區失敗")
            return False
        
        # 設置建物型態
        if not select_building_type(driver, search_params):
            print("設置建物型態失敗")
            return False
        
        # 點擊搜尋按鈕
        print("準備點擊搜尋按鈕...")
        
        # 確保截圖目錄存在
        os.makedirs("examples/data/screenshots", exist_ok=True)

        # 嘗試截圖以便診斷
        try:
            screenshot_path = "examples/data/screenshots/before_search_button.png"
            driver.save_screenshot(screenshot_path)
            print(f"已保存點擊搜尋按鈕前截圖：{screenshot_path}")
        except Exception as ss_err:
            print(f"保存截圖時出錯: {str(ss_err)}")
        
        # 使用JavaScript直接找到並點擊搜尋按鈕
        search_button_clicked = driver.execute_script("""
            // 嘗試多種方法找到搜尋按鈕
            var searchButton = null;
            
            // 方法1: 使用提供的選擇器
            try {
                var buttonSelector = arguments[0];
                searchButton = document.evaluate(buttonSelector, document, null, 
                                             XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                console.log('通過選擇器找到搜尋按鈕:', searchButton ? searchButton.outerHTML : 'null');
            } catch (e) {
                console.error('通過選擇器查找搜尋按鈕失敗:', e);
            }
            
            // 方法2: 使用常見的搜尋按鈕類或文本
            if (!searchButton) {
                var possibleButtons = [
                    document.querySelector('button.search-btn'),
                    document.querySelector('a.search_btn'),
                    document.querySelector('button.search_btn'),
                    document.querySelector('a.search-btn'),
                    ...Array.from(document.querySelectorAll('button')).filter(b => b.textContent.includes('搜尋')),
                    ...Array.from(document.querySelectorAll('a')).filter(a => a.textContent.includes('搜尋'))
                ].filter(Boolean);
                
                if (possibleButtons.length > 0) {
                    searchButton = possibleButtons[0];
                    console.log('通過備用方法找到搜尋按鈕:', searchButton.outerHTML);
                }
            }
            
            // 方法3: 查找頁面上所有具有搜尋關鍵字的元素
            if (!searchButton) {
                var allElements = document.querySelectorAll('*');
                for (var i = 0; i < allElements.length; i++) {
                    var el = allElements[i];
                    if (el.textContent && el.textContent.includes('搜尋') && 
                        (el.tagName === 'BUTTON' || el.tagName === 'A' || 
                         el.tagName === 'INPUT' || el.tagName === 'DIV')) {
                        searchButton = el;
                        console.log('通過文本內容找到搜尋按鈕:', el.outerHTML);
                        break;
                    }
                }
            }
            
            if (!searchButton) {
                console.error('無法找到搜尋按鈕');
                return false;
            }
            
            // 確保按鈕可見
            searchButton.scrollIntoView({block: 'center', behavior: 'smooth'});
            
            // 等待滾動完成並點擊按鈕
            return new Promise(resolve => {
                setTimeout(function() {
                    try {
                        // 先移除可能的阻礙元素
                        var overlays = document.querySelectorAll('.modal, .overlay, .dialog');
                        overlays.forEach(overlay => {
                            if (overlay && overlay.style) {
                                overlay.style.display = 'none';
                            }
                        });
                        
                        // 確保按鈕是啟用狀態
                        searchButton.disabled = false;
                        
                        // 嘗試直接點擊
                        searchButton.click();
                        console.log('搜尋按鈕點擊成功');
                        resolve(true);
                    } catch (e) {
                        console.error('搜尋按鈕點擊失敗:', e);
                        
                        // 備用方案1: 使用事件分發
                        try {
                            var clickEvent = new MouseEvent('click', {
                                bubbles: true,
                                cancelable: true,
                                view: window
                            });
                            searchButton.dispatchEvent(clickEvent);
                            console.log('搜尋按鈕事件分發成功');
                            resolve(true);
                        } catch (e2) {
                            console.error('搜尋按鈕事件分發失敗:', e2);
                            
                            // 備用方案2: 如果是<a>標籤，直接導航
                            try {
                                if (searchButton.tagName === 'A' && searchButton.href) {
                                    window.location.href = searchButton.href;
                                    console.log('通過href導航成功');
                                    resolve(true);
                                } else {
                                    resolve(false);
                                }
                            } catch (e3) {
                                console.error('通過href導航失敗:', e3);
                                resolve(false);
                            }
                        }
                    }
                }, 1000);
            });
        """, search_params.get("search_button", {}).get("selector", "//a[@class='search_btn']"))
        
        if not search_button_clicked:
            print("通過JavaScript點擊搜尋按鈕失敗，嘗試Selenium方法")
            
            # 備用方案：使用Selenium的方法
            try:
                # 嘗試多種搜尋按鈕選擇器
                search_button_selectors = [
                    "//a[@class='search_btn']",
                    "//button[contains(@class,'search-btn')]",
                    "//a[contains(@class,'search_btn')]",
                    "//button[contains(@class,'search_btn')]",
                    "//a[contains(@class,'search-btn')]",
                    "//button[contains(text(),'搜尋')]",
                    "//a[contains(text(),'搜尋')]",
                    "//*[contains(text(),'搜尋') and (self::button or self::a or self::input or self::div)]"
                ]
                
                for selector in search_button_selectors:
                    try:
                        wait = WebDriverWait(driver, 5)
                        search_button = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                        
                        # 滾動到按鈕位置
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", search_button)
                        time.sleep(1)
                        
                        # 嘗試點擊
                        search_button.click()
                        print(f"通過選擇器 '{selector}' 成功點擊搜尋按鈕")
                        break
                    except Exception as e:
                        print(f"使用選擇器 '{selector}' 點擊搜尋按鈕失敗: {str(e)}")
                        continue
                else:  # 如果for循環正常結束（沒有break），表示所有選擇器都失敗了
                    # 最後嘗試：用ActionChains模擬點擊
                    try:
                        # 嘗試通過文本找到按鈕
                        elements = driver.find_elements(By.XPATH, "//*[contains(text(),'搜尋')]")
                        if elements:
                            action = ActionChains(driver)
                            action.move_to_element(elements[0]).click().perform()
                            print("通過ActionChains成功點擊搜尋按鈕")
                        else:
                            print("找不到任何包含'搜尋'文本的元素")
                            return False
                    except Exception as action_err:
                        print(f"ActionChains點擊搜尋按鈕失敗: {str(action_err)}")
                        return False
            except Exception as e:
                print(f"點擊搜尋按鈕時出錯: {str(e)}")
                return False
        
        # 等待搜尋結果加載
        print("等待搜尋結果加載...")
        time.sleep(10)
        
        # 嘗試截圖以便診斷
        try:
            screenshot_path = "examples/data/screenshots/after_search_button.png"
            driver.save_screenshot(screenshot_path)
            print(f"已保存點擊搜尋按鈕後截圖：{screenshot_path}")
        except Exception as ss_err:
            print(f"保存截圖時出錯: {str(ss_err)}")
        
        # 確認是否已進入搜尋結果頁面
        result_page_loaded = driver.execute_script("""
            // 檢查是否存在搜尋結果元素
            var resultTable = document.querySelector('div.table-responsive');
            var resultItems = document.querySelectorAll('tr.group[data-sid]');
            
            if (resultTable || resultItems.length > 0) {
                console.log('搜尋結果頁面已加載，找到結果元素');
                return true;
            }
            
            // 檢查URL是否已變更
            if (window.location.href.includes('/list?') || 
                window.location.pathname !== '/list') {
                console.log('URL已變更，可能已進入搜尋結果頁面');
                return true;
            }
            
            console.log('未檢測到搜尋結果頁面特徵');
            return false;
        """)
        
        if not result_page_loaded:
            print("未檢測到搜尋結果頁面，可能搜尋失敗")
            # 即使沒有檢測到結果頁面，也繼續執行，因為可能是檢測邏輯問題
        
        return True
    except Exception as e:
        print(f"設置搜尋參數時出錯: {str(e)}")
        
        # 保存出錯時的截圖
        try:
            screenshot_path = f"examples/data/screenshots/search_params_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            driver.save_screenshot(screenshot_path)
            print(f"已保存錯誤截圖：{screenshot_path}")
        except Exception as ss_err:
            print(f"保存錯誤截圖時出錯: {str(ss_err)}")
            
        return False


def select_city(driver: webdriver.Chrome, search_params: Dict) -> bool:
    """選擇縣市 - 更穩定的實現"""
    city_config = search_params.get("city", {})
    if not city_config:
        return True
    
    try:
        print("開始選擇縣市...")
        
        # 等待頁面完全加載
        time.sleep(10)
        
        # 嘗試截圖以便診斷
        try:
            screenshot_path = "examples/data/screenshots/before_city_selection.png"
            driver.save_screenshot(screenshot_path)
            print(f"已保存縣市選擇前截圖：{screenshot_path}")
        except Exception as ss_err:
            print(f"保存截圖時出錯: {str(ss_err)}")
        
        # 使用JavaScript直接操作DOM選擇縣市
        city_value = city_config.get("default", "")
        container_selector = city_config.get("container_selector")
        
        # 1. 先確認並點擊縣市下拉框
        dropdown_clicked = driver.execute_script("""
            // 先確認level_1區域是否已顯示
            var level1Section = document.querySelector('section.level_1');
            var isVisible = level1Section && window.getComputedStyle(level1Section).display !== 'none';
            
            // 如果已經顯示，不需要再點擊下拉框
            if (isVisible) {
                console.log('縣市下拉框已經打開');
                return true;
            }
            
            // 找到下拉框容器
            var container = document.evaluate(arguments[0], document, null, 
                                          XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
            if (!container) {
                console.error('找不到縣市容器');
                return false;
            }
            
            // 調試信息
            console.log('找到縣市容器:', container.outerHTML);
            
            // 確保滾動到可見區域
            container.scrollIntoView({block: 'center', behavior: 'smooth'});
            
            // 等待滾動完成並點擊
            return new Promise(resolve => {
                setTimeout(function() {
                    try {
                        // 直接點擊
                        container.click();
                        console.log('縣市容器點擊成功');
                        resolve(true);
                    } catch (e) {
                        console.error('縣市容器點擊失敗:', e);
                        
                        // 備用方案：使用事件分發
                        try {
                            var clickEvent = new MouseEvent('click', {
                                bubbles: true,
                                cancelable: true,
                                view: window
                            });
                            container.dispatchEvent(clickEvent);
                            console.log('縣市容器事件分發成功');
                            resolve(true);
                        } catch (e2) {
                            console.error('縣市容器事件分發失敗:', e2);
                            resolve(false);
                        }
                    }
                }, 1000);
            });
        """, container_selector)
        
        if not dropdown_clicked:
            print("無法點擊縣市下拉框")
            return False
        
        print("縣市下拉框已打開")
        time.sleep(5)  # 等待下拉框完全展開
        
        # 嘗試截圖以便診斷
        try:
            screenshot_path = "examples/data/screenshots/city_dropdown_opened.png"
            driver.save_screenshot(screenshot_path)
            print(f"已保存縣市下拉框打開後截圖：{screenshot_path}")
        except Exception as ss_err:
            print(f"保存截圖時出錯: {str(ss_err)}")
        
        # 2. 選擇指定的縣市選項
        city_selected = driver.execute_script("""
            var cityValue = arguments[0];
            
            // 等待確保下拉框已顯示
            return new Promise(resolve => {
                setTimeout(function() {
                    // 準備多個選擇器以增加成功率
                    var selectors = [
                        `//section[@class='level_1']//span[text()='${cityValue}']`,
                        `//section[contains(@class,'level_1')]//label[contains(@class,'custom-radio')]//span[text()='${cityValue}']`,
                        `//section[contains(@class,'level_1')]//span[contains(text(),'${cityValue}')]`
                    ];
                    
                    // 嘗試不同的選擇器
                    var option = null;
                    for (var i = 0; i < selectors.length; i++) {
                        try {
                            option = document.evaluate(selectors[i], document, null, 
                                                   XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                            if (option) {
                                console.log('找到縣市選項:', option.outerHTML);
                                break;
                            }
                        } catch (e) {
                            console.error('選擇器錯誤:', e);
                        }
                    }
                    
                    // 如果找不到選項，尋找備用方案
                    if (!option) {
                        console.log('未找到指定縣市選項，嘗試備用方案');
                        
                        // 嘗試通過文本內容查找
                        var allSpans = document.querySelectorAll('section.level_1 span');
                        for (var i = 0; i < allSpans.length; i++) {
                            if (allSpans[i].textContent.trim() === cityValue) {
                                option = allSpans[i];
                                console.log('通過文本內容找到縣市選項');
                                break;
                            }
                        }
                    }
                    
                    // 如果仍找不到選項，返回失敗
                    if (!option) {
                        console.error('找不到縣市選項:', cityValue);
                        resolve(false);
                        return;
                    }
                    
                    // 確保滾動到可見區域
                    option.scrollIntoView({block: 'center', behavior: 'smooth'});
                    
                    // 等待滾動完成後點擊
                    setTimeout(function() {
                        try {
                            // 直接點擊
                            option.click();
                            console.log('縣市選項點擊成功');
                            resolve(true);
                        } catch (e) {
                            console.error('縣市選項點擊失敗:', e);
                            
                            // 備用方案1：點擊父元素
                            try {
                                if (option.parentElement && option.parentElement.tagName === 'LABEL') {
                                    option.parentElement.click();
                                    console.log('通過父元素點擊縣市選項成功');
                                    resolve(true);
                                    return;
                                }
                            } catch (e2) {
                                console.error('父元素點擊失敗:', e2);
                            }
                            
                            // 備用方案2：事件分發
                            try {
                                var clickEvent = new MouseEvent('click', {
                                    bubbles: true,
                                    cancelable: true,
                                    view: window
                                });
                                option.dispatchEvent(clickEvent);
                                console.log('縣市選項事件分發成功');
                                resolve(true);
                            } catch (e3) {
                                console.error('縣市選項事件分發失敗:', e3);
                                resolve(false);
                            }
                        }
                    }, 1000);
                }, 2000); // 等待2秒確保下拉框已完全顯示
            });
        """, city_value)
        
        if not city_selected:
            print(f"無法選擇縣市：{city_value}")
            return False
        
        print(f"已選擇縣市：{city_value}")
        time.sleep(10)  # 給予充足時間讓選擇生效並更新DOM
        
        # 最後截圖以確認選擇結果
        try:
            screenshot_path = "examples/data/screenshots/after_city_selection.png"
            driver.save_screenshot(screenshot_path)
            print(f"已保存縣市選擇後截圖：{screenshot_path}")
        except Exception as ss_err:
            print(f"保存截圖時出錯: {str(ss_err)}")
        
        return True
    except Exception as e:
        print(f"選擇縣市時出錯: {str(e)}")
        
        # 保存出錯時的截圖
        try:
            screenshot_path = f"examples/data/screenshots/city_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            driver.save_screenshot(screenshot_path)
            print(f"已保存錯誤截圖：{screenshot_path}")
        except Exception as ss_err:
            print(f"保存錯誤截圖時出錯: {str(ss_err)}")
            
        return False

def select_district(driver: webdriver.Chrome, search_params: Dict) -> bool:
    """選擇鄉鎮區 - 更穩定的實現"""
    district_config = search_params.get("district", {})
    if not district_config:
        return True
    
    try:
        print("開始選擇鄉鎮區...")
        
        # 等待縣市選擇完成後的頁面更新
        time.sleep(10)
        
        # 嘗試截圖以便診斷
        try:
            screenshot_path = "examples/data/screenshots/before_district_selection.png"
            driver.save_screenshot(screenshot_path)
            print(f"已保存鄉鎮區選擇前截圖：{screenshot_path}")
        except Exception as ss_err:
            print(f"保存截圖時出錯: {str(ss_err)}")
        
        # 使用JavaScript直接操作DOM選擇鄉鎮區
        district_value = district_config.get("default", "")
        container_selector = district_config.get("container_selector")
        
        # 1. 先確認並點擊鄉鎮區下拉框
        dropdown_clicked = driver.execute_script("""
            // 先確認level_2區域是否已顯示
            var level2Section = document.querySelector('section.level_2');
            var isLevel2Visible = level2Section && window.getComputedStyle(level2Section).display !== 'none';
            
            if (isLevel2Visible) {
                // 檢查下拉框是否已展開（判斷是否顯示鄉鎮區選項）
                var districtOptions = document.querySelectorAll('section.level_2 label.custom-radio');
                if (districtOptions.length > 0) {
                    console.log('鄉鎮區下拉框已經打開，找到', districtOptions.length, '個選項');
                    return true;
                }
            }
            
            // 找到下拉框容器
            var container = document.evaluate(arguments[0], document, null, 
                                          XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
            if (!container) {
                console.error('找不到鄉鎮區容器');
                return false;
            }
            
            // 調試信息
            console.log('找到鄉鎮區容器:', container.outerHTML);
            
            // 確保滾動到可見區域
            container.scrollIntoView({block: 'center', behavior: 'smooth'});
            
            // 等待滾動完成並點擊
            return new Promise(resolve => {
                setTimeout(function() {
                    try {
                        // 模擬用戶點擊行為，先移動鼠標到元素上
                        var mouseOverEvent = new MouseEvent('mouseover', {
                            bubbles: true,
                            cancelable: true,
                            view: window
                        });
                        container.dispatchEvent(mouseOverEvent);
                        
                        // 直接點擊
                        container.click();
                        console.log('鄉鎮區容器點擊成功');
                        resolve(true);
                    } catch (e) {
                        console.error('鄉鎮區容器點擊失敗:', e);
                        
                        // 備用方案1：使用事件分發
                        try {
                            var clickEvent = new MouseEvent('click', {
                                bubbles: true,
                                cancelable: true,
                                view: window
                            });
                            container.dispatchEvent(clickEvent);
                            console.log('鄉鎮區容器事件分發成功');
                            resolve(true);
                        } catch (e2) {
                            console.error('鄉鎮區容器事件分發失敗:', e2);
                            
                            // 備用方案2：強制顯示level_2區域
                            try {
                                if (level2Section) {
                                    level2Section.style.display = 'block';
                                    console.log('已強制顯示level_2區域');
                                    resolve(true);
                                } else {
                                    console.error('找不到level_2區域');
                                    resolve(false);
                                }
                            } catch (e3) {
                                console.error('強制顯示level_2區域失敗:', e3);
                                resolve(false);
                            }
                        }
                    }
                }, 1000);
            });
        """, container_selector)
        
        if not dropdown_clicked:
            print("無法點擊鄉鎮區下拉框")
            return False
        
        print("鄉鎮區下拉框已打開或嘗試強制打開")
        time.sleep(5)  # 等待下拉框完全展開
        
        # 嘗試截圖以便診斷
        try:
            screenshot_path = "examples/data/screenshots/district_dropdown_opened.png"
            driver.save_screenshot(screenshot_path)
            print(f"已保存鄉鎮區下拉框打開後截圖：{screenshot_path}")
        except Exception as ss_err:
            print(f"保存截圖時出錯: {str(ss_err)}")
        
        # 2. 選擇指定的鄉鎮區選項
        district_selected = driver.execute_script("""
            var districtValue = arguments[0];
            
            // 等待確保下拉框已顯示
            return new Promise(resolve => {
                setTimeout(function() {
                    // 準備多個選擇器以增加成功率
                    var selectors = [
                        `//section[@class='level_2']//span[text()='${districtValue}']`,
                        `//section[contains(@class,'level_2')]//label[contains(@class,'custom-radio')]//span[text()='${districtValue}']`,
                        `//section[contains(@class,'level_2')]//span[contains(text(),'${districtValue}')]`
                    ];
                    
                    // 嘗試不同的選擇器
                    var option = null;
                    for (var i = 0; i < selectors.length; i++) {
                        try {
                            option = document.evaluate(selectors[i], document, null, 
                                                   XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                            if (option) {
                                console.log('找到鄉鎮區選項:', option.outerHTML);
                                break;
                            }
                        } catch (e) {
                            console.error('選擇器錯誤:', e);
                        }
                    }
                    
                    // 如果找不到選項，尋找備用方案
                    if (!option) {
                        console.log('未找到指定鄉鎮區選項，嘗試備用方案');
                        
                        // 嘗試通過文本內容查找
                        var allSpans = document.querySelectorAll('section.level_2 span');
                        for (var i = 0; i < allSpans.length; i++) {
                            if (allSpans[i].textContent.trim() === districtValue) {
                                option = allSpans[i];
                                console.log('通過文本內容找到鄉鎮區選項');
                                break;
                            }
                        }
                        
                        // 如果仍找不到，嘗試選擇"全區"
                        if (!option) {
                            option = document.evaluate("//section[contains(@class,'level_2')]//span[text()='全區']", 
                                                   document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                            if (option) {
                                console.log('找到"全區"選項作為備用');
                            }
                        }
                    }
                    
                    // 如果仍找不到選項，返回失敗
                    if (!option) {
                        console.error('找不到鄉鎮區選項:', districtValue);
                        
                        // 最後嘗試：修改選擇器文本
                        var selectedText = document.querySelector('div.area_search div.custom_select_2:nth-child(2) span.select_txt');
                        if (selectedText) {
                            selectedText.textContent = districtValue;
                            console.log('已直接修改選擇文本為:', districtValue);
                            resolve(true);
                            return;
                        }
                        
                        resolve(false);
                        return;
                    }
                    
                    // 確保滾動到可見區域
                    option.scrollIntoView({block: 'center', behavior: 'smooth'});
                    
                    // 等待滾動完成後點擊
                    setTimeout(function() {
                        try {
                            // 直接點擊
                            option.click();
                            console.log('鄉鎮區選項點擊成功');
                            resolve(true);
                        } catch (e) {
                            console.error('鄉鎮區選項點擊失敗:', e);
                            
                            // 備用方案1：點擊父元素
                            try {
                                if (option.parentElement && option.parentElement.tagName === 'LABEL') {
                                    option.parentElement.click();
                                    console.log('通過父元素點擊鄉鎮區選項成功');
                                    resolve(true);
                                }
                            } catch (e2) {
                                console.error('父元素點擊失敗:', e2);
                            }
                            
                            // 備用方案2：事件分發
                            try {
                                var clickEvent = new MouseEvent('click', {
                                    bubbles: true,
                                    cancelable: true,
                                    view: window
                                });
                                option.dispatchEvent(clickEvent);
                                console.log('鄉鎮區選項事件分發成功');
                                resolve(true);
                            } catch (e3) {
                                console.error('鄉鎮區選項事件分發失敗:', e3);
                                resolve(false);
                            }
                        }
                    }, 1000);
                }, 2000); // 等待2秒確保下拉框已完全顯示
            });
        """, district_value)
        
        if not district_selected:
            print(f"無法選擇鄉鎮區：{district_value}")
            
            # 如果選擇失敗，嘗試一個直接的備用方案
            backup_success = driver.execute_script("""
                var districtValue = arguments[0];
                var selectText = document.querySelector('div.area_search div.custom_select_2:nth-child(2) span.select_txt');
                if (selectText) {
                    selectText.textContent = districtValue;
                    console.log('通過備用方案設置鄉鎮區為:', districtValue);
                    return true;
                }
                return false;
            """, district_value)
            
            if backup_success:
                print(f"已通過備用方案設置鄉鎮區為：{district_value}")
            else:
                return False
        
        print(f"已選擇鄉鎮區：{district_value}")
        time.sleep(10)  # 給予充足時間讓選擇生效並更新DOM
        
        # 最後截圖以確認選擇結果
        try:
            screenshot_path = "examples/data/screenshots/after_district_selection.png"
            driver.save_screenshot(screenshot_path)
            print(f"已保存鄉鎮區選擇後截圖：{screenshot_path}")
        except Exception as ss_err:
            print(f"保存截圖時出錯: {str(ss_err)}")
        
        return True
    except Exception as e:
        print(f"選擇鄉鎮區時出錯: {str(e)}")
        
        # 保存出錯時的截圖
        try:
            screenshot_path = f"examples/data/screenshots/district_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            driver.save_screenshot(screenshot_path)
            print(f"已保存錯誤截圖：{screenshot_path}")
        except Exception as ss_err:
            print(f"保存錯誤截圖時出錯: {str(ss_err)}")
            
        return False


def select_building_type(driver: webdriver.Chrome, search_params: Dict) -> bool:
    """選擇建物型態 - 使用直接JavaScript操作"""
    building_type_config = search_params.get("building_type", {})
    if not building_type_config:
        return True
    
    try:
        print("開始選擇建物型態...")
        
        # 等待足夠時間確保縣市和鄉鎮區選擇已完成
        time.sleep(10)
        
        # 使用JavaScript直接點擊建物型態容器
        container_selector = building_type_config.get("container_selector")
        
        # 嘗試截圖以便診斷
        try:
            screenshot_path = "examples/data/screenshots/before_building_type.png"
            driver.save_screenshot(screenshot_path)
            print(f"已保存建物型態選擇前截圖：{screenshot_path}")
        except Exception as ss_err:
            print(f"保存截圖時出錯: {str(ss_err)}")
        
        # 直接使用JavaScript找到並點擊建物型態下拉框
        container_clicked = driver.execute_script("""
            // 1. 首先嘗試使用XPath找到容器
            var container = document.evaluate(arguments[0], document, null, 
                                          XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
            
            // 2. 如果找不到，嘗試使用更通用的選擇器
            if (!container) {
                container = document.querySelector("div.rp_use div.custom_select_2");
                if (!container) {
                    console.error('找不到建物型態容器');
                    return false;
                }
            }
            
            // 3. 顯示在控制台用於調試
            console.log("找到建物型態容器:", container);
            
            // 4. 滾動到容器位置
            container.scrollIntoView({block: 'center', behavior: 'smooth'});
            
            // 5. 等待滾動完成
            return new Promise(resolve => {
                setTimeout(function() {
                    // 使用點擊事件
                    try {
                        container.click();
                        console.log("建物型態容器點擊成功");
                        resolve(true);
                    } catch(e) {
                        console.error("點擊建物型態容器失敗:", e);
                        
                        // 嘗試使用事件分發
                        try {
                            var clickEvent = new MouseEvent('click', {
                                bubbles: true,
                                cancelable: true,
                                view: window
                            });
                            container.dispatchEvent(clickEvent);
                            console.log("建物型態容器事件分發成功");
                            resolve(true);
                        } catch(e2) {
                            console.error("建物型態容器事件分發失敗:", e2);
                            resolve(false);
                        }
                    }
                }, 1000);
            });
        """, container_selector)
        
        if not container_clicked:
            print("無法點擊建物型態容器")
            return False
        
        print("已點擊建物型態容器")
        time.sleep(5)  # 給足夠時間讓下拉選單顯示
        
        # 再次截圖以檢查下拉選單是否顯示
        try:
            screenshot_path = "examples/data/screenshots/after_dropdown.png"
            driver.save_screenshot(screenshot_path)
            print(f"已保存下拉選單展開後截圖：{screenshot_path}")
        except Exception as ss_err:
            print(f"保存截圖時出錯: {str(ss_err)}")
        
        # 選擇建物型態
        building_type_value = building_type_config.get("default", "")
        print(f"準備選擇建物型態: {building_type_value}")
        
        # 使用JavaScript精確選擇建物型態
        option_selected = driver.execute_script("""
            var buildingTypeValue = arguments[0];
            
            // 1. 等待確保下拉選單已經顯示
            return new Promise(resolve => {
                setTimeout(function() {
                    // 2. 準備多個可能的選擇器
                    var selectors = [
                        `//div[contains(@class,'rp_use')]//ul//li//label//span[contains(text(),'${buildingTypeValue}')]`,
                        `//div[contains(@class,'flex_con')]//ul//li//label//span[contains(text(),'${buildingTypeValue}')]`,
                        `//section[contains(@class,'flex_con')]//ul//li//label//span[contains(text(),'${buildingTypeValue}')]`
                    ];
                    
                    // 3. 嘗試每個選擇器
                    var option = null;
                    for (var i = 0; i < selectors.length; i++) {
                        try {
                            option = document.evaluate(selectors[i], document, null, 
                                                   XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                            if (option) {
                                console.log("找到建物型態選項:", option);
                                break;
                            }
                        } catch (e) {
                            console.error('選擇器錯誤:', e);
                        }
                    }
                    
                    // 4. 如果沒找到，嘗試更簡單的 DOM 查詢
                    if (!option) {
                        var allOptions = document.querySelectorAll("div.rp_use span");
                        console.log("找到選項數量:", allOptions.length);
                        
                        for (var i = 0; i < allOptions.length; i++) {
                            if (allOptions[i].textContent.includes(buildingTypeValue)) {
                                option = allOptions[i];
                                console.log("通過文本內容找到建物型態選項:", option);
                                break;
                            }
                        }
                    }
                    
                    // 5. 如果仍然沒找到，嘗試選擇「建物型態不限」
                    if (!option) {
                        console.log("找不到指定建物型態，嘗試選擇「建物型態不限」");
                        option = document.evaluate("//div[contains(@class,'rp_use')]//span[contains(text(),'建物型態不限')]", 
                                               document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                    }
                    
                    // 6. 如果仍然沒找到任何選項，返回失敗
                    if (!option) {
                        console.error("找不到任何可選的建物型態選項");
                        resolve(false);
                        return;
                    }
                    
                    // 7. 滾動到選項位置
                    option.scrollIntoView({block: 'center', behavior: 'smooth'});
                    
                    // 8. 等待滾動完成後點擊
                    setTimeout(function() {
                        try {
                            // 直接點擊
                            option.click();
                            console.log("建物型態選項點擊成功");
                            resolve(true);
                        } catch (e) {
                            console.error("點擊建物型態選項失敗:", e);
                            
                            // 嘗試點擊父元素 (label)
                            try {
                                if (option.parentElement && option.parentElement.tagName === 'LABEL') {
                                    option.parentElement.click();
                                    console.log("點擊父元素成功");
                                    resolve(true);
                                } else {
                                    // 嘗試使用事件分發
                                    var clickEvent = new MouseEvent('click', {
                                        bubbles: true,
                                        cancelable: true,
                                        view: window
                                    });
                                    option.dispatchEvent(clickEvent);
                                    console.log("建物型態選項事件分發成功");
                                    resolve(true);
                                }
                            } catch (e2) {
                                console.error("建物型態選項備用點擊方法失敗:", e2);
                                resolve(false);
                            }
                        }
                    }, 1000);
                }, 2000); // 等待2秒確保下拉選單已顯示
            });
        """, building_type_value)
        
        if not option_selected:
            print(f"無法選擇建物型態：{building_type_value}")
            return False
        
        print(f"已選擇建物型態：{building_type_value}")
        time.sleep(5)  # 給予足夠時間讓選擇生效
        
        # 最後截圖以確認選擇結果
        try:
            screenshot_path = "examples/data/screenshots/after_building_type_selection.png"
            driver.save_screenshot(screenshot_path)
            print(f"已保存建物型態選擇後截圖：{screenshot_path}")
        except Exception as ss_err:
            print(f"保存截圖時出錯: {str(ss_err)}")
        
        return True
    except Exception as e:
        print(f"選擇建物型態時出錯: {str(e)}")
        
        # 保存出錯時的截圖
        try:
            screenshot_path = f"examples/data/screenshots/building_type_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            driver.save_screenshot(screenshot_path)
            print(f"已保存錯誤截圖：{screenshot_path}")
        except Exception as ss_err:
            print(f"保存錯誤截圖時出錯: {str(ss_err)}")
            
        return False


# ===== 數據提取區 =====

def get_total_records_count(driver: webdriver.Chrome, config: Dict) -> int:
    """獲取總記錄數"""
    try:
        list_page_config = config.get("list_page", {})
        total_count_xpath = list_page_config.get("total_count_xpath")
        
        if not total_count_xpath:
            return 0
        
        # 等待頁面加載
        time.sleep(config.get("delays", {}).get("page_load", 3))
        
        # 嘗試使用JavaScript直接查找總記錄數
        count_text = driver.execute_script("""
            var elements = document.querySelectorAll('ul.page_tab_detail li');
            for (var i = 0; i < elements.length; i++) {
                var text = elements[i].textContent;
                if (text.includes('共') && text.includes('筆')) {
                    return text;
                }
            }
            return '';
        """)
        
        if count_text:
            match = re.search(r'共\s*(\d+)\s*筆', count_text)
            if match:
                return int(match.group(1))
        
        # 如果JavaScript方法失敗，嘗試使用傳統方法
        page_source = driver.page_source
        tree = html.fromstring(page_source)
        
        # 直接查找包含"共X筆"文本的元素
        for element in tree.xpath("//li"):
            element_text = element.text_content()
            match = re.search(r'共\s*(\d+)\s*筆', element_text)
            if match:
                return int(match.group(1))
        
        # 如果找不到記錄數，嘗試計算表格行數
        try:
            rows = driver.find_elements(By.XPATH, "//tr[@class='group'][@data-sid]")
            return len(rows)
        except Exception as e:
            print(f"計算表格行數時出錯: {str(e)}")
        
        return 0
    except Exception as e:
        print(f"獲取總記錄數時出錯: {str(e)}")
        return 0


def extract_list_items(page_source: str, config: Dict) -> List[Dict]:
    """從列表頁提取數據"""
    results = []
    try:
        list_page_config = config.get("list_page", {})
        container_xpath = list_page_config.get("container_xpath")
        item_xpath = list_page_config.get("item_xpath")
        
        if not container_xpath or not item_xpath:
            return results
        
        # 解析HTML
        tree = html.fromstring(page_source)
        
        # 找到所有列表項，不使用容器限制
        items = tree.xpath(item_xpath)
        
        if not items:
            print("找不到任何列表項，嘗試直接查找")
            # 如果找不到項目，嘗試直接查找，不通過容器
            items = tree.xpath("//tr[@class='group'][@data-sid]")
        
        if not items:
            print("仍找不到列表項，返回空結果")
            return results
            
        print(f"找到 {len(items)} 個列表項")
        
        # 提取每個項目的字段
        fields_config = list_page_config.get("fields", {})
        for i, item in enumerate(items):
            item_data = {}
            for field_name, field_config in fields_config.items():
                try:
                    xpath = field_config.get("xpath")
                    field_type = field_config.get("type", "text")
                    
                    if field_type == "text":
                        elements = item.xpath(xpath)
                        # 調試
                        if field_name in ["transaction_date", "address"] and not elements:
                            print(f"字段 {field_name} 的XPath無匹配: {xpath}")
                            
                        if elements:
                            if isinstance(elements[0], str):
                                item_data[field_name] = clean_text(elements[0])
                            else:
                                item_data[field_name] = clean_text(elements[0].text_content())
                        else:
                            # 嘗試使用備用xpath
                            fallback_xpath = field_config.get("fallback_xpath")
                            if fallback_xpath:
                                elements = item.xpath(fallback_xpath)
                                if elements:
                                    if isinstance(elements[0], str):
                                        item_data[field_name] = clean_text(elements[0])
                                    else:
                                        item_data[field_name] = clean_text(elements[0].text_content())
                                else:
                                    item_data[field_name] = ""
                            else:
                                item_data[field_name] = ""
                    elif field_type == "attribute":
                        elements = item.xpath(xpath)
                        if elements:
                            item_data[field_name] = elements[0]
                        else:
                            item_data[field_name] = ""
                    elif field_type == "html":
                        elements = item.xpath(xpath)
                        if elements:
                            item_data[field_name] = html.tostring(elements[0], encoding='unicode')
                        else:
                            item_data[field_name] = ""
                except Exception as e:
                    print(f"提取字段 {field_name} 時出錯: {str(e)}")
                    item_data[field_name] = ""
            
            # 添加更多處理邏輯，例如從含車位價格中提取車位價格
            if "total_price" in item_data and item_data["total_price"]:
                try:
                    # 移除單位和非數字字符
                    price_text = re.sub(r'[^\d.]', '', item_data["total_price"])
                    if price_text:
                        item_data["total_price_value"] = float(price_text)
                except Exception as e:
                    print(f"處理總價數值時出錯: {str(e)}")
            
            # 處理含車位信息
            if "has_parking" in item_data and item_data["has_parking"]:
                try:
                    # 提取車位價格
                    match = re.search(r'含車位(\d+)萬', item_data["has_parking"])
                    if match:
                        item_data["parking_price"] = match.group(1)
                except Exception as e:
                    print(f"處理車位價格時出錯: {str(e)}")
            
            results.append(item_data)
            
            # 調試輸出第一筆資料
            if i == 0:
                print("第一筆資料內容:")
                for k, v in item_data.items():
                    print(f"  {k}: {v}")
        
        return results
    except Exception as e:
        print(f"提取列表項時出錯: {str(e)}")
        # 嘗試保存出錯的HTML以便調試
        try:
            with open("error_html.txt", "w", encoding="utf-8") as f:
                f.write(page_source[:10000])  # 保存前10000個字符
            print("已保存部分HTML到error_html.txt用於調試")
        except Exception as save_err:
            print(f"保存HTML出錯: {str(save_err)}")
        return results

def calculate_total_pages(total_records: int, items_per_page: int) -> int:
    """計算總頁數"""
    if total_records <= 0 or items_per_page <= 0:
        return 0
    return (total_records + items_per_page - 1) // items_per_page


def generate_page_url(base_url: str, page_number: int) -> str:
    """生成分頁URL"""
    if page_number <= 1:
        return base_url
    return f"{base_url}?p={page_number}"


def process_pagination(driver: webdriver.Chrome, config: Dict, base_url: str) -> List[Dict]:
    """處理分頁並提取所有頁面的數據"""
    all_results = []
    try:
        # 獲取總記錄數
        total_records = get_total_records_count(driver, config)
        print(f"總記錄數: {total_records}")
        
        # 獲取每頁項目數和最大頁數
        pagination_config = config.get("pagination", {})
        items_per_page = pagination_config.get("items_per_page", 20)
        max_pages = pagination_config.get("max_pages", 0)
        
        # 計算總頁數
        total_pages = calculate_total_pages(total_records, items_per_page)
        if max_pages > 0 and total_pages > max_pages:
            total_pages = max_pages
        
        print(f"總頁數: {total_pages}")
        
        # 處理每一頁
        for page in range(1, total_pages + 1):
            print(f"正在處理第 {page}/{total_pages} 頁")
            
            # 如果不是第一頁，則導航到該頁
            if page > 1:
                page_url = generate_page_url(base_url, page)
                driver.get(page_url)
                time.sleep(config.get("delays", {}).get("page_load", 3))
            
            # 提取當前頁的數據
            page_source = driver.page_source
            page_results = extract_list_items(page_source, config)
            
            # 添加到結果中
            all_results.extend(page_results)
            print(f"第 {page} 頁提取了 {len(page_results)} 條記錄")
            
            # 頁面間延遲
            if page < total_pages:
                time.sleep(config.get("delays", {}).get("between_pages", 2))
        
        return all_results
    except Exception as e:
        print(f"處理分頁時出錯: {str(e)}")
        return all_results


def extract_detail_page(driver: webdriver.Chrome, url: str, config: Dict) -> Dict[str, Any]:
    """提取詳情頁數據"""
    detail_data = {}
    try:
        # 導航到詳情頁
        driver.get(url)
        time.sleep(config.get("delays", {}).get("page_load", 3))
        
        # 獲取頁面源碼
        page_source = driver.page_source
        tree = html.fromstring(page_source)
        
        # 提取詳情頁字段
        detail_page_config = config.get("detail_page", {})
        container_xpath = detail_page_config.get("container_xpath")
        fields_config = detail_page_config.get("fields", {})
        
        # 找到容器
        container = tree.xpath(container_xpath)
        if not container:
            print(f"找不到詳情頁容器: {container_xpath}")
            # 嘗試保存當前頁面源碼用於調試
            try:
                with open(f"examples/data/screenshots/detail_page_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html", "w", encoding="utf-8") as f:
                    f.write(page_source)
                print("已保存詳情頁HTML用於調試")
            except Exception as save_err:
                print(f"保存詳情頁HTML出錯: {str(save_err)}")
            return detail_data
        
        # 提取每個字段
        for field_name, field_config in fields_config.items():
            try:
                xpath = field_config.get("xpath")
                field_type = field_config.get("type", "text")
                
                if field_type == "text":
                    elements = container[0].xpath(xpath)
                    if elements:
                        if isinstance(elements[0], str):
                            detail_data[field_name] = clean_text(elements[0])
                        else:
                            detail_data[field_name] = clean_text(elements[0].text_content())
                    else:
                        detail_data[field_name] = ""
                elif field_type == "html":
                    elements = container[0].xpath(xpath)
                    if elements:
                        detail_data[field_name] = html.tostring(elements[0], encoding='unicode')
                    else:
                        detail_data[field_name] = ""
                elif field_type == "attribute":
                    elements = container[0].xpath(xpath)
                    if elements:
                        detail_data[field_name] = elements[0]
                    else:
                        detail_data[field_name] = ""
            except Exception as e:
                print(f"提取詳情頁字段 {field_name} 時出錯: {str(e)}")
                detail_data[field_name] = ""
        
        # 調試輸出
        print("詳情頁數據:")
        for k, v in detail_data.items():
            print(f"  {k}: {v}")
        
        return detail_data
    except Exception as e:
        print(f"提取詳情頁時出錯: {str(e)}")
        return detail_data


def process_detail_pages(driver: webdriver.Chrome, list_results: List[Dict], config: Dict) -> List[Dict]:
    """處理所有詳情頁"""
    detailed_results = []
    try:
        detail_page_config = config.get("detail_page", {})
        url_pattern = detail_page_config.get("url_pattern", "")
        
        for i, item in enumerate(list_results):
            try:
                # 構建詳情頁URL
                detail_id = item.get("detail_link", "")
                if not detail_id:
                    print(f"項目 {i+1} 缺少詳情頁ID，跳過")
                    detailed_results.append(item)
                    continue
                
                detail_url = url_pattern.format(sid=detail_id)
                
                # 提取詳情頁數據
                print(f"正在提取詳情頁 {i+1}/{len(list_results)}: {detail_url}")
                detail_data = extract_detail_page(driver, detail_url, config)
                
                # 合併列表頁和詳情頁數據
                item.update(detail_data)
                detailed_results.append(item)
                
                # 項目間延遲
                if i < len(list_results) - 1:
                    time.sleep(config.get("delays", {}).get("between_items", 0.5))
            except Exception as e:
                print(f"處理詳情頁 {i+1} 時出錯: {str(e)}")
                detailed_results.append(item)
        
        return detailed_results
    except Exception as e:
        print(f"處理詳情頁時出錯: {str(e)}")
        return list_results


def save_results(results: List[Dict], config: Dict) -> Optional[str]:
    """保存結果到文件"""
    try:
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"price_house_{timestamp}.json"
        
        # 確保輸出目錄存在
        output_dir = "examples/data/output"
        os.makedirs(output_dir, exist_ok=True)
        
        # 保存到文件
        output_path = os.path.join(output_dir, filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(format_for_json(results), f, ensure_ascii=False, indent=2)
        
        print(f"結果已保存到: {output_path}")
        return output_path
    except Exception as e:
        print(f"保存結果時出錯: {str(e)}")
        return None


def handle_error(driver: webdriver.Chrome, config: Dict, error: Exception) -> None:
    """處理錯誤"""
    try:
        # 保存錯誤頁面
        advanced_settings = config.get("advanced_settings", {})
        if advanced_settings.get("save_error_page", False):
            error_dir = advanced_settings.get("error_page_dir", "debug")
            os.makedirs(error_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            error_filename = f"error_page_{timestamp}.html"
            error_path = os.path.join(error_dir, error_filename)
            
            with open(error_path, 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            
            print(f"錯誤頁面已保存到: {error_path}")
    except Exception as e:
        print(f"處理錯誤時出錯: {str(e)}")


def build_search_url(config: Dict) -> str:
    """構建搜尋URL"""
    try:
        # 直接返回基本 URL
        return config.get("base_url", "")
    except Exception as e:
        print(f"構建搜尋URL時出錯: {str(e)}")
        return config.get("base_url", "")


def main() -> None:
    """主函數"""
    driver = None
    try:
        # 載入配置
        config_path = "examples/config/price_house/basic/query.json"
        config = load_config(config_path)
        
        # 設置WebDriver
        driver = setup_webdriver(config)
        
        # 構建搜尋URL
        search_url = build_search_url(config)
        print(f"搜尋URL: {search_url}")
        
        # 導航到搜尋頁面
        driver.get(search_url)
        time.sleep(config.get("delays", {}).get("page_load", 3))
        
        # 設置搜尋參數
        if not set_search_parameters(driver, config):
            print("設置搜尋參數失敗")
            return
        
        # 處理分頁並提取列表數據
        list_results = process_pagination(driver, config, driver.current_url)
        print(f"共提取 {len(list_results)} 條列表數據")
        
        # 處理詳情頁
        detailed_results = process_detail_pages(driver, list_results, config)
        print(f"共提取 {len(detailed_results)} 條詳細數據")
        
        # 保存結果
        save_results(detailed_results, config)
        
    except Exception as e:
        print(f"執行過程中出錯: {str(e)}")
        if driver:
            handle_error(driver, config, e)
    finally:
        # 關閉瀏覽器
        if driver:
            driver.quit()
            print("瀏覽器已關閉")


if __name__ == "__main__":
    main()
