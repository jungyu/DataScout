"""
配置模組

此模組提供應用程式的基本配置功能
"""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

class Config:
    """配置類"""
    
    def __init__(self):
        """初始化配置"""
        self._load_env()
        
        # Telegram 配置
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        
        # Supabase 配置
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_KEY')
        self.supabase_service_role = os.getenv('SUPABASE_SERVICE_ROLE')
        
        # Web 服務配置
        self.web_service_url = os.getenv('WEB_SERVICE_URL', 'http://localhost:8000')
        
        # 日誌配置
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.log_file = os.getenv('LOG_FILE', 'stock_bot.log')
        
        # 股票配置
        self.default_stock_period = os.getenv('DEFAULT_STOCK_PERIOD', '1d')
    
    def _load_env(self) -> None:
        """載入環境變數"""
        # 嘗試從專案根目錄載入
        env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
        if os.path.exists(env_path):
            load_dotenv(dotenv_path=env_path)
            return
            
        # 嘗試從當前目錄載入
        if os.path.exists('.env'):
            load_dotenv()
            return
    
    def validate(self) -> None:
        """驗證配置"""
        required_vars = {
            'TELEGRAM_BOT_TOKEN': self.telegram_token,
            'SUPABASE_URL': self.supabase_url,
            'SUPABASE_KEY': self.supabase_key,
            'SUPABASE_SERVICE_ROLE': self.supabase_service_role
        }
        
        missing_vars = [var for var, value in required_vars.items() if not value]
        if missing_vars:
            raise ValueError(f"缺少必要的環境變數：{', '.join(missing_vars)}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """獲取配置值
        
        Args:
            key: 配置鍵
            default: 默認值
            
        Returns:
            Any: 配置值
        """
        return getattr(self, key.lower(), default)
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典
        
        Returns:
            Dict[str, Any]: 配置字典
        """
        return {
            'telegram_token': self.telegram_token,
            'supabase_url': self.supabase_url,
            'supabase_key': self.supabase_key,
            'supabase_service_role': self.supabase_service_role,
            'web_service_url': self.web_service_url,
            'log_level': self.log_level,
            'log_file': self.log_file,
            'default_stock_period': self.default_stock_period
        } 