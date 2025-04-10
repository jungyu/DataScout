"""
反指紋檢測配置模組
"""

from typing import Dict, Any, Optional, Tuple
import random

class AntiFingerprintConfig:
    """反指紋檢測配置類"""
    
    def __init__(
        self,
        user_agent: Optional[str] = None,
        proxy: Optional[str] = None,
        headless: bool = False,
        window_size: Tuple[int, int] = (1920, 1080),
        webgl_noise: float = 0.1,
        canvas_noise: float = 0.1,
        mouse_movement: bool = True,
        cookie_protection: bool = True,
        timeout: int = 30
    ):
        """
        初始化配置
        
        Args:
            user_agent: 瀏覽器 User-Agent
            proxy: 代理服務器地址
            headless: 是否使用無頭模式
            window_size: 窗口大小
            webgl_noise: WebGL 指紋噪聲值
            canvas_noise: Canvas 指紋噪聲值
            mouse_movement: 是否啟用滑鼠移動模擬
            cookie_protection: 是否啟用 Cookie 保護
            timeout: 頁面加載超時時間（秒）
        """
        self.user_agent = user_agent or self._generate_random_user_agent()
        self.proxy = proxy
        self.headless = headless
        self.window_size = window_size
        self.webgl_noise = webgl_noise
        self.canvas_noise = canvas_noise
        self.mouse_movement = mouse_movement
        self.cookie_protection = cookie_protection
        self.timeout = timeout
    
    @staticmethod
    def _generate_random_user_agent() -> str:
        """生成隨機的 User-Agent"""
        chrome_versions = ['110.0.5481.177', '111.0.5563.64', '112.0.5615.49']
        platform = random.choice(['Windows NT 10.0', 'Windows NT 6.1'])
        chrome_version = random.choice(chrome_versions)
        return f'Mozilla/5.0 ({platform}; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version} Safari/537.36'
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'AntiFingerprintConfig':
        """
        從字典創建配置
        
        Args:
            config_dict: 配置字典
            
        Returns:
            AntiFingerprintConfig 實例
        """
        return cls(**config_dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        轉換為字典
        
        Returns:
            配置字典
        """
        return {
            'user_agent': self.user_agent,
            'proxy': self.proxy,
            'headless': self.headless,
            'window_size': self.window_size,
            'webgl_noise': self.webgl_noise,
            'canvas_noise': self.canvas_noise,
            'mouse_movement': self.mouse_movement,
            'cookie_protection': self.cookie_protection,
            'timeout': self.timeout
        }
    
    def validate(self) -> bool:
        """
        驗證配置是否有效
        
        Returns:
            是否有效
        """
        try:
            assert isinstance(self.window_size, tuple) and len(self.window_size) == 2
            assert all(isinstance(x, int) and x > 0 for x in self.window_size)
            assert 0 <= self.webgl_noise <= 1
            assert 0 <= self.canvas_noise <= 1
            assert self.timeout > 0
            return True
        except AssertionError:
            return False 