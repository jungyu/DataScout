"""
基礎命令列介面模組

此模組提供了命令列介面的基礎類別，包含以下功能：
- 參數解析
- 配置載入
- 日誌設置
- 錯誤處理
"""

import os
import sys
import json
import argparse
import logging
from typing import Any, Dict, Optional

from .config import BaseConfig
from .exceptions import ConfigError

class BaseCLI:
    """基礎命令列介面類別"""
    
    def __init__(self, name: str):
        """
        初始化命令列介面
        
        Args:
            name: 命令名稱
        """
        self.name = name
        self.logger = None
        self.config = None
        self.args = None
        
    def setup(self):
        """設置命令列環境"""
        try:
            self._setup_logger()
            self._parse_args()
            self._load_config()
            self.logger.info("命令列環境設置完成")
        except Exception as e:
            print(f"錯誤: {str(e)}", file=sys.stderr)
            sys.exit(1)
            
    def _setup_logger(self):
        """設置日誌"""
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        log_file = os.path.join(log_dir, f"{self.name}.log")
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(self.name)
        
    def _parse_args(self):
        """解析命令列參數"""
        parser = argparse.ArgumentParser(description=f"{self.name} 命令列工具")
        
        # 一般參數
        parser.add_argument("--config", help="配置檔案路徑")
        parser.add_argument("--debug", action="store_true", help="開啟除錯模式")
        
        # 子命令
        subparsers = parser.add_subparsers(dest="command", help="可用命令")
        
        # 搜尋命令
        search_parser = subparsers.add_parser("search", help="搜尋商品")
        search_parser.add_argument("keyword", help="搜尋關鍵字")
        search_parser.add_argument("--limit", type=int, default=10, help="結果數量限制")
        
        # 詳情命令
        detail_parser = subparsers.add_parser("detail", help="獲取商品詳情")
        detail_parser.add_argument("item_id", help="商品ID")
        
        self.args = parser.parse_args()
        
    def _load_config(self):
        """載入配置"""
        config_path = self.args.config or "config/config.json"
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)
            self.config = BaseConfig(config_data)
        except Exception as e:
            raise ConfigError(f"載入配置失敗: {str(e)}")
            
    def run(self):
        """執行命令"""
        try:
            if self.args.command == "search":
                self._handle_search(self.args)
            elif self.args.command == "detail":
                self._handle_detail(self.args)
            else:
                self.logger.error(f"未知命令: {self.args.command}")
                sys.exit(1)
        except Exception as e:
            self.logger.error(f"執行命令失敗: {str(e)}")
            sys.exit(1)
            
    def _handle_search(self, args: argparse.Namespace):
        """
        處理搜尋命令
        
        Args:
            args: 命令參數
        """
        raise NotImplementedError("子類別必須實作 _handle_search 方法")
        
    def _handle_detail(self, args: argparse.Namespace):
        """
        處理詳情命令
        
        Args:
            args: 命令參數
        """
        raise NotImplementedError("子類別必須實作 _handle_detail 方法")
        
def main():
    """主函數"""
    cli = BaseCLI("datascout")
    cli.setup()
    cli.run()
    
if __name__ == "__main__":
    main() 