#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
代理管理器

此模組提供代理服務器管理相關功能，包括：
1. 代理服務器的配置和驗證
2. 代理池的管理和輪換
3. 代理服務器的健康檢查
4. 代理服務器的性能監控
5. 代理服務器的自動切換
"""

import os
import json
import time
import random
import logging
import requests
import threading
from typing import Dict, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from queue import Queue
from concurrent.futures import ThreadPoolExecutor

from src.core.utils import Logger, ErrorHandler
from src.core.utils.error_handler import retry_on_error


@dataclass
class ProxyConfig:
    """代理配置"""
    proxy_type: str = "http"  # http, https, socks4, socks5
    host: str = ""
    port: int = 0
    username: Optional[str] = None
    password: Optional[str] = None
    timeout: int = 10
    max_fails: int = 3
    check_interval: int = 300  # 5分鐘
    min_success_rate: float = 0.8
    max_latency: int = 5000  # 毫秒
    country: Optional[str] = None
    city: Optional[str] = None
    isp: Optional[str] = None
    created_at: int = field(default_factory=lambda: int(time.time()))
    last_check: int = field(default_factory=lambda: int(time.time()))
    success_count: int = 0
    fail_count: int = 0
    total_latency: int = 0
    
    @property
    def success_rate(self) -> float:
        """計算成功率"""
        total = self.success_count + self.fail_count
        return self.success_count / total if total > 0 else 0.0
    
    @property
    def average_latency(self) -> float:
        """計算平均延遲"""
        total = self.success_count + self.fail_count
        return self.total_latency / total if total > 0 else float('inf')
    
    def to_dict(self) -> Dict:
        """轉換為字典"""
        return {
            "proxy_type": self.proxy_type,
            "host": self.host,
            "port": self.port,
            "username": self.username,
            "password": self.password,
            "timeout": self.timeout,
            "max_fails": self.max_fails,
            "check_interval": self.check_interval,
            "min_success_rate": self.min_success_rate,
            "max_latency": self.max_latency,
            "country": self.country,
            "city": self.city,
            "isp": self.isp,
            "created_at": self.created_at,
            "last_check": self.last_check,
            "success_count": self.success_count,
            "fail_count": self.fail_count,
            "total_latency": self.total_latency
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ProxyConfig':
        """從字典創建實例"""
        return cls(
            proxy_type=data.get("proxy_type", "http"),
            host=data.get("host", ""),
            port=data.get("port", 0),
            username=data.get("username"),
            password=data.get("password"),
            timeout=data.get("timeout", 10),
            max_fails=data.get("max_fails", 3),
            check_interval=data.get("check_interval", 300),
            min_success_rate=data.get("min_success_rate", 0.8),
            max_latency=data.get("max_latency", 5000),
            country=data.get("country"),
            city=data.get("city"),
            isp=data.get("isp"),
            created_at=data.get("created_at", int(time.time())),
            last_check=data.get("last_check", int(time.time())),
            success_count=data.get("success_count", 0),
            fail_count=data.get("fail_count", 0),
            total_latency=data.get("total_latency", 0)
        )


class ProxyManager:
    """
    代理管理器，負責代理服務器的配置、驗證和管理
    """
    
    def __init__(
        self,
        config_path: str = "config/proxy.json",
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化代理管理器
        
        Args:
            config_path: 配置文件路徑
            logger: 日誌記錄器
        """
        self.logger = logger or setup_logger(__name__)
        self.config_path = Path(config_path)
        
        # 代理池
        self.proxy_pool: Dict[str, ProxyConfig] = {}
        
        # 加載配置
        self._load_config()
        
        # 健康檢查線程
        self._check_thread = None
        self._stop_event = threading.Event()
        
        # 代理隊列
        self._proxy_queue = Queue()
        
        # 初始化代理隊列
        self._init_proxy_queue()
        
        self.logger.info("代理管理器初始化完成")
    
    def _load_config(self):
        """載入配置文件"""
        try:
            if not self.config_path.exists():
                self.logger.warning(f"配置文件不存在: {self.config_path}")
                return
            
            with open(self.config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)
            
            for proxy_data in config_data.get("proxies", []):
                proxy_config = ProxyConfig.from_dict(proxy_data)
                proxy_key = f"{proxy_config.proxy_type}://{proxy_config.host}:{proxy_config.port}"
                self.proxy_pool[proxy_key] = proxy_config
            
            self.logger.info(f"已載入 {len(self.proxy_pool)} 個代理配置")
            
        except Exception as e:
            self.logger.error(f"載入代理配置失敗: {str(e)}")
    
    def _save_config(self):
        """保存配置文件"""
        try:
            config_data = {
                "proxies": [proxy.to_dict() for proxy in self.proxy_pool.values()]
            }
            
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info("代理配置已保存")
            
        except Exception as e:
            self.logger.error(f"保存代理配置失敗: {str(e)}")
    
    def add_proxy(self, proxy_config: ProxyConfig) -> bool:
        """
        添加代理
        
        Args:
            proxy_config: 代理配置
            
        Returns:
            是否成功添加
        """
        try:
            proxy_key = f"{proxy_config.proxy_type}://{proxy_config.host}:{proxy_config.port}"
            
            # 檢查代理是否可用
            if not self._check_proxy(proxy_config):
                self.logger.warning(f"代理不可用: {proxy_key}")
                return False
            
            # 添加到代理池
            self.proxy_pool[proxy_key] = proxy_config
            
            # 更新代理隊列
            self._update_proxy_queue()
            
            # 保存配置
            self._save_config()
            
            self.logger.info(f"已添加代理: {proxy_key}")
            return True
            
        except Exception as e:
            self.logger.error(f"添加代理失敗: {str(e)}")
            return False
    
    def remove_proxy(self, proxy_key: str) -> bool:
        """
        移除代理
        
        Args:
            proxy_key: 代理鍵值
            
        Returns:
            是否成功移除
        """
        try:
            if proxy_key not in self.proxy_pool:
                self.logger.warning(f"代理不存在: {proxy_key}")
                return False
            
            # 從代理池移除
            del self.proxy_pool[proxy_key]
            
            # 更新代理隊列
            self._update_proxy_queue()
            
            # 保存配置
            self._save_config()
            
            self.logger.info(f"已移除代理: {proxy_key}")
            return True
            
        except Exception as e:
            self.logger.error(f"移除代理失敗: {str(e)}")
            return False
    
    def get_proxy(self) -> Optional[ProxyConfig]:
        """
        獲取一個可用代理
        
        Returns:
            代理配置
        """
        try:
            if self._proxy_queue.empty():
                self.logger.warning("代理隊列為空")
                return None
            
            # 從隊列獲取代理
            proxy_key = self._proxy_queue.get()
            proxy_config = self.proxy_pool.get(proxy_key)
            
            if not proxy_config:
                self.logger.warning(f"代理不存在: {proxy_key}")
                return None
            
            # 檢查代理是否需要更新
            if self._need_check(proxy_config):
                if not self._check_proxy(proxy_config):
                    self.logger.warning(f"代理不可用: {proxy_key}")
                    return None
            
            # 將代理放回隊列
            self._proxy_queue.put(proxy_key)
            
            return proxy_config
            
        except Exception as e:
            self.logger.error(f"獲取代理失敗: {str(e)}")
            return None
    
    def _init_proxy_queue(self):
        """初始化代理隊列"""
        try:
            # 清空隊列
            while not self._proxy_queue.empty():
                self._proxy_queue.get()
            
            # 添加所有代理
            for proxy_key in self.proxy_pool.keys():
                self._proxy_queue.put(proxy_key)
            
            self.logger.info(f"代理隊列初始化完成，共 {self._proxy_queue.qsize()} 個代理")
            
        except Exception as e:
            self.logger.error(f"初始化代理隊列失敗: {str(e)}")
    
    def _update_proxy_queue(self):
        """更新代理隊列"""
        try:
            # 重新初始化隊列
            self._init_proxy_queue()
            
        except Exception as e:
            self.logger.error(f"更新代理隊列失敗: {str(e)}")
    
    def _need_check(self, proxy_config: ProxyConfig) -> bool:
        """
        檢查代理是否需要更新
        
        Args:
            proxy_config: 代理配置
            
        Returns:
            是否需要更新
        """
        # 檢查時間間隔
        if time.time() - proxy_config.last_check > proxy_config.check_interval:
            return True
        
        # 檢查失敗次數
        if proxy_config.fail_count >= proxy_config.max_fails:
            return True
        
        # 檢查成功率
        if proxy_config.success_rate < proxy_config.min_success_rate:
            return True
        
        # 檢查延遲
        if proxy_config.average_latency > proxy_config.max_latency:
            return True
        
        return False
    
    @retry_on_error(max_retries=3)
    def _check_proxy(self, proxy_config: ProxyConfig) -> bool:
        """
        檢查代理是否可用
        
        Args:
            proxy_config: 代理配置
            
        Returns:
            是否可用
        """
        try:
            # 構建代理 URL
            proxy_url = f"{proxy_config.proxy_type}://"
            if proxy_config.username and proxy_config.password:
                proxy_url += f"{proxy_config.username}:{proxy_config.password}@"
            proxy_url += f"{proxy_config.host}:{proxy_config.port}"
            
            # 構建請求
            proxies = {
                "http": proxy_url,
                "https": proxy_url
            }
            
            # 發送請求
            start_time = time.time()
            response = requests.get(
                "http://httpbin.org/ip",
                proxies=proxies,
                timeout=proxy_config.timeout
            )
            end_time = time.time()
            
            # 檢查響應
            if response.status_code != 200:
                self._update_proxy_stats(proxy_config, False)
                return False
            
            # 更新統計信息
            latency = int((end_time - start_time) * 1000)
            self._update_proxy_stats(proxy_config, True, latency)
            
            return True
            
        except Exception as e:
            self.logger.error(f"檢查代理失敗: {str(e)}")
            self._update_proxy_stats(proxy_config, False)
            return False
    
    def _update_proxy_stats(self, proxy_config: ProxyConfig, success: bool, latency: int = 0):
        """
        更新代理統計信息
        
        Args:
            proxy_config: 代理配置
            success: 是否成功
            latency: 延遲時間
        """
        try:
            proxy_config.last_check = int(time.time())
            
            if success:
                proxy_config.success_count += 1
                proxy_config.total_latency += latency
            else:
                proxy_config.fail_count += 1
            
            # 保存配置
            self._save_config()
            
        except Exception as e:
            self.logger.error(f"更新代理統計信息失敗: {str(e)}")
    
    def start_health_check(self):
        """啟動健康檢查"""
        try:
            if self._check_thread and self._check_thread.is_alive():
                self.logger.warning("健康檢查線程已在運行")
                return
            
            self._stop_event.clear()
            self._check_thread = threading.Thread(target=self._health_check_loop)
            self._check_thread.daemon = True
            self._check_thread.start()
            
            self.logger.info("健康檢查線程已啟動")
            
        except Exception as e:
            self.logger.error(f"啟動健康檢查失敗: {str(e)}")
    
    def stop_health_check(self):
        """停止健康檢查"""
        try:
            if not self._check_thread or not self._check_thread.is_alive():
                self.logger.warning("健康檢查線程未運行")
                return
            
            self._stop_event.set()
            self._check_thread.join()
            
            self.logger.info("健康檢查線程已停止")
            
        except Exception as e:
            self.logger.error(f"停止健康檢查失敗: {str(e)}")
    
    def _health_check_loop(self):
        """健康檢查循環"""
        try:
            while not self._stop_event.is_set():
                # 檢查所有代理
                with ThreadPoolExecutor(max_workers=5) as executor:
                    futures = []
                    for proxy_config in self.proxy_pool.values():
                        if self._need_check(proxy_config):
                            futures.append(
                                executor.submit(self._check_proxy, proxy_config)
                            )
                    
                    # 等待所有檢查完成
                    for future in futures:
                        future.result()
                
                # 更新代理隊列
                self._update_proxy_queue()
                
                # 等待下一次檢查
                time.sleep(60)
                
        except Exception as e:
            self.logger.error(f"健康檢查循環異常: {str(e)}")
    
    def get_proxy_stats(self) -> List[Dict]:
        """
        獲取代理統計信息
        
        Returns:
            代理統計信息列表
        """
        try:
            stats = []
            for proxy_key, proxy_config in self.proxy_pool.items():
                stats.append({
                    "proxy": proxy_key,
                    "success_rate": proxy_config.success_rate,
                    "average_latency": proxy_config.average_latency,
                    "total_requests": proxy_config.success_count + proxy_config.fail_count,
                    "last_check": datetime.fromtimestamp(proxy_config.last_check).isoformat()
                })
            return stats
            
        except Exception as e:
            self.logger.error(f"獲取代理統計信息失敗: {str(e)}")
            return []
    
    def cleanup(self):
        """清理資源"""
        try:
            # 停止健康檢查
            self.stop_health_check()
            
            # 保存配置
            self._save_config()
            
            self.logger.info("代理管理器清理完成")
            
        except Exception as e:
            self.logger.error(f"代理管理器清理失敗: {str(e)}")
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.cleanup() 