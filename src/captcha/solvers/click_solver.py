"""
點擊驗證碼解決器 (Click CAPTCHA Solver)
Copyright (c) 2024 Aaron-Yu, Claude AI
Author: Aaron-Yu <jungyuyu@gmail.com>
License: MIT License
版本: 1.0.0
"""

import time
import random
import logging
import cv2
import numpy as np
from PIL import Image
import io
import base64
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import ElementNotInteractableException, TimeoutException

from .base_solver import BaseSolver


class ClickSolver(BaseSolver):
    """
    點擊式驗證碼解決器，支援圖像識別和點擊指定物件的驗證碼處理
    """
    
    def __init__(self, driver, config=None):
        """
        初始化點擊式驗證碼解決器
        
        Args:
            driver: Selenium WebDriver 實例
            config (dict): 配置字典，可包含以下選項：
                - object_types (list): 要識別的物件類型列表，如 ["car", "traffic_light"]
                - confidence_threshold (float): 對象檢測置信度閾值 (0-1)
                - detection_model (str): 對象檢測模型路徑
                - external_api (dict): 外部 API 配置
                - simulation (dict): 行為模擬配置
        """
        super().__init__(driver, config)
        self.logger = logging.getLogger(__name__)
        
        # 預設配置
        default_config = {
            "object_types": ["car", "traffic_light", "crosswalk", "store_front", "bicycle"],
            "confidence_threshold": 0.7,
            "max_attempts": 3,
            "wait_between_clicks": [0.5, 1.5],
            "simulation": {
                "realistic_movement": True,
                "delay_before_click": [0.2, 0.8]
            }
        }
        
        # 合併配置
        self.config = {**default_config, **(config or {})}
        
        # 初始化對象檢測模型
        self.model = None
        if self.config.get("detection_model"):
            try:
                self._load_detection_model()
            except Exception as e:
                self.logger.warning(f"無法載入物件檢測模型: {e}")
    
    def _load_detection_model(self):
        """
        載入物件檢測模型，支援 OpenCV DNN 和自定義模型
        """
        model_path = self.config.get("detection_model")
        if not model_path:
            return
            
        # 這裡僅為示例，實際實現需要根據模型類型決定
        try:
            if model_path.endswith('.pb'):
                # TensorFlow 模型
                import tensorflow as tf
                self.model = tf.saved_model.load(model_path)
                self.logger.info("已成功載入 TensorFlow 物件檢測模型")
            elif model_path.endswith('.onnx'):
                # ONNX 模型
                self.model = cv2.dnn.readNetFromONNX(model_path)
                self.logger.info("已成功載入 ONNX 物件檢測模型")
            else:
                self.logger.warning(f"不支援的模型格式: {model_path}")
        except Exception as e:
            self.logger.error(f"載入物件檢測模型失敗: {e}")
            self.model = None
    
    def solve(self, captcha_element=None, frame_element=None, options=None):
        """
        解決點擊式驗證碼
        
        Args:
            captcha_element: 驗證碼圖像元素
            frame_element: 包含驗證碼的 iframe 元素 (可選)
            options (dict): 其他解決選項
            
        Returns:
            bool: 是否成功解決驗證碼
        """
        if not captcha_element:
            self.logger.error("未提供驗證碼元素")
            return False
            
        # 合併解決選項
        solve_options = {
            "max_attempts": self.config["max_attempts"],
            "object_types": self.config["object_types"]
        }
        if options:
            solve_options.update(options)
        
        # 切換到 iframe (如果提供)
        if frame_element:
            self.driver.switch_to.frame(frame_element)
        
        try:
            # 獲取驗證碼圖像
            image = self._get_captcha_image(captcha_element)
            if image is None:
                return False
                
            # 檢測要點擊的物件
            objects = self._detect_objects(image, 
                                          target_types=solve_options["object_types"],
                                          threshold=self.config["confidence_threshold"])
            
            if not objects:
                self.logger.warning("未檢測到任何目標物件")
                return False
                
            # 點擊檢測到的物件
            return self._click_objects(captcha_element, objects)
                
        except Exception as e:
            self.logger.error(f"解決點擊驗證碼時發生錯誤: {e}", exc_info=True)
            return False
        finally:
            # 切回主 frame
            if frame_element:
                self.driver.switch_to.default_content()
    
    def _get_captcha_image(self, element):
        """
        從元素獲取驗證碼圖像
        
        Args:
            element: 包含驗證碼圖像的元素
            
        Returns:
            numpy.ndarray: 圖像數組，失敗返回 None
        """
        try:
            # 嘗試獲取圖像 src
            if element.tag_name.lower() == 'img':
                # 直接從 img 元素獲取
                img_src = element.get_attribute('src')
                if img_src.startswith('data:image'):
                    # 解析 base64 圖像
                    img_data = base64.b64decode(img_src.split(',')[1])
                    img = Image.open(io.BytesIO(img_data))
                    return np.array(img)
                else:
                    # 網絡圖像，使用 OpenCV 下載
                    import urllib.request
                    resp = urllib.request.urlopen(img_src)
                    img = np.asarray(bytearray(resp.read()), dtype="uint8")
                    return cv2.imdecode(img, cv2.IMREAD_COLOR)
            else:
                # 截圖元素
                png = element.screenshot_as_png
                img = Image.open(io.BytesIO(png))
                return np.array(img)
        except Exception as e:
            self.logger.error(f"獲取驗證碼圖像失敗: {e}")
            return None
    
    def _detect_objects(self, image, target_types=None, threshold=0.7):
        """
        檢測圖像中的物件
        
        Args:
            image: 圖像數據
            target_types (list): 目標物件類型列表
            threshold (float): 置信度閾值
            
        Returns:
            list: 檢測到的物件列表，每個物件是 (x, y, w, h, confidence, class_id) 元組
        """
        objects = []
        
        # 如果有實現 AI 模型，使用模型檢測
        if self.model is not None:
            objects = self._detect_with_model(image, target_types, threshold)
        
        # 如果模型檢測失敗或未配置模型，嘗試使用外部 API
        if not objects and self.config.get("external_api"):
            objects = self._detect_with_external_api(image, target_types, threshold)
        
        # 如果仍然無法檢測，使用簡單的色彩和形狀檢測 (僅作備用方案)
        if not objects:
            objects = self._detect_with_basic_cv(image, target_types, threshold)
            
        return objects
    
    def _detect_with_model(self, image, target_types, threshold):
        """使用加載的模型檢測物件"""
        # 實際實現將依賴於所使用的模型類型
        # 這裡僅為示例框架
        try:
            # 簡單示例: 使用 YOLO 或類似模型檢測物件
            # 實際實現需要根據具體模型調整
            return []
        except Exception as e:
            self.logger.error(f"使用模型檢測物件失敗: {e}")
            return []
    
    def _detect_with_external_api(self, image, target_types, threshold):
        """使用外部 API 檢測物件"""
        api_config = self.config.get("external_api", {})
        if not api_config.get("url"):
            return []
            
        try:
            # 將圖像發送到 API
            import requests
            from io import BytesIO
            
            # 轉換圖像為 bytes
            img = Image.fromarray(image)
            buf = BytesIO()
            img.save(buf, format="PNG")
            img_bytes = buf.getvalue()
            
            # 準備請求
            headers = api_config.get("headers", {})
            payload = {
                "threshold": threshold
            }
            if target_types:
                payload["target_types"] = target_types
                
            files = {
                "image": ("captcha.png", img_bytes, "image/png")
            }
            
            # 發送請求
            response = requests.post(
                api_config["url"], 
                data=payload, 
                files=files, 
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                if "objects" in result:
                    return result["objects"]
            
            self.logger.warning(f"API 返回非成功狀態碼: {response.status_code}")
            return []
            
        except Exception as e:
            self.logger.error(f"使用外部 API 檢測物件失敗: {e}")
            return []
    
    def _detect_with_basic_cv(self, image, target_types, threshold):
        """使用基本 OpenCV 方法檢測物件 (簡單備用方案)"""
        # 這只是一個簡單的示例，實際上需要更複雜的計算機視覺技術
        try:
            objects = []
            # 轉換為灰度圖
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            # 使用 Canny 邊緣檢測
            edges = cv2.Canny(gray, 50, 150)
            # 查找輪廓
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # 過濾小輪廓，只保留可能是目標的較大輪廓
            height, width = image.shape[:2]
            min_area = width * height * 0.01  # 至少是圖像的 1%
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > min_area:
                    x, y, w, h = cv2.boundingRect(contour)
                    # 隨機添加置信度和類別 ID (模擬)
                    confidence = random.uniform(0.6, 0.9)
                    if confidence > threshold:
                        class_id = 0  # 模擬類別 ID
                        objects.append((x, y, w, h, confidence, class_id))
                        
            return objects
            
        except Exception as e:
            self.logger.error(f"基本 CV 檢測失敗: {e}")
            return []
    
    def _click_objects(self, captcha_element, objects):
        """
        點擊檢測到的物件
        
        Args:
            captcha_element: 驗證碼元素
            objects: 檢測到的物件列表
            
        Returns:
            bool: 是否成功點擊所有物件
        """
        if not objects:
            return False
            
        try:
            # 獲取元素位置和大小
            location = captcha_element.location
            size = captcha_element.size
            
            # 創建 ActionChains
            actions = ActionChains(self.driver)
            
            # 點擊每個檢測到的物件
            clicked = 0
            for x, y, w, h, confidence, class_id in objects:
                # 計算點擊位置（物件中心）
                center_x = location['x'] + x + w/2
                center_y = location['y'] + y + h/2
                
                # 添加人性化延遲
                if self.config["simulation"]["realistic_movement"]:
                    # 模擬自然鼠標移動
                    actions.move_by_offset(center_x, center_y)
                    # 隨機延遲
                    delay_range = self.config["simulation"]["delay_before_click"]
                    time.sleep(random.uniform(delay_range[0], delay_range[1]))
                else:
                    # 直接移動到目標
                    actions.move_to_element_with_offset(captcha_element, x + w/2, y + h/2)
                
                # 點擊
                actions.click()
                actions.perform()
                
                clicked += 1
                
                # 等待短暫時間
                wait_time = random.uniform(
                    self.config["wait_between_clicks"][0],
                    self.config["wait_between_clicks"][1]
                )
                time.sleep(wait_time)
            
            self.logger.info(f"成功點擊了 {clicked} 個物件")
            return clicked > 0
                
        except ElementNotInteractableException:
            self.logger.warning("物件不可點擊")
            return False
        except Exception as e:
            self.logger.error(f"點擊物件時發生錯誤: {e}")
            return False