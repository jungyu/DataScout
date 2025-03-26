#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union

from selenium import webdriver

from ...utils.logger import setup_logger


class BaseCaptchaSolver(ABC):
    """
    驗證碼解決器基類，定義了所有驗證碼解決器的共同介面
    """
    
    def __init__(self, driver=None, config: Dict = None, log_level: int = logging.INFO):
        """
        初始化驗證碼解決器
        
        Args:
            driver: WebDriver實例
            config: 配置字典
            log_level: 日誌級別
        """
        self.driver = driver
        self.logger = setup_logger(f"{__name__}.{self.__class__.__name__}", log_level)
        self.config = config or {}
        
        # 是否使用外部服務
        self.use_external_service = self.config.get("use_external_service", False)
        
        # 外部服務配置
        self.service_config = self.config.get("service_config", {})
        
        # 模型配置
        self.model_config = self.config.get("model_config", {})
        
        # 重試設置
        self.max_retries = self.config.get("max_retries", 3)
        self.retry_delay = self.config.get("retry_delay", 2)
        
        # 樣本目錄
        self.sample_dir = self.config.get("sample_dir", os.path.join("captchas", self._get_captcha_type()))
        
        # 統計資料
        self.success_count = 0
        self.failure_count = 0
        
        # 初始化解決器特定的設置
        self._init_solver()
    
    def _init_solver(self):
        """
        初始化解決器特定的設置，
        子類可以覆蓋此方法以進行自定義初始化
        """
        pass
    
    def setup(self):
        """設置解決器，可由子類覆寫"""
        pass
    
    @abstractmethod
    def _get_captcha_type(self) -> str:
        """
        獲取驗證碼類型
        
        Returns:
            驗證碼類型字符串
        """
        pass
    
    @abstractmethod
    def detect(self) -> bool:
        """
        檢測頁面上是否存在此類型的驗證碼
        
        Returns:
            bool: 是否檢測到驗證碼
        """
        pass
    
    @abstractmethod
    def solve(self, driver: webdriver.Remote = None) -> bool:
        """
        解決驗證碼
        
        Args:
            driver: WebDriver實例
            
        Returns:
            是否成功解決
        """
        driver = driver or self.driver
        pass
    
    def report_result(self, success: bool):
        """
        報告驗證碼解決結果，用於統計和學習
        
        Args:
            success: 是否成功解決
        """
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1
        
        self.logger.info(
            f"驗證碼解決結果: {success}, 成功率: "
            f"{self.success_count/(self.success_count+self.failure_count):.2%}"
        )
    
    def _save_sample(self, driver: webdriver.Remote, sample_data: Dict = None) -> str:
        """
        保存驗證碼樣本
        
        Args:
            driver: WebDriver實例
            sample_data: 樣本數據
            
        Returns:
            樣本文件路徑
        """
        # 確保樣本目錄存在
        os.makedirs(self.sample_dir, exist_ok=True)
        
        # 生成樣本文件路徑
        timestamp = int(time.time())
        sample_path = os.path.join(self.sample_dir, f"{self._get_captcha_type()}_{timestamp}")
        
        try:
            # 保存樣本截圖
            captcha_element = self._locate_captcha_element(driver)
            if captcha_element:
                captcha_element.screenshot(f"{sample_path}.png")
                self.logger.debug(f"樣本截圖已保存: {sample_path}.png")
            
            # 保存樣本數據
            if sample_data:
                import json
                with open(f"{sample_path}.json", "w", encoding="utf-8") as f:
                    json.dump(sample_data, f, indent=2)
                self.logger.debug(f"樣本數據已保存: {sample_path}.json")
            
            return sample_path
        
        except Exception as e:
            self.logger.error(f"保存樣本失敗: {str(e)}")
            return ""
    
    def _locate_captcha_element(self, driver: webdriver.Remote) -> Optional[webdriver.remote.webelement.WebElement]:
        """
        定位驗證碼元素
        
        Args:
            driver: WebDriver實例
            
        Returns:
            驗證碼元素或None
        """
        # 此方法需要在子類中實現
        return None
    
    def _call_external_service(self, service_type: str, service_api: str, service_key: str, data: Dict) -> Dict:
        """
        調用外部驗證碼解決服務
        
        Args:
            service_type: 服務類型
            service_api: 服務API URL
            service_key: 服務API密鑰
            data: 請求數據
            
        Returns:
            響應數據
        """
        try:
            import requests
            
            # 根據服務類型設置請求
            if service_type == "2captcha":
                # 2Captcha API
                response = requests.post(f"{service_api}/in.php", data=data)
                response_data = response.json()
                
                if response_data.get("status") != 1:
                    self.logger.error(f"2Captcha API錯誤: {response_data.get('request')}")
                    return {"success": False, "error": response_data.get("request")}
                
                # 獲取請求ID
                request_id = response_data.get("request")
                
                # 等待結果
                for _ in range(30):  # 最多等待30次，每次5秒
                    time.sleep(5)
                    
                    # 查詢結果
                    result_params = {
                        "key": service_key,
                        "action": "get",
                        "id": request_id,
                        "json": 1
                    }
                    
                    result_response = requests.get(f"{service_api}/res.php", params=result_params)
                    result_data = result_response.json()
                    
                    if result_data.get("status") == 1:
                        return {"success": True, "result": result_data.get("request")}
                    
                    if result_data.get("request") != "CAPCHA_NOT_READY":
                        return {"success": False, "error": result_data.get("request")}
                
                return {"success": False, "error": "Timeout waiting for result"}
            
            elif service_type == "anti-captcha":
                # Anti-Captcha API
                # 實現Anti-Captcha的API調用邏輯
                self.logger.warning("Anti-Captcha服務尚未實現")
                return {"success": False, "error": "Anti-Captcha service not implemented"}
            
            else:
                self.logger.error(f"不支持的服務類型: {service_type}")
                return {"success": False, "error": f"Unsupported service type: {service_type}"}
        
        except Exception as e:
            self.logger.error(f"調用外部服務失敗: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _load_model(self, model_path: str) -> Any:
        """
        載入驗證碼識別模型
        
        Args:
            model_path: 模型文件路徑
            
        Returns:
            載入的模型
        """
        try:
            # 根據模型類型載入
            model_type = self.model_config.get("type", "")
            
            if model_type == "tensorflow":
                try:
                    import tensorflow as tf
                    return tf.keras.models.load_model(model_path)
                except ImportError:
                    self.logger.error("未安裝TensorFlow，無法載入模型")
                    return None
            
            elif model_type == "pytorch":
                try:
                    import torch
                    return torch.load(model_path)
                except ImportError:
                    self.logger.error("未安裝PyTorch，無法載入模型")
                    return None
            
            elif model_type == "opencv":
                try:
                    import cv2
                    import pickle
                    with open(model_path, "rb") as f:
                        return pickle.load(f)
                except ImportError:
                    self.logger.error("未安裝OpenCV，無法載入模型")
                    return None
            
            else:
                self.logger.error(f"不支持的模型類型: {model_type}")
                return None
        
        except Exception as e:
            self.logger.error(f"載入模型失敗: {str(e)}")
            return None
    
    def _preprocess_image(self, image_path: str) -> Any:
        """
        預處理驗證碼圖片
        
        Args:
            image_path: 圖片文件路徑
            
        Returns:
            預處理後的圖片
        """
        try:
            # 根據模型類型進行預處理
            model_type = self.model_config.get("type", "")
            
            if model_type == "tensorflow" or model_type == "pytorch":
                try:
                    import numpy as np
                    from PIL import Image
                    
                    # 讀取圖片
                    img = Image.open(image_path)
                    
                    # 調整大小
                    target_size = self.model_config.get("image_size", (100, 40))
                    img = img.resize(target_size)
                    
                    # 轉換為灰度圖
                    if self.model_config.get("grayscale", True):
                        img = img.convert("L")
                    
                    # 轉換為numpy數組
                    img_array = np.array(img)
                    
                    # 正規化
                    if self.model_config.get("normalize", True):
                        img_array = img_array / 255.0
                    
                    # 擴展維度
                    if model_type == "tensorflow":
                        img_array = np.expand_dims(img_array, axis=0)
                        if self.model_config.get("grayscale", True):
                            img_array = np.expand_dims(img_array, axis=-1)
                    
                    return img_array
                
                except ImportError as e:
                    self.logger.error(f"缺少必要的庫: {str(e)}")
                    return None
            
            elif model_type == "opencv":
                try:
                    import cv2
                    import numpy as np
                    
                    # 讀取圖片
                    img = cv2.imread(image_path)
                    
                    # 轉換為灰度圖
                    if self.model_config.get("grayscale", True):
                        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    
                    # 調整大小
                    target_size = self.model_config.get("image_size", (100, 40))
                    img = cv2.resize(img, target_size)
                    
                    # 閾值處理
                    if self.model_config.get("threshold", True):
                        _, img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
                    
                    return img
                
                except ImportError:
                    self.logger.error("未安裝OpenCV，無法預處理圖片")
                    return None
            
            else:
                self.logger.error(f"不支持的模型類型: {model_type}")
                return None
        
        except Exception as e:
            self.logger.error(f"預處理圖片失敗: {str(e)}")
            return None
    
    def _predict(self, model: Any, preprocessed_image: Any) -> str:
        """
        使用模型預測驗證碼
        
        Args:
            model: 載入的模型
            preprocessed_image: 預處理後的圖片
            
        Returns:
            預測的驗證碼文本
        """
        try:
            # 根據模型類型進行預測
            model_type = self.model_config.get("type", "")
            
            if model_type == "tensorflow":
                # TensorFlow模型預測
                predictions = model.predict(preprocessed_image)
                return self._decode_predictions(predictions)
            
            elif model_type == "pytorch":
                # PyTorch模型預測
                import torch
                with torch.no_grad():
                    model.eval()
                    tensor_image = torch.FloatTensor(preprocessed_image)
                    predictions = model(tensor_image)
                    return self._decode_predictions(predictions.numpy())
            
            elif model_type == "opencv":
                # OpenCV模型預測
                import cv2
                result = model.predict(preprocessed_image)
                return str(result)
            
            else:
                self.logger.error(f"不支持的模型類型: {model_type}")
                return ""
        
        except Exception as e:
            self.logger.error(f"模型預測失敗: {str(e)}")
            return ""
    
    def _decode_predictions(self, predictions: Any) -> str:
        """
        解碼模型預測結果為文本
        
        Args:
            predictions: 模型的預測結果
            
        Returns:
            解碼後的驗證碼文本
        """
        # 此方法需要根據具體的模型輸出格式來實現
        # 對於文本驗證碼，通常是將每個字符的預測結果合併
        # 以下是一個簡單的示例，實際情況可能更複雜
        
        try:
            import numpy as np
            
            # 獲取字符集
            charset = self.model_config.get("charset", "0123456789abcdefghijklmnopqrstuvwxyz")
            charset = list(charset)
            
            # 驗證碼長度
            captcha_length = self.model_config.get("captcha_length", 4)
            
            # 解碼預測結果
            result = []
            
            # 如果預測結果是二維數組，每行對應一個字符
            if len(predictions.shape) == 2 and predictions.shape[0] == captcha_length:
                for i in range(captcha_length):
                    char_idx = np.argmax(predictions[i])
                    if char_idx < len(charset):
                        result.append(charset[char_idx])
            
            # 如果預測結果是三維數組，第一維是batch，第二維是字符位置
            elif len(predictions.shape) == 3 and predictions.shape[1] == captcha_length:
                for i in range(captcha_length):
                    char_idx = np.argmax(predictions[0][i])
                    if char_idx < len(charset):
                        result.append(charset[char_idx])
            
            # 如果預測結果是其他格式，需要在子類中實現特定的解碼邏輯
            else:
                self.logger.warning(f"未知的預測結果格式: {predictions.shape}")
                return ""
            
            return "".join(result)
        
        except Exception as e:
            self.logger.error(f"解碼預測結果失敗: {str(e)}")
            return ""
    
    def save_sample(self, data: Any, success: bool = False):
        """
        保存驗證碼樣本以供將來分析或訓練
        
        Args:
            data: 驗證碼數據（通常是圖像）
            success: 樣本是否為成功解決的樣本
        """
        if not self.config.get('save_samples', False):
            return
            
        import os
        import time
        
        # 決定保存路徑
        base_dir = self.config.get('sample_dir', '../captchas')
        solver_type = self.__class__.__name__.lower().replace('solver', '')
        status = 'success' if success else 'failed'
        
        # 創建目錄
        save_dir = os.path.join(base_dir, solver_type, status)
        os.makedirs(save_dir, exist_ok=True)
        
        # 保存樣本
        filename = f"{int(time.time())}_{hash(str(data))}.png"
        file_path = os.path.join(save_dir, filename)
        
        try:
            if hasattr(data, 'save'):  # PIL Image
                data.save(file_path)
            elif isinstance(data, bytes):  # Bytes data
                with open(file_path, 'wb') as f:
                    f.write(data)
            else:
                self.logger.warning(f"無法保存未知格式的驗證碼樣本: {type(data)}")
        except Exception as e:
            self.logger.error(f"保存驗證碼樣本失敗: {str(e)}")