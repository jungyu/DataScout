"""
旋轉驗證碼解決器 (Rotate CAPTCHA Solver)
Copyright (c) 2024 Aaron-Yu, Claude AI
Author: Aaron-Yu <jungyuyu@gmail.com>
License: MIT License
版本: 1.0.0
"""

import time
import random
import logging
import math
import io
import base64
import numpy as np
import cv2
from PIL import Image
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from .base_solver import BaseSolver


class RotateSolver(BaseSolver):
    """
    旋轉驗證碼解決器，處理需要將圖像旋轉到正確方向的驗證碼
    """
    
    def __init__(self, driver, config=None):
        """
        初始化旋轉驗證碼解決器
        
        Args:
            driver: Selenium WebDriver 實例
            config (dict): 配置字典，可包含以下選項：
                - rotation_detection_method (str): 旋轉檢測方法，如 'edge', 'horizon', 'reference'
                - max_attempts (int): 最大嘗試次數
                - rotation_step (int): 每次旋轉的角度步長
                - external_api (dict): 外部 API 配置
                - simulation (dict): 行為模擬配置
        """
        super().__init__(driver, config)
        self.logger = logging.getLogger(__name__)
        
        # 預設配置
        default_config = {
            "rotation_detection_method": "edge",  # 'edge', 'horizon', 'reference', 'api'
            "max_attempts": 5,
            "rotation_step": 10,  # 每次嘗試旋轉 10 度
            "model_path": None,
            "external_api": None,
            "simulation": {
                "realistic_movement": True,
                "movement_speed": 2,  # 1-10，10 最快
                "natural_rotation": True  # 模擬自然旋轉
            }
        }
        
        # 合併配置
        self.config = {**default_config, **(config or {})}
    
    def solve(self, captcha_element=None, frame_element=None, options=None):
        """
        解決旋轉驗證碼
        
        Args:
            captcha_element: 驗證碼圖像元素
            frame_element: 包含驗證碼的 iframe 元素 (可選)
            options (dict): 其他解決選項，可包含：
                - slider_element: 旋轉滑塊元素
                - confirm_button: 確認按鈕元素
                - instruction_text: 包含指令的元素
                - target_object: 目標物件，需要正確方向的物件
                
        Returns:
            bool: 是否成功解決驗證碼
        """
        if not captcha_element:
            self.logger.error("未提供驗證碼元素")
            return False
            
        # 切換到 iframe (如果提供)
        if frame_element:
            self.driver.switch_to.frame(frame_element)
        
        try:
            # 合併解決選項
            solve_options = {
                "max_attempts": self.config["max_attempts"]
            }
            if options:
                solve_options.update(options)
            
            # 獲取旋轉滑塊元素
            slider_element = solve_options.get("slider_element")
            if not slider_element:
                # 嘗試尋找常見的旋轉滑塊
                try:
                    slider_element = self.driver.find_element(By.CSS_SELECTOR, 
                                                             ".captcha-rotation-slider, .rotate-slider, .slider")
                except NoSuchElementException:
                    self.logger.error("無法找到旋轉滑塊元素")
                    return False
            
            # 確認按鈕 (如果需要)
            confirm_button = solve_options.get("confirm_button")
            
            # 獲取驗證碼圖像
            image = self._get_captcha_image(captcha_element)
            if image is None:
                return False
            
            # 獲取目標指令或分析目標物件
            target_object = solve_options.get("target_object")
            instruction_text = None
            
            if "instruction_text" in solve_options:
                instruction_elem = solve_options["instruction_text"]
                if instruction_elem:
                    instruction_text = instruction_elem.text
            
            # 檢測需要的旋轉角度
            rotation_angle = self._detect_rotation_angle(
                image, 
                target_object=target_object,
                instruction_text=instruction_text
            )
            
            if rotation_angle is None:
                self.logger.warning("無法檢測需要的旋轉角度")
                return False
            
            self.logger.info(f"檢測到需要旋轉的角度: {rotation_angle}°")
            
            # 執行旋轉操作
            success = self._rotate_image(slider_element, rotation_angle)
            
            # 點擊確認按鈕 (如果提供)
            if success and confirm_button:
                time.sleep(random.uniform(0.5, 1.0))
                confirm_button.click()
            
            return success
                
        except Exception as e:
            self.logger.error(f"解決旋轉驗證碼時發生錯誤: {e}", exc_info=True)
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
    
    def _detect_rotation_angle(self, image, target_object=None, instruction_text=None):
        """
        檢測圖像需要旋轉的角度
        
        Args:
            image: 圖像數據
            target_object: 目標物件名稱或描述
            instruction_text: 包含指令的文字
            
        Returns:
            float: 需要旋轉的角度，失敗返回 None
        """
        method = self.config["rotation_detection_method"]
        
        # 根據方法選擇適當的角度檢測策略
        if method == "edge":
            return self._detect_by_edge_detection(image)
        elif method == "horizon":
            return self._detect_by_horizon_line(image)
        elif method == "reference":
            return self._detect_by_reference_object(image, target_object, instruction_text)
        elif method == "api":
            return self._detect_by_external_api(image, target_object, instruction_text)
        else:
            self.logger.warning(f"未知的旋轉檢測方法: {method}")
            # 嘗試使用基本方法作為後備
            return self._detect_by_edge_detection(image)
    
    def _detect_by_edge_detection(self, image):
        """通過邊緣檢測估計旋轉角度"""
        try:
            # 轉換為灰度圖
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 使用 Canny 邊緣檢測
            edges = cv2.Canny(gray, 50, 150, apertureSize=3)
            
            # 使用 Hough 變換檢測直線
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=100, maxLineGap=10)
            
            if lines is None or len(lines) == 0:
                return None
            
            # 計算線條角度
            angles = []
            for line in lines:
                x1, y1, x2, y2 = line[0]
                # 避免除以零
                if x2 - x1 == 0:
                    continue
                angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
                # 規範化角度到 0-90 度範圍
                angle = angle % 180
                if angle > 90:
                    angle = 180 - angle
                angles.append(angle)
            
            if not angles:
                return None
            
            # 找出最常見的角度
            from collections import Counter
            angle_counts = Counter([round(a / 10) * 10 for a in angles])
            most_common_angle = angle_counts.most_common(1)[0][0]
            
            # 計算需要旋轉的角度
            # 假設正確方向應該是水平(0度)或垂直(90度)
            if most_common_angle < 45:
                rotation_needed = -most_common_angle
            else:
                rotation_needed = 90 - most_common_angle
                
            return rotation_needed
            
        except Exception as e:
            self.logger.error(f"邊緣檢測旋轉角度失敗: {e}")
            return None
    
    def _detect_by_horizon_line(self, image):
        """通過地平線或水平特徵檢測旋轉角度"""
        try:
            # 轉換為灰度圖
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 使用自適應閾值處理
            binary = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # 檢查水平線特徵
            horizontal_sum = np.sum(binary, axis=1)
            
            # 使用霍夫變換尋找可能的水平線
            # 這裡的實現可以根據具體需求優化
            
            # 由於完整實現較為複雜，這裡返回一個模擬角度
            # 實際應用中需更精確的計算
            return random.uniform(-30, 30)
            
        except Exception as e:
            self.logger.error(f"地平線檢測角度失敗: {e}")
            return None
    
    def _detect_by_reference_object(self, image, target_object, instruction_text):
        """通過參考物件檢測旋轉角度"""
        try:
            # 根據指令文字確定目標物件
            if instruction_text and not target_object:
                # 簡單的關鍵詞匹配示例
                keywords = {
                    "車": "car", "汽車": "car", "轎車": "car",
                    "樹": "tree", "植物": "plant",
                    "人": "person", "人物": "person",
                    "建築": "building", "房屋": "house",
                    "杯子": "cup", "水杯": "cup"
                }
                
                for keyword, obj in keywords.items():
                    if keyword in instruction_text:
                        target_object = obj
                        break
            
            if not target_object:
                self.logger.warning("無法確定目標物件")
                return None
            
            # 載入自定義模型或使用預訓練模型檢測物件
            # 這裡僅為示例，實際應用中需要具體實現
            
            # 根據物件的方向特徵確定旋轉角度
            # 比如車輛通常是水平的，人站立時是垂直的
            
            # 由於完整實現較為複雜，這裡返回一個模擬角度
            # 實際應用中需更精確的計算
            return random.uniform(-45, 45)
            
        except Exception as e:
            self.logger.error(f"參考物件檢測角度失敗: {e}")
            return None
    
    def _detect_by_external_api(self, image, target_object, instruction_text):
        """使用外部 API 檢測旋轉角度"""
        api_config = self.config.get("external_api")
        if not api_config or not api_config.get("url"):
            return None
            
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
            payload = {}
            if target_object:
                payload["target_object"] = target_object
            if instruction_text:
                payload["instruction_text"] = instruction_text
                
            files = {
                "image": ("captcha.png", img_bytes, "image/png")
            }
            
            # 發送請求
            response = requests.post(
                api_config["url"], 
                data=payload, 
                files=files, 
                headers=api_config.get("headers", {})
            )
            
            if response.status_code == 200:
                result = response.json()
                if "rotation_angle" in result:
                    return float(result["rotation_angle"])
            
            self.logger.warning(f"API 返回非成功狀態碼: {response.status_code}")
            return None
            
        except Exception as e:
            self.logger.error(f"使用外部 API 檢測角度失敗: {e}")
            return None
    
    def _rotate_image(self, slider_element, target_angle):
        """
        使用滑塊旋轉圖像
        
        Args:
            slider_element: 滑塊元素
            target_angle: 目標旋轉角度
            
        Returns:
            bool: 是否成功旋轉
        """
        try:
            # 獲取滑塊初始位置
            slider_location = slider_element.location
            
            # 創建 ActionChains
            actions = ActionChains(self.driver)
            actions.move_to_element(slider_element)
            actions.click_and_hold()
            actions.perform()
            
            # 等待短暫時間
            time.sleep(random.uniform(0.2, 0.5))
            
            # 模擬旋轉動作
            if self.config["simulation"]["natural_rotation"]:
                # 使用多次小幅度旋轉模擬自然旋轉
                steps = abs(int(target_angle / self.config["rotation_step"]))
                steps = max(3, min(steps, 10))  # 至少 3 步，最多 10 步
                
                angle_per_step = target_angle / steps
                current_angle = 0
                
                for i in range(steps):
                    current_angle += angle_per_step
                    # 計算當前角度的 x, y 坐標
                    radius = 50  # 假設滑塊軌道半徑為 50px
                    x_offset = radius * math.sin(math.radians(current_angle))
                    y_offset = -radius * (1 - math.cos(math.radians(current_angle)))
                    
                    actions.move_by_offset(x_offset, y_offset)
                    actions.perform()
                    
                    # 添加隨機延遲
                    delay = 0.5 / self.config["simulation"]["movement_speed"]
                    time.sleep(random.uniform(delay * 0.8, delay * 1.2))
            else:
                # 直接旋轉到目標角度
                radius = 50  # 假設滑塊軌道半徑為 50px
                x_offset = radius * math.sin(math.radians(target_angle))
                y_offset = -radius * (1 - math.cos(math.radians(target_angle)))
                
                actions.move_by_offset(x_offset, y_offset)
                actions.perform()
            
            # 鬆開滑塊
            time.sleep(random.uniform(0.3, 0.7))
            actions.release()
            actions.perform()
            
            return True
            
        except Exception as e:
            self.logger.error(f"旋轉圖像失敗: {e}")
            return False