#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import time
from typing import Dict, List, Optional, Any, Union

from ..utils.logger import setup_logger
from ..utils.error_handler import retry_on_exception, handle_exception


class MongoDBHandler:
    """
    MongoDB處理器，提供MongoDB數據庫的連接和操作功能。
    """
    
    def __init__(
        self,
        config: Dict = None,
        log_level: int = logging.INFO
    ):
        """
        初始化MongoDB處理器
        
        Args:
            config: 配置字典
            log_level: 日誌級別
        """
        self.logger = setup_logger(__name__, log_level)
        self.config = config or {}
        
        # MongoDB設置
        self.host = self.config.get("host", "localhost")
        self.port = self.config.get("port", 27017)
        self.username = self.config.get("username")
        self.password = self.config.get("password")
        self.auth_source = self.config.get("auth_source", "admin")
        self.db_name = self.config.get("db_name", "crawler")
        
        # 連接設置
        self.connect_timeout = self.config.get("connect_timeout", 30000)  # 30秒
        self.socket_timeout = self.config.get("socket_timeout", 60000)    # 60秒
        self.max_pool_size = self.config.get("max_pool_size", 100)
        self.retry_writes = self.config.get("retry_writes", True)
        
        # 初始化客戶端和數據庫
        self.client = None
        self.db = None
        
        # 初始化連接
        self._init_connection()
        
        self.logger.info("MongoDB處理器初始化完成")
    
    def _init_connection(self):
        """初始化MongoDB連接"""
        try:
            import pymongo
            
            # 構建連接字符串
            connection_string = "mongodb://"
            
            if self.username and self.password:
                connection_string += f"{self.username}:{self.password}@"
            
            connection_string += f"{self.host}:{self.port}/{self.db_name}"
            
            if self.username and self.password:
                connection_string += f"?authSource={self.auth_source}"
            
            # 連接選項
            connect_options = {
                "connectTimeoutMS": self.connect_timeout,
                "socketTimeoutMS": self.socket_timeout,
                "maxPoolSize": self.max_pool_size,
                "retryWrites": self.retry_writes
            }
            
            # 創建客戶端
            self.client = pymongo.MongoClient(connection_string, **connect_options)
            self.db = self.client[self.db_name]
            
            # 測試連接
            self.client.admin.command('ping')
            
            self.logger.info(f"已連接MongoDB: {self.host}:{self.port}/{self.db_name}")
        
        except ImportError:
            self.logger.error("未安裝pymongo庫，請先安裝: pip install pymongo")
            raise
        
        except Exception as e:
            self.logger.error(f"連接MongoDB失敗: {str(e)}")
            raise
    
    def get_collection(self, collection_name: str):
        """
        獲取集合對象
        
        Args:
            collection_name: 集合名稱
            
        Returns:
            集合對象
        """
        if not self.db:
            self.logger.error("MongoDB未連接")
            return None
        
        return self.db[collection_name]
    
    @retry_on_exception(retries=3, delay=1)
    def insert_one(self, collection_name: str, document: Dict) -> str:
        """
        插入單個文檔
        
        Args:
            collection_name: 集合名稱
            document: 文檔數據
            
        Returns:
            插入的文檔ID
        """
        try:
            collection = self.get_collection(collection_name)
            
            # 添加時間戳
            if "created_at" not in document:
                document["created_at"] = int(time.time())
            
            if "updated_at" not in document:
                document["updated_at"] = int(time.time())
            
            result = collection.insert_one(document)
            
            if result.acknowledged:
                inserted_id = str(result.inserted_id)
                self.logger.debug(f"已插入文檔到 {collection_name}, ID: {inserted_id}")
                return inserted_id
            else:
                self.logger.warning(f"插入文檔到 {collection_name} 失敗")
                return ""
        
        except Exception as e:
            self.logger.error(f"插入文檔到 {collection_name} 失敗: {str(e)}")
            raise
    
    @retry_on_exception(retries=3, delay=1)
    def insert_many(self, collection_name: str, documents: List[Dict]) -> List[str]:
        """
        批量插入多個文檔
        
        Args:
            collection_name: 集合名稱
            documents: 文檔數據列表
            
        Returns:
            插入的文檔ID列表
        """
        if not documents:
            return []
        
        try:
            collection = self.get_collection(collection_name)
            
            # 添加時間戳
            timestamp = int(time.time())
            for doc in documents:
                if "created_at" not in doc:
                    doc["created_at"] = timestamp
                
                if "updated_at" not in doc:
                    doc["updated_at"] = timestamp
            
            result = collection.insert_many(documents)
            
            if result.acknowledged:
                inserted_ids = [str(id) for id in result.inserted_ids]
                self.logger.debug(f"已批量插入 {len(inserted_ids)} 個文檔到 {collection_name}")
                return inserted_ids
            else:
                self.logger.warning(f"批量插入文檔到 {collection_name} 失敗")
                return []
        
        except Exception as e:
            self.logger.error(f"批量插入文檔到 {collection_name} 失敗: {str(e)}")
            raise
    
    @retry_on_exception(retries=3, delay=1)
    def update_one(self, collection_name: str, filter_query: Dict, update_data: Dict, upsert: bool = False) -> bool:
        """
        更新單個文檔
        
        Args:
            collection_name: 集合名稱
            filter_query: 過濾條件
            update_data: 更新數據
            upsert: 如果不存在是否插入
            
        Returns:
            是否成功更新
        """
        try:
            collection = self.get_collection(collection_name)
            
            # 添加更新時間戳
            if "$set" in update_data:
                update_data["$set"]["updated_at"] = int(time.time())
            else:
                update_data["$set"] = {"updated_at": int(time.time())}
            
            result = collection.update_one(filter_query, update_data, upsert=upsert)
            
            if result.acknowledged:
                self.logger.debug(
                    f"已更新文檔，集合: {collection_name}, "
                    f"匹配: {result.matched_count}, 修改: {result.modified_count}"
                )
                return True
            else:
                self.logger.warning(f"更新文檔失敗，集合: {collection_name}")
                return False
        
        except Exception as e:
            self.logger.error(f"更新文檔失敗，集合: {collection_name}, 錯誤: {str(e)}")
            raise
    
    @retry_on_exception(retries=3, delay=1)
    def update_many(self, collection_name: str, filter_query: Dict, update_data: Dict, upsert: bool = False) -> int:
        """
        批量更新多個文檔
        
        Args:
            collection_name: 集合名稱
            filter_query: 過濾條件
            update_data: 更新數據
            upsert: 如果不存在是否插入
            
        Returns:
            更新的文檔數量
        """
        try:
            collection = self.get_collection(collection_name)
            
            # 添加更新時間戳
            if "$set" in update_data:
                update_data["$set"]["updated_at"] = int(time.time())
            else:
                update_data["$set"] = {"updated_at": int(time.time())}
            
            result = collection.update_many(filter_query, update_data, upsert=upsert)
            
            if result.acknowledged:
                self.logger.debug(
                    f"已批量更新文檔，集合: {collection_name}, "
                    f"匹配: {result.matched_count}, 修改: {result.modified_count}"
                )
                return result.modified_count
            else:
                self.logger.warning(f"批量更新文檔失敗，集合: {collection_name}")
                return 0
        
        except Exception as e:
            self.logger.error(f"批量更新文檔失敗，集合: {collection_name}, 錯誤: {str(e)}")
            raise
    
    @retry_on_exception(retries=3, delay=1)
    def find_one(self, collection_name: str, filter_query: Dict = None, projection: Dict = None) -> Optional[Dict]:
        """
        查找單個文檔
        
        Args:
            collection_name: 集合名稱
            filter_query: 過濾條件
            projection: 投影，指定返回的字段
            
        Returns:
            文檔數據或None
        """
        try:
            collection = self.get_collection(collection_name)
            
            # 查詢
            document = collection.find_one(filter_query or {}, projection)
            
            if document:
                # 將ObjectId轉換為字符串
                if "_id" in document and hasattr(document["_id"], "__str__"):
                    document["_id"] = str(document["_id"])
                
                return document
            else:
                return None
        
        except Exception as e:
            self.logger.error(f"查找文檔失敗，集合: {collection_name}, 錯誤: {str(e)}")
            raise
    
    @retry_on_exception(retries=3, delay=1)
    def find_many(
        self, 
        collection_name: str, 
        filter_query: Dict = None, 
        projection: Dict = None,
        sort: List = None,
        limit: int = 0,
        skip: int = 0
    ) -> List[Dict]:
        """
        查找多個文檔
        
        Args:
            collection_name: 集合名稱
            filter_query: 過濾條件
            projection: 投影，指定返回的字段
            sort: 排序條件，格式為 [("field", 1/-1), ...]
            limit: 限制返回數量，0表示不限制
            skip: 跳過的文檔數量
            
        Returns:
            文檔數據列表
        """
        try:
            collection = self.get_collection(collection_name)
            
            # 查詢
            cursor = collection.find(filter_query or {}, projection)
            
            # 應用排序
            if sort:
                cursor = cursor.sort(sort)
            
            # 應用分頁
            if skip:
                cursor = cursor.skip(skip)
            
            if limit:
                cursor = cursor.limit(limit)
            
            # 轉換為列表
            documents = list(cursor)
            
            # 將ObjectId轉換為字符串
            for document in documents:
                if "_id" in document and hasattr(document["_id"], "__str__"):
                    document["_id"] = str(document["_id"])
            
            return documents
        
        except Exception as e:
            self.logger.error(f"查找多個文檔失敗，集合: {collection_name}, 錯誤: {str(e)}")
            raise
    
    @retry_on_exception(retries=3, delay=1)
    def delete_one(self, collection_name: str, filter_query: Dict) -> bool:
        """
        刪除單個文檔
        
        Args:
            collection_name: 集合名稱
            filter_query: 過濾條件
            
        Returns:
            是否成功刪除
        """
        try:
            collection = self.get_collection(collection_name)
            
            result = collection.delete_one(filter_query)
            
            if result.acknowledged:
                self.logger.debug(f"已刪除文檔，集合: {collection_name}, 數量: {result.deleted_count}")
                return result.deleted_count > 0
            else:
                self.logger.warning(f"刪除文檔失敗，集合: {collection_name}")
                return False
        
        except Exception as e:
            self.logger.error(f"刪除文檔失敗，集合: {collection_name}, 錯誤: {str(e)}")
            raise
    
    @retry_on_exception(retries=3, delay=1)
    def delete_many(self, collection_name: str, filter_query: Dict) -> int:
        """
        批量刪除多個文檔
        
        Args:
            collection_name: 集合名稱
            filter_query: 過濾條件
            
        Returns:
            刪除的文檔數量
        """
        try:
            collection = self.get_collection(collection_name)
            
            result = collection.delete_many(filter_query)
            
            if result.acknowledged:
                self.logger.debug(f"已批量刪除文檔，集合: {collection_name}, 數量: {result.deleted_count}")
                return result.deleted_count
            else:
                self.logger.warning(f"批量刪除文檔失敗，集合: {collection_name}")
                return 0
        
        except Exception as e:
            self.logger.error(f"批量刪除文檔失敗，集合: {collection_name}, 錯誤: {str(e)}")
            raise
    
    @retry_on_exception(retries=3, delay=1)
    def count_documents(self, collection_name: str, filter_query: Dict = None) -> int:
        """
        計算文檔數量
        
        Args:
            collection_name: 集合名稱
            filter_query: 過濾條件
            
        Returns:
            文檔數量
        """
        try:
            collection = self.get_collection(collection_name)
            
            count = collection.count_documents(filter_query or {})
            return count
        
        except Exception as e:
            self.logger.error(f"計算文檔數量失敗，集合: {collection_name}, 錯誤: {str(e)}")
            raise
    
    @retry_on_exception(retries=3, delay=1)
    def aggregate(self, collection_name: str, pipeline: List[Dict]) -> List[Dict]:
        """
        執行聚合管道操作
        
        Args:
            collection_name: 集合名稱
            pipeline: 聚合管道
            
        Returns:
            聚合結果
        """
        try:
            collection = self.get_collection(collection_name)
            
            results = list(collection.aggregate(pipeline))
            
            # 處理ObjectId
            for result in results:
                if "_id" in result and hasattr(result["_id"], "__str__"):
                    result["_id"] = str(result["_id"])
            
            return results
        
        except Exception as e:
            self.logger.error(f"執行聚合管道失敗，集合: {collection_name}, 錯誤: {str(e)}")
            raise
    
    @retry_on_exception(retries=3, delay=1)
    def create_index(self, collection_name: str, keys: Dict, **kwargs) -> str:
        """
        創建索引
        
        Args:
            collection_name: 集合名稱
            keys: 索引鍵，格式為 {"field": 1/-1, ...}
            **kwargs: 其他索引選項
            
        Returns:
            創建的索引名稱
        """
        try:
            collection = self.get_collection(collection_name)
            
            index_name = collection.create_index(keys, **kwargs)
            self.logger.info(f"已創建索引，集合: {collection_name}, 索引: {index_name}")
            
            return index_name
        
        except Exception as e:
            self.logger.error(f"創建索引失敗，集合: {collection_name}, 錯誤: {str(e)}")
            raise
    
    def list_indexes(self, collection_name: str) -> List[Dict]:
        """
        列出集合的所有索引
        
        Args:
            collection_name: 集合名稱
            
        Returns:
            索引信息列表
        """
        try:
            collection = self.get_collection(collection_name)
            
            indexes = list(collection.list_indexes())
            return indexes
        
        except Exception as e:
            self.logger.error(f"列出索引失敗，集合: {collection_name}, 錯誤: {str(e)}")
            return []
    
    def drop_index(self, collection_name: str, index_name: str) -> bool:
        """
        刪除索引
        
        Args:
            collection_name: 集合名稱
            index_name: 索引名稱
            
        Returns:
            是否成功刪除
        """
        try:
            collection = self.get_collection(collection_name)
            
            collection.drop_index(index_name)
            self.logger.info(f"已刪除索引，集合: {collection_name}, 索引: {index_name}")
            
            return True
        
        except Exception as e:
            self.logger.error(f"刪除索引失敗，集合: {collection_name}, 索引: {index_name}, 錯誤: {str(e)}")
            return False
    
    def drop_collection(self, collection_name: str) -> bool:
        """
        刪除集合
        
        Args:
            collection_name: 集合名稱
            
        Returns:
            是否成功刪除
        """
        try:
            collection = self.get_collection(collection_name)
            
            collection.drop()
            self.logger.info(f"已刪除集合: {collection_name}")
            
            return True
        
        except Exception as e:
            self.logger.error(f"刪除集合失敗，集合: {collection_name}, 錯誤: {str(e)}")
            return False
    
    def list_collections(self) -> List[str]:
        """
        列出數據庫中的所有集合
        
        Returns:
            集合名稱列表
        """
        try:
            collection_names = self.db.list_collection_names()
            return collection_names
        
        except Exception as e:
            self.logger.error(f"列出集合失敗，錯誤: {str(e)}")
            return []
    
    def get_collection_stats(self, collection_name: str) -> Dict:
        """
        獲取集合統計信息
        
        Args:
            collection_name: 集合名稱
            
        Returns:
            統計信息
        """
        try:
            stats = self.db.command("collStats", collection_name)
            return stats
        
        except Exception as e:
            self.logger.error(f"獲取集合統計信息失敗，集合: {collection_name}, 錯誤: {str(e)}")
            return {}
    
    def find_and_modify(
        self,
        collection_name: str,
        filter_query: Dict,
        update: Dict,
        upsert: bool = False,
        sort: List = None,
        return_updated: bool = False
    ) -> Optional[Dict]:
        """
        查找並修改文檔
        
        Args:
            collection_name: 集合名稱
            filter_query: 過濾條件
            update: 更新操作
            upsert: 如果不存在是否插入
            sort: 排序條件
            return_updated: 是否返回更新後的文檔
            
        Returns:
            修改前或修改後的文檔
        """
        try:
            collection = self.get_collection(collection_name)
            
            # 添加更新時間戳
            if "$set" in update:
                update["$set"]["updated_at"] = int(time.time())
            else:
                update["$set"] = {"updated_at": int(time.time())}
            
            result = collection.find_one_and_update(
                filter_query,
                update,
                upsert=upsert,
                sort=sort,
                return_document=True if return_updated else False
            )
            
            if result:
                # 將ObjectId轉換為字符串
                if "_id" in result and hasattr(result["_id"], "__str__"):
                    result["_id"] = str(result["_id"])
                
                return result
            else:
                return None
        
        except Exception as e:
            self.logger.error(f"查找並修改文檔失敗，集合: {collection_name}, 錯誤: {str(e)}")
            raise
    
    def bulk_write(self, collection_name: str, operations: List, ordered: bool = True) -> Dict:
        """
        批量寫入操作
        
        Args:
            collection_name: 集合名稱
            operations: 操作列表
            ordered: 是否按順序執行
            
        Returns:
            結果信息
        """
        try:
            import pymongo
            
            collection = self.get_collection(collection_name)
            
            result = collection.bulk_write(operations, ordered=ordered)
            
            return {
                "inserted_count": result.inserted_count,
                "matched_count": result.matched_count,
                "modified_count": result.modified_count,
                "deleted_count": result.deleted_count,
                "upserted_count": result.upserted_count,
                "upserted_ids": [str(id) for id in result.upserted_ids.values()]
            }
        
        except Exception as e:
            self.logger.error(f"批量寫入操作失敗，集合: {collection_name}, 錯誤: {str(e)}")
            raise
    
    def create_bulk_operations(self, operation_type: str, documents: List[Dict], filter_field: str = None) -> List:
        """
        創建批量操作
        
        Args:
            operation_type: 操作類型，支持 insert, update, delete
            documents: 文檔列表
            filter_field: 過濾字段，用於更新或刪除操作
            
        Returns:
            批量操作列表
        """
        try:
            import pymongo
            
            operations = []
            
            if operation_type == "insert":
                for doc in documents:
                    # 添加時間戳
                    if "created_at" not in doc:
                        doc["created_at"] = int(time.time())
                    
                    if "updated_at" not in doc:
                        doc["updated_at"] = int(time.time())
                    
                    operations.append(pymongo.InsertOne(doc))
            
            elif operation_type == "update":
                if not filter_field:
                    raise ValueError("更新操作需要指定過濾字段")
                
                for doc in documents:
                    if filter_field not in doc:
                        continue
                    
                    filter_query = {filter_field: doc[filter_field]}
                    
                    # 添加更新時間戳
                    doc["updated_at"] = int(time.time())
                    
                    operations.append(pymongo.UpdateOne(
                        filter_query,
                        {"$set": doc},
                        upsert=True
                    ))
            
            elif operation_type == "delete":
                if not filter_field:
                    raise ValueError("刪除操作需要指定過濾字段")
                
                for doc in documents:
                    if filter_field not in doc:
                        continue
                    
                    filter_query = {filter_field: doc[filter_field]}
                    operations.append(pymongo.DeleteOne(filter_query))
            
            else:
                raise ValueError(f"不支持的操作類型: {operation_type}")
            
            return operations
        
        except ImportError:
            self.logger.error("未安裝pymongo庫，請先安裝: pip install pymongo")
            return []
        
        except Exception as e:
            self.logger.error(f"創建批量操作失敗: {str(e)}")
            return []
    
    def close(self):
        """關閉MongoDB連接"""
        if self.client:
            try:
                self.client.close()
                self.logger.info("已關閉MongoDB連接")
            except Exception as e:
                self.logger.error(f"關閉MongoDB連接失敗: {str(e)}")
    
    def __del__(self):
        """析構函數，確保連接正確關閉"""
        self.close()#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import time
from typing import Dict, List, Optional, Any, Union

from ..utils.logger import setup_logger
from ..utils.error_handler import retry_on_exception, handle_exception


class MongoDBHandler:
    """
    MongoDB處理器，提供MongoDB數據庫的連接和操作功能。
    """
    
    def __init__(
        self,
        config: Dict = None,
        log_level: int = logging.INFO
    ):
        """
        初始化MongoDB處理器
        
        Args:
            config: 配置字典
            log_level: 日誌級別
        """
        self.logger = setup_logger(__name__, log_level)
        self.config = config or {}
        
        # MongoDB設置
        self.host = self.config.get("host", "localhost")
        self.port = self.config.get("port", 27017)
        self.username = self.config.get("username")
        self.password = self.config.get("password")
        self.auth_source = self.config.get("auth_source", "admin")
        self.db_name = self.config.get("db_name", "crawler")
        
        # 連接設置
        self.connect_