#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置模組

提供爬蟲系統的配置管理功能，包括：
- 配置加載
- 配置驗證
- 配置更新
- 配置備份
"""

from .loader import ConfigLoader
from .validator import ConfigValidator
from .updater import ConfigUpdater
from .backup import ConfigBackup

__version__ = '1.0.0'
__author__ = 'Aaron Yu (https://github.com/jungyu), Claude AI, Cursor AI'
__license__ = 'MIT'

__all__ = [
    'ConfigLoader',
    'ConfigValidator',
    'ConfigUpdater',
    'ConfigBackup'
] 