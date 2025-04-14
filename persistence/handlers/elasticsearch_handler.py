#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Elasticsearch存儲處理器

提供基於Elasticsearch的數據存儲功能，支持數據的增刪改查操作
"""

import time
import json
import functools
from typing import Dict, Any, List, Optional, Union, Tuple, Callable
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from elasticsearch.exceptions import NotFoundError as ESNotFoundError
from ..core.base import StorageHandler
from ..core.config import ElasticsearchConfig
from ..core.exceptions import (
    StorageError,
    NotFoundError,
    ValidationError,
    ConnectionError
)

class ElasticsearchHandler(StorageHandler):
    """Elasticsearch存儲處理器"""
    
    def __init__(self, config: Union[Dict[str, Any], ElasticsearchConfig]):
        """
        初始化Elasticsearch存儲處理器
        
        Args:
            config: 配置對象或配置字典
        """
        super().__init__(config)
        self.client: Optional[Elasticsearch] = None
        self._cache: Dict[str, Tuple[Any, float]] = {}
    
    def _setup_storage(self) -> None:
        """設置存儲環境"""
        try:
            # 創建客戶端
            self.client = Elasticsearch(
                hosts=self.config.hosts,
                http_auth=(self.config.username, self.config.password) if self.config.username and self.config.password else None,
                use_ssl=self.config.use_ssl,
                verify_certs=self.config.verify_certs,
                ca_certs=self.config.ca_certs,
                client_cert=self.config.client_cert,
                client_key=self.config.client_key,
                max_retries=self.config.max_retries,
                retry_on_timeout=self.config.retry_on_timeout,
                timeout=self.config.timeout,
                maxsize=self.config.max_connections,
                max_retry_time=self.config.max_retry_time
            )
            
            # 創建索引
            self._create_index()
            
            self.logger.info(
                f"Elasticsearch存儲環境已初始化: "
                f"{','.join(self.config.hosts)}/{self.config.index_name}"
            )
        except Exception as e:
            raise ConnectionError(f"連接Elasticsearch失敗: {str(e)}")
    
    def _create_index(self) -> None:
        """創建索引"""
        try:
            # 檢查索引是否存在
            if not self.client.indices.exists(index=self.config.index_name):
                # 創建索引
                self.client.indices.create(
                    index=self.config.index_name,
                    body={
                        "settings": self.config.index_settings,
                        "mappings": self.config.index_mappings
                    }
                )
                
                self.logger.info(f"索引已創建: {self.config.index_name}")
        except Exception as e:
            raise StorageError(f"創建Elasticsearch索引失敗: {str(e)}")
    
    def _cache_result(self, key: str, value: Any) -> None:
        """
        緩存查詢結果
        
        Args:
            key: 緩存鍵
            value: 緩存值
        """
        # 檢查緩存大小
        if len(self._cache) >= self.config.cache_size:
            # 刪除最早的緩存
            oldest_key = min(self._cache.items(), key=lambda x: x[1][1])[0]
            del self._cache[oldest_key]
        
        self._cache[key] = (value, time.time())
    
    def _get_cached_result(self, key: str) -> Optional[Any]:
        """
        獲取緩存的查詢結果
        
        Args:
            key: 緩存鍵
            
        Returns:
            Optional[Any]: 緩存的值，如果不存在或已過期則返回None
        """
        if key in self._cache:
            value, timestamp = self._cache[key]
            if time.time() - timestamp < self.config.cache_ttl:
                return value
            else:
                del self._cache[key]
        return None
    
    def _clear_cache(self) -> None:
        """清理過期的緩存"""
        current_time = time.time()
        expired_keys = [
            key for key, (_, timestamp) in self._cache.items()
            if current_time - timestamp >= self.config.cache_ttl
        ]
        for key in expired_keys:
            del self._cache[key]
    
    def save(self, data: Any, path: str) -> None:
        """
        保存數據到Elasticsearch
        
        Args:
            data: 要保存的數據
            path: 數據路徑（作為ID）
        """
        try:
            # 驗證數據
            self._validate_data(data)
            
            # 序列化數據
            serialized_data = json.dumps(data)
            
            # 獲取當前時間
            now = time.time()
            
            # 構建文檔
            document = {
                self.config.id_field: path,
                self.config.data_field: serialized_data,
                self.config.updated_at_field: now
            }
            
            # 檢查文檔是否存在
            exists = self.exists(path)
            
            if exists:
                # 更新文檔
                self.client.update(
                    index=self.config.index_name,
                    id=path,
                    body={"doc": document}
                )
            else:
                # 添加創建時間
                document[self.config.created_at_field] = now
                
                # 創建文檔
                self.client.index(
                    index=self.config.index_name,
                    id=path,
                    body=document
                )
            
            # 更新緩存
            self._cache_result(path, data)
            
            self.logger.info(f"數據已保存到Elasticsearch: {path}")
        except Exception as e:
            raise StorageError(f"保存數據到Elasticsearch失敗: {str(e)}")
    
    def load(self, path: str) -> Any:
        """
        從Elasticsearch加載數據
        
        Args:
            path: 數據路徑（作為ID）
            
        Returns:
            Any: 加載的數據
        """
        try:
            # 檢查緩存
            cached_data = self._get_cached_result(path)
            if cached_data is not None:
                return cached_data
            
            # 查詢文檔
            result = self.client.get(
                index=self.config.index_name,
                id=path
            )
            
            # 反序列化數據
            data = json.loads(result["_source"][self.config.data_field])
            
            # 緩存結果
            self._cache_result(path, data)
            
            self.logger.info(f"數據已從Elasticsearch加載: {path}")
            return data
        except ESNotFoundError:
            raise NotFoundError(f"數據不存在: {path}")
        except Exception as e:
            raise StorageError(f"從Elasticsearch加載數據失敗: {str(e)}")
    
    def delete(self, path: str) -> None:
        """
        從Elasticsearch刪除數據
        
        Args:
            path: 數據路徑（作為ID）
        """
        try:
            # 刪除文檔
            self.client.delete(
                index=self.config.index_name,
                id=path
            )
            
            # 清理緩存
            if path in self._cache:
                del self._cache[path]
            
            self.logger.info(f"數據已從Elasticsearch刪除: {path}")
        except ESNotFoundError:
            raise NotFoundError(f"數據不存在: {path}")
        except Exception as e:
            raise StorageError(f"從Elasticsearch刪除數據失敗: {str(e)}")
    
    def exists(self, path: str) -> bool:
        """
        檢查Elasticsearch數據是否存在
        
        Args:
            path: 數據路徑（作為ID）
            
        Returns:
            bool: 是否存在
        """
        try:
            # 檢查緩存
            if path in self._cache:
                return True
            
            # 查詢文檔
            return self.client.exists(
                index=self.config.index_name,
                id=path
            )
        except Exception as e:
            raise StorageError(f"檢查Elasticsearch數據是否存在失敗: {str(e)}")
    
    def list(self, path: str = None) -> List[str]:
        """
        列出Elasticsearch數據
        
        Args:
            path: 數據路徑前綴，None表示所有數據
            
        Returns:
            List[str]: 數據路徑列表
        """
        try:
            # 構建查詢
            query = {
                "query": {
                    "match_all": {}
                }
            }
            
            # 添加路徑前綴條件
            if path:
                query = {
                    "query": {
                        "prefix": {
                            self.config.id_field: path
                        }
                    }
                }
            
            # 執行查詢
            result = self.client.search(
                index=self.config.index_name,
                body=query,
                size=10000  # 最大返回數量
            )
            
            # 提取路徑
            paths = [hit["_id"] for hit in result["hits"]["hits"]]
            
            return paths
        except Exception as e:
            raise StorageError(f"列出Elasticsearch數據失敗: {str(e)}")
    
    def find(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        查詢Elasticsearch數據
        
        Args:
            query: 查詢條件
            
        Returns:
            List[Dict[str, Any]]: 數據列表
        """
        try:
            # 構建查詢
            es_query = {
                "query": {
                    "bool": {
                        "must": [
                            {"term": {key: value}}
                            for key, value in query.items()
                        ]
                    }
                }
            }
            
            # 執行查詢
            result = self.client.search(
                index=self.config.index_name,
                body=es_query,
                size=10000  # 最大返回數量
            )
            
            # 轉換結果
            data = []
            for hit in result["hits"]["hits"]:
                record = hit["_source"]
                record[self.config.data_field] = json.loads(
                    record[self.config.data_field]
                )
                data.append(record)
            
            return data
        except Exception as e:
            raise StorageError(f"查詢Elasticsearch數據失敗: {str(e)}")
    
    def count(self, query: Dict[str, Any] = None) -> int:
        """
        統計Elasticsearch數據數量
        
        Args:
            query: 查詢條件，None表示所有數據
            
        Returns:
            int: 數據數量
        """
        try:
            # 構建查詢
            es_query = {
                "query": {
                    "match_all": {}
                }
            }
            
            # 添加查詢條件
            if query:
                es_query = {
                    "query": {
                        "bool": {
                            "must": [
                                {"term": {key: value}}
                                for key, value in query.items()
                            ]
                        }
                    }
                }
            
            # 執行查詢
            result = self.client.count(
                index=self.config.index_name,
                body=es_query
            )
            
            return result["count"]
        except Exception as e:
            raise StorageError(f"統計Elasticsearch數據數量失敗: {str(e)}")
    
    def batch_save(self, data_list: List[Dict[str, Any]]) -> None:
        """
        批量保存數據到Elasticsearch
        
        Args:
            data_list: 數據列表，每個元素為包含data和path的字典
        """
        try:
            # 獲取當前時間
            now = time.time()
            
            # 構建批量操作
            actions = []
            for item in data_list:
                # 驗證數據
                self._validate_data(item["data"])
                
                # 序列化數據
                serialized_data = json.dumps(item["data"])
                
                # 構建文檔
                document = {
                    self.config.id_field: item["path"],
                    self.config.data_field: serialized_data,
                    self.config.updated_at_field: now
                }
                
                # 檢查文檔是否存在
                if self.exists(item["path"]):
                    # 更新文檔
                    actions.append({
                        "_op_type": "update",
                        "_index": self.config.index_name,
                        "_id": item["path"],
                        "doc": document
                    })
                else:
                    # 添加創建時間
                    document[self.config.created_at_field] = now
                    
                    # 創建文檔
                    actions.append({
                        "_op_type": "index",
                        "_index": self.config.index_name,
                        "_id": item["path"],
                        "_source": document
                    })
                
                # 更新緩存
                self._cache_result(item["path"], item["data"])
            
            # 執行批量操作
            bulk(self.client, actions)
            
            self.logger.info(f"批量數據已保存到Elasticsearch: {len(data_list)}條")
        except Exception as e:
            raise StorageError(f"批量保存數據到Elasticsearch失敗: {str(e)}")
    
    def batch_load(self, paths: List[str]) -> List[Dict[str, Any]]:
        """
        批量從Elasticsearch加載數據
        
        Args:
            paths: 數據路徑列表
            
        Returns:
            List[Dict[str, Any]]: 數據列表，每個元素為包含data和path的字典
        """
        try:
            # 檢查緩存
            data_list = []
            missing_paths = []
            
            for path in paths:
                cached_data = self._get_cached_result(path)
                if cached_data is not None:
                    data_list.append({
                        "path": path,
                        "data": cached_data
                    })
                else:
                    missing_paths.append(path)
            
            # 如果有缺失的數據，從Elasticsearch加載
            if missing_paths:
                # 構建查詢
                query = {
                    "query": {
                        "terms": {
                            "_id": missing_paths
                        }
                    }
                }
                
                # 執行查詢
                result = self.client.search(
                    index=self.config.index_name,
                    body=query,
                    size=len(missing_paths)
                )
                
                # 轉換結果
                for hit in result["hits"]["hits"]:
                    data = json.loads(hit["_source"][self.config.data_field])
                    data_list.append({
                        "path": hit["_id"],
                        "data": data
                    })
                    
                    # 緩存結果
                    self._cache_result(hit["_id"], data)
            
            # 檢查是否所有路徑都有數據
            if len(data_list) != len(paths):
                missing_paths = set(paths) - set(item["path"] for item in data_list)
                raise NotFoundError(f"部分數據不存在: {missing_paths}")
            
            return data_list
        except Exception as e:
            raise StorageError(f"批量從Elasticsearch加載數據失敗: {str(e)}")
    
    def batch_delete(self, paths: List[str]) -> None:
        """
        批量從Elasticsearch刪除數據
        
        Args:
            paths: 數據路徑列表
        """
        try:
            # 構建批量操作
            actions = []
            for path in paths:
                actions.append({
                    "_op_type": "delete",
                    "_index": self.config.index_name,
                    "_id": path
                })
            
            # 執行批量操作
            bulk(self.client, actions)
            
            # 清理緩存
            for path in paths:
                if path in self._cache:
                    del self._cache[path]
            
            self.logger.info(f"批量數據已從Elasticsearch刪除: {len(paths)}條")
        except Exception as e:
            raise StorageError(f"批量從Elasticsearch刪除數據失敗: {str(e)}")
    
    def batch_exists(self, paths: List[str]) -> Dict[str, bool]:
        """
        批量檢查Elasticsearch數據是否存在
        
        Args:
            paths: 數據路徑列表
            
        Returns:
            Dict[str, bool]: 路徑到存在狀態的映射
        """
        try:
            # 檢查緩存
            exists_map = {}
            missing_paths = []
            
            for path in paths:
                if path in self._cache:
                    exists_map[path] = True
                else:
                    missing_paths.append(path)
                    exists_map[path] = False
            
            # 如果有缺失的數據，從Elasticsearch查詢
            if missing_paths:
                # 構建查詢
                query = {
                    "query": {
                        "terms": {
                            "_id": missing_paths
                        }
                    }
                }
                
                # 執行查詢
                result = self.client.search(
                    index=self.config.index_name,
                    body=query,
                    size=len(missing_paths)
                )
                
                # 更新結果
                for hit in result["hits"]["hits"]:
                    exists_map[hit["_id"]] = True
            
            return exists_map
        except Exception as e:
            raise StorageError(f"批量檢查Elasticsearch數據是否存在失敗: {str(e)}")
    
    def migrate_data(self, target_handler: 'ElasticsearchHandler', batch_size: int = 1000) -> Tuple[int, int]:
        """
        遷移數據到目標Elasticsearch
        
        Args:
            target_handler: 目標Elasticsearch處理器
            batch_size: 每批處理的數據量
            
        Returns:
            Tuple[int, int]: (成功遷移的數據量, 失敗的數據量)
        """
        try:
            # 初始化計數器
            success_count = 0
            failed_count = 0
            
            # 獲取所有數據路徑
            paths = self.list()
            total_paths = len(paths)
            
            # 分批處理
            for i in range(0, total_paths, batch_size):
                batch_paths = paths[i:i + batch_size]
                
                try:
                    # 批量加載數據
                    data_list = self.batch_load(batch_paths)
                    
                    # 批量保存到目標
                    target_handler.batch_save(data_list)
                    
                    success_count += len(batch_paths)
                    self.logger.info(
                        f"數據遷移進度: {success_count}/{total_paths} "
                        f"({success_count/total_paths*100:.2f}%)"
                    )
                except Exception as e:
                    failed_count += len(batch_paths)
                    self.logger.error(f"批量遷移數據失敗: {str(e)}")
            
            self.logger.info(
                f"數據遷移完成: 成功 {success_count} 條, "
                f"失敗 {failed_count} 條"
            )
            return success_count, failed_count
        except Exception as e:
            raise StorageError(f"數據遷移失敗: {str(e)}")
    
    def migrate_schema(self, target_handler: 'ElasticsearchHandler') -> None:
        """
        遷移索引結構到目標Elasticsearch
        
        Args:
            target_handler: 目標Elasticsearch處理器
        """
        try:
            # 獲取源索引設置
            source_settings = self.client.indices.get_settings(
                index=self.config.index_name
            )
            
            # 獲取源索引映射
            source_mappings = self.client.indices.get_mapping(
                index=self.config.index_name
            )
            
            # 創建目標索引
            target_handler.client.indices.create(
                index=target_handler.config.index_name,
                body={
                    "settings": source_settings[self.config.index_name]["settings"],
                    "mappings": source_mappings[self.config.index_name]["mappings"]
                }
            )
            
            self.logger.info(
                f"索引結構已遷移到目標Elasticsearch: "
                f"{','.join(target_handler.config.hosts)}/"
                f"{target_handler.config.index_name}"
            )
        except Exception as e:
            raise StorageError(f"索引結構遷移失敗: {str(e)}")
    
    def __del__(self):
        """清理資源"""
        if self.client:
            self.client.close() 