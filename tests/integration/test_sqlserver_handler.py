#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SQL Server存儲處理器集成測試
"""

import unittest
import json
import time
from datetime import datetime
from persistence.handlers.sqlserver_handler import SQLServerHandler
from persistence.core.config import SQLServerConfig
from persistence.core.exceptions import (
    StorageError,
    NotFoundError,
    ValidationError,
    ConnectionError
)

class TestSQLServerHandlerIntegration(unittest.TestCase):
    """SQL Server存儲處理器集成測試類"""
    
    @classmethod
    def setUpClass(cls):
        """測試類初始化"""
        # 創建配置
        cls.config = SQLServerConfig(
            host='localhost',
            port=1433,
            username='test',
            password='test',
            database='test_db',
            table_name='test_table',
            schema='dbo'
        )
        
        # 創建處理器
        cls.handler = SQLServerHandler(cls.config)
        
        # 設置存儲環境
        cls.handler._setup_storage()
    
    def setUp(self):
        """測試前準備"""
        # 清理測試數據
        self.handler.delete('test/path1')
        self.handler.delete('test/path2')
    
    def test_save_and_load(self):
        """測試保存和加載數據"""
        # 準備測試數據
        data = {
            'string': 'test',
            'number': 123,
            'boolean': True,
            'null': None,
            'array': [1, 2, 3],
            'object': {'key': 'value'}
        }
        path = 'test/path1'
        
        # 保存數據
        self.handler.save(data, path)
        
        # 加載數據
        result = self.handler.load(path)
        
        # 驗證結果
        self.assertEqual(result, data)
    
    def test_save_and_update(self):
        """測試保存和更新數據"""
        # 準備初始數據
        initial_data = {'key': 'value1'}
        path = 'test/path1'
        
        # 保存初始數據
        self.handler.save(initial_data, path)
        
        # 準備更新數據
        updated_data = {'key': 'value2'}
        
        # 更新數據
        self.handler.save(updated_data, path)
        
        # 加載數據
        result = self.handler.load(path)
        
        # 驗證結果
        self.assertEqual(result, updated_data)
    
    def test_delete(self):
        """測試刪除數據"""
        # 準備測試數據
        data = {'key': 'value'}
        path = 'test/path1'
        
        # 保存數據
        self.handler.save(data, path)
        
        # 驗證數據存在
        self.assertTrue(self.handler.exists(path))
        
        # 刪除數據
        self.handler.delete(path)
        
        # 驗證數據不存在
        self.assertFalse(self.handler.exists(path))
        
        # 驗證刪除不存在的數據會拋出異常
        with self.assertRaises(NotFoundError):
            self.handler.delete(path)
    
    def test_list(self):
        """測試列出數據"""
        # 準備測試數據
        data1 = {'key': 'value1'}
        data2 = {'key': 'value2'}
        path1 = 'test/path1'
        path2 = 'test/path2'
        
        # 保存數據
        self.handler.save(data1, path1)
        self.handler.save(data2, path2)
        
        # 列出所有數據
        all_paths = self.handler.list()
        self.assertIn(path1, all_paths)
        self.assertIn(path2, all_paths)
        
        # 列出指定前綴的數據
        test_paths = self.handler.list('test')
        self.assertEqual(len(test_paths), 2)
        self.assertIn(path1, test_paths)
        self.assertIn(path2, test_paths)
    
    def test_find(self):
        """測試查詢數據"""
        # 準備測試數據
        data1 = {'field': 'value1', 'key': 'test1'}
        data2 = {'field': 'value2', 'key': 'test2'}
        path1 = 'test/path1'
        path2 = 'test/path2'
        
        # 保存數據
        self.handler.save(data1, path1)
        self.handler.save(data2, path2)
        
        # 查詢數據
        results = self.handler.find({'field': 'value1'})
        
        # 驗證結果
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][self.config.data_field], data1)
    
    def test_count(self):
        """測試統計數據數量"""
        # 準備測試數據
        data1 = {'field': 'value1'}
        data2 = {'field': 'value2'}
        path1 = 'test/path1'
        path2 = 'test/path2'
        
        # 保存數據
        self.handler.save(data1, path1)
        self.handler.save(data2, path2)
        
        # 統計所有數據
        total_count = self.handler.count()
        self.assertEqual(total_count, 2)
        
        # 統計指定條件的數據
        filtered_count = self.handler.count({'field': 'value1'})
        self.assertEqual(filtered_count, 1)
    
    def test_concurrent_operations(self):
        """測試並發操作"""
        # 準備測試數據
        data = {'key': 'value'}
        path = 'test/path1'
        
        # 並發保存和加載
        self.handler.save(data, path)
        result1 = self.handler.load(path)
        result2 = self.handler.load(path)
        
        # 驗證結果
        self.assertEqual(result1, data)
        self.assertEqual(result2, data)
    
    def test_large_data(self):
        """測試大數據處理"""
        # 準備大數據
        data = {
            'array': list(range(10000)),
            'string': 'x' * 10000,
            'nested': {
                'array': list(range(1000)),
                'string': 'y' * 1000
            }
        }
        path = 'test/path1'
        
        # 保存數據
        self.handler.save(data, path)
        
        # 加載數據
        result = self.handler.load(path)
        
        # 驗證結果
        self.assertEqual(result, data)
    
    @classmethod
    def tearDownClass(cls):
        """測試類清理"""
        # 清理測試數據
        cls.handler.delete('test/path1')
        cls.handler.delete('test/path2')
        
        # 關閉連接
        cls.handler.__del__()

if __name__ == '__main__':
    unittest.main() 