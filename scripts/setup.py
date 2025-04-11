#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
安裝腳本

用於設置開發環境和安裝依賴，包括：
- 環境變量設置
- 目錄結構創建
- 依賴包安裝
- 配置文件初始化
- 日誌系統設置
- 數據庫初始化
- 權限設置
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

# 添加項目根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.core.utils.config_utils import ConfigUtils
from src.core.utils.logger import Logger
from src.core.utils.path_utils import PathUtils
from scripts.utils.setup_utils import SetupUtils

def parse_args():
    """解析命令行參數"""
    parser = argparse.ArgumentParser(description='爬蟲系統安裝腳本')
    parser.add_argument('--env', choices=['dev', 'prod'], default='dev',
                      help='設置環境 (dev/prod)')
    parser.add_argument('--skip-deps', action='store_true',
                      help='跳過依賴安裝')
    parser.add_argument('--force', action='store_true',
                      help='強制重新安裝')
    return parser.parse_args()

def check_python_version():
    """檢查 Python 版本"""
    if sys.version_info < (3, 9):
        print("錯誤: 需要 Python 3.9 或更高版本")
        sys.exit(1)

def check_docker():
    """檢查 Docker 環境"""
    try:
        subprocess.run(['docker', '--version'], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("警告: Docker 未安裝或無法訪問")
    except FileNotFoundError:
        print("警告: Docker 未安裝")

def main():
    """主函數"""
    try:
        # 解析命令行參數
        args = parse_args()
        
        # 檢查環境
        check_python_version()
        check_docker()
        
        # 初始化工具
        config_utils = ConfigUtils()
        logger = Logger()
        path_utils = PathUtils()
        setup_utils = SetupUtils()
        
        # 設置環境變量
        setup_utils.set_env_variables(env=args.env)
        
        # 創建必要的目錄
        setup_utils.create_directories(force=args.force)
        
        # 安裝依賴
        if not args.skip_deps:
            setup_utils.install_dependencies(force=args.force)
        
        # 初始化配置
        setup_utils.init_config(env=args.env)
        
        # 設置日誌
        setup_utils.setup_logging(env=args.env)
        
        # 初始化數據庫
        setup_utils.init_database(env=args.env)
        
        # 設置權限
        setup_utils.set_permissions()
        
        logger.info(f"安裝完成 (環境: {args.env})")
        
    except Exception as e:
        logger.error(f"安裝失敗: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
