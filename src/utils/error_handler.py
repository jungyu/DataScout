#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
錯誤處理模組

提供統一的錯誤處理、記錄和報告功能
"""

import os
import time
import traceback
import logging
from typing import Optional, Dict, Any
from selenium import webdriver


class ErrorHandler:
    """
    錯誤處理類
    
    提供捕獲、記錄和處理爬蟲執行過程中的錯誤的功能
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        初始化錯誤處理器
        
        Args:
            logger: 記錄器實例，如果為None則創建新的記錄器
        """
        self.logger = logger or self._setup_default_logger()
        
    def _setup_default_logger(self) -> logging.Logger:
        """設置默認記錄器"""
        logger = logging.getLogger("ErrorHandler")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(level別)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    def handle_exception(
        self, 
        exception: Exception, 
        driver: Optional[webdriver.Remote] = None,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        處理異常
        
        Args:
            exception: 異常實例
            driver: WebDriver 實例，用於獲取截圖和頁面源碼
            context: 提供異常上下文的附加信息
            
        Returns:
            包含錯誤詳情的字典
        """
        # 記錄異常
        error_message = str(exception)
        self.logger.error(f"捕獲異常: {error_message}")
        
        # 獲取堆疊跟踪
        error_traceback = traceback.format_exc()
        self.logger.debug(f"異常堆疊: {error_traceback}")
        
        # 初始化錯誤詳情
        error_details = {
            "error_type": exception.__class__.__name__,
            "error_message": error_message,
            "traceback": error_traceback,
            "timestamp": time.time(),
            "context": context or {}
        }
        
        # 如果有WebDriver，保存頁面截圖和源碼
        if driver:
            try:
                debug_dir = os.path.join(os.getcwd(), "debug")
                os.makedirs(debug_dir, exist_ok=True)
                timestamp = int(time.time())
                
                # 保存截圖
                screenshot_path = os.path.join(debug_dir, f"error_{timestamp}.png")
                driver.save_screenshot(screenshot_path)
                error_details["screenshot"] = screenshot_path
                
                # 保存頁面源碼
                html_path = os.path.join(debug_dir, f"error_{timestamp}.html")
                with open(html_path, "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                error_details["page_source"] = html_path
                
                self.logger.info(f"已保存錯誤頁面: 截圖={screenshot_path}, HTML={html_path}")
            except Exception as e:
                self.logger.error(f"保存錯誤頁面時出錯: {str(e)}")
        
        return error_details
    
    def log_error(self, message: str, error: Optional[Exception] = None) -> None:
        """
        記錄錯誤信息
        
        Args:
            message: 錯誤消息
            error: 錯誤實例
        """
        if error:
            self.logger.error(f"{message}: {str(error)}")
            self.logger.debug(traceback.format_exc())
        else:
            self.logger.error(message)


import time
import logging
import functools
import traceback
from typing import Callable, Any, List, Dict, Union, Optional, Type, Tuple

from .logger import setup_logger


logger = setup_logger(__name__)


class RetryableError(Exception):
    """可重試的錯誤"""
    pass


class FatalError(Exception):
    """致命錯誤，不應重試"""
    pass


class CrawlerError(Exception):
    """爬蟲錯誤基類"""
    def __init__(self, message: str, error_code: str = None, details: Dict = None):
        """
        初始化爬蟲錯誤
        
        Args:
            message: 錯誤消息
            error_code: 錯誤代碼
            details: 錯誤詳情
        """
        self.error_code = error_code
        self.details = details or {}
        super().__init__(message)
    
    def to_dict(self) -> Dict:
        """將錯誤轉換為字典"""
        return {
            "message": str(self),
            "error_code": self.error_code,
            "details": self.details,
            "error_type": self.__class__.__name__
        }


class NetworkError(CrawlerError, RetryableError):
    """網絡相關錯誤"""
    pass


class AuthenticationError(CrawlerError, FatalError):
    """認證相關錯誤"""
    pass


class CaptchaError(CrawlerError, RetryableError):
    """驗證碼相關錯誤"""
    pass


class DataExtractionError(CrawlerError):
    """數據提取相關錯誤"""
    pass


class AntiCrawlingError(CrawlerError, RetryableError):
    """反爬蟲相關錯誤"""
    pass


class ConfigurationError(CrawlerError, FatalError):
    """配置相關錯誤"""
    pass


def retry_on_exception(
    retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Union[Type[Exception], Tuple[Type[Exception], ...]] = Exception,
    on_retry: Callable[[Exception, int, float], None] = None,
    logger_name: str = None
):
    """
    裝飾器：在發生指定異常時重試函數
    
    Args:
        retries: 最大重試次數
        delay: 初始延遲時間（秒）
        backoff: 延遲增長因子
        exceptions: 要捕獲的異常類型
        on_retry: 重試前調用的函數，接收異常、當前重試次數和下次延遲時間
        logger_name: 日誌記錄器名稱，為空時使用當前模塊的記錄器
    
    Returns:
        裝飾後的函數
    """
    func_logger = setup_logger(logger_name) if logger_name else logger
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 初始重試參數
            attempt = 0
            current_delay = delay
            last_exception = None
            
            # 嘗試執行函數
            while attempt <= retries:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    # 已達到最大重試次數
                    if attempt == retries:
                        func_logger.error(
                            f"函數 {func.__name__} 執行失敗，已重試 {retries} 次",
                            exc_info=True
                        )
                        raise
                    
                    # 如果是不可重試的錯誤，直接拋出
                    if isinstance(e, FatalError):
                        func_logger.error(
                            f"函數 {func.__name__} 執行失敗，不可重試錯誤: {str(e)}",
                            exc_info=True
                        )
                        raise
                    
                    # 記錄重試信息
                    attempt += 1
                    last_exception = e
                    func_logger.warning(
                        f"函數 {func.__name__} 執行出錯: {str(e)}，"
                        f"將在 {current_delay} 秒後進行第 {attempt} 次重試"
                    )
                    
                    # 調用重試回調
                    if on_retry:
                        try:
                            on_retry(e, attempt, current_delay)
                        except Exception as callback_error:
                            func_logger.error(
                                f"重試回調執行出錯: {str(callback_error)}",
                                exc_info=True
                            )
                    
                    # 等待後重試
                    time.sleep(current_delay)
                    current_delay *= backoff
                
                except Exception as e:
                    # 非指定異常，直接拋出
                    func_logger.error(
                        f"函數 {func.__name__} 執行出錯: {str(e)}，不在重試異常列表中",
                        exc_info=True
                    )
                    raise
            
            # 理論上不會執行到這裡，為了完整性添加
            raise last_exception
        
        return wrapper
    
    return decorator


def handle_exception(
    func: Callable = None,
    error_map: Dict[Type[Exception], Type[CrawlerError]] = None,
    default_error: Type[CrawlerError] = CrawlerError,
    log_traceback: bool = True,
    error_callback: Callable[[Exception], None] = None,
    logger_name: str = None
):
    """
    裝飾器：處理函數中的異常，將其轉換為自定義錯誤類型
    
    Args:
        func: 被裝飾的函數
        error_map: 異常類型到自定義錯誤類型的映射
        default_error: 默認的自定義錯誤類型
        log_traceback: 是否記錄異常堆疊
        error_callback: 發生錯誤時的回調函數
        logger_name: 日誌記錄器名稱，為空時使用當前模塊的記錄器
    
    Returns:
        裝飾後的函數
    """
    func_logger = setup_logger(logger_name) if logger_name else logger
    error_map = error_map or {}
    
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except CrawlerError:
                # 已經是自定義錯誤，直接拋出
                if log_traceback:
                    func_logger.error(f"函數 {f.__name__} 執行出錯", exc_info=True)
                raise
            except Exception as e:
                # 記錄錯誤
                if log_traceback:
                    error_traceback = traceback.format_exc()
                    func_logger.error(
                        f"函數 {f.__name__} 執行出錯: {str(e)}\n{error_traceback}"
                    )
                else:
                    func_logger.error(f"函數 {f.__name__} 執行出錯: {str(e)}")
                
                # 調用錯誤回調
                if error_callback:
                    try:
                        error_callback(e)
                    except Exception as callback_error:
                        func_logger.error(f"錯誤回調執行出錯: {str(callback_error)}")
                
                # 轉換為自定義錯誤
                for exception_type, error_type in error_map.items():
                    if isinstance(e, exception_type):
                        raise error_type(str(e), details={"original_error": str(e)}) from e
                
                # 使用默認錯誤類型
                raise default_error(str(e), details={"original_error": str(e)}) from e
        
        return wrapper
    
    if func is None:
        return decorator
    return decorator(func)


def safe_execute(
    func: Callable,
    *args,
    default_return: Any = None,
    exceptions: Union[Type[Exception], Tuple[Type[Exception], ...]] = Exception,
    log_error: bool = True,
    error_message: str = None,
    logger_name: str = None,
    **kwargs
) -> Any:
    """
    安全執行函數，捕獲異常並返回默認值
    
    Args:
        func: 要執行的函數
        *args: 函數參數
        default_return: 發生異常時返回的默認值
        exceptions: 要捕獲的異常類型
        log_error: 是否記錄錯誤
        error_message: 自定義錯誤消息
        logger_name: 日誌記錄器名稱，為空時使用當前模塊的記錄器
        **kwargs: 函數關鍵字參數
        
    Returns:
        函數返回值或默認值
    """
    func_logger = setup_logger(logger_name) if logger_name else logger
    
    try:
        return func(*args, **kwargs)
    except exceptions as e:
        if log_error:
            if error_message:
                func_logger.error(f"{error_message}: {str(e)}")
            else:
                func_logger.error(f"執行 {func.__name__} 失敗: {str(e)}")
        return default_return


class ErrorCollector:
    """
    錯誤收集器，用於收集並管理多個操作中的錯誤
    """
    
    def __init__(self, logger_name: str = None, raise_on_error: bool = False):
        """
        初始化錯誤收集器
        
        Args:
            logger_name: 日誌記錄器名稱，為空時使用當前模塊的記錄器
            raise_on_error: 是否在收集到錯誤時立即拋出
        """
        self.logger = setup_logger(logger_name) if logger_name else logger
        self.raise_on_error = raise_on_error
        self.errors = []
    
    def collect(self, func: Callable, *args, error_context: Dict = None, **kwargs) -> Any:
        """
        執行函數並收集錯誤
        
        Args:
            func: 要執行的函數
            *args: 函數參數
            error_context: 錯誤上下文信息
            **kwargs: 函數關鍵字參數
            
        Returns:
            函數返回值或None（如果發生錯誤）
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # 收集錯誤信息
            error_info = {
                "function": func.__name__,
                "error": str(e),
                "error_type": e.__class__.__name__,
                "traceback": traceback.format_exc(),
                "timestamp": time.time(),
                "context": error_context or {}
            }
            
            self.errors.append(error_info)
            self.logger.error(
                f"執行 {func.__name__} 失敗: {str(e)}\n"
                f"上下文: {error_context}\n"
                f"{error_info['traceback']}"
            )
            
            if self.raise_on_error:
                raise
            
            return None
    
    def has_errors(self) -> bool:
        """檢查是否有錯誤"""
        return len(self.errors) > 0
    
    def get_errors(self) -> List[Dict]:
        """獲取所有錯誤"""
        return self.errors
    
    def clear_errors(self):
        """清除所有錯誤"""
        self.errors = []
    
    def raise_if_errors(self, error_class: Type[Exception] = Exception):
        """如果有錯誤，拋出異常"""
        if self.has_errors():
            error_count = len(self.errors)
            first_error = self.errors[0]["error"] if self.errors else "未知錯誤"
            
            raise error_class(f"收集到 {error_count} 個錯誤，第一個錯誤: {first_error}")
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        # 如果有要求拋出錯誤且收集了錯誤
        if self.raise_on_error and self.has_errors():
            self.raise_if_errors()
        return not self.raise_on_error  # 如果不拋出錯誤，屏蔽上下文中的異常


def error_boundary(
    default_return: Any = None,
    log_error: bool = True,
    error_callback: Callable[[Exception], None] = None
):
    """
    錯誤邊界裝飾器，類似於React的ErrorBoundary
    用於隔離錯誤，防止整個程序崩潰
    
    Args:
        default_return: 發生錯誤時返回的默認值
        log_error: 是否記錄錯誤
        error_callback: 發生錯誤時的回調函數
    
    Returns:
        裝飾後的函數
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_error:
                    logger.error(
                        f"錯誤邊界捕獲到異常: {func.__name__} 執行失敗: {str(e)}",
                        exc_info=True
                    )
                
                if error_callback:
                    try:
                        error_callback(e)
                    except Exception as callback_error:
                        logger.error(f"錯誤回調執行出錯: {str(callback_error)}")
                
                return default_return
        
        return wrapper
    
    return decorator