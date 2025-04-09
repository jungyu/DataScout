#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文本處理工具模組

提供文本處理相關功能，包括：
1. 文本預處理
2. 文本驗證
3. 文本清理
4. 文本轉換
5. 文本比較
"""

import re
import logging
import unicodedata
from typing import Optional, List, Dict, Any, Union
from dataclasses import dataclass

from .error import TextProcessError, handle_error

@dataclass
class TextProcessResult:
    """文本處理結果數據類"""
    success: bool
    text: Optional[str] = None
    confidence: Optional[float] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class TextProcessor:
    """文本處理工具類"""
    
    def __init__(
        self,
        logger: Optional[logging.Logger] = None,
        min_length: int = 4,
        max_length: int = 8,
        allowed_chars: Optional[str] = None
    ):
        """
        初始化文本處理器
        
        Args:
            logger: 日誌記錄器
            min_length: 最小文本長度
            max_length: 最大文本長度
            allowed_chars: 允許的字符集
        """
        self.logger = logger or logging.getLogger(__name__)
        self.min_length = min_length
        self.max_length = max_length
        self.allowed_chars = allowed_chars or "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        
    @handle_error(error_types=(TextProcessError,))
    def preprocess_text(self, text: str) -> str:
        """
        文本預處理
        
        Args:
            text: 輸入文本
            
        Returns:
            預處理後的文本
        """
        try:
            # 移除空白字符
            text = text.strip()
            
            # 轉換為小寫
            text = text.lower()
            
            # 移除特殊字符
            text = re.sub(r'[^a-zA-Z0-9]', '', text)
            
            # 正規化Unicode字符
            text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')
            
            return text
            
        except Exception as e:
            self.logger.error(f"文本預處理失敗: {str(e)}")
            raise TextProcessError(f"文本預處理失敗: {str(e)}")
            
    @handle_error(error_types=(TextProcessError,))
    def validate_text(self, text: str) -> bool:
        """
        驗證文本
        
        Args:
            text: 輸入文本
            
        Returns:
            是否有效
        """
        try:
            # 檢查長度
            if not (self.min_length <= len(text) <= self.max_length):
                return False
                
            # 檢查字符
            if not all(c in self.allowed_chars for c in text):
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"文本驗證失敗: {str(e)}")
            raise TextProcessError(f"文本驗證失敗: {str(e)}")
            
    @handle_error(error_types=(TextProcessError,))
    def clean_text(self, text: str) -> str:
        """
        清理文本
        
        Args:
            text: 輸入文本
            
        Returns:
            清理後的文本
        """
        try:
            # 移除不可見字符
            text = ''.join(char for char in text if char.isprintable())
            
            # 移除重複字符
            text = re.sub(r'(.)\1+', r'\1', text)
            
            # 移除常見錯誤
            text = text.replace('0', 'o')  # 數字0替換為字母o
            text = text.replace('1', 'i')  # 數字1替換為字母i
            text = text.replace('5', 's')  # 數字5替換為字母s
            
            return text
            
        except Exception as e:
            self.logger.error(f"文本清理失敗: {str(e)}")
            raise TextProcessError(f"文本清理失敗: {str(e)}")
            
    @handle_error(error_types=(TextProcessError,))
    def compare_texts(self, text1: str, text2: str) -> float:
        """
        比較兩個文本的相似度
        
        Args:
            text1: 第一個文本
            text2: 第二個文本
            
        Returns:
            相似度分數 (0-1)
        """
        try:
            # 預處理文本
            text1 = self.preprocess_text(text1)
            text2 = self.preprocess_text(text2)
            
            # 計算編輯距離
            def levenshtein_distance(s1: str, s2: str) -> int:
                if len(s1) < len(s2):
                    return levenshtein_distance(s2, s1)
                    
                if len(s2) == 0:
                    return len(s1)
                    
                previous_row = range(len(s2) + 1)
                for i, c1 in enumerate(s1):
                    current_row = [i + 1]
                    for j, c2 in enumerate(s2):
                        insertions = previous_row[j + 1] + 1
                        deletions = current_row[j] + 1
                        substitutions = previous_row[j] + (c1 != c2)
                        current_row.append(min(insertions, deletions, substitutions))
                    previous_row = current_row
                    
                return previous_row[-1]
                
            # 計算相似度
            distance = levenshtein_distance(text1, text2)
            max_length = max(len(text1), len(text2))
            similarity = 1 - (distance / max_length)
            
            return similarity
            
        except Exception as e:
            self.logger.error(f"文本比較失敗: {str(e)}")
            raise TextProcessError(f"文本比較失敗: {str(e)}")
            
    @handle_error(error_types=(TextProcessError,))
    def process_text(self, text: str) -> TextProcessResult:
        """
        處理文本
        
        Args:
            text: 輸入文本
            
        Returns:
            處理結果
        """
        try:
            # 預處理
            processed_text = self.preprocess_text(text)
            
            # 清理
            cleaned_text = self.clean_text(processed_text)
            
            # 驗證
            is_valid = self.validate_text(cleaned_text)
            
            if not is_valid:
                return TextProcessResult(
                    success=False,
                    error="文本驗證失敗"
                )
                
            return TextProcessResult(
                success=True,
                text=cleaned_text,
                confidence=1.0
            )
            
        except Exception as e:
            self.logger.error(f"文本處理失敗: {str(e)}")
            return TextProcessResult(
                success=False,
                error=str(e)
            ) 