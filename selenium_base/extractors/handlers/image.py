#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
圖片提取器模組

提供圖片數據提取功能，包括：
1. 圖片定位
2. 圖片下載
3. 圖片驗證
4. 圖片處理
"""

import logging
import os
import time
import hashlib
from typing import Any, Dict, List, Optional, Union, Tuple
from dataclasses import dataclass
from urllib.parse import urlparse
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests
from PIL import Image
from io import BytesIO

from ..core.base import BaseExtractor
from ..core.types import ExtractorConfig, ExtractorResult
from ..core.error import ExtractorError, handle_extractor_error

@dataclass
class ImageExtractorConfig(ExtractorConfig):
    """圖片提取器配置"""
    image_selector: str = "img"
    wait_timeout: float = 10.0
    download_dir: str = "downloads/images"
    create_dir: bool = True
    overwrite: bool = False
    validate_size: bool = True
    min_width: Optional[int] = None
    min_height: Optional[int] = None
    max_width: Optional[int] = None
    max_height: Optional[int] = None
    validate_format: bool = True
    allowed_formats: List[str] = None
    validate_content: bool = True
    check_corruption: bool = True
    resize: bool = False
    target_width: Optional[int] = None
    target_height: Optional[int] = None
    maintain_aspect_ratio: bool = True
    quality: int = 85
    format: str = "JPEG"
    extract_alt: bool = True
    extract_title: bool = True
    extract_src: bool = True
    extract_dimensions: bool = True
    error_on_empty: bool = True
    error_on_invalid: bool = True
    error_on_timeout: bool = True
    retry_on_error: bool = True
    retry_count: int = 3
    retry_delay: float = 1.0

class ImageExtractor(BaseExtractor):
    """圖片提取器類別"""
    
    def __init__(
        self,
        config: Optional[Union[Dict[str, Any], ImageExtractorConfig]] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化圖片提取器
        
        Args:
            config: 配置字典或配置對象
            logger: 日誌記錄器
        """
        super().__init__(config, logger)
        self.config = config if isinstance(config, ImageExtractorConfig) else ImageExtractorConfig(**(config or {}))
        if self.config.allowed_formats is None:
            self.config.allowed_formats = ["JPEG", "PNG", "GIF", "BMP", "WEBP"]
            
    def _validate_config(self) -> bool:
        """
        驗證配置
        
        Returns:
            bool: 是否有效
        """
        try:
            if not self.config.image_selector:
                raise ExtractorError("圖片選擇器不能為空")
                
            if self.config.min_width is not None and self.config.min_width < 0:
                raise ExtractorError("最小寬度不能為負數")
                
            if self.config.min_height is not None and self.config.min_height < 0:
                raise ExtractorError("最小高度不能為負數")
                
            if self.config.max_width is not None and self.config.max_width < 0:
                raise ExtractorError("最大寬度不能為負數")
                
            if self.config.max_height is not None and self.config.max_height < 0:
                raise ExtractorError("最大高度不能為負數")
                
            if self.config.target_width is not None and self.config.target_width < 0:
                raise ExtractorError("目標寬度不能為負數")
                
            if self.config.target_height is not None and self.config.target_height < 0:
                raise ExtractorError("目標高度不能為負數")
                
            if self.config.quality < 0 or self.config.quality > 100:
                raise ExtractorError("質量必須在 0-100 之間")
                
            if self.config.format not in self.config.allowed_formats:
                raise ExtractorError(f"不支持的圖片格式: {self.config.format}")
                
            return True
            
        except Exception as e:
            self.logger.error(f"配置驗證失敗: {str(e)}")
            return False
            
    def _setup(self) -> None:
        """設置提取器環境"""
        if not self.validate_config():
            raise ExtractorError("配置驗證失敗")
            
        if self.config.create_dir and not os.path.exists(self.config.download_dir):
            os.makedirs(self.config.download_dir)
            
    def _cleanup(self) -> None:
        """清理提取器環境"""
        pass
        
    @handle_extractor_error()
    def find_image_elements(self, driver: Any) -> List[Any]:
        """
        查找圖片元素
        
        Args:
            driver: WebDriver 實例
            
        Returns:
            List[Any]: 圖片元素列表
        """
        try:
            elements = WebDriverWait(driver, self.config.wait_timeout).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, self.config.image_selector))
            )
            return elements
        except TimeoutException:
            if self.config.error_on_timeout:
                raise ExtractorError("等待圖片元素超時")
            return []
            
    def _get_image_info(self, element: Any) -> Dict[str, Any]:
        """
        獲取圖片信息
        
        Args:
            element: 圖片元素
            
        Returns:
            Dict[str, Any]: 圖片信息
        """
        info = {}
        
        if self.config.extract_alt:
            info['alt'] = element.get_attribute('alt') or ''
            
        if self.config.extract_title:
            info['title'] = element.get_attribute('title') or ''
            
        if self.config.extract_src:
            info['src'] = element.get_attribute('src') or ''
            
        if self.config.extract_dimensions:
            info['width'] = element.get_attribute('width')
            info['height'] = element.get_attribute('height')
            
        return info
        
    def _download_image(self, url: str) -> Tuple[bytes, str]:
        """
        下載圖片
        
        Args:
            url: 圖片URL
            
        Returns:
            Tuple[bytes, str]: 圖片數據和格式
        """
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            content = response.content
            format = Image.open(BytesIO(content)).format
            
            return content, format
            
        except Exception as e:
            raise ExtractorError(f"下載圖片失敗: {str(e)}")
            
    def _save_image(self, content: bytes, info: Dict[str, Any]) -> str:
        """
        保存圖片
        
        Args:
            content: 圖片數據
            info: 圖片信息
            
        Returns:
            str: 保存路徑
        """
        try:
            # 生成文件名
            filename = hashlib.md5(content).hexdigest()
            if info.get('alt'):
                filename = f"{filename}_{info['alt'][:30]}"
            elif info.get('title'):
                filename = f"{filename}_{info['title'][:30]}"
                
            # 添加擴展名
            filename = f"{filename}.{self.config.format.lower()}"
            filepath = os.path.join(self.config.download_dir, filename)
            
            # 檢查文件是否存在
            if os.path.exists(filepath) and not self.config.overwrite:
                return filepath
                
            # 保存圖片
            with open(filepath, 'wb') as f:
                f.write(content)
                
            return filepath
            
        except Exception as e:
            raise ExtractorError(f"保存圖片失敗: {str(e)}")
            
    def _process_image(self, content: bytes) -> bytes:
        """
        處理圖片
        
        Args:
            content: 圖片數據
            
        Returns:
            bytes: 處理後的圖片數據
        """
        try:
            image = Image.open(BytesIO(content))
            
            # 驗證尺寸
            if self.config.validate_size:
                width, height = image.size
                if self.config.min_width and width < self.config.min_width:
                    raise ExtractorError(f"圖片寬度小於最小值 {self.config.min_width}")
                if self.config.min_height and height < self.config.min_height:
                    raise ExtractorError(f"圖片高度小於最小值 {self.config.min_height}")
                if self.config.max_width and width > self.config.max_width:
                    raise ExtractorError(f"圖片寬度超過最大值 {self.config.max_width}")
                if self.config.max_height and height > self.config.max_height:
                    raise ExtractorError(f"圖片高度超過最大值 {self.config.max_height}")
                    
            # 驗證格式
            if self.config.validate_format and image.format not in self.config.allowed_formats:
                raise ExtractorError(f"不支持的圖片格式: {image.format}")
                
            # 調整大小
            if self.config.resize and (self.config.target_width or self.config.target_height):
                if self.config.maintain_aspect_ratio:
                    image.thumbnail(
                        (self.config.target_width or image.width, 
                         self.config.target_height or image.height),
                        Image.LANCZOS
                    )
                else:
                    image = image.resize(
                        (self.config.target_width or image.width,
                         self.config.target_height or image.height),
                        Image.LANCZOS
                    )
                    
            # 保存處理後的圖片
            output = BytesIO()
            image.save(
                output,
                format=self.config.format,
                quality=self.config.quality
            )
            
            return output.getvalue()
            
        except Exception as e:
            raise ExtractorError(f"處理圖片失敗: {str(e)}")
            
    def _validate_image(self, content: bytes) -> bool:
        """
        驗證圖片
        
        Args:
            content: 圖片數據
            
        Returns:
            bool: 是否有效
        """
        try:
            if not content:
                if self.config.error_on_empty:
                    raise ExtractorError("圖片數據為空")
                return False
                
            if self.config.check_corruption:
                Image.open(BytesIO(content)).verify()
                
            return True
            
        except Exception as e:
            if self.config.error_on_invalid:
                raise ExtractorError(f"圖片驗證失敗: {str(e)}")
            return False
            
    @handle_extractor_error()
    def _extract(self, driver: Any) -> List[Dict[str, Any]]:
        """
        提取圖片數據
        
        Args:
            driver: WebDriver 實例
            
        Returns:
            List[Dict[str, Any]]: 圖片數據列表
        """
        elements = self.find_image_elements(driver)
        if not elements:
            return []
            
        results = []
        for element in elements:
            try:
                # 獲取圖片信息
                info = self._get_image_info(element)
                if not info.get('src'):
                    continue
                    
                # 下載圖片
                content, format = self._download_image(info['src'])
                
                # 驗證圖片
                if not self._validate_image(content):
                    continue
                    
                # 處理圖片
                if self.config.resize or self.config.validate_size:
                    content = self._process_image(content)
                    
                # 保存圖片
                filepath = self._save_image(content, info)
                
                # 更新信息
                info.update({
                    'format': format,
                    'filepath': filepath,
                    'size': len(content)
                })
                
                results.append(info)
                
            except Exception as e:
                self.logger.warning(f"處理圖片失敗: {str(e)}")
                continue
                
        return results
        
    def extract(self, driver: Any) -> ExtractorResult:
        """
        提取圖片數據
        
        Args:
            driver: WebDriver 實例
            
        Returns:
            ExtractorResult: 提取結果
        """
        try:
            data = self._extract(driver)
            return ExtractorResult(success=True, data=data)
        except Exception as e:
            if self.config.retry_on_error:
                self.logger.warning(f"提取失敗，正在重試: {str(e)}")
                for i in range(self.config.retry_count):
                    try:
                        data = self._extract(driver)
                        return ExtractorResult(success=True, data=data)
                    except Exception as retry_e:
                        self.logger.warning(f"第 {i+1} 次重試失敗: {str(retry_e)}")
                        if i < self.config.retry_count - 1:
                            time.sleep(self.config.retry_delay)
                            
            return ExtractorResult(success=False, data=None, error=str(e)) 