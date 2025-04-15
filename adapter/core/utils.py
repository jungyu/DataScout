#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
適配器工具類別
"""

import json
import re
import uuid
import hashlib
import base64
from datetime import datetime
from typing import Any, Dict, List, Optional, Type, Union, TypeVar

T = TypeVar('T')

class Utils:
    """適配器工具類別"""
    
    @staticmethod
    def to_json(data: Any, ensure_ascii: bool = False, indent: Optional[int] = None) -> str:
        """
        將數據轉換為 JSON 字符串
        
        Args:
            data: 要轉換的數據
            ensure_ascii: 是否確保 ASCII 編碼
            indent: 縮進空格數
            
        Returns:
            str: JSON 字符串
        """
        return json.dumps(data, ensure_ascii=ensure_ascii, indent=indent)
        
    @staticmethod
    def from_json(json_str: str) -> Any:
        """
        將 JSON 字符串轉換為 Python 對象
        
        Args:
            json_str: JSON 字符串
            
        Returns:
            Any: Python 對象
        """
        return json.loads(json_str)
        
    @staticmethod
    def to_dict(obj: Any) -> Dict[str, Any]:
        """
        將對象轉換為字典
        
        Args:
            obj: 要轉換的對象
            
        Returns:
            Dict[str, Any]: 字典
        """
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        return dict(obj)
        
    @staticmethod
    def from_dict(data: Dict[str, Any], cls: Type[T]) -> T:
        """
        將字典轉換為對象
        
        Args:
            data: 字典數據
            cls: 目標類別
            
        Returns:
            T: 對象實例
        """
        return cls(**data)
        
    @staticmethod
    def to_list(data: Any) -> List[Any]:
        """
        將數據轉換為列表
        
        Args:
            data: 要轉換的數據
            
        Returns:
            List[Any]: 列表
        """
        if isinstance(data, list):
            return data
        if isinstance(data, (tuple, set)):
            return list(data)
        if isinstance(data, dict):
            return list(data.values())
        return [data]
        
    @staticmethod
    def to_str(data: Any) -> str:
        """
        將數據轉換為字符串
        
        Args:
            data: 要轉換的數據
            
        Returns:
            str: 字符串
        """
        if isinstance(data, str):
            return data
        if isinstance(data, (list, dict)):
            return Utils.to_json(data)
        return str(data)
        
    @staticmethod
    def to_int(data: Any) -> int:
        """
        將數據轉換為整數
        
        Args:
            data: 要轉換的數據
            
        Returns:
            int: 整數
        """
        if isinstance(data, int):
            return data
        if isinstance(data, float):
            return int(data)
        if isinstance(data, str):
            return int(float(data))
        return int(data)
        
    @staticmethod
    def to_float(data: Any) -> float:
        """
        將數據轉換為浮點數
        
        Args:
            data: 要轉換的數據
            
        Returns:
            float: 浮點數
        """
        if isinstance(data, float):
            return data
        if isinstance(data, int):
            return float(data)
        if isinstance(data, str):
            return float(data)
        return float(data)
        
    @staticmethod
    def to_bool(data: Any) -> bool:
        """
        將數據轉換為布爾值
        
        Args:
            data: 要轉換的數據
            
        Returns:
            bool: 布爾值
        """
        if isinstance(data, bool):
            return data
        if isinstance(data, str):
            return data.lower() in ('true', '1', 'yes', 'y')
        if isinstance(data, (int, float)):
            return bool(data)
        return bool(data)
        
    @staticmethod
    def to_datetime(data: Any, format: str = "%Y-%m-%d %H:%M:%S") -> datetime:
        """
        將數據轉換為日期時間
        
        Args:
            data: 要轉換的數據
            format: 日期時間格式
            
        Returns:
            datetime: 日期時間對象
        """
        if isinstance(data, datetime):
            return data
        if isinstance(data, str):
            return datetime.strptime(data, format)
        if isinstance(data, (int, float)):
            return datetime.fromtimestamp(data)
        raise ValueError(f"無法將 {type(data)} 轉換為日期時間")
        
    @staticmethod
    def to_type(data: Any, target_type: Type[T]) -> T:
        """
        將數據轉換為指定類型
        
        Args:
            data: 要轉換的數據
            target_type: 目標類型
            
        Returns:
            T: 轉換後的數據
        """
        if isinstance(data, target_type):
            return data
        if target_type == str:
            return Utils.to_str(data)
        if target_type == int:
            return Utils.to_int(data)
        if target_type == float:
            return Utils.to_float(data)
        if target_type == bool:
            return Utils.to_bool(data)
        if target_type == list:
            return Utils.to_list(data)
        if target_type == dict:
            return Utils.to_dict(data)
        if target_type == datetime:
            return Utils.to_datetime(data)
        return target_type(data)
        
    @staticmethod
    def is_empty(data: Any) -> bool:
        """
        檢查數據是否為空
        
        Args:
            data: 要檢查的數據
            
        Returns:
            bool: 是否為空
        """
        if data is None:
            return True
        if isinstance(data, (str, list, dict, set, tuple)):
            return len(data) == 0
        if isinstance(data, (int, float)):
            return data == 0
        if isinstance(data, bool):
            return not data
        return False
        
    @staticmethod
    def is_numeric(data: Any) -> bool:
        """
        檢查數據是否為數字
        
        Args:
            data: 要檢查的數據
            
        Returns:
            bool: 是否為數字
        """
        if isinstance(data, (int, float)):
            return True
        if isinstance(data, str):
            try:
                float(data)
                return True
            except ValueError:
                return False
        return False
        
    @staticmethod
    def is_datetime(data: Any) -> bool:
        """
        檢查數據是否為日期時間
        
        Args:
            data: 要檢查的數據
            
        Returns:
            bool: 是否為日期時間
        """
        if isinstance(data, datetime):
            return True
        if isinstance(data, str):
            try:
                datetime.strptime(data, "%Y-%m-%d %H:%M:%S")
                return True
            except ValueError:
                return False
        return False
        
    @staticmethod
    def is_json(data: Any) -> bool:
        """
        檢查數據是否為 JSON
        
        Args:
            data: 要檢查的數據
            
        Returns:
            bool: 是否為 JSON
        """
        if isinstance(data, (dict, list)):
            return True
        if isinstance(data, str):
            try:
                json.loads(data)
                return True
            except ValueError:
                return False
        return False
        
    @staticmethod
    def is_email(data: Any) -> bool:
        """
        檢查數據是否為電子郵件
        
        Args:
            data: 要檢查的數據
            
        Returns:
            bool: 是否為電子郵件
        """
        if not isinstance(data, str):
            return False
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, data))
        
    @staticmethod
    def is_url(data: Any) -> bool:
        """
        檢查數據是否為 URL
        
        Args:
            data: 要檢查的數據
            
        Returns:
            bool: 是否為 URL
        """
        if not isinstance(data, str):
            return False
        pattern = r'^https?://(?:[\w-]+\.)+[\w-]+(?:/[\w-./?%&=]*)?$'
        return bool(re.match(pattern, data))
        
    @staticmethod
    def is_phone(data: Any) -> bool:
        """
        檢查數據是否為電話號碼
        
        Args:
            data: 要檢查的數據
            
        Returns:
            bool: 是否為電話號碼
        """
        if not isinstance(data, str):
            return False
        pattern = r'^\+?[\d\s-]{10,}$'
        return bool(re.match(pattern, data))
        
    @staticmethod
    def is_ip(data: Any) -> bool:
        """
        檢查數據是否為 IP 地址
        
        Args:
            data: 要檢查的數據
            
        Returns:
            bool: 是否為 IP 地址
        """
        if not isinstance(data, str):
            return False
        pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if not re.match(pattern, data):
            return False
        return all(0 <= int(x) <= 255 for x in data.split('.'))
        
    @staticmethod
    def is_mac(data: Any) -> bool:
        """
        檢查數據是否為 MAC 地址
        
        Args:
            data: 要檢查的數據
            
        Returns:
            bool: 是否為 MAC 地址
        """
        if not isinstance(data, str):
            return False
        pattern = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
        return bool(re.match(pattern, data))
        
    @staticmethod
    def is_hex(data: Any) -> bool:
        """
        檢查數據是否為十六進制
        
        Args:
            data: 要檢查的數據
            
        Returns:
            bool: 是否為十六進制
        """
        if not isinstance(data, str):
            return False
        pattern = r'^[0-9A-Fa-f]+$'
        return bool(re.match(pattern, data))
        
    @staticmethod
    def is_base64(data: Any) -> bool:
        """
        檢查數據是否為 Base64
        
        Args:
            data: 要檢查的數據
            
        Returns:
            bool: 是否為 Base64
        """
        if not isinstance(data, str):
            return False
        try:
            base64.b64decode(data)
            return True
        except Exception:
            return False
        
    @staticmethod
    def is_uuid(data: Any) -> bool:
        """
        檢查數據是否為 UUID
        
        Args:
            data: 要檢查的數據
            
        Returns:
            bool: 是否為 UUID
        """
        if isinstance(data, uuid.UUID):
            return True
        if not isinstance(data, str):
            return False
        try:
            uuid.UUID(data)
            return True
        except ValueError:
            return False
        
    @staticmethod
    def is_md5(data: Any) -> bool:
        """
        檢查數據是否為 MD5
        
        Args:
            data: 要檢查的數據
            
        Returns:
            bool: 是否為 MD5
        """
        if not isinstance(data, str):
            return False
        pattern = r'^[a-f0-9]{32}$'
        return bool(re.match(pattern, data.lower()))
        
    @staticmethod
    def is_sha1(data: Any) -> bool:
        """
        檢查數據是否為 SHA1
        
        Args:
            data: 要檢查的數據
            
        Returns:
            bool: 是否為 SHA1
        """
        if not isinstance(data, str):
            return False
        pattern = r'^[a-f0-9]{40}$'
        return bool(re.match(pattern, data.lower()))
        
    @staticmethod
    def is_sha256(data: Any) -> bool:
        """
        檢查數據是否為 SHA256
        
        Args:
            data: 要檢查的數據
            
        Returns:
            bool: 是否為 SHA256
        """
        if not isinstance(data, str):
            return False
        pattern = r'^[a-f0-9]{64}$'
        return bool(re.match(pattern, data.lower()))
        
    @staticmethod
    def is_sha512(data: Any) -> bool:
        """
        檢查數據是否為 SHA512
        
        Args:
            data: 要檢查的數據
            
        Returns:
            bool: 是否為 SHA512
        """
        if not isinstance(data, str):
            return False
        pattern = r'^[a-f0-9]{128}$'
        return bool(re.match(pattern, data.lower()))
        
    @staticmethod
    def generate_uuid() -> str:
        """
        生成 UUID
        
        Returns:
            str: UUID 字符串
        """
        return str(uuid.uuid4())
        
    @staticmethod
    def generate_md5(data: str) -> str:
        """
        生成 MD5 哈希
        
        Args:
            data: 要哈希的數據
            
        Returns:
            str: MD5 哈希字符串
        """
        return hashlib.md5(data.encode()).hexdigest()
        
    @staticmethod
    def generate_sha1(data: str) -> str:
        """
        生成 SHA1 哈希
        
        Args:
            data: 要哈希的數據
            
        Returns:
            str: SHA1 哈希字符串
        """
        return hashlib.sha1(data.encode()).hexdigest()
        
    @staticmethod
    def generate_sha256(data: str) -> str:
        """
        生成 SHA256 哈希
        
        Args:
            data: 要哈希的數據
            
        Returns:
            str: SHA256 哈希字符串
        """
        return hashlib.sha256(data.encode()).hexdigest()
        
    @staticmethod
    def generate_sha512(data: str) -> str:
        """
        生成 SHA512 哈希
        
        Args:
            data: 要哈希的數據
            
        Returns:
            str: SHA512 哈希字符串
        """
        return hashlib.sha512(data.encode()).hexdigest()
        
    @staticmethod
    def encode_base64(data: str) -> str:
        """
        編碼 Base64
        
        Args:
            data: 要編碼的數據
            
        Returns:
            str: Base64 編碼字符串
        """
        return base64.b64encode(data.encode()).decode()
        
    @staticmethod
    def decode_base64(data: str) -> str:
        """
        解碼 Base64
        
        Args:
            data: 要解碼的數據
            
        Returns:
            str: Base64 解碼字符串
        """
        return base64.b64decode(data.encode()).decode() 