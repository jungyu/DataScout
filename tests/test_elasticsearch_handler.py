#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Elasticsearch存儲處理器單元測試
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import time
from typing import Dict, Any, List
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError as ESNotFoundError
from persistence.handlers.elasticsearch_handler import ElasticsearchHandler
from persistence.core.config import ElasticsearchConfig
from persistence.core.exceptions import (
    StorageError,
    NotFoundError,
    ValidationError,
    ConnectionError
)

class TestElasticsearchHandler(unittest.TestCase):
    """Elasticsearch存儲處理器測試類"""
    
    def setUp(self):
        """測試前準備"""
        # 創建配置
        self.config = ElasticsearchConfig(
            hosts=["localhost:9200"],
            index_name="test_index",
            id_field="id",
            data_field="data",
            created_at_field="created_at",
            updated_at_field="updated_at"
        )
        
        # 創建處理器
        self.handler = ElasticsearchHandler(self.config)
        
        # 模擬客戶端
        self.mock_client = Mock(spec=Elasticsearch)
        self.handler.client = self.mock_client
    
    def test_init(self):
        """測試初始化"""
        # 測試使用配置對象初始化
        handler = ElasticsearchHandler(self.config)
        self.assertEqual(handler.config, self.config)
        
        # 測試使用配置字典初始化
        config_dict = {
            "hosts": ["localhost:9200"],
            "index_name": "test_index",
            "id_field": "id",
            "data_field": "data",
            "created_at_field": "created_at",
            "updated_at_field": "updated_at"
        }
        handler = ElasticsearchHandler(config_dict)
        self.assertEqual(handler.config.hosts, config_dict["hosts"])
        self.assertEqual(handler.config.index_name, config_dict["index_name"])
    
    def test_setup_storage(self):
        """測試設置存儲環境"""
        # 模擬客戶端創建
        with patch("elasticsearch.Elasticsearch") as mock_es:
            mock_es.return_value = self.mock_client
            
            # 模擬索引不存在
            self.mock_client.indices.exists.return_value = False
            
            # 調用設置存儲環境
            self.handler._setup_storage()
            
            # 驗證客戶端創建
            mock_es.assert_called_once()
            
            # 驗證索引創建
            self.mock_client.indices.create.assert_called_once()
    
    def test_create_index(self):
        """測試創建索引"""
        # 模擬索引不存在
        self.mock_client.indices.exists.return_value = False
        
        # 調用創建索引
        self.handler._create_index()
        
        # 驗證索引創建
        self.mock_client.indices.create.assert_called_once_with(
            index=self.config.index_name,
            body={
                "settings": self.config.index_settings,
                "mappings": self.config.index_mappings
            }
        )
        
        # 模擬索引已存在
        self.mock_client.indices.exists.return_value = True
        
        # 調用創建索引
        self.handler._create_index()
        
        # 驗證索引未創建
        self.mock_client.indices.create.assert_called_once()
    
    def test_cache_result(self):
        """測試緩存結果"""
        # 設置緩存大小
        self.handler.config.cache_size = 2
        
        # 緩存結果
        self.handler._cache_result("key1", "value1")
        self.handler._cache_result("key2", "value2")
        self.handler._cache_result("key3", "value3")
        
        # 驗證緩存
        self.assertIn("key2", self.handler._cache)
        self.assertIn("key3", self.handler._cache)
        self.assertNotIn("key1", self.handler._cache)
    
    def test_get_cached_result(self):
        """測試獲取緩存結果"""
        # 設置緩存
        self.handler._cache["key"] = ("value", time.time())
        
        # 獲取緩存結果
        result = self.handler._get_cached_result("key")
        
        # 驗證結果
        self.assertEqual(result, "value")
        
        # 設置過期緩存
        self.handler._cache["expired_key"] = ("value", time.time() - self.handler.config.cache_ttl - 1)
        
        # 獲取過期緩存結果
        result = self.handler._get_cached_result("expired_key")
        
        # 驗證結果
        self.assertIsNone(result)
        self.assertNotIn("expired_key", self.handler._cache)
    
    def test_clear_cache(self):
        """測試清理緩存"""
        # 設置緩存
        current_time = time.time()
        self.handler._cache["valid_key"] = ("value", current_time)
        self.handler._cache["expired_key"] = ("value", current_time - self.handler.config.cache_ttl - 1)
        
        # 清理緩存
        self.handler._clear_cache()
        
        # 驗證緩存
        self.assertIn("valid_key", self.handler._cache)
        self.assertNotIn("expired_key", self.handler._cache)
    
    def test_save(self):
        """測試保存數據"""
        # 準備數據
        data = {"key": "value"}
        path = "test_path"
        
        # 模擬數據不存在
        self.mock_client.exists.return_value = False
        
        # 調用保存
        self.handler.save(data, path)
        
        # 驗證保存
        self.mock_client.index.assert_called_once()
        
        # 模擬數據已存在
        self.mock_client.exists.return_value = True
        
        # 調用保存
        self.handler.save(data, path)
        
        # 驗證更新
        self.mock_client.update.assert_called_once()
    
    def test_load(self):
        """測試加載數據"""
        # 準備數據
        path = "test_path"
        data = {"key": "value"}
        
        # 模擬緩存未命中
        self.handler._get_cached_result = Mock(return_value=None)
        
        # 模擬查詢結果
        self.mock_client.get.return_value = {
            "_source": {
                self.config.data_field: json.dumps(data)
            }
        }
        
        # 調用加載
        result = self.handler.load(path)
        
        # 驗證結果
        self.assertEqual(result, data)
        
        # 模擬緩存命中
        self.handler._get_cached_result = Mock(return_value=data)
        
        # 調用加載
        result = self.handler.load(path)
        
        # 驗證結果
        self.assertEqual(result, data)
        self.mock_client.get.assert_called_once()
    
    def test_delete(self):
        """測試刪除數據"""
        # 準備數據
        path = "test_path"
        
        # 設置緩存
        self.handler._cache[path] = ("value", time.time())
        
        # 調用刪除
        self.handler.delete(path)
        
        # 驗證刪除
        self.mock_client.delete.assert_called_once_with(
            index=self.config.index_name,
            id=path
        )
        
        # 驗證緩存清理
        self.assertNotIn(path, self.handler._cache)
    
    def test_exists(self):
        """測試檢查數據是否存在"""
        # 準備數據
        path = "test_path"
        
        # 模擬緩存未命中
        self.handler._cache = {}
        
        # 模擬查詢結果
        self.mock_client.exists.return_value = True
        
        # 調用檢查
        result = self.handler.exists(path)
        
        # 驗證結果
        self.assertTrue(result)
        
        # 模擬緩存命中
        self.handler._cache[path] = ("value", time.time())
        
        # 調用檢查
        result = self.handler.exists(path)
        
        # 驗證結果
        self.assertTrue(result)
        self.mock_client.exists.assert_called_once()
    
    def test_list(self):
        """測試列出數據"""
        # 準備數據
        paths = ["path1", "path2"]
        
        # 模擬查詢結果
        self.mock_client.search.return_value = {
            "hits": {
                "hits": [
                    {"_id": path}
                    for path in paths
                ]
            }
        }
        
        # 調用列出
        result = self.handler.list()
        
        # 驗證結果
        self.assertEqual(result, paths)
        
        # 測試帶前綴的列出
        prefix = "test"
        result = self.handler.list(prefix)
        
        # 驗證查詢
        self.mock_client.search.assert_called_with(
            index=self.config.index_name,
            body={
                "query": {
                    "prefix": {
                        self.config.id_field: prefix
                    }
                }
            },
            size=10000
        )
    
    def test_find(self):
        """測試查詢數據"""
        # 準備數據
        query = {"field": "value"}
        data = [{"id": "1", "data": json.dumps({"key": "value"})}]
        
        # 模擬查詢結果
        self.mock_client.search.return_value = {
            "hits": {
                "hits": [
                    {"_source": item}
                    for item in data
                ]
            }
        }
        
        # 調用查詢
        result = self.handler.find(query)
        
        # 驗證結果
        self.assertEqual(len(result), 1)
        self.assertEqual(
            result[0][self.config.data_field],
            json.loads(data[0][self.config.data_field])
        )
    
    def test_count(self):
        """測試統計數據數量"""
        # 準備數據
        query = {"field": "value"}
        count = 10
        
        # 模擬查詢結果
        self.mock_client.count.return_value = {"count": count}
        
        # 調用統計
        result = self.handler.count(query)
        
        # 驗證結果
        self.assertEqual(result, count)
        
        # 測試無條件統計
        result = self.handler.count()
        
        # 驗證查詢
        self.mock_client.count.assert_called_with(
            index=self.config.index_name,
            body={
                "query": {
                    "match_all": {}
                }
            }
        )
    
    def test_batch_save(self):
        """測試批量保存數據"""
        # 準備數據
        data_list = [
            {"path": "path1", "data": {"key1": "value1"}},
            {"path": "path2", "data": {"key2": "value2"}}
        ]
        
        # 模擬存在檢查
        self.mock_client.exists.return_value = False
        
        # 調用批量保存
        with patch("elasticsearch.helpers.bulk") as mock_bulk:
            self.handler.batch_save(data_list)
            
            # 驗證批量操作
            mock_bulk.assert_called_once()
    
    def test_batch_load(self):
        """測試批量加載數據"""
        # 準備數據
        paths = ["path1", "path2"]
        data = [
            {"_id": "path1", "_source": {self.config.data_field: json.dumps({"key1": "value1"})}},
            {"_id": "path2", "_source": {this.config.data_field: json.dumps({"key2": "value2"})}}
        ]
        
        # 模擬緩存未命中
        self.handler._get_cached_result = Mock(return_value=None)
        
        # 模擬查詢結果
        self.mock_client.search.return_value = {
            "hits": {
                "hits": data
            }
        }
        
        # 調用批量加載
        result = self.handler.batch_load(paths)
        
        # 驗證結果
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["path"], "path1")
        self.assertEqual(result[1]["path"], "path2")
    
    def test_batch_delete(self):
        """測試批量刪除數據"""
        # 準備數據
        paths = ["path1", "path2"]
        
        # 設置緩存
        for path in paths:
            self.handler._cache[path] = ("value", time.time())
        
        # 調用批量刪除
        with patch("elasticsearch.helpers.bulk") as mock_bulk:
            self.handler.batch_delete(paths)
            
            # 驗證批量操作
            mock_bulk.assert_called_once()
            
            # 驗證緩存清理
            for path in paths:
                self.assertNotIn(path, self.handler._cache)
    
    def test_batch_exists(self):
        """測試批量檢查數據是否存在"""
        # 準備數據
        paths = ["path1", "path2"]
        
        # 設置緩存
        self.handler._cache["path1"] = ("value", time.time())
        
        # 模擬查詢結果
        self.mock_client.search.return_value = {
            "hits": {
                "hits": [{"_id": "path2"}]
            }
        }
        
        # 調用批量檢查
        result = self.handler.batch_exists(paths)
        
        # 驗證結果
        self.assertTrue(result["path1"])
        self.assertTrue(result["path2"])
    
    def test_migrate_data(self):
        """測試數據遷移"""
        # 準備數據
        paths = ["path1", "path2"]
        data_list = [
            {"path": "path1", "data": {"key1": "value1"}},
            {"path": "path2", "data": {"key2": "value2"}}
        ]
        
        # 模擬目標處理器
        target_handler = Mock(spec=ElasticsearchHandler)
        
        # 模擬列出數據
        self.handler.list = Mock(return_value=paths)
        
        # 模擬批量加載
        self.handler.batch_load = Mock(return_value=data_list)
        
        # 調用數據遷移
        success_count, failed_count = self.handler.migrate_data(target_handler)
        
        # 驗證結果
        self.assertEqual(success_count, 2)
        self.assertEqual(failed_count, 0)
        
        # 驗證目標處理器調用
        target_handler.batch_save.assert_called_once_with(data_list)
    
    def test_migrate_schema(self):
        """測試索引結構遷移"""
        # 準備數據
        settings = {"setting": "value"}
        mappings = {"mapping": "value"}
        
        # 模擬目標處理器
        target_handler = Mock(spec=ElasticsearchHandler)
        
        # 模擬獲取設置
        self.mock_client.indices.get_settings.return_value = {
            self.config.index_name: {"settings": settings}
        }
        
        # 模擬獲取映射
        self.mock_client.indices.get_mapping.return_value = {
            this.config.index_name: {"mappings": mappings}
        }
        
        # 調用索引結構遷移
        self.handler.migrate_schema(target_handler)
        
        # 驗證目標處理器調用
        target_handler.client.indices.create.assert_called_once_with(
            index=target_handler.config.index_name,
            body={
                "settings": settings,
                "mappings": mappings
            }
        )

if __name__ == "__main__":
    unittest.main() 