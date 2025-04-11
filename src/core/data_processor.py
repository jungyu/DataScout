"""
數據處理模組

負責處理爬蟲數據，包括：
- 數據清洗
- 數據轉換
- 數據驗證
- 數據格式化
- 數據存儲
"""

import re
import json
import logging
import pandas as pd
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from dataclasses import dataclass
import os
import time

from .utils.logger import Logger, setup_logger
from .utils.path_utils import PathUtils
from .utils.config_utils import ConfigUtils
from .utils.error_handler import ErrorHandler
from .utils.data_processor import DataProcessor as UtilsDataProcessor

@dataclass
class DataProcessorConfig:
    """數據處理配置"""
    remove_html: bool = True
    remove_extra_spaces: bool = True
    normalize_whitespace: bool = True
    remove_special_chars: bool = True
    convert_dates: bool = True
    validate_data: bool = True
    output_format: str = "json"
    encoding: str = "utf-8"
    date_formats: List[str] = None
    required_fields: List[str] = None
    field_types: Dict[str, str] = None
    field_ranges: Dict[str, tuple] = None
    field_patterns: Dict[str, str] = None
    output_dir: str = "data/processed"
    backup_dir: str = "data/backup"
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    compression: bool = True
    chunk_size: int = 1000

class DataProcessor:
    """數據處理器"""
    
    def __init__(self, config: Dict):
        """
        初始化數據處理器
        
        Args:
            config: 配置字典
        """
        # 初始化工具類
        self.logger = setup_logger(
            name="data_processor",
            level=logging.INFO,
            log_dir="logs",
            console_output=True,
            file_output=True
        )
        self.path_utils = PathUtils(self.logger)
        self.config_utils = ConfigUtils(self.logger)
        self.error_handler = ErrorHandler(self.logger)
        self.utils_processor = UtilsDataProcessor(self.logger)
        
        # 加載配置
        self.config = DataProcessorConfig(**config)
        
        # 創建輸出目錄
        self.path_utils.ensure_dir(self.config.output_dir)
        self.path_utils.ensure_dir(self.config.backup_dir)
        
        # 初始化統計信息
        self.stats = {
            "processed_items": 0,
            "valid_items": 0,
            "invalid_items": 0,
            "error_count": 0,
            "start_time": datetime.now(),
            "last_update": None
        }
    
    def process(self, data: Union[Dict, List[Dict]]) -> Union[Dict, List[Dict]]:
        """
        處理數據
        
        Args:
            data: 輸入數據
            
        Returns:
            處理後的數據
        """
        try:
            # 處理單個字典
            if isinstance(data, dict):
                return self._process_item(data)
            
            # 處理字典列表
            if isinstance(data, list):
                return [self._process_item(item) for item in data]
            
            raise ValueError("不支持的數據類型")
            
        except Exception as e:
            self.logger.error(f"處理數據失敗: {str(e)}")
            self.error_handler.handle_error(e)
            return data
    
    def _process_item(self, item: Dict) -> Dict:
        """
        處理單個數據項
        
        Args:
            item: 數據項
            
        Returns:
            處理後的數據項
        """
        try:
            processed_item = {}
            
            for key, value in item.items():
                processed_value = self._process_value(value)
                processed_item[key] = processed_value
            
            # 驗證數據
            if self.config.validate_data:
                if not self._validate_item(processed_item):
                    self.stats["invalid_items"] += 1
                    return None
            
            self.stats["valid_items"] += 1
            return processed_item
            
        except Exception as e:
            self.logger.error(f"處理數據項失敗: {str(e)}")
            self.error_handler.handle_error(e)
            self.stats["error_count"] += 1
            return None
    
    def _process_value(self, value: Any) -> Any:
        """
        處理數據值
        
        Args:
            value: 數據值
            
        Returns:
            處理後的數據值
        """
        try:
            # 處理字符串
            if isinstance(value, str):
                return self._process_text(value)
            
            # 處理日期
            if isinstance(value, (datetime, str)) and self.config.convert_dates:
                return self._convert_date(value)
            
            return value
            
        except Exception as e:
            self.logger.error(f"處理數據值失敗: {str(e)}")
            self.error_handler.handle_error(e)
            return value
    
    def _process_text(self, text: str) -> str:
        """
        處理文本
        
        Args:
            text: 輸入文本
            
        Returns:
            處理後的文本
        """
        try:
            # 移除HTML標籤
            if self.config.remove_html:
                text = re.sub(r'<[^>]+>', '', text)
            
            # 移除多餘空格
            if self.config.remove_extra_spaces:
                text = re.sub(r'\s+', ' ', text)
            
            # 標準化空白字符
            if self.config.normalize_whitespace:
                text = ' '.join(text.split())
            
            # 移除特殊字符
            if self.config.remove_special_chars:
                text = re.sub(r'[^\w\s]', '', text)
            
            return text.strip()
            
        except Exception as e:
            self.logger.error(f"處理文本失敗: {str(e)}")
            self.error_handler.handle_error(e)
            return text
    
    def _convert_date(self, value: Union[datetime, str]) -> datetime:
        """
        轉換日期
        
        Args:
            value: 日期值
            
        Returns:
            轉換後的日期
        """
        try:
            # 已經是datetime類型
            if isinstance(value, datetime):
                return value
            
            # 嘗試不同的日期格式
            for date_format in self.config.date_formats:
                try:
                    return datetime.strptime(value, date_format)
                except ValueError:
                    continue
            
            raise ValueError(f"無法解析日期: {value}")
            
        except Exception as e:
            self.logger.error(f"轉換日期失敗: {str(e)}")
            self.error_handler.handle_error(e)
            return value
    
    def _validate_item(self, item: Dict) -> bool:
        """
        驗證數據項
        
        Args:
            item: 數據項
            
        Returns:
            是否驗證通過
        """
        try:
            # 檢查必填字段
            if self.config.required_fields:
                for field in self.config.required_fields:
                    if field not in item:
                        self.logger.warning(f"缺少必填字段: {field}")
                        return False
            
            # 檢查字段類型
            if self.config.field_types:
                for field, type_name in self.config.field_types.items():
                    if field in item:
                        if not isinstance(item[field], eval(type_name)):
                            self.logger.warning(f"字段類型不匹配: {field}")
                            return False
            
            # 檢查字段範圍
            if self.config.field_ranges:
                for field, (min_val, max_val) in self.config.field_ranges.items():
                    if field in item:
                        if not (min_val <= item[field] <= max_val):
                            self.logger.warning(f"字段值超出範圍: {field}")
                            return False
            
            # 檢查字段格式
            if self.config.field_patterns:
                for field, pattern in self.config.field_patterns.items():
                    if field in item:
                        if not re.match(pattern, str(item[field])):
                            self.logger.warning(f"字段格式不匹配: {field}")
                            return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"驗證數據項失敗: {str(e)}")
            self.error_handler.handle_error(e)
            return False
    
    def to_dataframe(self, data: List[Dict]) -> pd.DataFrame:
        """
        轉換為DataFrame
        
        Args:
            data: 數據列表
            
        Returns:
            DataFrame
        """
        try:
            return pd.DataFrame(data)
            
        except Exception as e:
            self.logger.error(f"轉換為DataFrame失敗: {str(e)}")
            self.error_handler.handle_error(e)
            return pd.DataFrame()
    
    def save_to_file(self, data: Union[Dict, List[Dict]], filename: str) -> bool:
        """
        保存到文件
        
        Args:
            data: 數據
            filename: 文件名
            
        Returns:
            是否保存成功
        """
        try:
            # 處理數據
            processed_data = self.process(data)
            
            # 生成文件路徑
            file_path = self.path_utils.join_path(self.config.output_dir, filename)
            
            # 根據格式保存
            if self.config.output_format == "json":
                with open(file_path, "w", encoding=self.config.encoding) as f:
                    json.dump(processed_data, f, ensure_ascii=False, indent=2)
            
            elif self.config.output_format == "csv":
                df = self.to_dataframe(processed_data)
                df.to_csv(file_path, index=False, encoding=self.config.encoding)
            
            elif self.config.output_format == "excel":
                df = self.to_dataframe(processed_data)
                df.to_excel(file_path, index=False)
            
            else:
                raise ValueError(f"不支持的輸出格式: {self.config.output_format}")
            
            # 備份文件
            if self.config.backup_dir:
                backup_path = self.path_utils.join_path(
                    self.config.backup_dir,
                    f"{int(time.time())}_{filename}"
                )
                self.path_utils.copy_file(file_path, backup_path)
            
            self.logger.info(f"已保存數據到文件: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"保存到文件失敗: {str(e)}")
            self.error_handler.handle_error(e)
            return False
    
    def load_from_file(self, filename: str) -> Union[Dict, List[Dict]]:
        """
        從文件加載
        
        Args:
            filename: 文件名
            
        Returns:
            加載的數據
        """
        try:
            # 生成文件路徑
            file_path = self.path_utils.join_path(self.config.output_dir, filename)
            
            # 根據格式加載
            if self.config.output_format == "json":
                with open(file_path, "r", encoding=self.config.encoding) as f:
                    data = json.load(f)
            
            elif self.config.output_format == "csv":
                df = pd.read_csv(file_path, encoding=self.config.encoding)
                data = df.to_dict("records")
            
            elif self.config.output_format == "excel":
                df = pd.read_excel(file_path)
                data = df.to_dict("records")
            
            else:
                raise ValueError(f"不支持的輸出格式: {self.config.output_format}")
            
            self.logger.info(f"已從文件加載數據: {file_path}")
            return data
            
        except Exception as e:
            self.logger.error(f"從文件加載失敗: {str(e)}")
            self.error_handler.handle_error(e)
            return None
    
    def get_stats(self) -> Dict:
        """
        獲取統計信息
        
        Returns:
            統計信息
        """
        try:
            stats = self.stats.copy()
            
            # 計算處理時間
            stats["processing_time"] = (datetime.now() - stats["start_time"]).total_seconds()
            
            # 計算成功率
            total_items = stats["processed_items"]
            if total_items > 0:
                stats["success_rate"] = stats["valid_items"] / total_items
            else:
                stats["success_rate"] = 0
            
            return stats
            
        except Exception as e:
            self.logger.error(f"獲取統計信息失敗: {str(e)}")
            self.error_handler.handle_error(e)
            return {}

    @staticmethod
    def clean_text(text: str) -> str:
        """
        清理文本數據
        
        Args:
            text: 要清理的文本
            
        Returns:
            清理後的文本
        """
        if not text:
            return ""
            
        # 移除多餘的空白字符
        text = re.sub(r'\s+', ' ', text)
        
        # 移除首尾空白
        text = text.strip()
        
        return text
        
    @staticmethod
    def clean_price(price: str) -> float:
        """
        清理價格數據
        
        Args:
            price: 要清理的價格字符串
            
        Returns:
            清理後的價格
        """
        if not price:
            return 0.0
            
        # 提取數字
        numbers = re.findall(r'[\d,]+\.?\d*', price)
        if not numbers:
            return 0.0
            
        # 移除逗號並轉換為浮點數
        return float(numbers[0].replace(',', ''))
        
    @staticmethod
    def clean_product_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        清理商品數據
        
        Args:
            data: 要清理的商品數據
            
        Returns:
            清理後的商品數據
        """
        cleaned = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                # 清理文本字段
                cleaned[key] = DataProcessor.clean_text(value)
            elif isinstance(value, (int, float)):
                # 數值字段保持不變
                cleaned[key] = value
            elif isinstance(value, dict):
                # 遞歸清理字典
                cleaned[key] = DataProcessor.clean_product_data(value)
            elif isinstance(value, list):
                # 清理列表中的每個元素
                cleaned[key] = [
                    DataProcessor.clean_product_data(item) if isinstance(item, dict)
                    else DataProcessor.clean_text(item) if isinstance(item, str)
                    else item
                    for item in value
                ]
            else:
                # 其他類型的數據保持不變
                cleaned[key] = value
                
        return cleaned
        
    @staticmethod
    def format_datetime(dt: Union[str, datetime]) -> str:
        """
        格式化日期時間
        
        Args:
            dt: 要格式化的日期時間
            
        Returns:
            格式化後的日期時間字符串
        """
        if isinstance(dt, str):
            try:
                dt = datetime.fromisoformat(dt)
            except ValueError:
                return dt
                
        return dt.strftime("%Y-%m-%d %H:%M:%S")
        
    @staticmethod
    def extract_numbers(text: str) -> List[float]:
        """
        從文本中提取數字
        
        Args:
            text: 要提取數字的文本
            
        Returns:
            提取到的數字列表
        """
        if not text:
            return []
            
        numbers = re.findall(r'[\d,]+\.?\d*', text)
        return [float(num.replace(',', '')) for num in numbers]
        
    @staticmethod
    def normalize_field_name(name: str) -> str:
        """
        標準化字段名稱
        
        Args:
            name: 要標準化的字段名稱
            
        Returns:
            標準化後的字段名稱
        """
        if not name:
            return ""
            
        # 轉換為小寫
        name = name.lower()
        
        # 替換特殊字符為下劃線
        name = re.sub(r'[^a-z0-9_]', '_', name)
        
        # 移除多餘的下劃線
        name = re.sub(r'_+', '_', name)
        
        # 移除首尾下劃線
        name = name.strip('_')
        
        return name 