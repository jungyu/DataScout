#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置模組

提供各種提取配置的數據類，用於定義爬蟲的行為和設置。

主要配置類：
- TextCleaningOptions: 文本清理選項
- HtmlCleaningOptions: HTML清理選項
- ExtractionConfig: 數據提取配置
- ListExtractionConfig: 列表頁提取配置
- DetailExtractionConfig: 詳情頁提取配置
- PaginationConfig: 分頁配置
- WebDriverConfig: WebDriver配置
- CaptchaHandlingConfig: 驗證碼處理配置
- StorageConfig: 存儲配置
- ExtractionSettings: 全局提取設置

使用示例：
    from src.extractors.config import ExtractionSettings, WebDriverConfig
    
    # 創建WebDriver配置
    webdriver_config = WebDriverConfig(
        browser_type='chrome',
        headless=True,
        enable_stealth=True
    )
    
    # 創建全局提取設置
    settings = ExtractionSettings(
        webdriver_config=webdriver_config,
        parallel_workers=4,
        random_delay=True
    )
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union, Callable


@dataclass
class TextCleaningOptions:
    """文本清理選項配置
    
    用於定義如何清理和處理提取的文本數據。
    
    Attributes:
        remove_whitespace: 是否移除多餘的空白字符
        remove_newlines: 是否移除換行符
        trim: 是否移除頭尾空白
        lowercase: 是否轉為小寫
        uppercase: 是否轉為大寫
        custom_replacements: 自定義替換規則
    """
    remove_whitespace: bool = True
    remove_newlines: bool = True
    trim: bool = True
    lowercase: bool = False
    uppercase: bool = False
    custom_replacements: Dict[str, str] = field(default_factory=dict)


@dataclass
class HtmlCleaningOptions:
    """HTML清理選項配置
    
    用於定義如何清理和處理HTML內容。
    
    Attributes:
        clean_html: 是否清理HTML
        remove_scripts: 是否移除腳本和樣式標籤
        remove_comments: 是否移除HTML註釋
        remove_ads: 是否移除廣告元素
        extract_images: 是否提取圖片
        extract_links: 是否提取鏈接
        ad_selectors: 廣告元素選擇器列表
    """
    clean_html: bool = True
    remove_scripts: bool = True
    remove_comments: bool = True
    remove_ads: bool = True
    extract_images: bool = False
    extract_links: bool = False
    ad_selectors: List[str] = field(default_factory=list)


@dataclass
class ExtractionConfig:
    """提取配置
    
    定義如何從元素中提取數據。
    
    Attributes:
        type: 數據類型 (text, attribute, html, compound等)
        xpath: 主XPath選擇器
        fallback_xpath: 備用XPath選擇器
        multiple: 是否提取多個值
        max_length: 最大長度限制
        default: 默認值
        attribute: 屬性名稱(用於attribute類型)
        regex: 正則表達式模式
        date_format: 日期格式
        nested_fields: 嵌套字段配置
        transform: 自定義轉換函數
    """
    type: str = 'text'
    xpath: str = ''
    fallback_xpath: Optional[str] = None
    multiple: bool = False
    max_length: Optional[int] = None
    default: Any = None
    attribute: Optional[str] = None
    regex: Optional[str] = None
    date_format: Optional[str] = None
    nested_fields: Optional[Dict[str, Any]] = None
    transform: Optional[Callable[[Any], Any]] = None


@dataclass
class ListExtractionConfig:
    """列表頁提取配置
    
    定義如何從列表頁面提取數據。
    
    Attributes:
        container_xpath: 列表容器XPath
        item_xpath: 列表項XPath
        fields: 字段配置
        use_parallel: 是否使用並行提取
        max_items: 最大提取項數
        wait_time: 等待時間
        scroll_after_load: 載入後是否滾動頁面
    """
    container_xpath: str = ''
    item_xpath: str = ''
    fields: Dict[str, ExtractionConfig] = field(default_factory=dict)
    use_parallel: bool = False
    max_items: Optional[int] = None
    wait_time: float = 3.0
    scroll_after_load: bool = True


@dataclass
class DetailExtractionConfig:
    """詳情頁提取配置
    
    定義如何從詳情頁面提取數據。
    
    Attributes:
        container_xpath: 詳情頁容器XPath
        fields: 字段配置
        url_field: URL字段名
        wait_time: 等待時間
        scroll_after_load: 載入後是否滾動頁面
        merge_strategy: 數據合併策略
        expand_sections: 展開區塊配置
        extraction_settings: HTML清理選項
    """
    container_xpath: str = ''
    fields: Dict[str, ExtractionConfig] = field(default_factory=dict)
    url_field: str = 'detail_url'
    wait_time: float = 3.0
    scroll_after_load: bool = True
    merge_strategy: str = 'nested'
    expand_sections: List[Dict[str, Any]] = field(default_factory=list)
    extraction_settings: Optional[HtmlCleaningOptions] = None


