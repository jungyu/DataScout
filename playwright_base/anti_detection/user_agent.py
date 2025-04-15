from typing import List, Optional
import random
from fake_useragent import UserAgent
from loguru import logger


class UserAgentManager:
    def __init__(self):
        """初始化 UserAgent 管理器"""
        try:
            self.ua = UserAgent()
            self._user_agents: List[str] = []
            self._load_user_agents()
        except Exception as e:
            logger.error(f"初始化 UserAgent 管理器時發生錯誤: {str(e)}")
            self._user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            ]

    def _load_user_agents(self):
        """加載 User-Agent 列表"""
        try:
            # 預加載一些常用的 User-Agent
            for _ in range(10):
                self._user_agents.append(self.ua.random)
        except Exception as e:
            logger.error(f"加載 User-Agent 列表時發生錯誤: {str(e)}")

    def get_random_user_agent(self) -> str:
        """
        獲取隨機 User-Agent

        Returns:
            str: 隨機 User-Agent 字符串
        """
        try:
            if self._user_agents:
                return random.choice(self._user_agents)
            return self.ua.random
        except Exception as e:
            logger.error(f"獲取隨機 User-Agent 時發生錯誤: {str(e)}")
            return self._user_agents[0] if self._user_agents else "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

    def add_user_agent(self, user_agent: str):
        """
        添加自定義 User-Agent

        Args:
            user_agent: User-Agent 字符串
        """
        if user_agent not in self._user_agents:
            self._user_agents.append(user_agent)

    def remove_user_agent(self, user_agent: str):
        """
        移除指定的 User-Agent

        Args:
            user_agent: 要移除的 User-Agent 字符串
        """
        if user_agent in self._user_agents:
            self._user_agents.remove(user_agent)

    def clear_user_agents(self):
        """清空 User-Agent 列表"""
        self._user_agents.clear()
        self._load_user_agents() 