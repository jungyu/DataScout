#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SQL Server存儲處理器單元測試
"""

import unittest
from unittest.mock import MagicMock, patch
import json
from datetime import datetime
from persistence.handlers.sqlserver_handler import SQLServerHandler
from persistence.core.config import SQLServerConfig
from persistence.core.exceptions import (
    StorageError,
    NotFoundError,
    ValidationError,
    ConnectionError
)

class TestSQLServerHandler(unittest.TestCase):
    """SQL Server存儲處理器測試類"""
    
    def setUp(self):
        """測試前準備"""
        # 創建配置
        self.config = SQLServerConfig(
            host='localhost',
            port=1433,
            username='test',
            password='test',
            database='test_db',
            table_name='test_table'
        )
        
        # 創建處理器
        self.handler = SQLServerHandler(self.config)
        
        # 模擬引擎和會話
        self.mock_engine = MagicMock()
        self.mock_session = MagicMock()
        self.mock_table = MagicMock()
        
        # 設置模擬對象
        self.handler.engine = self.mock_engine
        self.handler.session = self.mock_session
        self.handler.table = self.mock_table
    
    def test_init(self):
        """測試初始化"""
        # 測試配置對象
        handler = SQLServerHandler(self.config)
        self.assertEqual(handler.config, self.config)
        
        # 測試配置字典
        config_dict = {
            'host': 'localhost',
            'port': 1433,
            'username': 'test',
            'password': 'test',
            'database': 'test_db',
            'table_name': 'test_table'
        }
        handler = SQLServerHandler(config_dict)
        self.assertEqual(handler.config.host, 'localhost')
        self.assertEqual(handler.config.port, 1433)
    
    def test_setup_storage(self):
        """測試存儲環境設置"""
        # 模擬創建引擎
        with patch('sqlalchemy.create_engine') as mock_create_engine:
            mock_create_engine.return_value = self.mock_engine
            
            # 模擬創建會話
            with patch('sqlalchemy.orm.sessionmaker') as mock_sessionmaker:
                mock_sessionmaker.return_value.return_value = self.mock_session
                
                # 測試設置存儲環境
                self.handler._setup_storage()
                
                # 驗證調用
                mock_create_engine.assert_called_once()
                mock_sessionmaker.assert_called_once()
    
    def test_build_connection_uri(self):
        """測試構建連接URI"""
        # 測試使用端口
        uri = self.handler._build_connection_uri()
        self.assertIn('mssql+pyodbc://', uri)
        self.assertIn('localhost:1433', uri)
        
        # 測試使用實例名
        self.config.instance = 'test_instance'
        uri = self.handler._build_connection_uri()
        self.assertIn('localhost\\test_instance', uri)
    
    def test_create_table(self):
        """測試創建表"""
        # 模擬創建表
        with patch('sqlalchemy.MetaData') as mock_metadata:
            mock_metadata.return_value.create_all.return_value = None
            
            # 測試創建表
            self.handler._create_table()
            
            # 驗證調用
            mock_metadata.return_value.create_all.assert_called_once_with(
                self.mock_engine
            )
    
    def test_save(self):
        """測試保存數據"""
        # 準備測試數據
        data = {'key': 'value'}
        path = 'test/path'
        
        # 模擬序列化
        serialized_data = json.dumps(data)
        
        # 模擬檢查存在
        self.handler.exists = MagicMock(return_value=False)
        
        # 模擬插入
        self.mock_table.insert.return_value.values.return_value.execute.return_value = None
        
        # 測試保存
        self.handler.save(data, path)
        
        # 驗證調用
        self.mock_table.insert.assert_called_once()
        self.mock_session.commit.assert_called_once()
    
    def test_load(self):
        """測試加載數據"""
        # 準備測試數據
        path = 'test/path'
        data = {'key': 'value'}
        serialized_data = json.dumps(data)
        
        # 模擬查詢結果
        mock_result = MagicMock()
        mock_result.__getitem__.return_value = serialized_data
        self.mock_table.select.return_value.where.return_value.execute.return_value.first.return_value = mock_result
        
        # 測試加載
        result = self.handler.load(path)
        
        # 驗證結果
        self.assertEqual(result, data)
    
    def test_delete(self):
        """測試刪除數據"""
        # 準備測試數據
        path = 'test/path'
        
        # 模擬刪除結果
        mock_result = MagicMock()
        mock_result.rowcount = 1
        self.mock_table.delete.return_value.where.return_value.execute.return_value = mock_result
        
        # 測試刪除
        self.handler.delete(path)
        
        # 驗證調用
        self.mock_table.delete.assert_called_once()
        self.mock_session.commit.assert_called_once()
    
    def test_exists(self):
        """測試檢查數據是否存在"""
        # 準備測試數據
        path = 'test/path'
        
        # 模擬查詢結果
        self.mock_table.select.return_value.where.return_value.execute.return_value.first.return_value = MagicMock()
        
        # 測試存在
        result = self.handler.exists(path)
        
        # 驗證結果
        self.assertTrue(result)
    
    def test_list(self):
        """測試列出數據"""
        # 準備測試數據
        path = 'test'
        
        # 模擬查詢結果
        mock_row1 = MagicMock()
        mock_row1.__getitem__.return_value = 'test/path1'
        mock_row2 = MagicMock()
        mock_row2.__getitem__.return_value = 'test/path2'
        self.mock_table.select.return_value.where.return_value.execute.return_value = [mock_row1, mock_row2]
        
        # 測試列出
        result = self.handler.list(path)
        
        # 驗證結果
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0], 'test/path1')
        self.assertEqual(result[1], 'test/path2')
    
    def test_find(self):
        """測試查詢數據"""
        # 準備測試數據
        query = {'field': 'value'}
        data = {'key': 'value'}
        serialized_data = json.dumps(data)
        
        # 模擬查詢結果
        mock_row = MagicMock()
        mock_row.__getitem__.side_effect = lambda key: serialized_data if key == self.config.data_field else 'value'
        self.mock_table.select.return_value.where.return_value.execute.return_value = [mock_row]
        
        # 測試查詢
        result = self.handler.find(query)
        
        # 驗證結果
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0][self.config.data_field], data)
    
    def test_count(self):
        """測試統計數據數量"""
        # 準備測試數據
        query = {'field': 'value'}
        
        # 模擬查詢結果
        mock_result = MagicMock()
        mock_result.rowcount = 10
        self.mock_table.select.return_value.where.return_value.execute.return_value = mock_result
        
        # 測試統計
        result = self.handler.count(query)
        
        # 驗證結果
        self.assertEqual(result, 10)
    
    def test_cleanup(self):
        """測試清理資源"""
        # 測試清理
        self.handler.__del__()
        
        # 驗證調用
        self.mock_session.close.assert_called_once()
        self.mock_engine.dispose.assert_called_once()

if __name__ == '__main__':
    unittest.main() 