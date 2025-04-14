#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
UberEats 處理器
提供與 UberEats 平台的整合功能
"""

import json
import logging
import requests
from typing import Dict, Any, Optional, List, Union
from api_client.core.base_client import BaseClient
from api_client.core.config import APIConfig
from api_client.core.exceptions import APIError, AuthenticationError, RequestError
from api_client.utils.utils import Utils

class UberEatsHandler(BaseClient):
    """UberEats API 處理器"""
    
    def __init__(self, config: Union[Dict[str, Any], APIConfig]):
        """初始化 UberEats API 處理器
        
        Args:
            config: 配置對象，可以是字典或配置類實例
        """
        # 設置 API 類型
        if isinstance(config, dict):
            config["api_type"] = "rest"
            config["base_url"] = config.get("base_url", "https://api.uber.com/v1")
            config["auth_type"] = config.get("auth_type", "oauth2")
        else:
            config.api_type = "rest"
            config.base_url = config.base_url or "https://api.uber.com/v1"
            config.auth_type = config.auth_type or "oauth2"
        
        # 初始化父類
        super().__init__(config)
        
        # 初始化工具類
        self.utils = Utils()
    
    def get_restaurants(self, latitude: float, longitude: float, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """獲取餐廳列表
        
        Args:
            latitude: 緯度
            longitude: 經度
            limit: 返回結果數量限制
            offset: 偏移量
            
        Returns:
            餐廳列表
        """
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "limit": limit,
            "offset": offset
        }
        
        return self.get("/eats/v1/restaurants", params=params)
    
    def get_restaurant_details(self, restaurant_id: str) -> Dict[str, Any]:
        """獲取餐廳詳情
        
        Args:
            restaurant_id: 餐廳 ID
            
        Returns:
            餐廳詳情
        """
        return self.get(f"/eats/v1/restaurants/{restaurant_id}")
    
    def get_menu(self, restaurant_id: str) -> Dict[str, Any]:
        """獲取餐廳菜單
        
        Args:
            restaurant_id: 餐廳 ID
            
        Returns:
            餐廳菜單
        """
        return self.get(f"/eats/v1/restaurants/{restaurant_id}/menu")
    
    def search_restaurants(self, query: str, latitude: float, longitude: float, limit: int = 20) -> Dict[str, Any]:
        """搜索餐廳
        
        Args:
            query: 搜索關鍵詞
            latitude: 緯度
            longitude: 經度
            limit: 返回結果數量限制
            
        Returns:
            搜索結果
        """
        params = {
            "q": query,
            "latitude": latitude,
            "longitude": longitude,
            "limit": limit
        }
        
        return self.get("/eats/v1/search", params=params)
    
    def create_order(self, restaurant_id: str, items: List[Dict[str, Any]], delivery_address: Dict[str, Any]) -> Dict[str, Any]:
        """創建訂單
        
        Args:
            restaurant_id: 餐廳 ID
            items: 訂單項目列表
            delivery_address: 送貨地址
            
        Returns:
            訂單詳情
        """
        data = {
            "restaurant_id": restaurant_id,
            "items": items,
            "delivery_address": delivery_address
        }
        
        return self.post("/eats/v1/orders", json=data)
    
    def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """獲取訂單狀態
        
        Args:
            order_id: 訂單 ID
            
        Returns:
            訂單狀態
        """
        return self.get(f"/eats/v1/orders/{order_id}")
    
    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """取消訂單
        
        Args:
            order_id: 訂單 ID
            
        Returns:
            取消結果
        """
        return self.post(f"/eats/v1/orders/{order_id}/cancel")
    
    def get_user_profile(self) -> Dict[str, Any]:
        """獲取用戶資料
        
        Returns:
            用戶資料
        """
        return self.get("/v1/me")
    
    def get_order_history(self, limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        """獲取訂單歷史
        
        Args:
            limit: 返回結果數量限制
            offset: 偏移量
            
        Returns:
            訂單歷史
        """
        params = {
            "limit": limit,
            "offset": offset
        }
        
        return self.get("/eats/v1/orders/history", params=params)
    
    def get_promotions(self, latitude: float, longitude: float) -> Dict[str, Any]:
        """獲取促銷活動
        
        Args:
            latitude: 緯度
            longitude: 經度
            
        Returns:
            促銷活動列表
        """
        params = {
            "latitude": latitude,
            "longitude": longitude
        }
        
        return self.get("/eats/v1/promotions", params=params) 