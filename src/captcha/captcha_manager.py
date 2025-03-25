# 如果是Base64圖片
                if img_url.startswith('data:image'):
                    base64_data = img_url.split(',')[1]
                    return {'image_base64': base64_data}
                else:
                    return {'image_url': img_url}
            
            elif captcha_type == "slider":
                # 獲取滑塊元素和背景圖片
                slider_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'slider')]")
                if not slider_elements:
                    return {}
                
                # 嘗試獲取背景圖片
                background_img = driver.find_element(By.XPATH, "//div[contains(@class, 'slider')]/img")
                bg_url = background_img.get_attribute("src")
                
                return {
                    'slider_element': slider_elements[0],
                    'background_url': bg_url
                }
            
            elif captcha_type == "click":
                # 獲取點擊驗證碼圖片
                img_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'imgCaptcha')]/img")
                if not img_elements:
                    return {}
                
                img_element = img_elements[0]
                img_url = img_element.get_attribute("src")
                
                # 獲取提示文本
                hint_elements = driver.find_elements(By.XPATH, "//div[contains(text(), '點擊圖片中的')]")
                hint_text = hint_elements[0].text if hint_elements else ""
                
                return {
                    'image_url': img_url,
                    'hint_text': hint_text
                }
            
            elif captcha_type == "recaptcha":
                # 獲取ReCAPTCHA元素
                recaptcha_elements = driver.find_elements(By.XPATH, "//div[@class='g-recaptcha']")
                if not recaptcha_elements:
                    return {}
                
                # 獲取site-key
                site_key = recaptcha_elements[0].get_attribute("data-sitekey")
                page_url = driver.current_url
                
                return {
                    'site_key': site_key,
                    'page_url': page_url
                }
            
            return {}
        
        except Exception as e:
            self.logger.error(f"保存驗證碼樣本失敗: {str(e)}")
    
    def handle_simple_text_captcha(self, driver: webdriver.Remote) -> bool:
        """
        處理簡單的文本驗證碼（無需第三方服務）
        
        Args:
            driver: WebDriver實例
            
        Returns:
            是否成功處理
        """
        try:
            # 查找驗證碼圖片
            img_elements = driver.find_elements(By.XPATH, "//img[contains(@src, 'captcha')]")
            if not img_elements:
                return False
            
            img_element = img_elements[0]
            
            # 查找驗證碼輸入框
            input_elements = driver.find_elements(By.XPATH, "//input[contains(@placeholder, '驗證碼')]")
            if not input_elements:
                return False
            
            input_element = input_elements[0]
            
            # 提示用戶手動輸入
            self.logger.info("請在控制台手動輸入驗證碼")
            print("\n=== 請查看瀏覽器中的驗證碼圖片 ===")
            captcha_text = input("請輸入驗證碼: ")
            
            # 填入驗證碼
            input_element.clear()
            input_element.send_keys(captcha_text)
            
            # 查找提交按鈕
            submit_buttons = driver.find_elements(By.XPATH, "//button[contains(@type, 'submit')]")
            if submit_buttons:
                submit_buttons[0].click()
            
            time.sleep(2)
            return True
        
        except Exception as e:
            self.logger.error(f"處理簡單文本驗證碼失敗: {str(e)}")
            return False
    
    def handle_simple_slider_captcha(self, driver: webdriver.Remote) -> bool:
        """
        處理簡單的滑塊驗證碼（無需第三方服務）
        
        Args:
            driver: WebDriver實例
            
        Returns:
            是否成功處理
        """
        try:
            # 查找滑塊元素
            slider_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'slider')]//div[contains(@class, 'handle')]")
            if not slider_elements:
                return False
            
            slider_element = slider_elements[0]
            
            # 創建動作鏈
            actions = ActionChains(driver)
            
            # 移動到滑塊
            actions.move_to_element(slider_element)
            actions.click_and_hold()
            actions.pause(0.5)  # 暫停一下，模擬人類行為
            
            # 隨機移動距離
            # 注意：實際情況下，應該使用計算機視覺算法來確定正確的移動距離
            # 這裡只是一個簡單的示例
            move_distance = random.randint(100, 200)
            
            # 分段移動，更像人類操作
            steps = 10
            step_distance = move_distance / steps
            
            for i in range(steps):
                actions.move_by_offset(step_distance, 0)
                actions.pause(0.05)  # 每一步稍微暫停
            
            # 鬆開滑塊
            actions.release()
            actions.perform()
            
            # 等待驗證結果
            time.sleep(3)
            
            # 檢查驗證結果
            # 需要根據實際情況確定驗證成功的標誌
            success_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'success')]")
            if success_elements:
                self.logger.info("滑塊驗證成功")
                return True
            else:
                self.logger.warning("滑塊驗證失敗")
                return False
        
        except Exception as e:
            self.logger.error(f"處理簡單滑塊驗證碼失敗: {str(e)}")
            return False
    
    def refresh_captcha(self, driver: webdriver.Remote) -> bool:
        """
        刷新驗證碼
        
        Args:
            driver: WebDriver實例
            
        Returns:
            是否成功刷新
        """
        try:
            # 查找刷新按鈕或鏈接
            refresh_elements = driver.find_elements(By.XPATH, 
                "//a[contains(@class, 'captcha-refresh')] | "
                "//img[contains(@class, 'captcha-refresh')] | "
                "//a[contains(text(), '刷新')] | "
                "//span[contains(text(), '刷新')]")
            
            if refresh_elements:
                refresh_elements[0].click()
                time.sleep(1)
                return True
            
            # 如果沒有找到刷新按鈕，嘗試點擊驗證碼圖片本身
            img_elements = driver.find_elements(By.XPATH, "//img[contains(@src, 'captcha')]")
            if img_elements:
                img_elements[0].click()
                time.sleep(1)
                return True
            
            return False
        
        except Exception as e:
            self.logger.error(f"刷新驗證碼失敗: {str(e)}")
            return False
    
    def is_captcha_solved(self, driver: webdriver.Remote) -> bool:
        """
        檢查驗證碼是否已解決
        
        Args:
            driver: WebDriver實例
            
        Returns:
            是否已解決
        """
        # 重新檢測是否仍存在驗證碼
        detected, _ = self.detect_captcha(driver)
        return not detected
    
    def train_model(self, captcha_type: str, sample_dir: str = None):
        """
        訓練驗證碼識別模型（佔位函數，實際實現需要機器學習知識）
        
        Args:
            captcha_type: 驗證碼類型
            sample_dir: 樣本目錄
        """
        if sample_dir is None:
            sample_dir = os.path.join(self.sample_dir, captcha_type)
        
        self.logger.info(f"訓練 {captcha_type} 驗證碼識別模型")
        
        # 檢查樣本目錄是否存在
        if not os.path.exists(sample_dir):
            self.logger.warning(f"樣本目錄不存在: {sample_dir}")
            return
        
        # 查找樣本文件
        sample_files = [f for f in os.listdir(sample_dir) if f.endswith('.png')]
        
        if not sample_files:
            self.logger.warning(f"樣本目錄中沒有找到樣本: {sample_dir}")
            return
        
        self.logger.info(f"找到 {len(sample_files)} 個樣本")
        
        # 訓練模型的實際邏輯應該在這裡實現
        # 這需要使用機器學習庫，如TensorFlow或PyTorch
        
        self.logger.info("訓練模型功能尚未實現，請使用外部工具訓練模型")

            self.logger.error(f"獲取驗證碼數據失敗: {str(e)}")
            return {}
    
    def _solve_with_2captcha(self, api_url: str, api_key: str, captcha_type: str, captcha_data: Dict, driver: webdriver.Remote) -> bool:
        """
        使用2Captcha服務解決驗證碼
        
        Args:
            api_url: API URL
            api_key: API密鑰
            captcha_type: 驗證碼類型
            captcha_data: 驗證碼數據
            driver: WebDriver實例
            
        Returns:
            是否成功解決
        """
        try:
            import requests
            
            if captcha_type == "text":
                # 提交圖片驗證碼
                if 'image_base64' in captcha_data:
                    params = {
                        'key': api_key,
                        'method': 'base64',
                        'body': captcha_data['image_base64'],
                        'json': 1
                    }
                elif 'image_url' in captcha_data:
                    params = {
                        'key': api_key,
                        'method': 'userrecaptcha',
                        'googlekey': captcha_data['site_key'],
                        'pageurl': captcha_data['page_url'],
                        'json': 1
                    }
                else:
                    return False
                
                # 提交請求
                response = requests.post(f"{api_url}/in.php", params=params)
                response_data = response.json()
                
                if response_data['status'] != 1:
                    self.logger.error(f"2Captcha提交失敗: {response_data['request']}")
                    return False
                
                # 獲取請求ID
                request_id = response_data['request']
                
                # 等待結果
                for _ in range(30):  # 最多等待30次，每次5秒
                    time.sleep(5)
                    
                    # 查詢結果
                    result_params = {
                        'key': api_key,
                        'action': 'get',
                        'id': request_id,
                        'json': 1
                    }
                    
                    result_response = requests.get(f"{api_url}/res.php", params=result_params)
                    result_data = result_response.json()
                    
                    if result_data['status'] == 1:
                        # 獲取驗證碼答案
                        captcha_text = result_data['request']
                        
                        # 填入驗證碼
                        input_elements = driver.find_elements(By.XPATH, "//input[contains(@placeholder, '驗證碼')]")
                        if input_elements:
                            input_elements[0].clear()
                            input_elements[0].send_keys(captcha_text)
                            
                            # 提交表單
                            submit_buttons = driver.find_elements(By.XPATH, "//button[contains(@type, 'submit')]")
                            if submit_buttons:
                                submit_buttons[0].click()
                                time.sleep(2)
                                return True
                    
                    elif result_data['request'] != 'CAPCHA_NOT_READY':
                        self.logger.error(f"2Captcha解決失敗: {result_data['request']}")
                        return False
            
            elif captcha_type == "recaptcha":
                if 'site_key' not in captcha_data or 'page_url' not in captcha_data:
                    return False
                
                # 提交ReCAPTCHA
                params = {
                    'key': api_key,
                    'method': 'userrecaptcha',
                    'googlekey': captcha_data['site_key'],
                    'pageurl': captcha_data['page_url'],
                    'json': 1
                }
                
                # 提交請求
                response = requests.post(f"{api_url}/in.php", params=params)
                response_data = response.json()
                
                if response_data['status'] != 1:
                    self.logger.error(f"2Captcha提交ReCAPTCHA失敗: {response_data['request']}")
                    return False
                
                # 獲取請求ID
                request_id = response_data['request']
                
                # 等待結果
                for _ in range(30):  # 最多等待30次，每次5秒
                    time.sleep(5)
                    
                    # 查詢結果
                    result_params = {
                        'key': api_key,
                        'action': 'get',
                        'id': request_id,
                        'json': 1
                    }
                    
                    result_response = requests.get(f"{api_url}/res.php", params=result_params)
                    result_data = result_response.json()
                    
                    if result_data['status'] == 1:
                        # 獲取g-recaptcha-response
                        g_recaptcha_response = result_data['request']
                        
                        # 使用JavaScript設置g-recaptcha-response
                        script = f"""
                        document.getElementById('g-recaptcha-response').innerHTML = '{g_recaptcha_response}';
                        captchaCallback('{g_recaptcha_response}');
                        """
                        
                        driver.execute_script(script)
                        time.sleep(2)
                        return True
                    
                    elif result_data['request'] != 'CAPCHA_NOT_READY':
                        self.logger.error(f"2Captcha解決ReCAPTCHA失敗: {result_data['request']}")
                        return False
            
            return False
        
        except Exception as e:
            self.logger.error(f"使用2Captcha服務時發生錯誤: {str(e)}")
            return False
    
    def _solve_with_anticaptcha(self, api_url: str, api_key: str, captcha_type: str, captcha_data: Dict, driver: webdriver.Remote) -> bool:
        """
        使用Anti-Captcha服務解決驗證碼
        
        Args:
            api_url: API URL
            api_key: API密鑰
            captcha_type: 驗證碼類型
            captcha_data: 驗證碼數據
            driver: WebDriver實例
            
        Returns:
            是否成功解決
        """
        try:
            import requests
            
            # Anti-Captcha API實現
            # 注意：此處僅為示例，實際使用時需要按照Anti-Captcha的API文檔實現
            
            self.logger.warning("Anti-Captcha服務支持尚未完全實現")
            return False
        
        except Exception as e:
            self.logger.error(f"使用Anti-Captcha服務時發生錯誤: {str(e)}")
            return False
    
    def _save_captcha_sample(self, driver: webdriver.Remote, captcha_type: str):
        """
        保存驗證碼樣本
        
        Args:
            driver: WebDriver實例
            captcha_type: 驗證碼類型
        """
        try:
            # 創建樣本目錄
            sample_type_dir = os.path.join(self.sample_dir, captcha_type)
            os.makedirs(sample_type_dir, exist_ok=True)
            
            # 生成文件名
            timestamp = int(time.time())
            sample_file = os.path.join(sample_type_dir, f"{captcha_type}_{timestamp}")
            
            if captcha_type == "text":
                # 查找驗證碼圖片
                img_elements = driver.find_elements(By.XPATH, "//img[contains(@src, 'captcha')]")
                if not img_elements:
                    return
                
                img_element = img_elements[0]
                img_url = img_element.get_attribute("src")
                
                # 保存圖片
                if img_url.startswith('data:image'):
                    # Base64圖片
                    base64_data = img_url.split(',')[1]
                    with open(f"{sample_file}.png", "wb") as f:
                        f.write(base64.b64decode(base64_data))
                else:
                    # URL圖片
                    import requests
                    response = requests.get(img_url)
                    with open(f"{sample_file}.png", "wb") as f:
                        f.write(response.content)
                
                self.logger.debug(f"已保存文本驗證碼樣本: {sample_file}.png")
            
            elif captcha_type == "slider":
                # 保存背景圖片和滑塊圖片
                background_img = driver.find_element(By.XPATH, "//div[contains(@class, 'slider')]/img")
                bg_url = background_img.get_attribute("src")
                
                if bg_url.startswith('data:image'):
                    # Base64圖片
                    base64_data = bg_url.split(',')[1]
                    with open(f"{sample_file}_bg.png", "wb") as f:
                        f.write(base64.b64decode(base64_data))
                else:
                    # URL圖片
                    import requests
                    response = requests.get(bg_url)
                    with open(f"{sample_file}_bg.png", "wb") as f:
                        f.write(response.content)
                
                # 保存整個驗證碼區域的截圖
                slider_container = driver.find_element(By.XPATH, "//div[contains(@class, 'slider')]")
                slider_container.screenshot(f"{sample_file}_full.png")
                
                self.logger.debug(f"已保存滑塊驗證碼樣本: {sample_file}_bg.png, {sample_file}_full.png")
            
            elif captcha_type == "click":
                # 保存點擊驗證碼圖片
                img_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'imgCaptcha')]/img")
                if not img_elements:
                    return
                
                img_element = img_elements[0]
                img_url = img_element.get_attribute("src")
                
                # 保存圖片
                if img_url.startswith('data:image'):
                    # Base64圖片
                    base64_data = img_url.split(',')[1]
                    with open(f"{sample_file}.png", "wb") as f:
                        f.write(base64.b64decode(base64_data))
                else:
                    # URL圖片
                    import requests
                    response = requests.get(img_url)
                    with open(f"{sample_file}.png", "wb") as f:
                        f.write(response.content)
                
                # 保存提示文本
                hint_elements = driver.find_elements(By.XPATH, "//div[contains(text(), '點擊圖片中的')]")
                if hint_elements:
                    hint_text = hint_elements[0].text
                    with open(f"{sample_file}.txt", "w", encoding="utf-8") as f:
                        f.write(hint_text)
                
                self.logger.debug(f"已保存點擊驗證碼樣本: {sample_file}.png")
            
            elif captcha_type == "recaptcha":
                # 保存ReCAPTCHA信息
                recaptcha_elements = driver.find_elements(By.XPATH, "//div[@class='g-recaptcha']")
                if not recaptcha_elements:
                    return
                
                # 獲取site-key
                site_key = recaptcha_elements[0].get_attribute("data-sitekey")
                page_url = driver.current_url
                
                # 保存信息
                info = {
                    "site_key": site_key,
                    "page_url": page_url,
                    "timestamp": timestamp
                }
                
                with open(f"{sample_file}.json", "w", encoding="utf-8") as f:
                    json.dump(info, f, indent=2)
                
                # 保存截圖
                recaptcha_elements[0].screenshot(f"{sample_file}.png")
                
                self.logger.debug(f"已保存ReCAPTCHA樣本: {sample_file}.json, {sample_file}.png")
        
        except Exception as e:#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import logging
