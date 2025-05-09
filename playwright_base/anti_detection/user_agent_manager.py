"""
用戶代理（User-Agent）管理模組

提供管理和輪換用戶代理的功能，用於模擬不同瀏覽器和設備。
"""

import random
import json
import os
from typing import List, Dict, Optional, Union
from pathlib import Path

try:
    import user_agents
    from user_agents.parsers import UserAgent
    HAS_USER_AGENTS_LIB = True
except ImportError:
    HAS_USER_AGENTS_LIB = False

from playwright_base.utils.logger import setup_logger

# 設置日誌
logger = setup_logger(name=__name__)

class UserAgentManager:
    """
    用戶代理管理類。
    提供用戶代理的生成、輪換和分析功能。
    """
    
    def __init__(self, user_agents_file: str = None, browser_type: str = "chrome"):
        """
        初始化 UserAgentManager 實例。
        
        參數:
            user_agents_file (str): 包含用戶代理列表的 JSON 檔案路徑。
            browser_type (str): 優先使用的瀏覽器類型，例如 'chrome', 'firefox', 'safari'。
        """
        self.browser_type = browser_type.lower()
        self.user_agents_list = []
        self.current_index = 0
        
        # 預設常用用戶代理
        self._default_user_agents = {
            "chrome": [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            ],
            "firefox": [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:123.0) Gecko/20100101 Firefox/123.0",
                "Mozilla/5.0 (X11; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            ],
            "safari": [
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
                "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
                "Mozilla/5.0 (iPad; CPU OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Mobile/15E148 Safari/604.1",
            ],
            "edge": [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0",
            ]
        }
        
        # 如果提供了用戶代理檔案，則從檔案載入
        if user_agents_file and os.path.exists(user_agents_file):
            self._load_user_agents_from_file(user_agents_file)
        else:
            # 否則使用預設的用戶代理列表
            self._use_default_user_agents()
            
        logger.info(f"用戶代理管理器已初始化，共載入 {len(self.user_agents_list)} 個用戶代理")
    
    def _load_user_agents_from_file(self, file_path: str) -> None:
        """
        從檔案載入用戶代理列表。
        
        參數:
            file_path (str): JSON 檔案路徑。
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            if isinstance(data, list):
                # 直接列表格式
                self.user_agents_list = data
            elif isinstance(data, dict) and 'user_agents' in data:
                # 包含 'user_agents' 鍵的字典
                self.user_agents_list = data['user_agents']
            else:
                logger.warning(f"從 {file_path} 載入的用戶代理格式無效，使用預設用戶代理")
                self._use_default_user_agents()
                return
                
            logger.info(f"已從 {file_path} 載入 {len(self.user_agents_list)} 個用戶代理")
            
        except Exception as e:
            logger.error(f"載入用戶代理檔案時發生錯誤: {str(e)}")
            self._use_default_user_agents()
    
    def _use_default_user_agents(self) -> None:
        """使用預設用戶代理列表"""
        # 優先使用指定瀏覽器類型的用戶代理，若不存在則使用所有類型
        if self.browser_type in self._default_user_agents:
            self.user_agents_list = self._default_user_agents[self.browser_type]
            logger.info(f"使用 {self.browser_type} 的預設用戶代理 ({len(self.user_agents_list)} 個)")
        else:
            # 合併所有預設用戶代理
            self.user_agents_list = []
            for browser, agents in self._default_user_agents.items():
                self.user_agents_list.extend(agents)
            logger.info(f"使用所有瀏覽器的預設用戶代理 ({len(self.user_agents_list)} 個)")
    
    def get_random_user_agent(self) -> str:
        """
        隨機獲取一個用戶代理。
        
        返回:
            str: 隨機的用戶代理字符串。
        """
        if not self.user_agents_list:
            logger.warning("用戶代理列表為空，返回預設用戶代理")
            return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        
        ua = random.choice(self.user_agents_list)
        logger.debug(f"隨機選擇用戶代理: {ua}")
        return ua
    
    def next_user_agent(self) -> str:
        """
        順序獲取下一個用戶代理。
        
        返回:
            str: 下一個用戶代理字符串。
        """
        if not self.user_agents_list:
            logger.warning("用戶代理列表為空，返回預設用戶代理")
            return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        
        ua = self.user_agents_list[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.user_agents_list)
        logger.debug(f"選擇下一個用戶代理: {ua}")
        return ua
    
    def get_user_agent_by_pattern(self, pattern: str) -> Optional[str]:
        """
        根據模式字符串獲取匹配的用戶代理。
        
        參數:
            pattern (str): 用於匹配的字符串，例如 'chrome', 'windows', 'mobile'。
            
        返回:
            Optional[str]: 匹配的用戶代理字符串，若無匹配則返回 None。
        """
        pattern = pattern.lower()
        matching_agents = [ua for ua in self.user_agents_list if pattern in ua.lower()]
        
        if not matching_agents:
            logger.warning(f"沒有找到符合 '{pattern}' 的用戶代理")
            return None
            
        ua = random.choice(matching_agents)
        logger.debug(f"根據模式 '{pattern}' 選擇用戶代理: {ua}")
        return ua
    
    def analyze_user_agent(self, user_agent: str) -> Dict[str, str]:
        """
        分析用戶代理字符串，獲取瀏覽器、操作系統等資訊。
        
        參數:
            user_agent (str): 要分析的用戶代理字符串。
            
        返回:
            Dict[str, str]: 包含分析結果的字典。
        """
        # 檢查是否安裝了 user_agents 庫
        if not HAS_USER_AGENTS_LIB:
            logger.warning("未安裝 user_agents 庫，無法詳細分析用戶代理")
            return self._simple_analyze_user_agent(user_agent)
        
        try:
            ua = user_agents.parse(user_agent)
            return {
                'browser_family': ua.browser.family,
                'browser_version': ua.browser.version_string,
                'os_family': ua.os.family,
                'os_version': ua.os.version_string,
                'device_family': ua.device.family,
                'is_mobile': str(ua.is_mobile),
                'is_tablet': str(ua.is_tablet),
                'is_pc': str(ua.is_pc),
                'is_bot': str(ua.is_bot)
            }
        except Exception as e:
            logger.error(f"分析用戶代理時發生錯誤: {str(e)}")
            return self._simple_analyze_user_agent(user_agent)
    
    def _simple_analyze_user_agent(self, user_agent: str) -> Dict[str, str]:
        """
        簡單分析用戶代理字符串（不依賴外部庫）。
        
        參數:
            user_agent (str): 要分析的用戶代理字符串。
            
        返回:
            Dict[str, str]: 包含簡單分析結果的字典。
        """
        ua_lower = user_agent.lower()
        result = {
            'user_agent': user_agent,
            'browser_family': 'Unknown',
            'os_family': 'Unknown',
            'is_mobile': 'False'
        }
        
        # 瀏覽器檢測
        if 'chrome' in ua_lower and 'edg' in ua_lower:
            result['browser_family'] = 'Edge'
        elif 'chrome' in ua_lower:
            result['browser_family'] = 'Chrome'
        elif 'firefox' in ua_lower:
            result['browser_family'] = 'Firefox'
        elif 'safari' in ua_lower:
            result['browser_family'] = 'Safari'
        elif 'msie' in ua_lower or 'trident' in ua_lower:
            result['browser_family'] = 'Internet Explorer'
        elif 'opera' in ua_lower:
            result['browser_family'] = 'Opera'
        
        # 操作系統檢測
        if 'windows' in ua_lower:
            result['os_family'] = 'Windows'
        elif 'macintosh' in ua_lower or 'mac os x' in ua_lower:
            result['os_family'] = 'Mac OS X'
        elif 'linux' in ua_lower:
            result['os_family'] = 'Linux'
        elif 'android' in ua_lower:
            result['os_family'] = 'Android'
            result['is_mobile'] = 'True'
        elif 'iphone' in ua_lower or 'ipad' in ua_lower or 'ipod' in ua_lower:
            result['os_family'] = 'iOS'
            result['is_mobile'] = 'True'
        
        # 移動設備檢測
        if 'mobile' in ua_lower or 'android' in ua_lower or 'iphone' in ua_lower:
            result['is_mobile'] = 'True'
        
        return result
        
    def save_user_agents_to_file(self, file_path: str) -> bool:
        """
        將目前的用戶代理列表保存到檔案。
        
        參數:
            file_path (str): 要保存的檔案路徑。
            
        返回:
            bool: 保存是否成功。
        """
        try:
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
                
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump({'user_agents': self.user_agents_list}, f, indent=2)
                
            logger.info(f"已將 {len(self.user_agents_list)} 個用戶代理保存到 {file_path}")
            return True
        except Exception as e:
            logger.error(f"保存用戶代理到檔案時發生錯誤: {str(e)}")
            return False
    
    def add_user_agent(self, user_agent: str) -> None:
        """
        添加一個用戶代理到列表中。
        
        參數:
            user_agent (str): 要添加的用戶代理字符串。
        """
        if user_agent and user_agent not in self.user_agents_list:
            self.user_agents_list.append(user_agent)
            logger.debug(f"已添加新的用戶代理: {user_agent}")
            
    def get_matching_user_agents(self, browser: str = None, os: str = None, mobile: bool = None) -> List[str]:
        """
        獲取符合指定條件的用戶代理列表。
        
        參數:
            browser (str): 瀏覽器類型，例如 'chrome', 'firefox'。
            os (str): 操作系統類型，例如 'windows', 'macos', 'android'。
            mobile (bool): 是否為移動設備。
            
        返回:
            List[str]: 符合條件的用戶代理列表。
        """
        result = []
        
        for ua in self.user_agents_list:
            ua_lower = ua.lower()
            match = True
            
            # 檢查瀏覽器
            if browser:
                browser_lower = browser.lower()
                if browser_lower == 'chrome' and 'chrome' not in ua_lower:
                    match = False
                elif browser_lower == 'firefox' and 'firefox' not in ua_lower:
                    match = False
                elif browser_lower == 'safari' and 'safari' not in ua_lower:
                    match = False
                elif browser_lower == 'edge' and 'edg' not in ua_lower:
                    match = False
                    
            # 檢查操作系統
            if os and match:
                os_lower = os.lower()
                if os_lower == 'windows' and 'windows' not in ua_lower:
                    match = False
                elif os_lower in ('macos', 'mac') and ('macintosh' not in ua_lower and 'mac os x' not in ua_lower):
                    match = False
                elif os_lower == 'linux' and 'linux' not in ua_lower:
                    match = False
                elif os_lower == 'android' and 'android' not in ua_lower:
                    match = False
                elif os_lower == 'ios' and ('iphone' not in ua_lower and 'ipad' not in ua_lower and 'ipod' not in ua_lower):
                    match = False
                    
            # 檢查是否為移動設備
            if mobile is not None and match:
                is_mobile = 'mobile' in ua_lower or 'android' in ua_lower or 'iphone' in ua_lower or 'ipad' in ua_lower
                if mobile != is_mobile:
                    match = False
                    
            if match:
                result.append(ua)
                
        logger.debug(f"找到 {len(result)} 個符合條件的用戶代理")
        return result