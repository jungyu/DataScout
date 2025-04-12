#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
會話管理模組

提供以下功能：
1. 會話狀態管理
2. 會話驗證
3. 會話信息持久化
4. 會話過期處理
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Optional, Union

from .auth_exceptions import SessionError

class SessionManager:
    """會話管理類"""
    
    def __init__(self, session_file: Optional[str] = None):
        """
        初始化會話管理器
        
        Args:
            session_file: 會話信息文件路徑，默認為 ~/.datascout/session.json
        """
        self.session_file = session_file or os.path.expanduser("~/.datascout/session.json")
        self.sessions: Dict[str, Dict] = {}
        self._load_sessions()
        
    def _load_sessions(self) -> None:
        """從文件加載會話信息"""
        try:
            if os.path.exists(self.session_file):
                with open(self.session_file, "r", encoding="utf-8") as f:
                    self.sessions = json.load(f)
        except Exception as e:
            raise SessionError(f"加載會話信息失敗: {str(e)}")
            
    def _save_sessions(self) -> None:
        """保存會話信息到文件"""
        try:
            os.makedirs(os.path.dirname(self.session_file), exist_ok=True)
            with open(self.session_file, "w", encoding="utf-8") as f:
                json.dump(self.sessions, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise SessionError(f"保存會話信息失敗: {str(e)}")
            
    def create_session(self, domain: str, session_data: Dict) -> None:
        """
        創建新會話
        
        Args:
            domain: 域名
            session_data: 會話數據
        """
        if domain not in self.sessions:
            self.sessions[domain] = {}
            
        self.sessions[domain].update({
            **session_data,
            "created_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat()
        })
        self._save_sessions()
        
    def get_session(self, domain: str) -> Dict:
        """
        獲取會話信息
        
        Args:
            domain: 域名
            
        Returns:
            會話信息字典
        """
        return self.sessions.get(domain, {})
        
    def update_session(self, domain: str, session_data: Dict) -> None:
        """
        更新會話信息
        
        Args:
            domain: 域名
            session_data: 新的會話數據
        """
        if domain not in self.sessions:
            raise SessionError(f"域名 {domain} 的會話不存在")
            
        self.sessions[domain].update({
            **session_data,
            "last_activity": datetime.now().isoformat()
        })
        self._save_sessions()
        
    def delete_session(self, domain: str) -> None:
        """
        刪除會話
        
        Args:
            domain: 域名
        """
        if domain in self.sessions:
            del self.sessions[domain]
            self._save_sessions()
            
    def clear_sessions(self) -> None:
        """清空所有會話"""
        self.sessions.clear()
        self._save_sessions()
        
    def is_session_valid(self, domain: str, max_age: Optional[int] = None) -> bool:
        """
        檢查會話是否有效
        
        Args:
            domain: 域名
            max_age: 最大會話年齡（秒），默認為None（永不過期）
            
        Returns:
            會話是否有效
        """
        if domain not in self.sessions:
            return False
            
        session = self.sessions[domain]
        last_activity = datetime.fromisoformat(session["last_activity"])
        
        if max_age is not None:
            age = (datetime.now() - last_activity).total_seconds()
            if age > max_age:
                return False
                
        return True
        
    def refresh_session(self, domain: str) -> None:
        """
        刷新會話活動時間
        
        Args:
            domain: 域名
        """
        if domain not in self.sessions:
            raise SessionError(f"域名 {domain} 的會話不存在")
            
        self.sessions[domain]["last_activity"] = datetime.now().isoformat()
        self._save_sessions() 