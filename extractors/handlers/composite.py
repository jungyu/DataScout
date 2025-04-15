#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
複合提取器模組

提供提取器組合和並行處理功能，包括：
1. 提取器組合
2. 並行處理
3. 結果合併
4. 錯誤處理
"""

from typing import Dict, List, Optional, Union, Any, Set, Callable, Type
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio
import time
import json
from datetime import datetime

from ..core.base import BaseExtractor
from ..core.error import handle_extractor_error, ExtractorError
from .table import TableExtractor
from .text import TextExtractor
from .image import ImageExtractor
from .link import LinkExtractor
from .form import FormExtractor

@dataclass
class CompositeExtractorConfig:
    """複合提取器配置"""
    # 提取器配置
    extractors: Dict[str, Type[BaseExtractor]] = None
    extractor_configs: Dict[str, Dict[str, Any]] = None
    
    # 並行處理設置
    max_workers: int = 4
    timeout: float = 30.0
    retry_count: int = 3
    retry_delay: float = 1.0
    
    # 結果處理設置
    merge_results: bool = True
    deduplicate_results: bool = True
    sort_results: bool = False
    result_limit: Optional[int] = None
    
    # 錯誤處理設置
    continue_on_error: bool = True
    error_threshold: int = 5
    error_callback: Optional[Callable[[Exception], None]] = None
    
    def __post_init__(self):
        if self.extractors is None:
            self.extractors = {
                "table": TableExtractor,
                "text": TextExtractor,
                "image": ImageExtractor,
                "link": LinkExtractor,
                "form": FormExtractor
            }
        if self.extractor_configs is None:
            self.extractor_configs = {}

class CompositeExtractor(BaseExtractor):
    """複合提取器類別"""
    
    def __init__(self, driver: Any, config: Optional[CompositeExtractorConfig] = None):
        """初始化複合提取器
        
        Args:
            driver: WebDriver 實例
            config: 提取器配置
        """
        super().__init__(driver)
        self.config = config or CompositeExtractorConfig()
        self._extractors: Dict[str, BaseExtractor] = {}
        self._results: Dict[str, Any] = {}
        self._errors: List[Exception] = []
        
    @handle_extractor_error()
    def initialize_extractors(self) -> None:
        """初始化所有提取器"""
        for name, extractor_class in self.config.extractors.items():
            try:
                config = self.config.extractor_configs.get(name, {})
                self._extractors[name] = extractor_class(self.driver, **config)
            except Exception as e:
                self._errors.append(e)
                if self.config.error_callback:
                    self.config.error_callback(e)
                    
    @handle_extractor_error()
    def get_extractor(self, name: str) -> Optional[BaseExtractor]:
        """獲取指定提取器
        
        Args:
            name: 提取器名稱
            
        Returns:
            Optional[BaseExtractor]: 提取器實例
        """
        if name not in self._extractors:
            self.initialize_extractors()
        return self._extractors.get(name)
        
    @handle_extractor_error()
    def extract_with(self, name: str, *args, **kwargs) -> Any:
        """使用指定提取器進行提取
        
        Args:
            name: 提取器名稱
            *args: 位置參數
            **kwargs: 關鍵字參數
            
        Returns:
            Any: 提取結果
        """
        extractor = self.get_extractor(name)
        if not extractor:
            raise ExtractorError(f"提取器 {name} 不存在")
            
        try:
            result = extractor.extract(*args, **kwargs)
            self._results[name] = result
            return result
        except Exception as e:
            self._errors.append(e)
            if self.config.error_callback:
                self.config.error_callback(e)
            if not self.config.continue_on_error:
                raise
            return None
            
    @handle_extractor_error()
    def extract_parallel(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """並行執行多個提取任務
        
        Args:
            tasks: 提取任務列表，每個任務包含提取器名稱和參數
            
        Returns:
            Dict[str, Any]: 提取結果
        """
        results = {}
        errors = []
        
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            future_to_task = {
                executor.submit(
                    self.extract_with,
                    task["name"],
                    *task.get("args", []),
                    **task.get("kwargs", {})
                ): task
                for task in tasks
            }
            
            for future in as_completed(future_to_task):
                task = future_to_task[future]
                try:
                    result = future.result(timeout=self.config.timeout)
                    results[task["name"]] = result
                except Exception as e:
                    errors.append(e)
                    if self.config.error_callback:
                        self.config.error_callback(e)
                        
        self._results.update(results)
        self._errors.extend(errors)
        
        return results
        
    @handle_extractor_error()
    async def extract_async(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """異步執行多個提取任務
        
        Args:
            tasks: 提取任務列表，每個任務包含提取器名稱和參數
            
        Returns:
            Dict[str, Any]: 提取結果
        """
        results = {}
        errors = []
        
        async def execute_task(task):
            try:
                result = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.extract_with(
                        task["name"],
                        *task.get("args", []),
                        **task.get("kwargs", {})
                    )
                )
                return task["name"], result
            except Exception as e:
                if self.config.error_callback:
                    self.config.error_callback(e)
                return task["name"], None
                
        tasks = [execute_task(task) for task in tasks]
        completed = await asyncio.gather(*tasks)
        
        for name, result in completed:
            if result is not None:
                results[name] = result
                
        self._results.update(results)
        return results
        
    @handle_extractor_error()
    def merge_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """合併多個提取結果
        
        Args:
            results: 提取結果字典
            
        Returns:
            Dict[str, Any]: 合併後的結果
        """
        merged = {
            "timestamp": datetime.now().isoformat(),
            "total_extractors": len(results),
            "successful_extractors": 0,
            "failed_extractors": 0,
            "results": {},
            "errors": []
        }
        
        for name, result in results.items():
            if result is not None:
                merged["results"][name] = result
                merged["successful_extractors"] += 1
            else:
                merged["failed_extractors"] += 1
                
        if self.config.deduplicate_results:
            merged["results"] = self._deduplicate_results(merged["results"])
            
        if self.config.sort_results:
            merged["results"] = self._sort_results(merged["results"])
            
        if self.config.result_limit:
            merged["results"] = self._limit_results(merged["results"])
            
        return merged
        
    @handle_extractor_error()
    def _deduplicate_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """去除重複結果
        
        Args:
            results: 提取結果字典
            
        Returns:
            Dict[str, Any]: 去重後的結果
        """
        deduplicated = {}
        seen = set()
        
        for name, result in results.items():
            if isinstance(result, (list, set)):
                unique_items = []
                for item in result:
                    item_key = json.dumps(item, sort_keys=True)
                    if item_key not in seen:
                        seen.add(item_key)
                        unique_items.append(item)
                deduplicated[name] = unique_items
            else:
                deduplicated[name] = result
                
        return deduplicated
        
    @handle_extractor_error()
    def _sort_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """排序結果
        
        Args:
            results: 提取結果字典
            
        Returns:
            Dict[str, Any]: 排序後的結果
        """
        sorted_results = {}
        
        for name, result in results.items():
            if isinstance(result, (list, set)):
                sorted_results[name] = sorted(result)
            else:
                sorted_results[name] = result
                
        return sorted_results
        
    @handle_extractor_error()
    def _limit_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """限制結果數量
        
        Args:
            results: 提取結果字典
            
        Returns:
            Dict[str, Any]: 限制後的結果
        """
        limited = {}
        
        for name, result in results.items():
            if isinstance(result, (list, set)):
                limited[name] = result[:self.config.result_limit]
            else:
                limited[name] = result
                
        return limited
        
    @handle_extractor_error()
    def extract(self, *args, **kwargs) -> Dict[str, Any]:
        """執行提取操作
        
        Args:
            *args: 位置參數
            **kwargs: 關鍵字參數
            
        Returns:
            Dict[str, Any]: 提取結果
        """
        # 初始化提取器
        self.initialize_extractors()
        
        # 執行提取任務
        tasks = kwargs.get("tasks", [])
        if tasks:
            if kwargs.get("parallel", False):
                results = self.extract_parallel(tasks)
            elif kwargs.get("async", False):
                results = asyncio.run(self.extract_async(tasks))
            else:
                results = {
                    task["name"]: self.extract_with(
                        task["name"],
                        *task.get("args", []),
                        **task.get("kwargs", {})
                    )
                    for task in tasks
                }
        else:
            results = {
                name: extractor.extract(*args, **kwargs)
                for name, extractor in self._extractors.items()
            }
            
        # 合併結果
        if self.config.merge_results:
            results = self.merge_results(results)
            
        return results 