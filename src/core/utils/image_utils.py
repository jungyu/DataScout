#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
圖像處理工具模組

提供圖像處理相關的功能，包括：
- 圖像讀取和保存
- 圖像格式轉換
- 圖像預處理
- 圖像特徵提取
- 圖像相似度比較
"""

import os
import base64
import logging
from typing import Optional, Union, Tuple, List
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
import io

class ImageUtils:
    """圖像處理工具類"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        初始化圖像處理器
        
        Args:
            logger: 日誌記錄器
        """
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        
    def read_image(self, image_path: Union[str, Path]) -> Optional[np.ndarray]:
        """
        讀取圖像
        
        Args:
            image_path: 圖像路徑
            
        Returns:
            圖像數據，如果讀取失敗則返回None
        """
        try:
            image = cv2.imread(str(image_path))
            if image is None:
                self.logger.error(f"無法讀取圖像: {image_path}")
                return None
            return image
        except Exception as e:
            self.logger.error(f"讀取圖像失敗: {str(e)}")
            return None
            
    def save_image(self, image: np.ndarray, save_path: Union[str, Path]) -> bool:
        """
        保存圖像
        
        Args:
            image: 圖像數據
            save_path: 保存路徑
            
        Returns:
            是否保存成功
        """
        try:
            cv2.imwrite(str(save_path), image)
            return True
        except Exception as e:
            self.logger.error(f"保存圖像失敗: {str(e)}")
            return False
            
    def base64_to_image(self, base64_str: str) -> Optional[np.ndarray]:
        """
        Base64字符串轉圖像
        
        Args:
            base64_str: Base64字符串
            
        Returns:
            圖像數據，如果轉換失敗則返回None
        """
        try:
            # 移除Base64前綴
            if ',' in base64_str:
                base64_str = base64_str.split(',')[1]
                
            # 解碼Base64
            image_data = base64.b64decode(base64_str)
            
            # 轉換為圖像
            nparr = np.frombuffer(image_data, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            return image
            
        except Exception as e:
            self.logger.error(f"Base64轉圖像失敗: {str(e)}")
            return None
            
    def image_to_base64(self, image: np.ndarray, format: str = '.png') -> Optional[str]:
        """
        圖像轉Base64字符串
        
        Args:
            image: 圖像數據
            format: 圖像格式
            
        Returns:
            Base64字符串，如果轉換失敗則返回None
        """
        try:
            # 編碼圖像
            success, buffer = cv2.imencode(format, image)
            if not success:
                raise ValueError("圖像編碼失敗")
                
            # 轉換為Base64
            base64_str = base64.b64encode(buffer).decode('utf-8')
            
            return base64_str
            
        except Exception as e:
            self.logger.error(f"圖像轉Base64失敗: {str(e)}")
            return None
            
    def resize_image(
        self,
        image: np.ndarray,
        size: Tuple[int, int],
        interpolation: int = cv2.INTER_LINEAR
    ) -> Optional[np.ndarray]:
        """
        調整圖像大小
        
        Args:
            image: 圖像數據
            size: 目標大小 (寬, 高)
            interpolation: 插值方法
            
        Returns:
            調整後的圖像，如果失敗則返回None
        """
        try:
            return cv2.resize(image, size, interpolation=interpolation)
        except Exception as e:
            self.logger.error(f"調整圖像大小失敗: {str(e)}")
            return None
            
    def crop_image(
        self,
        image: np.ndarray,
        x: int,
        y: int,
        width: int,
        height: int
    ) -> Optional[np.ndarray]:
        """
        裁剪圖像
        
        Args:
            image: 圖像數據
            x: 左上角x坐標
            y: 左上角y坐標
            width: 裁剪寬度
            height: 裁剪高度
            
        Returns:
            裁剪後的圖像，如果失敗則返回None
        """
        try:
            return image[y:y+height, x:x+width]
        except Exception as e:
            self.logger.error(f"裁剪圖像失敗: {str(e)}")
            return None
            
    def convert_color(self, image: np.ndarray, code: int) -> Optional[np.ndarray]:
        """
        轉換圖像顏色空間
        
        Args:
            image: 圖像數據
            code: 轉換代碼
            
        Returns:
            轉換後的圖像，如果失敗則返回None
        """
        try:
            return cv2.cvtColor(image, code)
        except Exception as e:
            self.logger.error(f"轉換圖像顏色空間失敗: {str(e)}")
            return None
            
    def apply_threshold(
        self,
        image: np.ndarray,
        thresh: float,
        maxval: float = 255,
        type: int = cv2.THRESH_BINARY
    ) -> Optional[Tuple[float, np.ndarray]]:
        """
        應用閾值處理
        
        Args:
            image: 圖像數據
            thresh: 閾值
            maxval: 最大值
            type: 閾值類型
            
        Returns:
            (閾值, 處理後的圖像)，如果失敗則返回None
        """
        try:
            return cv2.threshold(image, thresh, maxval, type)
        except Exception as e:
            self.logger.error(f"應用閾值處理失敗: {str(e)}")
            return None
            
    def detect_edges(
        self,
        image: np.ndarray,
        threshold1: float = 100,
        threshold2: float = 200
    ) -> Optional[np.ndarray]:
        """
        檢測圖像邊緣
        
        Args:
            image: 圖像數據
            threshold1: 第一個閾值
            threshold2: 第二個閾值
            
        Returns:
            邊緣圖像，如果失敗則返回None
        """
        try:
            return cv2.Canny(image, threshold1, threshold2)
        except Exception as e:
            self.logger.error(f"檢測圖像邊緣失敗: {str(e)}")
            return None
            
    def find_contours(
        self,
        image: np.ndarray,
        mode: int = cv2.RETR_EXTERNAL,
        method: int = cv2.CHAIN_APPROX_SIMPLE
    ) -> Optional[Tuple[List[np.ndarray], List[np.ndarray]]]:
        """
        查找圖像輪廓
        
        Args:
            image: 圖像數據
            mode: 輪廓檢索模式
            method: 輪廓近似方法
            
        Returns:
            (輪廓, 層次結構)，如果失敗則返回None
        """
        try:
            contours, hierarchy = cv2.findContours(image, mode, method)
            return contours, hierarchy
        except Exception as e:
            self.logger.error(f"查找圖像輪廓失敗: {str(e)}")
            return None
            
    def draw_contours(
        self,
        image: np.ndarray,
        contours: List[np.ndarray],
        contour_idx: int = -1,
        color: Tuple[int, int, int] = (0, 255, 0),
        thickness: int = 1
    ) -> Optional[np.ndarray]:
        """
        繪製輪廓
        
        Args:
            image: 圖像數據
            contours: 輪廓列表
            contour_idx: 輪廓索引
            color: 顏色
            thickness: 線條粗細
            
        Returns:
            繪製後的圖像，如果失敗則返回None
        """
        try:
            result = image.copy()
            cv2.drawContours(result, contours, contour_idx, color, thickness)
            return result
        except Exception as e:
            self.logger.error(f"繪製輪廓失敗: {str(e)}")
            return None
            
    def calculate_similarity(self, image1: np.ndarray, image2: np.ndarray) -> Optional[float]:
        """
        計算兩個圖像的相似度
        
        Args:
            image1: 第一個圖像
            image2: 第二個圖像
            
        Returns:
            相似度分數(0-1)，如果失敗則返回None
        """
        try:
            # 確保圖像大小相同
            if image1.shape != image2.shape:
                image2 = cv2.resize(image2, (image1.shape[1], image1.shape[0]))
                
            # 計算均方誤差
            err = np.sum((image1.astype("float") - image2.astype("float")) ** 2)
            err /= float(image1.shape[0] * image1.shape[1])
            
            # 轉換為相似度分數
            similarity = 1 - (err / (255 * 255))
            
            return max(0, min(1, similarity))
            
        except Exception as e:
            self.logger.error(f"計算圖像相似度失敗: {str(e)}")
            return None 