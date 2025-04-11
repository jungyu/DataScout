#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
持久化模組

提供爬蟲系統的數據持久化功能，包括：
- 數據存儲
- 數據備份
- 數據恢復
"""

from .storage import Storage
from .backup import Backup
from .recovery import Recovery

__version__ = '1.0.0'
__author__ = 'Aaron Yu (https://github.com/jungyu), Claude AI, Cursor AI'
__license__ = 'MIT'

__all__ = [
    'Storage',
    'Backup',
    'Recovery'
]
