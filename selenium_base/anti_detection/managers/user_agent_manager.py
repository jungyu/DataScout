"""
用戶代理管理模組

管理瀏覽器用戶代理，以模擬不同的瀏覽器環境
"""

import random
from typing import Dict, List, Optional, Union, Any
from selenium import webdriver
from selenium_base.core.logger import Logger
from selenium_base.anti_detection.base_manager import BaseManager
from selenium_base.anti_detection.base_error import UserAgentError

class UserAgentManager(BaseManager):
    """用戶代理管理類別"""
    
    def __init__(self, driver: webdriver.Remote, config: Dict, logger: Optional[Logger] = None):
        """
        初始化用戶代理管理類別
        
        Args:
            driver: 瀏覽器驅動程式
            config: 配置字典
            logger: 日誌記錄器
        """
        super().__init__(driver, config, logger)
        self.current_user_agent = None
        
    def setup(self) -> None:
        """設置用戶代理環境"""
        if not self.is_enabled():
            return
            
        try:
            if self.config.get("rotate", False):
                self._rotate_user_agent()
            else:
                self._set_user_agent()
                
            self.logger.info("用戶代理設置完成")
        except Exception as e:
            self.logger.error(f"用戶代理設置失敗: {str(e)}")
            raise UserAgentError(f"用戶代理設置失敗: {str(e)}")
            
    def cleanup(self) -> None:
        """清理用戶代理環境"""
        if not self.is_enabled():
            return
            
        try:
            # 清除用戶代理設置
            self.execute_script("""
                Object.defineProperty(navigator, 'userAgent', {
                    get: function() { return undefined; }
                });
            """)
            self.logger.info("用戶代理清理完成")
        except Exception as e:
            self.logger.error(f"用戶代理清理失敗: {str(e)}")
            
    def _set_user_agent(self) -> None:
        """設置用戶代理"""
        try:
            user_agent = self.config.get("user_agent")
            if not user_agent:
                raise UserAgentError("用戶代理未設置")
                
            # 設置用戶代理
            self.execute_script(f"""
                Object.defineProperty(navigator, 'userAgent', {{
                    get: function() {{ return '{user_agent}'; }}
                }});
            """)
            
            self.current_user_agent = user_agent
            self.logger.info(f"設置用戶代理: {user_agent}")
            
        except Exception as e:
            self.logger.error(f"設置用戶代理失敗: {str(e)}")
            raise UserAgentError(f"設置用戶代理失敗: {str(e)}")
            
    def _rotate_user_agent(self) -> None:
        """輪換用戶代理"""
        try:
            user_agent_list = self.config.get("user_agent_list", [])
            if not user_agent_list:
                raise UserAgentError("用戶代理列表為空")
                
            # 隨機選擇用戶代理
            user_agent = random.choice(user_agent_list)
            
            # 設置用戶代理
            self.execute_script(f"""
                Object.defineProperty(navigator, 'userAgent', {{
                    get: function() {{ return '{user_agent}'; }}
                }});
            """)
            
            self.current_user_agent = user_agent
            self.logger.info(f"輪換用戶代理: {user_agent}")
            
        except Exception as e:
            self.logger.error(f"輪換用戶代理失敗: {str(e)}")
            raise UserAgentError(f"輪換用戶代理失敗: {str(e)}")
            
    def get_current_user_agent(self) -> Optional[str]:
        """
        獲取當前用戶代理
        
        Returns:
            當前用戶代理
        """
        return self.current_user_agent
        
    def add_user_agent(self, user_agent: str) -> None:
        """
        添加用戶代理
        
        Args:
            user_agent: 用戶代理字符串
        """
        try:
            user_agent_list = self.config.get("user_agent_list", [])
            user_agent_list.append(user_agent)
            self.config["user_agent_list"] = user_agent_list
            self.logger.info(f"添加用戶代理: {user_agent}")
        except Exception as e:
            self.logger.error(f"添加用戶代理失敗: {str(e)}")
            raise UserAgentError(f"添加用戶代理失敗: {str(e)}")
            
    def remove_user_agent(self, user_agent: str) -> None:
        """
        移除用戶代理
        
        Args:
            user_agent: 用戶代理字符串
        """
        try:
            user_agent_list = self.config.get("user_agent_list", [])
            user_agent_list = [ua for ua in user_agent_list if ua != user_agent]
            self.config["user_agent_list"] = user_agent_list
            self.logger.info(f"移除用戶代理: {user_agent}")
        except Exception as e:
            self.logger.error(f"移除用戶代理失敗: {str(e)}")
            raise UserAgentError(f"移除用戶代理失敗: {str(e)}")
            
    def clear_user_agents(self) -> None:
        """清除所有用戶代理"""
        try:
            self.config["user_agent_list"] = []
            self.logger.info("清除所有用戶代理")
        except Exception as e:
            self.logger.error(f"清除用戶代理失敗: {str(e)}")
            raise UserAgentError(f"清除用戶代理失敗: {str(e)}")
            
    def test_user_agent(self, user_agent: str) -> bool:
        """
        測試用戶代理
        
        Args:
            user_agent: 用戶代理字符串
            
        Returns:
            用戶代理是否有效
        """
        try:
            # 設置用戶代理
            self.execute_script(f"""
                Object.defineProperty(navigator, 'userAgent', {{
                    get: function() {{ return '{user_agent}'; }}
                }});
            """)
            
            # 測試用戶代理
            result = self.execute_script("return navigator.userAgent;")
            return result == user_agent
        except Exception as e:
            self.logger.error(f"測試用戶代理失敗: {str(e)}")
            return False 