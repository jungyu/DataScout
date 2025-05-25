"""
Telegram Bot 自定義異常
"""

class BotError(Exception):
    """Bot 基礎異常類"""
    pass

class BotInitializationError(BotError):
    """Bot 初始化錯誤"""
    pass

class BotConfigError(BotError):
    """Bot 配置錯誤"""
    pass

class BotRuntimeError(BotError):
    """Bot 運行時錯誤"""
    pass

class HandlerError(BotError):
    """處理器錯誤"""
    pass

class MiddlewareError(BotError):
    """中間件錯誤"""
    pass 