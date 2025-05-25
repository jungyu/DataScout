#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Supabase 服務模組

此模組提供與 Supabase 資料庫的交互功能。
"""

from .service import SupabaseService
from .config import SupabaseConfig

__all__ = ['SupabaseService', 'SupabaseConfig'] 