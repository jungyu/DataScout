#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Shopee 爬蟲命令列介面

提供蝦皮商品爬蟲的命令列介面，包括：
- 關鍵字搜尋
- 商品詳情爬取
- 結果儲存
"""

import os
import sys
import json
import argparse
import traceback
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler

from src.core.cli import BaseCLI
from src.config.base_config import BaseConfig
from src.core.exceptions import ConfigException, CrawlerException
from .core.shopee_crawler import ShopeeCrawler
from .core.browser_profile import BrowserProfile
from .core.request_controller import RequestController
from .core.browser_fingerprint import BrowserFingerprint
from .utils import save_results, load_config, setup_logger

class ShopeeCrawlerCLI(BaseCLI):
    """Shopee 爬蟲命令列介面"""
    
    def __init__(self):
        """初始化 CLI"""
        super().__init__("shopee_crawler")
        self.crawler = None
    
    def _load_config(self) -> BaseConfig:
        """載入配置"""
        try:
            config_data = load_config("config.json")
            return BaseConfig(config_data)
        except Exception as e:
            self.logger.error(f"載入配置失敗: {str(e)}")
            raise ConfigException("載入配置失敗", details={"error": str(e)})
    
    def _handle_search(self, args: argparse.Namespace):
        """處理搜尋命令"""
        try:
            # 初始化爬蟲
            self.crawler = ShopeeCrawler(self.config, self.logger)
            
            # 執行搜尋
            products = self.crawler.search_products(args.keyword, args.limit)
            
            # 儲存結果
            filepath = save_results(products, "search")
            self.logger.info(f"結果已儲存至: {filepath}")
            
        except Exception as e:
            self.logger.error(f"搜尋失敗: {str(e)}")
            raise CrawlerException("搜尋失敗", details={"error": str(e)})
    
    def _handle_detail(self, args: argparse.Namespace):
        """處理詳情命令"""
        try:
            # 初始化爬蟲
            self.crawler = ShopeeCrawler(self.config, self.logger)
            
            # 獲取詳情
            details = self.crawler.get_product_details(args.url)
            
            # 儲存結果
            filepath = save_results(details, "detail")
            self.logger.info(f"結果已儲存至: {filepath}")
            
        except Exception as e:
            self.logger.error(f"獲取詳情失敗: {str(e)}")
            raise CrawlerException("獲取詳情失敗", details={"error": str(e)})

def main():
    """主函數"""
    cli = ShopeeCrawlerCLI()
    cli.setup()
    cli.run()

if __name__ == "__main__":
    main()