@dataclass
class PaginationConfig:
    """分頁配置
    
    定義如何處理分頁。
    
    Attributes:
        next_button_xpath: 下一頁按鈕XPath
        has_next_page_check: 檢查是否有下一頁的XPath表達式
        page_number_xpath: 頁碼XPath
        url_pattern: URL模式
        max_pages: 最大頁數
        page_load_delay: 頁面加載延遲
        between_pages_delay: 頁面間延遲
    """
    next_button_xpath: str = ''
    has_next_page_check: str = ''
    page_number_xpath: str = ''
    url_pattern: str = ''
    max_pages: int = 1
    page_load_delay: float = 3.0
    between_pages_delay: float = 2.0


@dataclass
class WebDriverConfig:
    """WebDriver配置
    
    定義WebDriver的行為和設置。
    
    Attributes:
        browser_type: 瀏覽器類型
        headless: 是否啟用無頭模式
        disable_images: 是否禁用圖片加載
        disable_javascript: 是否禁用JavaScript
        disable_cookies: 是否禁用Cookie
        user_agent: 用戶代理
        proxy: 代理設置
        window_size: 窗口大小
        page_load_timeout: 頁面加載超時時間
        implicit_wait: 隱式等待時間
        enable_stealth: 是否啟用隱身模式
        driver_path: WebDriver路徑
        user_data_dir: 用戶數據目錄
    """
    browser_type: str = 'chrome'
    headless: bool = False
    disable_images: bool = False
    disable_javascript: bool = False
    disable_cookies: bool = False
    user_agent: Optional[str] = None
    proxy: Optional[Union[str, Dict[str, Any]]] = None
    window_size: Dict[str, int] = field(default_factory=lambda: {"width": 1920, "height": 1080})
    page_load_timeout: int = 30
    implicit_wait: int = 10
    enable_stealth: bool = True
    driver_path: Optional[str] = None
    user_data_dir: Optional[str] = None


@dataclass
class CaptchaHandlingConfig:
    """驗證碼處理配置
    
    定義如何處理驗證碼。
    
    Attributes:
        enabled: 是否啟用驗證碼處理
        retry_attempts: 重試次數
        detection_xpath: 驗證碼檢測XPath
        wait_time: 等待時間
        bypass_strategies: 繞過策略
    """
    enabled: bool = True
    retry_attempts: int = 3
    detection_xpath: List[str] = field(default_factory=lambda: [
        "//iframe[contains(@src, 'recaptcha')]",
        "//div[contains(@class, 'g-recaptcha')]",
        "//div[contains(@class, 'captcha')]"
    ])
    wait_time: float = 5.0
    bypass_strategies: List[str] = field(default_factory=lambda: [
        "wait_and_click", "iframe_switch", "action_delay"
    ])


@dataclass
class StorageConfig:
    """存儲配置
    
    定義如何存儲提取的數據。
    
    Attributes:
        save_to_file: 是否保存到文件
        output_dir: 輸出目錄
        format: 輸出格式
        filename_prefix: 文件名前綴
        return_items: 是否返回抓取的項目
        screenshots_dir: 截圖目錄
        debug_dir: 調試信息目錄
    """
    save_to_file: bool = True
    output_dir: str = 'output'
    format: str = 'json'
    filename_prefix: str = 'crawl_result'
    return_items: bool = True
    screenshots_dir: str = 'screenshots'
    debug_dir: str = 'debug'


@dataclass
class ExtractionSettings:
    """全局提取設置
    
    包含所有提取相關的配置。
    
    Attributes:
        webdriver_config: WebDriver配置
        storage_config: 存儲配置
        captcha_config: 驗證碼處理配置
        text_cleaning: 文本清理選項
        html_cleaning: HTML清理選項
        parallel_workers: 並行工作線程數
        default_timeout: 默認超時時間
        random_delay: 是否使用隨機延遲
        min_delay: 最小延遲時間
        max_delay: 最大延遲時間
    """
    webdriver_config: WebDriverConfig = field(default_factory=WebDriverConfig)
    storage_config: StorageConfig = field(default_factory=StorageConfig)
    captcha_config: CaptchaHandlingConfig = field(default_factory=CaptchaHandlingConfig)
    text_cleaning: TextCleaningOptions = field(default_factory=TextCleaningOptions)
    html_cleaning: HtmlCleaningOptions = field(default_factory=HtmlCleaningOptions)
    parallel_workers: int = 4
    default_timeout: int = 10
    random_delay: bool = True
    min_delay: float = 1.0
    max_delay: float = 3.0