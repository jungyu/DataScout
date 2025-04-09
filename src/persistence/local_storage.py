#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
本地存儲模組

此模組提供本地文件系統的數據存儲功能，支持 JSON 和 CSV 格式。
"""

import os
import json
import csv
import logging
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime

@dataclass
class LocalStorageConfig:
    """本地存儲配置類"""
    data_dir: str = "data"
    default_collection: str = "crawl_data"
    timestamp_field: str = "timestamp"
    id_field: str = "id"
    batch_size: int = 100
    retry_count: int = 3
    retry_delay: int = 1
    ensure_ascii: bool = False
    indent: int = 2
    encoding: str = "utf-8"

class LocalStorage:
    """本地存儲類"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化本地存儲
        
        Args:
            config: 配置字典
        """
        self.logger = logging.getLogger(__name__)
        
        # 加載配置
        self.config = LocalStorageConfig(**(config or {}))
        
        # 初始化存儲路徑
        self.data_dir = Path(self.config.data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.info("本地存儲初始化完成")
    
    def save_json(self, data: Dict, collection: Optional[str] = None) -> bool:
        """
        保存 JSON 數據
        
        Args:
            data: 數據字典
            collection: 集合名稱，為None時使用默認值
            
        Returns:
            是否成功保存
        """
        try:
            # 添加時間戳
            if self.config.timestamp_field not in data:
                data[self.config.timestamp_field] = datetime.now().isoformat()
            
            # 添加ID
            if self.config.id_field not in data:
                data[self.config.id_field] = str(int(datetime.now().timestamp() * 1000))
            
            # 確定存儲路徑
            collection = collection or self.config.default_collection
            collection_dir = self.data_dir / collection
            collection_dir.mkdir(parents=True, exist_ok=True)
            
            # 生成文件名
            file_name = f"{data[self.config.id_field]}.json"
            file_path = collection_dir / file_name
            
            # 保存數據
            with open(file_path, "w", encoding=self.config.encoding) as f:
                json.dump(data, f, ensure_ascii=self.config.ensure_ascii, indent=self.config.indent)
            
            self.logger.debug(f"已保存 JSON 數據到: {file_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"保存 JSON 數據失敗: {str(e)}")
            return False
    
    def save_csv(self, data_list: List[Dict], collection: Optional[str] = None, file_name: Optional[str] = None) -> bool:
        """
        保存 CSV 數據
        
        Args:
            data_list: 數據字典列表
            collection: 集合名稱，為None時使用默認值
            file_name: 文件名，為None時自動生成
            
        Returns:
            是否成功保存
        """
        try:
            if not data_list:
                self.logger.warning("沒有數據需要保存")
                return False
            
            # 確定存儲路徑
            collection = collection or self.config.default_collection
            collection_dir = self.data_dir / collection
            collection_dir.mkdir(parents=True, exist_ok=True)
            
            # 生成文件名
            if file_name is None:
                timestamp = int(datetime.now().timestamp())
                file_name = f"{collection}_{timestamp}.csv"
            
            file_path = collection_dir / file_name
            
            # 獲取所有字段
            all_fields = set()
            for data in data_list:
                all_fields.update(data.keys())
            
            # 移除一些不需要的系統字段
            system_fields = {"notion_page_id"}
            fields = sorted(list(all_fields - system_fields))
            
            # 保存數據
            with open(file_path, "w", newline="", encoding=self.config.encoding) as f:
                writer = csv.DictWriter(f, fieldnames=fields)
                writer.writeheader()
                
                for data in data_list:
                    # 轉換複雜字段為字符串
                    row = {}
                    for field in fields:
                        value = data.get(field)
                        if isinstance(value, (dict, list)):
                            row[field] = json.dumps(value, ensure_ascii=self.config.ensure_ascii)
                        else:
                            row[field] = value
                    
                    writer.writerow(row)
            
            self.logger.debug(f"已保存 CSV 數據到: {file_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"保存 CSV 數據失敗: {str(e)}")
            return False
    
    def load_json(self, collection: str, file_name: str) -> Optional[Dict]:
        """
        加載 JSON 數據
        
        Args:
            collection: 集合名稱
            file_name: 文件名
            
        Returns:
            數據字典，失敗時返回None
        """
        try:
            # 確定文件路徑
            file_path = self.data_dir / collection / file_name
            
            if not file_path.exists():
                self.logger.warning(f"文件不存在: {file_path}")
                return None
            
            # 讀取數據
            with open(file_path, "r", encoding=self.config.encoding) as f:
                data = json.load(f)
            
            self.logger.debug(f"已加載 JSON 數據: {file_path}")
            return data
        
        except Exception as e:
            self.logger.error(f"加載 JSON 數據失敗: {str(e)}")
            return None
    
    def load_csv(self, collection: str, file_name: str) -> List[Dict]:
        """
        加載 CSV 數據
        
        Args:
            collection: 集合名稱
            file_name: 文件名
            
        Returns:
            數據字典列表
        """
        try:
            # 確定文件路徑
            file_path = self.data_dir / collection / file_name
            
            if not file_path.exists():
                self.logger.warning(f"文件不存在: {file_path}")
                return []
            
            # 讀取數據
            data_list = []
            with open(file_path, "r", newline="", encoding=self.config.encoding) as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # 嘗試解析JSON字符串
                    for key, value in row.items():
                        try:
                            if value.startswith("{") or value.startswith("["):
                                row[key] = json.loads(value)
                        except:
                            pass
                    
                    data_list.append(row)
            
            self.logger.debug(f"已加載 CSV 數據: {file_path}")
            return data_list
        
        except Exception as e:
            self.logger.error(f"加載 CSV 數據失敗: {str(e)}")
            return []
    
    def list_files(self, collection: str, pattern: str = "*.json") -> List[str]:
        """
        列出集合中的文件
        
        Args:
            collection: 集合名稱
            pattern: 文件匹配模式
            
        Returns:
            文件名列表
        """
        try:
            # 確定集合路徑
            collection_dir = self.data_dir / collection
            
            if not collection_dir.exists():
                self.logger.warning(f"集合目錄不存在: {collection_dir}")
                return []
            
            # 獲取文件列表
            files = [f.name for f in collection_dir.glob(pattern)]
            
            self.logger.debug(f"已列出集合 {collection} 中的文件: {len(files)} 個")
            return files
        
        except Exception as e:
            self.logger.error(f"列出文件失敗: {str(e)}")
            return []
    
    def delete_file(self, collection: str, file_name: str) -> bool:
        """
        刪除文件
        
        Args:
            collection: 集合名稱
            file_name: 文件名
            
        Returns:
            是否成功刪除
        """
        try:
            # 確定文件路徑
            file_path = self.data_dir / collection / file_name
            
            if not file_path.exists():
                self.logger.warning(f"文件不存在: {file_path}")
                return False
            
            # 刪除文件
            file_path.unlink()
            
            self.logger.debug(f"已刪除文件: {file_path}")
            return True
        
        except Exception as e:
            self.logger.error(f"刪除文件失敗: {str(e)}")
            return False
    
    def get_collections(self) -> List[str]:
        """
        獲取所有集合名稱
        
        Returns:
            集合名稱列表
        """
        try:
            # 獲取目錄列表
            collections = [d.name for d in self.data_dir.iterdir() if d.is_dir()]
            
            self.logger.debug(f"已獲取集合列表: {len(collections)} 個")
            return collections
        
        except Exception as e:
            self.logger.error(f"獲取集合列表失敗: {str(e)}")
            return []
    
    def create_collection(self, collection: str) -> bool:
        """
        創建集合
        
        Args:
            collection: 集合名稱
            
        Returns:
            是否成功創建
        """
        try:
            # 確定集合路徑
            collection_dir = self.data_dir / collection
            
            if collection_dir.exists():
                self.logger.warning(f"集合已存在: {collection_dir}")
                return False
            
            # 創建目錄
            collection_dir.mkdir(parents=True, exist_ok=True)
            
            self.logger.debug(f"已創建集合: {collection_dir}")
            return True
        
        except Exception as e:
            self.logger.error(f"創建集合失敗: {str(e)}")
            return False
    
    def delete_collection(self, collection: str) -> bool:
        """
        刪除集合
        
        Args:
            collection: 集合名稱
            
        Returns:
            是否成功刪除
        """
        try:
            # 確定集合路徑
            collection_dir = self.data_dir / collection
            
            if not collection_dir.exists():
                self.logger.warning(f"集合不存在: {collection_dir}")
                return False
            
            # 刪除目錄及其內容
            for file_path in collection_dir.iterdir():
                file_path.unlink()
            collection_dir.rmdir()
            
            self.logger.debug(f"已刪除集合: {collection_dir}")
            return True
        
        except Exception as e:
            self.logger.error(f"刪除集合失敗: {str(e)}")
            return False
    
    def get_file_info(self, collection: str, file_name: str) -> Optional[Dict]:
        """
        獲取文件信息
        
        Args:
            collection: 集合名稱
            file_name: 文件名
            
        Returns:
            文件信息字典，失敗時返回None
        """
        try:
            # 確定文件路徑
            file_path = self.data_dir / collection / file_name
            
            if not file_path.exists():
                self.logger.warning(f"文件不存在: {file_path}")
                return None
            
            # 獲取文件信息
            stat = file_path.stat()
            
            info = {
                "name": file_path.name,
                "size": stat.st_size,
                "created_time": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "accessed_time": datetime.fromtimestamp(stat.st_atime).isoformat(),
            }
            
            self.logger.debug(f"已獲取文件信息: {file_path}")
            return info
        
        except Exception as e:
            self.logger.error(f"獲取文件信息失敗: {str(e)}")
            return None
    
    def get_collection_info(self, collection: str) -> Optional[Dict]:
        """
        獲取集合信息
        
        Args:
            collection: 集合名稱
            
        Returns:
            集合信息字典，失敗時返回None
        """
        try:
            # 確定集合路徑
            collection_dir = self.data_dir / collection
            
            if not collection_dir.exists():
                self.logger.warning(f"集合不存在: {collection_dir}")
                return None
            
            # 獲取目錄信息
            stat = collection_dir.stat()
            
            # 獲取文件列表
            files = list(collection_dir.glob("*"))
            
            info = {
                "name": collection_dir.name,
                "file_count": len(files),
                "total_size": sum(f.stat().st_size for f in files if f.is_file()),
                "created_time": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "accessed_time": datetime.fromtimestamp(stat.st_atime).isoformat(),
            }
            
            self.logger.debug(f"已獲取集合信息: {collection_dir}")
            return info
        
        except Exception as e:
            self.logger.error(f"獲取集合信息失敗: {str(e)}")
            return None
