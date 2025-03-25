#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import time
import random
import logging
import platform
from typing import Dict, List, Optional, Any, Union

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from ..core.webdriver_manager import WebDriverManager
from ..utils.logger import setup_logger
from ..utils.error_handler import retry_on_exception, handle_exception


class AntiDetectionManager:
    """
    反爬蟲管理器，提供全面的反爬蟲策略，
    檢測和應對各種反爬機制，包括WebDriver特徵隱藏、
    行為模擬、代理切換等。
    """
    
    def __init__(self, config: Dict = None, log_level: int = logging.INFO):
        """
        初始化反爬蟲管理器
        
        Args:
            config: 配置字典
            log_level: 日誌級別
        """
        self.logger = setup_logger(__name__, log_level)
        self.logger.info("初始化反爬蟲管理器")
        
        self.config = config or {}
        
        # WebDriver管理器
        self.webdriver_manager = WebDriverManager(
            config=self.config.get("webdriver_config", {}),
            log_level=log_level
        )
        
        # 默認延遲設置
        self.delays = self.config.get("delays", {
            "page_load": {"min": 2, "max": 5},
            "between_actions": {"min": 1, "max": 3},
            "before_click": {"min": 0.5, "max": 2},
            "typing_speed": {"min": 0.05, "max": 0.2}
        })
        
        # 代理設置
        self.proxies = self.config.get("proxies", [])
        self.proxy_index = 0
        
        # 用戶代理設置
        self.user_agents = self.config.get("user_agents", [])
        
        # 檢測計數器
        self.detection_count = 0
        self.max_retries = self.config.get("max_retries", 3)
        
        # 載入隱身腳本
        self.stealth_scripts = {}
        self._load_stealth_scripts()
        
        self.logger.info("反爬蟲管理器初始化完成")
    
    def _load_stealth_scripts(self):
        """載入隱身腳本"""
        script_dir = os.path.join(os.path.dirname(__file__), "stealth_scripts")
        
        if not os.path.exists(script_dir):
            self.logger.warning(f"隱身腳本目錄不存在: {script_dir}")
            return
        
        for script_file in os.listdir(script_dir):
            if script_file.endswith(".js"):
                script_path = os.path.join(script_dir, script_file)
                script_name = script_file.replace(".js", "")
                
                try:
                    with open(script_path, "r", encoding="utf-8") as f:
                        script_content = f.read()
                    
                    self.stealth_scripts[script_name] = script_content
                    self.logger.debug(f"已載入隱身腳本: {script_name}")
                except Exception as e:
                    self.logger.error(f"載入隱身腳本 {script_name} 失敗: {str(e)}")
    
    def create_webdriver(self, headless: bool = True) -> webdriver.Remote:
        """
        創建反爬蟲配置的WebDriver
        
        Args:
            headless: 是否使用無頭模式
            
        Returns:
            配置好的WebDriver實例
        """
        # 更新配置
        webdriver_config = self.config.get("webdriver_config", {}).copy()
        webdriver_config["headless"] = headless
        
        # 設置代理
        if self.proxies and self.config.get("use_proxy", False):
            proxy = self._get_next_proxy()
            if proxy:
                webdriver_config["proxy"] = proxy
        
        # 設置用戶代理
        if self.user_agents and self.config.get("randomize_user_agent", True):
            user_agent = self._get_random_user_agent()
            if user_agent:
                webdriver_config["user_agent"] = user_agent
        
        # 創建WebDriver
        self.webdriver_manager = WebDriverManager(
            config=webdriver_config,
            log_level=self.logger.level
        )
        
        # 獲取WebDriver實例
        driver = self.webdriver_manager.create_driver()
        
        # 應用隱身腳本
        self._apply_stealth_scripts(driver)
        
        # 配置WebDriver
        self._configure_driver(driver)
        
        return driver
    
    def _configure_driver(self, driver: webdriver.Remote):
        """配置WebDriver的額外設置"""
        # 設置頁面加載超時
        driver.set_page_load_timeout(self.config.get("page_load_timeout", 30))
        
        # 設置腳本超時
        driver.set_script_timeout(self.config.get("script_timeout", 30))
        
        # 設置窗口大小
        window_size = self.config.get("window_size", {"width": 1920, "height": 1080})
        driver.set_window_size(window_size["width"], window_size["height"])
    
    def _apply_stealth_scripts(self, driver: webdriver.Remote):
        """應用隱身腳本"""
        if not self.stealth_scripts:
            self.logger.warning("沒有可用的隱身腳本")
            return
        
        for script_name, script_content in self.stealth_scripts.items():
            try:
                driver.execute_script(script_content)
                self.logger.debug(f"已應用隱身腳本: {script_name}")
            except Exception as e:
                self.logger.error(f"應用隱身腳本 {script_name} 失敗: {str(e)}")
    
    def _get_next_proxy(self) -> Union[str, Dict, None]:
        """獲取下一個代理"""
        if not self.proxies:
            return None
        
        proxy = self.proxies[self.proxy_index]
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        
        return proxy
    
    def _get_random_user_agent(self) -> Optional[str]:
        """獲取隨機用戶代理"""
        if not self.user_agents:
            return None
        
        return random.choice(self.user_agents)
    
    def random_delay(self, delay_type: str = "between_actions"):
        """
        根據配置的延遲範圍，生成隨機延遲時間並等待
        
        Args:
            delay_type: 延遲類型，可選值：page_load, between_actions, before_click, typing_speed
        """
        delay_config = self.delays.get(delay_type, {"min": 1, "max": 3})
        min_delay = delay_config.get("min", 1)
        max_delay = delay_config.get("max", 3)
        
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    def simulate_human_typing(self, element, text: str, focus_first: bool = True):
        """
        模擬人類輸入文字
        
        Args:
            element: 要輸入的元素
            text: 要輸入的文字
            focus_first: 是否先聚焦元素
        """
        try:
            if focus_first:
                element.click()
            
            # 清除現有內容
            element.clear()
            
            typing_speed = self.delays.get("typing_speed", {"min": 0.05, "max": 0.2})
            min_speed = typing_speed.get("min", 0.05)
            max_speed = typing_speed.get("max", 0.2)
            
            # 逐字輸入
            for char in text:
                element.send_keys(char)
                delay = random.uniform(min_speed, max_speed)
                time.sleep(delay)
            
            # 輸入完成後的延遲
            self.random_delay("before_click")
        
        except Exception as e:
            self.logger.error(f"模擬人類輸入失敗: {str(e)}")
    
    def simulate_human_scroll(self, driver: webdriver.Remote, scroll_amount: int = None, direction: str = "down"):
        """
        模擬人類滾動頁面
        
        Args:
            driver: WebDriver實例
            scroll_amount: 滾動量，為None時隨機滾動
            direction: 滾動方向，可選值：up, down
        """
        try:
            # 如果未指定滾動量，生成隨機值
            if scroll_amount is None:
                scroll_amount = random.randint(100, 800)
            
            # 根據方向調整滾動量
            if direction.lower() == "up":
                scroll_amount = -scroll_amount
            
            # 使用JavaScript滾動
            script = f"window.scrollBy(0, {scroll_amount});"
            driver.execute_script(script)
            
            # 滾動後的延遲
            self.random_delay("between_actions")
        
        except Exception as e:
            self.logger.error(f"模擬人類滾動失敗: {str(e)}")
    
    def simulate_human_mouse_movement(self, driver: webdriver.Remote, target_element=None):
        """
        模擬人類鼠標移動
        
        Args:
            driver: WebDriver實例
            target_element: 目標元素，為None時隨機移動
        """
        try:
            # 導入ActionChains
            from selenium.webdriver import ActionChains
            
            actions = ActionChains(driver)
            
            if target_element:
                # 移動到目標元素
                actions.move_to_element(target_element)
            else:
                # 隨機移動
                x = random.randint(100, 700)
                y = random.randint(100, 500)
                actions.move_by_offset(x, y)
            
            actions.perform()
            
            # 移動後的延遲
            self.random_delay("between_actions")
        
        except Exception as e:
            self.logger.error(f"模擬人類鼠標移動失敗: {str(e)}")
    
    def detected_anti_crawling(self, driver: webdriver.Remote) -> bool:
        """
        檢測是否被反爬機制識別
        
        Args:
            driver: WebDriver實例
            
        Returns:
            是否被識別
        """
        # 檢測點一：檢查頁面是否包含常見的反爬文本
        anti_crawl_texts = [
            "驗證碼", "captcha", "禁止訪問", "access denied",
            "異常訪問", "unusual traffic", "人機驗證", "robot",
            "拒絕訪問", "請求頻率過高", "請稍後再試", "temporarily blocked",
            "安全檢查", "security check", "滑動驗證", "點擊驗證"
        ]
        
        try:
            page_source = driver.page_source.lower()
            
            for text in anti_crawl_texts:
                if text.lower() in page_source:
                    self.logger.warning(f"檢測到反爬機制: 頁面包含 '{text}'")
                    return True
            
            # 檢測點二：檢查是否有驗證碼元素
            captcha_selectors = [
                "//iframe[contains(@src, 'captcha')]",
                "//iframe[contains(@src, 'recaptcha')]",
                "//div[contains(@class, 'captcha')]",
                "//div[contains(@class, 'recaptcha')]",
                "//div[contains(@id, 'captcha')]",
                "//div[contains(@id, 'recaptcha')]",
                "//img[contains(@src, 'captcha')]",
                "//input[contains(@placeholder, 'captcha')]",
                "//input[contains(@id, 'captcha')]",
                "//div[contains(@class, 'slider')]//div[contains(@class, 'handle')]"
            ]
            
            for selector in captcha_selectors:
                elements = driver.find_elements(By.XPATH, selector)
                if elements:
                    self.logger.warning(f"檢測到反爬機制: 存在驗證碼元素 '{selector}'")
                    return True
            
            # 檢測點三：檢查頁面標題或URL是否包含錯誤提示
            error_indicators = [
                "error", "denied", "blocked", "unauthorized",
                "forbidden", "429", "too many requests", "retry"
            ]
            
            page_title = driver.title.lower()
            current_url = driver.current_url.lower()
            
            for indicator in error_indicators:
                if indicator in page_title or indicator in current_url:
                    self.logger.warning(f"檢測到反爬機制: 頁面標題或URL包含 '{indicator}'")
                    return True
            
            # 檢測點四：使用JavaScript檢測是否存在WebDriver
            webdriver_detection_script = """
            return (navigator.webdriver !== undefined && navigator.webdriver === true) ||
                   (window.callPhantom !== undefined) ||
                   (window._phantom !== undefined) ||
                   (window.__nightmare !== undefined) ||
                   (window.Buffer !== undefined);
            """
            
            try:
                is_detected = driver.execute_script(webdriver_detection_script)
                if is_detected:
                    self.logger.warning("檢測到反爬機制: JavaScript檢測到WebDriver特徵")
                    return True
            except Exception as js_error:
                self.logger.debug(f"執行JavaScript檢測失敗: {str(js_error)}")
            
            # 未檢測到反爬機制
            return False
        
        except Exception as e:
            self.logger.error(f"檢測反爬機制失敗: {str(e)}")
            # 為了安全起見，假設可能被檢測到
            return True
    
    def handle_detection(self, driver: webdriver.Remote) -> bool:
        """
        處理被反爬機制識別的情況
        
        Args:
            driver: WebDriver實例
            
        Returns:
            是否成功處理
        """
        # 增加檢測計數
        self.detection_count += 1
        
        # 檢查是否超過最大重試次數
        if self.detection_count > self.max_retries:
            self.logger.error(f"已達到最大重試次數 {self.max_retries}，放棄處理")
            return False
        
        self.logger.info(f"嘗試處理反爬機制檢測，第 {self.detection_count}/{self.max_retries} 次")
        
        # 策略一：更換代理
        if self.config.get("change_proxy_on_detection", True) and self.proxies:
            try:
                proxy = self._get_next_proxy()
                if proxy:
                    self.logger.info(f"更換代理: {proxy}")
                    # 由於WebDriver不支持運行時更換代理，需要重新創建
                    return False  # 返回False以觸發上層重新創建WebDriver
            except Exception as e:
                self.logger.error(f"更換代理失敗: {str(e)}")
        
        # 策略二：更換用戶代理
        if self.config.get("change_user_agent_on_detection", True) and self.user_agents:
            try:
                user_agent = self._get_random_user_agent()
                if user_agent:
                    self.logger.info(f"更換用戶代理: {user_agent}")
                    self.webdriver_manager.change_user_agent(user_agent)
            except Exception as e:
                self.logger.error(f"更換用戶代理失敗: {str(e)}")
        
        # 策略三：清除Cookie
        if self.config.get("clear_cookies_on_detection", True):
            try:
                self.logger.info("清除Cookie")
                driver.delete_all_cookies()
            except Exception as e:
                self.logger.error(f"清除Cookie失敗: {str(e)}")
        
        # 策略四：重新應用隱身腳本
        try:
            self.logger.info("重新應用隱身腳本")
            self._apply_stealth_scripts(driver)
        except Exception as e:
            self.logger.error(f"重新應用隱身腳本失敗: {str(e)}")
        
        # 策略五：模擬人類行為
        try:
            self.logger.info("模擬人類行為")
            self.simulate_human_scroll(driver)
            self.random_delay("between_actions")
            self.simulate_human_mouse_movement(driver)
        except Exception as e:
            self.logger.error(f"模擬人類行為失敗: {str(e)}")
        
        # 策略六：等待較長時間
        cooldown_time = self.config.get("detection_cooldown", 30)
        self.logger.info(f"等待冷卻時間: {cooldown_time} 秒")
        time.sleep(cooldown_time)
        
        # 刷新頁面
        try:
            self.logger.info("刷新頁面")
            driver.refresh()
            
            # 等待頁面加載
            self.random_delay("page_load")
        except Exception as e:
            self.logger.error(f"刷新頁面失敗: {str(e)}")
        
        # 再次檢測是否被識別
        if not self.detected_anti_crawling(driver):
            self.logger.info("成功處理反爬機制")
            self.detection_count = 0  # 重置計數器
            return True
        else:
            self.logger.warning("處理反爬機制失敗，仍被識別")
            return False
    
    def modify_browser_fingerprint(self, driver: webdriver.Remote):
        """
        修改瀏覽器指紋特徵
        
        Args:
            driver: WebDriver實例
        """
        try:
            # 修改瀏覽器指紋的JavaScript代碼
            fingerprint_script = """
            // 修改navigator屬性
            Object.defineProperty(navigator, 'webdriver', {
                get: () => false,
            });
            
            // 修改plugins
            Object.defineProperty(navigator, 'plugins', {
                get: () => {
                    // 創建虛擬插件
                    const plugins = [];
                    for (let i = 0; i < 3; i++) {
                        plugins.push({
                            name: `Plugin ${i}`,
                            description: `Fake plugin ${i}`,
                            filename: `plugin${i}.dll`,
                            length: 1
                        });
                    }
                    return plugins;
                }
            });
            
            // 修改語言
            Object.defineProperty(navigator, 'languages', {
                get: () => ['zh-TW', 'zh', 'en-US', 'en'],
            });
            
            // 修改硬件信息
            Object.defineProperty(navigator, 'hardwareConcurrency', {
                get: () => 8,
            });
            
            Object.defineProperty(navigator, 'deviceMemory', {
                get: () => 8,
            });
            
            // 修改WebGL
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                // 修改一些特定的參數
                if (parameter === 37445) {
                    return 'Intel Inc.';
                }
                if (parameter === 37446) {
                    return 'Intel(R) Iris(TM) Graphics 6100';
                }
                return getParameter.apply(this, arguments);
            };
            
            // 修改Canvas行為
            const originalGetContext = HTMLCanvasElement.prototype.getContext;
            HTMLCanvasElement.prototype.getContext = function() {
                const context = originalGetContext.apply(this, arguments);
                if (context && arguments[0] === '2d') {
                    // 修改填充矩形方法，使結果略微不同
                    const originalFillRect = context.fillRect;
                    context.fillRect = function() {
                        arguments[0] += Math.random() * 0.01;
                        arguments[1] += Math.random() * 0.01;
                        return originalFillRect.apply(this, arguments);
                    };
                }
                return context;
            };
            
            // 修改屏幕信息
            Object.defineProperty(screen, 'width', {
                get: () => 1920,
            });
            
            Object.defineProperty(screen, 'height', {
                get: () => 1080,
            });
            
            Object.defineProperty(screen, 'colorDepth', {
                get: () => 24,
            });
            
            // 移除檢測特徵
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
            """
            
            driver.execute_script(fingerprint_script)
            self.logger.info("成功修改瀏覽器指紋特徵")
        
        except Exception as e:
            self.logger.error(f"修改瀏覽器指紋特徵失敗: {str(e)}")
    
    def enable_stealth_mode(self, driver: webdriver.Remote):
        """
        啟用隱身模式，綜合應用多種反檢測技術
        
        Args:
            driver: WebDriver實例
        """
        # 應用隱身腳本
        self._apply_stealth_scripts(driver)
        
        # 修改瀏覽器指紋
        self.modify_browser_fingerprint(driver)
        
        # 添加額外的隱身措施
        try:
            # 偽造鼠標軌跡
            self._fake_mouse_movements(driver)
            
            # 偽造鍵盤事件
            self._fake_keyboard_events(driver)
            
            # 修改WebRTC行為
            self._modify_webrtc_behavior(driver)
            
            self.logger.info("成功啟用隱身模式")
        
        except Exception as e:
            self.logger.error(f"啟用隱身模式失敗: {str(e)}")
    
    def _fake_mouse_movements(self, driver: webdriver.Remote):
        """生成假的鼠標移動軌跡"""
        script = """
        // 創建模擬鼠標軌跡
        const events = [];
        const viewportWidth = window.innerWidth;
        const viewportHeight = window.innerHeight;
        
        // 生成隨機點
        let x = 100, y = 100;
        for (let i = 0; i < 20; i++) {
            x += Math.floor(Math.random() * 20) - 10;
            y += Math.floor(Math.random() * 20) - 10;
            
            // 確保在可視區域內
            x = Math.max(0, Math.min(x, viewportWidth));
            y = Math.max(0, Math.min(y, viewportHeight));
            
            events.push({
                type: 'mousemove',
                x: x,
                y: y,
                timestamp: Date.now() + i * 100
            });
        }
        
        // 存儲到window對象中，以備檢測時使用
        window._mouseTrack = events;
        """
        driver.execute_script(script)
    
    def _fake_keyboard_events(self, driver: webdriver.Remote):
        """生成假的鍵盤事件"""
        script = """
        // 創建模擬鍵盤事件
        const keyEvents = [];
        const keys = ['a', 'b', 'c', 'd', 'e'];
        
        for (let i = 0; i < 10; i++) {
            const key = keys[Math.floor(Math.random() * keys.length)];
            keyEvents.push({
                type: 'keydown',
                key: key,
                timestamp: Date.now() + i * 200
            });
            
            keyEvents.push({
                type: 'keyup',
                key: key,
                timestamp: Date.now() + i * 200 + 100
            });
        }
        
        // 存儲到window對象中，以備檢測時使用
        window._keyboardTrack = keyEvents;
        """
        driver.execute_script(script)
    
    def _modify_webrtc_behavior(self, driver: webdriver.Remote):
        """修改WebRTC行為，防止IP洩露"""
        script = """
        // 修改WebRTC行為
        if (navigator.mediaDevices && navigator.mediaDevices.enumerateDevices) {
            const originalEnumerateDevices = navigator.mediaDevices.enumerateDevices;
            navigator.mediaDevices.enumerateDevices = function() {
                return originalEnumerateDevices.apply(this, arguments)
                    .then(devices => {
                        // 返回空設備列表或修改的設備列表
                        return [];
                    });
            };
        }
        
        // 修改RTCPeerConnection，防止IP洩露
        if (window.RTCPeerConnection) {
            const originalRTCPeerConnection = window.RTCPeerConnection;
            window.RTCPeerConnection = function() {
                // 禁止創建連接或返回修改後的連接
                return null;
            };
        }
        """
        driver.execute_script(script)
    
    def detect_honeypots(self, driver: webdriver.Remote) -> bool:
        """
        檢測頁面中的蜜罐和陷阱
        
        Args:
            driver: WebDriver實例
            
        Returns:
            是否檢測到蜜罐
        """
        try:
            # 檢測隱藏元素陷阱
            honeypot_script = """
            // 檢測隱藏元素陷阱
            const honeypots = [];
            
            // 查找隱藏元素
            const elements = document.querySelectorAll('*');
            for (const element of elements) {
                const style = window.getComputedStyle(element);
                
                // 檢查是否為隱藏元素但可點擊
                if ((style.display === 'none' || style.visibility === 'hidden' || 
                     style.opacity === '0' || 
                     (element.getBoundingClientRect().width === 0 && element.getBoundingClientRect().height === 0)) &&
                    (element.tagName === 'A' || element.tagName === 'BUTTON' || 
                     element.onclick || element.getAttribute('role') === 'button')) {
                    honeypots.push({
                        tag: element.tagName,
                        id: element.id,
                        class: element.className,
                        type: 'hidden_clickable'
                    });
                }
                
                // 檢查不可見但可填寫的輸入框
                if ((style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') &&
                    (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA')) {
                    honeypots.push({
                        tag: element.tagName,
                        id: element.id,
                        class: element.className,
                        type: 'hidden_input'
                    });
                }
            }
            
            return honeypots;
            """
            
            honeypots = driver.execute_script(honeypot_script)
            
            if honeypots:
                self.logger.warning(f"檢測到 {len(honeypots)} 個蜜罐元素")
                for honeypot in honeypots[:5]:  # 僅顯示前5個
                    self.logger.debug(f"蜜罐元素: {honeypot}")
                return True
            
            # 檢測行為監控腳本
            monitoring_script = """
            // 檢測行為監控腳本
            const monitoringScripts = [];
            
            // 檢查是否有監聽全局鼠標和鍵盤事件
            if (window.__originalAddEventListener) {
                monitoringScripts.push({ type: 'event_listener_override', detail: 'addEventListener has been overridden' });
            }
            
            // 檢查是否有常見的反爬工具
            for (const key of Object.keys(window)) {
                if (key.includes('captcha') || key.includes('monitor') || key.includes('track') || 
                    key.includes('detect') || key.includes('spider') || key.includes('bot')) {
                    monitoringScripts.push({ type: 'suspicious_global', name: key });
                }
            }
            
            return monitoringScripts;
            """
            
            monitoring_results = driver.execute_script(monitoring_script)
            
            if monitoring_results:
                self.logger.warning(f"檢測到 {len(monitoring_results)} 個監控腳本")
                for script in monitoring_results[:5]:  # 僅顯示前5個
                    self.logger.debug(f"監控腳本: {script}")
                return True
            
            return False
        
        except Exception as e:
            self.logger.error(f"檢測蜜罐失敗: {str(e)}")
            return False