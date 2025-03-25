"""
Core module for the crawler system.
Contains the main crawler engine and template processing functionality.
"""

from .template_crawler import TemplateCrawler
from .webdriver_manager import WebDriverManager
from .crawler_engine import CrawlerEngine

__all__ = ['TemplateCrawler', 'WebDriverManager', 'CrawlerEngine']
