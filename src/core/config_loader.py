#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置管理模組

提供統一的配置管理功能，包括：
1. 基礎配置類
2. 配置載入和驗證
3. 配置合併和覆蓋
4. 配置快取
"""

import os
import json
import logging
import copy
from typing import Dict, Any, Optional, List, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from jsonschema import validate, ValidationError


@dataclass
class BaseConfig:
    """基礎配置類
    
    所有配置類的基類，提供基本的配置功能：
    1. 配置驗證
    2. 配置轉換
    3. 配置比較
    4. 配置統計
    """
    
    # 基本屬性
    id: str
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # 統計信息
    total_uses: int = 0
    success_count: int = 0
    failure_count: int = 0
    last_used: Optional[datetime] = None
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    
    # 元數據
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def validate(self) -> bool:
        """驗證配置"""
        try:
            # 子類實現具體的驗證邏輯
            return True
        except Exception:
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            'id': self.id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'total_uses': self.total_uses,
            'success_count': self.success_count,
            'failure_count': self.failure_count,
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'last_success': self.last_success.isoformat() if self.last_success else None,
            'last_failure': self.last_failure.isoformat() if self.last_failure else None,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseConfig':
        """從字典創建配置"""
        now = datetime.now()
        return cls(
            id=data.get('id', 'default'),
            created_at=data.get('created_at', now),
            updated_at=data.get('updated_at', now),
            total_uses=data.get('total_uses', 0),
            success_count=data.get('success_count', 0),
            failure_count=data.get('failure_count', 0),
            last_used=data.get('last_used'),
            last_success=data.get('last_success'),
            last_failure=data.get('last_failure'),
            metadata=data.get('metadata', {})
        )
    
    def update_stats(self, success: bool):
        """更新統計信息"""
        self.total_uses += 1
        if success:
            self.success_count += 1
            self.last_success = datetime.now()
        else:
            self.failure_count += 1
            self.last_failure = datetime.now()
        self.last_used = datetime.now()
        self.updated_at = datetime.now()
    
    @property
    def success_rate(self) -> float:
        """計算成功率"""
        if self.total_uses == 0:
            return 0.0
        return self.success_count / self.total_uses
    
    def __eq__(self, other: Any) -> bool:
        """比較配置是否相等"""
        if not isinstance(other, BaseConfig):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        """計算哈希值"""
        return hash(self.id)


class ConfigLoader:
    """
    配置載入器類，處理配置文件的載入、驗證和合併
    支援模板繼承和覆蓋機制，提供配置驗證和快取功能
    """
    
    def __init__(self, logger=None, config_dir: str = None):
        """
        初始化配置載入器
        
        Args:
            logger: 日誌記錄器，如果為None則創建新的
            config_dir: 配置目錄路徑，用於解析相對路徑
        """
        self.logger = logger or logging.getLogger(__name__)
        self.schema_cache = {}  # 用於緩存已加載的schema
        self.config_cache = {}  # 用於緩存已加載的配置
        self.config_dir = config_dir or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.logger.info(f"配置載入器初始化完成，配置目錄: {self.config_dir}")
    
    def _resolve_path(self, path: str) -> str:
        """
        解析配置路徑，支援相對路徑和絕對路徑
        
        Args:
            path: 配置路徑
            
        Returns:
            解析後的絕對路徑
        """
        if os.path.isabs(path):
            return path
        return os.path.join(self.config_dir, path)
    
    def load_config(self, config_path: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        載入配置文件
        
        Args:
            config_path: 配置文件路徑
            use_cache: 是否使用快取
            
        Returns:
            配置字典
            
        Raises:
            FileNotFoundError: 配置文件不存在
            json.JSONDecodeError: 配置文件格式不正確
        """
        resolved_path = self._resolve_path(config_path)
        
        # 檢查快取
        if use_cache and resolved_path in self.config_cache:
            self.logger.debug(f"從快取載入配置: {resolved_path}")
            return copy.deepcopy(self.config_cache[resolved_path])
        
        try:
            self.logger.info(f"載入配置文件: {resolved_path}")
            with open(resolved_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 更新快取
            if use_cache:
                self.config_cache[resolved_path] = copy.deepcopy(config)
                
            return config
        except FileNotFoundError:
            self.logger.error(f"配置文件不存在: {resolved_path}")
            raise FileNotFoundError(f"配置文件不存在: {resolved_path}")
        except json.JSONDecodeError as e:
            self.logger.error(f"配置文件格式不正確: {resolved_path}, 錯誤: {str(e)}")
            raise json.JSONDecodeError(f"配置文件格式不正確: {str(e)}", e.doc, e.pos)
    
    def load_template(self, template_path: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        載入爬蟲模板文件，支援模板繼承
        
        Args:
            template_path: 模板文件路徑
            use_cache: 是否使用快取
            
        Returns:
            模板字典
            
        Raises:
            FileNotFoundError: 模板文件不存在
            json.JSONDecodeError: 模板文件格式不正確
        """
        resolved_path = self._resolve_path(template_path)
        
        # 檢查快取
        if use_cache and resolved_path in self.config_cache:
            self.logger.debug(f"從快取載入模板: {resolved_path}")
            return copy.deepcopy(self.config_cache[resolved_path])
        
        try:
            self.logger.info(f"載入模板文件: {resolved_path}")
            with open(resolved_path, 'r', encoding='utf-8') as f:
                template = json.load(f)
            
            # 處理模板繼承
            if "extends" in template:
                base_template_path = template["extends"]
                self.logger.info(f"模板 {resolved_path} 繼承自 {base_template_path}")
                
                # 載入基礎模板
                base_template = self.load_template(base_template_path, use_cache)
                
                # 合併模板
                template = self.merge_configs(base_template, template)
            
            # 更新快取
            if use_cache:
                self.config_cache[resolved_path] = copy.deepcopy(template)
                
            return template
        except FileNotFoundError:
            self.logger.error(f"模板文件不存在: {resolved_path}")
            raise FileNotFoundError(f"模板文件不存在: {resolved_path}")
        except json.JSONDecodeError as e:
            self.logger.error(f"模板文件格式不正確: {resolved_path}, 錯誤: {str(e)}")
            raise json.JSONDecodeError(f"模板文件格式不正確: {str(e)}", e.doc, e.pos)
    
    def validate_config(self, config: Dict[str, Any], schema_path: str) -> Tuple[bool, Optional[str]]:
        """
        驗證配置是否符合schema
        
        Args:
            config: 配置字典
            schema_path: schema文件路徑
            
        Returns:
            (驗證是否通過, 錯誤訊息)
        """
        resolved_path = self._resolve_path(schema_path)
        
        # 從緩存加載或讀取schema
        if resolved_path in self.schema_cache:
            schema = self.schema_cache[resolved_path]
        else:
            try:
                self.logger.info(f"載入schema文件: {resolved_path}")
                with open(resolved_path, 'r', encoding='utf-8') as f:
                    schema = json.load(f)
                self.schema_cache[resolved_path] = schema
            except (FileNotFoundError, json.JSONDecodeError) as e:
                error_msg = f"加載schema失敗: {str(e)}"
                self.logger.error(error_msg)
                return False, error_msg
        
        # 驗證配置
        try:
            validate(instance=config, schema=schema)
            return True, None
        except ValidationError as e:
            error_msg = f"配置驗證失敗: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def merge_configs(self, base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        合併兩個配置，override_config覆蓋base_config的相同鍵
        
        Args:
            base_config: 基礎配置
            override_config: 覆蓋配置
            
        Returns:
            合併後的配置
        """
        merged = copy.deepcopy(base_config)
        
        # 遞迴合併字典
        def _merge_dict(d1, d2):
            for k, v2 in d2.items():
                if k in d1 and isinstance(d1[k], dict) and isinstance(v2, dict):
                    _merge_dict(d1[k], v2)
                else:
                    d1[k] = copy.deepcopy(v2)
        
        _merge_dict(merged, override_config)
        return merged
    
    def load_and_validate(self, config_path: str, schema_path: str = None) -> Dict[str, Any]:
        """
        載入並驗證配置
        
        Args:
            config_path: 配置文件路徑
            schema_path: schema文件路徑，如果不提供則跳過驗證
            
        Returns:
            驗證後的配置
            
        Raises:
            FileNotFoundError: 配置文件不存在
            json.JSONDecodeError: 配置文件格式不正確
            ValidationError: 配置不符合schema
        """
        # 載入配置
        config = self.load_config(config_path)
        
        # 驗證配置
        if schema_path:
            is_valid, error_msg = self.validate_config(config, schema_path)
            if not is_valid:
                self.logger.warning(f"配置 {config_path} 不符合schema: {error_msg}，但仍然繼續")
        
        return config
    
    def load_with_override(self, base_path: str, override_path: str = None, schema_path: str = None) -> Dict[str, Any]:
        """
        載入基礎配置並可選覆蓋
        
        Args:
            base_path: 基礎配置文件路徑
            override_path: 覆蓋配置文件路徑，如果不提供則僅使用基礎配置
            schema_path: schema文件路徑，如果不提供則跳過驗證
            
        Returns:
            最終配置
        """
        # 載入基礎配置
        base_config = self.load_config(base_path)
        
        # 如果提供覆蓋配置，則載入並合併
        if override_path:
            try:
                override_config = self.load_config(override_path)
                base_config = self.merge_configs(base_config, override_config)
                self.logger.info(f"已合併覆蓋配置: {override_path}")
            except Exception as e:
                self.logger.error(f"合併覆蓋配置 {override_path} 失敗: {str(e)}")
        
        # 驗證最終配置
        if schema_path:
            is_valid, error_msg = self.validate_config(base_config, schema_path)
            if not is_valid:
                self.logger.warning(f"最終配置不符合schema: {error_msg}，但仍然繼續")
        
        return base_config
    
    def load_template_with_config(self, template_path: str, config_path: str = None, schema_path: str = None) -> Dict[str, Any]:
        """
        載入模板並可選合併配置
        
        Args:
            template_path: 模板文件路徑
            config_path: 配置文件路徑，如果不提供則僅使用模板
            schema_path: schema文件路徑，如果不提供則跳過驗證
            
        Returns:
            最終配置
        """
        # 載入模板
        template = self.load_template(template_path)
        
        # 如果提供配置，則載入並合併
        if config_path:
            try:
                config = self.load_config(config_path)
                template = self.merge_configs(template, config)
                self.logger.info(f"已合併配置: {config_path}")
            except Exception as e:
                self.logger.error(f"合併配置 {config_path} 失敗: {str(e)}")
        
        # 驗證最終配置
        if schema_path:
            is_valid, error_msg = self.validate_config(template, schema_path)
            if not is_valid:
                self.logger.warning(f"最終配置不符合schema: {error_msg}，但仍然繼續")
        
        return template
    
    def save_config(self, config: Dict[str, Any], config_path: str) -> bool:
        """
        保存配置到文件
        
        Args:
            config: 配置字典
            config_path: 配置文件路徑
            
        Returns:
            是否保存成功
        """
        resolved_path = self._resolve_path(config_path)
        
        try:
            self.logger.info(f"保存配置到文件: {resolved_path}")
            
            # 確保目錄存在
            os.makedirs(os.path.dirname(resolved_path), exist_ok=True)
            
            # 保存配置
            with open(resolved_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            
            # 更新快取
            self.config_cache[resolved_path] = copy.deepcopy(config)
            
            return True
        except Exception as e:
            self.logger.error(f"保存配置失敗: {str(e)}")
            return False
    
    def clear_cache(self) -> None:
        """清除配置快取"""
        self.schema_cache.clear()
        self.config_cache.clear()
        self.logger.info("已清除配置快取")