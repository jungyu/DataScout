#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ClickHouse 存儲處理器單元測試
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from persistence.handlers.clickhouse_handler import ClickHouseHandler
from persistence.core.config import ClickHouseConfig
from persistence.core.exceptions import (
    StorageError,
    NotFoundError,
    ValidationError,
    ConnectionError
)

class TestClickHouseHandler(unittest.TestCase):
    """ClickHouse 存儲處理器測試類"""
    
    def setUp(self):
        """每個測試前準備"""
        # 創建配置
        self.config = ClickHouseConfig(
            host="localhost",
            port=9000,
            database="test_db",
            table_name="test_table"
        )
        
        # 創建處理器
        self.handler = ClickHouseHandler(self.config)
        
        # 模擬客戶端
        self.handler.client = Mock()
    
    def test_init(self):
        """測試初始化"""
        # 測試字典配置
        config_dict = {
            "host": "localhost",
            "port": 9000,
            "database": "test_db",
            "table_name": "test_table"
        }
        handler = ClickHouseHandler(config_dict)
        self.assertIsInstance(handler.config, ClickHouseConfig)
        
        # 測試配置實例
        handler = ClickHouseHandler(self.config)
        self.assertEqual(handler.config, self.config)
    
    def test_setup_storage(self):
        """測試設置存儲環境"""
        with patch("clickhouse_driver.Client") as mock_client:
            # 模擬客戶端
            mock_client.return_value = Mock()
            
            # 創建處理器
            handler = ClickHouseHandler(self.config)
            
            # 驗證客戶端創建
            mock_client.assert_called_once()
            
            # 驗證表創建
            handler.client.execute.assert_called()
    
    def test_create_table(self):
        """測試創建表"""
        # 模擬客戶端
        self.handler.client.execute = Mock()
        
        # 創建表
        self.handler._create_table()
        
        # 驗證建表 SQL
        self.handler.client.execute.assert_called_once()
        sql = self.handler.client.execute.call_args[0][0]
        self.assertIn("CREATE TABLE IF NOT EXISTS", sql)
        self.assertIn(self.config.table_name, sql)
    
    def test_save(self):
        """測試保存數據"""
        # 準備數據
        data = {"key": "value"}
        path = "test_path"
        
        # 模擬客戶端
        self.handler.client.execute = Mock()
        
        # 保存數據
        self.handler.save(data, path)
        
        # 驗證插入
        self.handler.client.execute.assert_called_once()
        sql = self.handler.client.execute.call_args[0][0]
        self.assertIn("INSERT INTO", sql)
        self.assertIn(self.config.table_name, sql)
    
    def test_load(self):
        """測試加載數據"""
        # 準備數據
        path = "test_path"
        data = {"key": "value"}
        data_str = '{"key": "value"}'
        
        # 模擬客戶端
        self.handler.client.execute = Mock(return_value=[[data_str]])
        
        # 加載數據
        result = self.handler.load(path)
        
        # 驗證查詢
        self.handler.client.execute.assert_called_once()
        sql = self.handler.client.execute.call_args[0][0]
        self.assertIn("SELECT", sql)
        self.assertIn(self.config.table_name, sql)
        
        # 驗證結果
        self.assertEqual(result, data)
    
    def test_load_not_found(self):
        """測試加載不存在的數據"""
        # 準備數據
        path = "test_path"
        
        # 模擬客戶端
        self.handler.client.execute = Mock(return_value=[])
        
        # 驗證異常
        with self.assertRaises(NotFoundError):
            self.handler.load(path)
    
    def test_delete(self):
        """測試刪除數據"""
        # 準備數據
        path = "test_path"
        
        # 模擬客戶端
        self.handler.client.execute = Mock()
        
        # 刪除數據
        self.handler.delete(path)
        
        # 驗證刪除
        self.handler.client.execute.assert_called_once()
        sql = self.handler.client.execute.call_args[0][0]
        self.assertIn("DELETE", sql)
        self.assertIn(self.config.table_name, sql)
    
    def test_exists(self):
        """測試檢查數據是否存在"""
        # 準備數據
        path = "test_path"
        
        # 模擬客戶端
        self.handler.client.execute = Mock(return_value=[[1]])
        
        # 檢查存在
        result = self.handler.exists(path)
        
        # 驗證查詢
        self.handler.client.execute.assert_called_once()
        sql = self.handler.client.execute.call_args[0][0]
        self.assertIn("SELECT count()", sql)
        self.assertIn(self.config.table_name, sql)
        
        # 驗證結果
        self.assertTrue(result)
    
    def test_list(self):
        """測試列出數據"""
        # 準備數據
        prefix = "test"
        paths = ["test/path1", "test/path2"]
        
        # 模擬客戶端
        self.handler.client.execute = Mock(return_value=[[p] for p in paths])
        
        # 列出數據
        result = self.handler.list(prefix)
        
        # 驗證查詢
        self.handler.client.execute.assert_called_once()
        sql = self.handler.client.execute.call_args[0][0]
        self.assertIn("SELECT DISTINCT", sql)
        self.assertIn(self.config.table_name, sql)
        
        # 驗證結果
        self.assertEqual(result, paths)
    
    def test_find(self):
        """測試查詢數據"""
        # 準備數據
        query = {"field": "value"}
        data = {"field": "value", "other": "other"}
        data_str = '{"field": "value", "other": "other"}'
        
        # 模擬客戶端
        self.handler.client.execute = Mock(return_value=[[data_str]])
        
        # 查詢數據
        result = self.handler.find(query)
        
        # 驗證查詢
        self.handler.client.execute.assert_called_once()
        sql = self.handler.client.execute.call_args[0][0]
        self.assertIn("SELECT", sql)
        self.assertIn(self.config.table_name, sql)
        
        # 驗證結果
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], data)
    
    def test_count(self):
        """測試統計數據數量"""
        # 準備數據
        query = {"field": "value"}
        
        # 模擬客戶端
        self.handler.client.execute = Mock(return_value=[[10]])
        
        # 統計數量
        result = self.handler.count(query)
        
        # 驗證查詢
        self.handler.client.execute.assert_called_once()
        sql = self.handler.client.execute.call_args[0][0]
        self.assertIn("SELECT count()", sql)
        self.assertIn(self.config.table_name, sql)
        
        # 驗證結果
        self.assertEqual(result, 10)
    
    def test_batch_save(self):
        """測試批量保存數據"""
        # 準備數據
        data_list = [
            {"path": "test_path1", "data": {"key": "value1"}},
            {"path": "test_path2", "data": {"key": "value2"}}
        ]
        
        # 模擬客戶端
        self.handler.client.execute = Mock()
        
        # 批量保存
        self.handler.batch_save(data_list)
        
        # 驗證插入
        self.handler.client.execute.assert_called_once()
        sql = self.handler.client.execute.call_args[0][0]
        self.assertIn("INSERT INTO", sql)
        self.assertIn(self.config.table_name, sql)
    
    def test_batch_load(self):
        """測試批量加載數據"""
        # 準備數據
        paths = ["test_path1", "test_path2"]
        data_list = [
            ["test_path1", '{"key": "value1"}'],
            ["test_path2", '{"key": "value2"}']
        ]
        
        # 模擬客戶端
        self.handler.client.execute = Mock(return_value=data_list)
        
        # 批量加載
        result = self.handler.batch_load(paths)
        
        # 驗證查詢
        self.handler.client.execute.assert_called_once()
        sql = self.handler.client.execute.call_args[0][0]
        self.assertIn("SELECT", sql)
        self.assertIn(self.config.table_name, sql)
        
        # 驗證結果
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["path"], "test_path1")
        self.assertEqual(result[0]["data"], {"key": "value1"})
        self.assertEqual(result[1]["path"], "test_path2")
        self.assertEqual(result[1]["data"], {"key": "value2"})
    
    def test_batch_delete(self):
        """測試批量刪除數據"""
        # 準備數據
        paths = ["test_path1", "test_path2"]
        
        # 模擬客戶端
        self.handler.client.execute = Mock()
        
        # 批量刪除
        self.handler.batch_delete(paths)
        
        # 驗證刪除
        self.handler.client.execute.assert_called_once()
        sql = self.handler.client.execute.call_args[0][0]
        self.assertIn("DELETE", sql)
        self.assertIn(self.config.table_name, sql)
    
    def test_batch_exists(self):
        """測試批量檢查數據是否存在"""
        # 準備數據
        paths = ["test_path1", "test_path2"]
        exists_list = [
            ["test_path1", 1],
            ["test_path2", 0]
        ]
        
        # 模擬客戶端
        self.handler.client.execute = Mock(return_value=exists_list)
        
        # 批量檢查
        result = self.handler.batch_exists(paths)
        
        # 驗證查詢
        self.handler.client.execute.assert_called_once()
        sql = self.handler.client.execute.call_args[0][0]
        self.assertIn("SELECT", sql)
        self.assertIn(self.config.table_name, sql)
        
        # 驗證結果
        self.assertTrue(result["test_path1"])
        self.assertFalse(result["test_path2"])
    
    def test_migrate_data(self):
        """測試數據遷移"""
        # 準備數據
        paths = ["test_path1", "test_path2"]
        data_list = [
            {"path": "test_path1", "data": {"key": "value1"}},
            {"path": "test_path2", "data": {"key": "value2"}}
        ]
        
        # 模擬源處理器
        self.handler.list = Mock(return_value=paths)
        self.handler.batch_load = Mock(return_value=data_list)
        
        # 模擬目標處理器
        target_handler = Mock()
        target_handler.batch_save = Mock()
        
        # 遷移數據
        success_count, failed_count = self.handler.migrate_data(target_handler)
        
        # 驗證遷移
        self.handler.list.assert_called_once()
        self.handler.batch_load.assert_called_once_with(paths)
        target_handler.batch_save.assert_called_once_with(data_list)
        
        # 驗證結果
        self.assertEqual(success_count, 2)
        self.assertEqual(failed_count, 0)
    
    def test_migrate_schema(self):
        """測試表結構遷移"""
        # 準備數據
        create_sql = "CREATE TABLE test_db.test_table ..."
        
        # 模擬源處理器
        self.handler.client.execute = Mock(return_value=[[create_sql]])
        
        # 模擬目標處理器
        target_handler = Mock()
        target_handler.config.database = "target_db"
        target_handler.config.table_name = "target_table"
        target_handler.client.execute = Mock()
        
        # 遷移表結構
        self.handler.migrate_schema(target_handler)
        
        # 驗證遷移
        self.handler.client.execute.assert_called_once()
        target_handler.client.execute.assert_called_once()
        sql = target_handler.client.execute.call_args[0][0]
        self.assertIn("target_db.target_table", sql)
    
    def test_cleanup(self):
        """測試清理資源"""
        # 模擬客戶端
        self.handler.client.disconnect = Mock()
        
        # 清理資源
        self.handler.cleanup()
        
        # 驗證斷開連接
        self.handler.client.disconnect.assert_called_once()

if __name__ == "__main__":
    unittest.main() 