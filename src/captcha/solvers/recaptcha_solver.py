"""
reCAPTCHA 驗證碼解決器 (reCAPTCHA Solver)
Copyright (c) 2024 Aaron-Yu, Claude AI
Author: Aaron-Yu <jungyuyu@gmail.com>
License: MIT License
版本: 1.0.0
"""

import time
import logging
import random
import json
import os
import base64
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from .base_solver import BaseCaptchaSolver  # 修改繼承類


class RecaptchaSolver(BaseCaptchaSolver):
    """
    reCAPTCHA 解決器，支援 reCAPTCHA v2 和 v3
    """
    
    def _init_solver(self):
        """初始化解決器特定設置"""
        # 自動檢測是否可以使用第三方服務
        self.use_external_service = self.config.get("use_external_service", False)
        
        # 音頻解決模式
        self.use_audio = self.config.get("use_audio", False)
        
        # 延遲設置
        self.delay_after_solve = self.config.get("delay_after_solve", [0.5, 1.5])
    
    def _get_captcha_type(self) -> str:
        """獲取驗證碼類型"""
        return "recaptcha"
    
    def detect(self) -> bool:
        """檢測頁面上是否存在 reCAPTCHA"""
        try:
            if not self.driver:
                self.logger.error("未提供WebDriver實例")
                return False
                
            # ReCAPTCHA選擇器
            recaptcha_selectors = [
                "iframe[src*='google.com/recaptcha']",
                "div.g-recaptcha",
                "div[class*='recaptcha']",
                "iframe[title='reCAPTCHA']"
            ]
            
            for selector in recaptcha_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    return True
            
            # 查找非標準嵌入的 reCAPTCHA
            scripts = self.driver.find_elements(By.CSS_SELECTOR, "script[src*='google.com/recaptcha/api.js']")
            if scripts:
                return True
                
            return False
            
        except Exception as e:
            self.logger.error(f"檢測 reCAPTCHA 時出錯: {str(e)}")
            return False
    
    def solve(self, driver: webdriver.Remote = None) -> bool:
        """
        解決 reCAPTCHA
        
        Args:
            driver: WebDriver實例
            
        Returns:
            bool: 是否成功解決
        """
        driver = driver or self.driver
        if not driver:
            self.logger.error("未提供WebDriver實例")
            return False
            
        try:
            # 找到 reCAPTCHA 元素
            captcha_element = self._find_recaptcha()
            if not captcha_element:
                self.logger.error("無法找到 reCAPTCHA 元素")
                return False
            
            # 檢測 reCAPTCHA 版本
            version = self._detect_version(captcha_element)
            self.logger.info(f"檢測到 reCAPTCHA 版本: {version}")
            
            # 根據版本解決驗證碼
            if version == "v2_checkbox":
                return self._solve_v2_checkbox(captcha_element)
            elif version == "v2_invisible":
                return self._solve_v2_invisible(captcha_element)
            elif version == "v3":
                return self._solve_v3(captcha_element)
            else:
                self.logger.error(f"不支援的 reCAPTCHA 版本: {version}")
                return False
                
        except Exception as e:
            self.logger.error(f"解決 reCAPTCHA 時發生錯誤: {str(e)}")
            return False
    
    def _find_recaptcha(self):
        """
        尋找頁面上的 reCAPTCHA 元素
        
        Returns:
            WebElement: reCAPTCHA 元素，未找到時返回 None
        """
        # 尋找常見的 reCAPTCHA 元素
        selectors = [
            ".g-recaptcha",
            "[data-sitekey]",
            "iframe[src*='google.com/recaptcha']",
            "iframe[src*='recaptcha.net']"
        ]
        
        for selector in selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                return element
            except NoSuchElementException:
                continue
        
        return None
    
    def _detect_version(self, element):
        """
        檢測 reCAPTCHA 版本
        
        Args:
            element: reCAPTCHA 元素
            
        Returns:
            str: 'v2_checkbox', 'v2_invisible', 或 'v3'
        """
        try:
            # 檢查元素屬性
            if 'data-size' in element.get_attribute('outerHTML') and element.get_attribute('data-size') == 'invisible':
                return "v2_invisible"
            
            # 檢查是否有 checkbox
            iframes = self.driver.find_elements(By.CSS_SELECTOR, "iframe[src*='google.com/recaptcha']")
            if iframes:
                # 未處於 iframe 內
                main_frame = self.driver.current_window_handle
                for iframe in iframes:
                    try:
                        self.driver.switch_to.frame(iframe)
                        checkbox = self.driver.find_elements(By.CSS_SELECTOR, ".recaptcha-checkbox-border")
                        if checkbox:
                            self.driver.switch_to.window(main_frame)
                            return "v2_checkbox"
                    except:
                        pass
                    finally:
                        self.driver.switch_to.window(main_frame)
            
            # 檢查是否為 v3
            # v3 通常只有一個腳本加載，沒有用戶界面
            scripts = self.driver.find_elements(By.CSS_SELECTOR, "script[src*='google.com/recaptcha/api.js']")
            for script in scripts:
                src = script.get_attribute("src")
                if "render=" in src:
                    return "v3"
            
            # 預設為 v2 checkbox
            return "v2_checkbox"
            
        except Exception as e:
            self.logger.error(f"檢測 reCAPTCHA 版本時發生錯誤: {e}")
            return "v2_checkbox"  # 假設為最常見的版本
    
    def _solve_v2_checkbox(self, captcha_element, frame_element=None):
        """
        解決 reCAPTCHA v2 勾選框版本
        
        Args:
            captcha_element: reCAPTCHA 元素
            frame_element: 包含驗證碼的 iframe 元素 (可選)
            
        Returns:
            bool: 是否成功解決
        """
        # 獲取網站密鑰
        site_key = captcha_element.get_attribute("data-sitekey")
        if not site_key:
            self.logger.error("無法獲取 reCAPTCHA 網站密鑰")
            return False
        
        # 使用第三方服務
        if self.config["service"] and self.config["api_key"]:
            token = self._solve_with_external_service(site_key, "v2")
            if token:
                return self._apply_token(token)
        
        # 備用：嘗試使用音頻解決方案
        if self.config["use_audio"]:
            return self._solve_with_audio()
        
        self.logger.error("無法解決 reCAPTCHA v2")
        return False
    
    def _solve_v2_invisible(self, captcha_element):
        """
        解決 reCAPTCHA v2 不可見版本
        
        Args:
            captcha_element: reCAPTCHA 元素
            
        Returns:
            bool: 是否成功解決
        """
        # 獲取網站密鑰
        site_key = captcha_element.get_attribute("data-sitekey")
        if not site_key:
            self.logger.error("無法獲取 reCAPTCHA 網站密鑰")
            return False
        
        # 使用第三方服務
        if self.config["service"] and self.config["api_key"]:
            token = self._solve_with_external_service(site_key, "v2")
            if token:
                return self._apply_token(token)
        
        self.logger.error("無法解決 reCAPTCHA v2 invisible")
        return False
    
    def _solve_v3(self, captcha_element):
        """
        解決 reCAPTCHA v3
        
        Args:
            captcha_element: reCAPTCHA 元素
            
        Returns:
            bool: 是否成功解決
        """
        # 嘗試從腳本獲取網站密鑰
        site_key = None
        scripts = self.driver.find_elements(By.CSS_SELECTOR, "script[src*='google.com/recaptcha/api.js']")
        for script in scripts:
            src = script.get_attribute("src")
            if "render=" in src:
                parts = src.split("render=")
                if len(parts) > 1:
                    site_key = parts[1].split("&")[0]
                    break
        
        if not site_key:
            self.logger.error("無法獲取 reCAPTCHA v3 網站密鑰")
            return False
        
        # 使用第三方服務
        if self.config["service"] and self.config["api_key"]:
            token = self._solve_with_external_service(site_key, "v3")
            if token:
                return self._apply_token(token)
        
        self.logger.error("無法解決 reCAPTCHA v3")
        return False
    
    def _solve_with_audio(self):
        """
        使用音頻識別解決 reCAPTCHA
        
        Returns:
            bool: 是否成功解決
        """
        try:
            # 尋找 reCAPTCHA iframe
            main_frame = self.driver.current_window_handle
            
            # 查找 reCAPTCHA iframe
            wait = WebDriverWait(self.driver, 10)
            iframe = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[src*='google.com/recaptcha/api2/anchor']")))
            
            # 切換到 reCAPTCHA iframe
            self.driver.switch_to.frame(iframe)
            
            # 點擊驗證碼勾選框
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".recaptcha-checkbox-border"))).click()
            
            # 切回主框架
            self.driver.switch_to.default_content()
            
            # 等待挑戰 iframe 出現
            time.sleep(2)
            challenge_iframe = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "iframe[src*='google.com/recaptcha/api2/bframe']")))
            
            # 切換到挑戰 iframe
            self.driver.switch_to.frame(challenge_iframe)
            
            # 點擊音頻圖標
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#recaptcha-audio-button"))).click()
            
            # 等待音頻挑戰加載
            try:
                # 如果出現 "多次嘗試失敗" 訊息，則退出
                if len(self.driver.find_elements(By.CSS_SELECTOR, ".rc-doscaptcha-body-text")) > 0:
                    self.logger.error("reCAPTCHA 音頻挑戰不可用 (多次嘗試失敗)")
                    self.driver.switch_to.default_content()
                    return False
                
                # 等待音頻加載完成
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".rc-audiochallenge-tdownload-link")))
                
                # 下載音頻文件
                audio_link = self.driver.find_element(By.CSS_SELECTOR, ".rc-audiochallenge-tdownload-link").get_attribute("href")
                
                # 這裡應該使用合適的音頻轉文字服務
                # 示例：使用 Google Cloud Speech-to-Text 或其他語音識別服務
                audio_text = self._audio_to_text(audio_link)
                
                if not audio_text:
                    self.logger.error("無法識別音頻內容")
                    self.driver.switch_to.default_content()
                    return False
                
                # 輸入識別結果
                audio_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#audio-response")))
                audio_input.clear()
                audio_input.send_keys(audio_text)
                
                # 點擊驗證按鈕
                self.driver.find_element(By.CSS_SELECTOR, "#recaptcha-verify-button").click()
                
                # 等待驗證結果
                time.sleep(3)
                
                # 檢查是否成功
                if len(self.driver.find_elements(By.CSS_SELECTOR, ".rc-audiochallenge-error-message")) > 0 and \
                   self.driver.find_element(By.CSS_SELECTOR, ".rc-audiochallenge-error-message").get_attribute("innerHTML") != "":
                    self.logger.error("音頻識別結果不正確")
                    self.driver.switch_to.default_content()
                    return False
                
                # 驗證成功
                self.driver.switch_to.default_content()
                return True
                
            except TimeoutException:
                self.logger.error("等待音頻挑戰超時")
                self.driver.switch_to.default_content()
                return False
                
        except Exception as e:
            self.logger.error(f"使用音頻解決 reCAPTCHA 時發生錯誤: {e}")
            try:
                self.driver.switch_to.default_content()
            except:
                pass
            return False
    
    def _audio_to_text(self, audio_url):
        """
        將音頻轉換為文字
        
        Args:
            audio_url: 音頻URL
            
        Returns:
            str: 識別出的文字，失敗時返回 None
        """
        try:
            # 下載音頻
            audio_data = requests.get(audio_url).content
            
            # 這裡是示例，實際應用中需要使用真正的語音識別服務
            # 例如 Google Cloud Speech-to-Text, Azure Speech Service 等
            
            # 模擬識別結果（在實際應用中替換為真正的 API 調用）
            # 真實場景下，這裡應該實現與語音識別服務的集成
            
            # 由於無法實現真正的語音識別，此處返回 None
            self.logger.warning("未實現音頻識別功能，需要集成實際的語音識別服務")
            return None
            
        except Exception as e:
            self.logger.error(f"音頻轉文字失敗: {e}")
            return None
    
    def _apply_token(self, token):
        """
        將解決令牌應用到頁面
        
        Args:
            token: reCAPTCHA 解決令牌
            
        Returns:
            bool: 是否成功應用令牌
        """
        try:
            # 注入 token
            script = f"""
            document.querySelector('[name="g-recaptcha-response"]').innerHTML = "{token}";
            
            // 對於 v2 invisible 和 v3
            if (typeof ___grecaptcha_cfg !== 'undefined') {{
                // 嘗試觸發回調
                try {{
                    for (let key in ___grecaptcha_cfg.clients) {{
                        if (___grecaptcha_cfg.clients[key].hasOwnProperty('callback')) {{
                            ___grecaptcha_cfg.clients[key]['callback']('{token}');
                        }}
                    }}
                }} catch (e) {{
                    console.error("觸發回調失敗:", e);
                }}
            }}
            """
            
            self.driver.execute_script(script)
            
            # 等待一段時間讓令牌生效
            delay = random.uniform(
                self.config["delay_after_solve"][0],
                self.config["delay_after_solve"][1]
            )
            time.sleep(delay)
            
            return True
            
        except Exception as e:
            self.logger.error(f"應用 reCAPTCHA 令牌時發生錯誤: {e}")
            return False