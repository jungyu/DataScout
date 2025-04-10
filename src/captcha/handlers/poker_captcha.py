"""
撲克牌驗證碼解決器模組
提供基本的撲克牌驗證碼識別和解決功能
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import cv2
import numpy as np
from PIL import Image
import io
import base64
from ...utils.logger import setup_logger

class PokerCaptchaSolver:
    """撲克牌驗證碼解決器"""
    
    def __init__(self, driver, logger=None):
        """
        初始化撲克牌驗證碼解決器
        
        Args:
            driver: Selenium WebDriver 實例
            logger: 日誌記錄器
        """
        self.driver = driver
        self.logger = logger or setup_logger('poker_captcha')
        
    def get_card_images(self):
        """
        從區域 A 和區域 B 提取卡牌圖片
        
        Returns:
            tuple: (area_a_cards, area_b_cards) 兩個區域的卡牌元素列表
        """
        # 等待驗證碼可見
        WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "div[class*='area']"))
        )
        
        # 獲取區域 A 的卡牌（模板）
        area_a = self.driver.find_element(By.CSS_SELECTOR, "div[class*='areaA']") 
        area_a_cards = area_a.find_elements(By.TAG_NAME, "img")
        
        # 獲取區域 B 的卡牌（選項）
        area_b = self.driver.find_element(By.CSS_SELECTOR, "div[class*='areaB']")
        area_b_cards = area_b.find_elements(By.TAG_NAME, "img")
        
        return area_a_cards, area_b_cards
    
    def get_card_features(self, card_element):
        """
        從卡牌元素中提取特徵（顏色和花色/點數）
        
        Args:
            card_element: 卡牌圖片元素
            
        Returns:
            dict: 包含卡牌特徵的字典
        """
        # 獲取卡牌圖片
        img_src = card_element.get_attribute('src')
        
        # 如果是 data URL
        if img_src.startswith('data:image'):
            # 提取 base64 部分
            base64_data = img_src.split(',')[1]
            img_data = base64.b64decode(base64_data)
            img = Image.open(io.BytesIO(img_data))
        else:
            # 如果是普通 URL，需要下載
            # 目前假設都是 data URLs
            pass
        
        # 轉換為 OpenCV 格式
        img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        
        # 識別卡牌顏色（紅色或黑色）
        # 轉換為 HSV 以更好地分割顏色
        hsv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2HSV)
        
        # 定義紅色範圍
        lower_red1 = np.array([0, 100, 100])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([160, 100, 100])
        upper_red2 = np.array([180, 255, 255])
        
        # 創建紅色遮罩
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        red_mask = mask1 + mask2
        
        # 計算紅色像素數量
        red_pixel_count = cv2.countNonZero(red_mask)
        
        # 判斷卡牌是紅色還是黑色
        color = "red" if red_pixel_count > 100 else "black"
        
        # 返回特徵（目前只有顏色，但可以擴展）
        return {
            "color": color,
            "image": img_cv  # 保留圖片以供進一步處理
        }
    
    def match_cards(self):
        """
        匹配區域 A 和區域 B 的卡牌
        
        Returns:
            list: 匹配的卡牌列表
        """
        area_a_cards, area_b_cards = self.get_card_images()
        
        # 提取區域 A 卡牌的特徵
        template_cards = []
        for card in area_a_cards:
            template_cards.append(self.get_card_features(card))
        
        # 提取區域 B 卡牌的特徵
        option_cards = []
        for i, card in enumerate(area_b_cards):
            features = self.get_card_features(card)
            features["index"] = i  # 儲存索引以供後續點擊
            option_cards.append(features)
        
        # 根據特徵找到匹配
        matches = []
        for template in template_cards:
            best_match = None
            best_score = float('inf')
            
            for option in option_cards:
                # 顏色匹配
                if template["color"] != option["color"]:
                    continue
                
                # 可以在這裡添加更多匹配標準
                # 目前使用簡單的模板匹配
                result = cv2.matchTemplate(template["image"], option["image"], cv2.TM_SQDIFF_NORMED)
                min_val, _, _, _ = cv2.minMaxLoc(result)
                
                if min_val < best_score:
                    best_score = min_val
                    best_match = option
            
            if best_match:
                matches.append(best_match)
        
        return matches
    
    def solve_captcha(self):
        """解決撲克牌驗證碼"""
        try:
            # 獲取匹配的卡牌
            matches = self.match_cards()
            
            # 點擊區域 B 中匹配的卡牌
            area_b_cards = self.driver.find_elements(By.CSS_SELECTOR, "div[class*='areaB'] img")
            for match in matches:
                index = match["index"]
                area_b_cards[index].click()
                time.sleep(0.5)  # 點擊之間的延遲
            
            # 點擊提交按鈕
            submit_button = self.driver.find_element(By.CSS_SELECTOR, "button.confirm")
            submit_button.click()
            
            # 等待結果或下一頁
            time.sleep(2)
            
            # 檢查是否需要解決另一個驗證碼
            try:
                captcha_present = self.driver.find_element(By.CSS_SELECTOR, "div[class*='area']").is_displayed()
                if captcha_present:
                    self.solve_captcha()  # 遞迴調用處理多個驗證碼
            except:
                pass  # 沒有更多驗證碼，繼續
                
            self.logger.info("成功解決撲克牌驗證碼")
            return True
            
        except Exception as e:
            self.logger.error(f"解決撲克牌驗證碼時發生錯誤: {str(e)}")
            return False 