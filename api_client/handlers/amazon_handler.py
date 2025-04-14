#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Amazon 處理器
提供與 Amazon 平台的整合功能
"""

import time
import hashlib
import hmac
import base64
import urllib.parse
import json
import logging
import requests
from typing import Dict, Any, Optional, List, Union
from api_client.core.base_client import BaseClient
from api_client.core.config import APIConfig
from api_client.core.exceptions import APIError, AuthenticationError, RequestError
from api_client.utils.utils import Utils

class AmazonHandler(BaseClient):
    """Amazon API 處理器"""
    
    def __init__(self, config: Union[Dict[str, Any], APIConfig]):
        """初始化 Amazon API 處理器
        
        Args:
            config: 配置對象，可以是字典或配置類實例
        """
        # 設置 API 類型
        if isinstance(config, dict):
            config["api_type"] = "rest"
            config["base_url"] = config.get("base_url", "https://webservices.amazon.com")
            config["auth_type"] = config.get("auth_type", "api_key")
        else:
            config.api_type = "rest"
            config.base_url = config.base_url or "https://webservices.amazon.com"
            config.auth_type = config.auth_type or "api_key"
        
        # 初始化父類
        super().__init__(config)
        
        # 初始化工具類
        self.utils = Utils()
        
        # 設置 Amazon 特定參數
        if isinstance(config, dict):
            self.associate_tag = config.get("associate_tag", "")
            self.aws_access_key_id = config.get("aws_access_key_id", "")
            self.aws_secret_key = config.get("aws_secret_key", "")
            self.region = config.get("region", "us-east-1")
        else:
            self.associate_tag = getattr(config, "associate_tag", "")
            self.aws_access_key_id = getattr(config, "aws_access_key_id", "")
            self.aws_secret_key = getattr(config, "aws_secret_key", "")
            self.region = getattr(config, "region", "us-east-1")
    
    def _generate_signature(self, params: Dict[str, Any], secret_key: str) -> str:
        """生成 Amazon API 簽名
        
        Args:
            params: 請求參數
            secret_key: AWS 密鑰
            
        Returns:
            簽名字符串
        """
        # 對參數進行排序
        sorted_params = sorted(params.items())
        
        # 構建簽名字符串
        string_to_sign = "GET\nwebservices.amazon.com\n/onca/xml\n"
        param_string = "&".join([f"{urllib.parse.quote(key, safe='~')}={urllib.parse.quote(str(value), safe='~')}" for key, value in sorted_params])
        string_to_sign += param_string
        
        # 計算簽名
        signature = base64.b64encode(
            hmac.new(
                secret_key.encode('utf-8'),
                string_to_sign.encode('utf-8'),
                hashlib.sha256
            ).digest()
        ).decode('utf-8')
        
        return signature
    
    def _prepare_params(self, operation: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """準備請求參數
        
        Args:
            operation: API 操作名稱
            params: 原始參數
            
        Returns:
            處理後的參數
        """
        # 基本參數
        request_params = {
            "Service": "ProductAdvertisingAPI",
            "Operation": operation,
            "AWSAccessKeyId": self.aws_access_key_id,
            "AssociateTag": self.associate_tag,
            "Timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "Version": "2013-08-01"
        }
        
        # 添加自定義參數
        request_params.update(params)
        
        # 生成簽名
        signature = self._generate_signature(request_params, self.aws_secret_key)
        request_params["Signature"] = signature
        
        return request_params
    
    def search_items(self, keywords: str, search_index: str = "All", item_count: int = 10, item_page: int = 1) -> Dict[str, Any]:
        """搜索商品
        
        Args:
            keywords: 搜索關鍵詞
            search_index: 搜索索引
            item_count: 每頁結果數量
            item_page: 頁碼
            
        Returns:
            搜索結果
        """
        params = {
            "Keywords": keywords,
            "SearchIndex": search_index,
            "ItemCount": item_count,
            "ItemPage": item_page
        }
        
        request_params = self._prepare_params("SearchItems", params)
        return self.get("/paapi5/searchitems", params=request_params)
    
    def get_items(self, item_ids: List[str]) -> Dict[str, Any]:
        """獲取商品詳情
        
        Args:
            item_ids: 商品 ID 列表
            
        Returns:
            商品詳情
        """
        params = {
            "ItemIds": item_ids
        }
        
        request_params = self._prepare_params("GetItems", params)
        return self.get("/paapi5/getitems", params=request_params)
    
    def get_browse_nodes(self, browse_node_ids: List[str]) -> Dict[str, Any]:
        """獲取瀏覽節點
        
        Args:
            browse_node_ids: 瀏覽節點 ID 列表
            
        Returns:
            瀏覽節點信息
        """
        params = {
            "BrowseNodeIds": browse_node_ids
        }
        
        request_params = self._prepare_params("GetBrowseNodes", params)
        return self.get("/paapi5/getbrowsenodes", params=request_params)
    
    def get_variations(self, asin: str, variation_count: int = 10, variation_page: int = 1) -> Dict[str, Any]:
        """獲取商品變體
        
        Args:
            asin: 商品 ASIN
            variation_count: 變體數量
            variation_page: 變體頁碼
            
        Returns:
            商品變體信息
        """
        params = {
            "ASIN": asin,
            "VariationCount": variation_count,
            "VariationPage": variation_page
        }
        
        request_params = self._prepare_params("GetVariations", params)
        return self.get("/paapi5/getvariations", params=request_params)
    
    def get_items_offers(self, item_ids: List[str], offer_count: int = 5) -> Dict[str, Any]:
        """獲取商品優惠
        
        Args:
            item_ids: 商品 ID 列表
            offer_count: 優惠數量
            
        Returns:
            商品優惠信息
        """
        params = {
            "ItemIds": item_ids,
            "OfferCount": offer_count
        }
        
        request_params = self._prepare_params("GetItemsOffers", params)
        return self.get("/paapi5/getitemsoffers", params=request_params)
    
    def get_cart(self, cart_id: str, hmac: str) -> Dict[str, Any]:
        """獲取購物車
        
        Args:
            cart_id: 購物車 ID
            hmac: 購物車 HMAC
            
        Returns:
            購物車信息
        """
        params = {
            "CartId": cart_id,
            "HMAC": hmac
        }
        
        request_params = self._prepare_params("GetCart", params)
        return self.get("/paapi5/getcart", params=request_params)
    
    def create_cart(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """創建購物車
        
        Args:
            items: 購物車項目列表
            
        Returns:
            購物車信息
        """
        params = {
            "Items": items
        }
        
        request_params = self._prepare_params("CreateCart", params)
        return self.get("/paapi5/createcart", params=request_params)
    
    def add_to_cart(self, cart_id: str, hmac: str, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """添加商品到購物車
        
        Args:
            cart_id: 購物車 ID
            hmac: 購物車 HMAC
            items: 要添加的商品列表
            
        Returns:
            更新後的購物車信息
        """
        params = {
            "CartId": cart_id,
            "HMAC": hmac,
            "Items": items
        }
        
        request_params = self._prepare_params("AddToCart", params)
        return self.get("/paapi5/addtocart", params=request_params) 