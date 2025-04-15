#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MomoShop 商品資料轉換器
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from ..core.base import BaseTransformer
from ..core.exceptions import TransformationError
from ..core.utils import Utils

class MomoshopTransformer(BaseTransformer):
    """MomoShop 商品資料轉換器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化轉換器
        
        Args:
            config: 轉換配置
        """
        super().__init__(config)
        self.utils = Utils()
        
    async def transform(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        轉換商品資料為 MongoDB 格式
        
        Args:
            data: 原始商品資料
            
        Returns:
            Dict[str, Any]: 轉換後的資料
            
        Raises:
            TransformationError: 轉換錯誤
        """
        try:
            # 基本資料轉換
            transformed = {
                "product_id": str(data.get("product_id", "")),
                "name": data.get("name", ""),
                "brand": data.get("brand", ""),
                "category": self._transform_category(data.get("category", {})),
                "price": self._transform_price(data.get("price", {})),
                "stock": self._transform_stock(data.get("stock", {})),
                "metadata": self._transform_metadata(data.get("metadata", {})),
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            # 驗證必要欄位
            if not transformed["product_id"] or not transformed["name"]:
                raise TransformationError("商品 ID 和名稱為必要欄位")
                
            return transformed
            
        except Exception as e:
            raise TransformationError(f"轉換商品資料失敗: {str(e)}")
            
    def _transform_category(self, category: Dict[str, Any]) -> Dict[str, Any]:
        """
        轉換分類資料
        
        Args:
            category: 原始分類資料
            
        Returns:
            Dict[str, Any]: 轉換後的分類資料
        """
        return {
            "main": category.get("main", ""),
            "sub": category.get("sub", ""),
            "path": category.get("path", []),
            "code": category.get("code", "")
        }
        
    def _transform_price(self, price: Dict[str, Any]) -> Dict[str, Any]:
        """
        轉換價格資料
        
        Args:
            price: 原始價格資料
            
        Returns:
            Dict[str, Any]: 轉換後的價格資料
        """
        return {
            "current": float(price.get("current", 0)),
            "original": float(price.get("original", 0)),
            "discount": float(price.get("discount", 0)),
            "currency": price.get("currency", "TWD"),
            "unit": price.get("unit", "元")
        }
        
    def _transform_stock(self, stock: Dict[str, Any]) -> Dict[str, Any]:
        """
        轉換庫存資料
        
        Args:
            stock: 原始庫存資料
            
        Returns:
            Dict[str, Any]: 轉換後的庫存資料
        """
        return {
            "quantity": int(stock.get("quantity", 0)),
            "status": stock.get("status", "out_of_stock"),
            "warehouse": stock.get("warehouse", ""),
            "last_updated": datetime.now()
        }
        
    def _transform_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        轉換元資料
        
        Args:
            metadata: 原始元資料
            
        Returns:
            Dict[str, Any]: 轉換後的元資料
        """
        return {
            "description": metadata.get("description", ""),
            "specifications": metadata.get("specifications", {}),
            "images": metadata.get("images", []),
            "tags": metadata.get("tags", []),
            "attributes": metadata.get("attributes", {}),
            "ratings": self._transform_ratings(metadata.get("ratings", {})),
            "reviews": self._transform_reviews(metadata.get("reviews", [])),
            "source_url": metadata.get("source_url", ""),
            "crawl_time": datetime.now().isoformat()
        }
        
    def _transform_ratings(self, ratings: Dict[str, Any]) -> Dict[str, Any]:
        """
        轉換評分資料
        
        Args:
            ratings: 原始評分資料
            
        Returns:
            Dict[str, Any]: 轉換後的評分資料
        """
        return {
            "average": float(ratings.get("average", 0)),
            "count": int(ratings.get("count", 0)),
            "distribution": ratings.get("distribution", {}),
            "last_updated": datetime.now()
        }
        
    def _transform_reviews(self, reviews: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        轉換評論資料
        
        Args:
            reviews: 原始評論資料
            
        Returns:
            List[Dict[str, Any]]: 轉換後的評論資料
        """
        transformed = []
        for review in reviews:
            transformed.append({
                "id": str(review.get("id", "")),
                "user": review.get("user", ""),
                "rating": float(review.get("rating", 0)),
                "content": review.get("content", ""),
                "date": review.get("date", datetime.now().isoformat()),
                "images": review.get("images", []),
                "likes": int(review.get("likes", 0)),
                "replies": review.get("replies", [])
            })
        return transformed 