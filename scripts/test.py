#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
測試腳本
用於執行單元測試和集成測試
"""

import os
import sys
import pytest
from pathlib import Path

# 添加項目根目錄到 Python 路徑
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.core.utils.config_utils import ConfigUtils
from src.core.utils.logger import Logger
from src.core.utils.path_utils import PathUtils
from scripts.utils.test_utils import TestUtils

def main():
    """主函數"""
    try:
        # 初始化工具
        config_utils = ConfigUtils()
        logger = Logger()
        path_utils = PathUtils()
        test_utils = TestUtils()
        
        # 設置測試環境
        test_utils.setup_test_env()
        
        # 執行測試
        test_utils.run_tests()
        
        # 生成測試報告
        test_utils.generate_report()
        
        logger.info("測試完成")
        
    except Exception as e:
        logger.error(f"測試失敗: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 