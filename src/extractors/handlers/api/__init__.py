"""
API處理器包

提供API請求和響應處理的功能。

主要組件：
- ApiHandler: API處理器

使用示例：
    from src.extractors.handlers.api import ApiHandler
    from src.extractors.config import ApiConfig
    
    # 創建配置
    config = ApiConfig(
        base_url="https://api.example.com",
        endpoints={
            "search": "/search",
            "detail": "/detail/{id}"
        }
    )
    
    # 創建處理器
    api_handler = ApiHandler(config)
    
    # 發送請求
    search_results = api_handler.request("search", params={"q": "keyword"})
    detail_data = api_handler.request("detail", params={"id": 123})
"""

from .api_handler import ApiHandler

__all__ = ['ApiHandler'] 