#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
安全工具類
提供數據加密和解密功能
"""

import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from typing import Optional

from .config_utils import ConfigUtils
from .logger import Logger

class SecurityUtils:
    """安全工具類"""
    
    def __init__(self):
        """初始化安全工具"""
        self.config_utils = ConfigUtils()
        self.logger = Logger()
        
        # 獲取安全配置
        self.security_config = self.config_utils.get_config('security')
        self.key_file = self.security_config.get('key_file', 'security.key')
        
        # 初始化加密器
        self.fernet = self._init_encryption()
    
    def _init_encryption(self) -> Optional[Fernet]:
        """
        初始化加密器
        
        Returns:
            Optional[Fernet]: 加密器實例
        """
        try:
            # 檢查密鑰文件是否存在
            if not os.path.exists(self.key_file):
                # 生成新密鑰
                key = Fernet.generate_key()
                with open(self.key_file, 'wb') as f:
                    f.write(key)
                self.logger.info("生成新的加密密鑰")
            else:
                # 讀取現有密鑰
                with open(self.key_file, 'rb') as f:
                    key = f.read()
            
            return Fernet(key)
            
        except Exception as e:
            self.logger.error(f"初始化加密器失敗: {str(e)}")
            return None
    
    def encrypt_data(self, data: str) -> Optional[str]:
        """
        加密數據
        
        Args:
            data: 要加密的數據
            
        Returns:
            Optional[str]: 加密後的數據
        """
        try:
            if not self.fernet:
                raise ValueError("加密器未初始化")
                
            # 加密數據
            encrypted_data = self.fernet.encrypt(data.encode())
            return base64.b64encode(encrypted_data).decode()
            
        except Exception as e:
            self.logger.error(f"加密數據失敗: {str(e)}")
            return None
    
    def decrypt_data(self, encrypted_data: str) -> Optional[str]:
        """
        解密數據
        
        Args:
            encrypted_data: 加密後的數據
            
        Returns:
            Optional[str]: 解密後的數據
        """
        try:
            if not self.fernet:
                raise ValueError("加密器未初始化")
                
            # 解密數據
            decoded_data = base64.b64decode(encrypted_data)
            decrypted_data = self.fernet.decrypt(decoded_data)
            return decrypted_data.decode()
            
        except Exception as e:
            self.logger.error(f"解密數據失敗: {str(e)}")
            return None
    
    def generate_key(self, password: str, salt: bytes) -> bytes:
        """
        生成加密密鑰
        
        Args:
            password: 密碼
            salt: 鹽值
            
        Returns:
            bytes: 生成的密鑰
        """
        try:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
            return key
            
        except Exception as e:
            self.logger.error(f"生成密鑰失敗: {str(e)}")
            return None 