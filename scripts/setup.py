#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
安裝腳本
用於設置開發環境和安裝依賴
"""

import os
import sys
import subprocess
from pathlib import Path

# 添加項目根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.core.utils.config_utils import ConfigUtils
from src.core.utils.logger import Logger
from src.core.utils.path_utils import PathUtils
from scripts.utils.setup_utils import SetupUtils

def main():
    """主函數"""
    try:
        # 初始化工具
        config_utils = ConfigUtils()
        logger = Logger()
        path_utils = PathUtils()
        setup_utils = SetupUtils()
        
        # 設置環境變量
        setup_utils.set_env_variables()
        
        # 創建必要的目錄
        setup_utils.create_directories()
        
        # 安裝依賴
        setup_utils.install_dependencies()
        
        # 初始化配置
        setup_utils.init_config()
        
        # 設置日誌
        setup_utils.setup_logging()
        
        logger.info("安裝完成")
        
    except Exception as e:
        logger.error(f"安裝失敗: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
