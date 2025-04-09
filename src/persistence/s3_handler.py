#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
AWS S3 存儲模組

此模組提供 AWS S3 存儲功能，支持文件的上傳、下載、刪除等操作。
"""

import logging
from typing import Dict, List, Optional, Union, BinaryIO
from dataclasses import dataclass, field
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
from pathlib import Path

@dataclass
class S3Config:
    """S3 配置類"""
    access_key_id: str
    secret_access_key: str
    region_name: str = "us-east-1"
    bucket_name: Optional[str] = None
    endpoint_url: Optional[str] = None
    timeout: int = 30
    retry_count: int = 3
    retry_delay: int = 1
    default_prefix: str = ""
    default_content_type: str = "application/octet-stream"
    default_acl: str = "private"
    default_storage_class: str = "STANDARD"
    default_metadata: Dict = field(default_factory=dict)

class S3Handler:
    """S3 處理類"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化 S3 處理器
        
        Args:
            config: 配置字典
        """
        self.logger = logging.getLogger(__name__)
        
        # 加載配置
        self.config = S3Config(**(config or {}))
        
        # 初始化客戶端
        self._client = None
        
        # 連接 S3
        self._connect()
        
        self.logger.info("S3 處理器初始化完成")
    
    def _connect(self) -> None:
        """建立 S3 連接"""
        try:
            # 創建客戶端
            self._client = boto3.client(
                's3',
                aws_access_key_id=self.config.access_key_id,
                aws_secret_access_key=self.config.secret_access_key,
                region_name=self.config.region_name,
                endpoint_url=self.config.endpoint_url
            )
            
            # 測試連接
            self._client.list_buckets()
            
            self.logger.info("已連接到 S3")
        
        except Exception as e:
            self.logger.error(f"S3 連接失敗: {str(e)}")
            raise
    
    def upload_file(self, file_path: Union[str, Path], key: Optional[str] = None,
                   bucket: Optional[str] = None, content_type: Optional[str] = None,
                   metadata: Optional[Dict] = None) -> bool:
        """
        上傳文件
        
        Args:
            file_path: 本地文件路徑
            key: S3 對象鍵，為None時使用文件名
            bucket: 存儲桶名稱，為None時使用默認存儲桶
            content_type: 內容類型，為None時使用默認類型
            metadata: 元數據，為None時使用默認元數據
            
        Returns:
            是否成功上傳
        """
        try:
            # 轉換文件路徑
            file_path = Path(file_path)
            
            # 確定對象鍵
            if key is None:
                key = str(file_path.name)
            
            # 添加前綴
            if self.config.default_prefix:
                key = f"{self.config.default_prefix}/{key}"
            
            # 確定存儲桶
            bucket = bucket or self.config.bucket_name
            if not bucket:
                raise ValueError("未指定存儲桶")
            
            # 確定內容類型
            content_type = content_type or self.config.default_content_type
            
            # 確定元數據
            metadata = metadata or self.config.default_metadata
            
            # 上傳文件
            self._client.upload_file(
                Filename=str(file_path),
                Bucket=bucket,
                Key=key,
                ExtraArgs={
                    'ContentType': content_type,
                    'Metadata': metadata,
                    'ACL': self.config.default_acl,
                    'StorageClass': self.config.default_storage_class
                }
            )
            
            self.logger.debug(f"已上傳文件: {key} -> {bucket}")
            return True
        
        except Exception as e:
            self.logger.error(f"上傳文件失敗: {str(e)}")
            return False
    
    def upload_fileobj(self, fileobj: BinaryIO, key: str,
                      bucket: Optional[str] = None, content_type: Optional[str] = None,
                      metadata: Optional[Dict] = None) -> bool:
        """
        上傳文件對象
        
        Args:
            fileobj: 文件對象
            key: S3 對象鍵
            bucket: 存儲桶名稱，為None時使用默認存儲桶
            content_type: 內容類型，為None時使用默認類型
            metadata: 元數據，為None時使用默認元數據
            
        Returns:
            是否成功上傳
        """
        try:
            # 添加前綴
            if self.config.default_prefix:
                key = f"{self.config.default_prefix}/{key}"
            
            # 確定存儲桶
            bucket = bucket or self.config.bucket_name
            if not bucket:
                raise ValueError("未指定存儲桶")
            
            # 確定內容類型
            content_type = content_type or self.config.default_content_type
            
            # 確定元數據
            metadata = metadata or self.config.default_metadata
            
            # 上傳文件對象
            self._client.upload_fileobj(
                fileobj,
                Bucket=bucket,
                Key=key,
                ExtraArgs={
                    'ContentType': content_type,
                    'Metadata': metadata,
                    'ACL': self.config.default_acl,
                    'StorageClass': self.config.default_storage_class
                }
            )
            
            self.logger.debug(f"已上傳文件對象: {key} -> {bucket}")
            return True
        
        except Exception as e:
            self.logger.error(f"上傳文件對象失敗: {str(e)}")
            return False
    
    def download_file(self, key: str, file_path: Union[str, Path],
                     bucket: Optional[str] = None) -> bool:
        """
        下載文件
        
        Args:
            key: S3 對象鍵
            file_path: 本地文件路徑
            bucket: 存儲桶名稱，為None時使用默認存儲桶
            
        Returns:
            是否成功下載
        """
        try:
            # 轉換文件路徑
            file_path = Path(file_path)
            
            # 添加前綴
            if self.config.default_prefix:
                key = f"{self.config.default_prefix}/{key}"
            
            # 確定存儲桶
            bucket = bucket or self.config.bucket_name
            if not bucket:
                raise ValueError("未指定存儲桶")
            
            # 下載文件
            self._client.download_file(
                Bucket=bucket,
                Key=key,
                Filename=str(file_path)
            )
            
            self.logger.debug(f"已下載文件: {bucket}/{key} -> {file_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"下載文件失敗: {str(e)}")
            return False
    
    def download_fileobj(self, key: str, fileobj: BinaryIO,
                        bucket: Optional[str] = None) -> bool:
        """
        下載文件對象
        
        Args:
            key: S3 對象鍵
            fileobj: 文件對象
            bucket: 存儲桶名稱，為None時使用默認存儲桶
            
        Returns:
            是否成功下載
        """
        try:
            # 添加前綴
            if self.config.default_prefix:
                key = f"{self.config.default_prefix}/{key}"
            
            # 確定存儲桶
            bucket = bucket or self.config.bucket_name
            if not bucket:
                raise ValueError("未指定存儲桶")
            
            # 下載文件對象
            self._client.download_fileobj(
                Bucket=bucket,
                Key=key,
                Fileobj=fileobj
            )
            
            self.logger.debug(f"已下載文件對象: {bucket}/{key}")
            return True
        
        except Exception as e:
            self.logger.error(f"下載文件對象失敗: {str(e)}")
            return False
    
    def delete_file(self, key: str, bucket: Optional[str] = None) -> bool:
        """
        刪除文件
        
        Args:
            key: S3 對象鍵
            bucket: 存儲桶名稱，為None時使用默認存儲桶
            
        Returns:
            是否成功刪除
        """
        try:
            # 添加前綴
            if self.config.default_prefix:
                key = f"{self.config.default_prefix}/{key}"
            
            # 確定存儲桶
            bucket = bucket or self.config.bucket_name
            if not bucket:
                raise ValueError("未指定存儲桶")
            
            # 刪除文件
            self._client.delete_object(
                Bucket=bucket,
                Key=key
            )
            
            self.logger.debug(f"已刪除文件: {bucket}/{key}")
            return True
        
        except Exception as e:
            self.logger.error(f"刪除文件失敗: {str(e)}")
            return False
    
    def list_files(self, prefix: Optional[str] = None, bucket: Optional[str] = None,
                  max_keys: int = 1000) -> List[Dict]:
        """
        列出文件
        
        Args:
            prefix: 前綴，為None時使用默認前綴
            bucket: 存儲桶名稱，為None時使用默認存儲桶
            max_keys: 最大返回數量
            
        Returns:
            文件列表
        """
        try:
            # 確定前綴
            if prefix is None:
                prefix = self.config.default_prefix
            elif self.config.default_prefix:
                prefix = f"{self.config.default_prefix}/{prefix}"
            
            # 確定存儲桶
            bucket = bucket or self.config.bucket_name
            if not bucket:
                raise ValueError("未指定存儲桶")
            
            # 列出文件
            response = self._client.list_objects_v2(
                Bucket=bucket,
                Prefix=prefix,
                MaxKeys=max_keys
            )
            
            files = []
            for obj in response.get("Contents", []):
                files.append({
                    "key": obj["Key"],
                    "size": obj["Size"],
                    "last_modified": obj["LastModified"],
                    "etag": obj["ETag"],
                    "storage_class": obj["StorageClass"]
                })
            
            self.logger.debug(f"已列出文件: {len(files)} 個")
            return files
        
        except Exception as e:
            self.logger.error(f"列出文件失敗: {str(e)}")
            return []
    
    def get_file_info(self, key: str, bucket: Optional[str] = None) -> Optional[Dict]:
        """
        獲取文件信息
        
        Args:
            key: S3 對象鍵
            bucket: 存儲桶名稱，為None時使用默認存儲桶
            
        Returns:
            文件信息，失敗時返回None
        """
        try:
            # 添加前綴
            if self.config.default_prefix:
                key = f"{self.config.default_prefix}/{key}"
            
            # 確定存儲桶
            bucket = bucket or self.config.bucket_name
            if not bucket:
                raise ValueError("未指定存儲桶")
            
            # 獲取文件信息
            response = self._client.head_object(
                Bucket=bucket,
                Key=key
            )
            
            info = {
                "key": key,
                "size": response["ContentLength"],
                "last_modified": response["LastModified"],
                "etag": response["ETag"],
                "content_type": response["ContentType"],
                "metadata": response.get("Metadata", {})
            }
            
            self.logger.debug(f"已獲取文件信息: {key}")
            return info
        
        except Exception as e:
            self.logger.error(f"獲取文件信息失敗: {str(e)}")
            return None
    
    def create_bucket(self, bucket: str, region: Optional[str] = None,
                     acl: Optional[str] = None) -> bool:
        """
        創建存儲桶
        
        Args:
            bucket: 存儲桶名稱
            region: 區域，為None時使用默認區域
            acl: 訪問控制，為None時使用默認控制
            
        Returns:
            是否成功創建
        """
        try:
            # 確定區域
            region = region or self.config.region_name
            
            # 確定訪問控制
            acl = acl or self.config.default_acl
            
            # 創建存儲桶
            self._client.create_bucket(
                Bucket=bucket,
                CreateBucketConfiguration={
                    'LocationConstraint': region
                },
                ACL=acl
            )
            
            self.logger.debug(f"已創建存儲桶: {bucket}")
            return True
        
        except Exception as e:
            self.logger.error(f"創建存儲桶失敗: {str(e)}")
            return False
    
    def delete_bucket(self, bucket: str, force: bool = False) -> bool:
        """
        刪除存儲桶
        
        Args:
            bucket: 存儲桶名稱
            force: 是否強制刪除（即使存儲桶不為空）
            
        Returns:
            是否成功刪除
        """
        try:
            if force:
                # 列出所有文件
                files = self.list_files(bucket=bucket)
                
                # 刪除所有文件
                for file in files:
                    self.delete_file(file["key"], bucket)
            
            # 刪除存儲桶
            self._client.delete_bucket(Bucket=bucket)
            
            self.logger.debug(f"已刪除存儲桶: {bucket}")
            return True
        
        except Exception as e:
            self.logger.error(f"刪除存儲桶失敗: {str(e)}")
            return False
    
    def list_buckets(self) -> List[Dict]:
        """
        列出存儲桶
        
        Returns:
            存儲桶列表
        """
        try:
            # 列出存儲桶
            response = self._client.list_buckets()
            
            buckets = []
            for bucket in response["Buckets"]:
                buckets.append({
                    "name": bucket["Name"],
                    "created": bucket["CreationDate"]
                })
            
            self.logger.debug(f"已列出存儲桶: {len(buckets)} 個")
            return buckets
        
        except Exception as e:
            self.logger.error(f"列出存儲桶失敗: {str(e)}")
            return []
    
    def get_bucket_info(self, bucket: str) -> Optional[Dict]:
        """
        獲取存儲桶信息
        
        Args:
            bucket: 存儲桶名稱
            
        Returns:
            存儲桶信息，失敗時返回None
        """
        try:
            # 獲取存儲桶信息
            response = self._client.get_bucket_location(Bucket=bucket)
            
            info = {
                "name": bucket,
                "location": response["LocationConstraint"]
            }
            
            self.logger.debug(f"已獲取存儲桶信息: {bucket}")
            return info
        
        except Exception as e:
            self.logger.error(f"獲取存儲桶信息失敗: {str(e)}")
            return None
    
    def close(self) -> None:
        """關閉 S3 連接"""
        try:
            if self._client:
                self._client = None
                
                self.logger.info("已關閉 S3 連接")
        
        except Exception as e:
            self.logger.error(f"關閉 S3 連接失敗: {str(e)}")
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close() 