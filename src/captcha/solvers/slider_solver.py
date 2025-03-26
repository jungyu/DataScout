from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import numpy as np
import cv2
from PIL import Image
from io import BytesIO
import base64
from typing import Optional, List, Tuple, Dict, Any

from .base_solver import BaseCaptchaSolver

class SliderCaptchaSolver(BaseCaptchaSolver):
    """滑塊驗證碼解決器"""
    
    def setup(self):
        """設置滑塊驗證碼解決器參數"""
        # 移動策略
        self.move_strategy = self.config.get('move_strategy', 'simulate_human')
        
        # 軌跡生成參數
        self.track_config = self.config.get('track_generation', {
            'offset_start': {'min': 20, 'max': 50},
            'move_time': {'min': 800, 'max': 2000},
            'steps': {'min': 20, 'max': 40},
            'early_slow_down': True,
            'slow_down_threshold': 0.7
        })
        
        # 模擬參數
        self.simulation_config = self.config.get('simulation', {
            'track_deviation': 0.2,
            'release_delay': {'min': 50, 'max': 200},
            'acceleration': {'min': 200, 'max': 1500},
            'deceleration': {'min': 200, 'max': 1500},
            'jitter': {'min': 0, 'max': 2},
            'mouse_down_delay': {'min': 50, 'max': 150}
        })
        
        # 圖像處理參數
        self.image_processing = self.config.get('image_processing', {
            'enabled': True,
            'edge_detection': True,
            'template_matching': True,
            'diff_threshold': 0.3
        })
    
    def detect(self) -> bool:
        """檢測頁面上是否存在滑塊驗證碼"""
        try:
            # 常見的滑塊驗證碼選擇器
            slider_selectors = [
                ".slider-captcha",
                ".sliderContainer",
                ".yidun_slider",
                ".geetest_slider_button",
                "div[class*='slider']",
                "div[class*='captcha'] .drag",
                ".captcha-puzzle"
            ]
            
            # XPath選擇器
            xpath_selectors = [
                "//div[contains(@class, 'slider') and contains(@class, 'captcha')]",
                "//div[contains(text(), '滑動驗證') or contains(text(), '拖動滑塊') or contains(text(), 'Slide to verify')]"
            ]
            
            # 檢查CSS選擇器
            for selector in slider_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    self.slider_element = elements[0]
                    
                    # 識別滑塊類型
                    self._identify_slider_type()
                    
                    return True
            
            # 檢查XPath選擇器
            for selector in xpath_selectors:
                elements = self.driver.find_elements(By.XPATH, selector)
                if elements:
                    self.slider_element = elements[0]
                    
                    # 識別滑塊類型
                    self._identify_slider_type()
                    
                    return True
            
            # 找不到滑塊驗證碼
            return False
            
        except Exception as e:
            self.logger.error(f"檢測滑塊驗證碼時出錯: {str(e)}")
            return False
    
    def solve(self) -> bool:
        """解決滑塊驗證碼"""
        try:
            # 根據滑塊類型選擇不同的解決方法
            if self.slider_type == "geetest":
                return self._solve_geetest()
            elif self.slider_type == "yidun":
                return self._solve_yidun()
            elif self.slider_type == "tencent":
                return self._solve_tencent()
            elif self.slider_type == "hcaptcha":
                return self._solve_hcaptcha()
            else:
                return self._solve_generic()
                
        except Exception as e:
            self.logger.error(f"解決滑塊驗證碼時出錯: {str(e)}")
            self.report_result(False)
            return False
    
    def _identify_slider_type(self):
        """識別滑塊驗證碼類型"""
        # 常見的滑塊驗證碼提供商
        self.slider_type = "unknown"
        
        try:
            # 檢查GeeTest
            geetest_elements = self.driver.find_elements(By.CSS_SELECTOR, ".geetest_slider, .geetest_panel")
            if geetest_elements:
                self.slider_type = "geetest"
                return
                
            # 檢查易盾
            yidun_elements = self.driver.find_elements(By.CSS_SELECTOR, ".yidun_slider, .yidun_panel")
            if yidun_elements:
                self.slider_type = "yidun"
                return
                
            # 檢查騰訊驗證碼
            tencent_elements = self.driver.find_elements(By.CSS_SELECTOR, ".tc-slider, .tc-captcha-container")
            if tencent_elements:
                self.slider_type = "tencent"
                return
                
            # 檢查hCaptcha
            hcaptcha_elements = self.driver.find_elements(By.CSS_SELECTOR, ".hcaptcha-box")
            if hcaptcha_elements:
                self.slider_type = "hcaptcha"
                return
                
            # 通用滑塊檢測
            self.slider_type = "generic"
            
        except Exception as e:
            self.logger.error(f"識別滑塊類型時出錯: {str(e)}")
            self.slider_type = "unknown"
    
    def _solve_generic(self) -> bool:
        """解決通用滑塊驗證碼"""
        try:
            # 找到滑塊和背景
            slider_button = self._find_slider_button()
            if slider_button is None:
                self.logger.error("找不到滑塊按鈕")
                return False
            
            # 計算滑動距離
            distance = self._calculate_slide_distance()
            if distance <= 0:
                self.logger.error(f"計算的滑動距離無效: {distance}px")
                return False
            
            # 生成滑動軌跡
            tracks = self._generate_slide_tracks(distance)
            
            # 執行滑動
            success = self._perform_slide(slider_button, tracks)
            
            # 等待驗證結果
            time.sleep(1)
            
            # 檢查是否成功
            verification_success = self._check_verification_success()
            
            self.report_result(verification_success)
            return verification_success
            
        except Exception as e:
            self.logger.error(f"解決通用滑塊驗證碼時出錯: {str(e)}")
            self.report_result(False)
            return False
    
    def _find_slider_button(self):
        """找到滑塊按鈕元素"""
        try:
            # 常見的滑塊按鈕選擇器
            button_selectors = [
                ".slider-btn",
                ".slider-button",
                ".sliderBtn",
                ".geetest_slider_button",
                ".yidun_slider",
                ".drag",
                "div[class*='slider'] > span",
                "div[class*='slider'] > div",
                "div[class*='captcha'] .drag",
                "div[class*='handle']"
            ]
            
            for selector in button_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    return elements[0]
            
            # 如果找不到按鈕，嘗試用滑塊容器來代替
            return self.slider_element
            
        except Exception as e:
            self.logger.error(f"找尋滑塊按鈕時出錯: {str(e)}")
            return None
    
    def _calculate_slide_distance(self) -> int:
        """計算滑動距離"""
        if not self.image_processing.get('enabled', True):
            # 如果未啟用圖像處理，返回估計值
            return random.randint(150, 250)
        
        try:
            # 獲取背景圖和滑塊圖
            background, slider = self._get_captcha_images()
            
            if background is None or slider is None:
                self.logger.warning("無法獲取圖像，使用預設距離")
                return random.randint(150, 250)
            
            # 保存樣本
            self.save_sample(background, False)
            
            # 計算滑動距離
            distance = 0
            
            # 嘗試模板匹配
            if self.image_processing.get('template_matching', True):
                distance = self._calculate_distance_by_template_matching(background, slider)
            
            # 如果模板匹配失敗，嘗試邊緣檢測
            if distance <= 0 and self.image_processing.get('edge_detection', True):
                distance = self._calculate_distance_by_edge_detection(background)
            
            # 如果以上方法都失敗，使用預設值
            if distance <= 0:
                self.logger.warning("計算滑動距離失敗，使用預設距離")
                distance = random.randint(150, 250)
            
            return distance
            
        except Exception as e:
            self.logger.error(f"計算滑動距離時出錯: {str(e)}")
            return random.randint(150, 250)
    
    def _get_captcha_images(self) -> Tuple[Optional[Image.Image], Optional[Image.Image]]:
        """獲取驗證碼背景圖和滑塊圖"""
        try:
            # 常見的背景圖選擇器
            background_selectors = [
                ".captcha-bg",
                ".sliderContainer .bg",
                ".yidun_bg-img",
                ".geetest_canvas_bg",
                "div[class*='captcha'] .bg-img",
                "canvas[class*='bg']"
            ]
            
            # 常見的滑塊圖選擇器
            slider_selectors = [
                ".captcha-puzzle",
                ".sliderContainer .block",
                ".yidun_jigsaw",
                ".geetest_canvas_slice",
                "div[class*='captcha'] .puzzle-img",
                "canvas[class*='slice']"
            ]
            
            # 獲取背景圖
            background_img = None
            for selector in background_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    # 嘗試獲取背景圖
                    background_img = self._get_image_from_element(elements[0])
                    if background_img:
                        break
            
            # 獲取滑塊圖
            slider_img = None
            for selector in slider_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    # 嘗試獲取滑塊圖
                    slider_img = self._get_image_from_element(elements[0])
                    if slider_img:
                        break
            
            return background_img, slider_img
            
        except Exception as e:
            self.logger.error(f"獲取驗證碼圖像時出錯: {str(e)}")
            return None, None
    
    def _get_image_from_element(self, element) -> Optional[Image.Image]:
        """從元素中獲取圖像"""
        try:
            # 嘗試獲取背景圖URL
            background_url = element.get_attribute('src')
            
            if background_url:
                # 如果是Base64編碼
                if background_url.startswith('data:image'):
                    img_data = background_url.split(',')[1]
                    img = Image.open(BytesIO(base64.b64decode(img_data)))
                    return img
                
                # 如果是URL
                if background_url.startswith('http'):
                    import requests
                    response = requests.get(background_url)
                    img = Image.open(BytesIO(response.content))
                    return img
            
            # 嘗試截圖
            screenshot = element.screenshot_as_png
            if screenshot:
                return Image.open(BytesIO(screenshot))
            
            return None
            
        except Exception as e:
            self.logger.error(f"從元素獲取圖像時出錯: {str(e)}")
            return None
    
    def _calculate_distance_by_template_matching(self, background: Image.Image, slider: Image.Image) -> int:
        """使用模板匹配計算滑動距離"""
        try:
            # 轉換為OpenCV格式
            bg_array = np.array(background)
            bg_cv = cv2.cvtColor(bg_array, cv2.COLOR_RGB2BGR)
            
            slider_array = np.array(slider)
            slider_cv = cv2.cvtColor(slider_array, cv2.COLOR_RGB2BGR)
            
            # 轉為灰度
            bg_gray = cv2.cvtColor(bg_cv, cv2.COLOR_BGR2GRAY)
            slider_gray = cv2.cvtColor(slider_cv, cv2.COLOR_BGR2GRAY)
            
            # 模板匹配
            result = cv2.matchTemplate(bg_gray, slider_gray, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val < self.image_processing.get('diff_threshold', 0.3):
                self.logger.warning(f"模板匹配置信度過低: {max_val:.2f}")
                return 0
            
            # X座標就是滑動距離
            return max_loc[0]
            
        except Exception as e:
            self.logger.error(f"使用模板匹配計算距離時出錯: {str(e)}")
            return 0
    
    def _calculate_distance_by_edge_detection(self, background: Image.Image) -> int:
        """使用邊緣檢測計算滑動距離"""
        try:
            # 轉換為OpenCV格式
            bg_array = np.array(background)
            bg_cv = cv2.cvtColor(bg_array, cv2.COLOR_RGB2BGR)
            
            # 轉為灰度
            bg_gray = cv2.cvtColor(bg_cv, cv2.COLOR_BGR2GRAY)
            
            # 邊緣檢測
            edges = cv2.Canny(bg_gray, 100, 200)
            
            # 尋找邊緣
            columns = []
            for i in range(edges.shape[1]):
                column = edges[:, i]
                if np.count_nonzero(column) > 10:  # 至少10個邊緣點
                    columns.append(i)
            
            # 尋找異常邊緣列
            if not columns:
                return 0
                
            # 分析邊緣點密度
            density = []
            for i in columns:
                column = edges[:, i]
                density.append(np.count_nonzero(column))
            
            # 尋找密度異常點
            mean_density = np.mean(density)
            std_density = np.std(density)
            
            outliers = []
            for i, d in enumerate(density):
                if d > mean_density + 1.5 * std_density:
                    outliers.append(columns[i])
            
            if not outliers:
                return 0
                
            # 返回第一個異常點
            return outliers[0]
            
        except Exception as e:
            self.logger.error(f"使用邊緣檢測計算距離時出錯: {str(e)}")
            return 0