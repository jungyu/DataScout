#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置模組

提供各種提取配置的數據類
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union, Callable


@dataclass
class TextCleaningOptions:
    """文本清理選項配置"""
    remove_whitespace: bool = True  # 移除多餘的空白字符
    remove_newlines: bool = True  # 移除換行符
    trim: bool = True  # 移除頭尾空白
    lowercase: bool = False  # 轉為小寫
    uppercase: bool = False  # 轉為大寫
    custom_replacements: Dict[str, str] = field(default_factory=dict)  # 自定義替換


@dataclass
class HtmlCleaningOptions:
    """HTML清理選項配置"""
    clean_html: bool = True  # 是否清理HTML
    remove_scripts: bool = True  # 移除腳本和樣式標籤
    remove_comments: bool = True  # 移除HTML註釋
    remove_ads: bool = True  # 移除廣告元素
    extract_images: bool = False  # 是否提取圖片
    extract_links: bool = False  # 是否提取鏈接
    ad_selectors: List[str] = field(default_factory=list)  # 廣告選擇器列表


@dataclass
class ExtractionConfig:
    """提取配置，定義如何從元素中提取數據"""
    type: str = 'text'  # 數據類型: text, attribute, html, compound等
    xpath: str = ''  # 主XPath選擇器
    fallback_xpath: Optional[str] = None  # 備用XPath選擇器
    multiple: bool = False  # 是否提取多個值
    max_length: Optional[int] = None  # 最大長度限制
    default: Any = None  # 默認值
    attribute: Optional[str] = None  # 屬性名稱(用於attribute類型)
    regex: Optional[str] = None  # 正則表達式模式
    date_format: Optional[str] = None  # 日期格式
    nested_fields: Optional[Dict[str, Any]] = None  # 嵌套字段配置
    transform: Optional[Callable[[Any], Any]] = None  # 自定義轉換函數


@dataclass
class ListExtractionConfig:
    """列表頁提取配置"""
    container_xpath: str = ''  # 列表容器XPath
    item_xpath: str = ''  # 列表項XPath
    fields: Dict[str, ExtractionConfig] = field(default_factory=dict)  # 字段配置
    use_parallel: bool = False  # 是否使用並行提取
    max_items: Optional[int] = None  # 最大提取項數
    wait_time: float = 3.0  # 等待時間
    scroll_after_load: bool = True  # 載入後是否滾動頁面


@dataclass
class DetailExtractionConfig:
    """詳情頁提取配置"""
    container_xpath: str = ''  # 詳情頁容器XPath
    fields: Dict[str, ExtractionConfig] = field(default_factory=dict)  # 字段配置
    url_field: str = 'detail_url'  # URL字段名
    wait_time: float = 3.0  # 等待時間
    scroll_after_load: bool = True  # 載入後是否滾動頁面
    merge_strategy: str = 'nested'  # 數據合併策略: nested, flat, override
    expand_sections: List[Dict[str, Any]] = field(default_factory=list)  # 展開區塊配置
    extraction_settings: Optional[HtmlCleaningOptions] = None  # HTML清理選項


@dataclass
class PaginationConfig:
    """分頁配置"""
    next_button_xpath: str = ''  # 下一頁按鈕XPath
    has_next_page_check: str = ''  # 檢查是否有下一頁的XPath表達式
    page_number_xpath: str = ''  # 頁碼XPath
    url_pattern: str = ''  # URL模式，用於直接跳轉到特定頁面
    max_pages: int = 1  # 最大頁數
    page_load_delay: float = 3.0  # 頁面加載延遲
    between_pages_delay: float = 2.0  # 頁面間延遲


@dataclass
class WebDriverConfig:
    """WebDriver配置"""
    browser_type: str = 'chrome'  # 瀏覽器類型: chrome, firefox, edge等
    headless: bool = False  # 是否啟用無頭模式
    disable_images: bool = False  # 是否禁用圖片加載
    disable_javascript: bool = False  # 是否禁用JavaScript
    disable_cookies: bool = False  # 是否禁用Cookie
    user_agent: Optional[str] = None  # 用戶代理
    proxy: Optional[Union[str, Dict[str, Any]]] = None  # 代理設置
    window_size: Dict[str, int] = field(default_factory=lambda: {"width": 1920, "height": 1080})  # 窗口大小
    page_load_timeout: int = 30  # 頁面加載超時時間
    implicit_wait: int = 10  # 隱式等待時間
    enable_stealth: bool = True  # 是否啟用隱身模式
    driver_path: Optional[str] = None  # WebDriver路徑
    user_data_dir: Optional[str] = None  # 用戶數據目錄


@dataclass
class CaptchaHandlingConfig:
    """驗證碼處理配置"""
    enabled: bool = True  # 是否啟用驗證碼處理
    retry_attempts: int = 3  # 重試次數
    detection_xpath: List[str] = field(default_factory=lambda: [
        "//iframe[contains(@src, 'recaptcha')]",
        "//div[contains(@class, 'g-recaptcha')]",
        "//div[contains(@class, 'captcha')]"
    ])  # 驗證碼檢測XPath
    wait_time: float = 5.0  # 等待時間
    bypass_strategies: List[str] = field(default_factory=lambda: [
        "wait_and_click", "iframe_switch", "action_delay"
    ])  # 繞過策略


@dataclass
class StorageConfig:
    """存儲配置"""
    save_to_file: bool = True  # 是否保存到文件
    output_dir: str = 'output'  # 輸出目錄
    format: str = 'json'  # 輸出格式: json, csv
    filename_prefix: str = 'crawl_result'  # 文件名前綴
    return_items: bool = True  # 是否返回抓取的項目
    screenshots_dir: str = 'screenshots'  # 截圖目錄
    debug_dir: str = 'debug'  # 調試信息目錄


@dataclass
class ExtractionSettings:
    """全局提取設置"""
    webdriver_config: WebDriverConfig = field(default_factory=WebDriverConfig)
    storage_config: StorageConfig = field(default_factory=StorageConfig)
    captcha_config: CaptchaHandlingConfig = field(default_factory=CaptchaHandlingConfig)
    text_cleaning: TextCleaningOptions = field(default_factory=TextCleaningOptions)
    html_cleaning: HtmlCleaningOptions = field(default_factory=HtmlCleaningOptions)
    parallel_workers: int = 4  # 並行工作線程數
    default_timeout: int = 10  # 默認超時時間
    random_delay: bool = True  # 是否使用隨機延遲
    min_delay: float = 1.0  # 最小延遲時間
    max_delay: float = 3.0  # 最大延遲時間