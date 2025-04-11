"""
高級撲克牌驗證碼解決器模組
提供更進階的撲克牌驗證碼識別和解決功能
"""

import cv2
import numpy as np
from .poker_captcha import PokerCaptchaSolver
from src.core.utils.logger import setup_logger

class AdvancedPokerCaptchaSolver(PokerCaptchaSolver):
    """高級撲克牌驗證碼解決器"""
    
    def __init__(self, driver, template_path=None, logger=None):
        """
        初始化高級撲克牌驗證碼解決器
        
        Args:
            driver: Selenium WebDriver 實例
            template_path: 模板圖片路徑
            logger: 日誌記錄器
        """
        super().__init__(driver, logger)
        self.template_path = template_path or "templates/cards"
        
        # 定義卡牌花色的模板
        self.suit_templates = {
            "hearts": cv2.imread(f"{self.template_path}/hearts_template.png", 0),
            "diamonds": cv2.imread(f"{self.template_path}/diamonds_template.png", 0),
            "clubs": cv2.imread(f"{self.template_path}/clubs_template.png", 0),
            "spades": cv2.imread(f"{self.template_path}/spades_template.png", 0)
        }
    
    def get_card_features(self, card_element):
        """
        進階的卡牌特徵提取
        
        Args:
            card_element: 卡牌圖片元素
            
        Returns:
            dict: 包含卡牌特徵的字典
        """
        # 使用父類方法獲取基本特徵
        features = super().get_card_features(card_element)
        
        # 轉換為灰度圖進行模板匹配
        gray = cv2.cvtColor(features["image"], cv2.COLOR_BGR2GRAY)
        
        # 使用模板匹配檢測花色
        best_suit = None
        best_score = float('-inf')
        
        for suit, template in self.suit_templates.items():
            # 模板匹配
            result = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(result)
            
            if max_val > best_score:
                best_score = max_val
                best_suit = suit
        
        # 添加花色到特徵
        features["suit"] = best_suit
        
        # 卡牌點數檢測可以在這裡添加
        # 這需要 OCR 或更複雜的圖像處理
        
        return features
    
    def match_cards(self):
        """
        基於進階特徵匹配卡牌
        
        Returns:
            list: 匹配的卡牌列表
        """
        area_a_cards, area_b_cards = self.get_card_images()
        
        template_cards = []
        for card in area_a_cards:
            template_cards.append(self.get_card_features(card))
        
        option_cards = []
        for i, card in enumerate(area_b_cards):
            features = self.get_card_features(card)
            features["index"] = i
            option_cards.append(features)
        
        matches = []
        for template in template_cards:
            for option in option_cards:
                # 匹配顏色和花色
                if (template["color"] == option["color"] and 
                    template["suit"] == option["suit"]):
                    matches.append(option)
                    break
        
        return matches 