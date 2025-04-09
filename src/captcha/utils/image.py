#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
圖像處理工具模組

提供圖像處理相關功能，包括：
1. 圖像預處理
2. 圖像增強
3. 圖像分割
4. 文字識別
5. 圖像保存和轉換
"""

import os
import cv2
import numpy as np
from PIL import Image
import logging
from typing import Optional, Union, List, Tuple, Dict, Any
from dataclasses import dataclass

from .error import ImageProcessError, handle_error

@dataclass
class ImageProcessResult:
    """圖像處理結果數據類"""
    success: bool
    image: Optional[np.ndarray] = None
    text: Optional[str] = None
    segments: Optional[List[np.ndarray]] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class ImageProcessor:
    """圖像處理工具類"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        初始化圖像處理器
        
        Args:
            logger: 日誌記錄器
        """
        self.logger = logger or logging.getLogger(__name__)
        
    @handle_error(error_types=(ImageProcessError,))
    def preprocess_image(
        self,
        image: Union[str, bytes, np.ndarray, Image.Image]
    ) -> np.ndarray:
        """
        圖像預處理
        
        Args:
            image: 輸入圖像，可以是文件路徑、字節數據、numpy數組或PIL圖像
            
        Returns:
            預處理後的圖像
        """
        try:
            # 轉換為numpy數組
            if isinstance(image, str):
                img = cv2.imread(image)
            elif isinstance(image, bytes):
                img = cv2.imdecode(np.frombuffer(image, np.uint8), cv2.IMREAD_COLOR)
            elif isinstance(image, np.ndarray):
                img = image.copy()
            elif isinstance(image, Image.Image):
                img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            else:
                raise ImageProcessError("不支持的圖像格式")
                
            if img is None:
                raise ImageProcessError("無法讀取圖像")
                
            # 轉換為灰度圖
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # 高斯模糊
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # 自適應閾值
            thresh = cv2.adaptiveThreshold(
                blurred,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY_INV,
                11,
                2
            )
            
            return thresh
            
        except Exception as e:
            self.logger.error(f"圖像預處理失敗: {str(e)}")
            raise ImageProcessError(f"圖像預處理失敗: {str(e)}")
            
    @handle_error(error_types=(ImageProcessError,))
    def enhance_image(self, image: np.ndarray) -> np.ndarray:
        """
        圖像增強
        
        Args:
            image: 輸入圖像
            
        Returns:
            增強後的圖像
        """
        try:
            # 直方圖均衡化
            equalized = cv2.equalizeHist(image)
            
            # 中值濾波
            filtered = cv2.medianBlur(equalized, 3)
            
            # 形態學操作
            kernel = np.ones((3, 3), np.uint8)
            dilated = cv2.dilate(filtered, kernel, iterations=1)
            eroded = cv2.erode(dilated, kernel, iterations=1)
            
            return eroded
            
        except Exception as e:
            self.logger.error(f"圖像增強失敗: {str(e)}")
            raise ImageProcessError(f"圖像增強失敗: {str(e)}")
            
    @handle_error(error_types=(ImageProcessError,))
    def segment_image(self, image: np.ndarray) -> List[np.ndarray]:
        """
        圖像分割
        
        Args:
            image: 輸入圖像
            
        Returns:
            分割後的圖像片段列表
        """
        try:
            # 查找輪廓
            contours, _ = cv2.findContours(
                image,
                cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE
            )
            
            # 過濾小區域
            min_area = 100
            valid_contours = [
                cnt for cnt in contours
                if cv2.contourArea(cnt) > min_area
            ]
            
            # 提取字符區域
            segments = []
            for cnt in valid_contours:
                x, y, w, h = cv2.boundingRect(cnt)
                segment = image[y:y+h, x:x+w]
                segments.append(segment)
                
            # 按x坐標排序
            segments.sort(key=lambda s: cv2.boundingRect(s)[0])
            
            return segments
            
        except Exception as e:
            self.logger.error(f"圖像分割失敗: {str(e)}")
            raise ImageProcessError(f"圖像分割失敗: {str(e)}")
            
    @handle_error(error_types=(ImageProcessError,))
    def recognize_text(self, image: np.ndarray) -> str:
        """
        識別圖像中的文字
        
        Args:
            image: 輸入圖像
            
        Returns:
            識別出的文字
        """
        try:
            # 這裡需要集成OCR引擎
            # 簡化處理，返回空字符串
            return ""
            
        except Exception as e:
            self.logger.error(f"文字識別失敗: {str(e)}")
            raise ImageProcessError(f"文字識別失敗: {str(e)}")
            
    @handle_error(error_types=(ImageProcessError,))
    def save_image(
        self,
        image: np.ndarray,
        path: str,
        format: str = "png"
    ) -> None:
        """
        保存圖像
        
        Args:
            image: 輸入圖像
            path: 保存路徑
            format: 圖像格式
        """
        try:
            cv2.imwrite(path, image)
            
        except Exception as e:
            self.logger.error(f"圖像保存失敗: {str(e)}")
            raise ImageProcessError(f"圖像保存失敗: {str(e)}")
            
    @handle_error(error_types=(ImageProcessError,))
    def image_to_base64(self, image: np.ndarray) -> str:
        """
        將圖像轉換為Base64編碼
        
        Args:
            image: 輸入圖像
            
        Returns:
            Base64編碼的圖像數據
        """
        try:
            import base64
            _, buffer = cv2.imencode('.png', image)
            return base64.b64encode(buffer).decode('utf-8')
            
        except Exception as e:
            self.logger.error(f"圖像轉Base64失敗: {str(e)}")
            raise ImageProcessError(f"圖像轉Base64失敗: {str(e)}") 