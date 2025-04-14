#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Amazon 處理器單元測試
"""

import json
import unittest
from unittest.mock import Mock, patch, MagicMock
from api_client.handlers.amazon_handler import AmazonHandler
from api_client.core.config import APIConfig
from api_client.core.exceptions import APIError, AuthenticationError, RequestError

class TestAmazonHandler(unittest.TestCase):
    """Amazon 處理器測試類"""
    
    def setUp(self):
        """測試前準備"""
        # 創建配置對象
        self.config = APIConfig(
            api_type="rest",
            base_url="https://webservices.amazon.com",
            auth_type="api_key",
            associate_tag="test_associate_tag",
            aws_access_key_id="test_access_key",
            aws_secret_key="test_secret_key",
            region="us-east-1"
        )
        
        # 創建處理器實例
        self.handler = AmazonHandler(self.config)
        
        # 模擬請求方法
        self.handler.get = Mock()
    
    def test_init_with_dict(self):
        """測試使用字典初始化"""
        config_dict = {
            "api_type": "rest",
            "base_url": "https://webservices.amazon.com",
            "auth_type": "api_key",
            "associate_tag": "test_associate_tag",
            "aws_access_key_id": "test_access_key",
            "aws_secret_key": "test_secret_key",
            "region": "us-east-1"
        }
        
        handler = AmazonHandler(config_dict)
        self.assertEqual(handler.associate_tag, "test_associate_tag")
        self.assertEqual(handler.aws_access_key_id, "test_access_key")
        self.assertEqual(handler.aws_secret_key, "test_secret_key")
        self.assertEqual(handler.region, "us-east-1")
    
    def test_init_with_config(self):
        """測試使用配置對象初始化"""
        self.assertEqual(self.handler.associate_tag, "test_associate_tag")
        self.assertEqual(self.handler.aws_access_key_id, "test_access_key")
        self.assertEqual(self.handler.aws_secret_key, "test_secret_key")
        self.assertEqual(self.handler.region, "us-east-1")
    
    def test_generate_signature(self):
        """測試簽名生成"""
        # 準備測試數據
        params = {
            "Service": "ProductAdvertisingAPI",
            "Operation": "SearchItems",
            "AWSAccessKeyId": "test_access_key",
            "AssociateTag": "test_associate_tag",
            "Keywords": "test",
            "Timestamp": "2023-01-01T00:00:00Z",
            "Version": "2013-08-01"
        }
        
        # 調用方法
        signature = self.handler._generate_signature(params, "test_secret_key")
        
        # 驗證結果
        self.assertIsInstance(signature, str)
        self.assertTrue(len(signature) > 0)
    
    def test_prepare_params(self):
        """測試參數準備"""
        # 準備測試數據
        operation = "SearchItems"
        params = {
            "Keywords": "test",
            "SearchIndex": "All",
            "ItemCount": 10,
            "ItemPage": 1
        }
        
        # 調用方法
        result = self.handler._prepare_params(operation, params)
        
        # 驗證結果
        self.assertEqual(result["Service"], "ProductAdvertisingAPI")
        self.assertEqual(result["Operation"], operation)
        self.assertEqual(result["AWSAccessKeyId"], "test_access_key")
        self.assertEqual(result["AssociateTag"], "test_associate_tag")
        self.assertEqual(result["Version"], "2013-08-01")
        self.assertEqual(result["Keywords"], "test")
        self.assertEqual(result["SearchIndex"], "All")
        self.assertEqual(result["ItemCount"], 10)
        self.assertEqual(result["ItemPage"], 1)
        self.assertIn("Timestamp", result)
        self.assertIn("Signature", result)
    
    def test_search_items(self):
        """測試商品搜索"""
        # 設置模擬返回值
        self.handler.get.return_value = {"Items": []}
        
        # 調用方法
        result = self.handler.search_items("test", "All", 10, 1)
        
        # 驗證結果
        self.handler.get.assert_called_once()
        self.assertEqual(result, {"Items": []})
    
    def test_get_items(self):
        """測試獲取商品詳情"""
        # 設置模擬返回值
        self.handler.get.return_value = {"Items": []}
        
        # 準備測試數據
        item_ids = ["B00TEST123", "B00TEST456"]
        
        # 調用方法
        result = self.handler.get_items(item_ids)
        
        # 驗證結果
        self.handler.get.assert_called_once()
        self.assertEqual(result, {"Items": []})
    
    def test_get_browse_nodes(self):
        """測試獲取瀏覽節點"""
        # 設置模擬返回值
        self.handler.get.return_value = {"BrowseNodes": []}
        
        # 準備測試數據
        browse_node_ids = ["123", "456"]
        
        # 調用方法
        result = self.handler.get_browse_nodes(browse_node_ids)
        
        # 驗證結果
        self.handler.get.assert_called_once()
        self.assertEqual(result, {"BrowseNodes": []})
    
    def test_get_variations(self):
        """測試獲取商品變體"""
        # 設置模擬返回值
        self.handler.get.return_value = {"Variations": []}
        
        # 準備測試數據
        asin = "B00TEST123"
        
        # 調用方法
        result = self.handler.get_variations(asin)
        
        # 驗證結果
        self.handler.get.assert_called_once()
        self.assertEqual(result, {"Variations": []})
    
    def test_get_items_offers(self):
        """測試獲取商品優惠"""
        # 設置模擬返回值
        self.handler.get.return_value = {"Items": []}
        
        # 準備測試數據
        item_ids = ["B00TEST123", "B00TEST456"]
        
        # 調用方法
        result = self.handler.get_items_offers(item_ids)
        
        # 驗證結果
        self.handler.get.assert_called_once()
        self.assertEqual(result, {"Items": []})
    
    def test_get_cart(self):
        """測試獲取購物車"""
        # 設置模擬返回值
        self.handler.get.return_value = {"Cart": {}}
        
        # 準備測試數據
        cart_id = "test_cart_id"
        hmac = "test_hmac"
        
        # 調用方法
        result = self.handler.get_cart(cart_id, hmac)
        
        # 驗證結果
        self.handler.get.assert_called_once()
        self.assertEqual(result, {"Cart": {}})
    
    def test_create_cart(self):
        """測試創建購物車"""
        # 設置模擬返回值
        self.handler.get.return_value = {"Cart": {}}
        
        # 準備測試數據
        items = [
            {"ASIN": "B00TEST123", "Quantity": 1},
            {"ASIN": "B00TEST456", "Quantity": 2}
        ]
        
        # 調用方法
        result = self.handler.create_cart(items)
        
        # 驗證結果
        self.handler.get.assert_called_once()
        self.assertEqual(result, {"Cart": {}})
    
    def test_add_to_cart(self):
        """測試添加商品到購物車"""
        # 設置模擬返回值
        self.handler.get.return_value = {"Cart": {}}
        
        # 準備測試數據
        cart_id = "test_cart_id"
        hmac = "test_hmac"
        items = [
            {"ASIN": "B00TEST123", "Quantity": 1},
            {"ASIN": "B00TEST456", "Quantity": 2}
        ]
        
        # 調用方法
        result = self.handler.add_to_cart(cart_id, hmac, items)
        
        # 驗證結果
        self.handler.get.assert_called_once()
        self.assertEqual(result, {"Cart": {}})
    
    def test_search_items_error(self):
        """測試商品搜索錯誤處理"""
        # 設置模擬錯誤
        self.handler.get.side_effect = APIError("API Error")
        
        # 驗證異常拋出
        with self.assertRaises(APIError):
            self.handler.search_items("test")
    
    def test_search_items_auth_error(self):
        """測試商品搜索認證錯誤處理"""
        # 設置模擬錯誤
        self.handler.get.side_effect = AuthenticationError("Auth Error")
        
        # 驗證異常拋出
        with self.assertRaises(AuthenticationError):
            self.handler.search_items("test")
    
    def test_search_items_request_error(self):
        """測試商品搜索請求錯誤處理"""
        # 設置模擬錯誤
        self.handler.get.side_effect = RequestError("Request Error")
        
        # 驗證異常拋出
        with self.assertRaises(RequestError):
            self.handler.search_items("test") 