import base64
import json
import random
from typing import Dict, List, Optional, Any, Union, Tuple, Type

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from ..utils.logger import setup_logger
from ..utils.error_handler import retry_on_exception, handle_exception
from .solvers.base_solver import BaseCaptchaSolver


class CaptchaManager:
    """
    驗證碼管理器，用於檢測和解決各種類型的驗證碼挑戰。
    支持文本驗證碼、滑塊驗證碼、點擊驗證碼和ReCAPTCHA等。
    """
    
    def __init__(self, config: Dict = None, log_level: int = logging.INFO):
        """
        初始化驗證碼管理器
        
        Args:
            config: 配置字典
            log_level: 日誌級別
        """
        self.logger = setup_logger(__name__, log_level)
        self.logger.info("初始化驗證碼管理器")
        
        self.config = config or {}
        
        # 驗證碼樣本存儲路徑
        self.sample_dir = self.config.get("sample_dir", "captchas")
        os.makedirs(self.sample_dir, exist_ok=True)
        
        # 是否保存驗證碼樣本
        self.save_samples = self.config.get("save_samples", True)
        
        # 驗證碼解決器
        self.solvers = {}
        self._load_solvers()
        
        # 驗證碼檢測器
        self.captcha_detectors = [
            self._detect_text_captcha,
            self._detect_slider_captcha,
            self._detect_click_captcha,
            self._detect_recaptcha
        ]
        
        # 等待超時
        self.timeout = self.config.get("timeout", 30)
        
        # 重試設置
        self.max_retries = self.config.get("max_retries", 3)
        self.retry_delay = self.config.get("retry_delay", 2)
        
        # 第三方服務
        self.api_key = self.config.get("api_key", None)
        self.third_party_services = self.config.get("third_party_services", [])
        
        self.logger.info("驗證碼管理器初始化完成")
    
    def _load_solvers(self):
        """載入驗證碼解決器"""
        # 動態載入解決器
        solver_types = {
            "text": self._load_solver_class(".solvers.text_solver", "TextCaptchaSolver"),
            "slider": self._load_solver_class(".solvers.slider_solver", "SliderCaptchaSolver"),
            "click": self._load_solver_class(".solvers.click_solver", "ClickCaptchaSolver"),
            "recaptcha": self._load_solver_class(".solvers.recaptcha_solver", "ReCaptchaSolver")
        }
        
        # 初始化解決器
        for solver_type, solver_class in solver_types.items():
            if solver_class:
                solver_config = self.config.get(f"{solver_type}_solver_config", {})
                self.solvers[solver_type] = solver_class(solver_config)
                self.logger.info(f"已載入 {solver_type} 驗證碼解決器")
    
    def _load_solver_class(self, module_path: str, class_name: str) -> Optional[Type[BaseCaptchaSolver]]:
        """
        動態載入驗證碼解決器類
        
        Args:
            module_path: 模塊路徑
            class_name: 類名
            
        Returns:
            解決器類或None
        """
        try:
            import importlib
            
            # 完整的模塊路徑
            full_module_path = f"{__package__}{module_path}"
            
            # 導入模塊
            module = importlib.import_module(full_module_path)
            
            # 獲取類
            solver_class = getattr(module, class_name)
            
            return solver_class
        
        except (ImportError, AttributeError) as e:
            self.logger.warning(f"載入驗證碼解決器類 {class_name} 失敗: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"載入驗證碼解決器類時發生錯誤: {str(e)}")
            return None
    
    def detect_captcha(self, driver: webdriver.Remote) -> Tuple[bool, str]:
        """
        檢測頁面中是否存在驗證碼
        
        Args:
            driver: WebDriver實例
            
        Returns:
            是否存在驗證碼和驗證碼類型
        """
        for detector in self.captcha_detectors:
            try:
                detected, captcha_type = detector(driver)
                if detected:
                    self.logger.info(f"檢測到 {captcha_type} 驗證碼")
                    return True, captcha_type
            except Exception as e:
                self.logger.error(f"執行驗證碼檢測器失敗: {str(e)}")
        
        return False, ""
    
    def _detect_text_captcha(self, driver: webdriver.Remote) -> Tuple[bool, str]:
        """檢測文本驗證碼"""
        # 常見的文本驗證碼選擇器
        text_captcha_selectors = [
            "//img[contains(@src, 'captcha')]",
            "//img[contains(@src, 'verify')]",
            "//img[contains(@src, 'vcode')]",
            "//img[contains(@id, 'captcha')]",
            "//img[contains(@class, 'captcha')]",
            "//input[contains(@placeholder, '驗證碼')]",
            "//input[contains(@placeholder, 'captcha')]",
            "//div[contains(text(), '驗證碼')]/following::img",
            "//label[contains(text(), '驗證碼')]/following::img"
        ]
        
        for selector in text_captcha_selectors:
            elements = driver.find_elements(By.XPATH, selector)
            if elements:
                return True, "text"
        
        return False, ""
    
    def _detect_slider_captcha(self, driver: webdriver.Remote) -> Tuple[bool, str]:
        """檢測滑塊驗證碼"""
        # 常見的滑塊驗證碼選擇器
        slider_captcha_selectors = [
            "//div[contains(@class, 'slider')]",
            "//div[contains(@class, 'sliderContainer')]",
            "//div[contains(@class, 'verify-slider')]",
            "//div[contains(@class, 'sliderMask')]",
            "//div[contains(@class, 'sliderIcon')]",
            "//div[contains(@id, 'slider')]",
            "//div[@class='gt_slider_knob']",
            "//div[@class='gt_slider_knob gt_show']"
        ]
        
        for selector in slider_captcha_selectors:
            elements = driver.find_elements(By.XPATH, selector)
            if elements:
                return True, "slider"
        
        return False, ""
    
    def _detect_click_captcha(self, driver: webdriver.Remote) -> Tuple[bool, str]:
        """檢測點擊驗證碼"""
        # 常見的點擊驗證碼選擇器
        click_captcha_selectors = [
            "//div[contains(@class, 'imgCaptcha')]",
            "//div[contains(@class, 'click-captcha')]",
            "//div[contains(@class, 'point-captcha')]",
            "//div[contains(text(), '點擊圖片中的')]",
            "//div[contains(text(), '請按順序點擊')]",
            "//div[contains(text(), '請點擊下圖中')]",
            "//div[contains(text(), 'Click on the')]"
        ]
        
        for selector in click_captcha_selectors:
            elements = driver.find_elements(By.XPATH, selector)
            if elements:
                return True, "click"
        
        return False, ""
    
    def _detect_recaptcha(self, driver: webdriver.Remote) -> Tuple[bool, str]:
        """檢測Google ReCAPTCHA"""
        # ReCAPTCHA選擇器
        recaptcha_selectors = [
            "//iframe[contains(@src, 'recaptcha')]",
            "//div[@class='g-recaptcha']",
            "//div[contains(@class, 'recaptcha')]",
            "//iframe[@title='reCAPTCHA']"
        ]
        
        for selector in recaptcha_selectors:
            elements = driver.find_elements(By.XPATH, selector)
            if elements:
                return True, "recaptcha"
        
        return False, ""
    
    @retry_on_exception(retries=3, delay=1)
    def solve_captcha(self, driver: webdriver.Remote) -> bool:
        """
        解決驗證碼
        
        Args:
            driver: WebDriver實例
            
        Returns:
            是否成功解決
        """
        # 檢測驗證碼類型
        detected, captcha_type = self.detect_captcha(driver)
        
        if not detected:
            self.logger.info("未檢測到驗證碼")
            return True
        
        self.logger.info(f"嘗試解決 {captcha_type} 驗證碼")
        
        # 獲取對應的解決器
        solver = self.solvers.get(captcha_type)
        
        if not solver:
            self.logger.warning(f"未找到 {captcha_type} 驗證碼解決器")
            # 嘗試使用第三方服務
            return self._solve_with_third_party(driver, captcha_type)
        
        # 保存驗證碼樣本（如果需要）
        if self.save_samples:
            self._save_captcha_sample(driver, captcha_type)
        
        # 使用解決器解決驗證碼
        try:
            result = solver.solve(driver)
            
            if result:
                self.logger.info(f"成功解決 {captcha_type} 驗證碼")
            else:
                self.logger.warning(f"解決 {captcha_type} 驗證碼失敗")
            
            return result
        
        except Exception as e:
            self.logger.error(f"解決 {captcha_type} 驗證碼時發生錯誤: {str(e)}")
            # 嘗試使用第三方服務
            return self._solve_with_third_party(driver, captcha_type)
    
    def _solve_with_third_party(self, driver: webdriver.Remote, captcha_type: str) -> bool:
        """
        使用第三方服務解決驗證碼
        
        Args:
            driver: WebDriver實例
            captcha_type: 驗證碼類型
            
        Returns:
            是否成功解決
        """
        if not self.third_party_services:
            self.logger.warning("沒有配置第三方服務")
            return False
        
        for service in self.third_party_services:
            service_type = service.get("type")
            service_api = service.get("api")
            service_key = service.get("key") or self.api_key
            
            if not all([service_type, service_api, service_key]):
                self.logger.warning(f"第三方服務配置不完整: {service}")
                continue
            
            # 檢查服務是否支持此類型的驗證碼
            if captcha_type not in service.get("supported_types", []):
                self.logger.debug(f"服務 {service_type} 不支持 {captcha_type} 驗證碼")
                continue
            
            self.logger.info(f"嘗試使用第三方服務 {service_type} 解決 {captcha_type} 驗證碼")
            
            try:
                # 獲取驗證碼圖片或相關信息
                captcha_data = self._get_captcha_data(driver, captcha_type)
                
                if not captcha_data:
                    self.logger.warning("獲取驗證碼數據失敗")
                    continue
                
                # 調用第三方服務API
                if service_type == "2captcha":
                    result = self._solve_with_2captcha(service_api, service_key, captcha_type, captcha_data, driver)
                elif service_type == "anti-captcha":
                    result = self._solve_with_anticaptcha(service_api, service_key, captcha_type, captcha_data, driver)
                else:
                    self.logger.warning(f"不支持的第三方服務類型: {service_type}")
                    continue
                
                if result:
                    self.logger.info(f"使用 {service_type} 成功解決驗證碼")
                    return True
                else:
                    self.logger.warning(f"使用 {service_type} 解決驗證碼失敗")
            
            except Exception as e:
                self.logger.error(f"使用第三方服務 {service_type} 時發生錯誤: {str(e)}")
        
        return False
    
    def _get_captcha_data(self, driver: webdriver.Remote, captcha_type: str) -> Dict:
        """
        獲取驗證碼數據
        
        Args:
            driver: WebDriver實例
            captcha_type: 驗證碼類型
            
        Returns:
            驗證碼數據
        """
        try:
            if captcha_type == "text":
                # 查找驗證碼圖片
                img_elements = driver.find_elements(By.XPATH, "//img[contains(@src, 'captcha')]")
                if not img_elements:
                    return {}
                
                img_element = img_elements[0]
                img_url = img_element.get_attribute("src")
                
                # 如果是Base64圖片
                if img_url.#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import logging
import base64
import json
import random
from typing import Dict, List, Optional, Any, Union, Tuple, Type

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from ..utils.logger import setup_logger
from ..utils.error_handler import retry_on_exception, handle_exception
from .solvers.base_solver import BaseCaptchaSolver


class CaptchaManager:
    """
    驗證碼管理器，用於檢測和解決各種類型的驗證碼挑戰。
    支持文本驗證碼、滑塊驗證碼、點擊驗證碼和ReCAPTCHA等。
    """
    
    def __init__(self, config: Dict = None, log_level: int = logging.INFO):
        """
        初始化驗證碼管理器
        
        Args:
            config: 配置字典
            log_level: 日誌級別
        """
        self.logger = setup_logger(__name__, log_level)
        self.logger.info("初始化驗證碼管