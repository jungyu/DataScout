#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MomoShop 配置

此模組提供 MomoShop 網站的配置常量。
"""

from typing import Dict, Any

# 網站配置
SITE_CONFIG: Dict[str, Any] = {
    "base_url": "https://www.momoshop.com.tw",
    "search_url": "https://www.momoshop.com.tw/search/searchShop.jsp",
    "category_url": "https://www.momoshop.com.tw/category/LgrpCategory.jsp",
    "product_url": "https://www.momoshop.com.tw/goods/GoodsDetail.jsp",
    
    # 驗證碼配置
    "captcha": {
        "timeout": 30000,
        "retry_count": 3,
    },
    
    # 請求配置
    "request": {
        "timeout": 60000,
        "retry_count": 3,
        "retry_delay": 1000,
    },
    
    # 瀏覽器配置
    "browser": {
        "headless": True,
        "slow_mo": 50,
        "viewport": {
            "width": 1920,
            "height": 1080,
        },
    },
}

# 選擇器配置
SELECTORS: Dict[str, Dict[str, str]] = {
    "search": {
        "list_item": "div.goodsUrl",
        "name": "h3.prdName",
        "price": "div.money b",
        "link": "a.goods-img-url",
        "image": "div.goodsUrl img.prdImg",
        "promotion": "p.sloganTitle",
        "tags": "div.iconArea i"
    },
    "product": {
        "list_item": "div.goodsUrl",
        "name": "//h1[@class='prdName']/text()",
        "price": "//ul[@class='prdPrice']//span[@class='price']/text()",
        "link": "//a[@class='goods-img-url']/@href",
        "image": "//img[@class='productImg']/@src",
        "promotion": "//div[@class='promotion']//p/text()",
        "tags": "//div[@class='iconArea']//i",
        "detail_name": "//h1[@class='prdName']/text()",
        "detail_price": "//ul[@class='prdPrice']//span[@class='price']/text()",
        "description": "//div[@class='productIntro']//div[@class='Area']",
        "specs": "//div[@class='specificationBox']//table//tr",
        "spec_name": "th",
        "spec_value": "td",
        "images": "//div[@class='swiper-wrapper']//img[@class='productImg']/@src"
    },
    "pagination": {
        "container": "div.pageArea",
        "next": "a.next",
        "prev": "a.prev",
        "page": "a.page",
    },
    "captcha": {
        "recaptcha": "iframe[title*='reCAPTCHA']",
        "image": "img.captcha-image",
        "input": "input.captcha-input",
        "submit": "button.captcha-submit",
        "slider": ".slider-captcha",
        "slider_background": ".slider-background",
        "slider_button": ".slider-button",
    },
}

# 瀏覽器配置
BROWSER_CONFIG: Dict[str, Any] = {
    "headless": True,
    "proxy": None,
    "browser_type": "chromium",
    "launch_options": {
        "slow_mo": 50,
    },
    "context_options": {
        "viewport": {
            "width": 1920,
            "height": 1080,
        },
    },
}

# 日誌配置
LOG_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "momoshop_scraper.log",
} 