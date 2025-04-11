#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
爬蟲測試套件

此套件包含所有爬蟲相關功能的測試用例，包括：
1. 配置測試
2. 反檢測測試
3. 驗證碼測試
4. 爬蟲功能測試
"""

__version__ = '1.0.0'
__author__ = 'Your Name'
__email__ = 'your.email@example.com'

# 測試配置
TEST_CONFIG = {
    'timeout': 10,  # 默認超時時間（秒）
    'retry_times': 3,  # 默認重試次數
    'wait_time': 5,  # 默認等待時間（秒）
}

# 測試數據目錄
TEST_DATA_DIR = 'test_data'

# 測試日誌配置
TEST_LOG_CONFIG = {
    'level': 'DEBUG',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'filename': 'test.log'
}
