#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
路徑配置模組

此模組提供所有數據目錄的路徑配置，包括：
1. 驗證碼截圖目錄
2. 調試文件目錄
3. 輸出文件目錄
4. 截圖目錄
"""

import os

# 基礎數據目錄
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")

# 驗證碼截圖目錄
CAPTCHA_DIR = os.path.join(DATA_DIR, "captcha")

# 調試文件目錄
DEBUG_DIR = os.path.join(DATA_DIR, "debug")

# 輸出文件目錄
OUTPUT_DIR = os.path.join(DATA_DIR, "output")

# 截圖目錄
SCREENSHOTS_DIR = os.path.join(DATA_DIR, "screenshots")

# 確保所有目錄存在
for directory in [DATA_DIR, CAPTCHA_DIR, DEBUG_DIR, OUTPUT_DIR, SCREENSHOTS_DIR]:
    os.makedirs(directory, exist_ok=True)

# 導出所有路徑
__all__ = [
    'DATA_DIR',
    'CAPTCHA_DIR',
    'DEBUG_DIR',
    'OUTPUT_DIR',
    'SCREENSHOTS_DIR'
] 