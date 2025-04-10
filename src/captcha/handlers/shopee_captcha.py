"""
蝦皮(Shopee)網站爬蟲驗證碼處理模組
用於處理各種類型的驗證碼挑戰
"""

import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class CaptchaHandler:
    """驗證碼處理器"""
    
    @staticmethod
    def bypass_shopee_captcha(driver):
        """嘗試繞過蝦皮的驗證碼挑戰"""
        try:
            print("檢測是否存在驗證碼...")
            
            # 檢查各種可能的驗證碼元素
            captcha_selectors = [
                "//div[contains(@class, 'captcha-container')]",
                "//div[contains(@class, 'slide-captcha')]",
                "//div[contains(@class, 'shopee-captcha')]",
                "//div[contains(text(), '安全驗證') or contains(text(), '驗證')]//ancestor::div[contains(@class, 'modal')]",
                "//div[contains(@class, 'geetest_panel')]"
            ]
            
            captcha_found = False
            for selector in captcha_selectors:
                elements = driver.find_elements(By.XPATH, selector)
                if elements and any(e.is_displayed() for e in elements):
                    captcha_found = True
                    print(f"檢測到驗證碼元素: {selector}")
                    break
            
            if not captcha_found:
                print("未檢測到驗證碼")
                return False
                
            # 截圖以便識別
            timestamp = int(time.time())
            screenshot_path = f"captcha_screenshot_{timestamp}.png"
            driver.save_screenshot(screenshot_path)
            print(f"已保存驗證碼截圖: {screenshot_path}")
            
            # 檢測驗證碼類型並處理
            # 1. 滑塊驗證碼
            slider_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'slider') and contains(@class, 'button')]")
            if slider_elements and slider_elements[0].is_displayed():
                print("檢測到滑塊驗證碼，嘗試處理...")
                return CaptchaHandler._handle_slider_captcha(driver)
            
            # 2. 圖形驗證碼
            image_captcha_elements = driver.find_elements(By.XPATH, "//img[contains(@src, 'captcha') or contains(@class, 'captcha')]")
            if image_captcha_elements and image_captcha_elements[0].is_displayed():
                print("檢測到圖形驗證碼，需要手動處理")
                return CaptchaHandler._prompt_manual_captcha(driver)
            
            # 3. ReCAPTCHA
            recaptcha_elements = driver.find_elements(By.XPATH, "//iframe[contains(@src, 'recaptcha')]")
            if recaptcha_elements and recaptcha_elements[0].is_displayed():
                print("檢測到reCAPTCHA，嘗試處理...")
                return CaptchaHandler._handle_recaptcha(driver)
                
            # 如果找不到具體類型，提示手動處理
            print("檢測到驗證需求，但無法確定具體類型，需要手動處理")
            return CaptchaHandler._prompt_manual_captcha(driver)
            
        except Exception as e:
            print(f"處理驗證碼時發生錯誤: {str(e)}")
            return False
    
    @staticmethod
    def _handle_slider_captcha(driver):
        """處理滑塊驗證碼"""
        try:
            # 查找滑塊元素
            slider = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'slide-button') or contains(@class, 'slider-button')]"))
            )
            
            # 查找軌道元素以確定距離
            track = driver.find_element(By.XPATH, "//div[contains(@class, 'slide-track') or contains(@class, 'slider-track')]")
            track_width = track.size['width']
            
            # 計算需要拖動的距離
            distance = track_width * 0.9  # 滑到90%位置
            
            # 生成人類化的拖動軌跡
            actions = ActionChains(driver)
            
            # 首先移動到滑塊位置
            actions.move_to_element(slider)
            actions.pause(random.uniform(0.2, 0.5))
            actions.click_and_hold()
            actions.pause(random.uniform(0.2, 0.5))
            
            # 緩慢移動 - 先加速再減速
            current = 0
            mid = distance * 0.7
            t = 0.2
            v = 0
            
            while current < distance:
                if current < mid:
                    # 加速階段
                    a = random.uniform(2, 3)
                    v = v + a * t
                    move = v * t + 0.5 * a * t * t
                else:
                    # 減速階段
                    a = -random.uniform(1, 2)
                    v = max(0, v + a * t)
                    move = v * t + 0.5 * a * t * t
                
                # 添加隨機微擾動
                if random.random() < 0.3:
                    move += random.uniform(-0.5, 0.5)
                
                current += move
                # 確保不超過目標距離
                current = min(current, distance)
                
                actions.move_by_offset(move, random.uniform(-0.5, 0.5))
                actions.pause(random.uniform(0.01, 0.03))
            
            # 釋放滑塊
            actions.release()
            actions.perform()
            
            # 等待驗證結果
            time.sleep(3)
            
            # 檢查是否成功
            success = not (driver.find_elements(By.XPATH, "//div[contains(@class, 'slide-button') or contains(@class, 'slider-button')]") and 
                          driver.find_elements(By.XPATH, "//div[contains(@class, 'slide-button') or contains(@class, 'slider-button')]")[0].is_displayed())
            
            if success:
                print("滑塊驗證成功")
            else:
                print("滑塊驗證可能失敗，需要手動處理")
                return CaptchaHandler._prompt_manual_captcha(driver)
                
            return success
        except Exception as e:
            print(f"處理滑塊驗證碼時發生錯誤: {str(e)}")
            return CaptchaHandler._prompt_manual_captcha(driver)
    
    @staticmethod
    def _handle_recaptcha(driver):
        """處理reCAPTCHA"""
        try:
            # 找到reCAPTCHA iframe
            recaptcha_frame = driver.find_element(By.XPATH, "//iframe[contains(@src, 'recaptcha')]")
            driver.switch_to.frame(recaptcha_frame)
            
            # 點擊核取方塊
            checkbox = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@class='recaptcha-checkbox-border']"))
            )
            
            # 模擬人類點擊
            ActionChains(driver).move_to_element(checkbox).pause(random.uniform(0.3, 0.8)).click().perform()
            
            # 切回主頁面
            driver.switch_to.default_content()
            
            # 等待可能的挑戰frame
            time.sleep(2)
            challenge_frames = driver.find_elements(By.XPATH, "//iframe[contains(@src, 'recaptcha/api2/bframe')]")
            
            if challenge_frames:
                print("檢測到reCAPTCHA挑戰，需要手動處理")
                return CaptchaHandler._prompt_manual_captcha(driver)
            
            # 檢查是否成功
            time.sleep(3)
            success = not (driver.find_elements(By.XPATH, "//iframe[contains(@src, 'recaptcha')]") and 
                          driver.find_elements(By.XPATH, "//iframe[contains(@src, 'recaptcha')]")[0].is_displayed())
            
            if success:
                print("reCAPTCHA驗證成功")
            else:
                print("reCAPTCHA驗證可能失敗，需要手動處理")
                return CaptchaHandler._prompt_manual_captcha(driver)
                
            return success
        except Exception as e:
            print(f"處理reCAPTCHA時發生錯誤: {str(e)}")
            return CaptchaHandler._prompt_manual_captcha(driver)
    
    @staticmethod
    def _prompt_manual_captcha(driver):
        """提示用戶手動處理驗證碼"""
        print("\n" + "="*50)
        print("檢測到需要手動處理的驗證碼!")
        print("請在瀏覽器窗口中完成驗證")
        print("完成後請按Enter鍵繼續...")
        print("="*50)
        
        # 等待用戶輸入
        input()
        
        print("繼續執行...")
        time.sleep(2)
        return True 