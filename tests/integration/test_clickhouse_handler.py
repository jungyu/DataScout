#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ClickHouse 存儲處理器集成測試
"""

import unittest
import time
import json
from typing import Dict, Any, List
from clickhouse_driver import Client
from persistence.handlers.clickhouse_handler import ClickHouseHandler
from persistence.core.config import ClickHouseConfig
from persistence.core.exceptions import (
    StorageError,
    NotFoundError,
    ValidationError,
    ConnectionError
)

class TestClickHouseHandlerIntegration(unittest.TestCase):
    """ClickHouse 存儲處理器集成測試類"""
    
    @classmethod
    def setUpClass(cls):
        """測試類初始化"""
        # 創建配置
        cls.config = ClickHouseConfig(
            host="localhost",
            port=9000,
            database="test_db_integration",
            table_name="test_table_integration"
        )
        
        # 創建處理器
        cls.handler = ClickHouseHandler(cls.config)
        
        # 清理測試表
        try:
            cls.handler.client.execute(
                f"DROP TABLE IF EXISTS {cls.config.database}.{cls.config.table_name}"
            )
        except:
            pass
    
    def setUp(self):
        """每個測試前準備"""
        # 清理測試數據
        try:
            self.handler.client.execute(
                f"TRUNCATE TABLE IF EXISTS {self.config.database}.{self.config.table_name}"
            )
        except:
            pass
    
    def test_save_and_load(self):
        """測試保存和加載數據"""
        # 準備數據
        data = {"key": "value"}
        path = "test_path"
        
        # 保存數據
        self.handler.save(data, path)
        
        # 加載數據
        result = self.handler.load(path)
        
        # 驗證結果
        self.assertEqual(result, data)
    
    def test_update(self):
        """測試更新數據"""
        # 準備數據
        data1 = {"key": "value1"}
        data2 = {"key": "value2"}
        path = "test_path"
        
        # 保存初始數據
        self.handler.save(data1, path)
        
        # 更新數據
        self.handler.save(data2, path)
        
        # 加載數據
        result = self.handler.load(path)
        
        # 驗證結果
        self.assertEqual(result, data2)
    
    def test_delete(self):
        """測試刪除數據"""
        # 準備數據
        data = {"key": "value"}
        path = "test_path"
        
        # 保存數據
        self.handler.save(data, path)
        
        # 刪除數據
        self.handler.delete(path)
        
        # 驗證數據不存在
        with self.assertRaises(NotFoundError):
            self.handler.load(path)
    
    def test_exists(self):
        """測試檢查數據是否存在"""
        # 準備數據
        data = {"key": "value"}
        path = "test_path"
        
        # 驗證數據不存在
        self.assertFalse(self.handler.exists(path))
        
        # 保存數據
        self.handler.save(data, path)
        
        # 驗證數據存在
        self.assertTrue(self.handler.exists(path))
    
    def test_list(self):
        """測試列出數據"""
        # 準備數據
        data1 = {"key": "value1"}
        data2 = {"key": "value2"}
        path1 = "test/path1"
        path2 = "test/path2"
        
        # 保存數據
        self.handler.save(data1, path1)
        self.handler.save(data2, path2)
        
        # 列出所有數據
        paths = self.handler.list()
        
        # 驗證結果
        self.assertEqual(len(paths), 2)
        self.assertIn(path1, paths)
        self.assertIn(path2, paths)
        
        # 列出前綴數據
        paths = self.handler.list("test")
        
        # 驗證結果
        self.assertEqual(len(paths), 2)
        self.assertIn(path1, paths)
        self.assertIn(path2, paths)
    
    def test_find(self):
        """測試查詢數據"""
        # 準備數據
        data1 = {"field": "value1", "other": "other1"}
        data2 = {"field": "value2", "other": "other2"}
        path1 = "test_path1"
        path2 = "test_path2"
        
        # 保存數據
        self.handler.save(data1, path1)
        self.handler.save(data2, path2)
        
        # 查詢數據
        query = {"field": "value1"}
        result = self.handler.find(query)
        
        # 驗證結果
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], data1)
    
    def test_count(self):
        """測試統計數據數量"""
        # 準備數據
        data1 = {"field": "value1"}
        data2 = {"field": "value2"}
        path1 = "test_path1"
        path2 = "test_path2"
        
        # 保存數據
        self.handler.save(data1, path1)
        self.handler.save(data2, path2)
        
        # 統計所有數據
        count = self.handler.count()
        
        # 驗證結果
        self.assertEqual(count, 2)
        
        # 統計條件數據
        query = {"field": "value1"}
        count = self.handler.count(query)
        
        # 驗證結果
        self.assertEqual(count, 1)
    
    def test_batch_save(self):
        """測試批量保存數據"""
        # 準備數據
        data_list = [
            {"path": "test_path1", "data": {"key": "value1"}},
            {"path": "test_path2", "data": {"key": "value2"}}
        ]
        
        # 批量保存數據
        self.handler.batch_save(data_list)
        
        # 驗證數據
        for item in data_list:
            result = self.handler.load(item["path"])
            self.assertEqual(result, item["data"])
    
    def test_batch_load(self):
        """測試批量加載數據"""
        # 準備數據
        data_list = [
            {"path": "test_path1", "data": {"key": "value1"}},
            {"path": "test_path2", "data": {"key": "value2"}}
        ]
        
        # 保存數據
        for item in data_list:
            self.handler.save(item["data"], item["path"])
        
        # 批量加載數據
        paths = [item["path"] for item in data_list]
        result = self.handler.batch_load(paths)
        
        # 驗證結果
        self.assertEqual(len(result), 2)
        for item in data_list:
            found = False
            for r in result:
                if r["path"] == item["path"]:
                    self.assertEqual(r["data"], item["data"])
                    found = True
                    break
            self.assertTrue(found)
    
    def test_batch_delete(self):
        """測試批量刪除數據"""
        # 準備數據
        data_list = [
            {"path": "test_path1", "data": {"key": "value1"}},
            {"path": "test_path2", "data": {"key": "value2"}}
        ]
        
        # 保存數據
        for item in data_list:
            self.handler.save(item["data"], item["path"])
        
        # 批量刪除數據
        paths = [item["path"] for item in data_list]
        self.handler.batch_delete(paths)
        
        # 驗證數據不存在
        for path in paths:
            with self.assertRaises(NotFoundError):
                self.handler.load(path)
    
    def test_batch_exists(self):
        """測試批量檢查數據是否存在"""
        # 準備數據
        data_list = [
            {"path": "test_path1", "data": {"key": "value1"}},
            {"path": "test_path2", "data": {"key": "value2"}}
        ]
        
        # 保存部分數據
        self.handler.save(data_list[0]["data"], data_list[0]["path"])
        
        # 批量檢查數據
        paths = [item["path"] for item in data_list]
        result = self.handler.batch_exists(paths)
        
        # 驗證結果
        self.assertTrue(result[paths[0]])
        self.assertFalse(result[paths[1]])
    
    def test_migrate_data(self):
        """測試數據遷移"""
        # 準備源數據
        source_data = [
            {"path": "test_path1", "data": {"key": "value1"}},
            {"path": "test_path2", "data": {"key": "value2"}}
        ]
        
        # 保存源數據
        for item in source_data:
            self.handler.save(item["data"], item["path"])
        
        # 創建目標處理器
        target_config = ClickHouseConfig(
            host="localhost",
            port=9000,
            database="test_db_target",
            table_name="test_table_target"
        )
        target_handler = ClickHouseHandler(target_config)
        
        try:
            # 遷移數據
            success_count, failed_count = self.handler.migrate_data(target_handler)
            
            # 驗證結果
            self.assertEqual(success_count, 2)
            self.assertEqual(failed_count, 0)
            
            # 驗證目標數據
            for item in source_data:
                result = target_handler.load(item["path"])
                self.assertEqual(result, item["data"])
        finally:
            # 清理目標表
            try:
                target_handler.client.execute(
                    f"DROP TABLE IF EXISTS {target_config.database}.{target_config.table_name}"
                )
            except:
                pass
    
    def test_migrate_schema(self):
        """測試表結構遷移"""
        # 創建目標處理器
        target_config = ClickHouseConfig(
            host="localhost",
            port=9000,
            database="test_db_target",
            table_name="test_table_target"
        )
        target_handler = ClickHouseHandler(target_config)
        
        try:
            # 遷移表結構
            self.handler.migrate_schema(target_handler)
            
            # 驗證目標表
            result = target_handler.client.execute(
                f"SHOW TABLES FROM {target_config.database}"
            )
            self.assertIn(target_config.table_name, [row[0] for row in result])
            
            # 獲取目標表結構
            target_schema = target_handler.client.execute(
                f"DESCRIBE TABLE {target_config.database}.{target_config.table_name}"
            )
            
            # 獲取源表結構
            source_schema = self.handler.client.execute(
                f"DESCRIBE TABLE {self.config.database}.{self.config.table_name}"
            )
            
            # 驗證表結構
            self.assertEqual(len(target_schema), len(source_schema))
            for i, (target_field, source_field) in enumerate(zip(target_schema, source_schema)):
                self.assertEqual(target_field[0], source_field[0])  # 字段名
                self.assertEqual(target_field[1], source_field[1])  # 字段類型
        finally:
            # 清理目標表
            try:
                target_handler.client.execute(
                    f"DROP TABLE IF EXISTS {target_config.database}.{target_config.table_name}"
                )
            except:
                pass
    
    def test_concurrent_operations(self):
        """測試並發操作"""
        import threading
        
        # 準備數據
        data_list = [
            {"path": f"test_path_{i}", "data": {"key": f"value_{i}"}}
            for i in range(100)
        ]
        
        # 定義保存線程
        def save_thread(items):
            for item in items:
                self.handler.save(item["data"], item["path"])
        
        # 定義加載線程
        def load_thread(items):
            for item in items:
                result = self.handler.load(item["path"])
                self.assertEqual(result, item["data"])
        
        # 定義刪除線程
        def delete_thread(items):
            for item in items:
                self.handler.delete(item["path"])
        
        # 創建線程
        threads = []
        chunk_size = len(data_list) // 4
        
        for i in range(0, len(data_list), chunk_size):
            chunk = data_list[i:i + chunk_size]
            threads.append(threading.Thread(target=save_thread, args=(chunk,)))
            threads.append(threading.Thread(target=load_thread, args=(chunk,)))
            threads.append(threading.Thread(target=delete_thread, args=(chunk,)))
        
        # 啟動線程
        for thread in threads:
            thread.start()
        
        # 等待線程完成
        for thread in threads:
            thread.join()
    
    def test_large_data(self):
        """測試大數據量"""
        # 準備大數據
        large_data = {
            "key": "value",
            "array": list(range(10000)),
            "nested": {
                "key1": "value1",
                "key2": "value2",
                "array": list(range(1000))
            }
        }
        path = "test_large_path"
        
        # 保存大數據
        self.handler.save(large_data, path)
        
        # 加載大數據
        result = self.handler.load(path)
        
        # 驗證結果
        self.assertEqual(result, large_data)
    
    @classmethod
    def tearDownClass(cls):
        """測試類清理"""
        # 清理測試表
        try:
            cls.handler.client.execute(
                f"DROP TABLE IF EXISTS {cls.config.database}.{cls.config.table_name}"
            )
        except:
            pass

if __name__ == "__main__":
    unittest.main() 