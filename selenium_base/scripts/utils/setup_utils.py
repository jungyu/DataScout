#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
安裝工具類
提供安裝過程中的各種工具方法
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Any

class SetupUtils:
    """安裝工具類"""
    
    def __init__(self):
        """初始化"""
        self.project_root = Path(__file__).parent.parent.parent
        self.requirements_file = self.project_root / "requirements.txt"
        self.config_dir = self.project_root / "config"
        self.log_dir = self.project_root / "logs"
    
    def set_env_variables(self) -> None:
        """設置環境變量"""
        os.environ["PYTHONPATH"] = str(self.project_root)
        os.environ["CONFIG_DIR"] = str(self.config_dir)
        os.environ["LOG_DIR"] = str(self.log_dir)
    
    def create_directories(self) -> None:
        """創建必要的目錄"""
        directories = [
            self.config_dir,
            self.log_dir,
            self.project_root / "data",
            self.project_root / "backups",
            self.project_root / "temp"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def install_dependencies(self) -> None:
        """安裝依賴"""
        if not self.requirements_file.exists():
            raise FileNotFoundError("找不到 requirements.txt 文件")
        
        subprocess.check_call([
            sys.executable, "-m", "pip", "install",
            "-r", str(self.requirements_file)
        ])
    
    def init_config(self) -> None:
        """初始化配置"""
        config_files = [
            "storage.json",
            "logging.json",
            "security.json"
        ]
        
        for config_file in config_files:
            config_path = self.config_dir / config_file
            if not config_path.exists():
                self._create_default_config(config_path)
    
    def setup_logging(self) -> None:
        """設置日誌"""
        log_config = self.config_dir / "logging.json"
        if not log_config.exists():
            self._create_default_log_config(log_config)
    
    def _create_default_config(self, config_path: Path) -> None:
        """
        創建默認配置文件
        
        Args:
            config_path: 配置文件路徑
        """
        default_configs = {
            "storage.json": {
                "mode": "local",
                "local": {
                    "path": "data",
                    "backup_path": "backups"
                },
                "mongodb": {
                    "uri": "",
                    "database": "",
                    "collection": ""
                },
                "notion": {
                    "token": "",
                    "database_id": "",
                    "parent_page_id": ""
                }
            },
            "logging.json": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file": "logs/app.log"
            },
            "security.json": {
                "encryption_key": "",
                "jwt_secret": "",
                "allowed_origins": []
            }
        }
        
        config_name = config_path.name
        if config_name in default_configs:
            import json
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(default_configs[config_name], f, indent=4)
    
    def _create_default_log_config(self, config_path: Path) -> None:
        """
        創建默認日誌配置
        
        Args:
            config_path: 配置文件路徑
        """
        default_config = {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": "INFO",
                    "formatter": "standard",
                    "stream": "ext://sys.stdout"
                },
                "file": {
                    "class": "logging.handlers.RotatingFileHandler",
                    "level": "INFO",
                    "formatter": "standard",
                    "filename": "logs/app.log",
                    "maxBytes": 10485760,
                    "backupCount": 5
                }
            },
            "loggers": {
                "": {
                    "handlers": ["console", "file"],
                    "level": "INFO",
                    "propagate": True
                }
            }
        }
        
        import json
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=4) 