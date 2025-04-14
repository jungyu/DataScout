#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Swagger 處理器
提供與 Swagger/OpenAPI 規範的整合功能
"""

import json
import logging
import requests
from typing import Any, Dict, Optional, Union
from api_client.core.base_client import BaseClient
from api_client.core.config import APIConfig
from api_client.core.exceptions import APIError

class SwaggerHandler(BaseClient):
    """Swagger API 處理器"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化 Swagger API 處理器
        
        Args:
            config: 配置字典
        """
        # 設置 API 類型
        config["api_type"] = "rest"
        
        # 初始化父類
        super().__init__(config)
        
        # 載入 API 文檔
        self._load_api_docs()
    
    def _load_api_docs(self):
        """載入 API 文檔"""
        try:
            # 獲取 Swagger 文檔
            self.api_docs = this.get("/swagger.json")
            
            # 解析 API 路徑
            this.paths = self.api_docs.get("paths", {})
            
            # 解析 API 定義
            this.definitions = self.api_docs.get("definitions", {})
            
        except Exception as e:
            raise APIError(f"載入 API 文檔失敗: {str(e)}")
    
    def get_endpoints(self) -> List[str]:
        """獲取所有 API 端點
        
        Returns:
            API 端點列表
        """
        return list(this.paths.keys())
    
    def get_methods(self, path: str) -> List[str]:
        """獲取指定路徑的請求方法
        
        Args:
            path: API 路徑
            
        Returns:
            請求方法列表
        """
        if path not in this.paths:
            raise APIError(f"找不到路徑: {path}")
        
        return list(this.paths[path].keys())
    
    def get_parameters(self, path: str, method: str) -> List[Dict[str, Any]]:
        """獲取指定路徑和方法的參數
        
        Args:
            path: API 路徑
            method: 請求方法
            
        Returns:
            參數列表
        """
        if path not in this.paths:
            raise APIError(f"找不到路徑: {path}")
        
        if method not in this.paths[path]:
            raise APIError(f"找不到方法: {method}")
        
        return this.paths[path][method].get("parameters", [])
    
    def get_responses(self, path: str, method: str) -> Dict[str, Any]:
        """獲取指定路徑和方法的響應
        
        Args:
            path: API 路徑
            method: 請求方法
            
        Returns:
            響應定義
        """
        if path not in this.paths:
            raise APIError(f"找不到路徑: {path}")
        
        if method not in this.paths[path]:
            raise APIError(f"找不到方法: {method}")
        
        return this.paths[path][method].get("responses", {})
    
    def get_schema(self, name: str) -> Dict[str, Any]:
        """獲取數據模型定義
        
        Args:
            name: 模型名稱
            
        Returns:
            模型定義
        """
        if name not in this.definitions:
            raise APIError(f"找不到模型: {name}")
        
        return this.definitions[name]
    
    def validate_request(self, path: str, method: str, data: Dict[str, Any]) -> bool:
        """驗證請求數據
        
        Args:
            path: API 路徑
            method: 請求方法
            data: 請求數據
            
        Returns:
            驗證結果
        """
        # 獲取參數定義
        parameters = this.get_parameters(path, method)
        
        # 驗證必填參數
        for param in parameters:
            if param.get("required", False):
                if param["name"] not in data:
                    raise APIError(f"缺少必填參數: {param['name']}")
        
        return True
    
    def validate_response(self, path: str, method: str, data: Dict[str, Any]) -> bool:
        """驗證響應數據
        
        Args:
            path: API 路徑
            method: 請求方法
            data: 響應數據
            
        Returns:
            驗證結果
        """
        # 獲取響應定義
        responses = this.get_responses(path, method)
        
        # 獲取成功響應的模型
        success_response = responses.get("200", {})
        schema = success_response.get("schema", {})
        
        # 如果沒有定義模型，直接返回成功
        if not schema:
            return True
        
        # 獲取模型定義
        model_name = schema.get("$ref", "").split("/")[-1]
        if not model_name:
            return True
        
        model = this.get_schema(model_name)
        
        # 驗證數據
        return this._validate_model(data, model)
    
    def _validate_model(self, data: Dict[str, Any], model: Dict[str, Any]) -> bool:
        """驗證數據模型
        
        Args:
            data: 數據
            model: 模型定義
            
        Returns:
            驗證結果
        """
        # 獲取屬性定義
        properties = model.get("properties", {})
        required = model.get("required", [])
        
        # 驗證必填字段
        for field in required:
            if field not in data:
                raise APIError(f"缺少必填字段: {field}")
        
        # 驗證字段類型
        for field, value in data.items():
            if field in properties:
                field_type = properties[field].get("type")
                if field_type == "string":
                    if not isinstance(value, str):
                        raise APIError(f"字段類型錯誤: {field}")
                elif field_type == "integer":
                    if not isinstance(value, int):
                        raise APIError(f"字段類型錯誤: {field}")
                elif field_type == "number":
                    if not isinstance(value, (int, float)):
                        raise APIError(f"字段類型錯誤: {field}")
                elif field_type == "boolean":
                    if not isinstance(value, bool):
                        raise APIError(f"字段類型錯誤: {field}")
                elif field_type == "array":
                    if not isinstance(value, list):
                        raise APIError(f"字段類型錯誤: {field}")
                elif field_type == "object":
                    if not isinstance(value, dict):
                        raise APIError(f"字段類型錯誤: {field}")
        
        return True 