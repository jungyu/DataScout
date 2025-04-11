#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Cookie管理工具模組

提供Cookie的讀取、保存、更新和管理功能。
支持多種格式的Cookie處理和持久化存儲。
支持Cookie的加密、備份、恢復、驗證和分析。
"""

import os
import json
import time
import base64
import logging
import hashlib
import shutil
import zipfile
import csv
from typing import Dict, List, Optional, Union, Any, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class CookieManager:
    """Cookie管理工具類"""
    
    def __init__(
        self,
        cookie_dir: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
        encryption_key: Optional[str] = None
    ):
        """
        初始化Cookie管理器
        
        Args:
            cookie_dir: Cookie文件目錄
            logger: 日誌記錄器
            encryption_key: 加密密鑰
        """
        self.cookie_dir = cookie_dir or "cookies"
        self.logger = logger or logging.getLogger(__name__)
        self.encryption_key = encryption_key
        self.fernet = None
        if encryption_key:
            self._setup_encryption(encryption_key)
        os.makedirs(self.cookie_dir, exist_ok=True)
        
    def _setup_encryption(self, key: str) -> None:
        """
        設置加密
        
        Args:
            key: 加密密鑰
        """
        try:
            # 使用 PBKDF2 生成密鑰
            salt = b'cookie_manager_salt'
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key_bytes = kdf.derive(key.encode())
            self.fernet = Fernet(base64.urlsafe_b64encode(key_bytes))
            self.logger.info("已設置Cookie加密")
        except Exception as e:
            self.logger.error(f"設置加密失敗: {str(e)}")
            self.fernet = None
            
    def _encrypt_data(self, data: str) -> str:
        """
        加密數據
        
        Args:
            data: 要加密的數據
            
        Returns:
            加密後的數據
        """
        if not self.fernet:
            return data
        try:
            return self.fernet.encrypt(data.encode()).decode()
        except Exception as e:
            self.logger.error(f"加密數據失敗: {str(e)}")
            return data
            
    def _decrypt_data(self, data: str) -> str:
        """
        解密數據
        
        Args:
            data: 要解密的數據
            
        Returns:
            解密後的數據
        """
        if not self.fernet:
            return data
        try:
            return self.fernet.decrypt(data.encode()).decode()
        except Exception as e:
            self.logger.error(f"解密數據失敗: {str(e)}")
            return data
            
    def save_cookies(
        self,
        cookies: List[Dict[str, Any]],
        domain: str,
        session_id: Optional[str] = None
    ) -> bool:
        """
        保存Cookie
        
        Args:
            cookies: Cookie列表
            domain: 域名
            session_id: 會話ID
            
        Returns:
            是否保存成功
        """
        try:
            # 生成文件名
            filename = f"{domain}_{session_id or 'default'}.json"
            filepath = os.path.join(self.cookie_dir, filename)
            
            # 添加保存時間和元數據
            cookie_data = {
                'cookies': cookies,
                'timestamp': datetime.now().isoformat(),
                'domain': domain,
                'metadata': {
                    'version': '1.0',
                    'checksum': self._calculate_checksum(cookies)
                }
            }
            
            # 轉換為JSON並加密
            json_data = json.dumps(cookie_data, indent=4, ensure_ascii=False)
            if self.fernet:
                json_data = self._encrypt_data(json_data)
            
            # 保存到文件
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(json_data)
                
            self.logger.info(f"已保存Cookie到: {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"保存Cookie失敗: {str(e)}")
            return False
            
    def load_cookies(
        self,
        domain: str,
        session_id: Optional[str] = None,
        max_age: Optional[int] = None
    ) -> Optional[List[Dict[str, Any]]]:
        """
        加載Cookie
        
        Args:
            domain: 域名
            session_id: 會話ID
            max_age: Cookie最大有效期(秒)
            
        Returns:
            Cookie列表，如果加載失敗則返回None
        """
        try:
            # 生成文件名
            filename = f"{domain}_{session_id or 'default'}.json"
            filepath = os.path.join(self.cookie_dir, filename)
            
            if not os.path.exists(filepath):
                self.logger.warning(f"Cookie文件不存在: {filepath}")
                return None
                
            # 讀取文件
            with open(filepath, 'r', encoding='utf-8') as f:
                json_data = f.read()
                
            # 解密數據
            if self.fernet:
                json_data = self._decrypt_data(json_data)
                
            cookie_data = json.loads(json_data)
            
            # 驗證數據完整性
            if not self._verify_checksum(cookie_data['cookies'], cookie_data['metadata']['checksum']):
                self.logger.warning(f"Cookie數據完整性驗證失敗: {filepath}")
                return None
                
            # 檢查Cookie是否過期
            if max_age is not None:
                saved_time = datetime.fromisoformat(cookie_data['timestamp'])
                if (datetime.now() - saved_time).total_seconds() > max_age:
                    self.logger.warning(f"Cookie已過期: {filepath}")
                    return None
                    
            return cookie_data['cookies']
            
        except Exception as e:
            self.logger.error(f"加載Cookie失敗: {str(e)}")
            return None
            
    def _calculate_checksum(self, cookies: List[Dict[str, Any]]) -> str:
        """
        計算Cookie數據的校驗和
        
        Args:
            cookies: Cookie列表
            
        Returns:
            校驗和
        """
        try:
            # 將Cookie轉換為字符串
            cookie_str = json.dumps(cookies, sort_keys=True)
            # 計算MD5哈希
            return hashlib.md5(cookie_str.encode()).hexdigest()
        except Exception as e:
            self.logger.error(f"計算校驗和失敗: {str(e)}")
            return ""
            
    def _verify_checksum(self, cookies: List[Dict[str, Any]], checksum: str) -> bool:
        """
        驗證Cookie數據的校驗和
        
        Args:
            cookies: Cookie列表
            checksum: 校驗和
            
        Returns:
            是否驗證通過
        """
        try:
            return self._calculate_checksum(cookies) == checksum
        except Exception as e:
            self.logger.error(f"驗證校驗和失敗: {str(e)}")
            return False
            
    def backup_cookies(self, backup_dir: Optional[str] = None) -> bool:
        """
        備份Cookie文件
        
        Args:
            backup_dir: 備份目錄，如果為None則使用默認目錄
            
        Returns:
            是否備份成功
        """
        try:
            # 設置備份目錄
            if backup_dir is None:
                backup_dir = os.path.join(self.cookie_dir, "backups")
            os.makedirs(backup_dir, exist_ok=True)
            
            # 生成備份文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(backup_dir, f"cookies_backup_{timestamp}.zip")
            
            # 創建ZIP文件
            with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # 添加所有Cookie文件
                for filename in os.listdir(self.cookie_dir):
                    if filename.endswith('.json'):
                        filepath = os.path.join(self.cookie_dir, filename)
                        zipf.write(filepath, filename)
                        
            self.logger.info(f"已備份Cookie到: {backup_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"備份Cookie失敗: {str(e)}")
            return False
            
    def restore_cookies(self, backup_file: str) -> bool:
        """
        從備份恢復Cookie
        
        Args:
            backup_file: 備份文件路徑
            
        Returns:
            是否恢復成功
        """
        try:
            if not os.path.exists(backup_file):
                self.logger.error(f"備份文件不存在: {backup_file}")
                return False
                
            # 創建臨時目錄
            temp_dir = os.path.join(self.cookie_dir, "temp_restore")
            os.makedirs(temp_dir, exist_ok=True)
            
            try:
                # 解壓備份文件
                with zipfile.ZipFile(backup_file, 'r') as zipf:
                    zipf.extractall(temp_dir)
                    
                # 移動文件到Cookie目錄
                for filename in os.listdir(temp_dir):
                    if filename.endswith('.json'):
                        src = os.path.join(temp_dir, filename)
                        dst = os.path.join(self.cookie_dir, filename)
                        shutil.move(src, dst)
                        
                self.logger.info(f"已從備份恢復Cookie: {backup_file}")
                return True
                
            finally:
                # 清理臨時目錄
                shutil.rmtree(temp_dir, ignore_errors=True)
                
        except Exception as e:
            self.logger.error(f"恢復Cookie失敗: {str(e)}")
            return False
            
    def validate_cookies(self, cookies: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
        """
        驗證Cookie
        
        Args:
            cookies: Cookie列表
            
        Returns:
            (是否有效, 錯誤列表)
        """
        errors = []
        
        for cookie in cookies:
            # 檢查必要字段
            required_fields = ['name', 'value', 'domain']
            for field in required_fields:
                if field not in cookie:
                    errors.append(f"缺少必要字段: {field}")
                    
            # 檢查過期時間
            if 'expires' in cookie:
                try:
                    expires = datetime.fromtimestamp(cookie['expires'])
                    if expires < datetime.now():
                        errors.append(f"Cookie已過期: {cookie.get('name', 'unknown')}")
                except Exception:
                    errors.append(f"無效的過期時間: {cookie.get('name', 'unknown')}")
                    
            # 檢查域名格式
            if 'domain' in cookie:
                domain = cookie['domain']
                if not domain.startswith('.'):
                    errors.append(f"域名格式錯誤: {domain}")
                    
        return len(errors) == 0, errors
        
    def get_cookie_stats(self) -> Dict[str, Any]:
        """
        獲取Cookie統計信息
        
        Returns:
            統計信息
        """
        try:
            stats = {
                'total_files': 0,
                'total_cookies': 0,
                'domains': {},
                'expired_cookies': 0,
                'secure_cookies': 0,
                'http_only_cookies': 0
            }
            
            # 遍歷所有Cookie文件
            for filename in os.listdir(self.cookie_dir):
                if not filename.endswith('.json'):
                    continue
                    
                stats['total_files'] += 1
                filepath = os.path.join(self.cookie_dir, filename)
                
                try:
                    # 讀取Cookie文件
                    with open(filepath, 'r', encoding='utf-8') as f:
                        json_data = f.read()
                        
                    # 解密數據
                    if self.fernet:
                        json_data = self._decrypt_data(json_data)
                        
                    cookie_data = json.loads(json_data)
                    cookies = cookie_data['cookies']
                    domain = cookie_data['domain']
                    
                    # 更新統計信息
                    stats['total_cookies'] += len(cookies)
                    stats['domains'][domain] = stats['domains'].get(domain, 0) + len(cookies)
                    
                    for cookie in cookies:
                        if cookie.get('secure'):
                            stats['secure_cookies'] += 1
                        if cookie.get('httpOnly'):
                            stats['http_only_cookies'] += 1
                        if 'expires' in cookie:
                            try:
                                expires = datetime.fromtimestamp(cookie['expires'])
                                if expires < datetime.now():
                                    stats['expired_cookies'] += 1
                            except Exception:
                                pass
                                
                except Exception as e:
                    self.logger.error(f"處理Cookie文件失敗 {filepath}: {str(e)}")
                    
            return stats
            
        except Exception as e:
            self.logger.error(f"獲取Cookie統計信息失敗: {str(e)}")
            return {}
            
    def update_cookies(
        self,
        cookies: List[Dict[str, Any]],
        domain: str,
        session_id: Optional[str] = None
    ) -> bool:
        """
        更新Cookie
        
        Args:
            cookies: 新的Cookie列表
            domain: 域名
            session_id: 會話ID
            
        Returns:
            是否更新成功
        """
        try:
            # 加載現有Cookie
            existing_cookies = self.load_cookies(domain, session_id) or []
            
            # 更新Cookie
            updated_cookies = []
            cookie_dict = {cookie['name']: cookie for cookie in existing_cookies}
            
            for cookie in cookies:
                name = cookie['name']
                if name in cookie_dict:
                    # 更新現有Cookie
                    cookie_dict[name].update(cookie)
                    updated_cookies.append(cookie_dict[name])
                else:
                    # 添加新Cookie
                    updated_cookies.append(cookie)
                    
            # 保存更新後的Cookie
            return self.save_cookies(updated_cookies, domain, session_id)
            
        except Exception as e:
            self.logger.error(f"更新Cookie失敗: {str(e)}")
            return False
            
    def clear_cookies(
        self,
        domain: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> bool:
        """
        清除Cookie
        
        Args:
            domain: 域名，如果為None則清除所有Cookie
            session_id: 會話ID，如果為None則清除所有會話
            
        Returns:
            是否清除成功
        """
        try:
            if domain is None:
                # 清除所有Cookie
                for filename in os.listdir(self.cookie_dir):
                    if filename.endswith('.json'):
                        os.remove(os.path.join(self.cookie_dir, filename))
                self.logger.info("已清除所有Cookie")
                return True
                
            # 清除指定域名的Cookie
            pattern = f"{domain}_{session_id or '*'}.json"
            for filename in os.listdir(self.cookie_dir):
                if filename.startswith(f"{domain}_") and (session_id is None or filename.endswith(f"_{session_id}.json")):
                    os.remove(os.path.join(self.cookie_dir, filename))
                    
            self.logger.info(f"已清除Cookie: {domain}")
            return True
            
        except Exception as e:
            self.logger.error(f"清除Cookie失敗: {str(e)}")
            return False
            
    def get_cookie_value(
        self,
        cookies: List[Dict[str, Any]],
        name: str,
        default: Any = None
    ) -> Any:
        """
        獲取Cookie值
        
        Args:
            cookies: Cookie列表
            name: Cookie名稱
            default: 默認值
            
        Returns:
            Cookie值
        """
        try:
            for cookie in cookies:
                if cookie['name'] == name:
                    return cookie['value']
            return default
        except Exception as e:
            self.logger.error(f"獲取Cookie值失敗: {str(e)}")
            return default
            
    def set_cookie_value(
        self,
        cookies: List[Dict[str, Any]],
        name: str,
        value: Any,
        domain: Optional[str] = None,
        path: str = "/",
        secure: bool = False,
        http_only: bool = False,
        max_age: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        設置Cookie值
        
        Args:
            cookies: Cookie列表
            name: Cookie名稱
            value: Cookie值
            domain: 域名
            path: 路徑
            secure: 是否僅HTTPS
            http_only: 是否僅HTTP
            max_age: 最大有效期(秒)
            
        Returns:
            更新後的Cookie列表
        """
        try:
            # 創建新Cookie
            cookie = {
                'name': name,
                'value': value,
                'path': path,
                'secure': secure,
                'httpOnly': http_only
            }
            
            if domain:
                cookie['domain'] = domain
            if max_age:
                cookie['expires'] = int(time.time() + max_age)
                
            # 更新或添加Cookie
            updated = False
            for i, existing_cookie in enumerate(cookies):
                if existing_cookie['name'] == name:
                    cookies[i] = cookie
                    updated = True
                    break
                    
            if not updated:
                cookies.append(cookie)
                
            return cookies
            
        except Exception as e:
            self.logger.error(f"設置Cookie值失敗: {str(e)}")
            return cookies
            
    def remove_cookie(
        self,
        cookies: List[Dict[str, Any]],
        name: str
    ) -> List[Dict[str, Any]]:
        """
        移除Cookie
        
        Args:
            cookies: Cookie列表
            name: Cookie名稱
            
        Returns:
            更新後的Cookie列表
        """
        try:
            return [cookie for cookie in cookies if cookie['name'] != name]
        except Exception as e:
            self.logger.error(f"移除Cookie失敗: {str(e)}")
            return cookies
            
    def list_cookies(self, domain: Optional[str] = None) -> List[str]:
        """
        列出Cookie文件
        
        Args:
            domain: 域名，如果為None則列出所有Cookie文件
            
        Returns:
            Cookie文件列表
        """
        try:
            if domain is None:
                return [f for f in os.listdir(self.cookie_dir) if f.endswith('.json')]
            return [f for f in os.listdir(self.cookie_dir) if f.startswith(f"{domain}_") and f.endswith('.json')]
        except Exception as e:
            self.logger.error(f"列出Cookie文件失敗: {str(e)}")
            return []
            
    def get_cookie_info(self, filepath: str) -> Optional[Dict[str, Any]]:
        """
        獲取Cookie文件信息
        
        Args:
            filepath: Cookie文件路徑
            
        Returns:
            Cookie文件信息，如果獲取失敗則返回None
        """
        try:
            if not os.path.exists(filepath):
                return None
                
            # 讀取文件
            with open(filepath, 'r', encoding='utf-8') as f:
                json_data = f.read()
                
            # 解密數據
            if self.fernet:
                json_data = self._decrypt_data(json_data)
                
            cookie_data = json.loads(json_data)
            
            return {
                'domain': cookie_data['domain'],
                'timestamp': cookie_data['timestamp'],
                'cookie_count': len(cookie_data['cookies']),
                'file_size': os.path.getsize(filepath),
                'last_modified': datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"獲取Cookie文件信息失敗: {str(e)}")
            return None
            
    def export_cookies(self, output_file: str, format: str = 'json',
                      domain: Optional[str] = None) -> bool:
        """
        導出Cookie
        
        Args:
            output_file: 輸出文件路徑
            format: 輸出格式（json或csv）
            domain: 域名，如果為None則導出所有Cookie
            
        Returns:
            是否導出成功
        """
        try:
            # 收集所有Cookie
            all_cookies = []
            cookie_files = self.list_cookies(domain)
            
            for filename in cookie_files:
                filepath = os.path.join(self.cookie_dir, filename)
                cookies = self.load_cookies(
                    domain=filename.split('_')[0],
                    session_id=filename.split('_')[1].replace('.json', '')
                )
                if cookies:
                    all_cookies.extend(cookies)
                    
            # 導出Cookie
            output_path = Path(output_file)
            if format.lower() == 'json':
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(all_cookies, f, indent=2, ensure_ascii=False)
            elif format.lower() == 'csv':
                with open(output_path, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=['name', 'value', 'domain', 'path'])
                    writer.writeheader()
                    writer.writerows(all_cookies)
            else:
                raise ValueError(f"不支持的輸出格式: {format}")
                
            self.logger.info(f"已導出Cookie到: {output_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"導出Cookie失敗: {str(e)}")
            return False
            
    def import_cookies(self, input_file: str, format: str = 'json',
                      domain: Optional[str] = None) -> bool:
        """
        導入Cookie
        
        Args:
            input_file: 輸入文件路徑
            format: 輸入格式（json或csv）
            domain: 域名，如果為None則使用文件中的域名
            
        Returns:
            是否導入成功
        """
        try:
            # 讀取Cookie
            input_path = Path(input_file)
            if format.lower() == 'json':
                with open(input_path, 'r', encoding='utf-8') as f:
                    cookies = json.load(f)
            elif format.lower() == 'csv':
                cookies = []
                with open(input_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        cookies.append(row)
            else:
                raise ValueError(f"不支持的輸入格式: {format}")
                
            # 保存Cookie
            if domain:
                return self.save_cookies(cookies, domain)
            else:
                # 按域名分組保存
                cookies_by_domain = {}
                for cookie in cookies:
                    cookie_domain = cookie.get('domain', '')
                    if cookie_domain not in cookies_by_domain:
                        cookies_by_domain[cookie_domain] = []
                    cookies_by_domain[cookie_domain].append(cookie)
                    
                success = True
                for cookie_domain, domain_cookies in cookies_by_domain.items():
                    if not self.save_cookies(domain_cookies, cookie_domain):
                        success = False
                return success
                
        except Exception as e:
            self.logger.error(f"導入Cookie失敗: {str(e)}")
            return False
            
    def sync_cookies(self, other_manager: 'CookieManager',
                    domain: Optional[str] = None) -> bool:
        """
        同步Cookie到另一個管理器
        
        Args:
            other_manager: 另一個Cookie管理器
            domain: 域名，如果為None則同步所有Cookie
            
        Returns:
            是否同步成功
        """
        try:
            cookie_files = self.list_cookies(domain)
            success = True
            
            for filename in cookie_files:
                domain = filename.split('_')[0]
                session_id = filename.split('_')[1].replace('.json', '')
                
                # 讀取Cookie
                cookies = self.load_cookies(domain, session_id)
                if cookies:
                    # 保存到另一個管理器
                    if not other_manager.save_cookies(cookies, domain, session_id):
                        success = False
                        
            return success
            
        except Exception as e:
            self.logger.error(f"同步Cookie失敗: {str(e)}")
            return False
            
    def get_cookie_history(self, domain: str,
                          session_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        獲取Cookie歷史記錄
        
        Args:
            domain: 域名
            session_id: 會話ID
            
        Returns:
            Cookie歷史記錄列表
        """
        try:
            history = []
            pattern = f"{domain}_{session_id or '*'}.json"
            
            for filename in os.listdir(self.cookie_dir):
                if filename.startswith(f"{domain}_") and (session_id is None or filename.endswith(f"_{session_id}.json")):
                    filepath = os.path.join(self.cookie_dir, filename)
                    info = self.get_cookie_info(filepath)
                    if info:
                        history.append(info)
                        
            # 按時間排序
            history.sort(key=lambda x: x['timestamp'], reverse=True)
            return history
            
        except Exception as e:
            self.logger.error(f"獲取Cookie歷史記錄失敗: {str(e)}")
            return []
            
    def analyze_cookies(self, domain: Optional[str] = None) -> Dict[str, Any]:
        """
        分析Cookie
        
        Args:
            domain: 域名，如果為None則分析所有Cookie
            
        Returns:
            分析結果
        """
        try:
            analysis = {
                'total_cookies': 0,
                'domains': {},
                'expired_cookies': 0,
                'secure_cookies': 0,
                'http_only_cookies': 0,
                'cookie_types': {},
                'expiration_distribution': {
                    'expired': 0,
                    'today': 0,
                    'week': 0,
                    'month': 0,
                    'year': 0,
                    'never': 0
                }
            }
            
            cookie_files = self.list_cookies(domain)
            for filename in cookie_files:
                file_domain = filename.split('_')[0]
                cookies = self.load_cookies(file_domain)
                if not cookies:
                    continue
                    
                # 更新統計信息
                analysis['total_cookies'] += len(cookies)
                analysis['domains'][file_domain] = analysis['domains'].get(file_domain, 0) + len(cookies)
                
                for cookie in cookies:
                    # 檢查安全標誌
                    if cookie.get('secure'):
                        analysis['secure_cookies'] += 1
                    if cookie.get('httpOnly'):
                        analysis['http_only_cookies'] += 1
                        
                    # 檢查過期時間
                    if 'expires' in cookie:
                        try:
                            expires = datetime.fromtimestamp(cookie['expires'])
                            now = datetime.now()
                            
                            if expires < now:
                                analysis['expired_cookies'] += 1
                                analysis['expiration_distribution']['expired'] += 1
                            elif expires.date() == now.date():
                                analysis['expiration_distribution']['today'] += 1
                            elif expires < now + timedelta(days=7):
                                analysis['expiration_distribution']['week'] += 1
                            elif expires < now + timedelta(days=30):
                                analysis['expiration_distribution']['month'] += 1
                            elif expires < now + timedelta(days=365):
                                analysis['expiration_distribution']['year'] += 1
                            else:
                                analysis['expiration_distribution']['never'] += 1
                        except Exception:
                            pass
                            
                    # 統計Cookie類型
                    cookie_type = cookie.get('name', '').split('_')[0]
                    analysis['cookie_types'][cookie_type] = analysis['cookie_types'].get(cookie_type, 0) + 1
                    
            return analysis
            
        except Exception as e:
            self.logger.error(f"分析Cookie失敗: {str(e)}")
            return {} 